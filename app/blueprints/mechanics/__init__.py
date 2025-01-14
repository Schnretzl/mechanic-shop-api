from flask import Blueprint

mechanics_blueprint = Blueprint('mechanics_blueprint', __name__)

from . import routes