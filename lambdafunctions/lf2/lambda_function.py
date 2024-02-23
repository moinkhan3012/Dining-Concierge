import json
import boto3
import logging
import os
import requests
import random
from utils import *
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def create_or_update_users_past_suggestions(restaurants_list, dinning_details):
    
    try:
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('past-restaurant-suggestions')
    
        record = {
            'user_id' : dinning_details['user_id'],
            'dinning_details': dinning_details,
            'restaurants': restaurants_list,
            }
            
        logger.info(f"past-restaurant-suggestions: {record}")
        response = table.put_item(
           Item=record
        )
    
    except Exception as err:
        print(err)
        logger.error(err)
        return None 
    
    logger.info(f"Updating records in past-restaurant-suggestions {response}")
    return response

def ses_send_mail(restaurants_list, dinning_details):
    SENDER = os.environ['SENDER_EMAIL'] 

    RECIPIENT = dinning_details['Email']
    
    SUBJECT = "Restaurant Suggestion from Foody"
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    columns = ['name', 'address', 'rating', 'reviews']
    #reorder dict
    reordered_dicts = [reorder_dict(restaurant, columns) for restaurant in restaurants_list['Responses']['yelp-restaurants']]

    BODY_HTML = dict_to_html_table(reordered_dicts, dinning_details['Cuisine'], dinning_details['Location'])

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': BODY_HTML,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    # Display an error if something goes wrong.	
    except Exception as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def sqs_receive_message():
    sqs = boto3.client('sqs')
    result = sqs.receive_message(
        QueueUrl = os.environ.get('QUEUE_URL'), 
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=0,
        WaitTimeSeconds=0
        )

    return result


def sqs_delete_message(receipt_handle):
    sqs = boto3.client('sqs')
    response = sqs.delete_message(
        QueueUrl= os.environ.get('QUEUE_URL'),
        ReceiptHandle=receipt_handle
    )
    
    logger.info(f"SQS deleted message {response}")

def lambda_handler(event, context):
    # TODO implement
    
    logger.info(event)

    result = sqs_receive_message()
    logger.info(f"SQS receive_message: {result}")


    if 'Messages' not in result:
        return {
            'statusCode': 200,
            'body': json.dumps('No messages in the queue')
        }
        
        
    #load the data in json
    
    for message in result['Messages']:
        dinning_details = json.loads(message['Body'])
        receipt_handle = message['ReceiptHandle']
    
        
        # Get list from elastic search
        host = os.environ.get('ES_HOST')
        url = host + '/_search?q=cuisine_type:{}&size=1000'.format(dinning_details['Cuisine'])
        response = requests.get(url, auth=(os.environ.get('ES_USERNAME'), os.environ.get('ES_PASSWORD'))) 
        
        logger.info(response)
        restaurant_data = json.loads(response.text)
        
        if restaurant_data['hits']['total']['value'] > 0:
            data_list = restaurant_data['hits']['hits']
            random_list = list(map(lambda x: x['_id'], data_list))
        
        selected_restaurants = random.sample(random_list, k = 5)
        
    
        client = boto3.resource('dynamodb')
        
        restaurants_list = client.batch_get_item(
            RequestItems={
                'yelp-restaurants': {'Keys': [{'business_id': id} for id in selected_restaurants]}
            }
        )
        
        logger.info(restaurants_list)
        ses_send_mail(restaurants_list, dinning_details)

        create_or_update_users_past_suggestions(restaurants_list['Responses']['yelp-restaurants'], dinning_details)
        sqs_delete_message(receipt_handle)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
