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

def convert_url_to_arabic(url):
    return url.replace('/en/', '/ar/')