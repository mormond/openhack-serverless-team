import logging
import json

import azure.functions as func


def main(documents: func.DocumentList, outputEventHubMessage: func.Out[str]) -> str:
    if documents:
        logging.info('Document id: %s', documents[0]['id'])

        for document in documents:

            sentiments = json.loads(document.data['sentimentScore'])['documents']
            sentimentScore = 0.0
            for sentiment in sentiments:
                sentimentScore = sentimentScore + float(sentiment['confidenceScores']['positive'])
            aveSentimentScore = sentimentScore / len(sentiments)

            message = {
                "timestamp": document.data['timestamp'],
                "productId": document.data['productId'],
                "sentimentScore": aveSentimentScore
            }

            outputEventHubMessage.set(json.dumps(message))

    