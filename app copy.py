import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from datetime import datetime, timedelta
import csv
import re

# Configure settings
BASE_URL = "https://ncpulblog.blogspot.com/"
OUTPUT_ROOT = "ncpul_articles_archive"
DELAY_BETWEEN_REQUESTS = 2  # seconds
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def setup_folders(base_path):
    """Create necessary folders for output"""
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    return base_path

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

def save_article(article_data, year, month):
    """Save individual article to file with year/month organization"""
    if not article_data.get('title') or not article_data.get('content'):
        return None
    
    # Create year and month folders
    year_folder = os.path.join(OUTPUT_ROOT, str(year))
    month_folder = os.path.join(year_folder, f"{month:02d}")
    
    for folder in [year_folder, month_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    # Create filename
    safe_title = sanitize_filename(article_data['title'])
    date_part = ""
    
    # Try to extract date from article data
    if 'date' in article_data:
        try:
            # Try to parse different date formats
            date_str = article_data['date']
            if 'at' in date_str:
                date_obj = datetime.strptime(date_str.split('at')[0].strip(), '%B %d, %Y')
            else:
                date_obj = datetime.strptime(date_str, '%B %d, %Y')
            date_part = date_obj.strftime('%Y%m%d_')
        except ValueError:
            pass
    
    if not date_part:
        date_part = datetime.now().strftime('%Y%m%d_%H%M%S_')
    
    filename = f"{date_part}{safe_title[:50]}.txt"
    filepath = os.path.join(month_folder, filename)
    
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

def get_year_month_urls(start_year, end_year):
    """Generate month URLs for all 12 months from start_year to end_year"""
    urls = []
    
    for year in range(start_year, end_year - 1, -1):  # From start_year down to end_year
        for month in range(12, 0, -1):  # From December (12) to January (1)
            # Blogspot URL format: /YYYY/MM/
            month_url = urljoin(BASE_URL, f"{year}/{month}/")
            urls.append((month_url, year, month))
    
    return urls

def scrape_month(url, year, month):
    """Scrape all articles from a specific month page"""
    articles = []
    current_url = url
    page_count = 0
    max_pages_per_month = 10  # Safety limit
    
    print(f"\nScraping {year}-{month:02d}: {current_url}")
    
    while current_url and page_count < max_pages_per_month:
        print(f"  Page {page_count + 1}")
        
        try:
            # Fetch page
            response = requests.get(current_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all articles
            article_divs = soup.find_all('div', class_='post')
            
            for article in article_divs:
                article_data = extract_article_data(article)
                if article_data.get('content'):
                    filepath = save_article(article_data, year, month)
                    if filepath:
                        # Add to CSV data (without content)
                        csv_data = {
                            'title': article_data.get('title', ''),
                            'date': article_data.get('date', ''),
                            'author': article_data.get('author', ''),
                            'url': article_data.get('url', ''),
                            'file_path': filepath,
                            'year': year,
                            'month': month
                        }
                        articles.append(csv_data)
            
            # Find next page (for paginated months)
            next_link = soup.find('a', class_='blog-pager-older-link')
            current_url = urljoin(current_url, next_link['href']) if next_link else None
            page_count += 1
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
            break
        except Exception as e:
            print(f"  Error processing page: {e}")
            break
    
    return articles

def save_to_csv(articles, folder_path):
    """Save metadata to CSV file"""
    if not articles:
        print("No articles to save to CSV")
        return
    
    csv_path = os.path.join(folder_path, 'articles_metadata.csv')
    fieldnames = ['title', 'date', 'author', 'url', 'file_path', 'year', 'month']
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(articles)
    
    print(f"\nSaved metadata for {len(articles)} articles to {csv_path}")

def main():
    print("Starting NCPUL blog archive scraper...")
    
    # Setup folders
    setup_folders(OUTPUT_ROOT)
    
    # Generate URLs for all months from 2025 down to 2015
    month_urls = get_year_month_urls(2025, 2015)
    
    all_articles = []
    total_articles = 0
    
    for url, year, month in month_urls:
        month_articles = scrape_month(url, year, month)
        all_articles.extend(month_articles)
        total_articles += len(month_articles)
        print(f"  Found {len(month_articles)} articles for {year}-{month:02d}")
    
    # Save combined CSV
    save_to_csv(all_articles, OUTPUT_ROOT)
    
    print("\nScraping complete! Summary:")
    print(f"- Total months processed: {len(month_urls)}")
    print(f"- Total articles scraped: {total_articles}")
    print(f"- Output folder: {os.path.abspath(OUTPUT_ROOT)}")
    
    if all_articles:
        print("\nSample articles:")
        for article in all_articles[:3]:
            print(f"  - {article['title']} ({article.get('date', 'no date')})")
            print(f"    Saved to: {article['file_path']}")

if __name__ == "__main__":
    main()