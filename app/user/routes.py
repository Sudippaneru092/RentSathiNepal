import os
import uuid
import logging
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.user import user_bp
from app.models import Favorite, Property, RoommateProfile, Chat, Review
from sqlalchemy import or_, and_
from app.models import User

logger = logging.getLogger('rentsathi')


def save_file(file, subfolder='misc'):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/gif'}

    if not file or not file.filename:
        return None

    ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return None

    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"Attempted upload of invalid MIME type: {file.content_type}")
        return None

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    
    file.save(os.path.join(folder, unique_name))
    return f"uploads/{subfolder}/{unique_name}"

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Total counts
    total_favorites = Favorite.query.filter_by(user_id=current_user.id).count()
    unread_count = Chat.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    total_properties = Property.query.filter_by(status='active').count()

    recent_favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .limit(4)
        .all()
    )
    fav_properties = [
        Property.query.get(f.property_id) for f in recent_favorites
        if Property.query.get(f.property_id)
    ]

    # Recent messages received
    recent_messages = (
        Chat.query
        .filter_by(receiver_id=current_user.id)
        .order_by(Chat.sent_at.desc())
        .limit(5)
        .all()
    )

    # Roommate profile
    roommate_profile = RoommateProfile.query.filter_by(user_id=current_user.id).first()
    has_roommate_profile = roommate_profile is not None

    return render_template(
        'user/dashboard.html',
        title='My Dashboard',
        fav_properties=fav_properties,
        recent_messages=recent_messages,
        total_favorites=total_favorites,
        total_messages=unread_count,
        total_properties=total_properties,
        has_roommate_profile=has_roommate_profile,
        roommate_profile=roommate_profile,
        fav_count=total_favorites,
        unread_count=unread_count,
    )


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.phone = request.form.get('phone', '').strip()
        current_user.gender = request.form.get('gender', '').strip()
        current_user.occupation = request.form.get('occupation', '').strip()
        current_user.province = request.form.get('province', '').strip()
        current_user.district = request.form.get('district', '').strip()
        current_user.city = request.form.get('city', '').strip()
        current_user.address = request.form.get('address', '').strip()

        # Profile image upload
        profile_img = request.files.get('profile_image')
        if profile_img and profile_img.filename:
            path = save_file(profile_img, subfolder='profiles')
            if path:
                current_user.profile_image = path

        # Password change (optional)
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_new = request.form.get('confirm_new_password', '').strip()

        if current_password:
            if not check_password_hash(current_user.password, current_password):
                logger.warning('Failed password change attempt for user %s from %s',
                               current_user.id, request.remote_addr)
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('user.profile'))
            if not new_password:
                flash('New password cannot be empty.', 'danger')
                return redirect(url_for('user.profile'))
            if new_password != confirm_new:
                flash('New passwords do not match.', 'danger')
                return redirect(url_for('user.profile'))
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return redirect(url_for('user.profile'))
            current_user.password = generate_password_hash(new_password)
            logger.info('Password changed for user %s', current_user.id)

        db.session.commit()
        logger.info('Profile updated for user %s', current_user.id)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', title='My Profile')


@user_bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .paginate(page=page, per_page=9, error_out=False)
    )
    fav_properties = [Property.query.get(f.property_id) for f in favorites.items]
    fav_properties = [p for p in fav_properties if p]

    return render_template(
        'user/favorites.html',
        title='My Favorites',
        favorites=favorites,
        fav_properties=fav_properties
    )


@user_bp.route('/roommate-profile', methods=['GET', 'POST'])
@login_required
def roommate_profile():
    rp = RoommateProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == 'POST':
        preferred_city = request.form.get('preferred_city', '').strip()
        budget = request.form.get('budget', '').strip()
        occupation = request.form.get('occupation', '').strip()
        gender_preference = request.form.get('gender_preference', '').strip()
        smoking_preference = request.form.get('smoking_preference', '').strip()
        drinking_preference = request.form.get('drinking_preference', '').strip()
        lifestyle = request.form.get('lifestyle', '').strip()
        bio = request.form.get('bio', '').strip()

        budget_val = None
        if budget:
            try:
                budget_val = float(budget)
            except ValueError:
                flash('Budget must be a valid number.', 'danger')
                return redirect(url_for('user.roommate_profile'))

        if rp:
            rp.preferred_city = preferred_city
            rp.budget = budget_val
            rp.occupation = occupation
            rp.gender_preference = gender_preference
            rp.smoking_preference = smoking_preference
            rp.drinking_preference = drinking_preference
            rp.lifestyle = lifestyle
            rp.bio = bio
        else:
            rp = RoommateProfile(
                user_id=current_user.id,
                preferred_city=preferred_city,
                budget=budget_val,
                occupation=occupation,
                gender_preference=gender_preference,
                smoking_preference=smoking_preference,
                drinking_preference=drinking_preference,
                lifestyle=lifestyle,
                bio=bio
            )
            db.session.add(rp)

        db.session.commit()
        flash('Roommate profile saved!', 'success')
        return redirect(url_for('user.roommate_profile'))

    return render_template('user/roommate_profile.html', title='Roommate Profile', rp=rp)

