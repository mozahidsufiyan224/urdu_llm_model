import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configuration
BASE_URL = "https://www.bbc.com/urdu"
OUTPUT_DIR = "urdu_articles"
MAX_ARTICLES = 50  # Reduce this for testing, increase later
DELAY = 3  # Be polite with delays

def sanitize_filename(title):
    """Make safe filenames"""
    return "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in title)[:150]

def scrape_bbc_urdu():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    article_count = 0
    page_url = BASE_URL

    while article_count < MAX_ARTICLES:
        try:
            print(f"Fetching: {page_url}")
            response = session.get(page_url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # New BBC Urdu article link pattern (updated 2023)
            articles = soup.find_all('a', href=lambda href: href and '/urdu/articles/' in href)
            
            for article in articles:
                if article_count >= MAX_ARTICLES:
                    break

                article_url = urljoin(BASE_URL, article['href'])
                try:
                    print(f"Scraping {article_count+1}: {article_url}")
                    article_resp = session.get(article_url)
                    article_resp.encoding = 'utf-8'
                    article_soup = BeautifulSoup(article_resp.text, 'html.parser')

                    # Extract metadata
                    title = article_soup.find('h1', {'id': 'content'})
                    if not title:
                        continue
                    title = title.get_text(strip=True)

                    # Get category from breadcrumbs
                    category = "general"
                    breadcrumb = article_soup.find('div', class_='ssrcss-1rhesle')
                    if breadcrumb:
                        links = breadcrumb.find_all('a')
                        if len(links) > 1:
                            category = links[-1].get_text(strip=True).lower()

                    # Get article content
                    content = ""
                    body = article_soup.find('main')
                    if body:
                        paragraphs = body.find_all('p')
                        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

                    if not content:
                        continue

                    # Save to file
                    category_dir = os.path.join(OUTPUT_DIR, category)
                    os.makedirs(category_dir, exist_ok=True)
                    
                    filename = f"{article_count}_{sanitize_filename(title)}.txt"
                    filepath = os.path.join(category_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"Title: {title}\n")
                        f.write(f"URL: {article_url}\n")
                        f.write(f"Category: {category}\n\n")
                        f.write(content)

                    article_count += 1
                    time.sleep(DELAY)

                except Exception as e:
                    print(f"Error scraping article: {e}")
                    continue

            # Find next page (if available)
            next_page = soup.find('a', {'aria-label': 'Next'})
            if not next_page:
                break
            page_url = urljoin(BASE_URL, next_page['href'])

        except Exception as e:
            print(f"Error fetching page: {e}")
            break

    print(f"Done! Saved {article_count} articles")

if __name__ == "__main__":
    scrape_bbc_urdu()