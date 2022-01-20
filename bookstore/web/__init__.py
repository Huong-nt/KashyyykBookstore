
import sys
import os
import json
import datetime
import decimal
import time
import logging
from bson.objectid import ObjectId
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

from config import config
from boto3.session import Session
from .utils.flask_boto3 import Boto3


class JSONEncoder(json.JSONEncoder):
    ''' extend json-encoder class'''

    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, (datetime.date, datetime.datetime, datetime.time)):
            return str(o)
        if isinstance(o, decimal.Decimal):
            return str(o)

        return json.JSONEncoder.default(self, o)


db = SQLAlchemy()
jwt = JWTManager()
boto = Boto3()
limiter = Limiter(
    key_func=get_ipaddr,
    default_limits=["5000 per day", "1000 per hour"]
)

def create_app(config_name):
    app = Flask(__name__)
    config[config_name].init_app(app)

    app.logger.setLevel(logging.DEBUG)
    app.config.from_object(config[config_name])
    boto3_session = Session(
        aws_access_key_id=app.config['BOTO3_ACCESS_KEY'],
        aws_secret_access_key=app.config['BOTO3_SECRET_KEY'],
        region_name=app.config['BOTO3_REGION']
    )

    db.init_app(app)
    jwt.init_app(app)
    boto.init_app(app)
    limiter.init_app(app)
    CORS(app, resources=r'/bookstore/api/*', allow_headers=['Content-Type', 'Authorization'])

    app.json_encoder = JSONEncoder
    
    # from .api import api
    # app.register_blueprint(api, url_prefix='/bookstore/api/v1')

    return app
