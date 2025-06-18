import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from datetime import datetime
import csv

# Configure settings
BASE_URL = "https://ncpulblog.blogspot.com/2022/"
OUTPUT_FOLDER = "ncpul_articles"
DELAY_BETWEEN_REQUESTS = 2  # seconds
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def setup_folders():
    """Create necessary folders for output"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    return OUTPUT_FOLDER

def sanitize_filename(title):
    """Create a safe filename from article title"""
    keep_chars = (' ', '.', '_', '-')
    return "".join(c if c.isalnum() or c in keep_chars else "_" for c in title).strip()

def extract_article_data(article_div):
    """Extract relevant data from article HTML"""
    data = {}
    
    # Title and URL
    title_tag = article_div.find('h3', class_='post-title')
    if title_tag:
        data['title'] = title_tag.get_text(strip=True)
        link = title_tag.find('a')
        if link:
            data['url'] = link['href']
    
    # Date
    date_tag = article_div.find('span', class_='post-timestamp')
    if date_tag:
        data['date'] = date_tag.get_text(strip=True)
    
    # Author
    author_tag = article_div.find('span', class_='post-author')
    if author_tag:
        data['author'] = author_tag.get_text(strip=True)
    
    # Content
    content_div = article_div.find('div', class_='post-body')
    if content_div:
        data['content'] = content_div.get_text(strip=True)
    
    return data

def save_article(article_data, folder_path):
    """Save individual article to file"""
    if not article_data.get('title') or not article_data.get('content'):
        return None
    
    # Create filename
    safe_title = sanitize_filename(article_data['title'])
    date_part = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{date_part}_{safe_title[:50]}.txt"
    filepath = os.path.join(folder_path, filename)
    
    # Write content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Title: {article_data['title']}\n\n")
        if 'date' in article_data:
            f.write(f"Published: {article_data['date']}\n")
        if 'author' in article_data:
            f.write(f"Author: {article_data['author']}\n")
        if 'url' in article_data:
            f.write(f"Original URL: {article_data['url']}\n")
        f.write("\n" + "="*50 + "\n\n")
        f.write(article_data['content'])
    
    return filepath

def scrape_articles(start_url, max_pages=5):
    """Main scraping function"""
    output_folder = setup_folders()
    all_articles = []
    current_url = start_url
    page_count = 0
    
    while current_url and page_count < max_pages:
        print(f"Scraping page {page_count + 1}: {current_url}")
        
        try:
            # Fetch page
            response = requests.get(current_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all articles
            articles = soup.find_all('div', class_='post')
            
            for article in articles:
                article_data = extract_article_data(article)
                if article_data.get('content'):
                    filepath = save_article(article_data, output_folder)
                    if filepath:
                        # Add to CSV data (without content)
                        csv_data = {
                            'title': article_data.get('title', ''),
                            'date': article_data.get('date', ''),
                            'author': article_data.get('author', ''),
                            'url': article_data.get('url', ''),
                            'file_path': filepath
                        }
                        all_articles.append(csv_data)
            
            # Find next page
            next_link = soup.find('a', class_='blog-pager-older-link')
            current_url = urljoin(current_url, next_link['href']) if next_link else None
            page_count += 1
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            print(f"Error processing page: {e}")
            break
    
    return all_articles

def save_to_csv(articles, folder_path):
    """Save metadata to CSV file"""
    if not articles:
        print("No articles to save to CSV")
        return
    
    csv_path = os.path.join(folder_path, 'articles_metadata.csv')
    fieldnames = ['title', 'date', 'author', 'url', 'file_path']
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"Saved metadata for {len(articles)} articles to {csv_path}")

if __name__ == "__main__":
    print("Starting NCPUL blog scraper...")
    scraped_articles = scrape_articles(BASE_URL, max_pages=5)
    save_to_csv(scraped_articles, OUTPUT_FOLDER)
    
    print("\nScraping complete! Summary:")
    print(f"- Total articles scraped: {len(scraped_articles)}")
    print(f"- Output folder: {os.path.abspath(OUTPUT_FOLDER)}")
    if scraped_articles:
        print("\nSample articles:")
        for article in scraped_articles[:3]:
            print(f"  - {article['title']} ({article.get('date', 'no date')})")
            print(f"    Saved to: {article['file_path']}")