import os
import uuid
from flask import Blueprint, request, current_app
from app import db
from app.models import Property, PropertyImage, PropertyDocument, Amenity, PropertyAmenity, OwnerProfile, Chat, User, Booking, VacancyCalendar
from app.api.helpers import api_response, token_required
from app.utils.logger import log_auth_attempt # If needed
from app.utils.geocode import geocode_address
import threading

api_owners = Blueprint('owners', __name__)

# --- INTERNAL HELPERS (Reused from routes.py) ---

def _geocode_property_async(app, property_id, address, city):
    def _run():
        with app.app_context():
            import time
            time.sleep(0.5) 
            coords = geocode_address(address, city)
            if coords:
                prop = Property.query.get(property_id)
                if prop and (prop.latitude is None or prop.longitude is None):
                    prop.latitude, prop.longitude = coords
                    db.session.commit()
    t = threading.Thread(target=_run, daemon=True)
    t.start()

def save_file_api(file, subfolder='misc'):
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, unique_name))
    return f"uploads/{subfolder}/{unique_name}"

# --- API ENDPOINTS ---

@api_owners.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    """Returns all the stats and basic property list for the owner's dashboard"""
    properties = Property.query.filter_by(owner_id=current_user.id).order_by(Property.created_at.desc()).all()
    owner_profile = OwnerProfile.query.filter_by(user_id=current_user.id).first()
    prop_ids = [p.id for p in properties]

    # Calculate Stats
    stats = {
        "total_props": len(properties),
        "available_props": sum(1 for p in properties if p.availability_status == 'available'),
        "occupied_props": sum(1 for p in properties if p.availability_status == 'occupied'),
        "pending_props": sum(1 for p in properties if p.verification_status == 'pending'),
        "verified_props": sum(1 for p in properties if p.verification_status == 'verified'),
        "total_inquiries": Chat.query.filter(Chat.receiver_id == current_user.id).count(),
        "unread_inquiries": Chat.query.filter(Chat.receiver_id == current_user.id, is_read=False).count(),
        "total_favorites": 0 if not prop_ids else __import__('app.models').Favorite.query.filter(__import__('app.models').Favorite.property_id.in_(prop_ids)).count(),
        "pending_bookings": 0 if not prop_ids else Booking.query.join(Property).filter(Property.owner_id == current_user.id, Booking.status == 'pending').count()
    }

    # Format Property List for Dashboard
    prop_list = []
    for p in properties:
        prop_list.append({
            "id": p.id,
            "title": p.title,
            "price": float(p.price),
            "city": p.city,
            "status": p.availability_status,
            "verification": p.verification_status,
            "image": p.get_primary_image()
        })

    return api_response("success", "Dashboard data fetched", data={
        "stats": stats,
        "properties": prop_list,
        "owner_profile": {
            "verification_status": owner_profile.verification_status if owner_profile else "not_created"
        }
    })

@api_owners.route('/property/add', methods=['POST'])
@token_required
def add_property(current_user):
    """
    Handles Multipart/Form-Data for images and text
    Android must send this as a Form, not JSON.
    """
    try:
        # Text data from request.form
        title = request.form.get('title', '').strip()
        price = request.form.get('price', '0')
        city = request.form.get('city', '').strip()
        property_type = request.form.get('property_type', '').strip()
        
        if not all([title, price, city, property_type]):
            return api_response("error", "Title, Price, City, and Type are required", code=400)

        new_prop = Property(
            owner_id=current_user.id,
            title=title,
            description=request.form.get('description', '').strip(),
            property_type=property_type,
            price=float(price),
            province=request.form.get('province', '').strip(),
            district=request.form.get('district', '').strip(),
            city=city,
            address=request.form.get('address', '').strip(),
            bedrooms=int(request.form.get('bedrooms', 0)),
            bathrooms=int(request.form.get('bathrooms', 0)),
            furnished=request.form.get('furnished') == '1',
            parking=request.form.get('parking') == '1',
            availability_status='available',
            verification_status='pending',
            status='active'
        )
        db.session.add(new_prop)
        db.session.flush()

        # Handle Images (Multiple)
        images = request.files.getlist('images')
        for img in images:
            path = save_file_api(img, 'properties')
            if path:
                db.session.add(PropertyImage(property_id=new_prop.id, image_path=path))

        # Handle Document
        doc = request.files.get('document')
        if doc:
            path = save_file_api(doc, 'documents')
            if path:
                db.session.add(PropertyDocument(
                    property_id=new_prop.id, 
                    document_type=request.form.get('document_type', ''),
                    document_file=path
                ))

        # Handle Amenities (Comma separated IDs from Android)
        amenities_ids = request.form.get('amenities', '').split(',')
        for aid in amenities_ids:
            if aid.strip():
                db.session.add(PropertyAmenity(property_id=new_prop.id, amenity_id=int(aid)))

        db.session.commit()
        
        # Async Geocoding
        _geocode_property_async(current_app._get_current_object(), new_prop.id, new_prop.address, new_prop.city)

        return api_response("success", "Property added successfully", data={"property_id": new_prop.id})

    except Exception as e:
        db.session.rollback()
        return api_response("error", str(e), code=500)

@api_owners.route('/property/<int:property_id>/delete', methods=['DELETE'])
@token_required
def delete_property(current_user, property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        return api_response("error", "Unauthorized", code=403)
    
    db.session.delete(prop)
    db.session.commit()
    return api_response("success", "Property deleted successfully")

@api_owners.route('/bookings', methods=['GET'])
@token_required
def get_bookings(current_user):
    bookings = db.session.query(Booking)\
        .join(Property, Booking.property_id == Property.id)\
        .filter(Property.owner_id == current_user.id)\
        .order_by(Booking.created_at.desc()).all()
    
    result = []
    for b in bookings:
        result.append({
            "booking_id": b.id,
            "property_title": b.property.title,
            "tenant_name": b.tenant.full_name,
            "move_in_date": b.move_in_date.isoformat(),
            "status": b.status
        })
    
    return api_response("success", "Bookings fetched", data=result)

@api_owners.route('/bookings/<int:booking_id>/respond', methods=['PATCH'])
@token_required
def respond_booking(current_user, booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.property.owner_id != current_user.id:
        return api_response("error", "Unauthorized", code=403)

    data = request.get_json()
    action = data.get('action') # 'confirm' or 'reject'

    if action == 'confirm':
        booking.status = 'confirmed'
        booking.property.availability_status = 'occupied'
        # Notification logic reused from routes.py
        msg = Chat(sender_id=current_user.id, receiver_id=booking.tenant_id, 
                   property_id=booking.property_id, message="✅ Your booking has been CONFIRMED!")
        db.session.add(msg)
    elif action == 'reject':
        booking.status = 'rejected'
        msg = Chat(sender_id=current_user.id, receiver_id=booking.tenant_id, 
                   property_id=booking.property_id, message="❌ Your booking has been declined.")
        db.session.add(msg)
    else:
        return api_response("error", "Invalid action", code=400)

    db.session.commit()
    return api_response("success", f"Booking {action}ed successfully")