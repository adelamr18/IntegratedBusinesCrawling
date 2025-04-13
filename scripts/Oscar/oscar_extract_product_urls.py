import sys
import os
import json
import csv
import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
input_json_path_for_category_urls = os.path.join(base_directory, 'extractions', 'Oscar', 'category_urls.json')
output_directory = os.path.join(base_directory, 'extractions', 'Oscar')
os.makedirs(output_directory, exist_ok=True)

output_file_path = os.path.join(output_directory, 'product_urls.csv')

def extract_product_urls():
    with open(input_json_path_for_category_urls, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_file_path, 'w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Category", "Product URL", "is_processed"])

        for cat_info in data.get("categories", []):
            category = cat_info["category"]
            category_url = cat_info["url"]

            try:
                response = requests.get(category_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                product_links = soup.find_all("a", href=lambda x: x and "show_product" in x)

                for link in product_links:
                    product_url = link["href"]
                    if product_url.startswith("/show_product"):
                        product_url = "https://www.oscarstores.com" + product_url
                    writer.writerow([category, product_url, "False"])

            except Exception as e:
                print(f"Error processing category '{category}': {e}")

if __name__ == "__main__":
    extract_product_urls()
    print(f"Product URLs extracted to: {output_file_path}")
