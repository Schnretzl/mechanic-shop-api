from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_blueprint
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema
from marshmallow import ValidationError
from app.models import Service_Ticket, Mechanic, db
from sqlalchemy import select, delete

@service_tickets_blueprint.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_service_ticket = Service_Ticket(VIN=service_ticket_data['VIN'], service_date=service_ticket_data['service_date'], service_desc=service_ticket_data['service_desc'], customer_id=service_ticket_data['customer_id'])
    
    for mechanic_id in service_ticket_data['mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalar()
        if mechanic:
            new_service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({'message': 'Invalid mechanic id'}), 404
    
    db.session.add(new_service_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_service_ticket), 201

@service_tickets_blueprint.route('/', methods=['GET'])
def get_service_tickets():
    query = select(Service_Ticket)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

@service_tickets_blueprint.route('/<int:service_ticket_id>', methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    query = delete(Service_Ticket).where(Service_Ticket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({'message': 'Service Ticket deleted'}), 200

@service_tickets_blueprint.route('/<int:service_ticket_id>/edit', methods=['PUT'])
def edit_service_ticket(service_ticket_id):
    try:
        service_ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Service_Ticket).where(Service_Ticket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    for mechanic_id in service_ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic not in service_ticket.mechanics:
            service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({'message': 'Invalid mechanic id', 'id': mechanic_id}), 404
        
    for mechanic_id in service_ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        
        if mechanic and mechanic in service_ticket.mechanics:
            service_ticket.mechanics.remove(mechanic)
            
    db.session.commit()
    print(service_ticket)
    return service_ticket_schema.jsonify(service_ticket), 200