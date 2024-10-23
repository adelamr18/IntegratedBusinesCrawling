from asyncio import sleep
import requests
import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from scripts.models.Product import Product
from utils.helpers import write_to_excel
from openpyxl import load_workbook, Workbook
import json

# Paths and directories
base_directory = '/Users/ajlapandzic/Desktop/Projects/IntegratedBusinesCrawling'
output_directory = os.path.join(base_directory, 'extractions', 'Seoudi')
progress_log = os.path.join(output_directory, 'progress_log.json')
error_log = os.path.join(output_directory, 'error_log.txt')

# Retry mechanism
MAX_RETRIES = 5

processed_barcodes = set()

# Track progress in a file (so the script can restart from last known state)
def load_progress():
    if os.path.exists(progress_log):
        with open(progress_log, 'r') as file:
            return json.load(file)
    return {"last_category": None, "last_slug": None}

def save_progress(category, slug):
    with open(progress_log, 'w') as file:
        json.dump({"last_category": category, "last_slug": slug}, file)

def log_error(message):
    with open(error_log, 'a') as file:
        file.write(f"{datetime.now()}: {message}\n")

def retry_request(func, *args, retries=MAX_RETRIES, **kwargs):
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error(f"Error: {e}. Retrying {attempt}/{retries}...")
            sleep(2 ** attempt)  # Exponential backoff
    log_error(f"Failed after {retries} attempts.")
    return None

def extract_products_per_category(output_file, todays_date):
    # Define all categories
    categories = [
        'Mjg5NA==',  # Seoudi products, Fruits and Vegetables
        'NTIy',      # Meat and Poultry
        'MjU=',      # Dairy, Eggs and Cheese
        'NTMx',      # Cold Cuts & Deli
        'NDcz',      # Chilled Food
        'Mzcy',      # Fish & Seafood
        'ODI=',      # Snacks & Sweets
        'OTc=',      # Food Cupboard
        'MTI0',      # Beverages
        'NTQw',      # Hot drinks
        'MTQ1',      # Frozen Food
        'MzU2MQ==',  # Healthy and Nutrition
        'MjYy',      # Baby Care
        'MTY2',      # Cleaning And Household
        'MTk5',      # Beauty And Personal Care
        'MjM1',      # Home, Kitchen And Garden
        'MzAx',      # Pet Supplies
        'MzEz',      # Toys And Activities
        'Mjgz',      # Electronics And Appliances
        'NTcyNQ==',  # Back To School Supplies
        'MzkwMw==',  # Buy In Bulk
        'MzIxNw=='   # Top Offers
    ]

    # Define the URL for the GraphQL endpoint
    url = "https://mcprod.seoudisupermarket.com/graphql"

    # Define the headers
    headers = {
        "Content-Type": "application/json"
    }

    # Load progress and retry mechanism additions
    progress = load_progress()
    last_slug = progress["last_slug"]  # Keep track of the last slug processed

    for category in categories:
        # Define the payload (query and variables)
        payload = {
            "query": """
            query Products($page: Int, $pageSize: Int, $search: String, $filter: ProductAttributeFilterInput = {}, $sort: ProductAttributeSortInput = {}) {
                connection: products(currentPage: $page, pageSize: $pageSize, filter: $filter, search: $search, sort: $sort) {
                    total_count
                    aggregations {
                        ...ProductAggregation
                    }
                    page_info {
                        ...PageInfo
                    }
                    nodes: items {
                        ...ProductCard
                    }
                }
            }
            fragment ProductAggregation on Aggregation {
                attribute_code
                label
                count
                options {
                    label
                    count
                    value
                }
            }
            fragment PageInfo on SearchResultPageInfo {
                total_pages
                current_page
                page_size
            }
            fragment ProductCard on ProductInterface {
                __typename
                id
                name
                sku
                special_from_date
                special_price
                special_to_date
                new_from_date
                new_to_date
                only_x_left_in_stock
                url_key
                weight_increment_step
                weight_base_unit
                brand {
                    name
                    url_key
                }
                categories {
                    url_path
                    name
                    level
                    max_allowed_qty
                }
                thumbnail {
                    url
                    label
                }
                price_range {
                    maximum_price {
                        final_price {
                            value
                        }
                        regular_price {
                            value
                        }
                    }
                }
                stockQtyTerm {
                    max_sale_qty
                    min_sale_qty
                }
            }
            """,
            "variables": {
                "page": 1,
                "pageSize": 20000,
                "sort": {
                    "position": "ASC"
                },
                "filter": {
                    "category_uid": {
                        "eq": category  # Use the current category
                    }
                }
            }
        }

        # Send the POST request and retry if necessary
        response = retry_request(requests.post, url, headers=headers, json=payload)

        if response and response.status_code == 200:
            products = response.json().get('data', {}).get('connection', {}).get('nodes', [])

            for product in products:
                url_key = product.get('url_key')

                # Check if we should start processing products
                if last_slug and url_key == last_slug:
                    last_slug = None  # Clear the slug to continue processing new products
                
                if last_slug is None:  # Only process products if we haven't reached the last_slug
                    if url_key:
                        # Call the details endpoint with the url_key as slug
                        fetch_product_details(url_key, output_file, todays_date)
                        # Save progress after processing each product
                        save_progress(category, url_key)

        else:
            log_error(f"Error for category {category}: {response.status_code} {response.text if response else 'No response'}")
            continue  # Move to the next category

