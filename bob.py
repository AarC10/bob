#!/usr/bin/env python3
"""Bob - RIT Slack bot main entry point."""
import logging
from typing import Callable

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import config
import utils
from commands import register_commands
from message_handlers import register_message_handlers

# Initialize app
app = App(token=config.SLACK_TOKEN, signing_secret=config.SLACK_SIGNING_SECRET)
logger = logging.getLogger(__name__)

# Set app instance for utility functions
utils.set_app(app)


@app.middleware
def log_request(logger: logging.Logger, body: dict, next: Callable):
	"""Log all incoming requests."""
	logger.debug(body)
	return next()


def main():
	"""Start the bot."""
	# Register all handlers
	register_commands(app)
	register_message_handlers(app)
	
	# Start the bot
	logger.info("Starting bob")
	SocketModeHandler(app, config.SLACK_APP_LEVEL_TOKEN).start()


if __name__ == '__main__':
	main()
