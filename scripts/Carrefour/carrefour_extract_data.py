import re
import os
import sys
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.helpers import driver_intialize, convert_url_to_arabic
from openpyxl import Workbook, load_workbook
import csv
import re
from datetime import datetime, timedelta
base_directory = 'I:\\Web Crawler Project'  # For Windows Adels machine
input_csv_path = os.path.join(base_directory, 'extractions', 'Carrefour', 'extract_carrefour_urls_19_09_2024.csv')
output_directory = os.path.join(base_directory, 'extractions', 'Carrefour')
from models.Product import Product

def extract_brand_name(driver):
    try:
        brand_name = driver.find_element(By.CSS_SELECTOR, '.css-1nnke3o').text
        
        if not brand_name:
            return ""

        return brand_name

    except Exception as e:
        print(f"Error extracting brand name: {e}")
        return ""

def extract_offer_end_date(driver):
    try:
        # Find the second child element that contains the number of days
        element = driver.find_element(By.CSS_SELECTOR, '.css-juexlj > span:nth-child(2)')
        
        # Extract the number of days from the text (e.g., "2 days")
        days_text = element.text.strip()
        
        # Use regex to find the number in the text
        match = re.search(r'\d+', days_text)
        
        if match:
            # Convert the extracted number to an integer
            days_to_add = int(match.group(0))
            
            # Calculate the new date by adding the number of days to today's date
            calculated_date = datetime.now() + timedelta(days=days_to_add)
            
            # Return the calculated date in the format YYYY-MM-DD
            return calculated_date.strftime('%Y-%m-%d')
        
        return ""  # Return empty string if no match found

    except Exception as e:
        return ""


def extract_categories(driver):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, '.css-iamwo8')
        parent_categories = [element.text.strip() for element in elements if element.text.strip()]
        while len(parent_categories) < 7:
            parent_categories.append("")
        return parent_categories[:7]
    except Exception as e:
        print(f"Error extracting parent categories: {e}")
        return [""] * 7

def extract_product_barcode(driver):
    try:
         
        element = driver.find_element(By.CSS_SELECTOR, "#__next > div.css-qo9h12 > main > div > div.css-9p8u88 > div:nth-child(2) > script")
        barcode = element.get_attribute("data-flix-ean")
    
        return barcode if barcode else "product barcode not found"
    
    except Exception:
        return "product barcode not found"

def extract_product_id(url):
    driver.get(url)
    match = re.search(r'/p/(\d+)', url)
    
    return match.group(1) if match else "id not found"

def extract_product_name_in_arabic(driver, url):
    driver.get(url)
    
    try:
        product_name_ar = driver.find_element(By.CSS_SELECTOR, '.css-106scfp').text
        
        if not product_name_ar:
            return "لم يتم العثور على اسم المنتج"

        return product_name_ar
    

    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "لم يتم العثور على اسم المنتج"

def extract_image_url(driver):
    
    try:
        # Select the div with the specified class
        image_div = driver.find_element(By.CSS_SELECTOR, 'div.css-1c2pck7 img')
        
        # Get the src attribute of the img tag
        img_url = image_div.get_attribute('src')
        return img_url

    except Exception as e:
        print(f"Error extracting image URL: {e}")
        return "Image not found"  

def extract_product_name_in_english(driver):
    try:
        product_name_ar = driver.find_element(By.CSS_SELECTOR, '.css-106scfp').text
        
        if not product_name_ar:
            return "Product name not found"

        return product_name_ar

    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "Product name not found"

def extract_product_price_before_offer(driver):    
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
            return match.group(0) if match else "Price not found"

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

    return "Price not found"

def extract_product_price_after_offer(driver):
    try:
        price_element = driver.find_element(By.CSS_SELECTOR, '.css-1i90gmp')
        price_text = price_element.text
        match = re.search(r'\d+\.\d+', price_text)
        return match.group(0) if match else ""
    except Exception:
        return ""

# Function to write the product data into an Excel file
def write_to_excel(output_file_name, product):
    file_exists = os.path.isfile(output_file_name)
    if file_exists:
        workbook = load_workbook(output_file_name)
        sheet = workbook.active
    else:
        workbook = Workbook()
        sheet = workbook.active
        sheet.append([
            'Merchant', 'Id', 'Brand ar', 'Brand en', 'Barcode', 'Item Name AR', 
            'Item Name EN', 'Category 1 EN', 'Category 2 EN', 'Category 3 EN', 
            'Category 4 EN', 'Category 5 EN', 'Category 6 EN', 'Category 7 EN',
            'Category 1 AR', 'Category 2 AR', 'Category 3 AR', 
            'Category 4 AR', 'Category 5 AR', 'Category 6 AR', 'Category 7 AR',
            'Price before', 'Price after', 'Offer start date', 'Offer end date', 
            'Url', 'Picture', 'Type', 'Crawled on'
        ])

    sheet.append([
        product.merchant, product.product_id, product.brand_ar, product.brand_en, 
        product.barcode, product.name_ar, product.name_en, product.category_one_eng, 
        product.category_two_eng, product.category_three_eng, product.category_four_eng, 
        product.category_five_eng, product.category_six_eng, product.category_seven_eng, 
        product.category_one_ar, product.category_two_ar, product.category_three_ar, 
        product.category_four_ar, product.category_five_ar, product.category_six_ar, 
        product.category_seven_ar, product.price_before, product.price_after, 
        product.offer_start_date, product.offer_end_date, product.url, product.image_url, 
        product.source_type, product.crawled_on
    ])
    workbook.save(output_file_name)

