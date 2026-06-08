from flask import Blueprint

owner_bp = Blueprint('owner', __name__)

from app.owner import routes
