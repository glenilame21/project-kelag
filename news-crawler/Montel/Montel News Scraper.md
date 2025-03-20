# Montel News Scraper

This project is a web scraper for Montel News built with [Playwright](https://playwright.dev/python) and asynchronous Python. The scraper navigates to Montel News, authenticates the user using credentials stored in a `.env` file, extracts article details (including title, subtitle, content, datetime, and categories), and stores the data in both JSON files and a SQL Server database using [pyodbc](https://github.com/mkleehammer/pyodbc).

## File Structure

- **[Montel_Scraper_PlayWright.py](news-crawler/Montel/Montel_Scraper_PlayWright.py)**: Main Python script containing the scraping logic.
- **.env**: Environment file containing sensitive data such as credentials, cookie file path, and download directory.
- **urls.json**: JSON file (located in the same directory as the script) containing the list of section URLs to scrape.

## Prerequisites

- Python 3.7+
- [Playwright for Python](https://playwright.dev/python/docs/intro)
- [pandas](https://pandas.pydata.org/)
- [pyodbc](https://github.com/mkleehammer/pyodbc)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- A SQL Server database with the table `mercurius.DT_SCRAPER` available for storing scraped data.

## Setup

1. **Install dependencies:**

   ```sh
   pip install playwright pandas pyodbc python-dotenv




Prepare the .env file:

Create a .env file in the project directory with the following variables:


MONTEL_USERNAME=your_username
PASSWORD=your_password
COOKIE_FILE=path/to/your/cookie_file.json
DOWNLOAD_DIR=your/download/directory


Ensure the urls.json file exists:

The scraper expects a JSON file containing URLs at:

C:/Users/Z_LAME/Desktop/Crawler/news-crawler/Montel/urls.json

You will have this in GitHub, replace it with your directory

