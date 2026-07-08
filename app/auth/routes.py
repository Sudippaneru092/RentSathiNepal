import logging
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm
from app.models import User, OwnerProfile, EmailOTP
from app.utils.logger import log_auth_attempt
from app.utils.rate_limiter import rate_limit
import random
from datetime import datetime, timedelta
from app.auth.forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    VerifyEmailForm
)
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    session
)
from flask import current_app, render_template
from flask_mail import Message
from app import mail
from flask import current_app
from app import mail

logger = logging.getLogger('rentsathi')


"""
Helper function to generate otp for email verification
"""

def generate_otp():
    """Generate a random 6-digit OTP."""
    return str(random.randint(100000, 999999))


"""
Login
"""
@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(requests_per_minute=20, by_user=False)
def login():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and check_password_hash(user.password, form.password.data):
            if user.account_status != 'active':
                log_auth_attempt(form.email.data, False, request.remote_addr)
                logger.warning('Login blocked — suspended account: %s from %s',
                               form.email.data, request.remote_addr)
                flash('Your account has been suspended. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            log_auth_attempt(form.email.data, True, request.remote_addr)
            logger.info('User logged in: %s (id=%s) from %s',
                        user.email, user.id, request.remote_addr)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return _redirect_after_login(user)
        else:
            log_auth_attempt(form.email.data, False, request.remote_addr)
            logger.warning('Failed login attempt for email: %s from %s',
                           form.email.data, request.remote_addr)
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html', title='Login', form=form)


"""
Registration
"""
@auth_bp.route('/register', methods=['GET', 'POST'])
@rate_limit(requests_per_minute=10, by_user=False)
def register():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)

    form = RegisterForm()

    if form.validate_on_submit():

        email = form.email.data.lower().strip()

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("This email is already registered.", "danger")
            return redirect(url_for("auth.register"))

        # Remove any old OTP for this email
        EmailOTP.query.filter_by(email=email).delete()

        otp = generate_otp()

        email_otp = EmailOTP(
            email=email,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )

        db.session.add(email_otp)
        db.session.commit()

        session["pending_registration"] = {
            "full_name": form.full_name.data.strip(),
            "email": email,
            "phone": form.phone.data.strip() if form.phone.data else None,
            "password": generate_password_hash(form.password.data),
            "role": form.role.data
        }

        # Email sending comes next step
        _send_verification_otp(email, otp)
        return redirect(url_for("auth.verify_email"))

    return render_template(
        'auth/register.html',
        title='Register',
        form=form
    )


"""Send the email verification OTP."""

def _send_verification_otp(email, otp):
    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.warning(
            "[DEV] Verification OTP for %s: %s",
            email,
            otp
        )
        return

    msg = Message(
        subject="Verify Your RentSathi Nepal Email",
        recipients=[email],
        html=render_template(
            "auth/email_verification.html",
            otp=otp,
            expiry=current_app.config.get("EMAIL_VERIFY_EXPIRY", 300)
        ),
    )

    mail.send(msg)

@auth_bp.route("/verify-email", methods=["GET", "POST"])
@rate_limit(requests_per_minute=10, by_user=False)
def verify_email():
    print("=== verify_email() entered ===")

    if "pending_registration" not in session:
        print("No pending_registration in session")
        flash("Your registration session has expired. Please register again.", "warning")
        return redirect(url_for("auth.register"))

    form = VerifyEmailForm()
    email = session["pending_registration"]["email"]

    print("Request method:", request.method)
    print("Form data:", request.form)
    print("Form errors:", form.errors)

    form = VerifyEmailForm()
    email = session["pending_registration"]["email"]

    valid = form.validate_on_submit()

    print("validate_on_submit:", valid)
    print("otp.data:", repr(form.otp.data))
    print("form.errors:", form.errors)


    if form.validate_on_submit():

        otp_record = EmailOTP.query.filter_by(email=email).first()

        if not otp_record:
            flash("Verification code not found. Please request a new one.", "danger")
            return redirect(url_for("auth.verify_email"))

        if otp_record.expires_at < datetime.utcnow():
            db.session.delete(otp_record)
            db.session.commit()

            flash("Your verification code has expired. Please request a new one.", "danger")
            return redirect(url_for("auth.verify_email"))

        if otp_record.otp != form.otp.data:
            flash("Invalid verification code.", "danger")
            return redirect(url_for("auth.verify_email"))

        data = session["pending_registration"]

        user = User(
            full_name=data["full_name"],
            email=data["email"],
            phone=data["phone"],
            password=data["password"],
            role=data["role"],
            account_status="active",
            profile_complete=False,
        )

        db.session.add(user)
        db.session.flush()

        if data["role"] == "owner":
            owner_profile = OwnerProfile(
                user_id=user.id,
                verification_status="pending"
            )
            db.session.add(owner_profile)

        db.session.delete(otp_record)
        db.session.commit()

        session.pop("pending_registration", None)

        login_user(user)

        flash(
            f"Welcome to RentSathi Nepal, {user.full_name.split()[0]}!",
            "success"
        )

        return redirect(url_for("auth.complete_profile"))

    return render_template(
        "auth/verify_email.html",
        title="Verify Email",
        form=form,
        email=email
    )

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


# ── PASSWORD RESET ─────────────────────────────────────────────────────────

def _generate_reset_token(user_id):
    """Sign a reset token containing the user id. Expires per config."""
    from itsdangerous import URLSafeTimedSerializer
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(user_id, salt='password-reset-salt')


def _verify_reset_token(token):
    """Return user_id from a valid, unexpired token or None."""
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
    from flask import current_app
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    expiry = current_app.config.get('PASSWORD_RESET_EXPIRY', 3600)
    try:
        user_id = s.loads(token, salt='password-reset-salt', max_age=expiry)
    except (SignatureExpired, BadSignature):
        return None
    return user_id


def _send_reset_email(user, reset_url):
    """Send the password-reset email. Silently skips if mail is not configured."""
    from flask import current_app, render_template
    from flask_mail import Message
    from app import mail

    if not current_app.config.get('MAIL_USERNAME'):
        # Mail not configured — log the URL to console so dev can still test
        current_app.logger.warning(
            '[DEV] Password reset URL (mail not configured): %s', reset_url
        )
        return

    msg = Message(
        subject='Reset Your RentSathi Password',
        recipients=[user.email],
        html=render_template(
            'auth/email_reset_password.html',
            user=user,
            reset_url=reset_url,
            now=__import__('datetime').datetime.utcnow(),
        ),
    )
    mail.send(msg)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@rate_limit(requests_per_minute=5, by_user=False)
def forgot_password():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        # Always show success message — don't reveal whether the email exists
        if user and user.account_status == 'active':
            token = _generate_reset_token(user.id)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            _send_reset_email(user, reset_url)
            logger.info('Password reset requested for: %s from %s',
                        form.email.data, request.remote_addr)
        else:
            logger.info('Password reset attempted for unknown/inactive email: %s from %s',
                        form.email.data, request.remote_addr)
        flash(
            'If that email is registered, you will receive a reset link shortly. '
            'Check your inbox (and spam folder).',
            'info'
        )
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    user_id = _verify_reset_token(token)
    if user_id is None:
        flash('That reset link is invalid or has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.get(user_id)
    if not user or user.account_status != 'active':
        flash('Account not found or suspended.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset! You can now sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form, token=token)
