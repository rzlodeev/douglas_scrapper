class ScraperError(Exception):
    """Base class for scraper error
    Attributes:
        message (str): The error message
    """
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
    
    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
    

class ScraperRequestError(ScraperError):
    """Exception raised for errors in the request
    Attributes:
        message (str): The error message
    """
    
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
    
class ScraperParseError(ScraperError):
    """Exception raised for errors in the parse operation
    Attributes:
        message (str): The error message
    """
    
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
    

class ScraperExtractError(ScraperError):
    """Exception raised for errors in the extraction operation
    Attributes:
        message (str): The error message
    """
    
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
    
class ScraperScrapeError(ScraperError):
    """Exception raised for errors in the scrape operation
    Attributes:
        message (str): The error message
    """
    
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"
    
class ScraperHandlerError(ScraperError):
    """Exception raised for errors in the error handling
    Attributes:
        message (str): The error message
    """
    
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return self.message
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.message})"