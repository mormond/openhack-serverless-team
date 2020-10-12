import logging

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        productID = req.route_params.get('productID')
    except ValueError:
        pass

    if productID:
        return func.HttpResponse(f"The product name for your product id {productID} is Starfruit Explosion")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a productID in the query string or in the form /productID/xxx.",
             status_code=200
        )
