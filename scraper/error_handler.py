"""Contains functions for logging errors and handling failed requests, 
which can be called from any scraper."""

from time import sleep
from random import randint
import logging

from bs4 import BeautifulSoup

import requests
from requests.exceptions import HTTPError

from scraper.exceptions import ScraperError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_error(error: str):
    """Log an error message
    Args:
        error (str): The error message to log
    """
    logger.error(error)

def handle_request_error(url: str, headers: dict) -> requests.models.Response:
    """Handle a failed request by retrying with a delay
    Args:
        url (str): The URL to send the request to
        headers (dict): The headers to be used in the request
    Returns:
        requests.models.Response: The response object
    Raises:
        ScraperError: If the request fails after multiple retries
    """
    retries = 3
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except HTTPError as e:
            log_error(f"Failed to send request: {e}")
            if i < retries - 1:
                delay = randint(1, 5)
                log_error(f"Retrying in {delay} seconds...")
                sleep(delay)
    raise ScraperError("Failed to send request after multiple retries")

def handle_parse_error(response: requests.models.Response) -> BeautifulSoup:
    """Handle a failed parse operation by retrying with a delay
    Args:
        response (requests.models.Response): The response object to parse
    Returns:
        BeautifulSoup: The parsed HTML content
    """
    retries = 3
    for i in range(retries):
        try:
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            log_error(f"Failed to parse HTML content: {e}")
            if i < retries - 1:
                delay = randint(1, 5)
                log_error(f"Retrying in {delay} seconds...")
                sleep(delay)
    raise ScraperError("Failed to parse HTML content after multiple retries")

def handle_scrape_error(url: str, headers: dict, extract_product_details: callable) -> dict:
    """Handle a failed scrape operation by retrying with a delay
    Args:
        url (str): The URL to scrape
        headers (dict): The headers to be used in the request
        extract_product_details (callable): The function to extract product details
    Returns:
        dict: A dictionary containing the product details
    """
    retries = 3
    for i in range(retries):
        try:
            response = handle_request_error(url, headers)
            soup = handle_parse_error(response)
            return extract_product_details(soup)
        except ScraperError as e:
            log_error(e)
            if i < retries - 1:
                delay = randint(1, 5)
                log_error(f"Retrying in {delay} seconds...")
                sleep(delay)
    return {}
