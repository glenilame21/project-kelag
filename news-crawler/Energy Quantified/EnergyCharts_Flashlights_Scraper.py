import requests
from datetime import datetime
from bs4 import BeautifulSoup
import os
import json
import urllib3
import pyodbc

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
login_url = 'https://energycharts.enerchase.de/'
form_data = {
    'Email-4': 'georg.isola@kelag.at',
    'Password-4': 'N8sLvbsB'
}
TARGET_URL = 'https://energycharts.enerchase.de/energycharts/energycharts---co2-marktbericht'

# Paths for saved files and trackers
download_path = 'C:/Users/Z_LAME/Desktop/Crawler/Downloads/Energy Quantified/'
file_tracker_path = os.path.join(download_path, 'titles_tracker.json')
# Separate tracker for database insertions
DB_TRACKER_PATH = os.path.join(download_path, 'db_titles_tracker.json')

# SQL Server configuration
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SQLBI01;"
    "DATABASE=DH_SANDBOX;"
    "Trusted_Connection=yes;"
)

def parse_date(date_str: str) -> datetime:
    date_format = '%Y-%m-%d %I:%M %p'
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError as e:
        print(f"Date parsing error: {e}")
        return None

def scrape_articles(session: requests.Session):
    """Scrape articles from the CO2 Marktbericht page"""
    response = session.get(TARGET_URL, verify=False)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'lxml')
    
    main_div = soup.find_all('div', class_='co2_richttext w-richtext')
    timestamp_elements = soup.find_all('div', class_='date marktbericht')
    h3_elements = soup.find_all('h3', class_='co2_heading')
    
    titles = [elem.text.strip() for elem in h3_elements]
    bodies = [elem.text.strip() for elem in main_div]
    timestamp_texts = [elem.text.strip() for elem in timestamp_elements]
    
    dates = []
    for t in timestamp_texts:
        dt = parse_date(t)
        dates.append(dt)
        
    articles = []
    min_length = min(len(titles), len(bodies), len(dates))
    for i in range(min_length):
        if dates[i] is not None:
            articles.append({
                "title": titles[i],
                "date": dates[i],
                "body": bodies[i],
                "source": "Energy Quantified"
            })
    return articles

def save_articles_to_files(articles):
    """Save new articles to JSON files and update the file tracker"""
    try:
        with open(file_tracker_path, "r", encoding="utf-8") as file:
            tracked_titles = set(json.load(file))
    except FileNotFoundError:
        tracked_titles = set()

    for article in articles:
        title = article["title"]
        if title in tracked_titles:
            continue

        tracked_titles.add(title)
        article_data = {
            "title": title,
            "date": article["date"].strftime("%Y-%m-%d %I:%M %p") if article["date"] else "",
            "body": article["body"]
        }
        # Sanitize filename (allow alphanumeric characters and spaces)
        filename = "".join(c for c in title if c.isalnum() or c == " ").rstrip()
        filepath = os.path.join(download_path, f"{filename}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article_data, f, indent=4, ensure_ascii=False)
        print(f"Saved article: '{title}' to file: {filepath}")

    with open(file_tracker_path, "w", encoding="utf-8") as file:
        json.dump(list(tracked_titles), file, indent=4, ensure_ascii=False)
    print("File tracker updated.")

def save_to_database(articles):
    """Save new articles to SQL Server and update the DB tracker"""
    try:
        # Load existing tracked titles for DB insertion
        try:
            with open(DB_TRACKER_PATH, "r", encoding="utf-8") as f:
                db_tracked_titles = set(json.load(f))
        except FileNotFoundError:
            db_tracked_titles = set()

        new_articles = [a for a in articles if a["title"] not in db_tracked_titles]
        if not new_articles:
            print("No new articles to insert into the database.")
            return

        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        insert_sql = """
            INSERT INTO mercurius.DT_SCRAPER 
            (title, subtitle, body, datetime, category, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        inserted_titles = []
        for article in new_articles:
            try:
                cursor.execute(
                    insert_sql,
                    (
                        article["title"],
                        "",  # Empty subtitle
                        article["body"],
                        article["date"],
                        "Strom",  # Category not available here
                        article["source"]
                    )
                )
                inserted_titles.append(article["title"])
                print(f"Saved to DB: {article['title']}")
            except pyodbc.IntegrityError:
                print(f"Duplicate found in DB: {article['title']}")
                continue

        conn.commit()
        print(f"Inserted {len(inserted_titles)} new articles into the database")
        if inserted_titles:
            db_tracked_titles.update(inserted_titles)
            with open(DB_TRACKER_PATH, "w", encoding="utf-8") as f:
                json.dump(sorted(db_tracked_titles), f, indent=2)
            print("DB tracker updated.")
    except pyodbc.Error as e:
        conn.rollback()
        print(f"Database error: {str(e)}")
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error: {str(e)}")
    finally:
        if "conn" in locals():
            conn.close()

def main():
    """Main execution flow"""
    with requests.Session() as session:
        # Login to the website
        session.post(login_url, data=form_data, verify=False)
        # Scrape articles
        articles = scrape_articles(session)
        if articles:
            save_articles_to_files(articles)
            save_to_database(articles)
        else:
            print("No valid articles found.")

if __name__ == "__main__":
    main()