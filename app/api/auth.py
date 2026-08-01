import jwt
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, current_app, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

from app import db, mail
from app.models import User, OwnerProfile, EmailOTP
from app.api.helpers import api_response, token_required
from app.utils.logger import log_auth_attempt
from app.utils.rate_limiter import rate_limit

api_auth = Blueprint('auth', __name__)

# ==============================================================================
# INTERNAL HELPERS (Reusing Business Logic)
# ==============================================================================

def create_token(user_id):
    """Generates a JWT token for the Android app"""
    payload = {
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow(),
        'user_id': user_id
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def _send_verification_otp(email, otp):
    """Reuses the exact email logic from auth/routes.py"""
    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.warning("[DEV] Verification OTP for %s: %s", email, otp)
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

# ==============================================================================
# API ENDPOINTS
# ==============================================================================

@api_auth.route('/register', methods=['POST'])
@rate_limit(requests_per_minute=10, by_user=False)
def register():
    data = request.get_json()
    
    # Validation (Replacing RegisterForm)
    required = ['full_name', 'email', 'password', 'role']
    if not all(k in data for k in required):
        return api_response("error", "Missing required fields", code=400)

    email = data['email'].lower().strip()
    
    if User.query.filter_by(email=email).first():
        return api_response("error", "This email is already registered", code=400)

    try:
        # API Logic: Create user immediately with 'pending_verification' status
        # This replaces the use of session["pending_registration"]
        new_user = User(
            full_name=data['full_name'].strip(),
            email=email,
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            password=generate_password_hash(data['password']),
            role=data['role'],
            account_status='pending_verification',
            profile_complete=False
        )
        db.session.add(new_user)
        db.session.flush() # Get user.id

        if data['role'] == 'owner':
            owner_profile = OwnerProfile(user_id=new_user.id, verification_status="pending")
            db.session.add(owner_profile)

        # Handle OTP
        EmailOTP.query.filter_by(email=email).delete()
        otp = str(random.randint(100000, 999999))
        email_otp = EmailOTP(
            email=email,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        db.session.add(email_otp)
        db.session.commit()

        _send_verification_otp(email, otp)
        return api_response("success", "Verification OTP sent to email", data={"user_id": new_user.id})
    
    except Exception as e:
        db.session.rollback()
        return api_response("error", str(e), code=500)

@api_auth.route('/verify-email', methods=['POST'])
@rate_limit(requests_per_minute=10, by_user=False)
def verify_email():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    otp_input = data.get('otp', '').strip()

    if not email or not otp_input:
        return api_response("error", "Email and OTP are required", code=400)

    otp_record = EmailOTP.query.filter_by(email=email).first()

    if not otp_record:
        return api_response("error", "Verification code not found", code=404)

    if otp_record.expires_at < datetime.utcnow():
        db.session.delete(otp_record)
        db.session.commit()
        return api_response("error", "Verification code expired", code=400)

    if otp_record.otp != otp_input:
        return api_response("error", "Invalid verification code", code=400)

    # Success: Activate the user
    user = User.query.filter_by(email=email).first()
    if user:
        user.account_status = 'active'
        db.session.delete(otp_record)
        db.session.commit()
        
        token = create_token(user.id)
        return api_response("success", "Email verified successfully", data={"token": token})

    return api_response("error", "User not found", code=404)

@api_auth.route('/login', methods=['POST'])
@rate_limit(requests_per_minute=20, by_user=False)
def login():
    data = request.get_json()
    email = data.get('email', '').lower().strip()
    password = data.get('password', '')

    if not email or not password:
        return api_response("error", "Email and password are required", code=400)

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        if user.account_status != 'active':
            log_auth_attempt(email, False, request.remote_addr)
            return api_response("error", "Your account is suspended or not verified", code=403)

        log_auth_attempt(email, True, request.remote_addr)
        token = create_token(user.id)
        
        return api_response("success", "Login successful", data={
            "token": token,
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role,
                "profile_complete": user.profile_complete
            }
        })
    
    log_auth_attempt(email, False, request.remote_addr)
    return api_response("error", "Invalid email or password", code=401)

@api_auth.route('/complete-profile', methods=['POST'])
@token_required
def complete_profile(current_user):
    data = request.get_json()

    # Update common fields (Reusing logic from complete_profile route)
    current_user.phone = data.get('phone', current_user.phone).strip()
    current_user.gender = data.get('gender', '').strip()
    current_user.occupation = data.get('occupation', '').strip()
    current_user.province = data.get('province', '').strip()
    current_user.district = data.get('district', '').strip()
    current_user.city = data.get('city', '').strip()
    current_user.address = data.get('address', '').strip()

    # Owner-specific fields
    if current_user.role == 'owner':
        op = current_user.owner_profile
        if op:
            op.citizenship_number = data.get('citizenship_number', '').strip()
            op.owner_type = data.get('owner_type', '').strip()

    current_user.profile_complete = True
    db.session.commit()

    return api_response("success", "Profile completed successfully")

@api_auth.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    return api_response("success", "Logged out successfully")

@api_auth.route('/forgot-password', methods=['POST'])
@rate_limit(requests_per_minute=5, by_user=False)
def forgot_password():
    data = request.get_json()
    email = data.get('email', '').lower().strip()

    if not email:
        return api_response("error", "Email is required", code=400)

    user = User.query.filter_by(email=email).first()
    if user and user.account_status == 'active':
        # Reuse logic from web routes
        from app.auth.routes import _generate_reset_token, _send_reset_email, url_for
        token = _generate_reset_token(user.id)
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        _send_reset_email(user, reset_url)

    return api_response("success", "If that email is registered, a reset link has been sent.")