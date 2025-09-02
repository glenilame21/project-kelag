# Energy Quantified News Scraper

This module provides scripts to scrape CO₂ market news articles from [energycharts.enerchase.de](https://energycharts.enerchase.de/), save them as JSON files, and insert them into a SQL Server database. It is designed for automated, regular extraction and deduplication of energy market news for analytics and reporting.

## Features

- **Automated Scraping**: Fetches the latest CO₂ market news articles.
- **Data Processing**: Cleans and normalizes article content and metadata.
- **Duplicate Prevention**: Tracks article titles to avoid storing duplicate content.
- **Database Integration**: 
  - Stores articles in the `mercurius.DT_SCRAPER` table.
  - Maintains processed article titles in a tracker JSON file.
- **File Storage**: Saves each article as a JSON file for archival and backup.

## File Structure

- [`co2.py`](Energy%20Quantified/co2.py): Main script for scraping and saving CO₂ news articles.
- [`EnergyCharts_Flashlights_Scraper.py`](Energy%20Quantified/EnergyCharts_Flashlights_Scraper.py): Alternative/legacy scraper with similar functionality.
- [`config.json`](Energy%20Quantified/config.json): Stores login credentials for the website.
- [`titles_tracker.json`](../Downloads/Energy%20Quantified/titles_tracker.json): Tracks saved article titles to prevent duplicates.
- [`db_titles_tracker.json`](../Downloads/Energy%20Quantified/db_titles_tracker.json): Tracks articles inserted into the database.

## Usage

1. **Install dependencies**  
   ```bash
   pip install requests beautifulsoup4 pandas pyodbc lxml
   ```

2. **Configure credentials**  
   Edit `config.json` with your login details for [energycharts.enerchase.de](https://energycharts.enerchase.de/).

3. **Run the scraper**  
   ```bash
   python co2.py
   ```
   or
   ```bash
   python EnergyCharts_Flashlights_Scraper.py
   ```

4. **Output**  
   - New articles are saved as JSON files in the `Downloads/Energy Quantified/` directory.
   - Articles are inserted into the `mercurius.DT_SCRAPER` table in SQL Server.
   - Title trackers are updated to prevent duplicates.

## Database Schema

The main table used is `mercurius.DT_SCRAPER` with at least the following columns:
- `title`
- `subtitle`
- `body`
- `datetime`
- `category`
- `source`

## Customization

- Update the SQL Server connection string in the scripts as needed.
- Adjust parsing logic in the scripts if the website structure changes.

## License

Internal use only. Please ensure compliance with your organization's data