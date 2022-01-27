
from ast import arg
from flask import jsonify, Response
from dicttoxml import dicttoxml

def build_response(content_dict, content_type='json') -> Response:
    '''
    Return response for request base on content type, which is json or xml
    '''
    if content_type == 'xml':
        # Convert dict to xml
        xml = dicttoxml(content_dict)
        return Response(response=xml, status=200, mimetype="application/xml")
    else:
        return jsonify(content_dict)

def get_content_type(args) -> str:
    '''
    Return type of content based on query param: json(default) or xml
    '''
    if 'contentType' in args and args['contentType'] == 'xml':
        return 'xml'
    return 'json'