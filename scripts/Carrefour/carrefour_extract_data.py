import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import os
import re
import csv
from datetime import datetime, timedelta
from openpyxl import Workbook, load_workbook
from concurrent.futures import ThreadPoolExecutor
base_directory = 'I:\\Web Crawler Project'
input_csv_path = os.path.join(base_directory, 'extractions', 'Carrefour', 'extract_carrefour_urls_19_09_2024.csv')
output_directory = os.path.join(base_directory, 'extractions', 'Carrefour')
from models.Product import Product
from utils.helpers import convert_url_to_arabic

# Extract brand name using BeautifulSoup
def extract_brand_name(soup):
    try:
        brand_name_element = soup.select_one('.css-1nnke3o')
        return brand_name_element.text.strip() if brand_name_element else ""
    except Exception as e:
        print(f"Error extracting brand name: {e}")
        return ""

# Extract offer end date using BeautifulSoup
def extract_offer_end_date(soup):
    try:
        element = soup.select_one('.css-juexlj > span:nth-child(2)')
        days_text = element.text.strip()
        match = re.search(r'\d+', days_text)
        if match:
            days_to_add = int(match.group(0))
            calculated_date = datetime.now() + timedelta(days=days_to_add)
            return calculated_date.strftime('%Y-%m-%d')
        return ""
    except Exception as e:
        return ""

# Extract categories using BeautifulSoup
def extract_categories(soup):
    try:
        elements = soup.select('.css-iamwo8')
        parent_categories = [element.text.strip() for element in elements if element.text.strip()]
        parent_categories = parent_categories[1:]
        while len(parent_categories) < 7:
            parent_categories.append("")
        return parent_categories[:7]
    except Exception as e:
        print(f"Error extracting parent categories: {e}")
        return [""] * 7

import json

def extract_product_barcode(soup):
    try:
        # Locate the specific script tag with id "__NEXT_DATA__"
        element = soup.select_one("#__NEXT_DATA__")

        if not element:
            return "Product barcode not found: script tag missing"
        
        # Get the content of the script tag
        script_content = element.string.strip()

        # Parse the content as JSON
        try:
            json_data = json.loads(script_content)

            # Navigate to the barcode in the JSON structure
            barcodes = json_data['props']['initialProps']['pageProps']['initialData']['products'][0]['attributes']['barCodes']

            if barcodes and isinstance(barcodes, list):
                print(barcodes[0])
                return barcodes[0]  # Return the first barcode
            else:
                return "No barcodes found"
        except (json.JSONDecodeError, KeyError) as e:
            return f"Error parsing JSON data: {e}"
    
    except Exception as e:
        print(f"Error extracting product barcode: {e}")
        return "Product barcode not found"

# Extract product name in Arabic using BeautifulSoup
def extract_product_name_in_arabic(soup):
    try:
        product_name_ar = soup.select_one('.css-106scfp').text
        return product_name_ar if product_name_ar else "لم يتم العثور على اسم المنتج"
    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "لم يتم العثور على اسم المنتج"

# Extract image URL using BeautifulSoup
def extract_image_url(soup):
    try:
        image_div = soup.select_one('div.css-1c2pck7 img')
        return image_div['src'] if image_div else "Image not found"
    except Exception as e:
        print(f"Error extracting image URL: {e}")
        return "Image not found"

# Extract product name in English using BeautifulSoup
def extract_product_name_in_english(soup):
    try:
        product_name_en = soup.select_one('.css-106scfp').text
        return product_name_en if product_name_en else "Product name not found"
    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "Product name not found"

# Extract product price before offer using BeautifulSoup
def extract_product_price_before_offer(soup, price_after_offer):
    try:
        if price_after_offer:
            price_element_with_offer_text = soup.select_one('del.css-1bdwabt').text
            if 'Use code' in price_element_with_offer_text:
                raise Exception("Promotional code found, exiting...")
            match = re.search(r'\d+\.\d+', price_element_with_offer_text)
            return match.group(0) if match else ""
        raise Exception("Price after offer not found")
    except Exception as e:
        try:
            price_element = soup.select_one('.css-17ctnp')
            match = re.search(r'\d+\.\d+', price_element.text) if price_element else None
            return match.group(0) if match else "Price not found"
        except Exception as e:
            return "Price not found"

# Extract product price after offer using BeautifulSoup
def extract_product_price_after_offer(soup):
    try:
        price_element = soup.select_one('.css-1i90gmp')
        match = re.search(r'\d+\.\d+', price_element.text) if price_element else None
        return match.group(0) if match else ""
    except Exception:
        return ""

# Write product data to Excel file
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

