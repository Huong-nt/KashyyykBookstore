
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm import backref, aliased
from sqlalchemy import literal, null

import operator
from sqlalchemy.orm.collections import MappedCollection, collection


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    permission = db.Column(db.Text, nullable=False, default='normal')
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)

    def to_json(self):
        _json = {
            'id': self.id,
            'name': self.name,
            'permission': self.permission,
            'created': self.created,
            'updated': self.updated,
        }
        return _json


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128))
    username = db.Column(db.String(30), unique=True, index=True, nullable=False)
    email = db.Column(db.String(128), unique=True, index=True, nullable=False)
    name = db.Column(db.String(128))
    pseudonym = db.Column(db.String(128))
    gender = db.Column(db.Enum('male', 'female'), default='male')
    avatar = db.Column(db.String(100))
    confirmed = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), onupdate=datetime.utcnow)

    # gateways = db.relationship('Gateway', secondary='user_gateway', backref='users', lazy='dynamic')
    gateways = association_proxy('user_gateways', 'gateways',
                    creator=lambda k, v: UserGateway(gateway_role_id=k, gateway=v)
                )

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User: {}>'.format(self.id)

    def to_json(self):
        _json = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'gender': self.gender,
            'confirmed': self.confirmed,
            'created': self.created,
            'updated': self.updated,
        }
        return _json

    def get_response(self):
        return self.to_json()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except:
            return False


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1024))
    description = db.Column(db.Text)
    cover = db.Column(db.String(1024))
    price = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    updated = db.Column(db.DateTime(), onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Book, self).__init__(**kwargs)

    def __repr__(self):
        return '<Book: {}>'.format(self.id)

    def to_json(self):
        _json = {
            'id': self.id,
            'type': self.type.to_json(),
            'sim': self.sim,
            'imei': self.imei,
            'hardware_version': self.hardware_version,
            'firmware_version': self.firmware_version,
            'mfg': self.mfg,
            'alert': self.alert,
            'blocking': self.blocking,
            'testing': self.testing,
            'state': self.state,
            'config': self.config.to_json() if self.config is not None else {},
            'subscription': self.subscription.to_json() if self.subscription is not None else None,
            'node_count': self.nodes.count(),
            'groups': [group.to_json() for group in self.groups],
            'contacts': [contact.to_json() for contact in self.contacts],
            'created': self.created,
            'updated': self.updated,
        }
        return _json

    def response_simple(self):
        _json = {
            'id': self.id,
            'type': self.type.to_json(),
            'imei': self.imei,
            'hardware_version': self.hardware_version,
            'firmware_version': self.firmware_version,
            'mfg': self.mfg,
        }
        return _json


class RoleUser(db.Model):
    __tablename__ = 'role_user'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    def __init__(self, **kwargs):
        super(RoleUser, self).__init__(**kwargs)

    def to_json(self):
        _json = {
            'role_id': self.role_id,
            'user_id': self.user_id,
        }
        return _json


class PublishedBook(db.Model):
    __tablename__ = 'published_books'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))

    def __init__(self, **kwargs):
        super(PublishedBook, self).__init__(**kwargs)

    def to_json(self):
        _json = {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
        }
        return _json

