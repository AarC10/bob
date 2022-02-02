import time, os
from selenium import webdriver


def create_wiki_page(team):
	"""
	Testing wiki creation and sending meeting notes to Slack
	"""
	print(team)

	if team == "avionics":
		link = "https://wiki.rit.edu/?createDialogSpaceKey=ritlaunch&createDialogBlueprintId=90c78ef1-be37-4b9f-9fbe-1b724b21f235"

	else:
		return "invalid"

	driver = webdriver.Chrome()
	action_chains = webdriver.ActionChains(driver)

	# Open Avionics meeting notes
	driver.get("https://wiki.rit.edu/display/ritlaunch/Meeting+Notes+-+Avionics")
	time.sleep(1)

	# Check if logged in
	if driver.find_element("xpath", "/html/body/div[2]/div/header/nav/div/div[2]/ul/li[6]/a"):
		driver.get("https://wiki.rit.edu/login.action?os_destination=%2Fdisplay%2Fritlaunch%2FMeeting%2BNotes%2B-%2BAvionics")
		time.sleep(1)
		driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[2]/div/form/fieldset/div[1]/input").send_keys(os.environ["CONFLUENCE_USER"])
		driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[2]/div/form/fieldset/div[2]/input").send_keys(os.environ["CONFLUENCE_PASSWORD"])

		driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[2]/div/form/fieldset/div[4]/input").click()

		time.sleep(1)


	# Link to create new page
	driver.get(link)
	time.sleep(1)

	# Publishes page
	driver.find_element("xpath", "/html/body/div[2]/div/div[2]/div[3]/form/div[9]/div/div/div[2]/div[6]/button").click()
	time.sleep(1)

	# Post page on Slack
	# say(f"Wiki page created: {driver.current_url}")
	wiki_page = driver.current_url


	driver.close()

	return wiki_page
