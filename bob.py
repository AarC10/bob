"""
Bob the Scientist Kerbonaut
Now working with RIT Launch Initiative
Objectives: Be better than Jeb

@author Aaron Chan the Ghost of Avionics Future
"""

import os

from slack_bolt import App
from pathlib import Path
from dotenv import load_dotenv

if __name__ == '__main__':
	load_dotenv()
	app = App(
		token=os.environ.get("SLACK_BOT_TOKEN"),
		signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
	)

	app.start(port=int(os.environ.get("PORT", 3000)))

