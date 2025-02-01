import sys
import os
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Include the helper function from your project setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.helpers import driver_initialize

# Define the base directory
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Define the output path for the JSON file
output_directory = os.path.join(base_directory, 'extractions', 'Oscar')
os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist
output_json_path = os.path.join(output_directory, 'category_urls.json')

def run_oscar_category_urls_crawler(driver):
    # Initialize actions
    actions = ActionChains(driver)

    # Open the webpage
    driver.get('https://www.oscarstores.com/')
    sleep(5)

    # Wait for the shop button to be clickable and click it
    shop_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="dropdownMenuLink"]/span'))
    )
    actions.click(shop_button).perform()
    sleep(5)

    # Locate the megamenu element and extract the top-level list items
    megamenu = driver.find_element(By.XPATH, '//*[@id="myTab"]')
    li_elements = megamenu.find_elements(By.XPATH, './li')

    # Collect all `see_all my-3` elements in a list
    see_all_elements = driver.find_elements(By.CLASS_NAME, 'see_all')

    # Initialize a list to store category names and URLs
    categories = []

    # Loop through each top-level `li` element to extract category name and URL
    for index, li in enumerate(li_elements):
        try:
            # Extract the button and the span containing the category text
            button = li.find_element(By.TAG_NAME, 'button')
            span = button.find_element(By.CLASS_NAME, 'text-capitalize')
            category_name = span.text.strip()  # Get the text and strip any extra spaces

            # Print the HTML of corresponding see_all element (for debugging purposes)
            if index < len(see_all_elements):  # Check if the index is within the range
                see_all_element = see_all_elements[index]

                # Now that we know the structure, we can access the URL from the <a> tag inside the see_all div
                a_tag = see_all_element.find_element(By.TAG_NAME, 'a')
                url = a_tag.get_attribute('href')  # Get the URL from the href attribute

                # Append the category and URL to the categories list
                categories.append({"category": category_name, "url": url})
            else:
                print(f"No corresponding URL for category: {category_name}")
        except Exception as e:
            print(f"Error extracting information for li element {index}:", e)

    # Save the results to a JSON file
    with open(output_json_path, 'w', encoding='utf-8') as file:
        json.dump({"categories": categories}, file, indent=4, ensure_ascii=False)

    # Optionally, close the driver after finishing the task
    driver.quit()

# Initialize the WebDriver using your custom helper function
driver = driver_initialize()
run_oscar_category_urls_crawler(driver)
