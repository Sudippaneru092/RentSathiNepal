from flask import Blueprint, request, current_app
from sqlalchemy import or_, func
from datetime import date as _date

from app import db
from app.models import Property, Review, Favorite, User, Amenity, PropertyAmenity, Chat, RoommateProfile, Booking, Report
from app.api.helpers import api_response, token_required
from app.utils.geocode import haversine_km, format_distance

api_properties = Blueprint('properties', __name__)

# --- INTERNAL HELPERS ---

def serialize_property(p, rating=0, is_favorite=False):
    """Converts a Property model instance into a JSON-friendly dictionary"""
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "property_type": p.property_type,
        "price": float(p.price),
        "city": p.city,
        "district": p.district,
        "province": p.province,
        "area": p.area,
        "address": p.address,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "bedrooms": p.bedrooms,
        "bathrooms": p.bathrooms,
        "furnished": p.furnished,
        "parking": p.parking,
        "availability_status": p.availability_status,
        "verification_status": p.verification_status,
        "primary_image": p.get_primary_image(),
        "avg_rating": rating,
        "is_favorite": is_favorite,
        "owner_id": p.owner_id,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }

def _build_search_query(args):
    """Reusing the exact business logic from main/routes.py"""
    q = args.get('q', '').strip()
    city = args.get('city', '').strip()
    ptype = args.get('property_type', '').strip()
    min_p = args.get('min_price', '').strip()
    max_p = args.get('max_price', '').strip()
    furnished = args.get('furnished', '').strip()
    bedrooms = args.get('bedrooms', '').strip()
    parking = args.get('parking', '').strip()
    sort = args.get('sort', 'newest').strip()

    query = Property.query.filter_by(
        status='active',
        availability_status='available',
        verification_status='verified'
    )

    if q:
        like = f'%{q}%'
        query = query.filter(or_(
            Property.title.ilike(like),
            Property.description.ilike(like),
            Property.city.ilike(like),
            Property.district.ilike(like),
            Property.area.ilike(like),
            Property.address.ilike(like),
        ))
    elif city:
        query = query.filter(or_(
            Property.city.ilike(f'%{city}%'),
            Property.district.ilike(f'%{city}%'),
        ))

    if ptype:
        query = query.filter_by(property_type=ptype)

    if min_p:
        try: query = query.filter(Property.price >= float(min_p))
        except ValueError: pass
    if max_p:
        try: query = query.filter(Property.price <= float(max_p))
        except ValueError: pass

    if furnished == '1': query = query.filter_by(furnished=True)
    elif furnished == '0': query = query.filter_by(furnished=False)

    if bedrooms and bedrooms != 'any':
        try:
            bd = int(bedrooms)
            query = query.filter(Property.bedrooms >= 4) if bd >= 4 else query.filter_by(bedrooms=bd)
        except ValueError: pass

    if parking == '1': query = query.filter_by(parking=True)

    if sort == 'price_asc': query = query.order_by(Property.price.asc())
    elif sort == 'price_desc': query = query.order_by(Property.price.desc())
    elif sort == 'oldest': query = query.order_by(Property.created_at.asc())
    else: query = query.order_by(Property.created_at.desc())

    return query

def _get_rating_map(property_ids):
    if not property_ids: return {}
    rows = db.session.query(
        Review.property_id,
        func.round(func.avg(Review.rating), 1).label('avg_rating')
    ).filter(Review.property_id.in_(property_ids)).group_by(Review.property_id).all()
    return {r.property_id: float(r.avg_rating) for r in rows}

# --- API ENDPOINTS ---

@api_properties.route('/home-stats', methods=['GET'])
def home_stats():
    """Returns stats and featured properties for the Android Home Screen"""
    total_props = Property.query.filter_by(status='active', availability_status='available', verification_status='verified').count()
    total_owners = User.query.filter_by(role='owner').count()
    
    # Featured properties (latest 10)
    props = Property.query.filter_by(status='active', availability_status='available', verification_status='verified').order_by(Property.created_at.desc()).limit(10).all()
    prop_ids = [p.id for p in props]
    rating_map = _get_rating_map(prop_ids)
    
    featured = [serialize_property(p, rating=rating_map.get(p.id, 0)) for p in props]
    
    return api_response("success", data={
        "stats": {"total_properties": total_props, "total_owners": total_owners},
        "featured_properties": featured
    })

