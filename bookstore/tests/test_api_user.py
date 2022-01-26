import unittest
from wsgiref import headers
from flask import current_app
from web import create_app, db
from web.models import User, Role, Permission


class ApiUserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

        # create a Publisher and a Viewer
        r = Role.query.filter_by(name='Publisher').first()
        self.u1 = User(email='john@example.com', username='JohnPublisher',
                  password='cat@big', pseudonym='JP', role=r)
        r = Role.query.filter_by(name='Viewer').first()
        self.u2 = User(email='doe@example.com', username='DoeViewer',
                  password='dog@small', pseudonym='DV', role=r)
        db.session.add(self.u1)
        db.session.add(self.u2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_information(self):
        # Add a user
        r = Role.query.filter_by(name='Viewer').first()
        u = User(email='u@example.com', username='U',
                 password='dog@small', pseudonym='SU', role=r)
        db.session.add(u)
        db.session.commit()

        # get access token
        response = self.client.post('bookstore/api/v1/auth', data={
            'username': 'U',
            'password': 'dog@small'
        })
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        token = response_json['data']['token']

        # Get user information
        response = self.client.get(
            'bookstore/api/v1/users', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(response_json['data']['username'], 'U')

        # Update user information
        response = self.client.put(
            'bookstore/api/v1/users',
            headers={'Authorization': f'Bearer {token}'},
            data={
                'name': 'A Viewer',
            }
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(response_json['data']['name'], 'A Viewer')

        # Delete user
        response = self.client.delete(
            'bookstore/api/v1/users', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)

    def test_user_publish_book(self):
        # get access token
        response = self.client.post('bookstore/api/v1/auth', data={
            'username': 'JohnPublisher',
            'password': 'cat@big'
        })
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        token = response_json['data']['token']

        # Publish a book
        response = self.client.post(
            f'bookstore/api/v1/users/{self.u1.id}/books',
            headers={'Authorization': f'Bearer {token}'},
            data={
                'title': 'Game of Animal',
                'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                'price': 30000
            },
            # files=[
            #     ('cover', ('2.c.png', open('/C:/Users/huong/Pictures/2.c.png', 'rb'), 'image/png'))
            # ]
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(response_json['data']['title'], 'Game of Animal')
        self.assertEqual(response_json['data']['price'], 30000)
        # Save book information
        book = response_json['data']
        
        # Update a book
        response = self.client.put(
            f"bookstore/api/v1/users/{self.u1.id}/books/{book['id']}",
            headers={'Authorization': f'Bearer {token}'},
            data={
                'price': 35000,
            }
        )
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(response_json['data']['price'], 35000)

        # Delete a book
        response = self.client.delete(
            f"bookstore/api/v1/users/{self.u1.id}/books/{book['id']}",
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
