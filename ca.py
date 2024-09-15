from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from selenium.common.exceptions import NoSuchElementException

 # Initialize the Firefox driver
def driver_intialize():
    firefox_options = Options()
    firefox_options.headless = True
    firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    service = Service(executable_path=r'I:\Web Crawler Project\geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver


def parse_with_selenium(driver): 
    driver.get('https://www.carrefouregypt.com/mafegy/en/fresh-food/n/c/clp_FEGY1600000')
    actions = ActionChains(driver)
    sleep(2)
    actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')).perform()
    sleep(2)
    elements_Level_1 = driver.find_elements(By.CSS_SELECTOR, 'ul.css-9fgw80 li a[data-testid="category_level_1"]')

    for element in elements_Level_1:
        first_buton = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')))
        actions.click(first_buton).perform()
        actions.move_to_element(element).perform()
        print(f"level 1 -- Hovered over: {element.get_attribute('rel')}")

        for count in range(1,100):
            try:
                item = driver.find_elements(By.XPATH, f'//*[@id="__next"]/div[1]/div[2]/nav/div[2]/ul[2]/li[{count}]/a/p')[0]
                print(f"level 2 -- Hovered over: {item.text}")
            except:
                print(f"{element.get_attribute('rel')} has {count-1} items")
                break
                


def navigate_to_products_list(url):
    correct_format_pattern = r"https://www\.carrefouregypt\.com/mafegy/en/c/FEGY\d+"
    pattern_to_modify = r"(https://www\.carrefouregypt\.com/mafegy/en)/.*/clp_(FEGY\d+)"
    if re.match(correct_format_pattern, url):
        print(f"new Url:{url} ")
        return url 
     
    modified_url = re.sub(pattern_to_modify, r"\1/c/\2", url)
    print(f"new Url:{modified_url} old: {url}")
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
            get_page_links(driver)
            print("2 Loaded Full Page")
            return 

def get_page_links(driver):
    print("started")
    elements_count_text = driver.find_element(By.CSS_SELECTOR,'[data-testid=page-info-content').text
    numbers = re.findall(r'\d+', elements_count_text)  # Find all sequences of digits
    numbers_only = int(''.join(numbers))  # Convert to integer after joining

    item_urls = []
    for row in range(1, numbers_only // 4):  # Now numbers_only is an integer
        for col in range(1, 5):
            try:
                #print(f'row = {row} column = {col}')
                item_url = driver.find_element(By.XPATH, f'//*[@id="__next"]/div[3]/div[1]/div[4]/div[2]/div[2]/ul/div/div[{row}]/div/div/div[{col}]/div/ul/div/div[1]/div[2]/a').get_attribute('href')
                item_urls.append(item_url)
                print(item_url)
            except NoSuchElementException:
                return item_urls
    pass

driver = driver_intialize()
driver.get('https://www.carrefouregypt.com/mafegy/en/c/FEGY1660000')
load_whole_page(driver,scroll_position=0, scroll_step=80, delay=0.1)