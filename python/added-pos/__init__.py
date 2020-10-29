import logging
import json

import azure.functions as func


def main(documents: func.DocumentList, outputEventHubMessage: func.Out[str]) -> str:
    if documents:
        logging.info('Document id: %s', documents[0]['id'])

        for document in documents:
            for detail in document.data['details']:
                outputEventHubMessage.set(json.dumps(detail))

    