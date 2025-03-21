import csv
import os
import time
import logging
import requests
from lxml import etree
from googletrans import Translator
import pandas as pd
import asyncio
from functools import wraps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
translator = Translator()

# Retry decorator for handling transient errors
def retries(max_retries=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logging.warning(f"Attempt {attempts}/{max_retries} failed for '{func.__name__}': {e}")
                    if attempts < max_retries:
                        logging.info(f"Retrying '{func.__name__}' after {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logging.error(f"'{func.__name__}' failed after {max_retries} retries.")
                        raise
        return wrapper
    return decorator

# Initialize the Chrome WebDriver
@retries(max_retries=3, delay=1, exceptions=(NoSuchElementException,))
def get_chromedriver(headless=False):
    logging.info("Initializing Chrome WebDriver...")
    
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "safebrowsing.enabled": True,
        "profile.managed_default_content_settings.images": 2,  # Disable images
        "profile.managed_default_content_settings.javascript": 1,  # Enable JS
    })
    options.add_argument("--disable-logging")
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_page_load_timeout(300)  # Set timeout to 30 seconds
    pid = driver.service.process.pid
    logging.info(f"Chrome WebDriver initialized with PID: {pid}")
    return driver, pid

@retries(max_retries=3, delay=2, exceptions=(TimeoutException,))
def get_href_attributes(driver, element_xpath, scroll_pause_time=5):
    logging.info("Starting to collect href attributes...")
    hrefs = set()
    i = 0
    try:
        wait = WebDriverWait(driver, 10)
        load_more_button = wait.until(
            EC.element_to_be_clickable((By.ID, "loadmoreScroll"))
        )
        total_cases = int(load_more_button.get_attribute('data-max-posts'))
        print('total_cases:', total_cases)
        while load_more_button:

            # Wait for elements to load
            WebDriverWait(driver, 50).until(
                EC.presence_of_all_elements_located((By.XPATH, element_xpath))
            )
            
            # Collect hrefs
            elements = driver.find_elements(By.XPATH, element_xpath)
            print(len(elements))
            for element in elements:
                try:
                    
                    href = element.get_attribute("href")
                    if href and href not in hrefs:
                        hrefs.add(href)
                except StaleElementReferenceException:
                    continue

            logging.info(f"Scroll {i + 1}: Collected {len(hrefs)} unique hrefs so far.")

            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)

            time.sleep(scroll_pause_time)

            # Stop if no new hrefs are added
            if len(hrefs) == total_cases:
                logging.info("No new hrefs found. Stopping scrolling.")
                break
            print("scrolling")
            i += 1

            try:
                wait = WebDriverWait(driver, 10)
                load_more_button = wait.until(
                    EC.element_to_be_clickable((By.ID, "loadmoreScroll"))
                )
            except:
                logging.info("Loading button not found. Stopping scrolling.")
                break

    except TimeoutException:
        logging.warning("Timeout occurred while waiting for elements.")
        return list(hrefs)

    logging.info(f"Final collection: {len(hrefs)} unique hrefs.")
    return list(hrefs)

# Write data to CSV
def write_to_csv(filename, data):
    logging.info(f"Writing data to {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Hotel Name', 'Hotel Category', 'Hotel Referral', 'Hotel Rent'])
        writer.writerows(data)
    logging.info("Data written to CSV successfully.")

def extract_data_from_page(url):
    try:
        # Send a GET request to fetch the page content
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        with open('file.html', 'w') as f:
            f.write(response.text)

        # Parse the HTML content using lxml
        tree = etree.HTML(response.text)
        
        # Extract the hotel name
        hotel_name = tree.xpath('//h1[@itemprop="name"]/text()')
        hotel_name = hotel_name[0].strip() if hotel_name else "N/A"
        
        # Extract the category
        category = tree.xpath('//div[@class="header__subtitle text-script-a"]/text()')
        hotel_category = category[0].strip() if category else "N/A"
        
        # Extract the referral link
        referral_link = tree.xpath('//div[@class="single-plekje__buttons"]//a[contains(., "Go to the website")]/@href | //a[contains(@class, "button--external gtm-website-visit")]/@href')
        referral_link = referral_link[0] if referral_link else "N/A"
        
        # Extract the rent per night
        rent_per_night = tree.xpath('//span[contains(@class, "block-meta__item-price")]/text()')
        rent_per_night = rent_per_night[0].strip() if rent_per_night else "N/A"
        
        
        address_parts = tree.xpath('//div[@class="article__caption"]//text()')
        address = " ".join([part.strip() for part in address_parts if part.strip()])  # Clean and join all text parts
        
        # Create a dictionary with the extracted data
        data = [
            hotel_name,
            hotel_category,
            referral_link,
            rent_per_night,
            address
        ]
        print(data)
        return data

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return []
    except Exception as e:
        print(f"Error extracting data: {e}")
        return []

async def translate_text(text, src='nl', dest='en'):
    try:
        translated = await translator.translate(text, src=src, dest=dest)
        return translated.text
    except Exception as e:
        print(f"Failed to translate text '{text}': {e}")
        return text  # Return the original text if translation fails

async def async_translate_and_extract(url):
    # Extract data from the page synchronously
    print(f'url : {url}')
    data = extract_data_from_page(url)
    
    if len(data) == 5:
        # Translate the category asynchronously
        data[1] = await translate_text(data[1])  # Category is at index 1, not 2
        data[4] = await translate_text(data[4])
        
    # Return the translated data
    return data

# Function to write data to an Excel file
def write_to_excel(file_name, data_list):
    # Check if data_list contains dictionaries or structured data
    if data_list and isinstance(data_list[0], dict):
        # Convert list of dictionaries to a DataFrame
        df = pd.DataFrame(data_list, columns=['name' , 'category' , 'referal_link' , 'rent per night' , 'address'])
    else:
        # Convert list of lists/tuples to a DataFrame
        df = pd.DataFrame(data_list, columns=['name' , 'category' , 'referal_link' , 'rent per night' , 'address'])

    # Write the DataFrame to an Excel file
    df.to_excel(file_name, index=False, engine="openpyxl")
    print(f"Data successfully written to {file_name}")

async def main():
    driver = None
    pid = None
    try:
        # Initialize WebDriver
        driver, pid = get_chromedriver(headless=True)
        driver.get("https://bijzonderplekje.nl/overnachten/")
        logging.info(f"Page Title: {driver.title}")

        # Collect hrefs
        hrefs = get_href_attributes(driver, '//a[@class="card card--plekje"]')
        logging.info("hrefs: {}".format(len(hrefs)))
        if not hrefs:
            logging.warning("No hrefs collected. Exiting.")
            return
        logging.info(f"Collected {len(hrefs)} unique hrefs.")
        print("hrefs:", len(hrefs))
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return
    finally:
        if driver:
            driver.quit()
            logging.info(f"Chrome WebDriver stopped. Process ID: {pid}")

    logging.info("Starting to extract data...")

    # Run async extraction and translation
    try:
        data_list = await asyncio.gather(
            *[async_translate_and_extract(href) for href in hrefs]
        )
        logging.info("Data extraction and translation completed.")
    except Exception as e:
        logging.error(f"Error during async extraction: {e}")
        return

    # Write data to Excel
    try:
        write_to_excel('Bijzonderplekje_data.xlsx', data_list)
        logging.info("Data written to Excel successfully.")
    except Exception as e:
        logging.error(f"Error writing to Excel: {e}")


if __name__ == "__main__":
    asyncio.run(main())
