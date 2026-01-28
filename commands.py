"""Slash command handlers for Bob Slack bot."""
import os
import time
import traceback
import logging

import create_wiki_page
from utils import *
from dining import get_todays_visiting_chefs_from_locations, format_chefs_message

logger = logging.getLogger(__name__)


def register_commands(app):
	"""Register all slash command handlers."""
	
	@app.command("/generate-meeting-notes")
	def generate_wiki_page_cmd(ack, say, payload, respond, command):
		ack()
		link = create_wiki_page.create_wiki_page(payload['text'])
		say(channel=payload['channel_id'], text=f"Avionics is starting soon! Here are your meeting notes: {link}")

	@app.command("/echo")
	def echo(ack, say, payload, respond, command):
		ack()
		if payload['user_name'] == os.environ.get("DEV_USER", ""):
			say(channel=payload['channel_id'], text=f"{command['text']}", link_names=True)
		else:
			respond(channel=payload['channel_id'], text=f"{command['text']}")

	@app.command("/nuke")
	def nuke(ack, say, payload, respond, command):
		ack()
		if payload['user_name'] == os.environ.get("DEV_USER", ""):
			for i in range(100):
				if "<@" in command['text']:
					user_id = command['text'].split("<@")[1].split(">")[0]
					user_name = app.client.users_info(user=user_id)['user']['name']
					command['text'] = command['text'].replace(f"<@{user_id}>", f"@{user_name}")
				say(channel=payload['channel_id'], text=f"{command['text']}", link_names=True)
		else:
			print(payload['user_name'] + " attempted to nuke the channel by saying " + payload['text'])
			respond(channel=payload['channel_id'], text=f":clown: no")

	@app.command("/airstrike")
	def airstrike(ack, say, payload, respond, command):
		ack()
		logger.info(payload)
		if check_user_in_payload(payload):
			if "everyone" in command['text']:
				return  # TODO: Grab everyone in the channel
			
			names = command['text'].split(" ")
			for i in range(5):
				for name in names:
					say(channel=payload['channel_id'], text=f"@{name}", link_names=True)
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
				app.client.chat_postMessage(channel=user_id, text=command['text'].replace(user_id, ""))
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
					app.client.chat_postMessage(channel=user_id, text=command['text'].replace(user_id, ""))
			else:
				respond("Please tag a user to nuke rawr at")

	@app.command("/execute")
	def execute(ack, say, payload, respond, command):
		ack()
		if "```" in command['text'] and payload['user_name'] == os.environ.get("DEV_USER", ""):
			try:
				exec(command['text'].replace("```", ""))
			except NameError:
				respond(traceback.format_exc())
				respond("Error executing:\n" + command['text'])
		else:
			respond("Remember to use ``` to surround your code")

	@app.command("/rit")
	def rit_router(ack, payload, respond, command):
		ack()
		args = (command.get("text") or "").strip().split()

		if not args:
			respond("Usage: /rit chefs")
			return

		if args[0].lower() not in ["chef", "chefs"]:
			respond("Unknown subcommand. Usage: /rit chef")
			return

		data = get_todays_visiting_chefs_from_locations()
		respond(format_chefs_message(data))
