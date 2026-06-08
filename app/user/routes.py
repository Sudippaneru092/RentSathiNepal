import os
import uuid
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.user import user_bp
from app.models import Favorite, Property, RoommateProfile, Chat, Review


def save_file(file, subfolder='misc'):
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


@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get recent favorites
    recent_favorites = (
        Favorite.query
        .filter_by(user_id=current_user.id)
        .order_by(Favorite.created_at.desc())
        .limit(6)
        .all()
    )
    # Load property info for each favorite
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

    return render_template(
        'user/dashboard.html',
        title='My Dashboard',
        fav_properties=fav_properties,
        recent_messages=recent_messages
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

        db.session.commit()
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


@user_bp.route('/messages')
@login_required
def messages():
    received = (
        Chat.query
        .filter_by(receiver_id=current_user.id)
        .order_by(Chat.sent_at.desc())
        .all()
    )
    sent = (
        Chat.query
        .filter_by(sender_id=current_user.id)
        .order_by(Chat.sent_at.desc())
        .all()
    )
    return render_template('user/messages.html', title='Messages', received=received, sent=sent)
