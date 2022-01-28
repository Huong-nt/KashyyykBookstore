from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError


user_register_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "maxLength": 128},
        "password": {
            "type": "string",
            "minLength": 5,
            "maxLength": 64
        },
        "email": { "type": "string", "format": "email" },
        "name": { "type": "string", "maxLength": 128 },
        "pseudonym": { "type": "string", "maxLength": 128 },
    },
    "required": ["username", "email", "password"],
    "additionalProperties": False
}


def validate_register_user(data):
    try:
        validate(data, user_register_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


user_authentication_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string", "maxLength": 128},
        "password": {
            "type": "string",
            "minLength": 5
        }
    },
    "required": ["username", "password"],
    "additionalProperties": False
}


def validate_user_authentication(data):
    try:
        validate(data, user_authentication_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
