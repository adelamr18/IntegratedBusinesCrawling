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

processed_barcodes = set()

# Paths and directories
#base_directory_mac_os = '/Users/ajlapandzic/Desktop/Projects/IntegratedBusinesCrawling'
base_directory_windows = r'C:\Users\DiscoCrawler1\Desktop\IntegratedBusinesCrawling'
output_directory = os.path.join(base_directory_windows, 'extractions', 'Spinneys')
progress_log = os.path.join(output_directory, 'progress_log.json')
error_log = os.path.join(output_directory, 'error_log.txt')

# Retry mechanism
MAX_RETRIES = 5

# Track progress in a file (so the script can restart from last known state)
def load_progress():
    if os.path.exists(progress_log):
        with open(progress_log, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {"last_category": None, "last_slug": None}

def save_progress(category, slug):
    with open(progress_log, 'w', encoding='utf-8') as file:
        json.dump({"last_category": category, "last_slug": slug}, file)
        
def save_last_slug(category, slug):
    with open(progress_log, 'w', encoding='utf-8') as file:
        json.dump({"last_category": category, "last_slug": slug}, file)     

def log_error(message):
    with open(error_log, 'a', encoding='utf-8') as file:
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

def load_last_slug(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as file:
            return json.load(file).get('last_slug', None)
    return None

def extract_products_per_category(output_file, todays_date):
    # Define all categories
    categories = [
        'Mw==',      # Spinneys products
        'Mjk1',      # Fruits & Vegetables
        'Mjk8',      # Meat & Poultry
        'NjY=',      # Seafood & Fish
        'OQ==',      # Grocery
        'NTY=',      # Bakery & Bread
        'Mzg=',      # Cheese, Dairy & Eggs
        'NTU=',      # Cold Cuts & Deli
        'NzI=',      # Beverages
        'Njc=',      # Frozen Food
        'ODA=',      # Sweets & Snacks
        'ODg=',      # Healthy & Specialty
        'MTgz',      # Pets
        'MTM4',      # Electronics
        'MTI5',      # Households
        'MTI0',      # Baby Products
        'MTAy',      # Cleaning Products
        'OTU=',      # Beauty & Personal Care
        'NzMw',      # Back to School
        'MzYw'       # Online Deals
    ]

    # Define the URL for the GraphQL endpoint
    url = "https://spinneys-egypt.com/graphql"

    # Define the headers
    headers = {
        "Content-Language": "en",
        "Content-Type": "application/json",
        "Queryname": "Products",
        "Querytype": "query",
        "Source": "browser",
        "Sourcecode": "DOKI",
        "Store": "default"
    }

    # Load progress and retry mechanism additions
    progress = load_progress()
    last_slug = progress["last_slug"]  # Keep track of the last slug processed

    for category in categories:
        page = 1  # Start from the first page for each category
        page_size = 100  # Set the page size to 100
        total_retrieved = 0  # Track the total products retrieved for this category
        has_more_products = True

        while has_more_products:
            # Define the payload (updated query and variables)
            payload = {
                "query": """
                query Products(
                    $page: Int, 
                    $pageSize: Int, 
                    $filter: ProductAttributeFilterInput = {}, 
                    $sort: ProductAttributeSortInput = {}, 
                    $search: String, 
                    $withAggregations: Boolean = false, 
                    $withPaging: Boolean = false, 
                    $withAttributes: Boolean = false
                ) { 
                    connection: products(
                        currentPage: $page, 
                        pageSize: $pageSize, 
                        filter: $filter, 
                        sort: $sort, 
                        search: $search
                    ) { 
                        aggregations @include(if: $withAggregations) { 
                            attribute_code 
                            label 
                            count 
                            options { 
                                label 
                                count 
                                value 
                            } 
                        } 
                        page_info @include(if: $withPaging) { 
                            total_pages 
                            current_page 
                            page_size 
                        } 
                        total_count 
                        nodes: items { 
                            __typename 
                            id 
                            name 
                            new_from_date 
                            new_to_date 
                            sku 
                            special_from_date 
                            special_price 
                            special_to_date 
                            only_x_left_in_stock 
                            url_key 
                            brand { 
                                url_key 
                            } 
                            categories { 
                                id 
                                url_path 
                                name 
                            } 
                            attributes @include(if: $withAttributes) { 
                                key 
                                label 
                                value 
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
                        } 
                    } 
                }
                """,
                "variables": {
                    "page": page,
                    "pageSize": page_size,
                    "sort": {
                        "position": "ASC"
                    },
                    "filter": {
                        "category_uid": {
                            "eq": category  # Use the current category
                        }
                    },
                    "withAggregations": True,
                    "withPaging": False,
                    "withAttributes": True,
                    "search": ""  # Include search parameter if needed
                }
            }

            # Send the POST request and retry if necessary
            response = retry_request(requests.post, url, headers=headers, json=payload)

            if response and response.status_code == 200:
                response_data = response.json()
                connection_data = response_data.get('data', {}).get('connection', None)
                if connection_data is not None:
                 products = connection_data.get('nodes', [])
                 total_count = response.json().get('data', {}).get('connection', {}).get('total_count', 0)
                
                # Update the total retrieved products
                total_retrieved += len(products)
                print(f'for category: {category} total retrieved is {total_retrieved}')

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

                # Determine if there are more products to fetch
                if total_retrieved >= total_count:
                    has_more_products = False  # All products have been retrieved
                else:
                    page += 1  # Increment page number for next batch of products

            else:
                log_error(f"Error for category {category}: {response.status_code} {response.text if response else 'No response'}")
                break  # Move to the next category


def get_product_details_per_language(slug, lang):
    # Define the URL for the GraphQL endpoint with the store as a query param
    details_url = f"https://spinneys-egypt.com/graphql?store={lang}"

    # Define the headers for the details request
    headers = {
        "Content-Type": "application/json",
        "Store": f"{lang}"
    }

    # Define the payload for fetching product details using url_key as slug
    details_payload = {
        "query": """
        query Product($slug: String!) {
            product(url_key: $slug) {
                id
                name
                sku
                rating_summary
                review_count
                meta_title
                meta_description
                special_from_date
                special_price
                special_to_date
                new_from_date
                new_to_date
                meta_keywords: meta_keyword
                brand {
                    name
                    image_url
                    url_key
                }
                image {
                    url
                    label
                }
                media_gallery {
                    disabled
                    label
                    url
                }
                short_description {
                    html
                }
                description {
                    html
                }
                attributes {
                    label
                    value
                    key
                }
                categories {
                    name
                    url_path
                }
                size_chart {
                    name
                    image
                }
                thumbnail {
                    url
                    label
                }
                brand {
                    name
                    url_key
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
                product_featured_attributes
            }
        }
        """,
        "variables": {
            "slug": slug
        }
    }

    # Send the POST request for product details
    return requests.post(details_url, headers=headers, json=details_payload)
    
brand_lookup = {}

def fetch_brands():
    """Fetch brands for each letter of the alphabet and populate the lookup table."""
    url = "https://spinneys-egypt.com/graphql"
    
    # Set parameters for the loop
    page_size = 100  # Number of brands per page
    total_pages = 1   # Initialize total_pages for the loop
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    # Headers for the GraphQL request
    headers = {
        "Content-Type": "application/json",
        "Source": "DOKI",
        "Store": "default"
    }

    for alpha in alphabet:
        current_page = 1  # Reset to the first page for each letter
        total_pages = 1    # Reset total pages for the letter

        while current_page <= total_pages:
            # Define the payload for fetching brands for the current letter
            payload = {
                "query": """
                query SearchBrands($pageSize: Int, $currentPage: Int, $alpha: String) {
                    brands(
                        filter: { name: { matchAlpha: $alpha } },
                        sort: { slider_sort_order: ASC, name: ASC },
                        pageSize: $pageSize,
                        currentPage: $currentPage
                    ) {
                        items {
                            name
                            image_url
                            url_key
                        }
                        page_info {
                            current_page
                            page_size
                            total_pages
                        }
                    }
                }
                """,
                "variables": {
                    "pageSize": page_size,
                    "currentPage": current_page,
                    "alpha": alpha
                }
            }

            # Make the POST request to fetch brand data
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                brands = data.get("data", {}).get("brands", {}).get("items", [])
                
                # Populate the lookup dictionary
                for brand in brands:
                    name = brand.get("name", "").lower().replace(" ", "")
                    image_url = brand.get("image_url")
                    if name and image_url:
                        brand_lookup[name] = image_url
                
                # Update pagination info
                page_info = data.get("data", {}).get("brands", {}).get("page_info", {})
                current_page = page_info.get("current_page", 1) + 1
                total_pages = page_info.get("total_pages", 1)
            else:
                print(f"Failed to fetch brands data for '{alpha}': {response.status_code}")
                break
            
def fetch_product_details(slug, output_file, todays_date):
    output_file_name = os.path.join(output_file, f"spinneys_extract_data_{todays_date}.xlsx")
    
    # Fetch product details in English
    product_details_in_english = get_product_details_per_language(slug, "default")

    if product_details_in_english and product_details_in_english.status_code == 200:
        product_data = product_details_in_english.json()
        if product_data:
            product_details_eng = product_data.get('data', {}).get('product', {})
        else:
            product_details_eng = {}

        merchant_name = "Spinneys"
        source_type = "Website"

        # Use safe checks for all field extractions
        categories_eng = product_details_eng.get('categories', []) or []
        product_id = product_details_eng.get('id') or None
        brand_details_eng = product_details_eng.get('brand', {}) or {}
        brand_name_in_english = brand_details_eng.get("name") or None

        # Extract all required English fields with safe checks
        product_barcode = product_details_eng.get('sku') or None
        product_name_in_english = product_details_eng.get('name') or None
        offer_start_date = product_details_eng.get('special_from_date') or None
        offer_end_date = product_details_eng.get('special_to_date') or None
        
        # Lookup for brand image URL safely
        brand_image_url = brand_lookup.get(brand_name_in_english.lower().replace(" ", ""), "") if brand_name_in_english else ""

        # Get price_before_offer and check price_after_offer safely
        price_range = product_details_eng.get('price_range', {})
        max_price = price_range.get('maximum_price', {})
        regular_price = max_price.get('regular_price', {})
        final_price = max_price.get('final_price', {})
        price_before_offer = regular_price.get('value') if regular_price else None
        price_after_offer = final_price.get('value') if final_price else None
        
        if price_after_offer == price_before_offer:
            price_after_offer = None
            offer_start_date = None
            offer_end_date = None

        thumbnail = product_details_eng.get('thumbnail', {})
        product_image_url = thumbnail.get('url') if thumbnail else None
        product_url = f"https://spinneys-egypt.com/en/{slug}"

        # Safely fetch product categories in English
        def safe_get_category_name(categories, index):
            return categories[index].get('name') if len(categories) > index and categories[index] else None

        category_one_eng = safe_get_category_name(categories_eng, 0)
        category_two_eng = safe_get_category_name(categories_eng, 1)
        category_three_eng = safe_get_category_name(categories_eng, 2)
        category_four_eng = safe_get_category_name(categories_eng, 3)
        category_five_eng = safe_get_category_name(categories_eng, 4)
        category_six_eng = safe_get_category_name(categories_eng, 5)
        category_seven_eng = safe_get_category_name(categories_eng, 6)
        category_eight_eng = safe_get_category_name(categories_eng, 7)
        category_nine_eng = safe_get_category_name(categories_eng, 8)

        # Fetch product details in Arabic
        product_details_in_arabic = get_product_details_per_language(slug, "ar_EG")

        # Initialize Arabic fields to None
        product_name_in_arabic = None
        brand_name_in_arabic = None
        categories_ar = []

        if product_details_in_arabic and product_details_in_arabic.status_code == 200:
            product_data_ar = product_details_in_arabic.json()
            if product_data_ar:
                product_details_ar = product_data_ar.get('data', {}).get('product', {})
            else:
                product_details_ar = {}

            if product_details_ar:
                product_name_in_arabic = product_details_ar.get('name') or None
                categories_ar = product_details_ar.get('categories', []) or []
                brand_details_ar = product_details_ar.get('brand', {}) or {}
                brand_name_in_arabic = brand_details_ar.get('name') or None

        # Safely fetch product categories in Arabic
        category_one_ar = safe_get_category_name(categories_ar, 0)
        category_two_ar = safe_get_category_name(categories_ar, 1)
        category_three_ar = safe_get_category_name(categories_ar, 2)
        category_four_ar = safe_get_category_name(categories_ar, 3)
        category_five_ar = safe_get_category_name(categories_ar, 4)
        category_six_ar = safe_get_category_name(categories_ar, 5)
        category_seven_ar = safe_get_category_name(categories_ar, 6)
        category_eight_ar = safe_get_category_name(categories_ar, 7)
        category_nine_ar = safe_get_category_name(categories_ar, 8)

    if product_barcode and product_barcode not in processed_barcodes:
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
            crawled_on=todays_date,
            brand_image_url=brand_image_url
        )

        # Write the product details to an Excel file
        write_to_excel(output_file_name, product)
    else:
        log_error(f"Error fetching details for slug {slug}: {product_details_in_english.status_code if product_details_in_english else 'No response'}")


def extract_discounted_products(output_file, todays_date):
    # Define the GraphQL endpoint
    url = "https://spinneys-egypt.com/graphql"

    # Define the headers
    headers = {
        "Content-Language": "en",
        "Content-Type": "application/json",
        "Queryname": "DiscountedProducts",
        "Querytype": "query",
        "Source": "browser",
        "Sourcecode": "DOKI",
        "Store": "default"
    }

    page = 1
    page_size = 100  # Set the page size (you can adjust as needed)
    total_retrieved = 0  # Track total number of products retrieved
    has_more_products = True

    progress_file = 'extractions/spinneys/progress_discounted_price.json'    
    # Load the last processed slug
    last_slug = load_last_slug(progress_file)
    
    # If last_slug is not None, continue from that slug
    if last_slug:
        print(f"Resuming from last slug: {last_slug}")
    
    while has_more_products:
        # Define the payload (data) for the current page
        payload = {
            "query": """
            query DiscountedProducts($page: Int, $pageSize: Int, $filter: ProductAttributeFilterInput = {}, $sort: ProductAttributeSortInput = {}, $withAggregations: Boolean = false, $withPaging: Boolean = false, $withAttributes: Boolean = false) {
                connection: productDeals(currentPage: $page, pageSize: $pageSize, filter: $filter, sort: $sort) {
                    aggregations @include(if: $withAggregations) {
                        ...ProductAggregation
                    }
                    page_info @include(if: $withPaging) {
                        ...PageInfo
                    }
                    total_count
                    nodes: items {
                        ...ProductCard
                        attributes @include(if: $withAttributes) {
                            key
                            label
                            value
                        }
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
                new_from_date
                new_to_date
                sku
                special_from_date
                special_price
                special_to_date
                only_x_left_in_stock
                url_key
                brand {
                    url_key
                }
                categories {
                    id
                    url_path
                    name
                }
                attributes {
                    key
                    label
                    value
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
                categories {
                    url_path
                    section
                }
                ...CartControl
                ... on ConfigurableProduct {
                    variants {
                        attributes {
                            code
                        }
                        product {
                            __typename
                            name
                            sku
                            special_from_date
                            special_price
                            special_to_date
                            only_x_left_in_stock
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
                            image {
                                url
                                label
                            }
                            url_key
                        }
                    }
                }
                ... on BundleProduct {
                    items {
                        options {
                            uid
                        }
                    }
                }
            }
            fragment CartControl on ProductInterface {
                cart_control {
                    increment_step
                    max_amount
                    min_amount
                    unit
                }
            }
            """,
            "variables": {
                "page": page,
                "pageSize": # The code `page_size` appears to be a variable declaration in Python, but
                # it is not assigned any value. It is simply declaring a variable named
                # `page_size` without initializing it.
                page_size,
                "sort": {"position": "ASC"},
                "filter": {},
                "withAggregations": True,
                "withPaging": True,
                "search": ""
            }
        }

        # Send the POST request for fetching discounted products
        try:
            response = retry_request(requests.post, url, headers=headers, json=payload)
            if response.status_code == 200:
                try:
                    response_data = response.json()  # Correctly parse the JSON response
                    discounted_products = response_data.get('data', {}).get('connection', {}).get('nodes', [])
                    total_count = response_data.get('data', {}).get('connection', {}).get('total_count', 0)

                    # Update the total number of products retrieved
                    total_retrieved += len(discounted_products)
                    print(f'total discounted products retrieved are: {total_retrieved}')

                    # Check if the last slug is in the current batch of products
                    if last_slug:
                        found_last_slug = False
                        for product in discounted_products:
                            slug = product.get('url_key')
                            if slug == last_slug:
                                found_last_slug = True
                            if found_last_slug and slug:
                                fetch_product_details(slug, output_file, todays_date)
                                save_last_slug(progress_file, slug)  # Save the last processed slug
                    else:
                        # Process each product normally
                        for product in discounted_products:
                            slug = product.get('url_key')
                            if slug:
                                fetch_product_details(slug, output_file, todays_date)
                                save_last_slug(progress_file, slug)  # Save the last processed slug

                    # Determine if there are more products to fetch
                    if total_retrieved >= total_count:
                        has_more_products = False  # Stop fetching as all products have been retrieved
                    else:
                        page += 1  # Increment the page number for the next iteration

                except json.JSONDecodeError:
                    print("Error parsing response JSON:", response.text)
            else:
                print("Error Response Body:", response.text)  # Log the raw response for debugging
                log_error(f"Error fetching discounted products: {response.status_code} {response.text}")

        except Exception as e:
            print("Exception occurred while making request:", e)
            # Optional: Implement retry logic here
            time.sleep(5)  # Wait for 5 seconds before retrying
            continue  # Restart the loop

def extract_all_spinneys_product_data(output_file, todays_date):
    extract_products_per_category(output_file, todays_date)

def run_spinneys_crawler():
    output_file = os.path.join(output_directory)
    todays_date = datetime.today().strftime('%Y-%m-%d')

    while True:  # Infinite loop to automatically restart the script
        try:
            extract_all_spinneys_product_data(output_file, todays_date)
            extract_discounted_products(output_file, todays_date)
            print("Data extraction completed successfully.")
            break  # Exit the loop if successful
        except Exception as e:
            log_error(f"Unexpected error: {e}")
            print(f"Error encountered: {e}. Restarting script in 10 seconds...")
            time.sleep(10)  # Add a delay before restarting the script
            
fetch_brands()
run_spinneys_crawler()
