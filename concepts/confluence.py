import requests
import json
import os
import sys

TOKEN = os.getenv(os.environ['CONFLUENCE_TOKEN'])

def	create_page(title, content, space, parent):
	url = "https://confluence.atlassian.com/rest/api/content"
	headers = {
		'Authorization': 'Basic {}'.format(TOKEN),
		'Content-Type': 'application/json',
	}

	data = {
		'title': title,
		'ancestors': [{'id': parent}],
		'body': {
			'storage': {
				'value': content,
				'type': 'storage'
			}
		},
		'labels': [],
		'_links': {
			'self': {
				'href': 'https://confluence.atlassian.com/rest/api/content/{}'.format(parent)
			}
		},
		'_expandable': {
			'ancestors': 'ancestors',
			'body': 'body.storage',
			'labels': 'labels',
			'self': 'self',
			'container': 'container'
		},
		'_type': 'page',
		},
