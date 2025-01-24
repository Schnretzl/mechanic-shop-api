from app import create_app
from app.models import db, Customer
import unittest

from app.utils.util import encode_token

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.customer = Customer(name='test_user', email='test@email.com', phone='123-456-7890', password='test')
            db.session.add(self.customer)
            db.session.commit()
        self.token = encode_token('admin')
        self.client = self.app.test_client()
            
    def test_create_customer(self):
        customer_payload = {
            'name': 'John Doe',
            'email': 'jdoe@email.com',
            'phone': '987-654-3210',
            'password': 'password'
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')
        
    def test_invalid_create_customer(self):
        customer_payload = {
            'name': 'John Doe',
            'email': 'jdoe@email.com',
            'password': 'password'
        }
        
        response = self.client.post('/customers/', json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['phone'], ['Missing data for required field.'])
        
    def test_login_customer(self):
        credentials = {
            'email': 'test@email.com',
            'password': 'test'
        }
        
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
        
    def test_invalid_login_customer(self):
        credentials = {
            'email': 'bad_email@email.com',
            'password': 'bad_password'
        }
        
        response = self.client.post('/customers/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password.')
        
    def test_update_customer(self):
        update_payload = {
            'name': 'Peter',
            'email': '',
            'phone': '',
            'password': ''
        }
        
        headers = {'Authorization': 'Bearer ' + self.test_login_customer()}
        
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter')
        self.assertEqual(response.json['email'], 'test@email.com')
        
    def test_get_customers(self):
        response = self.client.get('/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')

    def test_delete_customer(self):
        headers = {'Authorization': 'Bearer ' + self.test_login_customer()}
        response = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response.status_code, 200)