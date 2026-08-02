from functools import wraps
import logging
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.models import User, Property, OwnerProfile, Report, AdminLog, Review
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger('rentsathi')


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        abort(403)
 
    user = User.query.get_or_404(user_id)
 
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', user.full_name).strip()
 
        new_email = request.form.get('email', user.email).strip().lower()
        if new_email != user.email:
            existing = User.query.filter(User.email == new_email, User.id != user.id).first()
            if existing:
                flash('That email is already in use by another account.', 'danger')
                return redirect(url_for('admin.edit_user', user_id=user.id))
            user.email = new_email
 
        user.phone = request.form.get('phone', '').strip() or None
        user.gender = request.form.get('gender') or None
        user.occupation = request.form.get('occupation', '').strip() or None
        user.province = request.form.get('province', '').strip() or None
        user.district = request.form.get('district', '').strip() or None
        user.city = request.form.get('city', '').strip() or None
        user.address = request.form.get('address', '').strip() or None
 
        new_role = request.form.get('role')
        if new_role in ('user', 'owner', 'admin'):
            if user.id == current_user.id and new_role != 'admin':
                flash("You can't remove your own admin role.", 'warning')
            else:
                user.role = new_role
 
        new_status = request.form.get('account_status')
        if new_status in ('active', 'suspended'):
            user.account_status = new_status
 
        user.profile_complete = 'profile_complete' in request.form
 
        db.session.commit()
        flash(f"{user.full_name}'s details were updated.", 'success')
        return redirect(url_for('admin.edit_user', user_id=user.id))
 
    return render_template('admin/edit_user.html', user=user)
 
 
@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
def reset_user_password(user_id):
    if current_user.role != 'admin':
        abort(403)
 
    user = User.query.get_or_404(user_id)
 
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
 
    if len(new_password) < 8:
        flash('Password must be at least 8 characters long.', 'danger')
        return redirect(url_for('admin.edit_user', user_id=user.id))
 
    if new_password != confirm_password:
        flash('Passwords do not match.', 'danger')
        return redirect(url_for('admin.edit_user', user_id=user.id))
 
    # Same hashing function used at registration (app/auth/routes.py)
    user.password = generate_password_hash(new_password)
    db.session.commit()
 
    flash(f'Password reset for {user.full_name}.', 'success')
    return redirect(url_for('admin.edit_user', user_id=user.id))
 
 
@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()

    if user.role == "admin":
        flash("Admin accounts cannot be deleted.", "danger")
        return redirect(url_for("admin.edit_user", user_id=user.id))

    user.soft_delete()
    db.session.commit()

    flash("User deleted successfully.", "success")
    return redirect(url_for("admin.users"))
    
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/users/<int:user_id>/restore", methods=["POST"])
@login_required
@admin_required
def restore_user(user_id):
    user = User.query.filter_by(id=user_id, is_deleted=True).first_or_404()

    user.restore()
    db.session.commit()

    flash("User restored successfully.", "success")
    return redirect(url_for("admin.users"))

def log_action(action, description=None):
    log = AdminLog(admin_id=current_user.id, action=action, description=description)
    db.session.add(log)
    db.session.commit()


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.filter_by(role='user').count()
    total_owners = User.query.filter_by(role='owner').count()
    total_properties = Property.query.count()
    pending_properties = Property.query.filter_by(verification_status='pending').count()
    pending_owners = OwnerProfile.query.filter_by(verification_status='pending').count()
    pending_reports = Report.query.filter_by(status='pending').count()

    recent_logs = AdminLog.query.order_by(AdminLog.created_at.desc()).limit(10).all()
    recent_properties = Property.query.filter_by(verification_status='pending').order_by(
        Property.created_at.desc()).limit(5).all()
    recent_reports = Report.query.filter_by(status='pending').order_by(
        Report.created_at.desc()).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        total_users=total_users,
        total_owners=total_owners,
        total_properties=total_properties,
        pending_properties=pending_properties,
        pending_owners=pending_owners,
        pending_reports=pending_reports,
        recent_logs=recent_logs,
        recent_properties=recent_properties,
        recent_reports=recent_reports
    )


