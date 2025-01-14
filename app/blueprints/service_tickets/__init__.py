from flask import Blueprint

service_tickets_blueprint = Blueprint('service_tickets_blueprint', __name__)

from . import routes