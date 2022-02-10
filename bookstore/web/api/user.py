
import uuid
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, reqparse
import werkzeug
from werkzeug.utils import secure_filename

from . import api as api, api_restful, logger
from .. import db, boto
from ..utils import Utils
from ..utils.s3 import S3
from ..models import User, Book, Permission
from ..schema.book import validate_publish_book, validate_update_book
from ..utils.response import build_response, get_content_type

utils = Utils()

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'bmp'])


class UserView(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('password', type=str)
    parser.add_argument('email', type=str)
    parser.add_argument('name')
    parser.add_argument('pseudonym')

    @jwt_required()
    def get(self):
        content_type = get_content_type(request.args)
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        # find user by username
        user = User.query.filter_by(id=current_user['userid']).first()
        if user is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            }, content_type)

        # return user information
        return build_response({
            'ok': True,
            'code': 200,
            'data': user.get_response()
        }, content_type)

    @jwt_required()
    def put(self):
        content_type = get_content_type(request.args)
        # parse params
        args = self.parser.parse_args()
        params = {
            'password': args['password'],
            'email': args['email'],
            'name': args['name'],
            'pseudonym': args['pseudonym'],
        }
        # logger.info(params)
        # remove empty params
        params = utils.remove_none_params(params)

        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        # find user by user_id
        user = User.query.filter_by(id=current_user['userid']).first()
        if user is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            }, content_type)

        # update user with request params
        for key, value in params.items():
            setattr(user, key, value)
        # commit the changes to database
        try:
            db.session.commit()
            # return user information
            return build_response({
                'ok': True,
                'code': 200,
                'data': user.get_response()
            }, content_type)
        except Exception as e:
            # Rollback if it have any error
            logger.error(e)
            return {
                'ok': False,
                'code': 500,
                'message': 'internal server error'
            }, 200
        
    @jwt_required()
    def delete(self):
        content_type = get_content_type(request.args)
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        # find user by user_id
        user = User.query.filter_by(id=current_user['userid']).first()
        if user is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            }, content_type)

        try:
            # Detele all published book and then, delete the user
            Book.query.filter_by(author_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
            return build_response({
                'ok': False,
                'code': 200,
            }, content_type)
        except Exception as e:
            # Rollback if it have any error
            logger.error(e)
            db.session.rollback()
            return build_response({
                'ok': False,
                'code': 500,
                'message': 'internal server error'
            }, content_type)


api_restful.add_resource(UserView, '/users')


class UserPublicBookView(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', help='title cannot be blank')  # default type: unicode
    parser.add_argument('description')  # default type: unicode
    parser.add_argument('cover', type=werkzeug.datastructures.FileStorage, location='files')
    parser.add_argument('price', type=int)

    def __init__(self) -> None:
        super().__init__()

        # Init Aws s3 client
        self.S3_BUCKET_NAME = 'kashyyyk-resources'
        self.s3 = S3(boto.clients['s3'])

    @jwt_required()
    def get(self, user_id):
        content_type = get_content_type(request.args)
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        if user_id != current_user['userid']:
            return build_response({
                'ok': False,
                'code': 403,
                'message': 'jwt token not belong to user_id'
            }, content_type)
        # find user by id
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            }, content_type)

        books = Book.query.filter_by(author_id=user_id).all()
        res = [book.to_json() for book in books]

        return build_response({
            'ok': True,
            'code': 200,
            'data': res
        }, content_type)

    @jwt_required()
    def post(self, user_id):
        content_type = get_content_type(request.args)
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        if user_id != current_user['userid']:
            return build_response({
                'ok': False,
                'code': 403,
                'message': 'jwt token not belong to user_id'
            }, content_type)

        args = self.parser.parse_args()
        logger.info(args)

        # find user by id
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            }, content_type)
        
        # Check user permission
        if user.can(Permission.PUBLISH) == False:
            return build_response({
                'ok': False,
                'code': 401,
                'message': 'user does not have permission to publish the book'
            }, content_type)
        # parse book cover file content
        book_cover_url = None
        if 'cover' in args and args['cover'] != None and args['cover'].filename != '':
            file_cover = args['cover']
            file_name = secure_filename(file_cover.filename)
            file_extension = file_name.rsplit('.', 1)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                return build_response({
                    'ok': False,
                    'code': 400,
                    'message': 'file extension is not one of our supported types'
                }, content_type)
            # TODO: upload book cover to S3 (set public access)
            image_key_name = f'books/cover/' + uuid.uuid4().hex + '.' + file_extension
            book_cover_url = self.s3.upload_public(self.S3_BUCKET_NAME, image_key_name, file_cover, file_extension)

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
            return build_response({
                'ok': True,
                'code': 200,
                'data': book.get_response()
            }, content_type)
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return build_response({
                'ok': False,
                'code': 500,
                'message': 'internal server error'
            }, content_type)

    @jwt_required()
    def put(self, user_id, book_id):
        content_type = get_content_type(request.args)
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        if user_id != current_user['userid']:
            return build_response({
                'ok': False,
                'code': 403,
                'message': 'jwt token not belong to user_id'
            }, content_type)

        args = self.parser.parse_args()
        logger.info(args)

        # find user by id
        user = User.query.filter_by(id=user_id).first()
        if user is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'user not found'
            })
        book = Book.query.filter_by(id=book_id, author_id=user_id).first()
        if book is None:
            return build_response({
                'ok': False,
                'code': 404,
                'message': 'book not found or user do not have permission to update the book'
            }, content_type)
        
        params = {
            'title': args['title'],
            'description': args['description'],
            'price': args['price'],
        }
        logger.info(params)
        if 'cover' in args and args['cover'] != None and args['cover'].filename != '':
            # parse book cover file content and upload to aws S3
            file_cover = args['cover']
            file_name = secure_filename(file_cover.filename)
            file_extension = file_name.rsplit('.', 1)[1].lower()
            # Check file extension
            if file_extension not in ALLOWED_EXTENSIONS:
                return build_response({
                    'ok': False,
                    'code': 400,
                    'message': 'file extension is not one of our supported types'
                }, content_type)
            # upload book cover to S3 (set public access)
            image_key_name = f'books/cover/' + uuid.uuid4().hex + '.' + file_extension
            params['cover'] = self.s3.upload_public(self.S3_BUCKET_NAME, image_key_name, file_cover, file_extension)

        params = utils.remove_none_params(params)
        try:
            # update book with request params
            for key, value in params.items():
                setattr(book, key, value)
            # commit the changes to database
            db.session.commit()
            # return user information
            return build_response({
                'ok': True,
                'code': 200,
                'data': book.get_response()
            }, content_type)
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return build_response({
                'ok': False,
                'code': 500,
                'message': 'internal server error'
            })
    
    @jwt_required()
    def delete(self, user_id, book_id):
        content_type = get_content_type(request.args)
        # get basic information of user in JWT token
        current_user = get_jwt_identity()
        if user_id != current_user['userid']:
            return build_response({
                'ok': False,
                'code': 403,
                'message': 'jwt token not belong to user_id'
            }, content_type)
        
        try:
            # Delete a published book
            Book.query.filter_by(id=book_id, author_id=user_id).delete()
            db.session.commit()
            return build_response({
                'ok': True,
                'code': 200,
            }, content_type)
        except Exception as e:
            # Rollback if it have any error
            logger.error(e)
            db.session.rollback()
            return build_response({
                'ok': False,
                'code': 500,
                'message': 'internal server error'
            }, content_type)


api_restful.add_resource(
    UserPublicBookView, 
    '/users/<int:user_id>/books',
    '/users/<int:user_id>/books/<int:book_id>',
)