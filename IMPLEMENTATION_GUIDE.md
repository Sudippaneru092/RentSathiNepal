# Implementation Guide: Advanced Features

This document explains how to integrate and use the new advanced features added to RentSathi Nepal.

## Table of Contents
1. [Rate Limiting](#rate-limiting)
2. [Logging](#logging)
3. [Pagination Optimization](#pagination-optimization)
4. [Unit Tests](#unit-tests)

---

## Rate Limiting

### Overview
Rate limiting prevents abuse and DoS attacks by restricting the number of requests per user or IP address.

### Integration Steps

#### 1. Update `app/__init__.py`
```python
from app.utils.rate_limiter import limiter

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # ... existing code ...
    
    # Initialize rate limiter
    limiter.set_limit('search', 30)  # 30 requests per minute for search
    limiter.set_limit('api_nearby', 60)  # 60 requests per minute for API
    
    return app
```

#### 2. Apply to Routes

**Example: Search route (app/main/routes.py)**
```python
from app.utils.rate_limiter import rate_limit

@main_bp.route('/listings')
@rate_limit(requests_per_minute=30, by_user=True)
def listings():
    # Search logic
    pass
```

**Example: API endpoint**
```python
@main_bp.route('/api/nearby')
@rate_limit(requests_per_minute=60, by_user=False)  # Per IP
def api_nearby():
    # API logic
    pass
```

**Example: Authentication route**
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(requests_per_minute=5, by_user=False)  # 5 attempts per minute
def login():
    # Login logic
    pass
```

#### 3. Configuration

Set different limits for different routes:
```python
# In app/__init__.py
limiter.set_limit('login_attempt', 5)
limiter.set_limit('property_add', 20)
limiter.set_limit('review_add', 10)
limiter.set_limit('message_send', 50)
```

#### 4. Handling Rate Limit Exceeded

The decorator automatically handles responses:
- **JSON requests**: Returns 429 status with retry_after
- **HTML requests**: Redirects with flash message

---

## Logging

### Overview
Comprehensive logging system with multiple handlers for different severity levels.

### Integration Steps

#### 1. Update `app/__init__.py`
```python
from app.utils.logger import setup_logging

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    # ... existing code ...
    
    # Set up logging
    loggers = setup_logging(app)
    
    return app
```

#### 2. Use in Your Code

**General logging:**
```python
import logging

logger = logging.getLogger('rentsathi')

@main_bp.route('/listings')
def listings():
    try:
        properties = Property.query.all()
        logger.info(f"Fetched {len(properties)} properties")
    except Exception as e:
        logger.error(f"Error fetching properties: {str(e)}")
```

**Error logging:**
```python
from app.utils.logger import log_api_error

try:
    result = some_operation()
except Exception as e:
    log_api_error('/api/nearby', 'GET', 500, str(e))
```

**Authentication logging:**
```python
from app.utils.logger import log_auth_attempt

user = User.query.filter_by(email=email).first()
success = user and check_password_hash(user.password, password)
log_auth_attempt(email, success, request.remote_addr)
```

**Access logging:**
```python
from app.utils.logger import log_access

@app.after_request
def log_request(response):
    if request.endpoint:
        log_access(
            current_user.id if current_user.is_authenticated else None,
            request.endpoint,
            request.method,
            request.remote_addr,
            response.status_code
        )
    return response
```

#### 3. Log Files Generated

```
logs/
├── app.log              # General application logs
├── errors.log           # Errors only
├── access.log           # HTTP access logs
├── database.log         # Database query logs
└── security.log         # Security events
```

#### 4. Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (auth attempts, rate limits)
- **ERROR**: Error messages

---

## Pagination Optimization

### Overview
Multiple pagination strategies for different use cases, with caching support.

### Integration Steps

#### 1. Basic Pagination (Existing Approach)

**In `app/main/routes.py`:**
```python
from app.utils.pagination import PaginationOptimizer

@main_bp.route('/listings')
def listings():
    page = PaginationOptimizer.get_page_from_request()
    per_page = PaginationOptimizer.get_per_page_from_request()
    
    query = _build_search_query(request.args)
    result = PaginationOptimizer.paginate_query(
        query=query,
        page=page,
        per_page=per_page
    )
    
    return render_template(
        'main/listings.html',
        properties=result['items'],
        total=result['total'],
        has_next=result['has_next'],
        has_prev=result['has_prev']
    )
```

#### 2. Keyset Pagination (Faster for Large Datasets)

**Use for very large tables (100k+ rows):**
```python
from app.utils.pagination import LazyPaginator

@main_bp.route('/properties/stream')
def properties_stream():
    last_id = request.args.get('cursor', type=int)
    limit = request.args.get('limit', 20, type=int)
    
    query = Property.query.filter_by(status='active').order_by(Property.id.desc())
    result = LazyPaginator.paginate_by_id(
        query=query,
        last_id=last_id,
        limit=limit,
        order_by_column=Property.id
    )
    
    return render_template(
        'main/stream.html',
        items=result['items'],
        next_cursor=result['next_cursor'],
        has_next=result['has_next']
    )
```

#### 3. Date-based Keyset Pagination

**For feed-like interfaces (recent items first):**
```python
from app.utils.pagination import LazyPaginator

@user_bp.route('/messages')
def messages():
    last_date = request.args.get('cursor')
    
    query = Chat.query.filter_by(receiver_id=current_user.id).order_by(Chat.sent_at.desc())
    result = LazyPaginator.paginate_by_date(
        query=query,
        last_date=last_date,
        limit=20,
        order_by_column=Chat.sent_at
    )
    
    return render_template(
        'user/messages.html',
        messages=result['items'],
        next_cursor=result['next_cursor'],
        has_next=result['has_next']
    )
```

#### 4. With Caching

**Reduce database count queries:**
```python
from app.utils.pagination import pagination_helper, PaginationOptimizer

@admin_bp.route('/users')
def users():
    page = PaginationOptimizer.get_page_from_request()
    
    # Get cached total count
    total = pagination_helper.get_total_count(
        cache_key='admin_users_total',
        count_function=lambda: User.query.count()
    )
    
    query = User.query.order_by(User.created_at.desc())
    result = PaginationOptimizer.paginate_query(
        query=query,
        page=page,
        per_page=20,
        count_query=None  # Skip recounting
    )
    result['total'] = total  # Use cached total
    
    return render_template('admin/users.html', users=result['items'], total=total)
```

#### 5. Invalidate Cache (After data changes)

```python
from app.utils.pagination import pagination_helper

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    # Invalidate cache
    pagination_helper.invalidate_cache('admin_users_total')
    
    flash('User deleted', 'success')
    return redirect(url_for('admin.users'))
```

### Performance Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| **Offset/Limit** | Small datasets (<10k) | Simple, familiar | Slow for large offsets |
| **Keyset** | Large datasets (100k+) | Fast, consistent | Requires specific order |
| **Cached Count** | Stable data | Reduces DB load | Cache invalidation needed |

---

## Unit Tests

### Overview
Comprehensive test suite for authentication, models, and utilities.

### Running Tests

#### 1. Install Test Dependencies
```bash
pip install pytest pytest-cov
```

#### 2. Run All Tests
```bash
# From project root
python -m pytest tests/test_app.py -v

# With coverage
python -m pytest tests/test_app.py --cov=app --cov-report=html

# Specific test class
python -m pytest tests/test_app.py::AuthenticationTests -v

# Specific test
python -m pytest tests/test_app.py::AuthenticationTests::test_user_registration -v
```

#### 3. Test Categories

**Authentication Tests:**
```python
- test_user_registration          # User creation
- test_duplicate_email_prevention # Email uniqueness
- test_password_hashing           # Secure hashing
- test_owner_profile_creation     # Profile creation
```

**Property Management Tests:**
```python
- test_property_creation          # Create property
- test_property_validation        # Field validation
- test_property_average_rating    # Rating calculation
- test_property_deletion          # Cascade delete
```

**Feature Tests:**
```python
- test_add_favorite               # Add to favorites
- test_duplicate_favorite_prevention
- test_remove_favorite
- test_add_review                 # Add review
- test_rating_range_validation
- test_roommate_profile_creation
```

**Utility Tests:**
```python
- test_rate_limiter               # Rate limiting
- test_pagination_optimizer       # Pagination
```

#### 4. Adding New Tests

Create test files in `tests/` directory:

```python
# tests/test_owner_routes.py
import unittest
from tests.test_app import BaseTestCase

class OwnerRouteTests(BaseTestCase):
    """Test owner blueprint routes."""
    
    def test_add_property_page(self):
        """Test property add page loads."""
        user = self._create_test_user(role='owner')
        
        with self.client:
            # Login
            self.client.post('/auth/login', data={
                'email': user.email,
                'password': 'password123'
            })
            
            # Access add property page
            response = self.client.get('/owner/property/add')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Add Property', response.data)
```

#### 5. Continuous Integration

Add to `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python -m pytest tests/ --cov=app
```

---

## Integration Checklist

- [ ] Add rate limiting to critical routes
- [ ] Configure logging in app initialization
- [ ] Update search/listing routes with pagination optimization
- [ ] Run unit tests and verify all pass
- [ ] Set up log file monitoring
- [ ] Configure rate limit thresholds based on load testing
- [ ] Add logging to error handlers
- [ ] Set up cron job to rotate old log files

---

## Monitoring & Maintenance

### Log Monitoring
```bash
# Watch real-time logs
tail -f logs/app.log

# Monitor errors
tail -f logs/errors.log

# Check security events
grep "FAILED" logs/security.log
```

### Performance Monitoring
```python
# Check rate limiter status
from app.utils.rate_limiter import get_rate_limit_status

status = get_rate_limit_status(f"user_{user_id}")
print(status)  # {'requests_made': 5, 'limit': 30, 'remaining': 25, 'reset_in_seconds': 45}
```

### Cache Invalidation
```python
# Manually clear pagination cache
from app.utils.pagination import pagination_helper

pagination_helper.invalidate_cache('admin_users_total')
# Or clear all
pagination_helper.invalidate_cache()
```

---

## Troubleshooting

### Rate Limit Issues
- Check `logs/security.log` for "Rate limit exceeded" messages
- Adjust limits in `app/__init__.py`
- Per-IP limiting might be too strict behind proxy (use `by_user=True`)

### Logging Issues
- Verify `logs/` directory exists and is writable
- Check file permissions: `chmod 755 logs/`
- Monitor log file sizes to prevent disk space issues

### Pagination Performance
- Use keyset pagination for tables with >50k rows
- Enable caching for count queries on stable data
- Monitor slow query logs in `logs/database.log`

---

## Best Practices

1. **Rate Limiting**: Set limits based on load testing, not guesswork
2. **Logging**: Don't log sensitive data (passwords, tokens)
3. **Pagination**: Use appropriate strategy based on data size
4. **Testing**: Keep tests isolated and independent
5. **Monitoring**: Review logs regularly for issues