@user_bp.route('/bookings')
@login_required
def my_bookings():
    from app.models import Booking
    bookings = Booking.query.filter_by(tenant_id=current_user.id)\
                            .order_by(Booking.created_at.desc()).all()
    return render_template('user/bookings.html', title='My Bookings', bookings=bookings)


@user_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    from app.models import Booking
    booking = Booking.query.get_or_404(booking_id)
    if booking.tenant_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('user.my_bookings'))
    if booking.status not in ('pending',):
        flash('Only pending bookings can be cancelled.', 'warning')
        return redirect(url_for('user.my_bookings'))
    booking.status = 'cancelled'
    db.session.commit()
    logger.info('Booking cancelled: booking_id=%s by tenant=%s', booking_id, current_user.id)
    flash('Booking request cancelled.', 'info')
    return redirect(url_for('user.my_bookings'))


# ── ROOMMATE BROWSE ────────────────────────────────────────────────────────

@user_bp.route('/roommates')
def roommates():
    """
    Public browse page — anyone can see profiles, login required to view details.
    Filters: city, gender_preference, max_budget, occupation keyword.
    """
    from app.models import User as UserModel

    city       = request.args.get('city', '').strip()
    gender     = request.args.get('gender', '').strip()
    max_budget = request.args.get('max_budget', '').strip()
    keyword    = request.args.get('q', '').strip()
    page       = request.args.get('page', 1, type=int)

    query = RoommateProfile.query

    if city:
        query = query.filter(RoommateProfile.preferred_city.ilike(f'%{city}%'))
    if gender:
        query = query.filter_by(gender_preference=gender)
    if max_budget:
        try:
            query = query.filter(RoommateProfile.budget <= float(max_budget))
        except ValueError:
            pass
    if keyword:
        like = f'%{keyword}%'
        query = query.filter(
            db.or_(
                RoommateProfile.occupation.ilike(like),
                RoommateProfile.bio.ilike(like),
                RoommateProfile.lifestyle.ilike(like),
            )
        )

    # Exclude the current user's own profile from browse
    if current_user.is_authenticated:
        query = query.filter(RoommateProfile.user_id != current_user.id)

    # Only show profiles belonging to active user accounts
    query = query.join(UserModel, RoommateProfile.user_id == UserModel.id)\
                 .filter(UserModel.account_status == 'active')

    profiles = query.order_by(RoommateProfile.created_at.desc())\
                    .paginate(page=page, per_page=12, error_out=False)

    # Stats for hero
    total_profiles = RoommateProfile.query.join(UserModel)\
        .filter(UserModel.account_status == 'active').count()

    # Distinct cities for filter dropdown
    cities = db.session.query(RoommateProfile.preferred_city)\
        .filter(RoommateProfile.preferred_city.isnot(None),
                RoommateProfile.preferred_city != '')\
        .distinct().order_by(RoommateProfile.preferred_city).all()
    cities = [c[0] for c in cities]

    search_params = {k: v for k, v in request.args.items() if k != 'page'}

    return render_template(
        'user/roommates.html',
        title='Find a Roommate',
        profiles=profiles,
        total_profiles=total_profiles,
        cities=cities,
        search_params=search_params,
        city=city, gender=gender,
        max_budget=max_budget, keyword=keyword,
    )


@user_bp.route('/roommates/<int:profile_id>')
def roommate_view(profile_id):
    """View a single roommate profile."""
    from app.models import User as UserModel
    rp = RoommateProfile.query.get_or_404(profile_id)
    owner = UserModel.query.get_or_404(rp.user_id)
    if owner.account_status != 'active':
        flash('This profile is no longer available.', 'warning')
        return redirect(url_for('user.roommates'))
    return render_template(
        'user/roommate_view.html',
        title=f'{owner.full_name} — Roommate Profile',
        rp=rp,
        owner=owner,
    )