import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from scrapy.utils.project import get_project_settings
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import json
# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

class CarrefourSpider(scrapy.Spider):
    name = "Carrefour_Spider"

    def start_requests(self):
        # Define your initial URLs to scrape
        urls = ['https://www.carrefouregypt.com/mafegy/en/c/FEGY1760000']

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_with_selenium)

    
    def parse_with_selenium(self, response):
        # Initialize the Firefox driver
        settings = get_project_settings()
        geckodriver_path = settings.get('DRIVER_PATH')

        firefox_options = Options()
        firefox_options.headless = True
        firefox_options.add_argument('--window-size=1920,1080')
        firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        service = Service(executable_path=r'I:\Web Crawler Project\geckodriver.exe')
        driver = webdriver.Firefox(service=service, options=firefox_options)
        Categories = {}

        # Use Selenium to open the page
        driver.get(response.url)
        sleep(5)
        actions = ActionChains(driver)
        actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')).perform()
        sleep(2)
        elements_Level_1 = driver.find_elements(By.CSS_SELECTOR, 'ul.css-9fgw80 li a[data-testid="category_level_1"]')
        #print(f"length {len(elements_Level_1)}")
        for element in elements_Level_1:
            # Move to the element and perform hover
            #actions.move_to_element(driver.find_element(By.XPATH, f'//*/div[1]/div[2]/nav/div[2]/ul[1]/li[{element+1}]/a')).perform()
            actions.move_to_element(element).perform()
            print(f"level 1 -- Hovered over: {element.get_attribute('rel')}")

            #Adding a small delay to observe the hover action
            sleep(3)
            level_2_elements = driver.find_elements(By.CSS_SELECTOR, 'p[data-testid="category_level_2"]')

            Category_Sub_2 = {}
            counter =0
            for level_2 in level_2_elements:
                try:
                    actions.move_to_element(level_2).perform()
                    Category_Sub_2[f"{level_2.get_attribute('p')}"] = {
                        'Name': f"{level_2.get_attribute('p')}",
                        'Sub Xpath' : f"{level_2}"
                    }
                except StaleElementReferenceException:
                    
                    level_2_elements_2 = driver.find_elements(By.CSS_SELECTOR, 'p[data-testid="category_level_2"]')
                    #print(f"got element again length = {len(level_2_elements_2)} counter = {counter}")
                    #Category_Name = f"{level_2_elements_2[counter].get_attribute('rel')}"
                    if counter < len(level_2_elements_2):
                        Category_Name = f"{level_2_elements_2[counter].get_attribute('p')}"
                        #actions.move_to_element(Category_Name).perform()
                        Category_Sub_2[Category_Name] = {
                            'Name': Category_Name,
                            'Sub Xpath': f"{level_2_elements_2[counter]}"
                        }
                        print("passed")
                    else:
                        print(f"{element.get_attribute('rel')} Element at index {counter} not found after retry.")
                        
                counter = counter+1

            actions.move_to_element(driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[2]/nav/div[1]/div[1]/a')).perform()
                
            Categories[f"{element.get_attribute('rel')}"] = {
                'Name': f"{element.get_attribute('rel')}",
                'Xpath' : f'{element}',
                'Sub-Categories Xpaths' : Category_Sub_2
            }
        file_path = 'data.json'  # This will save the file in the root folder of your project
        # Open the file in write mode and save the JSON data
        with open(file_path, 'w') as json_file:
            json.dump(Categories, json_file, indent=4)
        print(Categories)
        driver.quit()  # Ensure the driver is properly closed after use


        # finally:
        #     print("Done")
        #     file_path = 'data.json'  # This will save the file in the root folder of your project

        # # Open the file in write mode and save the JSON data
        #     with open(file_path, 'w') as json_file:
        #         json.dump(Categories, json_file, indent=4)
        #     print(Categories)
            #driver.quit()  # Ensure the driver is properly closed after use

        # After Selenium is done, proceed with Scrapy parsing (if needed)
        # Example: yield Scrapy items or more requests

    def parse(self, response):
        # Standard Scrapy parsing logic
        pass
