def extract_product_name_in_english(soup, selector):
    try:
        product_name_en = soup.select_one(selector).text
        return product_name_en if product_name_en else "Product name not found"
    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "Product name not found"