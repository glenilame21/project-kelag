import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import json
import re
import urllib3
import pyodbc

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Function For Title Retreival
def get_titles(IEA_soup):
    titles = IEA_soup.find_all('h5', class_='m-news-detailed-listing__title f-title-8')
    for article in titles:
        print(article.text.strip())
        return titles

# Function For URL Retreival
def get_url(IEA_soup):
    full_url = []
    base_url = "https://www.iea.org"
    for link in IEA_soup.find_all('a', href=True , class_='m-news-detailed-listing__link'):
        full_url.append(base_url + link['href'])
    return full_url


# Function For Scraping And Saving
def scrape_and_save(url_list, directory):
            #adding to SQL Server
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SQLBI01;'
        'DATABASE=DH_SANDBOX;'
        'Trusted_Connection=yes;')
    cursor = conn.cursor()


    # Path to the file where the titles are stored
    titles_file_path = os.path.join(directory, "News_IEA_Titles.json")

    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Read existing titles or create an empty list if the file doesn't exist
    try:
        with open(titles_file_path, 'r', encoding='utf-8') as file:
            existing_titles = json.load(file)
    except FileNotFoundError:
        existing_titles = []

    for url in url_list:
        response = requests.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            title_element = soup.find('h1', class_='o-hero-news__title f-title-3')
            if not title_element:
                print(f"Title not found for URL {url}")
                continue
            title = title_element.text.strip()
            title = re.sub(r'[\\/*?:"<>|]', "-", title)

            # Check title before scraping
            if title in existing_titles:
                print(f"Skipping already scraped article: {title}")
                continue
        
            existing_titles.append(title)  # Add new title to the list
        except Exception as e:
            print(f"Error retrieving title for URL {url}: {e}")
            continue  # Skip to the next URL if there's an error

        # Try to find the subtitle, set to empty string if missing
        subtitle_element = soup.find('h4', class_='f-title-7')
        subtitle = subtitle_element.text.strip() if subtitle_element else ""

        # Try to find the body
        body_element = soup.find('div', class_='m-block__content f-rte f-rte--block')
        body = body_element.text.strip() if body_element else "Body element is missing"

        # Try to find the timestamp
        timestamp_element = soup.find('time')
        if timestamp_element:
            timestamp = datetime.strptime(timestamp_element['datetime'], '%Y-%m-%dT%H:%M:%S%z')
            #formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        else:
            formatted_timestamp = None

        # DataFrame to temporarily save
        df = pd.DataFrame({
            'title': [title],
            'subtitle': [subtitle],
            'body': [body],
            'formatted_timestamp': timestamp_element,
            'source' : 'IEA'
        })

        for index, row in df.iterrows():
            cursor.execute("INSERT INTO mercurius.DT_SCRAPER (title, subtitle, body, datetime, source) VALUES (?, ?, ?, ?,?)",
                           row['title'], row['subtitle'], row['body'], row['formatted_timestamp'], row['source'])

        # Convert DataFrame to JSON
        json_str = df.to_json(orient='records', indent=4)

        # Save the JSON string to a file
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = os.path.join(directory, f'{safe_title}.json')
        with open(filename, 'w', encoding='utf-8') as json_file:
            json_file.write(json_str)

    # Update the titles file
    with open(titles_file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_titles, file, indent=4, ensure_ascii=False)

        conn.commit()
        conn.close()
