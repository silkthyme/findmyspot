'use strict';

// imports dependencies and set up http server
const
	express = require('express'),
	bodyParser = require('body-parser'),
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


