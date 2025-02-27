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

# Extract clean text and structure it
def extract_clean_text(page_source):
    soup = BeautifulSoup(page_source, "html.parser")

    # Remove unwanted elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
        tag.decompose()

    # Handle missing title
    title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"

    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 30]
    
    lists = []
    for ul in soup.find_all("ul"):
        items = [li.get_text(strip=True) for li in ul.find_all("li")]
        if items:
            lists.append(items)

    return {
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists
    }

# Extract links using BeautifulSoup
def extract_links_bs(page_source, base_url):
    soup = BeautifulSoup(page_source, "html.parser")
    media_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"}
    
    links = set()
    for a in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a["href"])
        if not any(full_url.lower().endswith(ext) for ext in media_extensions):
            links.add(full_url)
    
    return links
