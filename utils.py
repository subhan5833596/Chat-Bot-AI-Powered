import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import config  # Import configuration

# Detect if a page needs Selenium
def needs_selenium(url):
    return any(tag in url for tag in ["javascript", "dynamic", "ajax"])

# Get page source (Auto-detect if Selenium is needed)
def get_page_source(url):
    try:
        if needs_selenium(url):
            options = Options()
            if config.HEADLESS_MODE:
                options.add_argument("--headless")
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            page_source = driver.page_source
            driver.quit()
        else:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            page_source = response.text

        return page_source

    except Exception as e:
        print(f"❌ Error loading {url}: {e}")
        return None

# Extract text using BeautifulSoup
def extract_text_bs(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    return soup.get_text(separator=" ", strip=True)

# Extract links using BeautifulSoup
def extract_links_bs(page_source, base_url):
    soup = BeautifulSoup(page_source, "html.parser")
    links = {urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)}
    return links
