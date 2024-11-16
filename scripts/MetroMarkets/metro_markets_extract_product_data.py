import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
import json
import time
from utils.extraction_helpers import extract_product_name_in_arabic_using_xpath

# Base directory and paths
base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_csv_path = os.path.join(base_directory, 'extractions', 'MetroMarkets', 'extracted_urls_2024-11-10.csv')
output_directory = os.path.join(base_directory, 'extractions', 'MetroMarkets')
os.makedirs(output_directory, exist_ok=True)

# Models and helpers
from models.Product import Product
from utils.helpers import write_product_to_excel, read_urls_from_csv, update_is_processed_in_csv

def extract_product_price_before_offer(soup):
    # Find the element with class 'price'
    price_element = soup.find(class_='price')
    
    if price_element:
        # Find the <p> element with class 'before' inside the 'price' element
        before_element = price_element.find('p', class_='before')
        if before_element:
            # Return the text content of the 'before' element
            return before_element.text.replace("LE", "").strip()
        
    return None    
        
def extract_product_price_after_offer(soup):
    # Find the element with class 'price'
    price_element = soup.find(class_='price')
    
    if price_element:
        # Find the <p> element with class 'after' inside the 'price' element
        before_element = price_element.find('p', class_='after')
        if before_element:
            # Return the text content of the 'after' element
            return before_element.text.replace("LE", "").strip()        

    # Return None if the element is not found
    return None

def extract_categories(soup):
    try:
        # Select the parent element using a CSS selector
        parent_element = soup.select_one('.breadcrumb')

        if not parent_element:
            raise Exception("Parent element not found")

        # Extract all 'li' children from the parent element
        li_elements = parent_element.find_all('li')

        # Check if 'li_elements' has the expected number of elements
        if len(li_elements) < 2:
            print("Not enough 'li' elements found in breadcrumb")
            return [""] * 7

        # Skip the first 'li' and get the text from each 'a' tag or 'h5' inside the remaining 'li' elements
        parent_categories = []
        for li in li_elements[1:]:
            # Check for 'a' tag and get the text if it exists
            a_tag = li.find('a')
            if a_tag and a_tag.text.strip():
                parent_categories.append(a_tag.text.strip())
            else:          
                 parent_categories.append("")  # Add an empty string if no text is found

        # Ensure there are exactly 7 categories by adding empty strings if necessary
        while len(parent_categories) < 7:
            parent_categories.append("")  # Pad with empty strings

        return parent_categories[:7]  # Return the first 7 categories
    except Exception as e:
        print(f"Error extracting parent categories: {e}")
        return [""] * 7  # Return a list of empty strings if an error occurs

def convert_url_to_arabic(url):
    # Split the URL and insert '/ar' before '/product'
    if '/product/' in url:
        return url.replace('/product/', '/ar/product/')
    else:
        return url  # Return the original URL if the pattern is not found

def process_url(url, output_file_name, crawled_date):
    try:
        is_successful = True

        # Convert URL to Arabic version
        url_in_arabic = convert_url_to_arabic(url)
        
        # Fetch and parse the Arabic page
        ar_response = requests.get(url_in_arabic)
        soup_ar = BeautifulSoup(ar_response.text, 'html.parser')
        product_name_in_arabic_xpath = '/html/body/div[3]/div[1]/main/div/div/div/div[2]/div/header/div/h5'
        
        product_name_in_arabic = extract_product_name_in_arabic_using_xpath(soup_ar, product_name_in_arabic_xpath)
            
        categories_ar = extract_categories(soup_ar)

        merchant = 'MetroMarkets'
        source_type = 'Website'

        # Fetch and parse the English page
        eng_response = requests.get(url)
        soup_eng = BeautifulSoup(eng_response.text, 'html.parser')

        # Locate the JSON script tag
        script_tag_en = soup_eng.find('script', type='application/ld+json')
        
        if script_tag_en:
            # Parse the JSON data
            product_data_eng = json.loads(script_tag_en.string)
            product_name_in_english = product_data_eng.get('name', 'Product name not found')
            brand_name_in_english = product_data_eng.get('brand', 'Brand name not found')
            product_id = product_data_eng.get('productID', 'Product ID not found')
            image_url = product_data_eng.get('image', 'Image URL not found')
        
        price_before_offer = extract_product_price_before_offer(soup_eng)
        price_after_offer = extract_product_price_after_offer(soup_eng)
        offer_start_date = datetime.now().strftime('%Y-%m-%d') if price_before_offer else ''
        categories_eng = extract_categories(soup_eng)

        if not price_before_offer:
            price_before_offer = price_after_offer
            price_after_offer = None
        
        
        product = Product(
            merchant=merchant,
            product_id=product_id,
            brand_ar= '',
            brand_en=brand_name_in_english,
            barcode='',
            name_ar=product_name_in_arabic,
            name_en=product_name_in_english,
            category_one_eng=categories_eng[1] if len(categories_eng) > 0 else '',
            category_two_eng=categories_eng[2] if len(categories_eng) > 1 else '',
            category_three_eng=categories_eng[3] if len(categories_eng) > 2 else '',
            category_four_eng=categories_eng[4] if len(categories_eng) > 3 else '',
            category_five_eng=categories_eng[5] if len(categories_eng) > 4 else '',
            category_six_eng=categories_eng[6] if len(categories_eng) > 5 else '',
            category_seven_eng='',
            category_eight_eng='',
            category_nine_eng= '',
            category_one_ar=categories_ar[1] if len(categories_ar) > 0 else '',
            category_two_ar=categories_ar[2] if len(categories_ar) > 1 else '',
            category_three_ar=categories_ar[3] if len(categories_ar) > 2 else '',
            category_four_ar=categories_ar[4] if len(categories_ar) > 3 else '',
            category_five_ar=categories_ar[5] if len(categories_ar) > 4 else '',
            category_six_ar=categories_ar[6] if len(categories_ar) > 5 else '',
            category_seven_ar='',
            category_eight_ar= '',
            category_nine_ar= '',
            price_before=price_before_offer,
            price_after=price_after_offer,
            offer_start_date=offer_start_date,
            offer_end_date='',
            url=url,
            image_url=image_url,
            source_type=source_type,
            crawled_on=crawled_date,
            brand_image_url = ''
        )
        
        write_product_to_excel(output_file_name, product)

        # Mark URL as processed
        update_is_processed_in_csv(url, is_successful, input_csv_path)

    except Exception as e:
        print(f"Error processing {url}: {e}")
        is_successful = False
        
        # Mark URL as unprocessed if an error occurs
        update_is_processed_in_csv(url, is_successful, input_csv_path)

    return is_successful

# Main function to run the crawler
def run_metro_markets_product_details_crawler():
    crawled_date = datetime.now().strftime('%Y-%m-%d')
    output_file_name = os.path.join(output_directory, f'extracted_products_{crawled_date}.xlsx')

    # Load URLs from CSV
    urls_to_process = read_urls_from_csv(input_csv_path)

    # Retry unprocessed URLs
    for url in urls_to_process:
        success = process_url(url, output_file_name, crawled_date)
        if not success:
            print(f"Retrying URL: {url}")
            time.sleep(5)  # Wait before retrying
            process_url(url, output_file_name, crawled_date)

run_metro_markets_product_details_crawler()