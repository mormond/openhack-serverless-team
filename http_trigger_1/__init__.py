"""
high level support for doing this and that.
"""
import logging

import azure.functions as func

def 
main(req: func.HttpRequest) -> func.HttpResponse:
    '''high level support for doing this and that.'''
    logging.info('Python HTTP trigger function processed a request.')

    try:
        product_id = req.route_params.get('productID')
    except ValueError:
        pass

    if product_id:
        return func.HttpResponse( \
            f"The product name for your product id {product_id} is Starfruit Explosion")

    return func.HttpResponse( \
            "This HTTP triggered function executed successfully. \
                Pass a productID in the query string or in the form /productID/xxx.",
            status_code=200)
