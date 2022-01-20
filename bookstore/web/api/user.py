
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
    def get(self, user_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="user not found")
        return jsonify({
            'ok': True,
            'data': user.get_response()
        })

    @jwt_required
    def put(self, user_id):
        current_user = get_jwt_identity()
        
        args = self.parser.parse_args()
        params = {
            'password': args['password'],
            'email': args['email'],
            'name': args['name'],
            'pseudonym': args['pseudonym'],
        }
        logger.info(params)
        params = utils.remove_none_params(params)

        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="user not found")

        for key, value in params.items():
            setattr(user, key, value)
        db.session.commit()
        return jsonify({
            'ok': True,
            'data': user.get_response()
        })

    @jwt_required
    def delete(self, user_id):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            abort(404, message="user not found")
        
        # TODO: detele user
        # TODO: detele all published book


api_restful.add_resource(UserView, '/users/<int:user_id>')
