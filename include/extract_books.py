import pandas
import requests
from bs4 import BeautifulSoup
import os
import csv
import logging
from datetime import datetime
import time
from pathlib import Path

class BookScraper:
    def __init__(self, base_url="https://books.toscrape.com/catalogue/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.output_dir = os.path.join(project_root, "data", "raw")
        os.makedirs(self.output_dir, exist_ok=True)

    def get_soup(self, url):
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None
    
    def scrape_book_data(self):
        page = 1
        all_books = []
        while True:
            url = f"{self.base_url}page-{page}.html"
            logging.info(f"Scraping page: {url}")
            soup = self.get_soup(url)
            if soup is None:
                break

            books = soup.find_all('article', class_='product_pod')
            if books is None or len(books) == 0:
                logging.info("No more books found, ending scrape.")
                break

            for book in books:
                title = book.h3.a["title"]
                price = book.find('p', class_='price_color').get_text()
                availability = book.find('p', class_='instock availability').get_text(strip=True)
                rating = book.find('p', class_='star-rating')['class'][1]
                product_page_url = book.h3.a.get('href')

                book_info = {
                    "title": title,
                    "price": price,
                    "availability": availability,
                    "rating": rating,
                    "product_page_url": f"{self.base_url}{product_page_url}"
                }
                all_books.append(book_info)

            page += 1
            time.sleep(1)

        logging.info(f"Scraped {len(all_books)} books in total.")
        return all_books

    def write_to_csv(self, data):
        if not data:
            logging.warning("No data to write to CSV.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"books_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        logging.info(f"Data written to {filepath}")
        return filepath

def extract_books():
    scraper = BookScraper()
    logging.info("Starting book data extraction...")

    data = scraper.scrape_book_data()
    csv_file = scraper.write_to_csv(data)

    logging.info("Book data extraction completed.")
    return csv_file

if __name__ == "__main__":
    extract_books()