CLIENT_ID = '3a7fad8d-0bb9-4451-87be-e82fa0855ce2'
CLIENT_SECRET = '9b05153f-d0ed-4ba0-a1d6-cd5d4bf9cf30'

import smartcar
from flask import Flask, request, jsonify, abort
import requests
import json
app = Flask(__name__)

client = smartcar.AuthClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri='https://32327f9c.ngrok.io/callback',
    scope=['read_vehicle_info', 'read_location', 'read_odometer'],
    test_mode=False,
)

@app.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    id = request.args.get('state')
    access = client.exchange_code(code)

    print(access)
    response = smartcar.get_vehicle_ids(access['access_token'])
    vehicle_id = response['vehicles'][0]
    global vehicle
    vehicle = smartcar.Vehicle(vehicle_id, access['access_token'])
    # return jsonify(access)


    response = {
        "text": "You have successfully signed in!"
    }

    callSendAPI(id, response)
    return 'Please close this popup window'

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    body = request.json

    if body['object'] == 'page':
        for entry in body['entry']:
            webhook_event = entry['messaging'][0]
            print(webhook_event)
            try:
                user_message = webhook_event['message']['text']
            except KeyError:
                response = {
                    'text':'Please type a valid input'
                }
            else:
                print(user_message)

                if user_message.lower() == 'sign in' or user_message.lower() == 'signin':
                    response = {
                        "attachment":{
                          "type":"template",
                          "payload":{
                            "template_type":"button",
                            "text":"Press the button below!",
                            "buttons":[
                              {
                                "type":"web_url",
                                "url": client.get_auth_url(state=webhook_event['sender']['id']),
                                "title":"Sign in",
                                "webview_height_ratio": "full"
                              }
                            ]
                          }
                        }
                    }
                elif user_message.lower() == 'find':
                    try:
                        location = vehicle.location()
                        latitude = location['data']['latitude']
                        longitude = location['data']['longitude']
                        print(latitude, longitude)
                        response = {
                            'text':'Your car is here!\nhttps://maps.google.com/?q=%s,%s' % (latitude, longitude)
                        }
                    except NameError:
                        response = {
                            'text': 'Pardon? Type \"sign in\" to login'
                        }
                elif user_message.lower() == 'lock':
                    try:
                        vehicle.lock()
                        response = {
                            'text': 'Your car is now locked!'
                        }
                    except NameError:
                        response = {
                            'text': 'Pardon? Type \"sign in\" to login'
                        }
                elif user_message.lower() == 'unlock':
                    try:
                        vehicle.unlock()
                        response = {
                            'text': 'We unlocked your car!'
                        }
                    except NameError:
                        response = {
                            'text': 'Pardon? Type \"sign in\" to login'
                        }
                else:
                    response = {
                        'text':'Forgot where you parked? Shoot our bot a message and it will respond with the location of your car!'
                    }

            callSendAPI(webhook_event['sender']['id'], response)
        return 'EVENT_RECEIVED'
    else:
        abort(404)

@app.route('/webhook', methods=['GET'])
def verify():
    return request.args.get('hub.challenge')

def callSendAPI(sender_psid, response):
    request_body = {
        'recipient': {
            'id': sender_psid
        },
        'message': response
    }
    params = {
        "access_token":'EAAPBvndkCP4BADvlG56O44ODcIRgIWukSZAQmspjCWm760Osbs64nNokvwnkhUsMAhU9ZAyg2SutWXyIOaV3UwufsicB1D5NiuKzDgZB0udE20DejJUyMKwoZA3zrfd3Nes7HTTLPE3tfLBZAxwypCNZB1vIAapG0cKbv9rA4gTenfFlC5ZAIKq'
    }
    r = requests.post('https://graph.facebook.com/v2.6/me/messages', params=params, json=request_body)
    print(r.status_code)
    print(r.text)


if __name__ == '__main__':
    app.run(port=1337)
