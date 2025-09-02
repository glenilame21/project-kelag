import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pyodbc

today = datetime.today().strftime("%Y-%m-%d")

api_url = f"https://reuters-business-and-financial-news.p.rapidapi.com/category-id/382/article-date/{today}/0/20"

headers = {
    "x-rapidapi-key": "bc0a78f80cmshace3bef6f79ea6ep1e03cajsne43d9641f3e6",
    "x-rapidapi-host": "reuters-business-and-financial-news.p.rapidapi.com",
}

response = requests.get(api_url, headers=headers)

response = response.json()


keys_to_extract = [
    "articlesName",
    "articlesShortDescription",
    "articlesDescription",
    "articlesId",
    "publishedAt"
]

data = []

def process_description(x):
    try:
        # If the string is valid JSON, process it as a list of content items.
        items = json.loads(x)
        if isinstance(items, list):
            return "\n\n".join([item.get("content", "") for item in items if "content" in item])
        return x
    except json.JSONDecodeError:
        # Not a valid JSON string; assume it's HTML formatted plain text.
        soup = BeautifulSoup(x, "html.parser")
        return soup.get_text()

for article in response.get("articles", []):
    record = {key: article.get(key, None) for key in keys_to_extract}

    # Process articlesDescription using process_description helper
    raw_desc = article.get("articlesDescription")
    if raw_desc:
        record["articlesDescription"] = process_description(raw_desc)
    else:
        record["articlesDescription"] = None

    # Transform publishedAt to a pandas timestamp (using the 'date' field)
    published = article.get("publishedAt")
    if isinstance(published, dict) and "date" in published:
        record["publishedAt"] = pd.to_datetime(published["date"])
    else:
        record["publishedAt"] = None

    # Extract category from keywords: using the second item ('keywordName')
    keywords = article.get("keywords", [])
    if isinstance(keywords, list) and len(keywords) > 1 and isinstance(keywords[1], dict):
        record["category"] = keywords[1].get("keywordName")
    else:
        record["category"] = None

    data.append(record)

df = pd.DataFrame(data)
# Drop duplicates based on articlesId
df = df.drop_duplicates(subset=["articlesId"])

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SQLBI01;"
    "DATABASE=DH_SANDBOX;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Create ArticlesId table if it does not exist
cursor.execute("""
IF NOT EXISTS (
    SELECT * FROM sys.tables 
    WHERE name = 'ArticlesId' 
      AND schema_id = SCHEMA_ID('mercurius')
)
BEGIN
    CREATE TABLE mercurius.ArticlesId (
        id INT IDENTITY(1,1) PRIMARY KEY,  -- Auto-incremented ID
        articlesId INT NOT NULL
    )
END
""")
conn.commit()

# Loop through each row, check if articlesId is already stored, then insert if new
for index, row in df.iterrows():
    # Check if the articlesId already exists
    cursor.execute("SELECT 1 FROM mercurius.ArticlesId WHERE articlesId = ?", row["articlesId"])
    if cursor.fetchone() is None:
        # Insert into DT_SCRAPER only if the articlesId is not stored
        print("Inserting article:", row["articlesName"])
        cursor.execute(
            "INSERT INTO mercurius.DT_SCRAPER (title, subtitle, body, datetime, source, category) VALUES (?, ?, ?, ?, ?, ?)",
            row["articlesName"],
            row["articlesShortDescription"],
            row["articlesDescription"],
            row["publishedAt"],
            "Reuters",
            row["category"]
        )
        # Mark the articlesId as stored by inserting into ArticlesId table
        cursor.execute(
            "INSERT INTO mercurius.ArticlesId (articlesId) VALUES (?)",
            row["articlesId"]
        )
    else:
        print("Article already stored, skipping:", row["articlesName"])

# Commit all changes and close the connection
conn.commit()
conn.close()