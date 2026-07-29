import os
import uuid
import logging
import threading
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.owner import owner_bp
from app.models import Property, PropertyImage, PropertyDocument, Amenity, PropertyAmenity, OwnerProfile, Chat, User

from app.utils.geocode import geocode_address

logger = logging.getLogger('rentsathi')


def _geocode_property_async(app, property_id, address, city):
    """Run geocoding in a background thread so it doesn't block the request."""
    def _run():
        with app.app_context():
            import time
            time.sleep(0.5)  # Respect Nominatim 1 req/s rate limit
            coords = geocode_address(address, city)
            if coords:
                prop = Property.query.get(property_id)
                if prop and (prop.latitude is None or prop.longitude is None):
                    prop.latitude, prop.longitude = coords
                    db.session.commit()
    t = threading.Thread(target=_run, daemon=True)
    t.start()


def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'owner':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_file(file, subfolder='misc'):
    """Save an uploaded file and return its relative path."""
    if not file or not file.filename:
        return None
    if not allowed_file(file.filename):
        return None
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, unique_name))
    return f"uploads/{subfolder}/{unique_name}"


@owner_bp.route('/dashboard')
@login_required
@owner_required
def dashboard():
    from app.models import Chat, Review, Favorite
    properties = Property.query.filter_by(owner_id=current_user.id).order_by(Property.created_at.desc()).all()
    owner_profile = OwnerProfile.query.filter_by(user_id=current_user.id).first()

    prop_ids = [p.id for p in properties]

    # Stats
    total_props       = len(properties)
    available_props   = sum(1 for p in properties if p.availability_status == 'available')
    occupied_props    = sum(1 for p in properties if p.availability_status == 'occupied')
    pending_props     = sum(1 for p in properties if p.verification_status == 'pending')
    verified_props    = sum(1 for p in properties if p.verification_status == 'verified')

    # Inquiries (messages received about owner's properties)
    total_inquiries = Chat.query.filter(
        Chat.receiver_id == current_user.id
    ).count() if prop_ids else 0

    unread_inquiries = Chat.query.filter(
        Chat.receiver_id == current_user.id
    ).count()

    # Recent inquiries
    recent_inquiries = Chat.query.filter(
        Chat.receiver_id == current_user.id
    ).order_by(Chat.sent_at.desc()).limit(5).all()

    # Recent reviews across all properties
    recent_reviews = []
    if prop_ids:
        recent_reviews = Review.query.filter(
            Review.property_id.in_(prop_ids)
        ).order_by(Review.created_at.desc()).limit(5).all()

    # Total favorites across all properties
    total_favorites = Favorite.query.filter(
        Favorite.property_id.in_(prop_ids)
    ).count() if prop_ids else 0

    # Pending booking requests
    from app.models import Booking
    pending_bookings = Booking.query.join(Property).filter(
        Property.owner_id == current_user.id,
        Booking.status == 'pending'
    ).count() if prop_ids else 0

    return render_template('owner/dashboard.html',
                           title='Owner Dashboard',
                           properties=properties,
                           owner_profile=owner_profile,
                           total_props=total_props,
                           available_props=available_props,
                           occupied_props=occupied_props,
                           pending_props=pending_props,
                           verified_props=verified_props,
                           total_inquiries=total_inquiries,
                           unread_inquiries=unread_inquiries,
                           recent_inquiries=recent_inquiries,
                           recent_reviews=recent_reviews,
                           total_favorites=total_favorites,
                           pending_bookings=pending_bookings)


