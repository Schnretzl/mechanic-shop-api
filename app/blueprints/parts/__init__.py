from flask import Blueprint

parts_blueprint = Blueprint('parts_blueprint', __name__)

from . import routes