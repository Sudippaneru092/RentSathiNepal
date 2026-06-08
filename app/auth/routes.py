from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User, OwnerProfile


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.account_status != 'active':
                flash('Your account has been suspended. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return _redirect_after_login(user)
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', title='Login', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            password=generate_password_hash(form.password.data),
            role=form.role.data,
            account_status='active',
            profile_complete=False,      # new users must complete profile
        )
        db.session.add(user)
        db.session.flush()

        if form.role.data == 'owner':
            owner_profile = OwnerProfile(
                user_id=user.id,
                verification_status='pending'
            )
            db.session.add(owner_profile)

        db.session.commit()
        login_user(user)   # log them in immediately after register
        flash(f'Welcome to RentSathi Nepal, {user.full_name.split()[0]}! Let\'s set up your profile.', 'success')
        # Send directly to profile completion
        return redirect(url_for('auth.complete_profile'))

    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/complete-profile', methods=['GET', 'POST'])
@login_required
def complete_profile():
    # If already complete, send to dashboard
    if current_user.profile_complete:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        # Common fields
        current_user.phone        = request.form.get('phone', '').strip()
        current_user.gender       = request.form.get('gender', '').strip()
        current_user.occupation   = request.form.get('occupation', '').strip()
        current_user.province     = request.form.get('province', '').strip()
        current_user.district     = request.form.get('district', '').strip()
        current_user.city         = request.form.get('city', '').strip()
        current_user.address      = request.form.get('address', '').strip()

        # Owner-specific
        if current_user.role == 'owner':
            op = current_user.owner_profile
            if op:
                op.citizenship_number = request.form.get('citizenship_number', '').strip()
                op.owner_type         = request.form.get('owner_type', '').strip()

        current_user.profile_complete = True
        db.session.commit()

        flash('Profile completed! Welcome to RentSathi Nepal.', 'success')
        return _redirect_by_role(current_user.role)

    return render_template('auth/complete_profile.html',
                           title='Complete Your Profile')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/skip-profile')
@login_required
def skip_profile():
    """Allow user to skip profile completion and go straight to dashboard."""
    current_user.profile_complete = True   # mark done so they aren't redirected again
    db.session.commit()
    flash('You can complete your profile anytime from Settings.', 'info')
    return _redirect_by_role(current_user.role)


def _redirect_after_login(user):
    """After login: send incomplete profiles to completion page, others to dashboard."""
    if not user.profile_complete and user.role != 'admin':
        return redirect(url_for('auth.complete_profile'))
    return _redirect_by_role(user.role)


def _redirect_by_role(role):
    if role == 'owner':
        return redirect(url_for('owner.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('user.dashboard'))
