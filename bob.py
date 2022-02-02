import os
import re
import logging
import time
import create_wiki_page

from selenium import webdriver
from dotenv import load_dotenv
from typing import Callable
from selenium.common.exceptions import WebDriverException
from slack_sdk import WebClient
from slack_bolt import App, Say, BoltContext
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_LEVEL_TOKEN = os.environ["SLACK_APP_LEVEL_TOKEN"]

app = App(token=SLACK_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
logger = logging.getLogger(__name__)


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
	logger.debug(body)
	return next()

@app.message(":wave:")
def say_hello(message, say):
	user = message['user']
	say(f"Hi there, <@{user}>!")

@app.command("/generate-meeting-notes")
def generate_wiki_page(ack, say, payload, respond, command):
	ack()

	link = create_wiki_page.create_wiki_page(payload['text'])

	say(channel = payload['channel_id'], text = f"Meeting Notes Generated: {link}")

@app.command("/echo")
def echo(ack, say, payload, respond, command):
	ack()
	# respond(f"{command['text']}")

	if payload['user_name'] == os.environ["DEV_USER"]:
		say(channel = payload['channel_id'], text = f"{command['text']}")

	# TODO: Handle DMs

def extract_subtype(body: dict, context: BoltContext, next: Callable):
	context["subtype"] = body.get("event", {}).get("subtype", None)
	next()

# TODO: Scheduled messages testing

# TODO: Responses/Reactions to certain messages

# @app.event({"type": "message", "subtype": None})
# def reply_in_thread(body: dict, say: Say):
# 	event = body["event"]
# 	thread_ts = event.get("thread_ts", None) or event["ts"]
# 	say(text="Hey, what's up?", thread_ts=thread_ts)


# @app.event(
# 	event={"type": "message", "subtype": "message_deleted"},
# 	matchers=[
# 		# Skip the deletion of messages by this listener
# 		lambda body: "You've deleted a message: "
# 					 not in body["event"]["previous_message"]["text"]
# 	],
# )
# def detect_deletion(say: Say, body: dict):
# 	text = body["event"]["previous_message"]["text"]
# 	say(f"You've deleted a message: {text}")
#
#
# @app.event(
# 	event={"type": "message", "subtype": re.compile("(me_message)|(file_share)")},
# 	middleware=[extract_subtype],
# )
# def add_reaction(
#
# 		body: dict, client: WebClient, context: BoltContext, logger: logging.Logger
# ):
# 	subtype = context["subtype"]  # by extract_subtype
# 	logger.info(f"subtype: {subtype}")
# 	message_ts = body["event"]["ts"]
# 	api_response = client.reactions_add(
# 		channel=context.channel_id,
# 		timestamp=message_ts,
# 		name="eyes",
# 	)
# 	logger.info(f"api_response: {api_response}")


# # This listener handles all uncaught message events
# # (The position in source code matters)
# @app.event({"type": "message"}, middleware=[extract_subtype])
# def just_ack(logger, context):
# 	subtype = context["subtype"]  # by extract_subtype
# 	logger.info(f"{subtype} is ignored")

if __name__ == '__main__':
	SocketModeHandler(app, SLACK_APP_LEVEL_TOKEN).start()
