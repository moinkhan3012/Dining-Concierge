import json
import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel("INFO")

def lambda_handler(event, context):

    logger.info(f"Event {event}")
    message = event['messages'][0]

    logger.info(f"Context {context}")

    # Send the message to your Lex chatbot
    lex = boto3.client('lexv2-runtime')
    response = lex.recognize_text(
        botId='546ED9RSO9', 
        botAliasId='TSTALIASID',
        sessionId= '63944ade-e6fd-4476-b145-ffa7fed74fd4',
        localeId='en_US',  
        text=message['unstructured']['text']
    )
    
    logger.info(response)

    messages = []
    for message in response['messages']:
        if message['contentType'] != 'PlainText':
            messages.append({ 'type' : 'structured', 'structured' : { 'text': message['content']}})

        else:
            messages.append({ 'type' : 'unstructured', 'unstructured' : { 'text': message['content']}})
        

    # Send back the response from Lex as the API response
    return {
        'statusCode': 200,
        'messages': messages
    }