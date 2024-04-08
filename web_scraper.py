import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque

def scrape_website(url, base_url):
    scraped_data = []
    queue = deque([url])
    visited = set()

    while queue:
        current_url = queue.popleft()

        if current_url in visited:
            continue

        visited.add(current_url)

        try:
            response = requests.get(current_url)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract data from the page
            data = extract_data(soup)
            scraped_data.append((current_url, data))

            # Find all links on the page
            links = extract_links(soup, base_url)

            # Add new links to the queue
            for link in links:
                if link not in visited:
                    queue.append(link)

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {current_url}: {e}")

    return scraped_data

def extract_data(soup):
    # This function should extract the desired data from the HTML
    # using BeautifulSoup. You'll need to modify it based on your
    # requirements.
    data = soup.get_text()
    return data

def extract_links(soup, base_url):
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
    return links

def main():
    base_url = "https://www.iitbbs.ac.in/"
    start_url = "https://www.iitbbs.ac.in/"

    scraped_data = scrape_website(start_url, base_url)

    # Process or save the scraped data as needed
    with open("scraped_data.txt", "w") as f:
        for url, data in scraped_data:
            f.write(f"URL: {url}\n")
            f.write(f"Data: {data}\n")
            f.write("-" * 80 + "\n")

if __name__ == "__main__":
    main()