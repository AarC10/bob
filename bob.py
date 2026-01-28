#!/usr/bin/env python3
import os
import re
import random
import logging
import time
import datetime
import traceback

import create_wiki_page

from selenium import webdriver
from dotenv import load_dotenv
from typing import Callable
from selenium.common.exceptions import WebDriverException
from slack_sdk import WebClient
from slack_bolt import App, Say, BoltContext
from slack_bolt.adapter.socket_mode import SocketModeHandler

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


load_dotenv()
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_LEVEL_TOKEN = os.environ["SLACK_APP_LEVEL_TOKEN"]

app = App(token=SLACK_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
logger = logging.getLogger(__name__)

def check_user_in_payload(payload):
	return payload['user_name'] == os.environ["DEV_USER"] or payload['user_name'] == os.environ["MOD_USER"]


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
	logger.debug(body)
	return next()

@app.message(":wave:")
def say_hello(message, say):
	user = message['user']
	say(f"Hi there, <@{user}>!")

@app.message(re.compile("[Tt][Hh][Aa][Nn][Kk][Ss] [Bb][Oo][Bb]"))
def thank_bob(say, payload):
	name = random.choice(["thumbs", "ablobbouncefast", "raised_hands", "robot_face", "-w", "amongusplushspin", "cool_beans", "peepo-thumbs", "ablobblewobble", "ablobsmooch"])
	app.client.reactions_add(channel = payload['channel'], name = name, timestamp = payload['ts'])

# Respond with meow to Jim in any case
@app.message("[Jj][Ii][Mm]")
def jim(say, payload):
	print(payload)
	if (payload['channel'] == "C04SVDRGCV9"):
		say(channel = payload['channel'], text="meow")


@app.command("/generate-meeting-notes")
def generate_wiki_page(ack, say, payload, respond, command):
	ack()

	link = create_wiki_page.create_wiki_page(payload['text'])

	say(channel = payload['channel_id'], text = f"Avionics is starting soon! Here are your meeting notes: {link}")

@app.command("/echo")
def echo(ack, say, payload, respond, command):
	ack()
	# respond(f"{command['text']}")

	if payload['user_name'] == os.environ["DEV_USER"]:
		say(channel = payload['channel_id'], text = f"{command['text']}", link_names = True)

	else:
		respond(channel = payload['channel_id'], text = f"{command['text']}")

@app.command("/nuke")
def nuke(ack, say, payload, respond, command):
	ack()

	if payload['user_name'] == os.environ["DEV_USER"]:
		for i in range(100):
			# Check for tags
			if "<@" in command['text']:
				# Get the user ID
				user_id = command['text'].split("<@")[1].split(">")[0]
				# Get the user's name
				user_name = app.client.users_info(user = user_id)['user']['name']
				# Replace the tag with the user's name
				command['text'] = command['text'].replace(f"<@{user_id}>", f"@{user_name}")

			say(channel = payload['channel_id'], text = f"{command['text']}", link_names = True)
	else:
		print(payload['user_name'] + " attempted to nuke the channel by saying " + payload['text'])
		respond(channel = payload['channel_id'], text = f":clown: no")

@app.command("/airstrike")
def airstrike(ack, say, payload, respond, command):
	ack()
	logger.info(payload)
	if payload['user_name'] == os.environ["DEV_USER"] or payload['user_name'] == os.environ["MOD_USER"]:
		if "everyone" in command['text']:
			return # TODO: Grab everyone in the channel

		names = command['text'].split(" ")
		for i in range(5):
			for name in names:
				say(channel=payload['channel_id'], text=f"@" + name, link_names=True)
			time.sleep(1)

	else:
		say(channel=payload['channel_id'], text="L Bozo @" + payload['user_name'], link_names=True)


@app.command("/rawr")
def rawr(ack, payload, respond, command):
	ack()
	logger.info(payload)
	if check_user_in_payload(payload):
		if "@" in command['text']:
			user_id = command['text'].split()[0]
			app.client.chat_postMessage(channel = user_id, text = command['text'].replace(user_id, ""))
		else:
			respond("Please tag a user to rawr at")

@app.command("/nukerawr")
def nuke_rawr(ack, payload, respond, command):
	ack()
	logger.info(payload)
	if check_user_in_payload(payload):
		if "@" in command['text']:
			user_id = command['text'].split()[0]
			for i in range(100):
				app.client.chat_postMessage(channel = user_id, text = command['text'].replace(user_id, ""))
		else:
			respond("Please tag a user to nuke rawr at")

@app.command("/execute")
def execute(ack, say, payload, respond, command):
	ack()
	if "```" in command['text'] and payload['user_name'] == os.environ["DEV_USER"]:
		try:
			exec(command['text'].replace("```", ""))

		except NameError:
			respond(traceback.format_exc())
			respond("Error executing:\n" + command['text'])
	else:
		respond("Remember to use ``` to surround your code")

@app.event("message")
def handle_message_events(body, logger):
	logger.info(body)

	if body.get("event").get("type") == "message":
		print(body)
		# print("[" + "] " body.get	 + ":" + body.get("event").get("text"))
		# print(body.get("event").get("text"))

	# TODO: Handle DMs

def extract_subtype(body: dict, context: BoltContext, next: Callable):
	context["subtype"] = body.get("event", {}).get("subtype", None)
	next()

def react_to_message(message_link, reaction):
	message_id = message_link.split("/")[-1]
	channel_id = message_link.split("/")[-2]
	message_id = message_id[:-6] + "." + message_id[-6:]
	app.client.reactions_add(channel = channel_id, name = reaction, timestamp = message_id)

# TODO: Scheduled messages testing
# Post on Thursdays at 6:30pm
# app.client.chat_scheduleMessage(channel = "", post_at = "", text = "")


def cleanup_emotes(message_link: str) -> None:
	message_id = message_link.split("/")[-1]
	channel_id = message_link.split("/")[-2]
	ts = message_id[:-6] + "." + message_id[-6:]

	me = app.client.auth_test()["user_id"]

	removed = []
	failed = []  # (emoji, error)

	try:
		resp = app.client.reactions_get(channel=channel_id, timestamp=ts)
		reactions = resp.get("message", {}).get("reactions", [])
	except Exception as e:
		print(f"Failed to fetch reactions: {e}")
		return

	for r in reactions:
		emoji = r.get("name")
		users = r.get("users", [])
		if not emoji or me not in users:
			continue

		try:
			app.client.reactions_remove(channel=channel_id, timestamp=ts, name=emoji)
			removed.append(emoji)
			# sleep 
		except Exception as e:
			failed.append((emoji, str(e)))

	print(f"Removed ({len(removed)}): {removed}")
	if failed:
		print(f"Failed ({len(failed)}):")
		for emoji, err in failed:
			print(f"  - {emoji}: {err}")


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



MENUS_URL = "https://www.rit.edu/dining/menus"

LOCATION_MAP = {
	"RITZ Sports Zone": "RITZ Sports Zone",
	"Cafe & Market at Crossroads": "Cafe & Market at Crossroads",
	"Brick City Cafe": "Brick City Cafe",
}

MENUS_URL = "https://www.rit.edu/dining/menus"

LOCATION_NAMES = [
	"RITZ Sports Zone",
	"Cafe & Market at Crossroads",
	"Brick City Cafe",
]

CHEF_PAGES = {
	"RITZ Sports Zone": "https://www.rit.edu/dining/location/ritz",
	"The Cafe & Market at Crossroads": "https://www.rit.edu/dining/location/cafe-and-market-crossroads",
	"Kitchen at Brick City": "https://www.rit.edu/dining/location/kitchen-brick-city",
}

def fetch_html(url: str) -> str:
	session = requests.Session()
	retries = Retry(
		total=3,
		backoff_factor=1.5,
		status_forcelist=[429, 500, 502, 503, 504],
		allowed_methods=["GET"],
	)
	session.mount("https://", HTTPAdapter(max_retries=retries))

	headers = {"User-Agent": "BobSlackBot/1.0 (RIT Dining Visiting Chefs)"}
	resp = session.get(url, headers=headers, timeout=30)  # increase timeout here
	resp.raise_for_status()
	return resp.text

def get_todays_visiting_chefs_from_locations() -> dict[str, list[str]]:
	results: dict[str, list[str]] = {}
	for loc_name, url in CHEF_PAGES.items():
		try:
			html = fetch_html(url)
			soup = BeautifulSoup(html, "html.parser")

			chef_divs = soup.select("div.chef-name")
			chefs = [d.get_text(" ", strip=True) for d in chef_divs if d.get_text(strip=True)]

			if chefs:
				results[loc_name] = chefs

		except Exception as e:
			results[loc_name] = [f"[ERROR fetching/parsing: {e}]"]

	return results

def format_chefs_message(chefs_by_loc: dict[str, list[str]]) -> str:
	lines = []
	for loc, chefs in chefs_by_loc.items():
		lines.append(f"{loc}")
		for c in chefs:
			lines.append(c)
		lines.append("")
	return "\n".join(lines).strip()

@app.command("/rit")
def rit_router(ack, payload, respond, command):
	ack()
	args = (command.get("text") or "").strip().split()

	if not args:
		respond("Usage: /rit chef")
		return

	if args[0].lower() != "chef":
		respond("Unknown subcommand. Usage: /rit chef")
		return

	try:
		data = get_todays_visiting_chefs_from_locations()
		respond(format_chefs_message(data))
	except Exception as e:
		respond(f"Failed to fetch visiting chefs: {e}")
		return

	if not chefs:
		respond("No visiting chefs found for today.")
		return

if __name__ == '__main__':
	SocketModeHandler(app, SLACK_APP_LEVEL_TOKEN).start()

	# Create a timestamp for tomorrow at 9AM
	tomorrow = datetime.date.today() + datetime.timedelta(days=1)
	scheduled_time = datetime.time(hour=9, minute=30)
	schedule_timestamp = datetime.datetime.combine(tomorrow, scheduled_time).strftime('%s')

	try:
		# Call the chat.scheduleMessage method using the WebClient
		result = app.client.chat_scheduleMessage(
			channel=channel_id,
			text="Looking towards the future",
			post_at=schedule_timestamp
		)
		# Log the result
		logger.info(result)

	except SlackApiError as e:
		logger.error("Error scheduling message: {}".format(e))
