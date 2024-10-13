import pandas as pd
from scraper.douglas_product_scraper import DouglasProductListScraper
import os
import xlsxwriter
from utils.webdriver import WebDriver
import argparse

web_driver = WebDriver()

def scrape_douglas_products(amount_of_pages):
    """Scrape Douglas product list and save to Excel file"""
    # Initialize the scraper
    scraper = DouglasProductListScraper("https://www.douglas.lv/lv/katalogs/")

    return scraper.scrape_product_list(amount_of_pages)

def convert_price(value):
    try:
        return f"{float(value):.2f}"
    except ValueError:
        return value

def save_products_to_excel(products):
    """Save a list of products to an Excel file"""
    # Define the column mapping and order
    column_mapping = {
        "brand": ("Brand", 30),
        "name": ("Product name", 35),
        "price": ("Price (EUR)", 10),
        "type": ("Type", 10),
        "volume_or_pcs": ("Product volume or pcs", 15),
        "in_stock": ("Is in stock", 10),
        "tag_name": ("Tag name", 25),
        "tag_list": ("Tags", 30),
        "about": ("About", 50)
    }

    # Check for column existence and rename
    df = pd.DataFrame(products)

    # Convert the price to float where applicable
    if 'price' in df.columns:
        df['price'] = df['price'].apply(convert_price)

    for col in df.columns:
        if col in column_mapping:
            df.rename(columns={col: column_mapping[col][0]}, inplace=True)

    # Save the DataFrame to an Excel file
    file_path = "products.xlsx"
    if os.path.exists(file_path):
        os.remove(file_path)

    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    # Set column widths and format
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    for col, (header, width) in column_mapping.items():
        if header in df.columns:
            col_idx = df.columns.get_loc(header)
            worksheet.set_column(col_idx, col_idx, width)

    # Apply conditional formatting for "Is in stock" column
    if "Is in stock" in df.columns:
        col_idx = df.columns.get_loc("Is in stock")
        worksheet.conditional_format(1, col_idx, len(df), col_idx, {
            'type': 'cell',
            'criteria': '==',
            'value': True,
            'format': workbook.add_format({'bg_color': 'green'})
        })
        worksheet.conditional_format(1, col_idx, len(df), col_idx, {
            'type': 'cell',
            'criteria': '==',
            'value': False,
            'format': workbook.add_format({'bg_color': 'red'})
        })

    writer.close()


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Scrape Douglas products and save to Excel file.")
    parser.add_argument('-p', '--pages', type=int, default=None, help="Number of pages to scrape. If not provided, scrape all pages.")

    args = parser.parse_args()
    amount_of_pages = args.pages

    # Process the Douglas products
    print("Getting amount of pages to scrape...")
    scraper = DouglasProductListScraper("https://www.douglas.lv/lv/katalogs/")
    if not amount_of_pages:
        amount_of_pages = scraper.get_amount_of_pages()

    for page_number in range(1, amount_of_pages + 1):
        print(f"Scraping page {page_number} from {amount_of_pages}")
        products = scraper.scrape_product_list(page_number)

    print("Saving results to Excel file...")
    save_products_to_excel(products)


if __name__ == "__main__":
    main()
