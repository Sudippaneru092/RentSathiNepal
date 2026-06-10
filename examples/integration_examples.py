"""
Integration examples: Using rate limiting, logging, and pagination together.
This demonstrates best practices for combining all advanced features.
"""

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
import logging

# Import advanced utilities
from app.utils.rate_limiter import rate_limit
from app.utils.logger import log_access, log_api_error, log_auth_attempt
from app.utils.pagination import PaginationOptimizer, pagination_helper

logger = logging.getLogger('rentsathi')


# ==================== EXAMPLE 1: Search with Rate Limiting & Logging ====================

def example_listings_with_all_features(main_bp):
    """
    Example: Advanced listings page combining all features.
    
    Features:
    - Rate limiting (30 requests/min per user)
    - Pagination optimization
    - Comprehensive logging
    - Error handling
    """
    
    @main_bp.route('/listings/advanced')
    @rate_limit(requests_per_minute=30, by_user=True)
    def listings_advanced():
        try:
            # Extract and validate pagination parameters
            page = PaginationOptimizer.get_page_from_request()
            per_page = PaginationOptimizer.get_per_page_from_request(default=12, max_allowed=50)
            
            # Extract search filters
            city = request.args.get('city', '').strip()
            min_price = request.args.get('min_price', '').strip()
            max_price = request.args.get('max_price', '').strip()
            
            # Log search attempt
            user_id = current_user.id if current_user.is_authenticated else None
            logger.info(
                f"Search initiated - User: {user_id}, "
                f"City: {city}, Price: {min_price}-{max_price}, Page: {page}"
            )
            
            # Build query with filters
            from app.models import Property
            query = Property.query.filter_by(
                status='active',
                verification_status='verified',
                availability_status='available'
            )
            
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            
            if min_price:
                try:
                    query = query.filter(Property.price >= float(min_price))
                except ValueError:
                    logger.warning(f"Invalid min_price parameter: {min_price}")
            
            if max_price:
                try:
                    query = query.filter(Property.price <= float(max_price))
                except ValueError:
                    logger.warning(f"Invalid max_price parameter: {max_price}")
            
            # Use pagination with caching
            cache_key = f"search_{city}_{min_price}_{max_price}"
            
            result = PaginationOptimizer.paginate_query(
                query=query,
                page=page,
                per_page=per_page
            )
            
            # Log successful search
            logger.info(
                f"Search completed - Results: {len(result['items'])}/{result['total']}, "
                f"Pages: {result['pages']}, User: {user_id}"
            )
            
            return render_template(
                'main/listings.html',
                properties=result['items'],
                pagination=result,
                city=city,
                min_price=min_price,
                max_price=max_price
            )
        
        except Exception as e:
            logger.error(f"Error in listings search: {str(e)}", exc_info=True)
            return render_template('errors/500.html'), 500


# ==================== EXAMPLE 2: API Endpoint with Rate Limiting ====================

def example_api_properties(main_bp):
    """
    Example: API endpoint with per-IP rate limiting and detailed logging.
    """
    
    @main_bp.route('/api/v1/properties')
    @rate_limit(requests_per_minute=60, by_user=False)  # Per IP
    def api_properties():
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            city = request.args.get('city', '').strip()
            
            from app.models import Property
            
            query = Property.query.filter_by(
                status='active',
                verification_status='verified'
            )
            
            if city:
                query = query.filter(Property.city.ilike(f'%{city}%'))
            
            result = PaginationOptimizer.paginate_query(
                query=query,
                page=page,
                per_page=per_page
            )
            
            # Log API call
            logger.info(
                f"API call - Endpoint: /api/v1/properties, "
                f"IP: {request.remote_addr}, Page: {page}, "
                f"Results: {len(result['items'])}/{result['total']}"
            )
            
            return jsonify({
                'status': 'success',
                'data': [
                    {
                        'id': p.id,
                        'title': p.title,
                        'price': float(p.price),
                        'city': p.city,
                        'type': p.property_type,
                        'beds': p.bedrooms,
                        'baths': p.bathrooms
                    }
                    for p in result['items']
                ],
                'pagination': {
                    'page': result['page'],
                    'per_page': result['per_page'],
                    'total': result['total'],
                    'pages': result['pages'],
                    'has_next': result['has_next']
                }
            }), 200
        
        except Exception as e:
            log_api_error('/api/v1/properties', 'GET', 500, str(e))
            
            return jsonify({
                'status': 'error',
                'message': 'Internal server error'
            }), 500


# ==================== EXAMPLE 3: Admin Actions with Audit Logging ====================

def example_admin_verify_property(admin_bp):
    """
    Example: Admin action with rate limiting and audit logging.
    """
    
    @admin_bp.route('/property/<int:property_id>/verify', methods=['POST'])
    @login_required
    @rate_limit(requests_per_minute=20, by_user=True)
    def verify_property(property_id):
        try:
            from app.models import Property, AdminLog
            from app import db
            
            property = Property.query.get_or_404(property_id)
            action = request.form.get('action', 'verify')
            
            if action == 'verify':
                property.verification_status = 'verified'
                action_desc = f"Verified property: {property.title}"
            elif action == 'reject':
                property.verification_status = 'rejected'
                action_desc = f"Rejected property: {property.title}"
            else:
                raise ValueError(f"Unknown action: {action}")
            
            db.session.commit()
            
            # Create audit log
            admin_log = AdminLog(
                admin_id=current_user.id,
                action=action,
                description=action_desc
            )
            db.session.add(admin_log)
            db.session.commit()
            
            # Invalidate pagination cache
            pagination_helper.invalidate_cache('admin_pending_properties')
            
            # Log admin action for security
            logger.warning(
                f"Admin action - User: {current_user.email}, "
                f"ID: {current_user.id}, Action: {action}, "
                f"Property: {property_id}, IP: {request.remote_addr}"
            )
            
            return jsonify({
                'status': 'success',
                'message': f'Property {action}ed successfully'
            }), 200
        
        except Exception as e:
            log_api_error(
                f'/admin/property/{property_id}/verify',
                'POST',
                500,
                str(e)
            )
            return jsonify({'status': 'error', 'message': 'Failed to process'}), 500


