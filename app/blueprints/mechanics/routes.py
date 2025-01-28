from flask import request, jsonify
from app.blueprints.mechanics import mechanics_blueprint
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema, mechanic_login_schema
from app.extensions import limiter, cache
from marshmallow import ValidationError
from app.models import Mechanic, ServiceTicket, db
from sqlalchemy import select
from app.utils.util import encode_token, token_required

@mechanics_blueprint.route('/login', methods=['POST'])
def login():
    try:
        credentials = mechanic_login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id)
        
        response = {
            'status': 'success',
            'message': 'Successfully logged in',
            'token': token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401

@mechanics_blueprint.route('/', methods=['POST'])
@limiter.limit("3 per hour")
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_mechanic = Mechanic(name=mechanic_data['name'], email=mechanic_data['email'], phone=mechanic_data['phone'], salary=mechanic_data['salary'], password=mechanic_data['password'])
    
    db.session.add(new_mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_blueprint.route('/', methods=['GET'])
def get_mechanics():
    query = select(Mechanic)
    result = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(result), 200

@mechanics_blueprint.route('/', methods=['PUT'])
@token_required
def update_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic is None:
        return jsonify({'message': 'Mechanic not found'}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in mechanic_data.items():
        if value:
            setattr(mechanic, field, value)
        
    db.session.commit()
    
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_blueprint.route('/', methods=['DELETE'])
@token_required
def delete_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    
    db.session.delete(mechanic)
    db.session.commit()
    
    return jsonify({'message': f'Successfully deleted mechanic {mechanic_id}'}), 200

@mechanics_blueprint.route('/popular', methods=['GET'])
@cache.cached(timeout=60)
def popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key=lambda mechanic: len(mechanic.service_tickets), reverse=True)
    
    return mechanics_schema.jsonify(mechanics), 200

@mechanics_blueprint.route('/search', methods=['GET'])
def search_mechanics():
    name = request.args.get('name')
    
    query = select(Mechanic).where(Mechanic.name.like(f'%{name}%'))
    mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(mechanics), 200