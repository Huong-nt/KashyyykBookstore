
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from . import api as api, api_restful, logger
from .. import db, boto
from ..utils import Utils
from ..models import User, Book

utils = Utils()

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'bmp'])


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
            return jsonify({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            })

        # return user information
        return jsonify({
            'ok': True,
            'code': 200,
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
            return jsonify({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            })

        # update user with input params
        for key, value in params.items():
            setattr(user, key, value)
        # commit the changes to database
        db.session.commit()
        # return user information
        return jsonify({
            'ok': True,
            'code': 200,
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


class UserPublicBookView(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', help='title cannot be blank',
                        required=True)  # default type: unicode
    parser.add_argument('description')  # default type: unicode
    parser.add_argument(
        'cover', type=werkzeug.datastructures.FileStorage, location='files')
    parser.add_argument('price', type=int)

    @jwt_required
    def get(self, user_id):
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        if user_id != current_user['userid']:
            return jsonify({
                'ok': False,
                'code': 403,
                'message': 'jwt token not belong to user_id'
            })
        # find user by id
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return jsonify({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            })

        books = Book.query.filter_by(author_id=user_id).all()
        res = [book.to_json() for book in books]

        return jsonify({
            'ok': True,
            'data': res
        })

    @jwt_required
    def post(self, user_id):
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        if user_id != current_user['userid']:
            return jsonify({
                'ok': False,
                'code': 403,
                'message': 'jwt token not belong to user_id'
            })

        args = self.parser.parse_args()
        logger.info(args)

        # find user by id
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return jsonify({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            })

        # parse book cover file content
        file_cover = args['cover']
        file_name = secure_filename(file_cover.filename)
        file_extension = file_name.rsplit('.', 1)[1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            return jsonify({
                'ok': False,
                'code': 400,
                'message': 'file extension is not one of our supported types'
            })
        # TODO: upload book cover to S3 (set public access)
        book_cover_url = ''
        try:
            book = Book(
                title=args['title'],
                description=args['description'],
                cover=book_cover_url,
                price=args['price'],
                author_id=user_id,
            )
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return jsonify({
                'ok': False,
                'code': 500,
                'message': 'internal server error'
            })

    @jwt_required
    def push(self, user_id, book_id):
        pass
    
    @jwt_required
    def delete(self, user_id, book_id):
        pass


api_restful.add_resource(
    UserPublicBookView, 
    '/users/<int:user_id>/books',
    '/users/<int:user_id>/books/<int:book_id>',
)