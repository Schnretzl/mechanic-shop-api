from app.models import Service_Ticket
from app.extensions import ma
from marshmallow import fields

class Service_TicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested("MechanicSchema", many=True)
    customer = fields.Nested("CustomerSchema")
    
    class Meta:
        model = Service_Ticket
        fields = ('id', 'VIN', 'service_date', 'service_desc', 'customer_id', 'mechanic_ids', 'customer', 'mechanics')
        
service_ticket_schema = Service_TicketSchema()
service_tickets_schema = Service_TicketSchema(many=True)
return_service_tickets_schema = Service_TicketSchema(exclude=['customer_id'], many=True)