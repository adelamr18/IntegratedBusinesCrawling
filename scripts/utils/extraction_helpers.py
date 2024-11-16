from lxml import html

def extract_product_name_in_english(soup, selector):
    try:
        product_name_en = soup.select_one(selector).text
        return product_name_en if product_name_en else "Product name not found"
    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "Product name not found"
    
def extract_product_name_in_arabic(soup, selector):
    try:
        product_name_ar = soup.select_one(selector).text
        return product_name_ar if product_name_ar else "لم يتم العثور على اسم المنتج"
    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "لم يتم العثور على اسم المنتج"
    
def extract_product_name_in_arabic_using_xpath(soup_ar, xpath_selector):
    try:
        page_content = str(soup_ar)
        tree = html.fromstring(page_content)
        product_name_ar = tree.xpath(xpath_selector)
        
        return product_name_ar[0].text if product_name_ar and product_name_ar[0] is not None else "لم يتم العثور على اسم المنتج"
    except Exception as e:
        print(f"Error extracting product name: {e}")
        return "لم يتم العثور على اسم المنتج"
