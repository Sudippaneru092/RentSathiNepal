"""
Database pagination utilities for optimized query performance.
Implements caching and efficient pagination patterns.
"""

from flask import request
from sqlalchemy import func
import logging

logger = logging.getLogger('rentsathi.db')


class PaginationOptimizer:
    """Handles efficient pagination for large datasets."""
    
    @staticmethod
    def paginate_query(query, page=1, per_page=20, count_query=None, cache_key=None):
        """
        Paginate a query with optional caching and optimized counting.
        
        Args:
            query: SQLAlchemy query object
            page: Current page number (1-indexed)
            per_page: Items per page
            count_query: Custom query for counting (optimization for complex queries)
            cache_key: Optional cache key for storing pagination metadata
            
        Returns:
            Pagination object with items, total, pages, has_prev, has_next
        """
        try:
            # Validate inputs
            page = max(1, int(page) if page else 1)
            per_page = max(1, min(100, int(per_page) if per_page else 20))  # Cap at 100
            
            # Get total count
            total = count_query.count() if count_query else query.count()
            
            # Log pagination for monitoring
            logger.debug(f"Pagination - Page: {page}, Per page: {per_page}, Total items: {total}")
            
            # Calculate pagination metadata
            total_pages = (total + per_page - 1) // per_page  # Ceiling division
            has_prev = page > 1
            has_next = page < total_pages
            
            # Get items for current page
            offset = (page - 1) * per_page
            items = query.offset(offset).limit(per_page).all()
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_page': page - 1 if has_prev else None,
                'next_page': page + 1 if has_next else None,
            }
        
        except Exception as e:
            logger.error(f"Pagination error: {str(e)}")
            return {
                'items': [],
                'total': 0,
                'page': 1,
                'per_page': per_page,
                'pages': 0,
                'has_prev': False,
                'has_next': False,
                'prev_page': None,
                'next_page': None,
                'error': str(e)
            }
    
    @staticmethod
    def get_page_from_request():
        """Extract page number from request arguments."""
        try:
            page = request.args.get('page', 1, type=int)
            return max(1, page)
        except (ValueError, TypeError):
            return 1
    
    @staticmethod
    def get_per_page_from_request(default=20, max_allowed=100):
        """Extract per_page parameter from request arguments."""
        try:
            per_page = request.args.get('per_page', default, type=int)
            return max(1, min(per_page, max_allowed))
        except (ValueError, TypeError):
            return default


class LazyPaginator:
    """Keyset-based pagination for very large datasets (more efficient than offset)."""
    
    @staticmethod
    def paginate_by_id(query, last_id=None, limit=20, order_by_column=None):
        """
        Paginate using keyset pagination (faster for large datasets).
        
        Args:
            query: SQLAlchemy query object
            last_id: ID of last item from previous page (for next page)
            limit: Number of items to return
            order_by_column: Column to order by (defaults to 'id')
            
        Returns:
            Dictionary with items, has_next, and next_cursor
        """
        try:
            limit = max(1, min(limit, 100))
            
            # Apply cursor filter if provided
            if last_id:
                query = query.filter(order_by_column > last_id)
            
            # Fetch one extra to determine if there's a next page
            items = query.limit(limit + 1).all()
            
            has_next = len(items) > limit
            if has_next:
                items = items[:limit]
            
            next_cursor = items[-1].id if items and has_next else None
            
            logger.debug(f"Keyset pagination - Items: {len(items)}, Has next: {has_next}")
            
            return {
                'items': items,
                'has_next': has_next,
                'next_cursor': next_cursor,
                'limit': limit
            }
        
        except Exception as e:
            logger.error(f"Keyset pagination error: {str(e)}")
            return {
                'items': [],
                'has_next': False,
                'next_cursor': None,
                'limit': limit,
                'error': str(e)
            }
    
    @staticmethod
    def paginate_by_date(query, last_date=None, limit=20, order_by_column=None):
        """
        Paginate using date-based keyset pagination.
        
        Args:
            query: SQLAlchemy query object
            last_date: DateTime of last item from previous page
            limit: Number of items to return
            order_by_column: Column to order by (defaults to created_at)
            
        Returns:
            Dictionary with items, has_next, and next_cursor
        """
        try:
            from datetime import datetime
            
            limit = max(1, min(limit, 100))
            
            # Apply cursor filter if provided
            if last_date:
                query = query.filter(order_by_column < last_date)
            
            # Fetch one extra to determine if there's a next page
            items = query.limit(limit + 1).all()
            
            has_next = len(items) > limit
            if has_next:
                items = items[:limit]
            
            next_cursor = items[-1].created_at if items and has_next else None
            
            logger.debug(f"Date-based keyset pagination - Items: {len(items)}, Has next: {has_next}")
            
            return {
                'items': items,
                'has_next': has_next,
                'next_cursor': next_cursor,
                'limit': limit
            }
        
        except Exception as e:
            logger.error(f"Date-based keyset pagination error: {str(e)}")
            return {
                'items': [],
                'has_next': False,
                'next_cursor': None,
                'limit': limit,
                'error': str(e)
            }


class CachedPaginationHelper:
    """Helper for caching pagination metadata to avoid repeated counts."""
    
    def __init__(self, cache_timeout=300):
        """Initialize with cache timeout in seconds."""
        self.cache = {}
        self.cache_timeout = cache_timeout
        self.cache_times = {}
    
    def get_total_count(self, cache_key, count_function):
        """
        Get total count with caching.
        
        Args:
            cache_key: Unique key for this count
            count_function: Function to call if cache miss
            
        Returns:
            Total count
        """
        from datetime import datetime, timedelta
        
        now = datetime.now()
        
        # Check if cache exists and is still valid
        if cache_key in self.cache:
            cache_time = self.cache_times.get(cache_key)
            if cache_time and (now - cache_time).total_seconds() < self.cache_timeout:
                logger.debug(f"Cache hit for count key: {cache_key}")
                return self.cache[cache_key]
        
        # Cache miss - recalculate
        logger.debug(f"Cache miss for count key: {cache_key}")
        count = count_function()
        self.cache[cache_key] = count
        self.cache_times[cache_key] = now
        
        return count
    
    def invalidate_cache(self, cache_key=None):
        """Invalidate cache for a specific key or all keys."""
        if cache_key:
            self.cache.pop(cache_key, None)
            self.cache_times.pop(cache_key, None)
            logger.debug(f"Invalidated cache for key: {cache_key}")
        else:
            self.cache.clear()
            self.cache_times.clear()
            logger.debug("Cleared all pagination cache")


# Global pagination helper instance
pagination_helper = CachedPaginationHelper(cache_timeout=300)
