# Project general description and thoughts on how to develop it.
## General description
The project is a Python scraper. Scraper description from the client:
"scraper should take all products data, starting from category, name, description, volume, price and price after discount. Photos if possible. Price check should be daily. Sites are following: douglas.lv, notino.lv, kristiana.lv,(all categories) save24.lv (for this site only perfume category). The results should be in xlxs file. Further scraping usage for context: ideally we would like to made price comparison in some tool (Excel or etc) and selected products extract them to our web shop."

## Project details

Scraping Environment: Since the scraper is expected to run on a virtual machine, the cloud environment (such as an EC2 instance) will need to handle long-running processes, possibly running multiple scrapers for different sites. This should be easy to manage as cloud VMs often allow for long-running scripts and cron jobs to ensure data extraction happens daily.

Website Structure and Complexity: The website appears to be modern and dynamic, likely relying on JavaScript to load product data. This means I might need to use a headless browser like Selenium or Playwright to fully render the page and extract product details since traditional methods (like requests and BeautifulSoup) might not work.

Product Quantity: With more than 10,000 items on each site, and multiple sites to scrape, I’ll need to consider how to optimize the scraping process. I might want to handle pagination smartly, ensuring efficient data extraction. For large-scale data like this, especially if the scraper needs to run daily, parallelizing the requests or scraping multiple categories/products concurrently will improve performance.

Price and Stock Status: As for the product listings without prices and showing "Drīz tirzniecībā!" (which likely means “coming soon” or “out of stock” in Latvian), I’ll still need to scrape and store these items. The scraper should also capture both prices (when available) and stock statuses, which will allow the client to track changes in availability over time.

Product Details: Client wants to scrape a range of details: category, name, description, volume, price, price after discount, and photos if possible. I've observed some additional details on the site, like short descriptions, properties (like tags), audience (gender), and long descriptions, which will enrich the data.

Performance: The main purpose is to scrape data to have it current, not specifically focused on high performance or speed. However, if the scraper runs daily, some performance tweaks might still help maintain efficiency (e.g., managing throttling and parallel requests).

Data Storage: although the client hasn't specified a precise storage format, it sounds like an Excel-compatible output would be ideal for price comparison and manual product selection for the webshop. This suggests mine solution should allow easy data filtering or extraction into CSV/XLSX.

Error Handling: My scraper needs to gracefully handle errors. In case of general failure, it should specify what went wrong. If an individual product can't be processed, it should be flagged with a "failed to fetch" status and logged, so the user knows how many products weren't scraped successfully.

Flexibility: The project should be flexible enough to scrape product data from multiple websites, even when their layouts differ. The separation of logic into individual modules for each site allows for easier maintenance and scalability. Whenever a new site needs to be added, you can simply create a new scraper module that adheres to the same interface without affecting existing scrapers.

## Example File Structure
```bash
product_scraper/
│
├── main.py                 # Entry point of the application
├── requirements.txt        # List of required libraries
├── config.py               # Configuration settings (e.g., URLs, headers)
│
├── scraper/                # Scraper module
│   ├── __init__.py         # Initialization for the scraper package
│   ├── base_scraper.py     # Base class for scraping logic
│   ├── douglas_product_scraper.py # Scraper for douglas.lv products
│   ├── notino_product_scraper.py # Scraper for notino.lv products
│   ├── kristiana_product_scraper.py # Scraper for kristiana.lv products
│   ├── save24_product_scraper.py # Scraper for save24.lv products
│   └── error_handler.py    # Error handling functions and logging
│
├── data/                   # Data module
│   ├── __init__.py         # Initialization for the data package
│   ├── data_extractor.py   # Functions for extracting product data
│   ├── storage.py          # Functions for storing data (e.g., CSV, Excel)
│   └── database.py         # Database handling functions (if using a database)
│
├── utils/                  # Utility functions
│   ├── __init__.py         # Initialization for the utils package
│   └── helpers.py          # Helper functions (e.g., data cleaning, formatting)
│
└── tests/                  # Tests for your application
    ├── __init__.py         # Initialization for the tests package
    ├── test_scraper.py     # Tests for the scraper module
    └── test_data.py        # Tests for the data module
```

### Main Modules and Their Relationships

1. **main.py**:
   The entry point of the application, which orchestrates the execution of the scraper and data handling modules. It may also configure the scheduler for running the scraper periodically. Also implements a dispatcher or factory method that decides which scraper to invoke based on user input or configuration. This can help streamline the process of scraping multiple sites.

2. **config.py**:
   Contains configuration settings like target URLs, request headers, and any other constants. This allows for easy adjustments without modifying core logic. Stores configurations for each site, including URLs, unique selectors, and other necessary parameters.

3. **scraper/**:
   This module houses the scraping logic:
   - base_scraper.py: A base class that contains common scraping methods and properties. Other scrapers can inherit from this class. Here defined common methods that are applicable to all scrapers, such as sending requests, handling headers, and common error handling. Provides abstract methods (or uses a template method pattern) that require the child classes to implement specific methods for extracting data (e.g., extract_product_details()).
   - {site_name}_product_scraper.py: Four files for each site, that ontains the implementation for scraping product details. This module will utilize the base_scraper.py for shared functionality. Each of these modules can inherit from a common BaseScraper class but implement their own parsing logic tailored to their respective HTML structure.
   - error_handler.py: Contains functions for logging errors and handling failed requests, which can be called from any scraper.

4. **data/**:
   This module handles data extraction and storage:
   - data_extractor.py: Functions that parse HTML and extract product data using selectors or other methods. Since the product data structure may vary from site to site, consider implementing a normalization layer in the data_extractor.py. This layer will standardize the extracted data into a uniform format, making it easier to store and process later. Regardless of how data is structured from each site, normalize them into a common dictionary format.
   - storage.py: Functions that save extracted data to a file format (e.g., CSV, Excel).
   - database.py: If you decide to use a database to store failed fetches or other information, this module will manage those operations.

5. **utils/**:
   This module provides utility functions that are used across the application, such as data cleaning or formatting functions that can be reused in different parts of the code.

6. **tests/**:
   Contains unit tests for your application. Each test file corresponds to the main modules, ensuring that your scraping and data handling logic is functioning correctly.

### Relationships
- The main.py file serves as the conductor, invoking methods from the scraper and data modules to perform its tasks.
- The scraper module directly interacts with the data module to pass extracted data for storage.
- The error_handler functions in the scraper module are utilized during scraping to log and manage failures, interacting with both the data module (to store failed products) and main.py (to inform the user).
- The utils module supports various other modules by providing shared functionality, reducing code duplication.
- The tests module verifies the functionality of the main modules, ensuring reliability and maintainability.
