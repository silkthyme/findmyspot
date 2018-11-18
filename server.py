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
    vehicle = smartcar.Vehicle(vehicle_id, access['access_token'])
    location = vehicle.location()
    latitude = location['data']['latitude']
    longitude = location['data']['longitude']
    print(latitude, longitude)
    text = {
        'text':'https://maps.google.com/?q=%s,%s' % (latitude, longitude)
    }
    callSendAPI(id, text)
    # return jsonify(access)
    return 'Please close this popup window'

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    body = request.json

    if body['object'] == 'page':
        for entry in body['entry']:
            webhook_event = entry['messaging'][0]
            print(webhook_event)
            print(webhook_event['message']['text'])
            response = {
                "attachment":{
                  "type":"template",
                  "payload":{
                    "template_type":"button",
                    "text":"Click to locate your car",
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
