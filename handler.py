"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
from dbtest import Connection

#connection = None
connection = Connection('connection.txt')
# I know it's bad.. global variable for item
global_item = ''

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Lost and Found. " \
            "What are you looking for?"
    reprompt_text = "Please ask me the location of your item by saying, " \
                    "where is my laptop."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying lost and found. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# not used.
def literal_test_in_session(intent, session):
    session_attributes = {}
    should_end_session = True

    literal = intent['slots']['Literal']['value']
    res = connection.literal_test(literal)
    speech_output = res
    reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def set_location_in_session(intent, session):
    """ Add an item to a new location.
    """

    session_attributes = {}
    should_end_session = True

    item = intent['slots']['Item']['value']
    location = intent['slots']['Location']['value']
    if 'next_task' in session['attributes'] \
            and session['attributes']['next_task'] == 'set_location':
        item = session['attributes']['item_name']
    res = connection.set_location(item, location)
    speech_output = item + " is now located in " + location
    reprompt_text = None

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def get_location_from_session(intent, session):
    """Get location name with item name
    """
    session_attributes = {}
    item = intent['slots']['Item']['value']

    res = connection.find_location(item)
    if res[0] == 1:
        location = res[1]
        speech_output = item + " is located in " + location
        # TODO: should end =false --> reprompt: have more to ask?
        should_end_session = True
        reprompt_text = None
        # TODO: right place to call the beeper? do we need thread?
        # res[1][0]: location, res[1][1]: time gap, res[1][2]: true or false
        # if res[1][2] == True:
            #connection.find_location_beep(item)
    else:
        # couldn't find it
        speech_output = res[1] # No item named 'item'. 
        # TODO: shouldend=false --> reprompt: Please try again...
        should_end_session = True
        reprompt_text = None
    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def add_location_in_session(intent, session):
    session_attributes = {}
    should_end_session = True
    reprompt_text = None
    location = intent['slots']['Location']['value'].capitalize()
    res = connection.add_new_location(location)
    if res[0] == 1:
        speech_output = "Location " + location + " was added to the database."
    else:
        speech_output = "Location " + location + " already exists."

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def add_item_in_session(intent, session):
    session_attributes = {}
    item = intent['slots']['Item']['value']
    res = connection.add_new_item(item)
    categories = connection.get_categories()
    categories_str = ', '.join(categories)
    if res[0] == 1:
        speech_output = "Item " + item + " was added to the database. " \
                        "What is the category? Please select a category among "\
                        "%s." % categories_str
        should_end_session = False
        reprompt_text = None
        session_attributes = {'next_task':'set_category', 'item_name': item}
    else:
        should_end_session = True
        speech_output = "Item " + item + " already exists."
        reprompt_text = None

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def set_category_in_session(intent, session):
    if session['attributes']:
        # TODO: should add condition if 'next_task' is 'set category'
        if 'item_name' in session['attributes']:
            item = session['attributes']['item_name'].capitalize()
            category = intent['slots']['Category']['value'].capitalize()
            res = connection.set_category(item, category)
            speech_output = "Item " + item + " is now stored in "+category+ \
                            ". Where do you want to put this item? "\
                            "Please say,for example, I want to put it on desk."
            session_attributes={'next_task':'set_location', 'item_name': item}
        else:
            speech_output = 'session has attributes. but not item name'
            # not sure attibutes should be {}
            session_attributes = {}
    else:
        speech_output = 'session does not have attributes'
        # not sure attibutes should be {}
        session_attributes = {}
    should_end_session = False
    reprompt_text = None

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_recommendation_in_session(intent, session):
    session_attributes = {}
    reprompt_text = None
    should_end_session = False

    item = intent['slots']['Item']['value'].capitalize()
    res = connection.get_recommendation(item)
    speech_output = "I recommend you putting it on " + res + ". " \
            "Do you want to put it there?"
    session_attributes = {'next_task':'set_recommendation',\
            'item_name' : item, 'location_name': res}

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def user_response_in_session(intent, session):
    # case 1 : get recommendation -> yes
    if 'next_task' in session['attributes']:
        if session['attributes']['next_task'] == 'set_recommendation':
            if intent['slots']['YesNo']['value'].startswith('yes'):
                item = session['attributes']['item_name']
                location = session['attributes']['location_name']
                connection.set_location(item, location)
                session_attributes = {}
                speech_output = 'Item ' + item + ' is now located in ' + location
                should_end_session = True
                reprompt_text = None
            if intent['slots']['YesNo']['value'].startswith('no'):
                speech_output = "Choose another location by saying, " \
                        "I want to put " + item + " on desk."
                session_attributes = {'next_task':'set_location',\
                        'item_name': item}
                should_end_session = False
                reprompt_text = None
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print("intent_name=" + intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "WhereIsItem":
        return get_location_from_session(intent, session)
    if intent_name == "SetLocation":
        return set_location_in_session(intent, session)
    if intent_name == "LiteralTest":
        return literal_test_in_session(intent, session)
    if intent_name == "AddItem":
        return add_item_in_session(intent, session)
    if intent_name == "AddLocation":
        return add_location_in_session(intent, session)
    if intent_name == "SetCategory":
        return set_category_in_session(intent, session)
    if intent_name == "GetRecommendation":
        return get_recommendation_in_session(intent, session)
    if intent_name == "UserResponse":
        return user_response_in_session(intent, session)
    #TODO:help intent! ex. browsing categories, locations, nfctag, nfcreader
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    # not using this intent
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")


    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])



