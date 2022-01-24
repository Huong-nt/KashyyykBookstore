import unittest
from wsgiref import headers
from flask import current_app
from web import create_app, db
from web.models import User, Role, Permission


class ApiAuthenticationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_and_authen(self):
        # register a new account
        response = self.client.post('bookstore/api/v1/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat@big',
            'name': 'John',
        })
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)

        # get access token
        response = self.client.post('bookstore/api/v1/auth', data={
            'username': 'john',
            'password': 'cat@big'
        })
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)

        token = response_json['data']['token']
        # validate token
        response = self.client.get('bookstore/api/v1/users', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(response_json['data']['username'], 'john')
    
