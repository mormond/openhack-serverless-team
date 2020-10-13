"""
high level support for doing this and that.
"""
import logging

import azure.functions as func


def main(req: func.HttpRequest, doc: func.DocumentList) -> func.HttpResponse:
    '''high level support for doing this and that.'''
    logging.info('get_rating function processed a request.')

    if not doc:
        logging.warning("Rating item not found")
        return func.HttpResponse("Item not found.", status_code=404)
    else:
        logging.info("Found ToDo item")

    return func.HttpResponse(str(doc[0].data), status_code=200, mimetype='application/json')