@admin_bp.route('/properties')
@login_required
@admin_required
def properties():
    status_filter = request.args.get('status', '')
    verification_filter = request.args.get('verification', '')
    page = request.args.get('page', 1, type=int)

    query = Property.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if verification_filter:
        query = query.filter_by(verification_status=verification_filter)

    properties = query.order_by(Property.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/properties.html', title='Manage Properties',
                           properties=properties, status_filter=status_filter,
                           verification_filter=verification_filter)


@admin_bp.route('/properties/<int:property_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_property(property_id):
    """Quick action route for the Verify/Reject buttons in the table."""
    prop = Property.query.get_or_404(property_id)
    action = request.form.get('action')

    if action == 'verify':
        prop.verification_status = 'verified'
        db.session.commit()
        flash(f'Property "{prop.title}" has been verified.', 'success')
        log_action('quick_verify_property', f'Verified property ID {property_id}')
        from app.utils.notifications import notify_property_verified
        notify_property_verified(prop)
        
    elif action == 'reject':
        prop.verification_status = 'rejected'
        db.session.commit()
        flash(f'Property "{prop.title}" has been rejected.', 'warning')
        log_action('quick_reject_property', f'Rejected property ID {property_id}')
        from app.utils.notifications import notify_property_rejected
        notify_property_rejected(prop)
        
    return redirect(url_for('admin.properties'))

@admin_bp.route('/properties/<int:property_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_property_status(property_id):
    """Suspends or Activates a property (sets status to active/inactive)."""
    prop = Property.query.get_or_404(property_id)
    
    if prop.status == 'active':
        prop.status = 'inactive'
        flash(f'Property "{prop.title}" has been suspended.', 'warning')
        log_action('suspend_property', f'Suspended property ID {property_id}: {prop.title}')
    else:
        prop.status = 'active'
        flash(f'Property "{prop.title}" has been activated.', 'success')
        log_action('activate_property', f'Activated property ID {property_id}: {prop.title}')
    
    db.session.commit()
    return redirect(request.referrer or url_for('admin.properties'))

@admin_bp.route('/properties/<int:property_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_property(property_id):
    """Soft delete a property."""
    prop = Property.query.get_or_404(property_id)
    title = prop.title
    prop.soft_delete()
    db.session.commit()
    log_action('delete_property', f'Deleted property: {title}')
    flash(f'Property "{title}" has been removed.', 'success')
    return redirect(url_for('admin.properties'))


@admin_bp.route('/properties/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_property(property_id):
    prop = Property.query.get_or_404(property_id)
    from app.models import Amenity, PropertyAmenity 
    all_amenities = Amenity.query.all()

    # --- THE FIX IS HERE ---
    # We need the amenity_id from the junction table, NOT the id of the junction record itself
    existing_amenity_ids = [link.amenity_id for link in prop.amenities.all()]
    # -----------------------

    if request.method == 'POST':
        try:
            # 1. Update all your standard property fields
            prop.title = request.form.get('title', prop.title).strip()
            prop.description = request.form.get('description', prop.description)
            prop.property_type = request.form.get('property_type', prop.property_type)
            prop.price = float(request.form.get('price', prop.price))
            prop.province = request.form.get('province', prop.province)
            prop.district = request.form.get('district', prop.district)
            prop.city = request.form.get('city', prop.city)
            prop.address = request.form.get('address', prop.address)
            prop.bedrooms = int(request.form.get('bedrooms', prop.bedrooms or 0))
            prop.bathrooms = int(request.form.get('bathrooms', prop.bathrooms or 0))
            prop.area = request.form.get('area', prop.area)
            prop.furnished = 'furnished' in request.form
            prop.parking = 'parking' in request.form

            # 2. Update Amenities (Add/Remove)
            selected_amenity_ids = request.form.getlist('amenities')
            
            # Wipe old links
            PropertyAmenity.query.filter_by(property_id=prop.id).delete()
            
            # Add new links from the checkboxes
            for a_id in selected_amenity_ids:
                new_link = PropertyAmenity(property_id=prop.id, amenity_id=int(a_id))
                db.session.add(new_link)

            # 3. Update Verification
            new_status = request.form.get('verification_status')
            if new_status in ['pending', 'verified', 'rejected']:
                if prop.verification_status != new_status:
                    old_status = prop.verification_status
                    prop.verification_status = new_status
                    log_action('change_property_status', f'Property {prop.id} status: {old_status} -> {new_status}')
                    if new_status == 'verified':
                        from app.utils.notifications import notify_property_verified
                        notify_property_verified(prop)

            db.session.commit()
            flash(f"Property '{prop.title}' updated successfully.", "success")
            return redirect(url_for('admin.properties'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error: {str(e)}")
            flash("Error saving changes.", "danger")
            return redirect(url_for('admin.properties'))

    return render_template('admin/edit_property.html', 
                           prop=prop, 
                           all_amenities=all_amenities, 
                           existing_amenity_ids=existing_amenity_ids)



@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if status_filter:
        query = query.filter_by(account_status=status_filter)

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', title='Manage Users', users=users,
                           role_filter=role_filter, status_filter=status_filter)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot change status of admin accounts.', 'danger')
        return redirect(request.referrer or url_for('admin.users'))

    if user.account_status == 'active':
        user.account_status = 'suspended'
        flash(f'User {user.full_name} has been suspended.', 'warning')
        log_action('suspend_user', f'Suspended user ID {user_id}: {user.email}')
    else:
        user.account_status = 'active'
        flash(f'User {user.full_name} has been activated.', 'success')
        log_action('activate_user', f'Activated user ID {user_id}: {user.email}')
    
    db.session.commit()
    # Use request.referrer so the admin stays on the page they are currently viewing
    return redirect(request.referrer or url_for('admin.users'))

@admin_bp.route('/owners/<int:owner_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_owner(owner_id):
    """Master Edit Route: Handles User and OwnerProfile updates together."""
    owner = OwnerProfile.query.get_or_404(owner_id)
    user = owner.user 

    if request.method == 'POST':
        try:
            # --- Update User Model (Personal Details) ---
            user.full_name = request.form.get('full_name', user.full_name).strip()
            
            # Email Uniqueness Check
            new_email = request.form.get('email', user.email).strip().lower()
            if new_email != user.email:
                if User.query.filter(User.email == new_email, User.id != user.id).first():
                    flash('This email is already in use by another account.', 'danger')
                    return redirect(url_for('admin.edit_owner', owner_id=owner_id))
                user.email = new_email

            user.phone = request.form.get('phone', '').strip() or None
            user.gender = request.form.get('gender') or None
            user.occupation = request.form.get('occupation', '').strip() or None
            user.province = request.form.get('province', '').strip() or None
            user.district = request.form.get('district', '').strip() or None
            user.city = request.form.get('city', '').strip() or None
            user.address = request.form.get('address', '').strip() or None
            user.account_status = request.form.get('account_status', user.account_status)

            # --- Update OwnerProfile Model (Business Details) ---
            owner.citizenship_number = request.form.get('citizenship_number', owner.citizenship_number).strip() or None
            owner.owner_type = request.form.get('owner_type', owner.owner_type)
            
            # --- Handle Verification Decision (Reject to Accept logic) ---
            new_status = request.form.get('verification_status')
            if new_status in ['pending', 'verified', 'rejected']:
                if owner.verification_status != new_status:
                    old_status = owner.verification_status
                    owner.verification_status = new_status
                    log_action('change_owner_status', f'Owner {user.email} changed from {old_status} to {new_status}')
                    
                    # Notify owner if they were just verified
                    if new_status == 'verified':
                        from app.utils.notifications import notify_owner_verified
                        notify_owner_verified(owner)

            db.session.commit()
            flash(f"Successfully updated profile for {user.full_name}", "success")
            return redirect(url_for('admin.owners'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating owner {owner_id}: {str(e)}")
            flash("An error occurred while saving changes.", "danger")
            return redirect(url_for('admin.owners'))

    return render_template('admin/edit_owners.html', owner=owner, user=user)




@admin_bp.route('/owners')
@login_required
@admin_required
def owners():
    verification_filter = request.args.get('verification', '')
    page = request.args.get('page', 1, type=int)

    query = OwnerProfile.query
    if verification_filter:
        query = query.filter_by(verification_status=verification_filter)

    owners = query.order_by(OwnerProfile.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/owners.html', title='Manage Owners', owners=owners,
                           verification_filter=verification_filter)


@admin_bp.route('/owners/<int:owner_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_owner(owner_id):
    """Quick action route for the 'Verify' and 'Reject' buttons in the table."""
    owner = OwnerProfile.query.get_or_404(owner_id)
    action = request.form.get('action')

    if action == 'verify':
        owner.verification_status = 'verified'
        db.session.commit()
        flash(f'Owner {owner.user.full_name} has been verified.', 'success')
        log_action('quick_verify_owner', f'Verified owner ID {owner_id}')
        from app.utils.notifications import notify_owner_verified
        notify_owner_verified(owner)
    elif action == 'reject':
        owner.verification_status = 'rejected'
        db.session.commit()
        flash(f'Owner {owner.user.full_name} has been rejected.', 'warning')
        log_action('quick_reject_owner', f'Rejected owner ID {owner_id}')
        from app.utils.notifications import notify_owner_rejected
        notify_owner_rejected(owner)
        
    return redirect(url_for('admin.owners'))

@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    status_filter = request.args.get('status', 'pending')
    page = request.args.get('page', 1, type=int)

    query = Report.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    reports = query.order_by(Report.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/reports.html', title='Reports', reports=reports,
                           status_filter=status_filter)


@admin_bp.route('/reports/<int:report_id>/update', methods=['POST'])
@login_required
@admin_required
def update_report(report_id):
    report = Report.query.get_or_404(report_id)
    new_status = request.form.get('status')
    if new_status in ('reviewed', 'resolved', 'pending'):
        report.status = new_status
        db.session.commit()
        log_action('update_report', f'Updated report ID {report_id} status to {new_status}')
        flash('Report status updated.', 'success')
    return redirect(url_for('admin.reports'))


@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    page = request.args.get('page', 1, type=int)
    logs = AdminLog.query.order_by(AdminLog.created_at.desc()).paginate(page=page, per_page=30, error_out=False)
    return render_template('admin/logs.html', title='Admin Logs', logs=logs)


@admin_bp.route('/amenities', methods=['GET', 'POST'])
@login_required
@admin_required
def amenities():
    from app.models import Amenity
    if request.method == 'POST':
        name = request.form.get('amenity_name', '').strip()
        if name:
            existing = Amenity.query.filter_by(amenity_name=name).first()
            if existing:
                flash('Amenity already exists.', 'warning')
            else:
                amenity = Amenity(amenity_name=name)
                db.session.add(amenity)
                db.session.commit()
                log_action('add_amenity', f'Added amenity: {name}')
                flash(f'Amenity "{name}" added.', 'success')
        else:
            flash('Amenity name cannot be empty.', 'danger')

    all_amenities = Amenity.query.order_by(Amenity.amenity_name).all()
    return render_template('admin/amenities.html', title='Manage Amenities', amenities=all_amenities)


@admin_bp.route('/amenities/<int:amenity_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_amenity(amenity_id):
    from app.models import Amenity
    amenity = Amenity.query.get_or_404(amenity_id)
    name = amenity.amenity_name
    db.session.delete(amenity)
    db.session.commit()
    log_action('delete_amenity', f'Deleted amenity: {name}')
    flash(f'Amenity "{name}" deleted.', 'info')
    return redirect(url_for('admin.amenities'))

import os
from werkzeug.utils import secure_filename
# ... (your other imports)

# Assuming you have this configured in your app
# UPLOAD_FOLDER = 'static/uploads/citizenship' 

@admin_bp.route('/owners/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_owner():
    if request.method == 'POST':
        try:
            # 1. Extract User Data
            full_name = request.form.get('full_name').strip()
            email = request.form.get('email').strip().lower()
            phone = request.form.get('phone', '').strip() or None
            password = request.form.get('password')
            gender = request.form.get('gender')
            occupation = request.form.get('occupation', '').strip() or None
            province = request.form.get('province', '').strip() or None
            district = request.form.get('district', '').strip() or None
            city = request.form.get('city', '').strip() or None
            address = request.form.get('address', '').strip() or None

            # 2. Extract Owner Profile Data
            citizenship_number = request.form.get('citizenship_number', '').strip() or None
            owner_type = request.form.get('owner_type')

            # Validation: Check if email exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'danger')
                return redirect(url_for('admin.create_owner'))

            # Validation: Password length
            if len(password) < 8:
                flash('Password must be at least 8 characters.', 'danger')
                return redirect(url_for('admin.create_owner'))

            # 3. Create User Object
            new_user = User(
                full_name=full_name,
                email=email,
                phone=phone,
                password=generate_password_hash(password),
                role='owner', # Force role to owner
                gender=gender,
                occupation=occupation,
                province=province,
                district=district,
                city=city,
                address=address,
                account_status='active'
            )
            db.session.add(new_user)
            db.session.flush() # Get the new_user.id before committing

            # 4. Handle File Uploads (Citizenship Images)
            front_img_path = None
            back_img_path = None
            
            # Helper to handle file saving (Adjust 'app.config['UPLOAD_FOLDER']' as per your app)
            def save_file(file):
                if file and file.filename != '':
                    filename = secure_filename(f"owner_{new_user.id}_{file.filename}")
                    # Change this path to your actual upload directory
                    save_path = os.path.join('static/uploads/citizenship', filename)
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    file.save(save_path)
                    return f"uploads/citizenship/{filename}"
                return None

            front_img_path = save_file(request.files.get('citizenship_front'))
            back_img_path = save_file(request.files.get('citizenship_back'))

            # 5. Create Owner Profile Object
            new_owner_profile = OwnerProfile(
                user_id=new_user.id,
                citizenship_number=citizenship_number,
                owner_type=owner_type,
                citizenship_front_image=front_img_path,
                citizenship_back_image=back_img_path,
                verification_status='pending' # New owners start as pending
            )
            db.session.add(new_owner_profile)

            db.session.commit()
            log_action('create_owner', f'Admin created new owner: {email}')
            flash(f'Owner {full_name} created successfully.', 'success')
            return redirect(url_for('admin.owners'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating owner: {str(e)}")
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('admin.create_owner'))

    return render_template('admin/add_owner.html', title='Add New Owner')


import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        try:
            # 1. Extract Data
            full_name = request.form.get('full_name').strip()
            email = request.form.get('email').strip().lower()
            phone = request.form.get('phone', '').strip() or None
            password = request.form.get('password')
            role = request.form.get('role')  # Will be 'user' or 'admin'
            account_status = request.form.get('account_status', 'active')
            
            # Personal Details
            gender = request.form.get('gender')
            occupation = request.form.get('occupation', '').strip() or None
            province = request.form.get('province', '').strip() or None
            district = request.form.get('district', '').strip() or None
            city = request.form.get('city', '').strip() or None
            address = request.form.get('address', '').strip() or None

            # 2. Validations
            if User.query.filter_by(email=email).first():
                flash('This email is already registered.', 'danger')
                return redirect(url_for('admin.create_user'))

            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'danger')
                return redirect(url_for('admin.create_user'))

            if role not in ['user', 'admin']:
                flash('Invalid role selected.', 'danger')
                return redirect(url_for('admin.create_user'))

            # 3. Create User
            new_user = User(
                full_name=full_name,
                email=email,
                phone=phone,
                password=generate_password_hash(password),
                role=role,
                account_status=account_status,
                gender=gender,
                occupation=occupation,
                province=province,
                district=district,
                city=city,
                address=address,
                profile_complete=True # Since admin is creating it, we assume it's complete
            )

            db.session.add(new_user)
            db.session.commit()
            
            log_action('create_user_by_admin', f'Admin created {role}: {email}')
            flash(f'User {full_name} created successfully as {role}.', 'success')
            return redirect(url_for('admin.users'))

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('admin.create_user'))

    return render_template('admin/create_user.html', title='Create New User')