from flask import request, jsonify
from app.blueprints.service_tickets import service_tickets_blueprint
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema, edit_mechanics_service_ticket_schema
from app.blueprints.parts.schemas import part_schema, parts_schema, add_part_service_ticket_schema
from marshmallow import ValidationError
from app.models import ServiceTicket, Mechanic, Part, ServiceTicketPart, db
from sqlalchemy import select, delete

@service_tickets_blueprint.route('/', methods=['POST'])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
        
    new_service_ticket = ServiceTicket(VIN=service_ticket_data['VIN'], service_date=service_ticket_data['service_date'], service_desc=service_ticket_data['service_desc'], customer_id=service_ticket_data['customer_id'])

    if 'mechanic_ids' in service_ticket_data:    
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
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(ServiceTicket)
        service_tickets = db.paginate(query, page=page, per_page=per_page)
        return service_tickets_schema.jsonify(service_tickets), 200
    except:
        query = select(ServiceTicket)
        result = db.session.execute(query).scalars().all()
        return service_tickets_schema.jsonify(result), 200
    
@service_tickets_blueprint.route('/<int:service_ticket_id>', methods=['GET'])
def get_service_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()

    if service_ticket is None:
        return jsonify({'message': 'Service ticket not found'}), 404

    return service_ticket_schema.jsonify(service_ticket), 200

@service_tickets_blueprint.route('/<int:service_ticket_id>', methods=['DELETE'])
def delete_service_ticket(service_ticket_id):
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    
    db.session.delete(service_ticket)
    db.session.commit()
    return jsonify({'message': f'Successfully deleted service ticket {service_ticket_id}'}), 200

@service_tickets_blueprint.route('/<int:service_ticket_id>/edit/mechanics', methods=['PUT'])
def edit_service_ticket_mechanics(service_ticket_id):
    try:
        service_ticket_edits = edit_mechanics_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
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
    return service_ticket_schema.jsonify(service_ticket), 200
        
@service_tickets_blueprint.route('/<int:service_ticket_id>/edit/parts', methods=['PUT'])
def edit_service_ticket_parts(service_ticket_id):
    try:
        edit_data = add_part_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(ServiceTicket).where(ServiceTicket.id == service_ticket_id)
    service_ticket = db.session.execute(query).scalars().first()
    query = select(Part).where(Part.id == edit_data['part_id'])
    part = db.session.execute(query).scalars().first()
    if not service_ticket or not part:
        return jsonify({'message': 'Invalid service ticket or part id'}), 404
    else:
        new_service_ticket_part = ServiceTicketPart(service_ticket_id=service_ticket_id, part_id=edit_data['part_id'], quantity=edit_data['quantity'])
        db.session.add(new_service_ticket_part)
        db.session.commit()  
    
    return add_part_service_ticket_schema.jsonify(new_service_ticket_part), 200