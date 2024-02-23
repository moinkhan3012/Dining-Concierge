import json
import datetime
import os
import dateutil.parser
import logging
from utils import *
import boto3
import time


import re
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)



def ses_send_mail(restaurants_list, dinning_details):
    SENDER = os.environ['SENDER_EMAIL'] 

    RECIPIENT = dinning_details['Email']
    
    SUBJECT = "Restaurant Suggestion from Foody"
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    columns = ['name', 'address', 'rating', 'reviews']
    print(restaurants_list)
    reordered_dicts = [reorder_dict(restaurant, columns) for restaurant in restaurants_list]
    
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



def sqs_send(dinning_details):
    
    try:    
        sqs = boto3.client('sqs')
        result = sqs.send_message(
          QueueUrl = os.environ.get('QUEUE_URL'),
          MessageBody = json.dumps(dinning_details))
    
        logger.info(f"SQS response: {result}")
        
        return True
    
    except Exception as err:
        logger.error(err)
        
        return False


# Function to check if email is valid
def isvalid_email(email):
    # Regular expression pattern for validating email addresses
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

# Function to check if location is valid
def isvalid_location(location):
    logger.info(f"location: {location}")
    valid_cities = ['manhattan']
    return location.lower() in valid_cities

# Function to check if Cuisine Type is valid
def isvalid_cuisine_type(cuisine_type):
    logger.info(cuisine_type)
    cuisine_types = ['italian', 'french', 'indian']
    return cuisine_type.lower() in cuisine_types

# Function to check if date is valid
def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

# Function to check if time is valid
def isvalid_time(time):
    try:
        dateutil.parser.parse(time)
        return True
    except ValueError:
        return False

# Function to build validation result
def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'validationResult': {
            'isValid': isvalid,
            'violatedSlot': violated_slot,
            'message': {'content': message_content, 'contentType': 'PlainText'}
        }
    }

# Function to validate hotel reservation
def validate_dining(slots):
    location = try_ex(lambda: slots['Location']['value']['interpretedValue'])
    d_time = try_ex(lambda: slots['DiningTime']['value']['interpretedValue'])
    d_date =  try_ex(lambda: slots['DiningDate']['value']['interpretedValue'])
    n_people = safe_int(try_ex(lambda: slots['NumberofPeople']['value']['interpretedValue']))
    cuisine = try_ex(lambda: slots['Cuisine']['value']['interpretedValue'])
    email = try_ex(lambda: slots['Email']['value']['interpretedValue'])


    logger.info(f"{location}, {d_time}, {n_people}, {d_date}, {cuisine}, {email}")
    if location:
        if not isvalid_location(location):
            return build_validation_result(False, 'Location', f'We currently do not support {location} as a valid destination. Manhattan is the hottest spot we serve. Could please enter your preferred location?')

    else:
        return build_validation_result(False, 'Location', f'We did not quite understand your Location. Manhattan is the hottest spot we serve. Could please enter your preferred location?')


    if d_date:
        if not isvalid_date(d_date):
            return build_validation_result(False, 'DiningDate', 'I did not understand your date.  When would you like to make reservation?')
        logger.info(datetime.datetime.strptime(d_date, '%Y-%m-%d').date())
        
        logger.info(f"Todays date: {datetime.date.today()}")
        if datetime.datetime.strptime(d_date, '%Y-%m-%d').date() <=  datetime.date.today():
            return build_validation_result(False, 'DiningDate', 'Reservations must be scheduled at least one day in advance. Can you try a different date?')

    if d_time:
        if not isvalid_time(d_time):
            return build_validation_result(False, 'DiningTime', 'I did not get your time.  When would you like to make reservation?')

    if n_people is not None and (n_people < 1 or n_people > 100):
        return build_validation_result(False, 'NumberofPeople', 'You can make a reservation for from 1 to 100 person. How many number of people would you like to make reservation for?')

    if cuisine and not isvalid_cuisine_type(cuisine):
        return build_validation_result(False, 'Cuisine', 'Cuisine Type seems to be inaccurate. Would you like to try  cuisine from italian, chinese, french, indian or mexican?')

    if email and not isvalid_email(email):
        return build_validation_result(False, 'Email', 'Provided Email is inaccurate. Please check the email and try again.')

    return {'validationResult': {'isValid': True}}

