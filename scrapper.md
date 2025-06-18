# scrap.py data from websites

# NCPUL Blog Scraper Documentation

## Overview
This Python script is designed to scrape and archive articles from the NCPUL blog (https://ncpulblog.blogspot.com/). The script systematically retrieves blog posts from specified years and months, extracts relevant content and metadata, and saves them in an organized folder structure with accompanying metadata in a CSV file.

## Features
- Recursive scraping of blog posts by year and month
- Content extraction including titles, dates, authors, and full text
- Automatic folder organization by year and month
- Sanitization of filenames for safe storage
- Metadata preservation in CSV format
- Respectful crawling with configurable delays between requests
- Error handling and logging

## Requirements
- Python 3.x
- Required Python packages:
  - requests
  - beautifulsoup4
  - lxml (parser for BeautifulSoup)

## Installation
1. Install Python 3.x from [python.org](https://www.python.org/downloads/)
2. Install required packages:
   ```
   pip install requests beautifulsoup4 lxml
   ```

## Configuration
The script includes several configurable parameters at the top of the file:

```python
BASE_URL = "https://ncpulblog.blogspot.com/"  # Target blog URL
OUTPUT_ROOT = "ncpul_articles_archive"       # Root folder for output
DELAY_BETWEEN_REQUESTS = 2                   # Seconds between requests
HEADERS = {                                  # Request headers
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
```

## Functions

### `setup_folders(base_path)`
Creates necessary output folders if they don't exist.

**Parameters:**
- `base_path`: Root directory for output

**Returns:**
- The created base path

### `sanitize_filename(title)`
Converts article titles to safe filenames.

**Parameters:**
- `title`: Article title string

**Returns:**
- Sanitized filename string

### `is_blog_post_url(url)`
Checks if a URL matches the pattern of a blog post URL.

**Parameters:**
- `url`: URL to check

**Returns:**
- Boolean indicating if URL is a blog post

### `extract_article_data(article_div, url=None)`
Extracts article data from HTML div element.

**Parameters:**
- `article_div`: BeautifulSoup div element containing article
- `url`: Optional URL of the article

**Returns:**
- Dictionary with extracted article data

### `save_article(article_data, year=None, month=None)`
Saves article content to file with year/month organization.

**Parameters:**
- `article_data`: Dictionary containing article data
- `year`: Optional year override
- `month`: Optional month override

**Returns:**
- Path to saved file or None if failed

### `get_year_month_urls(start_year, end_year)`
Generates month URLs for all months between specified years.

**Parameters:**
- `start_year`: First year to scrape
- `end_year`: Last year to scrape

**Returns:**
- List of tuples (url, year, month)

### `scrape_blog_post(url)`
Scrapes an individual blog post URL.

**Parameters:**
- `url`: URL of blog post to scrape

**Returns:**
- Dictionary with article metadata or None if failed

### `scrape_month(url, year, month)`
Scrapes all articles from a specific month page.

**Parameters:**
- `url`: URL of month archive page
- `year`: Year being scraped
- `month`: Month being scraped

**Returns:**
- List of article metadata dictionaries

### `save_to_csv(articles, folder_path)`
Saves article metadata to CSV file.

**Parameters:**
- `articles`: List of article metadata dictionaries
- `folder_path`: Path to save CSV file

### `main()`
Main function that orchestrates the scraping process.

## Usage
1. Configure the script parameters as needed
2. Run the script:
   ```
   python ncpul_scraper.py
   ```
3. The script will:
   - Create output folders
   - Scrape articles from 2015 to 2025
   - Save articles in organized folders
   - Create a metadata CSV file
   - Print a summary of results

## Output Structure
The script creates the following folder structure:
```
ncpul_articles_archive/
├── articles_metadata.csv
├── YYYY/
│   ├── MM/
│   │   ├── YYYYMMDD_Article_Title.txt
│   │   ├── ...
```

Each article file contains:
- Title
- Publication date (if available)
- Author (if available)
- Original URL
- Article content

The CSV file contains metadata for all scraped articles with columns:
- title
- date
- author
- url
- file_path
- year
- month

## Error Handling
The script includes error handling for:
- HTTP request failures
- Missing or malformed article elements
- File system operations
- Date parsing issues

## Limitations
- Dependent on the blog's HTML structure (may break if template changes)
- Limited to Blogspot blogs with similar structure
- No built-in mechanism to resume interrupted scrapes

## Customization
To adapt the script for other blogs:
1. Update `BASE_URL`
2. Adjust the CSS selectors in `extract_article_data()`
3. Modify the URL pattern in `is_blog_post_url()`
4. Update the year range in `get_year_month_urls()`

## Best Practices
- Respect `DELAY_BETWEEN_REQUESTS` to avoid overloading servers
- Monitor output for errors
- Consider adding logging for production use
- Regularly back up scraped data

## License
This script is provided as-is without warranty. Users are responsible for complying with the target website's terms of service and robots.txt directives.
