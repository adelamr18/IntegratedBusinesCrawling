from selenium.webdriver.common.by import By
import sys
from time import sleep
from utils.helpers import driver_intialize
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import NoSuchElementException
import csv
import os
from utils.helpers import driver_intialize

def navigate_to_main_category(driver): 
    driver.get('https://www.carrefouregypt.com/mafegy/en/c/NFEGY2300000')
    actions = ActionChains(driver)
    sleep(2)
    actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')).perform()
    sleep(2)
    elements_Level_1 = driver.find_elements(By.CSS_SELECTOR, 'ul.css-9fgw80 li a[data-testid="category_level_1"]')
    print(len(elements_Level_1))
    for element in range(1, len(elements_Level_1)):
        print(element)
        first_buton = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')))
        actions.click(first_buton).perform()
        main_category_element = driver.find_element(By.XPATH, f'//*[@id="__next"]/div[1]/div[2]/nav/div[2]/ul[1]/li[{element}]/a/p')
        #actions.move_to_element(driver.find_elements(By.XPATH, f'//*[@id="__next"]/div[1]/div[2]/nav/div[2]/ul[1]/li[{element}]/a/p')).perform()
        actions.click(main_category_element).perform()
        print(f"level 1 -- Hovered over: {main_category_element.text}")
        main_category_name = main_category_element.text
        actions.click(main_category_element).perform()
        sleep(30)
        url= driver.current_url
        print("Current URL:", url)
        navigate_to_products_list(driver, url)
        url_list = load_whole_page(driver, scroll_position=0, scroll_step=50, delay=0.1)
        write_to_csv(main_category_name , url_list)
        actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')).perform()
    driver.quit()
       

def navigate_to_products_list(driver , url):
    correct_format_pattern = r"https://www\.carrefouregypt\.com/mafegy/en/c/.*\d+"
    pattern_to_modify = r"(https://www\.carrefouregypt\.com/mafegy/en)/.*/clp_(.*\d+)"
    if re.match(correct_format_pattern, url):
        print(f"new Url:{url} ")
        driver.get(url)
        return url 
     
    modified_url = re.sub(pattern_to_modify, r"\1/c/\2", url)
    print(f"new Url:{modified_url} old: {url}")
    driver.get(modified_url)
    return modified_url



def load_whole_page(driver, scroll_position=0, scroll_step=50, delay=0.1):
    actions = ActionChains(driver)
    while True:
        # Get the total height of the page
        total_height = driver.execute_script("return document.body.scrollHeight")
        
        print(total_height)
        while scroll_position < (total_height):
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            scroll_position += scroll_step
            sleep(delay)
        
        try:
            load_more_button = driver.find_element(By.CSS_SELECTOR, '[data-testid=trolly-button]')
            if load_more_button:
                driver.execute_script('document.querySelector(\'[data-testid="trolly-button"]\').click()')
                print("load clicked")
                sleep(2)  
                return load_whole_page(driver,scroll_position=total_height, scroll_step=80, delay=0.1)
        except NoSuchElementException:
            links = get_page_links(driver)
            print("2 Loaded Full Page")
            return links

def get_page_links(driver):
    all_items = driver.find_elements(By.CSS_SELECTOR, '.css-1npvvk7')
    item_urls = []
    for element in all_items:
        a_element = element.find_element(By.TAG_NAME, 'a')
        # Extract the href attribute from the <a> tag
        href = a_element.get_attribute('href')
        if href:  # Ensure href is not None
            item_urls.append(href)
    print(len(item_urls))
    return item_urls

def write_to_csv(category, urls):
    file_name = 'Carrefour_URLs.csv'

    # Check if the file exists
    file_exists = os.path.isfile(file_name)

    # Open the file in append mode, create if not exists
    with open(file_name, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # If the file doesn't exist, write the header
        if not file_exists:
            writer.writerow(["Main Category", "URL"])

        # Write the URLs to the file, each with the main category
        for url in urls:
            writer.writerow([category, url])

    print(f"URLs have been added to {file_name} successfully!")

    pass

def run_specific_categories():
    urls = [
        {
            'name': 'personal care',
            'url': 'https://www.carrefouregypt.com/mafegy/en/personal-care/n/c/clp_NFEGY2000000'
        },
        {
            'name': 'electronic appliances',
            'url': 'https://www.carrefouregypt.com/mafegy/en/electronics-appliances/n/c/clp_NFEGY4000000'
        },
        {
            'name': 'cleaning household',
            'url': 'https://www.carrefouregypt.com/mafegy/en/cleaning-household/n/c/clp_NFEGY3000000'
        }
    ]
    for item in urls:
        name = item.get('name')
        url = item.get('url')
        navigate_to_products_list(driver, url)
        url_list = load_whole_page(driver, scroll_position=0, scroll_step=50, delay=0.1)
        write_to_csv(name , url_list)
    pass

driver = driver_intialize()

#navigate_to_products_list(driver , "https://www.carrefouregypt.com/mafegy/en/baby-products/n/c/clp_FEGY1000000")
run_specific_categories()
#navigate_to_main_category(driver)