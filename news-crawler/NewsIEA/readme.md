# IEA News Scraper

A Python-based web scraper for collecting news articles from the International Energy Agency (IEA) website. The scraper extracts article metadata and content, saves results as JSON files, and stores data in a SQL Server database.

## Features

- **Web Scraping**: Scrapes the latest news articles from [IEA News](https://www.iea.org/news/)
- **Content Extraction**: Extracts title, subtitle, body content, and publication dates
- **Duplicate Prevention**: Avoids re-downloading articles by tracking previously scraped titles
- **Data Storage**: 
  - Saves each article as a JSON file in a specified directory
  - Inserts article data into the `mercurius.DT_SCRAPER` SQL Server table
- **Error Handling**: Built-in mechanisms to handle network issues and parsing errors

## Project Structure

```
├── IEA_F.py           # Core scraping and database functions
├── IEA_scraper.py     # Main entry point script
└── README.md          # This file
```

## Requirements

- **Python**: 3.7 or higher
- **Dependencies**:
  - [requests](https://pypi.org/project/requests/) - HTTP requests
  - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - HTML parsing
  - [pandas](https://pypi.org/project/pandas/) - Data manipulation
  - [pyodbc](https://pypi.org/project/pyodbc/) - SQL Server connectivity

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install requests beautifulsoup4 pandas pyodbc
   ```

3. **Set up database access** (see Configuration section below)

## Configuration

### Database Setup
1. Ensure you have access to a SQL Server instance
2. Verify the `mercurius.DT_SCRAPER` table exists with the appropriate schema
3. Update database connection parameters in `IEA_F.py` if necessary

### Directory Setup
Update the download directory path in `IEA_scraper.py` to specify where JSON files should be saved.

## Usage

Run the scraper using the main script:

```bash
python IEA_scraper.py
```

### What happens when you run it:
1. The scraper visits the IEA news page
2. Extracts article links and metadata
3. Downloads full article content
4. Saves each article as a JSON file in the specified directory
5. Inserts article data into the SQL Server database
6. Updates the tracking file (`News_IEA_Titles.json`) to prevent duplicates

## Output

- **JSON Files**: Individual article files saved in your specified directory
- **Database Records**: Article data inserted into `mercurius.DT_SCRAPER` table
- **Tracking File**: `News_IEA_Titles.json` maintains a list of processed articles

## Notes

- **Duplicate Prevention**: The script maintains a `News_IEA_Titles.json` file to track previously scraped articles
- **SSL Warnings**: SSL warnings are disabled for convenience; consider enabling SSL verification for production use
- **Rate Limiting**: Be respectful of the IEA website's resources and consider adding delays between requests if needed

## Troubleshooting

**Common Issues**:
- **Database Connection**: Verify SQL Server credentials and network access
- **Permission Errors**: Ensure write permissions for the download directory
- **Network Issues**: Check internet connectivity and firewall settings

## License

Internal use only. Please ensure compliance with your organization's data usage policies and respect the IEA website's terms of service.