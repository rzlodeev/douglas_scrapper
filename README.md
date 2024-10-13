# Scraper

## Project Layout
This project is a web scraper designed to extract data from e-commerce websites. (Currently douglas.lv).
Project runs in a docker container.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rzlodeev/douglas_scrapper.git
cd douglas_scrapper
```

2. Build the docker image:
```bash
docker build -t douglas_scrapper .
```

3. Run the docker container:
```bash
docker run -it douglas_scrapper
```

## Usage

1. Run the scraper:
```bash
python3 main.py
```

(optional) You can specify the number of pages to scrape:
```bash
python3 main.py --pages 2
```

2. The results will be saved in the products.xlsx file.



