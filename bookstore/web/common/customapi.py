from flask import Blueprint, jsonify
import flask_restful
import logging
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError, InvalidHeaderError

class CustomApi(flask_restful.Api):
    def handle_error(self, e):
        if isinstance(e, ExpiredSignatureError):
            return jsonify({"ok": False, "error": "token has expired"}), 401
        if isinstance(e, NoAuthorizationError):
            return jsonify({"ok": False, "error": "token is missing"}), 401
        if isinstance(e, InvalidHeaderError):
            return jsonify({"ok": False, "error": "token is missing"}), 401
        if isinstance(e, JWTDecodeError) or isinstance(e, InvalidSignatureError):
            return jsonify({"ok": False, "error": "can not decode the token"}), 403

        message = ''
        if hasattr(e, 'message'):
            message = str(e.message)
        if hasattr(e, 'data') and message == '':
            if 'message' in e.data:
                message = str(e.data['message'])
        if hasattr(e, 'description') and message == '':
            message = e.description
            
        response = {"ok": False, 'error': message}
        try:
            return jsonify(response), e.code
        except Exception as e:
            for attr in dir(e):
                logging.error("obj.%s = %r" % (attr, getattr(e, attr)))
            return jsonify(response), 500
