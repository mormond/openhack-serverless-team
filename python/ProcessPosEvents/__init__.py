from typing import List
import logging

import azure.functions as func


def main(events: List[func.EventHubEvent], doc: func.Out[func.Document]):
    for event in events:

        payload = event.get_body().decode('utf-8')

        logging.info('Python EventHub trigger processed an event: %s', payload)
        doc.set(func.Document.from_json(payload))
