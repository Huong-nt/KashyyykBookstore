import unittest
import time
from app import create_app, db
from app.models import User, Role, Permission

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)
    
    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password
    
    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
    
    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)
    
    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
    
    def test_invalid_confirmation_token(self):
        u1 = User(password='cat')
        u2 = User(password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))
    
    def test_expired_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))
    
    def test_viewer_role(self):
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.VIEW))
        self.assertFalse(u.can(Permission.PUBLISH))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_publisher_role(self):
        r = Role.query.filter_by(name='Publisher').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.VIEW))
        self.assertTrue(u.can(Permission.PUBLISH))
        self.assertFalse(u.can(Permission.ADMIN))
    
    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.VIEW))
        self.assertTrue(u.can(Permission.PUBLISH))
        self.assertTrue(u.can(Permission.ADMIN))