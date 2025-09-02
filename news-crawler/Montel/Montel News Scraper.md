# Montel News Scraper

This project is a web scraper for Montel News built with [Playwright](https://playwright.dev/python) and asynchronous Python. The scraper navigates to Montel News, authenticates the user using credentials stored in a `.env` file, extracts article details (including title, subtitle, content, datetime, and categories), and stores the data in both JSON files and a SQL Server database using [pyodbc](https://github.com/mkleehammer/pyodbc).

## File Structure

- **[Montel_Scraper_PlayWright.py](Montel/Montel_Scraper_PlayWright.py)**: Main Python script containing the scraping logic.
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
   playwright install
   ```

2. **Prepare the .env file:**

   Create a `.env` file in the `Montel/` directory with the following variables:

   ```
   MONTEL_USERNAME=your_username
   PASSWORD=your_password
   COOKIE_FILE=path/to/your/cookie_file.json
   DOWNLOAD_DIR=your/download/directory
   ```

3. **Prepare the URLs file:**

   The scraper expects a JSON file containing URLs at:

   ```
   Montel/urls.json
   ```

   Example format:

   ```json
   {
     "urls": [
       "https://montelnews.com/news/section1",
       "https://montelnews.com/news/section2"
     ]
   }
   ```

## Usage

Run the scraper with:

```sh
python Montel/Montel_Scraper_PlayWright.py
```

The script will:
- Authenticate to Montel News using Playwright and credentials from `.env`
- Scrape articles from the URLs in `urls.json`
- Save each article as a JSON file in the download directory
- Insert new articles into the SQL Server database, avoiding duplicates

## Notes

- Make sure your SQL Server is accessible and the `mercurius.DT_SCRAPER` table exists.
- The script uses cookies for authentication; ensure the cookie file path is correct.
- Duplicate articles are avoided by tracking titles in a local JSON file.

## License

Internal use only. Please ensure compliance with your organization's data and API policies.