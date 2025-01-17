from app.models import Service_Ticket
from app.extensions import ma
from marshmallow import fields

class Service_TicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", many=True)
    customer = fields.Nested("CustomerSchema")
    class Meta:
        model = Service_Ticket
        fields = ('id', 'VIN', 'service_date', 'service_desc', 'customer_id', 'mechanic_ids', 'customer', 'mechanics')
        
class EditServiceTicketSchema(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')
    
service_ticket_schema = Service_TicketSchema()
service_tickets_schema = Service_TicketSchema(many=True)
customer_service_tickets_schema = Service_TicketSchema(exclude=['customer_id', 'customer'], many=True)
edit_service_ticket_schema = EditServiceTicketSchema()