from app import create_app
from app.models import db, Mechanic
import unittest

from app.utils.util import encode_token

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            self.mechanic = Mechanic(name='test_user', email='test@email.com', phone='123-456-7890', salary=10, password='test')
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token('admin')
        self.client = self.app.test_client()
            
    def test_create_mechanic(self):
        mechanic_payload = {
            'name': 'John Doe',
            'email': 'jdoe@email.com',
            'phone': '987-654-3210',
            'salary': 10,
            'password': 'password'
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'John Doe')
        
    def test_invalid_create_mechanic(self):
        mechanic_payload = {
            'name': 'John Doe',
            'email': 'jdoe@email.com',
            'salary': 10,
            'password': 'password'
        }
        
        response = self.client.post('/mechanics/', json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['phone'], ['Missing data for required field.'])
        
    def test_login_mechanic(self):
        credentials = {
            'email': 'test@email.com',
            'password': 'test'
        }
        
        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        return response.json['token']
        
    def test_invalid_login_mechanic(self):
        credentials = {
            'email': 'bad_email@email.com',
            'password': 'bad_password'
        }
        
        response = self.client.post('/mechanics/login', json=credentials)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], 'Invalid email or password.')
        
    def test_update_mechanic(self):
        update_payload = {
            'name': 'Peter',
            'email': '',
            'phone': '',
            'salary': 20,
            'password': ''
        }
        
        headers = {'Authorization': 'Bearer ' + self.test_login_mechanic()}
        
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Peter')
        self.assertEqual(response.json['email'], 'test@email.com')
        
    def test_get_mechanics(self):
        response = self.client.get('/mechanics/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')

    def test_delete_mechanic(self):
        headers = {'Authorization': 'Bearer ' + self.test_login_mechanic()}
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        
    def test_popular_mechanics(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')
        
    def test_search_mechanics(self):
        response = self.client.get('/mechanics/search?name=test_user')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'test_user')