@owner_bp.route('/property/add', methods=['GET', 'POST'])
@login_required
@owner_required
def add_property():
    amenities = Amenity.query.order_by(Amenity.amenity_name).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        property_type = request.form.get('property_type', '').strip()
        price = request.form.get('price', '').strip()
        province = request.form.get('province', '').strip()
        district = request.form.get('district', '').strip()
        city = request.form.get('city', '').strip()
        area = request.form.get('area', '').strip()
        address = request.form.get('address', '').strip()
        latitude = request.form.get('latitude', '').strip()
        longitude = request.form.get('longitude', '').strip()
        bedrooms = request.form.get('bedrooms', '0').strip()
        bathrooms = request.form.get('bathrooms', '0').strip()
        furnished = request.form.get('furnished') == '1'
        parking = request.form.get('parking') == '1'
        selected_amenities = request.form.getlist('amenities')

        # Validation
        errors = []
        if not title:
            errors.append('Title is required.')
        if not property_type:
            errors.append('Property type is required.')
        if not city:
            errors.append('City is required.')
        if not price:
            errors.append('Price is required.')
        else:
            try:
                price = float(price)
                if price <= 0:
                    errors.append('Price must be a positive number.')
            except ValueError:
                errors.append('Price must be a valid number.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('owner/add_property.html', title='Add Property',
                                   amenities=amenities, form_data=request.form)

        try:
            bedrooms = int(bedrooms)
        except ValueError:
            bedrooms = 0
        try:
            bathrooms = int(bathrooms)
        except ValueError:
            bathrooms = 0

        lat = None
        lon = None
        if latitude:
            try:
                lat = float(latitude)
            except ValueError:
                pass
        if longitude:
            try:
                lon = float(longitude)
            except ValueError:
                pass

        property = Property(
            owner_id=current_user.id,
            title=title,
            description=description,
            property_type=property_type,
            price=price,
            province=province,
            district=district,
            city=city,
            area=area,
            address=address,
            latitude=lat,
            longitude=lon,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            furnished=furnished,
            parking=parking,
            availability_status='available',
            verification_status='pending',
            status='active'
        )
        db.session.add(property)
        db.session.flush()

        # Handle property images
        images = request.files.getlist('images')
        for image in images:
            if image and image.filename:
                path = save_file(image, subfolder='properties')
                if path:
                    prop_image = PropertyImage(property_id=property.id, image_path=path)
                    db.session.add(prop_image)

        # Handle property documents
        document = request.files.get('document')
        doc_type = request.form.get('document_type', '').strip()
        if document and document.filename:
            doc_path = save_file(document, subfolder='documents')
            if doc_path:
                prop_doc = PropertyDocument(
                    property_id=property.id,
                    document_type=doc_type,
                    document_file=doc_path,
                    verification_status='pending'
                )
                db.session.add(prop_doc)

        # Handle amenities
        for amenity_id in selected_amenities:
            try:
                aid = int(amenity_id)
                amenity = Amenity.query.get(aid)
                if amenity:
                    pa = PropertyAmenity(property_id=property.id, amenity_id=aid)
                    db.session.add(pa)
            except ValueError:
                pass

        db.session.commit()

        # Auto-geocode in background if no coords provided manually
        if lat is None or lon is None:
            _geocode_property_async(current_app._get_current_object(), property.id, address, city)

        logger.info('Property added: id=%s title=%r owner=%s',
                    property.id, property.title, current_user.id)
        flash('Property added successfully! It will be visible after verification.', 'success')
        return redirect(url_for('owner.dashboard'))

    return render_template('owner/add_property.html', title='Add Property',
                           amenities=amenities, form_data={})


