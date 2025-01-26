from app import create_app
from app.models import db, Part
import unittest

class TestPart(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.part = Part(name='test_part', price=50, quantity=1)
            db.session.add(self.part)
            db.session.commit()
        self.client = self.app.test_client()
            
    def test_create_part(self):
        part_payload = {
            'name': 'oil',
            'price': 25,
            'quantity': 10,
        }
        
        response = self.client.post('/parts/', json=part_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'oil')
        
    def test_invalid_create_part(self):
        part_payload = {
            'name': 'oil',
            'quantity': 1
        }
        
        response = self.client.post('/parts/', json=part_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['price'], ['Missing data for required field.'])

    def test_update_part(self):
        update_payload = {
            'name': 'air filter',
            'price': 10,
            'quantity': 5
        }
        
        response = self.client.put('/parts/1', json=update_payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'air filter')
        self.assertEqual(response.json['price'], 10)
        self.assertEqual(response.json['quantity'], 5)
        
    def test_get_parts(self):
        response = self.client.get('/parts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_part')

    def test_delete_part(self):
        response = self.client.delete('/parts/1')
        self.assertEqual(response.status_code, 200)
