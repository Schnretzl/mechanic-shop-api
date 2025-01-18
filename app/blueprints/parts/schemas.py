from app.models import Part
from app.extensions import ma
from marshmallow import fields

class PartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Part
        
class AddPartsServiceTicketSchema(ma.Schema):
    part_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    class Meta:
        fields = ('part_id', 'quantity')
        
part_schema = PartSchema()
parts_schema = PartSchema(many=True)
add_part_service_ticket_schema = AddPartsServiceTicketSchema()