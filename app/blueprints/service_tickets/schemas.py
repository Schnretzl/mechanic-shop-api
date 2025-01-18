from app.models import ServiceTicket
from app.extensions import ma
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", many=True)
    customer = fields.Nested("CustomerSchema")
    parts = fields.Nested("PartSchema", many=True)
    class Meta:
        model = ServiceTicket
        include_fk = True
        fields = ('id', 'VIN', 'service_date', 'service_desc', 'customer_id', 'mechanic_ids', 'customer', 'mechanics', 'parts')
        
class EditMechanicsServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')
    
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
customer_service_tickets_schema = ServiceTicketSchema(exclude=['customer_id', 'customer'], many=True)
edit_mechanics_service_ticket_schema = EditMechanicsServiceTicketSchema()