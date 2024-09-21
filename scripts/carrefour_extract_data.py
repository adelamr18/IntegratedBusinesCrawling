import re
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from utils.helpers import driver_intialize
from openpyxl import Workbook, load_workbook
import csv

def extract_product_price_after_offer(url):
    driver = driver_intialize()
    driver.get(url)
    
    price_text = ""
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, '.css-1i90gmp')
        price_text = price_element.text
        
        # Extract the numeric part
        match = re.search(r'\d+\.\d+', price_text)
        return match.group(0) if match else "Price not found"

    except Exception:
        try:
            price_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'EGP')]")
            price_text = price_element.text
            
            # Extract the numeric part
            match = re.search(r'\d+\.\d+', price_text)
            return match.group(0) if match else "Price not found"
            
        except Exception:
            return "Price not found"

    finally:
        driver.quit()

    return ""
    

def extract_product_price_before_offer(url):
    driver = driver_intialize()
    driver.get(url)
    
    price_text = ""

    try:
        # Try to find the price element with the offer
        price_element_with_offer = driver.find_element(By.CSS_SELECTOR, '.css-1jh6byp')
        price_text = price_element_with_offer.text
        
        if price_text:
            print('Offer price found:', price_text)
            price_element_with_offer_text = driver.find_element(By.CSS_SELECTOR, 'del.css-1bdwabt').text
            
            if 'Use code' in price_element_with_offer_text:
                raise Exception("Promotional code found, exiting...")    
            
            print('Price before offer:', price_element_with_offer_text)
            
            # Extract only the numeric part from the price before the offer
            match = re.search(r'\d+\.\d+', price_element_with_offer_text)
            print(match.group(0))
            return match.group(0) if match else ""

    except Exception as e:
        print("Offer price element not found or promotional code detected, trying to get regular price...")
        try:
            price_element = driver.find_element(By.CSS_SELECTOR, '.css-17ctnp')
            price_text = price_element.text
            
            # Extract the numeric part
            match = re.search(r'\d+\.\d+', price_text)
            return match.group(0) if match else "Price not found"

        except Exception:
            try:
                price_element = driver.find_element(By.XPATH, "//h2[contains(text(), 'EGP')]")
                price_text = price_element.text
                
                # Extract the numeric part
                match = re.search(r'\d+\.\d+', price_text)
                return match.group(0) if match else "Price not found"
                
            except Exception:
                return "Price not found"

    finally:
        driver.quit()

    return ""

def write_to_excel(output_file_name, id_counter, category, price_before_offer, price_after_offer, url):
    # Check if the file exists
    file_exists = os.path.isfile(output_file_name)
    
    if file_exists:
        workbook = load_workbook(output_file_name)
        sheet = workbook.active
    else:
        workbook = Workbook()
        sheet = workbook.active
        
        # Write the header if the file doesn't exist
        sheet.append([
            'Merchant', 'id', 'brand ar', 'brand en', 'barcode', 'Item Name AR', 
            'Item Name EN', 'Category', 'Parent Category', 'price before', 
            'price after', 'offer start date', 'offer end date', 'url', 
            'picture', 'crawled on'
        ])

    # Writing data into Excel
    sheet.append([
        'Carrefour',             # Merchant
        id_counter,              # id (incremental)
        '',                      # brand ar (empty for now)
        '',                      # brand en (empty for now)
        '',                      # barcode
        '',                      # Item Name AR
        '',                      # Item Name EN
        '',                      # Category
        '',                      # Parent Category
        price_before_offer,      # Price before offer
        price_after_offer,       # price after offer
        '',                      # offer start date
        '',                      # offer end date
        url,                     # URL of the product
        '',                      # picture (empty for now)
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # crawled on timestamp
    ])

    # Save the workbook after each append
    workbook.save(output_file_name)

def process_urls_and_save_to_excel(csv_file, output_file):
    
    id_counter = 1
    todays_date = datetime.now().strftime('%d_%m_%Y')
    output_file_name = os.path.join(output_file, f"extract_carrefour_data_{todays_date}.xlsx")

    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category = row['Main Category']
                url = row['URL']
                
                # Extract the price for each URL before offer
                price_before_offer = extract_product_price_before_offer(url)
                
                # Extract the price for each url after offer if exists
                price_after_offer = extract_product_price_after_offer(url)
                
                # Write to Excel directly for each URL
                write_to_excel(output_file_name, id_counter, category, price_before_offer, price_after_offer, url)
                
                id_counter += 1

        print(f"Data successfully saved to {output_file_name}")

    except Exception as e:
        print(f"An error occurred during processing: {e}")

# Call the function with the appropriate CSV file path and output directory
input_csv_path = '/Users/gebrila/Desktop/SelfStudy/CarrefourAutomation/extractions/extract_carrefour_urls_19_09_2024.csv'
output_directory = '/Users/gebrila/Desktop/SelfStudy/CarrefourAutomation/extractions/'
process_urls_and_save_to_excel(input_csv_path, output_directory)

