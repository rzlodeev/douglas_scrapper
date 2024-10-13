from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WebDriver:
    """A class for handling the WebDriver
    Attributes:
        driver (webdriver.Firefox): The WebDriver object
    """
    
    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
    
    def get(self, url: str):
        """Open the given URL in the WebDriver
        Args:
            url (str): The URL to open
        """
        return self.driver.get(url)
    
    def find_element(self, by: str, value: str):
        """Find an element in the WebDriver
        Args:
            by (str): The method to use for finding the element
            value (str): The value to search for
        Returns:
            selenium.webdriver.remote.webelement.WebElement: The element object
        """
        return self.driver.find_element(by, value)
    
    def wait_for_element(self, by: str, value: str, timeout: int = 10):
        """Wait for an element to be present in the WebDriver
        Args:
            by (str): The method to use for finding the element
            value (str): The value to search for
            timeout (int): The maximum time to wait for the element
        Returns:
            selenium.webdriver.remote.webelement.WebElement: The element object
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def get_page_source(self):
        """Get the page source from the WebDriver
        Returns:
            str: The page source
        """
        return self.driver.page_source
    
    def close(self):
        """Close the WebDriver"""
        self.driver.quit()