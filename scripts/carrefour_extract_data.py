import re
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from utils.helpers import driver_intialize

def extract_product_price():
    driver = driver_intialize()
    driver.get('https://www.carrefouregypt.com/mafegy/en/white-eggs/mychoice-white-eggs-30p/p/305478')  # Example URL

    try:
        price_element = driver.find_element(By.CSS_SELECTOR, '.css-17ctnp')
    except:
        price_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'EGP')]")

    # Extract the text, e.g., 'EGP 190.00(Inc. VAT)'
    price_text = price_element.text

    # Use regex to extract the numeric part (including decimals)
    match = re.search(r'\d+\.\d+', price_text)  # Matches numbers with decimals like 190.00

    if match:
        price_number = match.group(0).split('.')[0]  # Extract only the integer part
        print(price_number)  # Output should be: 190
    else:
        print("Price not found!")

    driver.quit()

# Run the function
extract_product_price()
