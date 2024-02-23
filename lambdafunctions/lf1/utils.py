from decimal import Decimal

def elicit_slot(session_state, slot_to_elicit, message=None):
    session_state['dialogAction'] =  {
            'type': 'ElicitSlot',
            'slotToElicit': slot_to_elicit
            }

    response = {
        'sessionState': session_state
    }    

    if message:
        response['messages'] = [message]
    return response


def confirm_intent(session_state, message=None):
    
    session_state['dialogAction'] = {
        'type': 'ConfirmIntent'
        }
        
    return {
    'sessionState': session_state,
    'messages': [message] or []
    }



def close(intent_name, message):
    
    session_state = {
        "dialogAction": {
            "type": "Close"
        },
        "intent": {
            "name": intent_name,
            "state": "Fulfilled"
        }
    }
    
    
    
    return {
        'sessionState': session_state,
        'messages': [message]
    }


def delegate(session_state):
    session_state["dialogAction"]= {
            "type": "Delegate"
        }
    return {
        'sessionState': session_state,
    }
    
    

    
    # return {
    #     'sessionState': session_state,
    #     'dialogAction': {
    #         'type': 'Delegate',
    #         'slots': slots
    #     }
    # }


# --- Helper Functions ---

def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed-in function in a try block. If KeyError is encountered, return None.
    This function is intended to be used to safely access dictionaries.
    """
    try:
        return func()
    except (KeyError, TypeError) as e:
        return None


def decimal_default(obj):
    try:    
        if isinstance(obj, Decimal):
            return float(obj)
    except Exception as err:
        return str(obj)
        
        

def reorder_dict(d, key_order):
    """Reorder keys in a dictionary."""
    return {key: d[key] for key in key_order if key in d}

def dict_to_html_table(data, cuisine_type, location):
    # Start building HTML table
    html_table = f"""<html>
            <head></head>
            <body>
            <h1> Here is your suggestions for {cuisine_type.title()} restaurants in {location}</h1>.
            <table border='1'>"""

    # Add table header
    html_table += "<tr>"
    for key in data[0].keys():
        html_table += f"<th>{key.title()}</th>"
    html_table += "</tr>"

    # Add table rows
    for item in data:
        html_table += "<tr>"
        for key, value in item.items():
            html_table += f"<td>{str(value).title()}</td>"
        html_table += "</tr>"

    # Close HTML table
    html_table += """</table>
        <br><br>
        <p> Hope you like the suggestions.
                </body>
            </html>"""

    return html_table

