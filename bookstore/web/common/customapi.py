from flask import request
import flask_restful
import logging
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from flask_jwt_extended.exceptions import NoAuthorizationError, JWTDecodeError, InvalidHeaderError

from ..utils.response import build_response, get_content_type

class CustomApi(flask_restful.Api):
    def handle_error(self, e):
        content_type = get_content_type(request.args)
        if isinstance(e, ExpiredSignatureError):
            return build_response({"ok": False, "code": 401, "error": "token has expired"}, content_type)
        if isinstance(e, NoAuthorizationError):
            return build_response({"ok": False, "code": 401, "error": "token is missing"}, content_type)
        if isinstance(e, InvalidHeaderError):
            return build_response({"ok": False, "code": 401, "error": "token is missing"}, content_type)
        if isinstance(e, JWTDecodeError) or isinstance(e, InvalidSignatureError):
            return build_response({"ok": False, "code": 403, "error": "can not decode the token"}, content_type)

        message = ''
        if hasattr(e, 'message'):
            message = str(e.message)
        if hasattr(e, 'data') and message == '':
            if 'message' in e.data:
                message = str(e.data['message'])
        if hasattr(e, 'description') and message == '':
            message = e.description
        
        response = {"ok": False, 'error': message}
        if hasattr(e, 'code'):
            response['code'] = e.code
            return build_response(response, content_type)
        else:
            response['code'] = 500
            for attr in dir(e):
                logging.error("obj.%s = %r" % (attr, getattr(e, attr)))
            return build_response(response, content_type)
