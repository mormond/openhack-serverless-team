from typing import List
import logging
import json
import os

import azure.functions as func
from azure.servicebus import TopicClient
from azure.servicebus import Message

def main(events: List[func.EventHubEvent], doc: func.Out[func.Document], msg: func.Out[str]): #pylint: disable=E1136

    sb_connection_str = os.environ['AzureServiceBusConnectionString']
    sb_client = TopicClient(address=sb_connection_str, name='receipts')

    for event in events:

        payload = event.get_body().decode('utf-8')

        logging.info('Python EventHub trigger processed an event: %s', payload)
        doc.set(func.Document.from_json(payload))

        order = json.loads(payload)
        if (order['header']['receiptUrl'] != None):
            totalCost = 0.0

            for line_item in order['details']:
                totalCost = totalCost + float(line_item['totalCost'])

            x = {
                "totalItems": len(order['details']),
                "totalCost": totalCost,
                "salesNumber": order['header']['salesNumber'],
                "salesDate": order['header']['dateTime'],
                "storeLocation": order['header']['locationId'],
                "receiptUrl": order['header']['receiptUrl']
                }

            sb_client.send(Message(json.dumps(x)))
      
