import os
import csv
import json
import time
from urllib.parse import urljoin, urlparse
from utils import get_page_source, extract_clean_text, extract_links_bs
import config  # Import configuration

START_URL = config.START_URL
FILE_NAME = config.FILE_NAME
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

    # Extract cleaned text & structured data
    structured_data = extract_clean_text(page_source)

    # Store data in structured format
    data_store.append({
        "url": url,
        "title": structured_data["title"],
        "headings": structured_data["headings"],
        "paragraphs": structured_data["paragraphs"],
        "lists": structured_data["lists"]
    })

    # Stop if we reach the max limit
    if len(visited_urls) >= MAX_LINKS:
        return

    # Filter links - Keep only internal links
    base_domain = urlparse(START_URL).netloc
    links = [link for link in extract_links_bs(page_source, url) if urlparse(link).netloc == base_domain]

    # Recursively scrape new links
    for link in links:
        if len(visited_urls) < MAX_LINKS:
            scrape_recursive(link)
        else:
            break

def save_data(filename):
    """Saves scraped data to JSONL format."""
    file_name = f"{filename}.jsonl"
    print(f"Saving scraped data to {file_name}")
    
    with open(file_name, "w", encoding="utf-8") as f:
        for entry in data_store:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

    print(f"✅ Data saved to {file_name}")

# Run Scraper
scrape_recursive(START_URL)
save_data(FILE_NAME)
