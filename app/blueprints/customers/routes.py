from flask import request, jsonify
from app.blueprints.customers import customers_blueprint
from app.blueprints.customers.schemas import customer_schema, customers_schema
from app.extensions import limiter, cache
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select, delete

@customers_blueprint.route('/', methods=['POST'])
@limiter.limit("3 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

@customers_blueprint.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(result), 200

@customers_blueprint.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    if customer is None:
        return jsonify({'message': 'Customer not found'}), 404
    
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in customer_data.items():
        setattr(customer, field, value)
        
    db.session.commit()
    
    return customer_schema.jsonify(customer), 200

@customers_blueprint.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Member deleted'}), 200