"""Configuration and constants for Bob Slack bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Slack credentials
SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_LEVEL_TOKEN = os.environ["SLACK_APP_LEVEL_TOKEN"]

# User permissions
DEV_USER = os.environ.get("DEV_USER", "")
MOD_USER = os.environ.get("MOD_USER", "")

# Dining URLs and locations
MENUS_URL = "https://www.rit.edu/dining/menus"

LOCATION_MAP = {
	"RITZ Sports Zone": "RITZ Sports Zone",
	"Cafe & Market at Crossroads": "Cafe & Market at Crossroads",
	"Brick City Cafe": "Brick City Cafe",
}

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
