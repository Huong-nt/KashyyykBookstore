
from flask import jsonify, request, current_app
from flask_restful import Resource, reqparse

from ..models import Book


class BookView(Resource):
    parser = reqparse.RequestParser()

    def get(self, book_id):
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
            # pagination

            books = Book.query.filter_by().all()
            return jsonify({
                'ok': True,
                'code': 200,
                'data': [book.get_response() for book in books]
            })

    


