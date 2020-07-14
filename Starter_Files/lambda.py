### Required Libraries ###
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response

def validate_data(age, investment_amount, intent_request):
    if age is not None:
        # birth_date = datetime.strptime(age,"%Y-%m-%d")
        # age1 = relativedelta(datetime.now(), birth_date).years
        age = int(age)
        if age > 65:
            return build_validation_result(
                False,
                "birthday",
                "You should be at under 65 years old to use this service, "
                "please provide a different date of birth.",
            )
        if investment_amount is not None:
            inv = int(
                investment_amount
            )  # Since parameters are strings it's important to cast values
            if inv < 5000:
                return build_validation_result(
                    False,
                    "usdAmount",
                    "The amount to invest should be greater than 5000, "
                    "please provide a correct amount.",
                )

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)
### Intents Handlers ###


# ### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        slots = get_slots(intent_request)
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        val_result = validate_data(age, investment_amount, intent_request)

        ### YOUR DATA VALIDATION CODE STARTS HERE ###
        if not val_result['isValid']:
            slots[val_result['violatedSlot']] = None
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                val_result["violatedSlot"],
                val_result["message"],
            )
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation
    print(investment_amount)
    print(type(investment_amount))
    recommend=""
    if risk_level == 'None':
        recommend = 'Invest all $'+ investment_amount + ' in bonds(AGG)'
    elif risk_level == 'Very Low':
        recommend = 'Invest $'+ str(int(investment_amount) * 0.9) + 'in bonds(AGG) and ' + str(int(investment_amount) * 0.1) +' in equities (SPY).'
    elif risk_level == 'Low':
        recommend = 'Invest $'+ str(int(investment_amount) * 0.8) + 'in bonds(AGG) and ' + str(int(investment_amount) * 0.2) +' in equities (SPY).'
    elif risk_level == 'Moderate':
        recommend = 'Invest $'+str(int(investment_amount)*.4) + 'in bonds(AGG) and ' + str(int(investment_amount)*.6)+' in equities (SPY).'  
    elif risk_level == 'Semi-Moderate':
        recommend = 'Invest $'+str(int(investment_amount)*.3) + 'in bonds(AGG) and ' + str(int(investment_amount)*.7)+' in equities (SPY).'  
    else:
        recommend = 'Invest all $'+investment_amount+' in equities (SPY).'
    # return recommend
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, recommend
            ),
        },
    )


### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

