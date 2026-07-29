import os
import logging
from flask import Flask, render_template, request as flask_request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from config import Config
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
socketio = SocketIO(cors_allowed_origins="*")


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)
    # ── Structured logging ────────────────────────────────────────────────
    from app.utils.logger import setup_logging
    setup_logging(app)

    # ── Register blueprints ───────────────────────────────────────────────
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.owner import owner_bp
    app.register_blueprint(owner_bp, url_prefix='/owner')

    from app.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.chats import chat_bp
    app.register_blueprint(chat_bp)
    # ── Access logging (after every request) ─────────────────────────────
    @app.after_request
    def log_access(response):
        from app.utils.logger import log_access as _log_access
        # Skip static files to keep logs clean
        if flask_request.path.startswith('/static'):
            return response
        user_id = current_user.id if current_user.is_authenticated else None
        _log_access(
            user_id=user_id,
            endpoint=flask_request.path,
            method=flask_request.method,
            ip_address=flask_request.remote_addr,
            status_code=response.status_code,
        )
        return response

    # ── Error handlers ────────────────────────────────────────────────────
    _err_logger = logging.getLogger('rentsathi.errors')

    @app.errorhandler(403)
    def forbidden(e):
        _err_logger.warning(
            '403 Forbidden: %s %s from %s',
            flask_request.method, flask_request.path, flask_request.remote_addr
        )
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        _err_logger.info(
            '404 Not Found: %s %s from %s',
            flask_request.method, flask_request.path, flask_request.remote_addr
        )
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        _err_logger.error(
            '500 Internal Server Error: %s %s — %s',
            flask_request.method, flask_request.path, str(e),
            exc_info=True,
        )
        db.session.rollback()
        return render_template('errors/404.html'), 500  # reuse until a 500 template is added

    with app.app_context():
        from app import models  # ensure models are imported for Migrate

    # ── Jinja2 global helper ──────────────────────────────────────────────
    @app.template_global()
    def prop_img_url(path):
        """Return correct URL for property image — external URL or local static path."""
        if not path:
            return None
        if path.startswith('http'):
            return path
        from flask import url_for
        return url_for('static', filename=path)

    # ── Global stats context processor ───────────────────────────────────
    @app.context_processor
    def inject_global_stats():
        """Inject real DB stats into every template (used on auth pages etc.)."""
        try:
            from app.models import Property as _Prop, User as _User, RoommateProfile as _RP
            from sqlalchemy import func as _func
            _total_properties = _Prop.query.filter_by(
                status='active', availability_status='available', verification_status='verified'
            ).count()
            _total_users  = _User.query.filter_by(role='user').count()
            _total_owners = _User.query.filter_by(role='owner').count()
            _total_cities = db.session.query(
                _func.count(_func.distinct(_Prop.city))
            ).filter_by(
                status='active', availability_status='available', verification_status='verified'
            ).scalar() or 0
            _total_roommate_profiles = _RP.query.join(_User).filter(
                _User.account_status == 'active'
            ).count()
        except Exception:
            _total_properties = _total_users = _total_owners = _total_cities = _total_roommate_profiles = 0
        return dict(
            g_total_properties=_total_properties,
            g_total_users=_total_users,
            g_total_owners=_total_owners,
            g_total_cities=_total_cities,
            g_total_roommate_profiles=_total_roommate_profiles,
        )
    from flask_login import current_user
    from app.models import Favorite, Chat
    from flask_login import current_user

    @app.context_processor
    def inject_user_counts():
        if current_user.is_authenticated:
            from app.models import Favorite, Chat, Property
            # Try importing Booking or BookingRequest depending on your model name
            try:
                from app.models import Booking
            except ImportError:
                from app.models import BookingRequest as Booking

            # 1. Favorites count
            fav_count = Favorite.query.filter_by(user_id=current_user.id).count()

            # 2. Unread messages count
            unread_count = Chat.query.filter_by(
                receiver_id=current_user.id, 
                is_read=False
            ).count()

            # 3. Pending bookings count
            pending_bookings = 0
            try:
                if current_user.role == 'owner':
                    # If Booking model has owner_id directly
                    if hasattr(Booking, 'owner_id'):
                        pending_bookings = Booking.query.filter_by(
                            owner_id=current_user.id, 
                            status='pending'
                        ).count()
                    else:
                        # Join through Property if owner_id is on Property model
                        pending_bookings = Booking.query.join(Property).filter(
                            Property.owner_id == current_user.id,
                            Booking.status == 'pending'
                        ).count()
                else:
                    # For regular users/tenants: pending requests sent by them
                    pending_bookings = Booking.query.filter_by(
                        user_id=current_user.id, 
                        status='pending'
                    ).count()
            except Exception:
                pending_bookings = 0

            return {
                "fav_count": fav_count,
                "unread_count": unread_count,
                "pending_bookings": pending_bookings
            }

        return {
            "fav_count": 0,
            "unread_count": 0,
            "pending_bookings": 0
        }
    with app.app_context():
        from app import models
        from app.chats import event

    return app
