import socket
import pickle
from pathlib import Path

import slack
import os

from dotenv import load_dotenv

import bob

UDP_IP = "127.0.0.1"
UDP_PORT = int(input("Enter port number: "))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

try:
	while True:
		data, addr = sock.recvfrom(1024)
		location = pickle.loads(data)

		client.chat_postMessage(channel=f"#slackbot-dev", text="Packet Received: ")

		for key in location:
			message = f"\t{key}: {location[key]}"

			try:
				client.chat_postMessage(channel=f"#slackbot-dev", text=message)

			except slack.errors.SlackApiError as e:
				print("Could not send. " + str(e))

		client.chat_postMessage(channel=f"#slackbot-dev", text="\n")

		print()

except KeyboardInterrupt:
	print("\nExiting...")

	sock.close()
