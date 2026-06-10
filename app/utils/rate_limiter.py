"""
Rate limiting utilities to prevent abuse and DoS attacks.
Implements both per-user and global rate limiting.
"""

from functools import wraps
from flask import request, jsonify, flash, redirect, url_for
from flask_login import current_user
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using sliding window."""
    
    def __init__(self):
        # Format: {identifier: deque of timestamps}
        self.requests = defaultdict(deque)
        self.limits = {}
    
    def set_limit(self, identifier, requests_per_minute):
        """Set rate limit for an identifier (route, user, etc)."""
        self.limits[identifier] = requests_per_minute
    
    def is_allowed(self, identifier, requests_per_minute=None):
        """Check if request is allowed under rate limit."""
        if requests_per_minute is None:
            requests_per_minute = self.limits.get(identifier, 60)
        
        now = datetime.now()
        window_start = now - timedelta(minutes=1)
        
        # Remove old requests outside the window
        while self.requests[identifier] and self.requests[identifier][0] < window_start:
            self.requests[identifier].popleft()
        
        # Check if limit exceeded
        if len(self.requests[identifier]) >= requests_per_minute:
            logger.warning(f"Rate limit exceeded for identifier: {identifier}")
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_reset_time(self, identifier):
        """Get when the rate limit will reset (in seconds)."""
        if not self.requests[identifier]:
            return 0
        
        oldest_request = self.requests[identifier][0]
        reset_time = oldest_request + timedelta(minutes=1)
        seconds_until_reset = (reset_time - datetime.now()).total_seconds()
        
        return max(0, int(seconds_until_reset))


# Global rate limiter instance
limiter = RateLimiter()


def rate_limit(requests_per_minute=60, by_user=True, identifier=None):
    """
    Rate limiting decorator.
    
    Args:
        requests_per_minute: Max requests allowed per minute
        by_user: If True, limit per user; if False, limit per IP
        identifier: Custom identifier (overrides by_user)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Determine the identifier
            if identifier:
                limit_id = identifier
            elif by_user and current_user.is_authenticated:
                limit_id = f"user_{current_user.id}"
            else:
                limit_id = f"ip_{request.remote_addr}"
            
            # Check rate limit
            if not limiter.is_allowed(limit_id, requests_per_minute):
                reset_time = limiter.get_reset_time(limit_id)
                logger.warning(
                    f"Rate limit exceeded for {limit_id} on {request.endpoint}. "
                    f"Reset in {reset_time}s"
                )
                
                # Return JSON or redirect based on request type
                if request.is_json or request.endpoint.startswith('api.'):
                    return jsonify({
                        'error': 'Too many requests. Please try again later.',
                        'retry_after': reset_time
                    }), 429
                else:
                    flash(f'Too many requests. Please try again in {reset_time} seconds.', 'warning')
                    return redirect(request.referrer or url_for('main.index'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_rate_limit_status(identifier):
    """Get current rate limit status for debugging."""
    requests_made = len(limiter.requests.get(identifier, []))
    limit = limiter.limits.get(identifier, 60)
    reset_time = limiter.get_reset_time(identifier)
    
    return {
        'requests_made': requests_made,
        'limit': limit,
        'remaining': max(0, limit - requests_made),
        'reset_in_seconds': reset_time
    }
