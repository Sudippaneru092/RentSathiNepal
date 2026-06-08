from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_, func
from app import db
from app.main import main_bp
from app.models import Property, Review, Favorite, User, Amenity, PropertyAmenity, Chat
from app.utils.geocode import haversine_km, format_distance, geocode_address


def _build_search_query(args):
    """Shared filter logic used by both index and listings routes."""
    q        = args.get('q', '').strip()          # full-text search
    city     = args.get('city', '').strip()
    ptype    = args.get('property_type', '').strip()
    min_p    = args.get('min_price', '').strip()
    max_p    = args.get('max_price', '').strip()
    furnished= args.get('furnished', '').strip()
    bedrooms = args.get('bedrooms', '').strip()
    parking  = args.get('parking', '').strip()
    sort     = args.get('sort', 'newest').strip()

    query = Property.query.filter_by(
        status='active',
        availability_status='available',
        verification_status='verified'
    )

    # Full-text search across title, description, city, district, area, address
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
        try:
            query = query.filter(Property.price >= float(min_p))
        except ValueError:
            pass
    if max_p:
        try:
            query = query.filter(Property.price <= float(max_p))
        except ValueError:
            pass

    if furnished == '1':
        query = query.filter_by(furnished=True)
    elif furnished == '0':
        query = query.filter_by(furnished=False)

    if bedrooms and bedrooms != 'any':
        try:
            bd = int(bedrooms)
            if bd >= 4:
                query = query.filter(Property.bedrooms >= 4)
            else:
                query = query.filter_by(bedrooms=bd)
        except ValueError:
            pass

    if parking == '1':
        query = query.filter_by(parking=True)

    # Sorting
    if sort == 'price_asc':
        query = query.order_by(Property.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Property.price.desc())
    elif sort == 'oldest':
        query = query.order_by(Property.created_at.asc())
    else:  # newest
        query = query.order_by(Property.created_at.desc())

    return query


@main_bp.route('/')
def index():
    # For home page just show latest 9 verified properties
    properties = Property.query.filter_by(
        status='active', availability_status='available', verification_status='verified'
    ).order_by(Property.created_at.desc()).paginate(page=1, per_page=9, error_out=False)

    favorite_ids = set()
    if current_user.is_authenticated:
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        favorite_ids = {f.property_id for f in favs}

    return render_template(
        'main/index.html',
        title='Find Your Perfect Home in Nepal',
        properties=properties,
        favorite_ids=favorite_ids,
        search_params={'city': '', 'property_type': ''},
    )


@main_bp.route('/listings')
def listings():
    page     = request.args.get('page', 1, type=int)
    sort     = request.args.get('sort', 'newest').strip()
    q        = request.args.get('q', '').strip()
    city     = request.args.get('city', '').strip()
    ptype    = request.args.get('property_type', '').strip()
    min_p    = request.args.get('min_price', '').strip()
    max_p    = request.args.get('max_price', '').strip()
    furnished= request.args.get('furnished', '').strip()
    bedrooms = request.args.get('bedrooms', '').strip()
    parking  = request.args.get('parking', '').strip()

    query = _build_search_query(request.args)
    properties = query.paginate(page=page, per_page=12, error_out=False)

    # Active filter chips — collect non-empty filters for display
    active_filters = []
    if q:
        active_filters.append(('q', q, f'"{q}"'))
    if city:
        active_filters.append(('city', city, f'City: {city}'))
    if ptype:
        active_filters.append(('property_type', ptype, ptype.capitalize()))
    if min_p:
        active_filters.append(('min_price', min_p, f'Min Rs.{int(float(min_p)):,}'))
    if max_p:
        active_filters.append(('max_price', max_p, f'Max Rs.{int(float(max_p)):,}'))
    if furnished == '1':
        active_filters.append(('furnished', '1', 'Furnished'))
    elif furnished == '0':
        active_filters.append(('furnished', '0', 'Unfurnished'))
    if bedrooms and bedrooms != 'any':
        label = f'{bedrooms}+ Beds' if bedrooms == '4' else f'{bedrooms} Bed{"s" if bedrooms != "1" else ""}'
        active_filters.append(('bedrooms', bedrooms, label))
    if parking == '1':
        active_filters.append(('parking', '1', 'Parking'))

    # All amenities for filter panel
    amenities = Amenity.query.order_by(Amenity.amenity_name).all()

    # Favorite IDs
    favorite_ids = set()
    if current_user.is_authenticated:
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        favorite_ids = {f.property_id for f in favs}

    # Price range stats for slider hint
    price_stats = db.session.query(
        func.min(Property.price), func.max(Property.price)
    ).filter_by(status='active', availability_status='available', verification_status='verified').first()
    price_min_db = int(price_stats[0] or 0)
    price_max_db = int(price_stats[1] or 200000)

    # Build params dict for pagination links (exclude 'page')
    search_params = {k: v for k, v in request.args.items() if k != 'page'}

    return render_template(
        'main/listings.html',
        title='Browse Rentals',
        properties=properties,
        favorite_ids=favorite_ids,
        active_filters=active_filters,
        amenities=amenities,
        search_params=search_params,
        price_min_db=price_min_db,
        price_max_db=price_max_db,
        # current filter values
        q=q, city=city, ptype=ptype,
        min_p=min_p, max_p=max_p,
        furnished=furnished, bedrooms=bedrooms,
        parking=parking, sort=sort,
    )