@api_properties.route('/search', methods=['GET'])
def search():
    """Paginated search based on filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    query = _build_search_query(request.args)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    prop_ids = [p.id for p in pagination.items]
    rating_map = _get_rating_map(prop_ids)
    
    # Handle favorites if user is logged in
    favorite_ids = set()
    from flask import request
    # Since this is a GET request, we check if token is provided in headers manually
    # or we can make this endpoint @token_required but then guests can't search.
    # For simplicity, I'll assume the Android app sends the user_id if logged in.
    user_id = request.args.get('user_id')
    if user_id:
        favs = Favorite.query.filter_by(user_id=user_id).all()
        favorite_ids = {f.property_id for f in favs}

    properties = [serialize_property(p, rating=rating_map.get(p.id, 0), is_favorite=(p.id in favorite_ids)) for p in pagination.items]

    return api_response("success", data={
        "properties": properties,
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    })

@api_properties.route('/<int:property_id>', methods=['GET'])
def property_detail(property_id):
    p = Property.query.get_or_404(property_id)
    
    # Security check (Same as web)
    if p.status != 'active' or p.verification_status != 'verified':
        return api_response("error", "This property is not available", code=404)

    # Gather related data
    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    amenities = db.session.query(Amenity).join(PropertyAmenity).filter(PropertyAmenity.property_id == property_id).all()
    images = [img.image_path for img in p.images.all()]
    
    # Vacancy Calendar
    today = _date.today()
    vacancies = VacancyCalendar.query.filter_by(property_id=property_id, status='available').filter(
        or_(VacancyCalendar.available_until.is_(None), VacancyCalendar.available_until >= today)
    ).order_by(VacancyCalendar.available_from.asc()).all()

    return api_response("success", data={
        "property": serialize_property(p),
        "images": images,
        "amenities": [a.amenity_name for a in amenities],
        "reviews": [{"user": r.reviewer.full_name, "rating": r.rating, "text": r.review, "date": r.created_at.isoformat()} for r in reviews],
        "vacancies": [{"from": v.available_from.isoformat(), "until": v.available_until.isoformat() if v.available_until else None} for v in vacancies],
        "owner": {"id": p.owner_id, "name": p.owner.full_name, "email": p.owner.email}
    })

@api_properties.route('/nearby', methods=['GET'])
def nearby():
    """GPS based search"""
    try:
        user_lat = float(request.args.get('lat'))
        user_lng = float(request.args.get('lng'))
    except (ValueError, TypeError):
        return api_response("error", "lat and lng are required", code=400)

    radius = float(request.args.get('radius', 5))
    ptype = request.args.get('property_type', '').strip()

    base = Property.query.filter(
        Property.status == 'active',
        Property.availability_status == 'available',
        Property.verification_status == 'verified',
        Property.latitude.isnot(None),
        Property.longitude.isnot(None),
    )
    if ptype: base = base.filter_by(property_type=ptype)

    results = []
    for prop in base.all():
        dist = haversine_km(user_lat, user_lng, prop.latitude, prop.longitude)
        if dist <= radius:
            results.append({
                "property": serialize_property(prop),
                "distance_km": round(dist, 2),
                "distance_label": format_distance(dist)
            })

    results.sort(key=lambda x: x['distance_km'])
    return api_response("success", data={"results": results, "total": len(results)})

@api_properties.route('/<int:property_id>/favorite', methods=['POST'])
@token_required
def toggle_favorite(current_user, property_id):
    p = Property.query.get_or_404(property_id)
    existing = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return api_response("success", "Removed from favorites")
    else:
        fav = Favorite(user_id=current_user.id, property_id=property_id)
        db.session.add(fav)
        db.session.commit()
        return api_response("success", "Added to favorites")

@api_properties.route('/<int:property_id>/book', methods=['POST'])
@token_required
def book_property(current_user, property_id):
    from app.models import Booking
    p = Property.query.get_or_404(property_id)

    if current_user.role != 'user':
        return api_response("error", "Only tenants can make bookings", code=403)
    
    if current_user.id == p.owner_id:
        return api_response("error", "You cannot book your own property", code=400)

    data = request.get_json()
    move_in_str = data.get('move_in_date', '').strip()
    message_text = data.get('message', '').strip()

    if not move_in_str:
        return api_response("error", "Move-in date is required", code=400)

    try:
        move_in = _date.fromisoformat(move_in_str)
        if move_in < _date.today():
            return api_response("error", "Date cannot be in the past", code=400)
    except ValueError:
        return api_response("error", "Invalid date format (YYYY-MM-DD)", code=400)

    # Check existing
    existing = Booking.query.filter_by(property_id=property_id, tenant_id=current_user.id).filter(Booking.status.in_(['pending', 'confirmed'])).first()
    if existing:
        return api_response("error", "Active booking request already exists", code=400)

    booking = Booking(property_id=property_id, tenant_id=current_user.id, move_in_date=move_in, message=message_text, status='pending')
    
    # Create associated chat message
    chat = Chat(sender_id=current_user.id, receiver_id=p.owner_id, property_id=property_id, message=f"📅 Booking Request: {move_in_str}")
    
    db.session.add(booking)
    db.session.add(chat)
    db.session.commit()

    return api_response("success", "Booking request sent successfully")

@api_properties.route('/<int:property_id>/review', methods=['POST'])
@token_required
def add_review(current_user, property_id):
    p = Property.query.get_or_404(property_id)
    if current_user.role == 'owner' and p.owner_id == current_user.id:
        return api_response("error", "You cannot review your own property", code=400)

    data = request.get_json()
    rating = data.get('rating')
    review_text = data.get('review', '').strip()

    if not rating or not (1 <= int(rating) <= 5):
        return api_response("error", "Rating must be between 1 and 5", code=400)

    existing = Review.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if existing:
        return api_response("error", "You already reviewed this property", code=400)

    review = Review(property_id=property_id, user_id=current_user.id, rating=int(rating), review=review_text)
    db.session.add(review)
    db.session.commit()

    return api_response("success", "Review submitted")