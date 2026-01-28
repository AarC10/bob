"""Utility functions for Bob Slack bot."""
import os
import threading
import time


def check_user_in_payload(payload):
	"""Check if user has DEV or MOD permissions."""
	dev_user = os.environ.get("DEV_USER", "")
	mod_user = os.environ.get("MOD_USER", "")
	return payload['user_name'] == dev_user or payload['user_name'] == mod_user


def parse_message_link(message_link: str) -> tuple[str, str]:
	"""Parse a Slack message link into (channel_id, timestamp)."""
	message_id = message_link.split("/")[-1]
	channel_id = message_link.split("/")[-2]
	ts = message_id[:-6] + "." + message_id[-6:]
	return channel_id, ts


def react_to_message(app_client, message_link: str, reaction: str):
	"""Add a reaction to a message."""
	channel_id, ts = parse_message_link(message_link)
	app_client.reactions_add(channel=channel_id, name=reaction, timestamp=ts)


def cleanup_emotes(app_client, message_link: str) -> None:
	"""Remove all reactions from a message that were added by this bot."""
	channel_id, ts = parse_message_link(message_link)
	me = app_client.auth_test()["user_id"]

	removed = []
	failed = []  # (emoji, error)

	try:
		resp = app_client.reactions_get(channel=channel_id, timestamp=ts)
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
			app_client.reactions_remove(channel=channel_id, timestamp=ts, name=emoji)
			removed.append(emoji)
		except Exception as e:
			failed.append((emoji, str(e)))

	print(f"Removed ({len(removed)}): {removed}")
	if failed:
		print(f"Failed ({len(failed)}):")
		for emoji, err in failed:
			print(f"  - {emoji}: {err}")


# Global flags for reaction spam control
_reaction_thread_stop = threading.Event()
_reaction_thread = None


def react_spam(app_client, message_link: str, delay: float = 1.0):
	"""React to a message with all available custom emojis, one per second."""
	global _reaction_thread, _reaction_thread_stop
	
	channel_id, ts = parse_message_link(message_link)
	
	emoji_list = app_client.emoji_list()
	emojis = list(emoji_list.get("emoji", {}).keys())
	
	standard = ["thumbsup", "thumbsdown", "heart", "eyes", "fire", "100", "rocket", "tada"]
	all_emojis = standard + emojis
	
	print(f"Starting to add {len(all_emojis)} reactions to message...")
	_reaction_thread_stop.clear()
	
	def _react_loop():
		for emoji in all_emojis:
			if _reaction_thread_stop.is_set():
				print("Stopped by user request")
				break
			try:
				app_client.reactions_add(channel=channel_id, timestamp=ts, name=emoji)
				print(f"Added: {emoji}")
				time.sleep(delay)
			except Exception as e:
				print(f"Failed {emoji}: {e}")
				continue
		print("Done!")
	
	_reaction_thread = threading.Thread(target=_react_loop, daemon=True)
	_reaction_thread.start()


def stop_react_spam():
	"""Stop the currently running react_spam operation."""
	global _reaction_thread_stop
	_reaction_thread_stop.set()
	print("Stopping reaction spam...")
