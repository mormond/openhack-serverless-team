"""
high level support for doing this and that.
"""
import logging
import uuid
import datetime
import requests

import azure.functions as func


def main(req: func.HttpRequest, doc: func.Out[func.Document]) -> func.HttpResponse: #pylint: disable=E1136
    '''high level support for doing this and that.'''
    logging.info('create_rating function processed a request.')

    try:
        req_body = req.get_json()

        user_id = req_body.get('userId')
        product_id = req_body.get('productId')
        location_name = req_body.get('locationName')
        rating = req_body.get('rating')
        user_notes = req_body.get('userNotes')
        req_body['id'] = str(uuid.uuid4())
        req_body['timestamp'] = str(datetime.datetime.utcnow())

    except ValueError:
        pass

    x = requests.get(f'https://serverlessohproduct.trafficmanager.net/api/GetProduct?productId={product_id}')
    if (x.status_code != 200):
        return func.HttpResponse( \
                "The supplied productId is not recognised.", \
                status_code=404)

    y = requests.get(f'https://serverlessohuser.trafficmanager.net/api/GetUser?userId={user_id}')
    if (y.status_code != 200):
        return func.HttpResponse( \
                "The supplied userId is not recognised.", \
                status_code=404)
    
    if ( rating not in [0,1,2,3,4,5]):
         return func.HttpResponse( \
                "The supplied rating should be an integer between 0 and 5 inclusive.", \
                status_code=404)

    doc.set(func.Document.from_dict(req_body))

    return func.HttpResponse( \
        str(req_body), \
            status_code=200, mimetype='application/json')
            