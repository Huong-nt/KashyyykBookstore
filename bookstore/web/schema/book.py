from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError


book_publish_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "maxLength": 1024},
        "description": {"type": "string"},
        "cover": {"type": "string"},
        "price": {"type": "integer", "minimum": 0},
    },
    "required": [],
    "additionalProperties": False
}


def validate_publish_book(data):
    try:
        validate(data, book_publish_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_update_book(data):
    try:
        validate(data, book_publish_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}