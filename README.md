# Scraper

## Project Layout
This project is a web scraper designed to extract data from e-commerce websites. (Currently douglas.lv).
Project runs in a docker container.

## Installation


### Prerequisites

Make sure you have the following installed on your system:

- Python
- Git


1. Clone the repository:
```bash
git clone https://github.com/rzlodeev/douglas_scrapper.git
cd douglas_scrapper
```


2. Configure the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. 

Run the scraper:

```bash
python main.py
```

Optionally, you can scrape site catalog partitially, specifying number of first pages to scrap.

```bash
python main.py -p 2
```

This will scrap only first 2 pages of the catalog (40 products)

You will see the progress in the cmd output.

After finishing files will be saved in the products.xlsx
