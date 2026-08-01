import os
import uuid
from flask import Blueprint, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from app import db
from app.models import User, Favorite, Property, RoommateProfile, Chat, Booking
from app.api.helpers import api_response, token_required

api_users = Blueprint('users', __name__)

# ==============================================================================
# INTERNAL HELPERS
# ==============================================================================

def save_api_file(file, subfolder='misc'):
    """Reusing the save_file logic from user/routes.py"""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in allowed:
        return None
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, unique_name))
    return f"uploads/{subfolder}/{unique_name}"

def serialize_property_mini(p):
    """Small version of property for dashboard/favorites lists"""
    return {
        "id": p.id,
        "title": p.title,
        "price": float(p.price),
        "city": p.city,
        "image": p.get_primary_image()
    }

# ==============================================================================
# API ROUTES
# ==============================================================================

@api_users.route('/dashboard', methods=['GET'])
@token_required
def dashboard(current_user):
    # 1. Counts
    total_favorites = Favorite.query.filter_by(user_id=current_user.id).count()
    unread_count = Chat.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    
    # 2. Recent Favorites (up to 4)
    recent_favs_records = (
        Favorite.query.filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc()).limit(4).all()
    )
    fav_properties = []
    for f in recent_favs_records:
        p = Property.query.get(f.property_id)
        if p: fav_properties.append(serialize_property_mini(p))

    # 3. Recent Messages (up to 5)
    recent_msgs = (
        Chat.query.filter_by(receiver_id=current_user.id)
        .order_by(Chat.sent_at.desc()).limit(5).all()
    )
    messages = [{
        "id": m.id,
        "sender": User.query.get(m.sender_id).full_name,
        "message": m.message,
        "sent_at": m.sent_at.isoformat(),
        "is_read": m.is_read
    } for m in recent_msgs]

    # 4. Roommate Profile Status
    rp = RoommateProfile.query.filter_by(user_id=current_user.id).first()

    return api_response("success", data={
        "stats": {
            "total_favorites": total_favorites,
            "unread_messages": unread_count
        },
        "recent_favorites": fav_properties,
        "recent_messages": messages,
        "roommate_profile": {
            "exists": rp is not None,
            "data": {
                "preferred_city": rp.preferred_city,
                "budget": float(rp.budget) if rp and rp.budget else 0
            } if rp else None
        }
    })

@api_users.route('/profile', methods=['GET', 'POST'])
@token_required
def profile(current_user):
    if request.method == 'GET':
        return api_response("success", data={
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "gender": current_user.gender,
            "occupation": current_user.occupation,
            "province": current_user.province,
            "district": current_user.district,
            "city": current_user.city,
            "address": current_user.address,
            "profile_image": current_user.profile_image
        })

    if request.method == 'POST':
        # Android sends data as Form-Data (not JSON) to allow image uploads
        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        current_user.gender = request.form.get('gender', current_user.gender).strip()
        current_user.occupation = request.form.get('occupation', current_user.occupation).strip()
        current_user.province = request.form.get('province', current_user.province).strip()
        current_user.district = request.form.get('district', current_user.district).strip()
        current_user.city = request.form.get('city', current_user.city).strip()
        current_user.address = request.form.get('address', current_user.address).strip()

        # Profile image upload
        profile_img = request.files.get('profile_image')
        if profile_img and profile_img.filename:
            path = save_api_file(profile_img, subfolder='profiles')
            if path:
                current_user.profile_image = path

        # Password change logic
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        if current_password:
            if not check_password_hash(current_user.password, current_password):
                return api_response("error", "Current password is incorrect", code=400)
            if not new_password or len(new_password) < 6:
                return api_response("error", "New password must be at least 6 chars", code=400)
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        return api_response("success", "Profile updated successfully")

@api_users.route('/favorites', methods=['GET'])
@token_required
def favorites(current_user):
    page = request.args.get('page', 1, type=int)
    favs = (
        Favorite.query.filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .paginate(page=page, per_page=12, error_out=False)
    )
    
    properties = []
    for f in favs.items:
        p = Property.query.get(f.property_id)
        if p: properties.append(serialize_property_mini(p))

    return api_response("success", data={
        "properties": properties,
        "total": favs.total,
        "pages": favs.pages,
        "current_page": favs.page
    })