# Function to process URLs and extract data from each URL and save to Excel
def process_urls_and_save_to_excel(csv_file, output_file, driver):
    # Get today's date formatted as 'DD_MM_YYYY'
    todays_date = datetime.now().strftime('%d_%m_%Y')
    # Construct the output Excel file name with today's date
    output_file_name = os.path.join(output_file, f"extract_carrefour_data_{todays_date}.xlsx")
    merchant = 'Carrefour'  # Define the merchant name
    source_type = 'Website'  # Define the source type
    
    try:
        # Open the CSV file containing URLs
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)  # Read the CSV as a dictionary
            for row in reader:
                url = row['URL']  # Extract URL from the current row
                # Convert the URL to Arabic format
                formatted_url_in_arabic = convert_url_to_arabic(url)
                driver.get(formatted_url_in_arabic)
                # Navigate to the Arabic URL
                # Extract product name in Arabic
                product_name_in_arabic = extract_product_name_in_arabic(driver, formatted_url_in_arabic)
                
                # Extract brand name in Arabic
                brand_name_in_arabic = extract_brand_name(driver)
                
                # Extract categories in Arabic
                categories_ar = extract_categories(driver)
                
                driver.get(url)  # Navigate to the English URL
                # Extract product name in English
                product_name_in_english = extract_product_name_in_english(driver)
                
                # Extract brand name in English
                brand_name_in_english = extract_brand_name(driver)
                
                # Extract product ID from the URL
                product_id = extract_product_id(url)
                
                # Extract categories in English
                categories_eng = extract_categories(driver)
                
                # Extract product barcode
                product_barcode = extract_product_barcode(driver)
                
                # Extract price before the offer
                price_before_offer = extract_product_price_before_offer(driver)
                
                # Extract price after the offer
                price_after_offer = extract_product_price_after_offer(driver)
                
                # Extract offer start date
                offer_start_date = datetime.now().strftime('%Y-%m-%d') if price_after_offer else ''
                
                # Extract offer end date
                offer_end_data = extract_offer_end_date(driver)
        
                # Extract image URL
                image_url = extract_image_url(driver)
                
                # Create a Product object with all extracted data
                product = Product(
                    merchant=merchant,
                    product_id=product_id,
                    brand_ar=brand_name_in_arabic,
                    brand_en=brand_name_in_english,
                    barcode=product_barcode,
                    name_ar=product_name_in_arabic,
                    name_en=product_name_in_english,
                    category_one_eng=categories_eng[0] if len(categories_eng) > 0 else '', 
                    category_two_eng=categories_eng[1] if len(categories_eng) > 1 else '', 
                    category_three_eng=categories_eng[2] if len(categories_eng) > 2 else '', 
                    category_four_eng=categories_eng[3] if len(categories_eng) > 3 else '', 
                    category_five_eng=categories_eng[4] if len(categories_eng) > 4 else '', 
                    category_six_eng=categories_eng[5] if len(categories_eng) > 5 else '', 
                    category_seven_eng=categories_eng[6] if len(categories_eng) > 6 else '',
                    category_one_ar=categories_ar[0] if len(categories_ar) > 0 else '', 
                    category_two_ar=categories_ar[1] if len(categories_ar) > 1 else '', 
                    category_three_ar=categories_ar[2] if len(categories_ar) > 2 else '', 
                    category_four_ar=categories_ar[3] if len(categories_ar) > 3 else '', 
                    category_five_ar=categories_ar[4] if len(categories_ar) > 4 else '', 
                    category_six_ar=categories_ar[5] if len(categories_ar) > 5 else '', 
                    category_seven_ar=categories_ar[6] if len(categories_ar) > 6 else '', 
                    price_before=price_before_offer,
                    price_after=price_after_offer,
                    offer_start_date=offer_start_date,
                    offer_end_date=offer_end_data,
                    url=url,
                    image_url=image_url,
                    source_type=source_type,
                    crawled_on=todays_date 
                )
                
                # Write the product data to the output Excel file
                write_to_excel(output_file_name, product)
    except Exception as e:
        # Print any errors encountered during processing
        print(f"Error processing URLs: {e}")


# Call the function with the appropriate CSV file path and output directory
driver = driver_intialize()
process_urls_and_save_to_excel(input_csv_path, output_directory, driver)

