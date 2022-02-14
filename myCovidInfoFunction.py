
import json
import datetime
import requests

def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']
    
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None    

def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']

    return {}

def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [ message ] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }


def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }
    
def api_data():
    api = "https://api.covid19api.com/summary"
    json_d = requests.get(api).json()
    return json_d
    
def get_covid_data():
    json_data = api_data()
    countries = json_data['Countries']
    country_total_cases = countries[122]["TotalConfirmed"]
    return country_total_cases
  
def global_deaths(intent_request):
    session_attributes = get_session_attributes(intent_request)
    json_data = api_data()
    countries = json_data['Global']
    global_covid_deaths = countries['TotalDeaths']
    text = "Total Covid-19 deaths in the world is {}".format(global_covid_deaths)
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)
    
def covid_global(intent_request):
    session_attributes = get_session_attributes(intent_request)
    json_data = api_data()
    countries = json_data['Global']
    global_cases = countries['TotalConfirmed']
    text = "Total Covid-19 cases in the world is {}.".format(global_cases)
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)
    
def covid_total_recoveries(intent_request):
    session_attributes = get_session_attributes(intent_request)
    json_data = api_data()
    countries = json_data['Countries']
    country_name  = countries[122]["Country"]
    country_total_recoveries = countries[122]["TotalRecovered"]
    text = "The total recoveries patient in {} is {}".format(country_name, country_total_recoveries)
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)
    
def covid_total_deaths(intent_request):
    session_attributes = get_session_attributes(intent_request)
    json_data = api_data()
    countries = json_data['Countries']
    country_name  = countries[122]["Country"]
    country_total_deaths = countries[122]["TotalDeaths"]
    text = "The total deaths due to Covid-19 in {} is {}".format(country_name, country_total_deaths)
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)
    
def covid_new_cases(intent_request):
    session_attributes = get_session_attributes(intent_request)
    json_data = api_data()
    countries = json_data['Countries']
    country_name  = countries[122]["Country"]
    country_new_cases = countries[122]["NewConfirmed"]
    text = "The new cases of covid-19 in {} is {}".format(country_name, country_new_cases)
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)

def covid_info(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    country_slot_name = get_slot(intent_request, 'countryName')
    if country_slot_name == "Nepal":
        covid_case = get_covid_data()
        text = "Total number of cases in {} is {}".format(country_slot_name, covid_case)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)

def convert_date_of_birth(intent_request):
    slots = get_slots(intent_request)
    get_date = get_slot(intent_request, 'dateOfBirth')
    date = datetime.datetime.now()
    age = date.year - get_date
    return age


def collect_question(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    user_name = get_slot(intent_request, 'name')
    covid_symptom = get_slot(intent_request, 'symptoms')
    covid_symptoms = ['Fever', 'Cough', 'Tiredness', 'Loss  Taste and Smell']
    current_adds = ['OutsideValley', 'InsideValley']
    current_address = get_slot(intent_request, 'currentAddress')
    vaccine = get_slot(intent_request, 'vaccination')
    date_of_birth = get_slot(intent_request, 'dateOfBirth')
    if vaccine == "Full Dose" and covid_symptom == "None":
        text = "{}. You do not need to quarantine or seek doctor.".format(user_name)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
        
    elif vaccine == "Full Dose" and current_address in current_adds and covid_symptom in covid_symptoms:
        text = "{}. You need to quarantine for 3 days and take care in personal health.".format(user_name)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)

    elif vaccine == "None" and current_address == "OutsideValley" and covid_symptom in covid_symptoms:
        text = "{}. You need to quarantine and please seek to your doctor as soon as possible.".format(user_name)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
        
    elif vaccine == "Half Dose" and current_address == "InsideValley" and  covid_symptom in covid_symptoms:
        text = "{}. You need to quarantine for 7 days and take care in personal health.".format(user_name)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
    elif vaccine == "Half Dose" and current_address == "OutsideValley" and  covid_symptom in covid_symptoms:
        text = "{}. You need to quarantine for 14 days and if needed please seek to your doctor.".format(user_name)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
        
    elif vaccine == "None" and current_address in current_adds and covid_symptom == "None":
        text = "{}. You do not need to quarantine but please get a vaccine as soon as possible.".format(user_name)
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
    else:
        return None
    fulfillment_state = 'Fulfilled'
    return close(intent_request, session_attributes, fulfillment_state, message)

def ask_question(intent_request):
    session_attributes = get_session_attributes(intent_request)
    slots = get_slots(intent_request)
    yes_no = get_slot(intent_request, 'yesOrNo')
    
    if yes_no == "Yes":
        text = "Nice! Now we'll ask you some questions, Please answer each question/statement as honestly as possible. Type *"+"Start"+"* to continue." 
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
        
        
    elif yes_no == "No":
        text = text = "Take care, If you need any help please visit here again!"
        message = {
            'contentType': 'PlainText',
            'content': text
        }
        return elicit_intent(intent_request, session_attributes, message)
    else:
        return None

    fulfillment_state = "Fulfilled"    
    return close(intent_request, session_attributes, fulfillment_state, message)   

def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']
    response = None
    # Dispatch to your bot's intent handlers
    if intent_name == 'AskQuestion':
        return ask_question(intent_request)
    elif intent_name == 'CollectQuestion':
        return collect_question(intent_request)
    elif intent_name == 'CovidInfo':
        return covid_info(intent_request)
    elif intent_name == 'CovidNewCases':
        return covid_new_cases(intent_request)
    elif intent_name == 'TotalDeaths':
        return covid_total_deaths(intent_request)
    elif intent_name == 'TotalRecoveries':
        return covid_total_recoveries(intent_request)
    elif intent_name == 'Global':
        return covid_global(intent_request)
    elif intent_name == 'GlobalDeaths':
        return global_deaths(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')

def lambda_handler(event, context):
    response = dispatch(event)
    return response