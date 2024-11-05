import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import json
from datetime import datetime
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set the base directory and input/output paths
base_directory = '/Users/ajlapandzic/Desktop/Projects/IntegratedBusinesCrawling'
input_json_path_for_category_urls = os.path.join(base_directory, 'extractions', 'MetroMarkets', 'category_urls.json')
output_directory = os.path.join(base_directory, 'extractions', 'MetroMarkets')

def load_category_urls(json_file):
    """Load category URLs from a JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['categories']

def scrape_category_pages(base_url, category_name, output_file_name):
    """Scrape product pages from a given category URL."""
    
    # Open CSV file for writing
    with open(output_file_name, mode='a', newline='', encoding='utf-8') as csvfile:
        # Create a CSV writer
        csv_writer = csv.writer(csvfile)
        
        # Write the header row to the CSV file if it's empty
        if csvfile.tell() == 0:  # Check if file is empty
            csv_writer.writerow(['Category', 'Product URL', 'is_processed'])

        page_num = 1
        while True:
            # Build URL for the current page
            url = f"{base_url}?page={page_num}"
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Failed to retrieve page {page_num}. Status code: {response.status_code}")
                break

            # Parse page content
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Select the parent container holding all products per page
            product_container = soup.select_one("body > div.root > div.home-wrapper > div.search-parent-wrapper > main > div > div.search-content > div.search-grid-wrapper > div")
            if not product_container:
                print("No products found on this page.")
                break

            # Loop through each product inside the container and extract the data
            products = product_container.find_all('div', class_="product-card")  # Update with the actual class name
            for product in products:
                # Extract the link to the product
                product_link = product.select_one('a')['href'] if product.select_one('a') else None
                print(product_link)
                
                if product_link:
                    # Combine the base URL if the link is relative
                    product_link = product_link if product_link.startswith('http') else f"https://www.metro-markets.com{product_link}"
                else:
                    product_link = 'N/A'  # Set to 'N/A' if link is not found
                
                # Print product information
                print(f"Category: {category_name}, Product Link: {product_link}")
                
                # Write product data to the CSV file
                csv_writer.writerow([category_name, product_link, False])  # is_processed is always False
            
            # Check for pagination
            pagination = soup.select_one('body > div.root > div.home-wrapper > div.search-parent-wrapper > main > div > div.search-content > div.search-grid-wrapper > nav > ul')
            if not pagination:
                print("No more pages found.")
                break
            
            # Check if the current page has a next page
            active_page = pagination.select_one('li.page-item.active')
            next_page = active_page.find_next_sibling('li')  # Get the next sibling
            
            # If next page is None or doesn't have an anchor, we've reached the last page
            if next_page is None or not next_page.find('a'):
                print("Reached the last page.")
                break
            
            # Move to the next page
            page_num += 1
            time.sleep(1)  # Be kind to the server

def main():
    # Load the category URLs from JSON
    crawled_date = datetime.now().strftime('%Y-%m-%d')
    output_file_name = os.path.join(output_directory, f'extracted_urls_{crawled_date}.csv')
    categories = load_category_urls(input_json_path_for_category_urls)

    # Call the scraping function for each category
    for category in categories:
        category_name = category['name']
        category_url = category['url']
        scrape_category_pages(category_url, category_name, output_file_name)

if __name__ == "__main__":
    main()
