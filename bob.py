"""
Bob the Scientist Kerbonaut
Now working with RIT Launch Initiative
Objectives: Be better than Jeb

@author Aaron Chan the Ghost of Avionics Future
"""

import slack
import os
from pathlib import Path
from dotenv import load_dotenv



def post_message(channel, message):
	try:
		client.chat_postMessage(channel = f"#{channel}", text = str(message))

	except slack.errors.SlackApiError as e:
		print("Could not send. Check channel entry.")

def main():
	while True:
		stdin = input()

		if stdin != '':
			channel, message = stdin.split('>')
			post_message(channel, message)

if __name__ == '__main__':
	env_path = Path('.') / '.env'
	load_dotenv(dotenv_path=env_path)

	client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
	main()