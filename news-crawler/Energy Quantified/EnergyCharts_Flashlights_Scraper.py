import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pyodbc
import json
import urllib3
from pathlib import Path
from typing import List, Dict

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
CONFIG_PATH = "C:/Users/Z_LAME/Desktop/Crawler/news-crawler/Energy Quantified/config.json"
DB_CONNECTION_STRING = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=SQLBI01;'
    'DATABASE=DH_SANDBOX;'
    'Trusted_Connection=yes;'
)
TARGET_URL = 'https://energycharts.enerchase.de/energycharts/energycharts---flashlights'
TRACKER_PATH = "C:/Users/Z_LAME/Desktop/Crawler/Downloads/Energy Quantified/titles_tracker.json"
SOURCE = 'Energy Quantified'

# Ensure download directory exists
Path(TRACKER_PATH).parent.mkdir(parents=True, exist_ok=True)

def load_config() -> Dict:
    """Load login credentials from config file"""
    with open(CONFIG_PATH) as config_file:
        return json.load(config_file)

def parse_date(date_str: str) -> datetime:
    """Convert date string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d %I:%M %p')
    except ValueError as e:
        print(f"Date parsing error: {e}")
        return None

def scrape_articles(session: requests.Session) -> List[Dict]:
    """Scrape articles from Flashlights page"""
    response = session.get(TARGET_URL, verify=False)
    soup = BeautifulSoup(response.text, 'lxml')

    # Extract elements
    titles = [h2.text.strip() for h2 in soup.find_all('h2', class_='f-heading-detail-small')]
    categories = [cat.text.strip() for cat in soup.find_all('div', class_='fl_tag')]
    date_strings = [date.text.strip() for date in soup.find_all('div', class_='date')]
    bodies = [body.text.strip() for body in soup.find_all('div', class_='w-richtext')]

    # Validate and pair data
    min_length = min(len(titles), len(categories), len(date_strings), len(bodies))
    articles = []
    
    for i in range(min_length):
        parsed_date = parse_date(date_strings[i])
        if parsed_date:
            articles.append({
                'title': titles[i],
                'category': categories[i],
                'date': parsed_date,
                'body': bodies[i],
                'source': SOURCE
            })
    
    return articles

def save_to_database(articles: List[Dict]):
    """Save articles to database and update title tracker"""
    try:
        # Load existing tracked titles
        try:
            with open(TRACKER_PATH, 'r', encoding='utf-8') as f:
                tracked_titles = set(json.load(f))
        except FileNotFoundError:
            tracked_titles = set()

        # Filter new articles
        new_articles = [a for a in articles if a['title'] not in tracked_titles]
        if not new_articles:
            print("No new articles to insert.")
            return

        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Prepare insert statement
        insert_sql = """
            INSERT INTO mercurius.DT_SCRAPER 
            (title, subtitle, body, datetime, category, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        # Insert new articles
        inserted_titles = []
        for article in new_articles:
            try:
                cursor.execute(insert_sql, (
                    article['title'],
                    '',  # Empty subtitle
                    article['body'],
                    article['date'],
                    article['category'],
                    article['source']
                ))
                inserted_titles.append(article['title'])
                print(f"Saved: {article['title']}")
            except pyodbc.IntegrityError:
                print(f"Duplicate found in DB: {article['title']}")
                continue

        conn.commit()
        print(f"Inserted {len(inserted_titles)} new articles")

        # Update title tracker
        if inserted_titles:
            tracked_titles.update(inserted_titles)
            with open(TRACKER_PATH, 'w', encoding='utf-8') as f:
                json.dump(sorted(tracked_titles), f, indent=2)
            print("Title tracker updated")

    except pyodbc.Error as e:
        conn.rollback()
        print(f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main execution flow"""
    # Load credentials and create session
    form_data = load_config()
    
    with requests.Session() as session:
        # Login
        session.post('https://energycharts.enerchase.de/', data=form_data, verify=False)
        
        # Scrape articles
        articles = scrape_articles(session)
        
        # Save to database and update tracker
        if articles:
            save_to_database(articles)
        else:
            print("No valid articles found")

if __name__ == "__main__":
    main()