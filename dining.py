"""RIT Dining visiting chefs functionality."""
import re
import json
import logging
import datetime
import concurrent.futures

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import CHEF_PAGES

logger = logging.getLogger(__name__)


def fetch_html(url: str) -> str:
	"""Fetch HTML content from a URL with retry logic."""
	session = requests.Session()
	retries = Retry(
		total=3,
		backoff_factor=1.5,
		status_forcelist=[429, 500, 502, 503, 504],
		allowed_methods=["GET"],
	)
	session.mount("https://", HTTPAdapter(max_retries=retries))

	headers = {"User-Agent": "BobSlackBot/1.0 (RIT Dining Visiting Chefs)"}
	resp = session.get(url, headers=headers, timeout=30)
	resp.raise_for_status()
	return resp.text


def _extract_chef_json(html: str) -> dict | None:
	"""Pull the embedded chefData JSON blob out of the location page."""
	match = re.search(r"var\s+chefData\s*=\s*JSON\.parse\(`(?P<data>.*?)`\);", html, re.DOTALL)
	if not match:
		return None

	raw_json = match.group("data")
	try:
		return json.loads(raw_json)
	except json.JSONDecodeError as exc:
		logger.error(f"[chefs] failed to parse chefData JSON: {exc}")
		return None


def _collect_visiting_chefs(chef_data: dict, date_str: str) -> list[str]:
	"""Collect visiting chef entries for a specific date."""
	chefs: list[str] = []
	for events in chef_data.values():
		for event in events:
			if event.get("date") != date_str:
				continue
			for menu in event.get("menus") or []:
				if (menu.get("category") or "").lower() != "visiting chef":
					continue
				name = menu.get("name") or "Unknown chef"
				note = menu.get("name_note")
				parts = [name]
				if note:
					parts.append(note)
				chefs.append(" — ".join(parts))
	return chefs


def get_todays_visiting_chefs_from_locations() -> dict[str, list[str]]:
	"""Scrape visiting chefs from each location page via the embedded chefData blob (parallel)."""
	results: dict[str, list[str]] = {}
	today = datetime.date.today().isoformat()

	def fetch_and_parse(loc_name_url):
		loc_name, url = loc_name_url
		try:
			logger.info(f"[chefs] fetching {loc_name}: {url}")
			html = fetch_html(url)
			chef_data = _extract_chef_json(html)
			if not chef_data:
				logger.warning(f"[chefs] no chefData found for {loc_name}")
				return (loc_name, [])
			chefs = _collect_visiting_chefs(chef_data, today)
			return (loc_name, chefs)
		except Exception as exc:
			logger.error(f"[chefs] failed {loc_name}: {exc}")
			return (loc_name, [f"[ERROR: {exc}]"])

	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [executor.submit(fetch_and_parse, item) for item in CHEF_PAGES.items()]
		for future in concurrent.futures.as_completed(futures):
			loc_name, chefs = future.result()
			results[loc_name] = chefs

	return results


def format_chefs_message(chefs_by_loc: dict[str, list[str]]) -> str:
	"""Format visiting chefs data into a Slack message."""
	lines = []
	for loc, chefs in chefs_by_loc.items():
		lines.append(f"*{loc}*")
		if chefs:
			for c in chefs:
				lines.append(f"• {c}")
		else:
			lines.append("• (No visiting chefs listed)")
		lines.append("")
	return "\n".join(lines).strip()
