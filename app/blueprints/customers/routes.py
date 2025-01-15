from flask import request, jsonify
from app.blueprints.customers import customers_blueprint
from app.blueprints.customers.schemas import CustomerSchema, customer_schema, customers_schema, login_schema
from app.extensions import limiter, cache
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select
from app.utils.util import encode_token, token_required

@customers_blueprint.route('/login', methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()
    
    if customer and customer.password == password:
        token = encode_token(customer.id)
        
        response = {
            'status': 'success',
            'message': 'Successfully logged in',
            'token': token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'message': 'Invalid email or password.'}), 401

@customers_blueprint.route('/', methods=['POST'])
@limiter.limit("3 per hour")
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'], password=customer_data['password'])
    
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

@customers_blueprint.route('/', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted'}), 200