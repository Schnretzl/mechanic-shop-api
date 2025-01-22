from flask import Flask
from app.models import db
from app.extensions import ma, limiter, cache
from app.blueprints.customers import customers_blueprint
from app.blueprints.service_tickets import service_tickets_blueprint
from app.blueprints.mechanics import mechanics_blueprint
from app.blueprints.parts import parts_blueprint
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
)

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    # Add extensions to app
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    # Register blueprints
    app.register_blueprint(customers_blueprint, url_prefix='/customers')
    app.register_blueprint(service_tickets_blueprint, url_prefix='/service_tickets')
    app.register_blueprint(mechanics_blueprint, url_prefix='/mechanics')
    app.register_blueprint(parts_blueprint, url_prefix='/parts')
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    return app