from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium import webdriver

 # Initialize the Firefox driver
def driver_intialize():
    firefox_options = Options()
    firefox_options.headless = True
    firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    service = Service(executable_path=r'I:\Web Crawler Project\geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=firefox_options)
    return driver

def extract_product_price():
    driver = driver_intialize()
    driver.get('https://www.carrefouregypt.com/mafegy/en/white-eggs/mychoice-white-eggs-30p/p/305478')
    actions = ActionChains(driver)
    price = driver.find_elements(By.CSS_SELECTOR, '.css-17ctnp')
    print(price)
