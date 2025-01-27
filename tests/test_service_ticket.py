from urllib import response
from app import create_app
from app.models import db, ServiceTicket, Mechanic, Customer, Part
import unittest

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        with self.app.app_context():
            db.drop_all()
            db.create_all()

            self.customer = Customer(name='test_customer', email='test@email.com', phone='123-456-7890', password='test')
            db.session.add(self.customer)
            self.service_ticket = ServiceTicket(VIN='1234567890', service_date='2000-01-01', service_desc='test service', customer_id=1)
            db.session.add(self.service_ticket)
            self.mechanic = Mechanic(name='test_mechanic', email='test@email.com', phone='123-456-7890', salary=10, password='test')
            db.session.add(self.mechanic)
            self.part = Part(name='test_part', price=10, quantity=1)
            db.session.add(self.part)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_service_ticket(self):
        service_ticket_payload = {
            'VIN': '987654321',
            'service_date': '2000-01-01',
            'service_desc': 'oil change',
            'customer_id': 1
        }

        response = self.client.post('/service_tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['VIN'], '987654321')

    def test_invalid_create_service_ticket(self):
        service_ticket_payload = {
            'service_date': '2000-01-01',
            'service_desc': 'oil change',
            'customer_id': 1
        }

        response = self.client.post('/service_tickets/', json=service_ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['VIN'], ['Missing data for required field.'])

    def test_edit_service_ticket_mechanics(self):
        service_ticket_edits = {
            'add_mechanic_ids': [1],
            'remove_mechanic_ids': []
        }

        response = self.client.put('/service_tickets/1/edit/mechanics', json=service_ticket_edits)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['mechanics'][0]['name'], 'test_mechanic')

    def test_edit_service_ticket_parts(self):
        service_ticket_edits = {
            'part_id': 1,
            'quantity': 1
        }

        response = self.client.put('/service_tickets/1/edit/parts', json=service_ticket_edits)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/service_tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['parts'][0]['name'], 'test_part')
        
    def test_get_service_tickets(self):
        response = self.client.get('/service_tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['service_desc'], 'test service')

    def test_get_service_ticket(self):
        response = self.client.get('/service_tickets/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['service_desc'], 'test service')

    def test_delete_service_ticket(self):
        response = self.client.delete('/service_tickets/1')
        self.assertEqual(response.status_code, 200)
