from flask import request, jsonify
from app.blueprints.parts import parts_blueprint
from app.blueprints.parts.schemas import part_schema, parts_schema
from app.blueprints.service_tickets.schemas import customer_service_tickets_schema
from app.extensions import limiter, cache
from marshmallow import ValidationError
from app.models import Part, db
from sqlalchemy import select


@parts_blueprint.route('/', methods=['POST'])
def create_part():
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_part = Part(name=part_data['name'], price=part_data['price'], quantity=part_data['quantity'])
    
    db.session.add(new_part)
    db.session.commit()
    
    return part_schema.jsonify(new_part), 201

@parts_blueprint.route('/', methods=['GET'])
# @cache.cached(timeout=60)
def get_parts():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Part)
        parts = db.paginate(query, page=page, per_page=per_page)
        return parts_schema.jsonify(parts), 200
    except:
        query = select(Part)
        result = db.session.execute(query).scalars().all()
        return parts_schema.jsonify(result), 200

@parts_blueprint.route('/<int:part_id>/service_tickets', methods=['GET'])
def get_part_tickets(part_id):
    query = select(Part).where(Part.id == part_id)
    part = db.session.execute(query).scalars().first()
    
    if part is None:
        return jsonify({'message': 'Part not found'}), 404
    
    service_tickets = part.service_tickets
    print(service_tickets)
    
    return customer_service_tickets_schema.jsonify(service_tickets), 200
    

@parts_blueprint.route('/<int:part_id>', methods=['PUT'])
def update_part(part_id):
    query = select(Part).where(Part.id == part_id)
    part = db.session.execute(query).scalars().first()
    
    if part is None:
        return jsonify({'message': 'Part not found'}), 404
    
    try:
        part_data = part_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in part_data.items():
        setattr(part, field, value)
        
    db.session.commit()
    
    return part_schema.jsonify(part), 200

@parts_blueprint.route('/<int:part_id>', methods=['DELETE'])
def delete_part(part_id):
    query = select(Part).where(Part.id == part_id)
    part = db.session.execute(query).scalars().first()
    
    if part is None:
        return jsonify({'message': 'Part not found'}), 404
    
    db.session.delete(part)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted part {part_id}'}), 200