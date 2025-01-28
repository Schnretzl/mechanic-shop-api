from flask import request, jsonify
from app.blueprints.customers import customers_blueprint
from app.blueprints.customers.schemas import customer_schema, customers_schema, customer_login_schema
from app.blueprints.service_tickets.schemas import customer_service_tickets_schema
from app.extensions import limiter, cache
from marshmallow import ValidationError
from app.models import Customer, db
from sqlalchemy import select
from app.utils.util import encode_token, token_required

@customers_blueprint.route('/login', methods=['POST'])
def login():
    try:
        credentials = customer_login_schema.load(request.json)
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
def get_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page)
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        result = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(result), 200

@customers_blueprint.route('/my-tickets', methods=['GET'])
@token_required
def get_customer_tickets(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    
    if customer is None:
        return jsonify({'message': 'Customer not found'}), 404
    
    service_tickets = customer.service_tickets
    
    return customer_service_tickets_schema.jsonify(service_tickets), 200

@customers_blueprint.route('/', methods=['PUT'])
@token_required
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
        if value:
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
    return jsonify({'message': f'Successfully deleted customer {customer_id}'}), 200