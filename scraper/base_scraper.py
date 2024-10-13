"""A base class that contains common scraping methods and properties. 
Other scrapers can inherit from this class. 
Common methods that are applicable to all scrapers, such as sending requests, 
handling headers, and common error handling are definde here. 
Provides abstract methods (or uses a template method pattern) 
that require the child classes to implement specific methods 
for extracting data (e.g., extract_product_details())."""

from abc import ABC, abstractmethod
from time import sleep
from random import randint

import requests
from requests.exceptions import HTTPError

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from scraper.exceptions import ScraperError


class BaseListScraper(ABC):
    """A base class for scraping product list page
    Attributes:
        url (str): The URL of the website to scrape
        headers (dict): The headers to be used in the request
        user_agent (str): The user agent to be used in the request
    """
    
    def __init__(self, url: str):
        self.base_url = url
        self.headers = {
            "User-Agent": self.user_agent
        }

    @property
    def user_agent(self) -> str:
        """Generate a random user agent"""
        return UserAgent().random

    def send_request(self, url: str) -> requests.models.Response:
        """Send a request to the given URL and return the response
        Args:
            url (str): The URL to send the request to
        Returns:
            requests.models.Response: The response object
        Raises:
            ScraperError: If the request fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response
        except HTTPError as e:
            raise ScraperError(f"Failed to send request: {e}")

    def parse_html(self, response: requests.models.Response) -> BeautifulSoup:
        """Parse the HTML content of a response object
        Args:
            response (requests.models.Response): The response object
        Returns:
            BeautifulSoup: The parsed HTML content
        """
        return BeautifulSoup(response.content, "html.parser")

    @abstractmethod
    def extract_product_links(self, soup: BeautifulSoup) -> list:
        """Extract product links from the parsed HTML content from a single page
        Args:
            soup (BeautifulSoup): The parsed HTML content
        Returns:
            list: A list of product links
        """

    @abstractmethod
    def extract_brands(self, soup: BeautifulSoup) -> list:
        """Extract brands from the parsed HTML content
        for case, where all brands are listed on the single page (Notino)
        Args:
            soup (BeautifulSoup): The parsed HTML content
        Returns:
            list: A list of brands
        """

    def scrape(self) -> list:
        """Scrape the website and extract product links
        Returns:
            list: A list of product links
        """
        try:
            response = self.send_request(self.url)
            soup = self.parse_html(response)
            return self.extract_product_links(soup)
        except ScraperError as e:
            print(e)
            return []
        finally:
            sleep(randint(1, 3))


class BaseScraper(ABC):
    """A base class for scraping product page
    Attributes:
        url (str): The URL of the website to scrape
        headers (dict): The headers to be used in the request
        user_agent (str): The user agent to be used in the request
    """
    
    def __init__(self, url: str):
        self.url = url
        self.headers = {
            "User-Agent": self.user_agent
        }

    @property
    def user_agent(self) -> str:
        """Generate a random user agent"""
        return UserAgent().random

    def send_request(self, url: str) -> requests.models.Response:
        """Send a request to the given URL and return the response
        Args:
            url (str): The URL to send the request to
        Returns:
            requests.models.Response: The response object
        Raises:
            ScraperError: If the request fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response
        except HTTPError as e:
            raise ScraperError(f"Failed to send request: {e}")

    def parse_html(self, response: requests.models.Response) -> BeautifulSoup:
        """Parse the HTML content of a response object
        Args:
            response (requests.models.Response): The response object
        Returns:
            BeautifulSoup: The parsed HTML content
        """
        return BeautifulSoup(response.content, "html.parser")

    @abstractmethod
    def extract_product_details(self, soup: BeautifulSoup) -> dict:
        """Extract product details from the parsed HTML content
        Args:
            soup (BeautifulSoup): The parsed HTML content
        Returns:
            dict: A dictionary containing the product details
        """

    def scrape(self) -> dict:
        """Scrape the website and extract product details
        Returns:
            dict: A dictionary containing the product details
        """
        try:
            response = self.send_request(self.url)
            soup = self.parse_html(response)
            return self.extract_product_details(soup)
        except ScraperError as e:
            print(e)
            return {}
        finally:
            sleep(randint(1, 3))
        

