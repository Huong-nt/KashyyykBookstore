
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import api as api, api_restful, logger
from .. import db, boto
from ..utils import Utils
from ..models import User

utils = Utils()

class UserView(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('password', type=str)
    parser.add_argument('email', type=str)
    parser.add_argument('name')
    parser.add_argument('pseudonym')

    @jwt_required
    def get(self):
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        # find user by username
        user = User.query.filter_by(username=current_user['username']).first()
        if user is None:
            abort(404, message="user not found")
        # return user information
        return jsonify({
            'ok': True,
            'data': user.get_response()
        })

    @jwt_required
    def put(self):
        # parse params
        args = self.parser.parse_args()
        params = {
            'password': args['password'],
            'email': args['email'],
            'name': args['name'],
            'pseudonym': args['pseudonym'],
        }
        logger.info(params)
        # remove empty params
        params = utils.remove_none_params(params)

        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        # find user by username
        user = User.query.filter_by(username=current_user['username']).first()
        if user is None:
            abort(404, message="user not found")

        # update user with input params
        for key, value in params.items():
            setattr(user, key, value)
        # commit the changes to database
        db.session.commit()
        # return user information
        return jsonify({
            'ok': True,
            'data': user.get_response()
        })

    @jwt_required
    def delete(self):
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        user = User.query.filter_by(username=current_user['username']).first()
        if user is None:
            abort(404, message="user not found")
        
        # TODO: detele user
        # TODO: detele all published book


api_restful.add_resource(UserView, '/users')
