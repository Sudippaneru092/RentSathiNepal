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
    property = Property.query.get_or_404(property_id)
    action = request.form.get('action')
    if action == 'verify':
        property.verification_status = 'verified'
        db.session.commit()
        flash(f'Property "{property.title}" has been verified.', 'success')
        log_action('verify_property', f'Verified property ID {property_id}: {property.title}')
        logger.info('Admin %s verified property id=%s "%s"',
                    current_user.id, property_id, property.title)
        from app.utils.notifications import notify_property_verified
        notify_property_verified(property)
    elif action == 'reject':
        property.verification_status = 'rejected'
        db.session.commit()
        flash(f'Property "{property.title}" has been rejected.', 'warning')
        log_action('reject_property', f'Rejected property ID {property_id}: {property.title}')
        logger.info('Admin %s rejected property id=%s "%s"',
                    current_user.id, property_id, property.title)
        from app.utils.notifications import notify_property_rejected
        notify_property_rejected(property)
    return redirect(url_for('admin.properties'))


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
        return redirect(url_for('admin.users'))
    if user.account_status == 'active':
        user.account_status = 'suspended'
        flash(f'User {user.full_name} has been suspended.', 'warning')
        log_action('suspend_user', f'Suspended user ID {user_id}: {user.email}')
        logger.info('Admin %s suspended user id=%s %s',
                    current_user.id, user_id, user.email)
    else:
        user.account_status = 'active'
        flash(f'User {user.full_name} has been activated.', 'success')
        log_action('activate_user', f'Activated user ID {user_id}: {user.email}')
        logger.info('Admin %s activated user id=%s %s',
                    current_user.id, user_id, user.email)
    db.session.commit()
    return redirect(url_for('admin.users'))


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
    owner = OwnerProfile.query.get_or_404(owner_id)
    action = request.form.get('action')
    if action == 'verify':
        owner.verification_status = 'verified'
        db.session.commit()
        flash('Owner has been verified.', 'success')
        log_action('verify_owner', f'Verified owner profile ID {owner_id}')
        logger.info('Admin %s verified owner profile id=%s user=%s',
                    current_user.id, owner_id, owner.user_id)
        from app.utils.notifications import notify_owner_verified
        notify_owner_verified(owner)
    elif action == 'reject':
        owner.verification_status = 'rejected'
        db.session.commit()
        flash('Owner has been rejected.', 'warning')
        log_action('reject_owner', f'Rejected owner profile ID {owner_id}')
        logger.info('Admin %s rejected owner profile id=%s user=%s',
                    current_user.id, owner_id, owner.user_id)
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