def get_product_details_per_language(slug, lang):
    # Define the URL for the GraphQL endpoint with the store as a query param
    details_url = f"https://mcprod.seoudisupermarket.com/graphql?store={lang}"

    # Define the headers for the details request
    headers = {
        "Content-Type": "application/json",
        "Store": f"{lang}"
    }

    # Define the payload for fetching product details using url_key as slug
    details_payload = {
        "query": """
        query Product($slug: String!) {
            product: product(url_key: $slug) {
                __typename
                id
                name
                sku
                special_from_date
                special_price
                special_to_date
                new_from_date
                new_to_date
                only_x_left_in_stock
                url_key
                weight_increment_step
                weight_base_unit
                brand {
                    name
                    url_key
                }
                categories {
                    url_path
                    name
                    level
                    max_allowed_qty
                }
                thumbnail {
                    url
                    label
                }
                price_range {
                    maximum_price {
                        final_price {
                            value
                        }
                        regular_price {
                            value
                        }
                    }
                }
                stockQtyTerm {
                    max_sale_qty
                    min_sale_qty
                }
            }
        }
        """,
        "variables": {
            "slug": slug
        }
    }

    # Send the POST request for product details
    return requests.post(details_url, headers=headers, json=details_payload)

def fetch_product_details(slug, output_file, todays_date):
    output_file_name = os.path.join(output_file, f"seoudi_extract_data_{todays_date}.xlsx")
    
    # Fetch product details in English
    product_details_in_english = get_product_details_per_language(slug, "default")

    # Process the English response if the request is successful
    if product_details_in_english and product_details_in_english.status_code == 200:
        product_details_eng = product_details_in_english.json().get('data', {}).get('product', {})
        merchant_name = "Seoudi"
        source_type = "Website"
        categories_eng = product_details_eng.get('categories', [])
        product_id = product_details_eng.get('id')
        brand_details_eng = product_details_eng.get('brand', {}) if product_details_eng is not None else {}
        brand_name_in_english = brand_details_eng.get("name") if brand_details_eng is not None else None

        # Extract all required English fields
        product_barcode = product_details_eng.get('sku')
        product_name_in_english = product_details_eng.get('name')
        offer_start_date = product_details_eng.get('special_from_date', None)
        offer_end_date = product_details_eng.get('special_to_date', None)

        # Get price_before_offer
        price_before_offer = product_details_eng.get('price_range', {}).get('maximum_price', {}).get('regular_price', {}).get('value', None)

        # Check price_after_offer
        price_after_offer = product_details_eng.get('price_range', {}).get('maximum_price', {}).get('final_price', {}).get('value', None)
        if price_after_offer == price_before_offer:
            price_after_offer = None
            offer_start_date = None
            offer_end_date = None

        product_image_url = product_details_eng.get('thumbnail', {}).get('url', None)
        product_url = f"https://seoudisupermarket.com/en/{product_details_eng.get('url_key')}"

        # Fetch product categories in English
        category_one_eng = categories_eng[0].get('name') if len(categories_eng) > 0 else None
        category_two_eng = categories_eng[1].get('name') if len(categories_eng) > 1 else None
        category_three_eng = categories_eng[2].get('name') if len(categories_eng) > 2 else None
        category_four_eng = categories_eng[3].get('name') if len(categories_eng) > 3 else None
        category_five_eng = categories_eng[4].get('name') if len(categories_eng) > 4 else None
        category_six_eng = categories_eng[5].get('name') if len(categories_eng) > 5 else None
        category_seven_eng = categories_eng[6].get('name') if len(categories_eng) > 6 else None
        category_eight_eng = categories_eng[7].get('name') if len(categories_eng) > 7 else None
        category_nine_eng = categories_eng[8].get('name') if len(categories_eng) > 8 else None
        
        # Fetch product details in Arabic
        product_details_in_arabic = get_product_details_per_language(slug, "ar_EG")
        
        # Initialize Arabic fields to None
        product_name_in_arabic = None
        brand_name_in_arabic = None
        categories_ar = []

        if product_details_in_arabic and product_details_in_arabic.status_code == 200:
            product_details_ar = product_details_in_arabic.json().get('data', {}).get('product', {})
            
            # Only access Arabic product details if the response is not None
            if product_details_ar:
                product_name_in_arabic = product_details_ar.get('name', None)
                categories_ar = product_details_ar.get('categories', [])
                brand_details_ar = product_details_ar.get('brand', {})
                brand_name_in_arabic = brand_details_ar.get('name', None) if brand_details_ar else None
        
        # Fetch product categories in Arabic
        category_one_ar = categories_ar[0].get('name') if len(categories_ar) > 0 else None
        category_two_ar = categories_ar[1].get('name') if len(categories_ar) > 1 else None
        category_three_ar = categories_ar[2].get('name') if len(categories_ar) > 2 else None
        category_four_ar = categories_ar[3].get('name') if len(categories_ar) > 3 else None
        category_five_ar = categories_ar[4].get('name') if len(categories_ar) > 4 else None
        category_six_ar = categories_ar[5].get('name') if len(categories_ar) > 5 else None
        category_seven_ar = categories_ar[6].get('name') if len(categories_ar) > 6 else None
        category_eight_ar = categories_ar[7].get('name') if len(categories_ar) > 7 else None
        category_nine_ar = categories_ar[8].get('name') if len(categories_ar) > 8 else None
        
    if product_barcode not in processed_barcodes:
        # Add barcode to the processed set
        processed_barcodes.add(product_barcode)
        
        # Create a product instance with both English and Arabic data
        product = Product(
            merchant=merchant_name,
            product_id=product_id,
            brand_en=brand_name_in_english,
            brand_ar=brand_name_in_arabic,
            name_ar=product_name_in_arabic, 
            barcode=product_barcode,
            name_en=product_name_in_english,
            source_type=source_type,
            price_before=price_before_offer,
            price_after=price_after_offer,
            image_url=product_image_url,
            url=product_url,
            offer_start_date=offer_start_date,
            offer_end_date=offer_end_date,
            category_one_eng=category_one_eng,
            category_two_eng=category_two_eng,
            category_three_eng=category_three_eng,
            category_four_eng=category_four_eng,
            category_five_eng=category_five_eng,
            category_six_eng=category_six_eng,
            category_seven_eng=category_seven_eng,
            category_eight_eng=category_eight_eng,
            category_nine_eng=category_nine_eng,
            category_one_ar=category_one_ar,
            category_two_ar=category_two_ar,
            category_three_ar=category_three_ar,
            category_four_ar=category_four_ar,
            category_five_ar=category_five_ar,
            category_six_ar=category_six_ar,
            category_seven_ar=category_seven_ar,
            category_eight_ar=category_eight_ar,
            category_nine_ar=category_nine_ar,
            crawled_on=todays_date
        )

        # Write the product details to an Excel file
        write_to_excel(output_file_name, product)

    else:
        log_error(f"Error fetching details for slug {slug}: {product_details_in_english.status_code if product_details_in_english else 'No response'}")

def extract_all_seoudi_product_data(output_file, todays_date):
    extract_products_per_category(output_file, todays_date)

def run_seoudi_crawler():
    output_file = os.path.join(output_directory)
    todays_date = datetime.today().strftime('%Y-%m-%d')

    while True:  # Infinite loop to automatically restart the script
        try:
            extract_all_seoudi_product_data(output_file, todays_date)
            print("Data extraction completed successfully.")
            break  # Exit the loop if successful
        except Exception as e:
            log_error(f"Unexpected error: {e}")
            print(f"Error encountered: {e}. Restarting script in 10 seconds...")
            time.sleep(10)  # Add a delay before restarting the script

run_seoudi_crawler()
