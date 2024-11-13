import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.helpers import driver_initialize
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from time import sleep

# Define the base directory
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the output path for the JSON file
output_directory = os.path.join(base_directory, 'extractions', 'MetroMarkets')
os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist
output_json_path = os.path.join(output_directory, 'category_urls.json')

def run_metro_markets_category_urls_crawler(driver):
    # Initialize actions
    actions = ActionChains(driver)

    # Open the webpage
    driver.get('https://www.metro-markets.com/')
    sleep(5)

    # Wait for the shop button to be clickable and click it
    shop_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="navbarSupportedContent"]/ul/li[1]/a')))
    actions.click(shop_button).perform()
    sleep(5)

    # Find the megamenu element and extract the list items
    megamenu = driver.find_element(By.XPATH, '//*[@id="webShop"]/ul')
    items = megamenu.find_elements(By.TAG_NAME, 'li')
    # Create a list to store category names and URLs
    categories = []

    # Loop through each 'li' and extract the category name and URL
    for item in items:
        try:
            link = item.find_element(By.TAG_NAME, 'a')
            category_name = link.text.strip()  # Get the category name
            category_url = link.get_attribute('href')  # Get the URL
            if category_name and category_url:
             categories.append({"name": category_name, "url": category_url})  # Append to the categories list
            print(f"Category: {category_name}, URL: {category_url}")
        except Exception as e:
            print("Error accessing link in li element:", e)

    # Write the categories to a JSON file
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump({"categories": categories}, json_file, indent=4, ensure_ascii=False)

    # Optionally, close the driver after finishing the task
    driver.quit()

# Run the crawler function
driver = driver_initialize()
run_metro_markets_category_urls_crawler(driver)
