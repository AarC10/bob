import os
import re
import logging
import time

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

@app.message("Test wiki create")
def create_wiki_page(say):
	"""
	Testing wiki creation and sending meeting notes to Slack
	"""
	driver = webdriver.Chrome()
	action_chains = webdriver.ActionChains(driver)

	# Open Avionics meeting notes
	driver.get("https://wiki.rit.edu/display/ritlaunch/Meeting+Notes+-+Avionics")
	time.sleep(1)

	# Check if logged in
	if driver.find_element("xpath", "/html/body/div[2]/div/header/nav/div/div[2]/ul/li[6]/a"):
		driver.get("https://wiki.rit.edu/login.action?os_destination=%2Fdisplay%2Fritlaunch%2FMeeting%2BNotes%2B-%2BAvionics")
		time.sleep(1)
		driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[2]/div/form/fieldset/div[1]/input").send_keys(os.environ["CONFLUENCE_USER"])
		driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[2]/div/form/fieldset/div[2]/input").send_keys(os.environ["CONFLUENCE_PASSWORD"])

		driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[2]/div/form/fieldset/div[4]/input").click()

		time.sleep(1)


	# Link to create new page
	driver.get("https://wiki.rit.edu/?createDialogSpaceKey=ritlaunch&createDialogBlueprintId=90c78ef1-be37-4b9f-9fbe-1b724b21f235&title=Meeting+Notes+-+Avionics+-+2022-02-01")
	time.sleep(1)

	# Publishes page
	driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[3]/form/div[9]/div/div/div[2]/div[6]/button").click()
	time.sleep(1)

	# Post page on Slack
	say(f"Wiki page created: {driver.current_url}")

	driver.close()

def extract_subtype(body: dict, context: BoltContext, next: Callable):
	context["subtype"] = body.get("event", {}).get("subtype", None)
	next()

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
