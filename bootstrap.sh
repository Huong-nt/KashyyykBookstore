#!/bin/sh
export FLASK_APP=./bookstore/flasky.py
export FLASK_CONFIG=development
# export FLASK_ENV=development
source $(pipenv --venv)/bin/activate
flask run -h 0.0.0.0 -p 5002
