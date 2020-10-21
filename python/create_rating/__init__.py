"""
high level support for doing this and that.
"""
import logging
import uuid
from datetime import datetime
import json
import requests
import os
import re

import azure.functions as func

def splitParagraphIntoSentences(paragraph):
    sentenceEnders = re.compile('[.!?]')
    sentenceList = sentenceEnders.split(paragraph)
    return sentenceList


def checkSentimentScores(sentimentResult):
    jsonSentimentResult = json.loads(sentimentResult)

    for document in jsonSentimentResult["documents"]:
        negScore = float(document["confidenceScores"]["negative"])
        if negScore >= 0.7:
            return True
    
    return False


def main(req: func.HttpRequest, doc: func.Out[func.Document]) -> func.HttpResponse: #pylint: disable=E1136
    '''high level support for doing this and that.'''
    logging.info('create_rating function processed a request.')

    try:
        req_body = req.get_json()

        user_id = req_body.get('userId')
        product_id = req_body.get('productId')
        #location_name = req_body.get('locationName')
        rating = req_body.get('rating')
        user_notes = req_body.get('userNotes')
        req_body['id'] = str(uuid.uuid4())
        req_body['timestamp'] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")

    except ValueError:
        pass

    check_product_id = requests.get( \
        f'https://serverlessohproduct.trafficmanager.net/api/GetProduct?productId={product_id}')

    if check_product_id.status_code != 200:
        return func.HttpResponse( \
                "The supplied productId is not recognised.", \
                status_code=404)

    check_user_id = requests.get( \
        f'https://serverlessohuser.trafficmanager.net/api/GetUser?userId={user_id}')

    if check_user_id.status_code != 200:
        return func.HttpResponse( \
                "The supplied userId is not recognised.", \
                status_code=404)

    if ( rating not in [0,1,2,3,4,5]):
        return func.HttpResponse( \
            "The supplied rating should be an integer between 0 and 5 inclusive.", \
                status_code=404)

    headers = {
        "Ocp-Apim-Subscription-Key": os.environ['cs_key'],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    url = 'https://meocognitiveservices.cognitiveservices.azure.com/text/analytics/v3.0/sentiment'

    sentences = splitParagraphIntoSentences(user_notes)

    documents = []
    count = 0
    for sentence in sentences:
        count = count+1
        if len(sentence) > 0:
            documents.append( { 
                "language": "en",
                "id": count,
                "text": sentence
                })

    payload = { 
        "documents": documents 
        }

    sentResponse = requests.post(url=url, headers=headers, data=json.dumps(payload))

    if checkSentimentScores(sentResponse.text):
        logging.info(msg="Bad Sentiment")
    else:
        logging.info(msg="Good Sentiment")

    req_body['sentimentScore'] = sentResponse.text

    doc.set(func.Document.from_dict(req_body))

    return func.HttpResponse( \
        json.dumps(req_body), \
            status_code=200, mimetype='application/json')
            