# Function to suggest dinining
def dinning_suggestion(intent_request):
    
    intent_name = intent_request['sessionState']['intent']['name']
    
    #get the slot values
    location = try_ex(lambda: intent_request['sessionState']['intent']['slots']['Location']['value']['interpretedValue'])
    d_time = try_ex(lambda: intent_request['sessionState']['intent']['slots']['DiningTime']['value']['interpretedValue'])
    d_date = try_ex(lambda: intent_request['sessionState']['intent']['slots']['DiningDate']['value']['interpretedValue'])
    n_people = safe_int(try_ex(lambda: intent_request['sessionState']['intent']['slots']['NumberofPeople']['value']['interpretedValue']))
    cuisine = try_ex(lambda: intent_request['sessionState']['intent']['slots']['Cuisine']['value']['interpretedValue'])
    email = try_ex(lambda: intent_request['sessionState']['intent']['slots']['Email']['value']['interpretedValue'])
    
    session_attributes = intent_request['sessionState'].get('sessionAttributes', {})

    reservation = {
        'ReservationType': 'Dinning',
        'Location': location,
        'Cuisine': cuisine,
        'DiningTime': d_time,
        'DiningDate': d_date,
        'NumberofPeople': n_people,
        'Email': email
    }

    #check the invocationsource
    if intent_request['invocationSource']=="DialogCodeHook":
        
        #validate the slots
        validation_result = validate_dining(intent_request['sessionState']['intent']['slots'])
        logger.info(validation_result)
        
        # ask again for the correct value if there is any invalid slots
        if not validation_result['validationResult']['isValid']:
            return elicit_slot(intent_request['sessionState'], validation_result['validationResult']['violatedSlot'], validation_result['validationResult']['message'])

        else:
            # Pass directly to Lex
            return delegate(intent_request['sessionState'])

            
    # TODO : replace Close by confirm intent in fullfillmentcodehook
    elif intent_request['invocationSource'] == 'FulfillmentCodeHook':

        reservation['user_id'] = intent_request['sessionId']
        result = sqs_send(reservation)
        logger.debug(f"SQS result: {result}")
       
        message = {
           "contentType": "PlainText",
            "content": "You’re all set. Expect my suggestions shortly! Have a good day."
        }
        if result:
            return close(intent_name,  message)

        else:
            message['content'] = "Sorry, we are facing some issues!"
            return close(intent_name,  message)

    message = {'contentType': 'PlainText', 'content': 'You’re all set. Expect my suggestions shortly! Have a good day.'}
    return close(intent_name,  message)


def greeting_intent(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    logger.info("In GreetingIntent")
    closing_message = {
    "contentType": "PlainText",
    "content": "Hi there, how can I help?",
    
    }
    
    #check if user has past suggestions in dynamo db
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('past-restaurant-suggestions')
    
    restaurants_list = table.get_item(Key={'user_id': '63944ade-e6fd-4476-b145-ffa7fed74fd4'}) 

    logger.info(f"restaurants_list: {restaurants_list}")


    if intent_request['interpretations'][0]['intent']['confirmationState']=='Confirmed':
        logger.info(f"sessionAttributes: {intent_request['sessionState']['sessionAttributes']}")
    
        data = json.loads(intent_request['sessionState']['sessionAttributes']['restaurants_list'])
    
        logger.info(f"Load restaurants: {data}")

        ses_send_mail(data['restaurants'] , data['dinning_details'])
        message = {
            'content': "Great! You will receive suggestions on your email shortly!", 
            'contentType': 'PlainText'
        }
    
        intent_request['sessionState']['sessionAttributes'] = {}
        return close(intent_name,  message)
    
    elif intent_request['interpretations'][0]['intent']['confirmationState']=='Denied':
        message = {
            'content': "No problem! Tell me how can I assist you today?", 
            'contentType': 'PlainText'
        }
        intent_request['sessionState']['sessionAttributes'] = {}
        return close(intent_name,  message)

    if 'Item' in restaurants_list:
        #check if intent is
    
        cuisine_type = restaurants_list['Item']['dinning_details']['Cuisine']
        location = restaurants_list['Item']['dinning_details']['Location']
        message = {
            'content': f"You previously requested suggestions for {cuisine_type} in {location}, do you want it over the email now?", 
            'contentType': 'PlainText'
        }
    
        intent_request['sessionState']['sessionAttributes'].update({'restaurants_list': json.dumps(restaurants_list['Item'], default=decimal_default)})
        # Pass the confirmIntent
        return confirm_intent(intent_request['sessionState'], message)
    
    return close(intent_name,  closing_message)
    
def thankyou_intent(intent_name):
    message = {
    "contentType": "PlainText",
    "content": "You’re welcome! Have a nice day.",
    
    }
    
    
    return close(intent_name,  message)
    

# Function to dispatch intent
def dispatch(intent_request):

    intent_name = intent_request['sessionState']['intent']['name']

    logger.debug(f'Intent Name: {intent_name}')
    if intent_name == 'DiningSuggestionsIntent':
        response =  dinning_suggestion(intent_request)
        logger.debug(f"response of dinning_suggestion: {response}")
        return response
    elif intent_name =='GreetingIntent':
        return greeting_intent(intent_request)

    elif intent_name =='ThankYouIntent':
        return thankyou_intent(intent_name)
        
        
    raise Exception('Intent with name ' + intent_name + ' not supported')



# Lambda handler
def lambda_handler(event, context):
    logger.debug('event.bot.name={}'.format(event['bot']['name']))
    logger.info(event)
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    return dispatch(event)
