from bs4 import BeautifulSoup
import requests
import json

class Scraper:
    """Handles web scraping operations."""
    def __init__(self, url, depth=1):
        self.url = url
        self.depth = depth
        self.visited_urls = set()
        self.data_collection = {}
    
    def fetch_html(self, url):
        """Fetches and parses the HTML content of a given URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def extract_data(self, soup, tag):
        """Extracts elements like headings, paragraphs, and divs."""
        elements = soup.find_all(tag)
        data = {}
        
        for index, elem in enumerate(elements):
            key = f"{tag}-{index + 1}"
            data[key] = {
                "class": " ".join(elem.get("class", [])) if elem.get("class") else "none",
                "id": elem.get("id") if elem.get("id") else "none",
                "text": elem.get_text(strip=True),
                "links": [a["href"] for a in elem.find_all("a", href=True)],
            }
        return data

    def extract_links(self, soup):
        """Extracts all links present in the webpage."""
        links_data = {}
        links = soup.find_all("a", href=True)

        for index, a in enumerate(links):
            key = f"a-{index + 1}"
            links_data[key] = {
                "class": " ".join(a.get("class", [])) if a.get("class") else "none",
                "id": a.get("id") if a.get("id") else "none",
                "href": a.get("href"),
                "text": a.get_text(strip=True),
            }
        return links_data

    def scrape(self):
        """Starts the scraping process."""
        def crawl(url, depth):
            if depth > self.depth or url in self.visited_urls:
                return
            self.visited_urls.add(url)
            
            print(f"Scraping: {url} (Depth: {depth})")
            soup = self.fetch_html(url)
            if not soup:
                return
            
            self.data_collection[url] = {
                "headings": self.extract_data(soup, "h1"),
                "paragraphs": self.extract_data(soup, "p"),
                "divs": self.extract_data(soup, "div"),
                "links": self.extract_links(soup),
            }
            
            for link in self.data_collection[url]["links"].values():
                abs_link = link["href"]
                if abs_link.startswith("/"):
                    abs_link = self.url + abs_link
                if abs_link.startswith("http"):
                    crawl(abs_link, depth + 1)
        
        crawl(self.url, 1)
        return self.data_collection


class ChatBot:
    """Chatbot that processes user queries using scraped data."""
    def __init__(self, data):
        self.data = data

    def search_link_data(self, found_results):
        """If links are found, scrape them for more relevant data."""
        extra_data = {}
        for result in found_results:
            if "http" in result["text"]:
                link = result["text"].split()[0]
                print(f"🔍 Scraping more data from: {link}")
                scraper = Scraper(link, depth=1)
                extra_data[link] = scraper.scrape()
        return extra_data
    
    def connect_data(self, found_results, extra_data):
        """Combine found data and additional scraped data into a structured response."""
        response = "Here’s what I found:\n"
        for result in found_results[:3]:
            response += f"\n🔹 **{result['section']}** from {result['url']}:\n{result['text']}\n"
        
        if extra_data:
            response += "\n🔍 I also found more details from the linked pages:\n"
            for link, data in extra_data.items():
                response += f"\n🔗 **{link}**:\n"
                for section, elements in data.items():
                    for element_id, content in elements.items():
                        response += f"- {content.get('text', '')[:150]}...\n"
        
        return response
    
    def chat(self, prompt):
        """Finds relevant information based on the prompt keywords."""
        keywords = prompt.lower().split()
        found_results = []
        
        for url, page_data in self.data.items():
            for section, elements in page_data.items():
                for element_id, content in elements.items():
                    text = content.get("text", "").lower()
                    if any(keyword in text for keyword in keywords):
                        found_results.append({
                            "url": url,
                            "section": section,
                            "text": content["text"],
                        })
        
        if found_results:
            extra_data = self.search_link_data(found_results)
            return self.connect_data(found_results, extra_data)
        else:
            return "Sorry, I couldn't find anything related."


if __name__ == "__main__":
    website_url = "https://www.google.com"
    depth_level = 2  # Controls how deep we scrape
    
    scraper = Scraper(website_url, depth_level)
    scraped_data = scraper.scrape()
    
    chatbot = ChatBot(scraped_data)
    user_query = "hey can you give me the privacy policy"
    response = chatbot.chat(user_query)
    
    print(response)
