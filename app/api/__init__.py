from flask import Blueprint

# Create a parent blueprint for all API routes
# This allows us to group all APIs under /api/v1
api_bp = Blueprint('api', __name__)

# We import the modules inside the function or at the bottom 
# to avoid circular imports
from app.api import auth, users, properties, owners, chats

# Registering the sub-blueprints
# Note: I am using 'api_auth', 'api_users' etc. to avoid naming 
# conflicts with your existing web blueprints (auth, user, etc.)
api_bp.register_blueprint(auth.api_auth, url_prefix='/auth')
api_bp.register_blueprint(users.api_users, url_prefix='/users')
api_bp.register_blueprint(properties.api_properties, url_prefix='/properties')
api_bp.register_blueprint(owners.api_owners, url_prefix='/owners')
api_bp.register_blueprint(chats.api_chats, url_prefix='/chats')