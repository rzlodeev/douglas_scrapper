"""Scraper for Douglas product pages."""

from random import randint
from time import sleep

from bs4 import BeautifulSoup
import requests
from requests.exceptions import HTTPError

from scraper.base_scraper import BaseScraper, BaseListScraper
from scraper.exceptions import ScraperError

from logger_config import get_logger

logger = get_logger(__name__)


class DouglasProductListScraper(BaseListScraper):
    """A scraper for Douglas product list pages"""

    def __init__(self, base_url: str):
        logger.info("Initializing DouglasProductListScraper with base URL: %s", base_url)
        self.base_url = base_url
        super().__init__(base_url)

    def get_amount_of_pages(self) -> int:
        """Get the amount of pages in the product list"""
        try:
            response = self.send_request(self.base_url)
            soup = self.parse_html(response)
            amount_of_pages = soup.select_one("#products_listing > div.page_info.clearfix > div.paginator > a.page.last").text
            return int(amount_of_pages)
        except HTTPError as e:
            logger.error("Failed to get amount of pages: %s", e)
        except Exception as e:
            logger.error("An error occurred: %s", e)

    def get_page_url(self, page_number: int) -> str:
        """Construct the URL for a specific page number"""
        return f"{self.base_url}?&page={page_number}"

    def extract_product_links(self, soup: BeautifulSoup) -> list:
        """Extract product links from the HTML content of the product list page"""
        product_elements = soup.select("#products_listing > div.plist.list_wrp.clearfix > div.product_element")
        product_links = [element.find("a")["href"] for element in product_elements]
        return product_links
    
    def extract_brands(self, soup):
        return super().extract_brands(soup)
    
    def extract_general_product_details(self, soup: BeautifulSoup) -> dict:
        """Extract general product details from the HTML content of the product list page"""
        general_product_details = []
        try:
            product_elements = soup.select("#products_listing > div.plist.list_wrp.clearfix > div.product_element")
            for element in product_elements:
                product_details = {}

                # Get name, brand, type with skipping if not available
                # Get name
                try:
                    product_details["name"] = element.select_one("span.product_info_block > span.name").find(text=True, recursive=False).strip()
                except AttributeError:
                    logger.warning("Failed to extract name for product")

                # Get brand
                try:
                    product_details["brand"] = element.select_one("span.product_info_block > span.name > span.brand_caps").text.strip()
                except AttributeError:
                    logger.warning("Failed to extract brand for product: %s", product_details.get("name", "N/A"))

                # Get type
                try:
                    product_details["type"] = element.select_one("span.product_info_block > span.type").text.strip()
                except AttributeError:
                    logger.warning("Failed to extract type for product: %s", product_details.get("name", "N/A"))

                # Get price, in stock or mark as not available
                try:
                    price_text = element.select_one("span.product_info_block > span.price > span.now").text.strip()
                    try:
                        product_details["price"] = float(''.join(c for c in price_text if c.isdigit() or c == '.'))
                        product_details["in_stock"] = True
                    except ValueError:
                        product_details["price"] = price_text
                        product_details["in_stock"] = False
                except AttributeError:
                    logger.warning("Failed to extract price for product: %s", product_details["name"])

                # Get volume or pcs in packing
                try:
                    volume_text = element.select_one("span.product_info_block > span.volume").text.strip()
                    product_details["volume_or_pcs"] = volume_text
                except AttributeError:
                    pass
                
                # Check if there is old price
                try:
                    old_price_element = element.select_one("span.product_info_block > span.price > span.old_price")
                    if old_price_element:
                        product_details["old_price"] = float(old_price_element.text.strip().replace("€", "").replace(",", "."))
                except AttributeError:
                    pass

                general_product_details.append(product_details)
        except AttributeError:
            logger.warning("Failed to extract general product details")
        return general_product_details

    def scrape_product_list(self, page_number: int) -> list:
        """Scrape the product list from a specific page number"""
        page_url = self.get_page_url(page_number)
        logger.info("Scraping product list from page: %s", page_url)
        try:
            response = self.send_request(page_url)

            soup = self.parse_html(response)

            product_links = self.extract_product_links(soup)

            general_product_details = self.extract_general_product_details(soup)
            logger.info("Extracted general product details from page: %s", page_url)
            products = []
            for link in product_links:
                sleep(randint(1, 3))  # Random sleep to avoid 429 error

                if "item" in link:
                    logger.info("Scraping product %s", link)
                else:
                    logger.info("Scraping product %s", link)

                has_multiple_prices = general_product_details[product_links.index(link)].get("price") == "MULTIPLE_VALUES"

                product_scraper = DouglasProductScraper(link, has_multiple_prices)
                product_details = product_scraper.scrape()

                products.append(product_details)

            # Update the product details with the general product details
            for i, product in enumerate(products):
                product.update(general_product_details[i])

            return products
        except HTTPError as e:
            raise ScraperError(f"HTTP error occurred: {e}")
        except Exception as e:
            raise ScraperError(f"An error occurred: {e}")


class DouglasProductScraper(BaseScraper):
    """A scraper for Douglas product page"""

    def __init__(self, url: str, has_multiple_prices: bool = False):
        self.has_multiple_prices = has_multiple_prices
        super().__init__(url)

    def extract_product_details(self, soup: BeautifulSoup) -> dict:
        """Extract product details from the HTML content
        Args:
            soup (BeautifulSoup): The parsed HTML content
        Returns:
            dict: A dictionary containing the product details
        """
        product_details = {}
        
        # Update with tag_name
        try:
            product_details["tag_name"] = soup.select_one("#product_info1 > div.short_description > div:nth-child(1) > span.k").text.strip()
        except AttributeError:
            logger.warning("Failed to extract tag name for product: %s", self.url)

        # Update with gender
        try:
            product_details["gender"] = soup.select_one("#product_info1 > div.short_description > div:nth-child(2) > span.v").text.strip()
        except AttributeError:
            logger.warning("Failed to extract gender for product: %s", self.url)

        # Update with about
        try:
            product_details["about"] = soup.select_one("#tab_about > div > div > div > p:nth-child(4)").text.strip()
        except AttributeError:
            logger.warning("Failed to extract about for product: %s", self.url)

        # Update with tag_list
        try:
            product_details["tag_list"] = soup.select_one("#product_info1 > div.short_description > div:nth-child(1) > span.v ").text.strip()
        except AttributeError:
            logger.warning("Failed to extract tag list for product: %s", self.url)
        
        return product_details

    def scrape(self) -> dict:
        """Scrape the product details from the product web page
        Returns:
            dict: A dictionary containing the product details
        """
        try:
            response = self.send_request(self.url)
            soup = self.parse_html(response)
            product_details = self.extract_product_details(soup)
            return product_details
        except ScraperError as e:
            raise ScraperError(f"Failed to scrape product details: {e}")
        except Exception as e:
            raise ScraperError(f"An error occurred: {e}")