# ==================== EXAMPLE 4: User Messages with Date-based Pagination ====================

def example_user_messages(user_bp):
    """
    Example: User messages with date-based keyset pagination (efficient for feeds).
    """
    
    @user_bp.route('/messages')
    @login_required
    def messages():
        try:
            from app.models import Chat
            from app.utils.pagination import LazyPaginator
            
            last_date = request.args.get('cursor')
            
            # Get received messages with date-based keyset pagination
            query = Chat.query.filter_by(
                receiver_id=current_user.id
            ).order_by(Chat.sent_at.desc())
            
            result = LazyPaginator.paginate_by_date(
                query=query,
                last_date=last_date,
                limit=20,
                order_by_column=Chat.sent_at
            )
            
            logger.info(
                f"Messages loaded - User: {current_user.id}, "
                f"Count: {len(result['items'])}, Has next: {result['has_next']}"
            )
            
            return render_template(
                'user/messages.html',
                messages=result['items'],
                next_cursor=result['next_cursor'],
                has_next=result['has_next']
            )
        
        except Exception as e:
            logger.error(f"Error loading messages: {str(e)}", exc_info=True)
            return render_template('errors/500.html'), 500


# ==================== EXAMPLE 5: Login with Rate Limiting & Security Logging ====================

def example_login_with_rate_limit(auth_bp):
    """
    Example: Login with strict rate limiting and security audit logging.
    """
    
    @auth_bp.route('/login', methods=['GET', 'POST'])
    @rate_limit(requests_per_minute=5, by_user=False)  # 5 attempts per minute per IP
    def login():
        from app.models import User
        from werkzeug.security import check_password_hash
        from flask_login import login_user
        
        if request.method == 'POST':
            email = request.form.get('email', '').lower().strip()
            password = request.form.get('password', '')
            
            user = User.query.filter_by(email=email).first()
            success = user and check_password_hash(user.password, password)
            
            # Log authentication attempt for security
            log_auth_attempt(email, success, request.remote_addr)
            
            if success:
                if user.account_status != 'active':
                    logger.warning(
                        f"Login attempt on suspended account: {email} from {request.remote_addr}"
                    )
                    return render_template('auth/login.html', error='Account suspended')
                
                login_user(user)
                logger.info(f"Successful login: {email} from {request.remote_addr}")
                return redirect(url_for('main.index'))
            else:
                logger.warning(f"Failed login attempt: {email} from {request.remote_addr}")
                return render_template('auth/login.html', error='Invalid credentials')
        
        return render_template('auth/login.html')


# ==================== EXAMPLE 6: Request Logging Middleware ====================

def setup_request_logging(app):
    """
    Setup automatic request/response logging for all routes.
    """
    import time
    
    @app.before_request
    def before_request():
        """Record request start time."""
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Log request completion with duration."""
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
            
            user_id = current_user.id if current_user.is_authenticated else None
            
            # Log all requests
            logger.info(
                f"HTTP {response.status_code} - {request.method} {request.path} - "
                f"User: {user_id} - IP: {request.remote_addr} - "
                f"Duration: {duration_ms:.2f}ms"
            )
            
            # Log slow requests
            if duration_ms > 1000:
                logger.warning(
                    f"Slow request ({duration_ms:.2f}ms): "
                    f"{request.method} {request.path}"
                )
        
        return response


# ==================== EXAMPLE 7: Performance Statistics ====================

def get_performance_stats():
    """Get current application performance statistics."""
    from app.utils.rate_limiter import limiter
    
    return {
        'rate_limiter': {
            'active_identifiers': len(limiter.requests),
            'total_requests': sum(len(v) for v in limiter.requests.values())
        },
        'pagination_cache': {
            'cached_keys': len(pagination_helper.cache),
            'cache_timeout_seconds': pagination_helper.cache_timeout
        },
        'stats_timestamp': str(__import__('datetime').datetime.now())
    }


def example_stats_endpoint(admin_bp):
    """Example: Admin stats endpoint."""
    
    @admin_bp.route('/stats')
    @login_required
    def stats():
        stats = get_performance_stats()
        logger.info(f"Stats accessed by User: {current_user.id}")
        return jsonify(stats), 200


# ==================== USAGE INSTRUCTIONS ====================

"""
To use these examples in your application:

1. Rate Limiting:
   from examples.integration_examples import example_listings_with_all_features
   example_listings_with_all_features(main_bp)

2. API Endpoints:
   from examples.integration_examples import example_api_properties
   example_api_properties(main_bp)

3. Admin Actions:
   from examples.integration_examples import example_admin_verify_property
   example_admin_verify_property(admin_bp)

4. Request Logging:
   from examples.integration_examples import setup_request_logging
   setup_request_logging(app)

5. Performance Monitoring:
   from examples.integration_examples import get_performance_stats
   stats = get_performance_stats()
"""
