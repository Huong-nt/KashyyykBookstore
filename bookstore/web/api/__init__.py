#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app
from werkzeug.local import LocalProxy
from ..common.customapi import CustomApi

api = Blueprint('bookstore-api', __name__)
api_restful = CustomApi(api)

logger = LocalProxy(lambda: current_app.logger)

from . import user, book
