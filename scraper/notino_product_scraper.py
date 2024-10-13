"""Scraper for Notino products. 
Contains scraper of brands catalog site, specific brand paginated site and product page."""

from random import randint

from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError

import time

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper.base_scraper import BaseScraper, BaseListScraper
from scraper.exceptions import ScraperError

from utils.webdriver import WebDriver

from logger_config import get_logger

logger = get_logger(__name__)


class NotinoProductListScraper(BaseListScraper):
    """A scraper for Notino brands catalog pages"""

    def __init__(self, base_url: str, driver: WebDriver):
        logger.info("Initializing NotinoBrandsCatalogScraper with base URL: %s", base_url)
        self.base_url = base_url
        self.web_driver = driver

        super().__init__(base_url)

    def get_brands(self) -> list:
        """Get the brands from the brands catalog page"""
        try:
            time.sleep(randint(1, 3))
            response = self.send_request(self.base_url)
            soup = self.parse_html(response)
            brands, links = self.extract_brands(soup)
            return brands, links
        except HTTPError as e:
            logger.error("Failed to get brands catalog site: %s", e)
        except Exception as e:
            logger.error("An error occurred: %s", e)

    def extract_brands(self, soup: BeautifulSoup) -> list:
        """Extract brands from the HTML content of the brands catalog page"""
        brands = []
        links = []
        
        crossroad_brands_div = soup.find('div', class_='crossroad-brands')
        if not crossroad_brands_div:
            logger.error("No 'crossroad-brands' div found")
            return brands, links

        brand_divs = crossroad_brands_div.find_all('div', class_='brand')
        for brand_div in brand_divs:
            reset_div = brand_div.find('div', class_='reset')
            if not reset_div:
                continue

            li_elements = reset_div.find_all('li')
            for li in li_elements:
                a_tag = li.find('a')
            if a_tag and 'href' in a_tag.attrs:
                links.append(a_tag['href'])
                brands.append(a_tag.text.strip())

        return brands, links
    
    def get_brand_url(self, brand: str) -> str:
        """Construct the URL for a specific brand"""
        return f"{self.base_url}/{brand}"

    def load_all_products_for_brand(self, brand: str):
        """Load all products for a brand by clicking the 'Show more' button until it no longer exists"""
        url = self.get_brand_url(brand)
        self.web_driver.get(url)

        logger.info("Loading all products for brand %s", brand)

        try:
            while True:
                # Wait for the "Show more" button to be clickable
                show_more_button = self.web_driver.wait_for_element(By.CSS_SELECTOR, 'button[data-testid="footer-action-button"]')
                show_more_button.click()
                # # Wait for new products to load
                self.web_driver.wait_for_element(By.CSS_SELECTOR, 'div[data-testid="product-container"]')

                # Check if the "Show more" button still exists
                if not self.web_driver.find_element(By.CSS_SELECTOR, 'button[data-testid="footer-action-button"]'):
                    break

                time.sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Extract all product containers
            soup = BeautifulSoup(self.web_driver.get_page_source(), 'html.parser')
            product_containers = soup.find_all('div', {'data-testid': 'product-container'})
            self.web_driver.close()

        logger.info("Loaded %d products for brand %s", len(product_containers), brand)
        return product_containers
    
    def extract_product_links(self, soup: BeautifulSoup) -> list:
        """Extract product links from the HTML content of the brand page"""
        product_elements = soup.select("div[data-testid='product-container']")
        product_links = [element.find("a")["href"] for element in product_elements]
        return product_links
    
    def extract_general_product_details(self, soup: BeautifulSoup) -> dict:
        """Extract general product details from the HTML content of the brand page"""
        general_product_details = []
        logger.info("Extracting general product details")
        try:
            product_elements = soup.select("div[data-testid='product-container']")
            for element in product_elements:
                product_details = {}

                # Get name, brand with skipping if not available
                # Get name
                try:
                    product_details["name"] = element.select_one("a > div:nth-child(3) > h2").text.strip()
                except AttributeError:
                    logger.error("No product name found for product %s", element.select_one("a")["href"])
                    continue

                # Get brand
                try:
                    product_details["brand"] = element.select_one("a > div:nth-child(3) > h3").text.strip()
                except AttributeError:
                    logger.error("No brand found for product %s", element.select_one("a")["href"])
                    continue

                # Get description
                try:
                    product_details["description"] = element.select_one("a > div:nth-child(3) > p").text.strip()
                except AttributeError:
                    logger.error("No description found for product %s", element.select_one("a")["href"])
                    continue

                # Get price
                try:
                    price_text = element.select_one("a > div:nth-child(3) > div.product-price > div > div > span[data-testid='price-component']").text.strip()
                    product_details["price"] = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
                except AttributeError:
                    # If price is not available, warning message is contained in the warning-text div instead of product-price div
                    try:
                        price_text = element.select_one("a > div:nth-child(3) > div.warning-text").text.strip()
                        product_details["price"] = price_text
                    except AttributeError:
                        logger.error("No price found for product %s", element.select_one("a")["href"])
                        continue
                
                general_product_details.append(product_details)
        except Exception as e:
            logger.error("An error occurred: %s", e)
        return general_product_details
    
    def extract_product_details(self, soup: BeautifulSoup) -> dict:
        """Extract product details from the HTML content of the product page"""
        product_details = {}
        try:
            # Get description
            try:
                product_details["description"] = soup.select_one("div[data-testid='pd-description-text'] > p.nth-child(1)").text.strip()
            except AttributeError:
                logger.error("No description found for product %s", self.url)

            # Get category
            try:
                product_details["type"] = soup.select_one("div[data-testid='brandcrumb-wrapper'] > div > a:nth-last-child(3)").text.strip()
            except AttributeError:
                logger.error("No category found for product %s", self.url)

            # Get volume
            try:
                product_details["volume"] = soup.select_one("div[aria-live='assertive'] > div:nth-child(1) > span").text.strip()
            except AttributeError:
                logger.error("No volume found for product %s", self.url)

            # Get price before discount if available
            try:
                product_details["original_price"] = float(soup.select_one("div[data-testid='originalPriceLineThroughWrapper'] > span > span").text.strip())
            except AttributeError:
                product_details["original_price"] = None

        except Exception as e:
            logger.error("An error occurred: %s", e)
        
        return product_details

    def scrape_products_for_brand(self, brand: str):
        """Scrape all products for a specific brand on Notino"""
        product_containers = self.load_all_products_for_brand(brand)
        general_product_details = self.extract_general_product_details(product_containers)

        product_links = self.extract_product_links(product_containers)

        product_details = []
        for link in product_links:
            logger.info("Scraping product details for product %s", link)

            response = self.send_request(link)
            soup = self.parse_html(response)
            product_details.append(self.extract_product_details(soup))


    