@owner_bp.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner_id != current_user.id:
        abort(403)

    amenities = Amenity.query.order_by(Amenity.amenity_name).all()
    existing_amenity_ids = {pa.amenity_id for pa in property.amenities.all()}

    if request.method == 'POST':
        property.title = request.form.get('title', '').strip()
        property.description = request.form.get('description', '').strip()
        property.property_type = request.form.get('property_type', '').strip()
        property.province = request.form.get('province', '').strip()
        property.district = request.form.get('district', '').strip()
        property.city = request.form.get('city', '').strip()
        property.area = request.form.get('area', '').strip()
        property.address = request.form.get('address', '').strip()
        property.furnished = request.form.get('furnished') == '1'
        property.parking = request.form.get('parking') == '1'
        property.availability_status = request.form.get('availability_status', 'available').strip()

        try:
            property.price = float(request.form.get('price', 0))
        except ValueError:
            property.price = 0

        try:
            property.bedrooms = int(request.form.get('bedrooms', 0))
        except ValueError:
            property.bedrooms = 0

        try:
            property.bathrooms = int(request.form.get('bathrooms', 0))
        except ValueError:
            property.bathrooms = 0

        lat = request.form.get('latitude', '').strip()
        lon = request.form.get('longitude', '').strip()
        property.latitude = float(lat) if lat else None
        property.longitude = float(lon) if lon else None

        # Update amenities
        PropertyAmenity.query.filter_by(property_id=property.id).delete()
        selected_amenities = request.form.getlist('amenities')
        for amenity_id in selected_amenities:
            try:
                aid = int(amenity_id)
                pa = PropertyAmenity(property_id=property.id, amenity_id=aid)
                db.session.add(pa)
            except ValueError:
                pass

        # Handle new images
        images = request.files.getlist('images')
        for image in images:
            if image and image.filename:
                path = save_file(image, subfolder='properties')
                if path:
                    prop_image = PropertyImage(property_id=property.id, image_path=path)
                    db.session.add(prop_image)

        db.session.commit()

        # Re-geocode if address changed and no manual coords
        if not property.latitude or not property.longitude:
            _geocode_property_async(
                current_app._get_current_object(), property.id,
                property.address or '', property.city or ''
            )

        flash('Property updated successfully!', 'success')
        return redirect(url_for('owner.dashboard'))

    return render_template('owner/edit_property.html', title='Edit Property',
                           property=property, amenities=amenities,
                           existing_amenity_ids=existing_amenity_ids,
                           now_date=__import__('datetime').date.today().isoformat())


