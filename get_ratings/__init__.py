"""
high level support for doing this and that.
"""
import logging
import json
import azure.functions as func


def main(req: func.HttpRequest, doc: func.DocumentList) -> func.HttpResponse:
    '''high level support for doing this and that.'''
    logging.info('get_ratings function processed a request.')

    if not doc:
        logging.warning("UserId not found")
        return func.HttpResponse("UserId not found.", status_code=404)
    else:
        logging.info("Found UserId.")

    response = []
    for d in doc.data:
        d.pop("_attachments")
        response.append(d.data)

    return func.HttpResponse(json.dumps(response), 
                                status_code=200, 
                                mimetype='application/json')
