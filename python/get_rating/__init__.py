"""
high level support for doing this and that.
"""
import logging
import json

import azure.functions as func


def main(req: func.HttpRequest, doc: func.DocumentList) -> func.HttpResponse: # pylint: disable=W0613
    '''high level support for doing this and that.'''
    logging.info('get_rating function processed a request.')

    if not doc:
        logging.warning("Rating item not found")
        return func.HttpResponse("Item not found.", status_code=404)

    logging.info("Found Rating item")

    return func.HttpResponse(json.dumps(doc[0].data),
                                status_code=200,
                                mimetype='application/json')