@owner_bp.route('/property/<int:property_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.owner_id != current_user.id:
        abort(403)

    db.session.delete(property)
    db.session.commit()
    logger.info('Property deleted: id=%s title=%r by owner=%s',
                property_id, property.title, current_user.id)
    flash('Property deleted successfully.', 'success')
    return redirect(url_for('owner.dashboard'))


@owner_bp.route('/property/<int:property_id>/image/<int:image_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_property_image(property_id, image_id):
    property = Property.query.get_or_404(property_id)
    if property.owner_id != current_user.id:
        abort(403)
    image = PropertyImage.query.get_or_404(image_id)
    if image.property_id != property_id:
        abort(403)
    db.session.delete(image)
    db.session.commit()
    flash('Image removed.', 'info')
    return redirect(url_for('owner.edit_property', property_id=property_id))


@owner_bp.route('/bookings')
@login_required
@owner_required
def bookings():
    from app.models import Booking
    # All bookings for this owner's properties
    bookings = db.session.query(Booking)\
        .join(Property, Booking.property_id == Property.id)\
        .filter(Property.owner_id == current_user.id)\
        .order_by(Booking.created_at.desc()).all()
    pending_count = sum(1 for b in bookings if b.status == 'pending')
    return render_template('owner/bookings.html', title='Booking Requests',
                           bookings=bookings, pending_count=pending_count)


@owner_bp.route('/bookings/<int:booking_id>/respond', methods=['POST'])
@login_required
@owner_required
def respond_booking(booking_id):
    from app.models import Booking
    booking = Booking.query.get_or_404(booking_id)

    # Verify this booking is for the owner's property
    if booking.property.owner_id != current_user.id:
        abort(403)

    action = request.form.get('action')
    if action == 'confirm':
        booking.status = 'confirmed'
        # Mark property as occupied
        booking.property.availability_status = 'occupied'
        db.session.commit()
        # Notify tenant via chat
        from app.models import Chat
        chat = Chat(
            sender_id=current_user.id,
            receiver_id=booking.tenant_id,
            property_id=booking.property_id,
            message=f"✅ Your booking request for '{booking.property.title}' on {booking.move_in_date.strftime('%B %d, %Y')} has been CONFIRMED! Please contact me to arrange the details."
        )
        db.session.add(chat)
        db.session.commit()
        # Email notification
        from app.utils.notifications import notify_booking_confirmed
        notify_booking_confirmed(booking)
        logger.info('Booking confirmed: booking_id=%s property=%s tenant=%s by owner=%s',
                    booking_id, booking.property_id, booking.tenant_id, current_user.id)
        flash('Booking confirmed! The property is now marked as occupied.', 'success')

    elif action == 'reject':
        booking.status = 'rejected'
        db.session.commit()
        from app.models import Chat
        chat = Chat(
            sender_id=current_user.id,
            receiver_id=booking.tenant_id,
            property_id=booking.property_id,
            message=f"❌ Unfortunately, your booking request for '{booking.property.title}' has been declined. Please browse other available properties."
        )
        db.session.add(chat)
        db.session.commit()
        # Email notification
        from app.utils.notifications import notify_booking_rejected
        notify_booking_rejected(booking)
        logger.info('Booking rejected: booking_id=%s property=%s tenant=%s by owner=%s',
                    booking_id, booking.property_id, booking.tenant_id, current_user.id)
        flash('Booking request declined.', 'info')

    return redirect(url_for('owner.bookings'))


@owner_bp.route('/property/<int:property_id>/vacancy/add', methods=['POST'])
@login_required
@owner_required
def add_vacancy(property_id):
    """Add a VacancyCalendar entry for a property."""
    from app.models import VacancyCalendar
    from datetime import date as _date

    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        abort(403)

    available_from = request.form.get('available_from', '').strip()
    available_until = request.form.get('available_until', '').strip()

    if not available_from:
        flash('Available from date is required.', 'danger')
        return redirect(url_for('owner.edit_property', property_id=property_id))

    try:
        from_date = _date.fromisoformat(available_from)
    except ValueError:
        flash('Invalid "available from" date.', 'danger')
        return redirect(url_for('owner.edit_property', property_id=property_id))

    until_date = None
    if available_until:
        try:
            until_date = _date.fromisoformat(available_until)
            if until_date <= from_date:
                flash('"Available until" must be after "available from".', 'danger')
                return redirect(url_for('owner.edit_property', property_id=property_id))
        except ValueError:
            flash('Invalid "available until" date.', 'danger')
            return redirect(url_for('owner.edit_property', property_id=property_id))

    entry = VacancyCalendar(
        property_id=property_id,
        available_from=from_date,
        available_until=until_date,
        status='available',
    )
    db.session.add(entry)
    db.session.commit()
    flash('Availability window added.', 'success')
    return redirect(url_for('owner.edit_property', property_id=property_id))


@owner_bp.route('/property/<int:property_id>/vacancy/<int:entry_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_vacancy(property_id, entry_id):
    """Remove a VacancyCalendar entry."""
    from app.models import VacancyCalendar

    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != current_user.id:
        abort(403)

    entry = VacancyCalendar.query.get_or_404(entry_id)
    if entry.property_id != property_id:
        abort(403)

    db.session.delete(entry)
    db.session.commit()
    flash('Availability window removed.', 'info')
    return redirect(url_for('owner.edit_property', property_id=property_id))

@owner_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@owner_required 
def owner_profile():
    owner_profile = OwnerProfile.query.filter_by(user_id=current_user.id).first()
    if not owner_profile:
        owner_profile = OwnerProfile(user_id=current_user.id, verification_status='pending')
        db.session.add(owner_profile)
        db.session.commit()

    if request.method == 'POST':
        owner_profile.citizenship_number = request.form.get('citizenship_number', '').strip()
        owner_profile.owner_type = request.form.get('owner_type', '').strip()

        front_img = request.files.get('citizenship_front_image')
        back_img = request.files.get('citizenship_back_image')

        if front_img and front_img.filename:
            path = save_file(front_img, subfolder='citizenship')
            if path:
                owner_profile.citizenship_front_image = path

        if back_img and back_img.filename:
            path = save_file(back_img, subfolder='citizenship')
            if path:
                owner_profile.citizenship_back_image = path

        # Update user info
        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        current_user.province = request.form.get('province', '').strip()
        current_user.district = request.form.get('district', '').strip()
        current_user.city = request.form.get('city', '').strip()
        current_user.address = request.form.get('address', '').strip()

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('owner.owner_profile'))

    return render_template('owner/profile.html', title='Owner Profile', owner_profile=owner_profile)