from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import os
from openpyxl import Workbook, load_workbook
from openpyxl import Workbook, load_workbook
from webdriver_manager.firefox import GeckoDriverManager

import os
# Initialize the Firefox driver
def driver_initialize():
    firefox_options = Options()
    firefox_options.headless = True  # Run in headless mode (no browser UI)
    firefox_options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox'
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver


def convert_url_to_arabic(url):
    return url.replace('/en/', '/ar/')

def write_to_excel(output_file_name, product):
    file_exists = os.path.isfile(output_file_name)
    
    if file_exists:
        workbook = load_workbook(output_file_name)
        sheet = workbook.active
    else:
        workbook = Workbook()
        sheet = workbook.active
        # Add headers if creating a new file
        sheet.append([
            'Merchant', 'Id', 'Brand ar', 'Brand en', 'Barcode', 'Item Name AR', 
            'Item Name EN', 'Category 1 EN', 'Category 2 EN', 'Category 3 EN', 
            'Category 4 EN', 'Category 5 EN', 'Category 6 EN', 'Category 7 EN',
            'Category 8 EN', 'Category 9 EN',  # Additional categories
            'Category 1 AR', 'Category 2 AR', 'Category 3 AR', 
            'Category 4 AR', 'Category 5 AR', 'Category 6 AR', 'Category 7 AR',
            'Category 8 AR', 'Category 9 AR',  # Additional categories
            'Price before', 'Price after', 'Offer start date', 'Offer end date', 
            'Url', 'Brand Url' ,'Picture', 'Type', 'Crawled on'
        ])

    # Append the product data to the sheet
    sheet.append([
        product.merchant, product.product_id, product.brand_ar, product.brand_en, 
        product.barcode, product.name_ar, product.name_en, product.category_one_eng, 
        product.category_two_eng, product.category_three_eng, product.category_four_eng, 
        product.category_five_eng, product.category_six_eng, product.category_seven_eng, 
        product.category_eight_eng, product.category_nine_eng,
        product.category_one_ar, product.category_two_ar, product.category_three_ar, 
        product.category_four_ar, product.category_five_ar, product.category_six_ar, 
        product.category_seven_ar, product.category_eight_ar, product.category_nine_ar,
        product.price_before, product.price_after, 
        product.offer_start_date, product.offer_end_date, 
        product.url, product.brand_image_url ,product.image_url, 
        product.source_type, product.crawled_on
    ])
    
    workbook.save(output_file_name)
         