# Process each URL and extract product information
def process_url(url, output_file_name, faulty_urls, crawled_date):
    try:
        is_successful = True
        url_in_arabic = convert_url_to_arabic(url)
        ar_response = requests.get(url_in_arabic)
        soup_ar = BeautifulSoup(ar_response.text, 'html.parser')

        merchant = 'Carrefour'
        source_type = 'Website'

        product_name_in_arabic = extract_product_name_in_arabic(soup_ar)
        brand_name_in_arabic = extract_brand_name(soup_ar)
        categories_ar = extract_categories(soup_ar)
        
        eng_response = requests.get(url)
        soup = BeautifulSoup(eng_response.text, 'html.parser')
        
        product_name_in_english = extract_product_name_in_english(soup)
        brand_name_in_english = extract_brand_name(soup)
        product_id = re.search(r'/p/(\d+)', url).group(1) if re.search(r'/p/(\d+)', url) else "id not found"
        categories_eng = extract_categories(soup)
        product_barcode = extract_product_barcode(soup)
        price_after_offer = extract_product_price_after_offer(soup)
        price_before_offer = extract_product_price_before_offer(soup, price_after_offer)
        offer_start_date = datetime.now().strftime('%Y-%m-%d') if price_after_offer else ''
        offer_end_date = extract_offer_end_date(soup)
        image_url = extract_image_url(soup)

        product = Product(
            merchant=merchant,
            product_id=product_id,
            brand_ar=brand_name_in_arabic,
            brand_en=brand_name_in_english,
            barcode=product_barcode,
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
            offer_end_date=offer_end_date,
            url=url,
            image_url=image_url,
            source_type=source_type,
            crawled_on=crawled_date
        )

        write_to_excel(output_file_name, product)

        # Update is_processed in the CSV file
        update_is_processed_in_csv(url, True)

    except Exception as e:
        print(f"Error processing URL {url}: {e}")
        is_successful = False
        update_is_processed_in_csv(url, is_successful)
        faulty_urls.append(url)

def read_urls_from_csv(csv_file_path):
    urls = []
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Skip the header
            next(reader)
            for row in reader:
                if len(row) < 3 or row[2] == '':  # Check if is_processed column is empty
                    urls.append(row[1])  # Append only the URL
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return urls

def update_is_processed_in_csv(url, is_successful):
    rows = []
    url_found = False  # Flag to check if the URL exists
    try:
        with open(input_csv_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)

            # Add is_processed header if not exists
            if len(header) < 3 or header[2] != 'is_processed':
                header.append('is_processed')
            rows.append(header)

            for row in reader:
                if row[1] == url:
                    url_found = True
                    # If URL is found, update the is_processed status
                    if len(row) < 3:
                        row.append('True' if is_successful else 'False')
                    else:
                        row[2] = 'True' if is_successful else 'False'
                rows.append(row)

            # If the URL was not found, append a new row with the corresponding status
            if not url_found:
                rows.append([None, url, 'True' if is_successful else 'False'])  # Assuming None for the first column

        # Write updated rows back to CSV
        with open(input_csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    except Exception as e:
        print(f"Error updating CSV file: {e}")

        # If an error happens, we still want to mark the URL as not processed
        rows.append([None, url, 'False'])  # Assuming None for the first column
        # Write rows back to CSV, ensuring the header is included
        try:
            with open(input_csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        except Exception as write_error:
            print(f"Error writing to CSV file: {write_error}")


    except Exception as e:
        print(f"Error updating CSV file: {e}")
        # If an error happens, we still want to mark the URL as not processed
        rows.append([None, url, 'False'])  # Assuming None for the first column
        # Write rows back to CSV, ensuring the header is included
        try:
            with open(input_csv_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        except Exception as write_error:
            print(f"Error writing to CSV file: {write_error}")

def process_urls_and_save_to_excel(input_csv_path, output_directory):
    output_file_name = os.path.join(output_directory, 'carrefour_products_four.xlsx')
    faulty_urls_file = os.path.join(output_directory, 'faulty_urls.txt')
    
    while True:  # Loop indefinitely
        crawled_date = datetime.now().strftime('%d_%m_%Y')
        urls = read_urls_from_csv(input_csv_path)

        # List to store faulty URLs
        faulty_urls = []

        # Process each URL sequentially
        for url in urls:
            print(url)
            process_url(url, output_file_name, faulty_urls, crawled_date)

        # Save faulty URLs to a file if any
        if faulty_urls:
            with open(faulty_urls_file, 'w') as f:
                for url in faulty_urls:
                    f.write(f"{url}\n")
            print(f"Faulty URLs saved to {faulty_urls_file}")

        print("Waiting for new URLs or reprocessing...")
          # Wait for 60 seconds before rechecking the CSV

process_urls_and_save_to_excel(input_csv_path, output_directory)
