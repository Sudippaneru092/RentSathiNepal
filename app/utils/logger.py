"""
Logging configuration for the RentSathi Nepal application.
Includes file-based and console logging with different levels.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(app):
    """
    Configure logging for the Flask application.
    Creates both file and console handlers with appropriate levels.
    """
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file paths
    general_log = os.path.join(logs_dir, 'app.log')
    error_log = os.path.join(logs_dir, 'errors.log')
    access_log = os.path.join(logs_dir, 'access.log')
    
    # Log format
    detailed_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console format (shorter)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # ==================== General Logger ====================
    general_logger = logging.getLogger('rentsathi')
    general_logger.setLevel(logging.DEBUG)
    
    # File handler for general logs (rotated daily, max 10 files)
    general_file_handler = logging.handlers.RotatingFileHandler(
        general_log, maxBytes=10_485_760, backupCount=10  # 10MB per file
    )
    general_file_handler.setLevel(logging.INFO)
    general_file_handler.setFormatter(detailed_format)
    general_logger.addHandler(general_file_handler)
    
    # Console handler for general logs
    general_console_handler = logging.StreamHandler()
    general_console_handler.setLevel(logging.INFO if not app.debug else logging.DEBUG)
    general_console_handler.setFormatter(console_format)
    general_logger.addHandler(general_console_handler)
    
    # ==================== Error Logger ====================
    error_logger = logging.getLogger('rentsathi.errors')
    error_logger.setLevel(logging.ERROR)
    
    # File handler for errors only
    error_file_handler = logging.handlers.RotatingFileHandler(
        error_log, maxBytes=10_485_760, backupCount=10
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_format)
    error_logger.addHandler(error_file_handler)
    
    # ==================== Access Logger ====================
    access_logger = logging.getLogger('rentsathi.access')
    access_logger.setLevel(logging.INFO)
    
    # File handler for access logs (daily rotation)
    access_file_handler = logging.handlers.TimedRotatingFileHandler(
        access_log, when='midnight', interval=1, backupCount=30
    )
    access_file_handler.setLevel(logging.INFO)
    access_file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    )
    access_logger.addHandler(access_file_handler)
    
    # ==================== Database Logger ====================
    db_logger = logging.getLogger('rentsathi.db')
    db_logger.setLevel(logging.DEBUG)
    
    db_file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_dir, 'database.log'), maxBytes=5_242_880, backupCount=5
    )
    db_file_handler.setLevel(logging.DEBUG)
    db_file_handler.setFormatter(detailed_format)
    db_logger.addHandler(db_file_handler)
    
    # ==================== Security Logger ====================
    security_logger = logging.getLogger('rentsathi.security')
    security_logger.setLevel(logging.WARNING)
    
    security_file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(logs_dir, 'security.log'), maxBytes=5_242_880, backupCount=5
    )
    security_file_handler.setLevel(logging.WARNING)
    security_file_handler.setFormatter(detailed_format)
    security_logger.addHandler(security_file_handler)
    
    # Suppress noisy third-party loggers
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    general_logger.info("=" * 50)
    general_logger.info(f"Application started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    general_logger.info(f"Environment: {'DEBUG' if app.debug else 'PRODUCTION'}")
    general_logger.info("=" * 50)
    
    return {
        'general': general_logger,
        'errors': error_logger,
        'access': access_logger,
        'db': db_logger,
        'security': security_logger
    }


# Helper functions for common logging patterns
def log_auth_attempt(username, success, ip_address):
    """Log authentication attempts."""
    logger = logging.getLogger('rentsathi.security')
    status = "SUCCESS" if success else "FAILED"
    logger.warning(f"Auth attempt ({status}): {username} from {ip_address}")


def log_api_error(endpoint, method, error_code, error_msg):
    """Log API errors."""
    logger = logging.getLogger('rentsathi.errors')
    logger.error(f"API Error - {method} {endpoint}: [{error_code}] {error_msg}")


def log_db_query(query, duration_ms):
    """Log database queries (for performance monitoring)."""
    logger = logging.getLogger('rentsathi.db')
    if duration_ms > 100:  # Log slow queries
        logger.warning(f"Slow DB query ({duration_ms}ms): {query}")
    else:
        logger.debug(f"DB query ({duration_ms}ms): {query}")


def log_access(user_id, endpoint, method, ip_address, status_code):
    """Log HTTP access."""
    logger = logging.getLogger('rentsathi.access')
    user_info = f"User:{user_id}" if user_id else "Anonymous"
    logger.info(f"{user_info} - {method} {endpoint} - {status_code} - {ip_address}")


def log_admin_action(admin_id, action, details):
    """Log administrative actions."""
    logger = logging.getLogger('rentsathi.security')
    logger.info(f"Admin action by User:{admin_id} - {action}: {details}")
