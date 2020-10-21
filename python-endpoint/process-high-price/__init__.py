import logging
import json
from base64 import b64encode

import requests
import azure.functions as func

def main(message: func.ServiceBusMessage) -> func.InputStream: #pylint: disable=E1136
    # Log the Service Bus Message as plaintext

    #message_content_type = message.content_type
    message_body = message.get_body().decode("utf-8")

    logging.info("Python ServiceBus topic trigger processed message.")
    #logging.info("Message Content Type: " + message_content_type)
    logging.info("Message Body: " + message_body)

    messagePayload = json.loads(message_body)

    receiptUrl = messagePayload["receiptUrl"]

    r = requests.get(receiptUrl)
    pdfEncoded = b64encode(r.content)

    outPayload = {
        "Store": messagePayload["storeLocation"],
        "SalesNumber": messagePayload["salesNumber"],
        "TotalCost": messagePayload["totalCost"],
        "Items": messagePayload["totalItems"],
        "SalesDate": messagePayload["salesDate"],
        "ReceiptImage": pdfEncoded.decode('utf-8')
    }

    return json.dumps(outPayload)
