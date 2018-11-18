'use strict';

// imports dependencies and set up http server
const
	express = require('express'),
	bodyParser = require('body-parser'),
        request = require('request'),
	app = express().use(bodyParser.json()); // creates express http server

// sets server port and logs message on success
app.listen(process.env.PORT || 1337, () => console.log('webhook is listening'));

// creates the endpoint for our webhook
app.post('/webhook', (req, res) => {

	let body = req.body;

	// checks this is an event from a page subscription
	if (body.object == 'page') {

		// iterates over each entry - there may be multiple if batched
		body.entry.forEach(function(entry) {

			// gets the message. entry.messaging is an array, but
			// will only ever contain one message, so we get index 0
			let webhook_event = entry.messaging[0];
			console.log(webhook_event);
			console.log(webhook_event.message.text);
			let response = {
      "text": `My name is ben`
    }
			callSendAPI(webhook_event.sender.id, response); 
		});

		// returns a '200 OK' response to all requests
		res.status(200).send('EVENT_RECEIVED');
	} else {
		// Returns a '404 Not Found' if event is not from a page subscription
		res.sendStatus(404);
	}
});
// adds support for GET requests to our webhook
app.get('/webhook', (req, res) => {

	// your verify token. should be a random string.
	let VERIFY_TOKEN = "verify_token"

	// parse the query params
	let mode = req.query['hub.mode'];
	let token = req.query['hub.verify_token'];
	let challenge = req.query['hub.challenge'];

	// checks if a token and mode is in the query string of the request
	if (mode && token) {

		// checks the mode and token sent is correct
		if (mode == 'subscribe' && token == "verify_token") {

			// responds with the challenge token from the request
			console.log('WEBHOOK_VERIFIED');
			res.status(200).send(challenge);

		} else {
			// responds with '403 Forbidden' if verify tokens do not match 
			res.sendStatus(403);
		}
	}
});
function callSendAPI(sender_psid, response) {
  // Construct the message body
  let request_body = {
    "recipient": {
      "id": sender_psid
    },
    "message": response
  }

  // Send the HTTP request to the Messenger Platform
  request({
    "uri": "https://graph.facebook.com/v2.6/me/messages",
    "qs": { "access_token":'EAAPBvndkCP4BAAtf20C1O2hE9qZAespn4SZBWelemAQBCqpMFHZBgMeSv4ZBcnn6E2dZBtxl0vaxF3oPCsJtxcZCnJSZAvZAIKwP35ErZAqWZA9KpYGffeVRVTcw9v8lYDpZC1VQZCjoa1P37bCDr64z4mZCTN0IaZAIvLKpEUz7xIcGSXvHFZACk3ZCSc7T' },
    "method": "POST",
    "json": request_body
  }, (err, res, body) => {
    if (!err) {
      console.log('message sent!')
    } else {
      console.error("Unable to send message:" + err);
    }
  }); 
}