@api_users.route('/roommate-profile', methods=['GET', 'POST'])
@token_required
def roommate_profile(current_user):
    rp = RoommateProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'GET':
        if not rp: return api_response("error", "No roommate profile found", code=404)
        return api_response("success", data={
            "preferred_city": rp.preferred_city,
            "budget": float(rp.budget) if rp.budget else 0,
            "occupation": rp.occupation,
            "gender_preference": rp.gender_preference,
            "smoking_preference": rp.smoking_preference,
            "drinking_preference": rp.drinking_preference,
            "lifestyle": rp.lifestyle,
            "bio": rp.bio
        })

    if request.method == 'POST':
        data = request.get_json()
        budget_val = None
        try:
            budget_val = float(data.get('budget')) if data.get('budget') else None
        except ValueError:
            return api_response("error", "Budget must be a number", code=400)

        if rp:
            rp.preferred_city = data.get('preferred_city', rp.preferred_city)
            rp.budget = budget_val
            rp.occupation = data.get('occupation', rp.occupation)
            rp.gender_preference = data.get('gender_preference', rp.gender_preference)
            rp.smoking_preference = data.get('smoking_preference', rp.smoking_preference)
            rp.drinking_preference = data.get('drinking_preference', rp.drinking_preference)
            rp.lifestyle = data.get('lifestyle', rp.lifestyle)
            rp.bio = data.get('bio', rp.bio)
        else:
            rp = RoommateProfile(
                user_id=current_user.id,
                preferred_city=data.get('preferred_city'),
                budget=budget_val,
                occupation=data.get('occupation'),
                gender_preference=data.get('gender_preference'),
                smoking_preference=data.get('smoking_preference'),
                drinking_preference=data.get('drinking_preference'),
                lifestyle=data.get('lifestyle'),
                bio=data.get('bio')
            )
            db.session.add(rp)

        db.session.commit()
        return api_response("success", "Roommate profile saved")

@api_users.route('/bookings', methods=['GET'])
@token_required
def my_bookings(current_user):
    bookings = Booking.query.filter_by(tenant_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return api_response("success", data=[{
        "id": b.id,
        "property": b.property.title,
        "move_in_date": b.move_in_date.isoformat(),
        "status": b.status,
        "created_at": b.created_at.isoformat()
    } for b in bookings])

@api_users.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@token_required
def cancel_booking(current_user, booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.tenant_id != current_user.id:
        return api_response("error", "Unauthorized", code=403)
    if booking.status != 'pending':
        return api_response("error", "Only pending bookings can be cancelled", code=400)
    
    booking.status = 'cancelled'
    db.session.commit()
    return api_response("success", "Booking cancelled")

@api_users.route('/roommates/search', methods=['GET'])
def search_roommates():
    city = request.args.get('city', '').strip()
    gender = request.args.get('gender', '').strip()
    max_budget = request.args.get('max_budget', '').strip()
    keyword = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)

    query = RoommateProfile.query
    if city: query = query.filter(RoommateProfile.preferred_city.ilike(f'%{city}%'))
    if gender: query = query.filter_by(gender_preference=gender)
    if max_budget:
        try: query = query.filter(RoommateProfile.budget <= float(max_budget))
        except ValueError: pass
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(or_(
            RoommateProfile.occupation.ilike(like),
            RoommateProfile.bio.ilike(like),
            RoommateProfile.lifestyle.ilike(like)
        ))

    # Filter out active users only and exclude self
    user_id = request.args.get('user_id')
    query = query.join(User, RoommateProfile.user_id == User.id).filter(User.account_status == 'active')
    if user_id:
        query = query.filter(RoommateProfile.user_id != user_id)

    profiles = query.order_by(RoommateProfile.created_at.desc()).paginate(page=page, per_page=12, error_out=False)

    return api_response("success", data={
        "profiles": [{
            "profile_id": rp.id,
            "full_name": rp.user.full_name,
            "city": rp.preferred_city,
            "budget": float(rp.budget) if rp.budget else 0,
            "bio": rp.bio[:100] + "..." if rp.bio else ""
        } for rp in profiles.items],
        "total": profiles.total,
        "pages": profiles.pages
    })

@api_users.route('/roommates/<int:profile_id>', methods=['GET'])
def roommate_view(profile_id):
    rp = RoommateProfile.query.get_or_404(profile_id)
    user = User.query.get(rp.user_id)
    if not user or user.account_status != 'active':
        return api_response("error", "Profile not available", code=404)

    return api_response("success", data={
        "user": {"full_name": user.full_name, "email": user.email, "phone": user.phone},
        "profile": {
            "preferred_city": rp.preferred_city,
            "budget": float(rp.budget) if rp.budget else 0,
            "occupation": rp.occupation,
            "gender_preference": rp.gender_preference,
            "smoking_preference": rp.smoking_preference,
            "drinking_preference": rp.drinking_preference,
            "lifestyle": rp.lifestyle,
            "bio": rp.bio
        }
    })