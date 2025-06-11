from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import webhook  # noqa: F401
