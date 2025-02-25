import os
import csv
import json
import time
from urllib.parse import urljoin, urlparse
from utils import get_page_source, extract_text_bs, extract_links_bs
import config  # Import configuration

START_URL = config.START_URL
OUTPUT_FORMAT = config.OUTPUT_FORMAT
MAX_LINKS = 100  # Limit to 100 links

visited_urls = set()
data_store = []

def scrape_recursive(url):
    """Scrapes the given URL recursively until MAX_LINKS are fetched."""
    if url in visited_urls or len(visited_urls) >= MAX_LINKS:
        return
    
    print(f"Scraping: {url}")
    visited_urls.add(url)
    
    # Get page source
    page_source = get_page_source(url)
    if not page_source:
        return

    # Extract text & links
    text = extract_text_bs(page_source)
    links = extract_links_bs(page_source, url)

    # Store data
    data_store.append({"url": url, "text": text})

    # Stop if we reach the max limit
    if len(visited_urls) >= MAX_LINKS:
        return

    # Filter links - Keep only internal links
    base_domain = urlparse(START_URL).netloc
    links = [link for link in links if urlparse(link).netloc == base_domain]

    # Recursively scrape new links
    for link in links:
        if len(visited_urls) < MAX_LINKS:
            scrape_recursive(link)
        else:
            break

def save_data():
    """Saves scraped data to CSV or JSON."""
    if OUTPUT_FORMAT == "csv":
        with open("scraped_data.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["url", "text"])
            writer.writeheader()
            writer.writerows(data_store)
        print("✅ Data saved to scraped_data.csv")

    elif OUTPUT_FORMAT == "json":
        with open("scraped_data.json", "w", encoding="utf-8") as f:
            json.dump(data_store, f, indent=4)
        print("✅ Data saved to scraped_data.json")

# Run Scraper
scrape_recursive(START_URL)
save_data()
