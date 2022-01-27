import json
import unittest
from wsgiref import headers
from flask import current_app
from web import create_app, db
from web.models import User, Role, Book


class ApiBookTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

        # create a Publisher
        r = Role.query.filter_by(name='Publisher').first()
        self.u1 = User(
            email='john@example.com',
            username='JohnPublisher',
            password='cat@big',
            pseudonym='JP',
            role=r
        )
        db.session.add(self.u1)
        db.session.commit()

        # Create some books
        books = [
            {
                'title': 'Sapiens A Brief History of Humankind',
                'description': 'Most books about the history of humanity pursue either a historical or a biological approach, but Dr. Yuval Noah Harari breaks the mold with this highly original book that begins about 70,000 years ago with the appearance of modern cognition',
                'price': 15000,
                'author_id': 1,
            },
            {
                'title': '21 Lessons for the 21st Century',
                'description': 'How do computers and robots change the meaning of being human? How do we deal with the epidemic of fake news? Are nations and religions still relevant? What should we teach our children?',
                'price': 30000,
                'author_id': 1,
            },
        ]
        for book in books:
            db.session.add(Book(
                title=book['title'],
                description=book['description'],
                price=book['price'],
                author_id=book['author_id'],
            ))
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_book_by_id(self):
        # Get user information
        response = self.client.get('bookstore/api/v1/books/1')
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)

    def test_search_book(self):
        # Case 1: search all book have price >= 40000
        #   return 0 book
        query = {
            "filters": [
                {"name": "price", "op": "ge", "val": 40000}
            ]}
        response = self.client.get(
            f"bookstore/api/v1/books?q={json.dumps(query)}",
        )
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(len(response_json['data']), 0)

        # Case 2: search all book have price >= 20000
        #   return 1 book
        query = {
            "filters": [
                {"name": "price", "op": "ge", "val": 20000}
            ]}
        response = self.client.get(
            f"bookstore/api/v1/books?q={json.dumps(query)}",
        )
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(len(response_json['data']), 1)

        # Case 3: search all book have title contains "sapiens"
        #   return 1 book
        query = {
            "filters": [
                {"name": "title", "op": "ilike", "val": '%sapiens%'}
            ]}
        response = self.client.get(
            f"bookstore/api/v1/books?q={json.dumps(query)}",
        )
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        response_json = response.get_json()
        self.assertEqual(response_json['code'], 200)
        self.assertEqual(len(response_json['data']), 1)
