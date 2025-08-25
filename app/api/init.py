from flask import Blueprint

bp = Blueprint("api", __name__)

# import routes AFTER creating bp to avoid circular imports
from app.api import routes  # noqa: E402,F401
