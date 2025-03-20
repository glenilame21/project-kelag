import os
import json
import re
import pandas as pd
import pyodbc
import logging
from datetime import datetime, timezone
import asyncio
import random
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MonteL_PL:
    @staticmethod
    async def random_sleep(min_seconds=1, max_seconds=4):
        """Pause execution for a random duration between min_seconds and max_seconds."""
        sleep_duration = random.uniform(min_seconds, max_seconds)
        logger.info(f"Pausing for {sleep_duration:.2f} seconds...")
        await asyncio.sleep(sleep_duration)
        logger.info("Resuming execution...")

    @staticmethod
    async def timestamp(page, dates, today):
        time_elements = await page.query_selector_all('time.news-item__date')
        for element in time_elements:
            text = (await element.text_content()).strip()
            if 'ago' in text:
                dates.append(today)
            else:
                try:
                    date = datetime.strptime(text, '%d.%m.%Y %H:%M').date()
                    dates.append(date)
                except ValueError:
                    logger.error(f"Invalid date format: {text}")
                    dates.append(today)

    @staticmethod
    async def article_title(page):
        return await page.query_selector_all('h2.news-item__title')

    @staticmethod
    async def append_url(dates, today, article_titles):
        base_url = 'https://montelnews.com'
        full_urls = []
        for i, date in enumerate(dates):
            if date == today:
                link_element = await article_titles[i].query_selector('a')
                if link_element:
                    link = await link_element.get_attribute('href')
                    full_urls.append(base_url + link)
        return full_urls

    @staticmethod
    async def scrape_and_save(page, url_list, directory):
        titles_file_path = os.path.join(directory, 'titles.json')
        
        try:
            with open(titles_file_path, 'r', encoding='utf-8') as file:
                existing_titles = json.load(file)
        except FileNotFoundError:
            existing_titles = []

        data_to_insert = []
        
        for url in url_list:
            try:
                await page.goto(url, timeout=60000)
                await MonteL_PL.random_sleep()  # Random sleep after page load

                # Title handling
                title_element = await page.query_selector('h1.article__title')
                if not title_element:
                    logger.warning(f"No title found for {url}")
                    continue
                
                title = (await title_element.text_content()).strip()
                clean_title = re.sub(r'[\\/*?:"<>|]', "-", title)
                
                if clean_title in existing_titles:
                    logger.info(f"Skipping duplicate: {clean_title}")
                    continue

                # Content extraction
                subtitle = (await page.text_content('p.article__lead')) or "No subtitle available"
                body = (await page.text_content('div.article__body.bard')) or "No content available"

                # Datetime handling from ISO attribute
                time_element = await page.query_selector('time.article__date')
                article_datetime = None
                
                if time_element:
                    iso_datetime = await time_element.get_attribute('datetime')
                    if iso_datetime:
                        try:
                            article_datetime = datetime.fromisoformat(
                                iso_datetime.replace('Z', '+00:00')
                            ).astimezone(timezone.utc).replace(tzinfo=None)
                        except ValueError as e:
                            logger.error(f"Datetime parse error: {e} for {url}")
                
                # Fallback to current UTC time if parsing fails
                if not article_datetime:
                    article_datetime = datetime.utcnow()
                    logger.info(f"Using fallback datetime for {url}")

                # Category handling
                category_elements = await page.query_selector_all('a.article__topic')
                categories = [await element.text_content() for element in category_elements]
                category_json = json.dumps([cat.strip() for cat in categories if cat.strip()])

                # Collect data for batch insertion later
                data_to_insert.append(
                    (clean_title, subtitle, body, article_datetime, category_json, 'Montel')
                )

                # Update local JSON
                existing_titles.append(clean_title)
                df = pd.DataFrame({
                    'title': [clean_title],
                    'subtitle': [subtitle],
                    'body': [body],
                    'datetime': [article_datetime.isoformat()],
                    'category': [categories]
                })
                
                df.to_json(
                    os.path.join(directory, f'{clean_title}.json'),
                    orient='records',
                    indent=4,
                    date_format='iso'
                )

            except Exception as e:
                logger.error(f"Error processing {url}: {str(e)}")
                continue

        # Batch insert into database
        if data_to_insert:
            try:
                with pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    'SERVER=SQLBI01;'
                    'DATABASE=DH_SANDBOX;'
                    'Trusted_Connection=yes;'
                ) as conn:
                    cursor = conn.cursor()
                    cursor.executemany(
                        '''INSERT INTO mercurius.DT_SCRAPER 
                        (title, subtitle, body, datetime, category, source) 
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        data_to_insert
                    )
                    conn.commit()
                    logger.info(f"Successfully inserted {len(data_to_insert)} records.")
            except pyodbc.Error as e:
                logger.error(f"Database error: {str(e)}")
            
        # Update titles file
        with open(titles_file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_titles, file, indent=4)

async def authenticate_user(page, context):
    USERNAME = os.getenv('MONTEL_USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    COOKIE_FILE = os.getenv('COOKIE_FILE')
    
    try:
        await context.add_cookies(json.load(open(COOKIE_FILE)))
        await page.goto("https://montelnews.com/")
        if not await page.query_selector("a.button--logout"):
            raise Exception("Cookies expired")
    except:
        await page.goto("https://montelnews.com/login")
        try:
            await page.wait_for_selector('button.coi-banner__accept', timeout=5000)
            await page.click('button.coi-banner__accept')
            logger.info("Cookie acceptance button clicked")
        except Exception:
            logger.info("Cookie acceptance button not found")
        
        # Wait for the login buttons to be visible
        await page.wait_for_selector('div.page-login-card__buttons a.button:has-text("Log in")')
        # Get all login buttons matching the selector
        login_buttons = await page.query_selector_all('div.page-login-card__buttons a.button:has-text("Log in")')
        # Click the second login button if available; otherwise, click the first one
        if len(login_buttons) > 1:
            await login_buttons[1].click()
            logger.info("Second login button clicked")
        else:
            await login_buttons[0].click()
            logger.info("Fallback: First login button clicked")
            
        await MonteL_PL.random_sleep()
        await page.fill('#loginId', USERNAME)
        await page.fill('#password', PASSWORD)
        await page.click('button.blue.button')
        await page.wait_for_url("https://montelnews.com/")
        json.dump(await context.cookies(), open(COOKIE_FILE, 'w'))



async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Authentication
        await authenticate_user(page, context)

        # Scraping execution
        download_dir = os.getenv('DOWNLOAD_DIR', "C:/Users/Z_LAME/Desktop/Crawler/Downloads/MontelPlaywright")
        os.makedirs(download_dir, exist_ok=True)

        with open("C:/Users/Z_LAME/Desktop/Crawler/news-crawler/Montel/urls.json") as f:
            urls = json.load(f)['urls']

        for section_url in urls:
            await page.goto(section_url)
            await MonteL_PL.random_sleep()  # Random sleep after navigating to section
            dates = []
            today = datetime.now().date()
            await MonteL_PL.timestamp(page, dates, today)
            titles = await MonteL_PL.article_title(page)
            article_urls = await MonteL_PL.append_url(dates, today, titles)
            await MonteL_PL.scrape_and_save(page, article_urls, download_dir)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
