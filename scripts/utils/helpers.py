from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium import webdriver

 # Initialize the Firefox driver
def driver_intialize():
    firefox_options = Options()
    firefox_options.headless = True
    firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    
    # Create a Firefox profile
    profile = webdriver.FirefoxProfile()

    # Disable images in the profile
    profile.set_preference("permissions.default.image", 2)

    # Disable JavaScript in the profiles
    profile.set_preference("javascript.enabled", False)

    # Set the geckodriver executable path
    service = Service(executable_path=r'geckodriver.exe')

    # Initialize the Firefox driver with the profile and options
    driver = webdriver.Firefox(service=service, options=firefox_options)

    return driver

def convert_url_to_arabic(url):
    return url.replace('/en/', '/ar/')