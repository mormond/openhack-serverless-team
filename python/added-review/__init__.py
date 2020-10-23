import logging
import json

import azure.functions as func


def main(documents: func.DocumentList, outputEventHubMessage: func.Out[str]) -> str:
    if documents:
        logging.info('Document id: %s', documents[0]['id'])

        for document in documents:
            outputEventHubMessage.set(json.dumps(document.data))

    