@main_bp.route('/search/suggestions')
def search_suggestions():
    """AJAX endpoint: returns city/title suggestions as JSON."""
    term = request.args.get('q', '').strip()
    if len(term) < 2:
        return jsonify([])
    like = f'%{term}%'
    cities = db.session.query(Property.city).filter(
        Property.city.ilike(like),
        Property.status == 'active',
        Property.verification_status == 'verified'
    ).distinct().limit(5).all()
    titles = db.session.query(Property.title, Property.id).filter(
        Property.title.ilike(like),
        Property.status == 'active',
        Property.verification_status == 'verified'
    ).limit(5).all()
    results = [{'type': 'city', 'label': c[0], 'value': c[0]} for c in cities]
    results += [{'type': 'property', 'label': t[0], 'value': t[0], 'id': t[1]} for t in titles]
    return jsonify(results)


# ── NEARBY SEARCH ────────────────────────────────────────────────────────────

@main_bp.route('/nearby')
def nearby():
    """
    Nearby search page.
    Accepts: lat, lng, radius (km), property_type
    Shows properties sorted by distance, with distance badges.
    """
    try:
        user_lat = float(request.args.get('lat', ''))
        user_lng = float(request.args.get('lng', ''))
    except (ValueError, TypeError):
        # No coords yet — show the "allow location" landing
        return render_template('main/nearby.html',
                               title='Properties Near Me',
                               waiting=True,
                               properties=[], radius=5, ptype='')

    radius  = float(request.args.get('radius', 5))   # km
    ptype   = request.args.get('property_type', '').strip()

    # Fetch all active verified properties that have coordinates
    base = Property.query.filter(
        Property.status == 'active',
        Property.availability_status == 'available',
        Property.verification_status == 'verified',
        Property.latitude.isnot(None),
        Property.longitude.isnot(None),
    )
    if ptype:
        base = base.filter_by(property_type=ptype)

    candidates = base.all()

    # Calculate distance and filter by radius
    results = []
    for prop in candidates:
        dist = haversine_km(user_lat, user_lng, prop.latitude, prop.longitude)
        if dist <= radius:
            results.append({
                'property': prop,
                'distance_km': round(dist, 2),
                'distance_label': format_distance(dist),
            })

    # Sort by distance ascending
    results.sort(key=lambda x: x['distance_km'])

    # Favorite IDs
    favorite_ids = set()
    if current_user.is_authenticated:
        favs = Favorite.query.filter_by(user_id=current_user.id).all()
        favorite_ids = {f.property_id for f in favs}

    return render_template('main/nearby.html',
                           title=f'Properties within {radius:.0f} km',
                           waiting=False,
                           properties=results,
                           radius=radius,
                           ptype=ptype,
                           user_lat=user_lat,
                           user_lng=user_lng,
                           favorite_ids=favorite_ids,
                           total=len(results))


@main_bp.route('/api/nearby')
def api_nearby():
    """
    JSON API for nearby properties — used by the map view / AJAX calls.
    Returns properties with distance within radius sorted by distance.
    """
    try:
        user_lat = float(request.args.get('lat'))
        user_lng = float(request.args.get('lng'))
    except (ValueError, TypeError):
        return jsonify({'error': 'lat and lng are required'}), 400

    radius = float(request.args.get('radius', 5))
    ptype  = request.args.get('property_type', '').strip()

    base = Property.query.filter(
        Property.status == 'active',
        Property.availability_status == 'available',
        Property.verification_status == 'verified',
        Property.latitude.isnot(None),
        Property.longitude.isnot(None),
    )
    if ptype:
        base = base.filter_by(property_type=ptype)

    results = []
    for prop in base.all():
        dist = haversine_km(user_lat, user_lng, prop.latitude, prop.longitude)
        if dist <= radius:
            results.append({
                'id': prop.id,
                'title': prop.title,
                'lat': prop.latitude,
                'lng': prop.longitude,
                'price': float(prop.price),
                'type': prop.property_type,
                'city': prop.city,
                'distance_km': round(dist, 2),
                'distance_label': format_distance(dist),
                'image': prop.get_primary_image(),
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'verified': prop.verification_status == 'verified',
                'url': url_for('main.property_detail', property_id=prop.id),
            })

    results.sort(key=lambda x: x['distance_km'])
    return jsonify({'results': results, 'total': len(results), 'radius_km': radius})


