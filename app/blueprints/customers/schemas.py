from app.models import Customer
from app.extensions import ma

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
customer_login_schema = CustomerSchema(exclude=['name', 'phone'])