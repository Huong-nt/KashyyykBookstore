
import json
import uuid

from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource, reqparse, abort

from . import api as api, api_restful, logger
from .. import db
from ..models import User, Role, RoleUser
from ..schema.user import validate_user_authentication, validate_user
from ..utils import Utils

utils = Utils()


class UserRegistration(Resource):
    ''' register user endpoint '''
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, help='Username cannot be blank', required=True)
    parser.add_argument('password', type=str, help='Password cannot be blank', required=True)
    parser.add_argument('email', type=str)
    parser.add_argument('name')
    parser.add_argument('pseudonym')
    parser.add_argument('avatar', type=str)

    def post(self):
        args = self.parser.parse_args()
        args = {
            'username': args['username'],
            'password': args['password'],
            'email': args['email'],
            'name': args['name'],
            'pseudonym': args['pseudonym'],
            'address': args['address'],
        }
        logger.info(args)
        data = validate_user(utils.remove_none_params(args))
        if data['ok']:
            data = data['data']
            logger.info(data)
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            role = Role.query.filter_by(name="normal_user").first()
            roleUser = RoleUser(user_id=user.id, role_id=role.id)
            db.session.add(roleUser)
            db.session.commit()
            return {'ok': True, 'message': 'User created successfully!'}, 200
        else:
            return {'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'].message)}, 400


api_restful.add_resource(UserRegistration, '/register')


class UserAuth(Resource):
    ''' auth endpoint '''
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, help='Username cannot be blank', required=True)
    parser.add_argument('password', type=str, help='Password cannot be blank', required=True)

    def post(self):
        args = self.parser.parse_args()
        # logger.info(request.headers['X-Forwarded-For'])
        data = validate_user_authentication(args)
        if data['ok']:
            data = data['data']
            user = User.query.filter_by(username=data['username']).first()
            if not user:
                abort(404, message="user not found or not confirmed")

            if user.verify_password(data['password']):
                access_token = create_access_token(identity=data)
                # refresh_token = create_refresh_token(identity=data)
                res = {
                    'token': access_token,
                    # 'refresh': refresh_token
                }
                return {'ok': True, 'data': res}, 200
            else:
                return {'ok': False, 'message': 'invalid username or password'}, 401
        else:
            return {'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'].message)}, 400


api_restful.add_resource(UserAuth, '/auth')
