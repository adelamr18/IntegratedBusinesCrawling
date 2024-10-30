import requests
from bs4 import BeautifulSoup
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def scrape_category_pages(base_url):
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
            
            if product_link:
                # Combine the base URL if the link is relative
                product_link = product_link if product_link.startswith('http') else f"https://www.metro-markets.com{product_link}"
                print(f"Product Link: {product_link}")
                
            # Extract other product data as needed
            product_name = product.select_one('div.product-name').text.strip() if product.select_one('div.product-name') else 'N/A'
            product_price = product.select_one('span.product-price').text.strip() if product.select_one('span.product-price') else 'N/A'
            print(f"Product Name: {product_name}, Product Price: {product_price}")
        
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

# Call the function with the category URL
category_url = "https://www.metro-markets.com/categoryl1/Bakery/9"
scrape_category_pages(category_url)
