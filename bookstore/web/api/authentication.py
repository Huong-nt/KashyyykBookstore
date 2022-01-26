
import json
import uuid

from flask import jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource, reqparse, abort

from . import api as api, api_restful, logger
from .. import db
from ..models import User, Role
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

    def post(self):
        args = self.parser.parse_args()
        args = {
            'username': args['username'],
            'password': args['password'],
            'email': args['email'],
            'name': args['name'],
            'pseudonym': args['pseudonym'],
        }
        logger.info(args)
        data = validate_user(utils.remove_none_params(args))
        if data['ok']:
            data = data['data']
            logger.info(data)
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            return {'ok': True, 'code': 200, 'message': 'User created successfully!'}, 200
        else:
            return jsonify({
                'ok': False,
                'code': 400,
                'message': f'Bad request parameters: {data["message"].message}'
            })


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
                return jsonify({
                    'ok': False,
                    'code': 404,
                    'message': 'user not found'
                })
            # Add user id information to token
            data['userid'] = user.id

            # Verify the password 
            if user.verify_password(data['password']):
                # Create and embed the user information into access token
                access_token = create_access_token(identity=data)
                # refresh_token = create_refresh_token(identity=data)
                res = {
                    'token': access_token,
                    # 'refresh': refresh_token
                }
                return jsonify({'ok': True, 'code': 200, 'data': res})
            else:
                return jsonify({
                    'ok': False,
                    'code': 401,
                    'message': 'invalid username or password'
                })
        else:
            return jsonify({
                'ok': False,
                'code': 400,
                'message': f'Bad request parameters: {data["message"].message}'
            })


api_restful.add_resource(UserAuth, '/auth')
