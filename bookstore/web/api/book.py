
import json

from flask import jsonify, request, current_app
from flask_restful import Resource
from flask_restless import search

from . import api as api, api_restful, logger
from .. import db
from ..models import Book
from ..utils import filter

def validate_query_filters(args):
    '''
    q={
        "filters": [
            {"name":"price","op":"ge","val":10000},
        ]
    }
    or
    q={
        "filters": [
            {"name":"title","op":"ilike","val":"%game%"},
        ]
    }
    '''
    if 'q' in args:
        q = args['q'].replace('\n', '')
        q = json.loads(q)
        return q['filters']


class BookView(Resource):
    def get(self, book_id=None):
        # Get information of a book by book id
        if book_id is not None:
            book = Book.query.filter_by(id=book_id).first()
            if book is None:
                return jsonify({
                    'ok': False,
                    'code': 404,
                    'message': 'user not found'
                })
            return jsonify({
                'ok': True,
                'code': 200,
                'data': book.get_response()
            })
        # Get all book by conditions
        else:
            # TODO: pagination
            args = request.args
            try:
                filters = validate_query_filters(args)
            except:
                return jsonify({
                    'ok': False,
                    'code': 400,
                    'message': 'filter is invalid'
                })
            if filters == None:
                books = Book.query.all()
            else:
                books = search.search(db, Book, filters).all()
            return jsonify({
                'ok': True,
                'code': 200,
                'data': [book.get_response() for book in books]
            })


api_restful.add_resource(
    BookView,
    '/books',
    '/books/<int:book_id>',
)