@main_bp.route('/property/<int:property_id>')
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)

    # Only show active/verified properties to public, but owners and admins can see their own
    if property.status != 'active' or property.verification_status != 'verified':
        if not current_user.is_authenticated:
            flash('This property is not available.', 'warning')
            return redirect(url_for('main.index'))
        if current_user.role not in ('admin',) and property.owner_id != current_user.id:
            flash('This property is not available.', 'warning')
            return redirect(url_for('main.index'))

    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    amenities = db.session.query(Amenity).join(PropertyAmenity).filter(
        PropertyAmenity.property_id == property_id
    ).all()
    images = property.images.all()

    is_favorite = False
    if current_user.is_authenticated:
        is_favorite = Favorite.query.filter_by(
            user_id=current_user.id, property_id=property_id
        ).first() is not None

    owner = User.query.get(property.owner_id)

    return render_template(
        'main/property_detail.html',
        title=property.title,
        property=property,
        reviews=reviews,
        amenities=amenities,
        images=images,
        is_favorite=is_favorite,
        owner=owner
    )


@main_bp.route('/property/<int:property_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(property_id):
    property = Property.query.get_or_404(property_id)
    existing = Favorite.query.filter_by(user_id=current_user.id, property_id=property_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash('Removed from favorites.', 'info')
    else:
        fav = Favorite(user_id=current_user.id, property_id=property_id)
        db.session.add(fav)
        db.session.commit()
        flash('Added to favorites!', 'success')

    return redirect(request.referrer or url_for('main.property_detail', property_id=property_id))


@main_bp.route('/property/<int:property_id>/review', methods=['POST'])
@login_required
def add_review(property_id):
    property = Property.query.get_or_404(property_id)

    if current_user.role == 'owner' and property.owner_id == current_user.id:
        flash('You cannot review your own property.', 'warning')
        return redirect(url_for('main.property_detail', property_id=property_id))

    existing = Review.query.filter_by(user_id=current_user.id, property_id=property_id).first()
    if existing:
        flash('You have already reviewed this property.', 'warning')
        return redirect(url_for('main.property_detail', property_id=property_id))

    try:
        rating = int(request.form.get('rating', 0))
        review_text = request.form.get('review', '').strip()
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5.', 'danger')
            return redirect(url_for('main.property_detail', property_id=property_id))

        review = Review(
            property_id=property_id,
            user_id=current_user.id,
            rating=rating,
            review=review_text
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
    except Exception:
        db.session.rollback()
        flash('An error occurred while submitting your review.', 'danger')

    return redirect(url_for('main.property_detail', property_id=property_id))


@main_bp.route('/property/<int:property_id>/contact', methods=['POST'])
@login_required
def contact_owner(property_id):
    property = Property.query.get_or_404(property_id)

    if current_user.id == property.owner_id:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('main.property_detail', property_id=property_id))

    message_text = request.form.get('message', '').strip()
    if not message_text:
        flash('Message cannot be empty.', 'danger')
        return redirect(url_for('main.property_detail', property_id=property_id))

    chat = Chat(
        sender_id=current_user.id,
        receiver_id=property.owner_id,
        property_id=property_id,
        message=message_text
    )
    db.session.add(chat)
    db.session.commit()
    flash('Your message has been sent to the owner!', 'success')
    return redirect(url_for('main.property_detail', property_id=property_id))


@main_bp.route('/property/<int:property_id>/report', methods=['POST'])
@login_required
def report_property(property_id):
    from app.models import Report
    property = Property.query.get_or_404(property_id)
    reason = request.form.get('reason', '').strip()

    if not reason:
        flash('Please provide a reason for the report.', 'danger')
        return redirect(url_for('main.property_detail', property_id=property_id))

    report = Report(
        reported_by=current_user.id,
        property_id=property_id,
        reason=reason,
        status='pending'
    )
    db.session.add(report)
    db.session.commit()
    flash('Property has been reported. Our team will review it.', 'success')
    return redirect(url_for('main.property_detail', property_id=property_id))
