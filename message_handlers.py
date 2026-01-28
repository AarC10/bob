"""Message event handlers for Bob Slack bot."""
import re
import random
import logging
from typing import Callable

from slack_bolt import BoltContext

logger = logging.getLogger(__name__)


def register_message_handlers(app):
	"""Register all message event handlers."""
	
	@app.message(":wave:")
	def say_hello(message, say):
		user = message['user']
		say(f"Hi there, <@{user}>!")

	@app.message(re.compile("[Tt][Hh][Aa][Nn][Kk][Ss] [Bb][Oo][Bb]"))
	def thank_bob(say, payload):
		name = random.choice([
			"thumbs", "ablobbouncefast", "raised_hands", "robot_face", 
			"-w", "amongusplushspin", "cool_beans", "peepo-thumbs", 
			"ablobblewobble", "ablobsmooch"
		])
		app.client.reactions_add(channel=payload['channel'], name=name, timestamp=payload['ts'])

	@app.message("[Jj][Ii][Mm]")
	def jim(say, payload):
		print(payload)
		if payload['channel'] == "C04SVDRGCV9":
			say(channel=payload['channel'], text="meow")

	@app.event("message")
	def handle_message_events(body, logger):
		logger.info(body)
		if body.get("event").get("type") == "message":
			print(body)


def extract_subtype(body: dict, context: BoltContext, next: Callable):
	"""Middleware to extract message subtype."""
	context["subtype"] = body.get("event", {}).get("subtype", None)
	next()
