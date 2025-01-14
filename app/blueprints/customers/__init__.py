from flask import Blueprint

customers_blueprint = Blueprint('customers_blueprint', __name__)

from . import routes