# Reuters Daily News ETL

A Python ETL (Extract, Transform, Load) script that fetches the latest business and financial news articles from Reuters using the [Reuters Business and Financial News API](https://rapidapi.com/makingdatameaningful/api/reuters-business-and-financial-news) via RapidAPI, processes the data, and stores it in a SQL Server database.

## Features

- **Automated Data Collection**: Downloads the latest Reuters news articles for specified categories and dates
- **Data Processing**: Cleans and normalizes article content and metadata using BeautifulSoup
- **Duplicate Prevention**: Tracks article IDs to avoid storing duplicate content
- **Database Integration**: 
  - Stores articles in the `mercurius.DT_SCRAPER` table
  - Maintains processed article IDs in `mercurius.ArticlesId` table
- **Auto-Table Creation**: Automatically creates the `ArticlesId` tracking table if it doesn't exist

## Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - [requests](https://pypi.org/project/requests/) - HTTP requests
  - [pandas](https://pypi.org/project/pandas/) - Data manipulation
  - [pyodbc](https://pypi.org/project/pyodbc/) - SQL Server connectivity  
  - [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) - HTML parsing
- **API Access**: Reuters Business and Financial News API subscription via RapidAPI
- **Database**: SQL Server instance with appropriate permissions

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install requests pandas pyodbc beautifulsoup4
   ```

2. **Set up SQL Server access**:
   - Ensure you have access to a SQL Server instance
   - Verify connection permissions for the `mercurius` database
   - The script will automatically create the `ArticlesId` table if needed

3. **Configure API access** (see Configuration section below)

## Configuration

### API Key Setup

⚠️ **Important**: This API requires a **paid subscription** (approximately €8/month as of current pricing).

1. **Get your API key**:
   - Visit [RapidAPI Reuters Business and Financial News](https://rapidapi.com/makingdatameaningful/api/reuters-business-and-financial-news)
   - Subscribe to the API service
   - Copy your API key from the dashboard

2. **Update the script**:
   ```python
   headers = {
       "x-rapidapi-key": "YOUR_API_KEY_HERE",  # Replace with your actual key
       "x-rapidapi-host": "reuters-business-and-financial-news.p.rapidapi.com"
   }
   ```

### Database Configuration

Update the database connection parameters in the script:
```python
# Update these with your SQL Server details
server = 'your_server_name'
database = 'mercurius'
# Add authentication details as needed
```

## Usage

Run the ETL script:

```bash
python reuters_etl.py
```

### What the script does:

1. **Extract**: Fetches latest Reuters articles from the API
2. **Transform**: 
   - Cleans HTML content using BeautifulSoup
   - Normalizes metadata and article structure
   - Filters out previously processed articles
3. **Load**:
   - Inserts new articles into `mercurius.DT_SCRAPER`
   - Records processed article IDs in `mercurius.ArticlesId`

## Database Schema

The script works with two main tables:

- **`mercurius.DT_SCRAPER`**: Stores article content and metadata
- **`mercurius.ArticlesId`**: Tracks processed article IDs to prevent duplicates

## Cost Considerations

- **API Subscription**: ~€8/month for the Reuters API access
- **Usage Limits**: Check your RapidAPI plan for request limits
- **Monitoring**: Monitor your API usage to avoid unexpected charges

## Error Handling

The script includes handling for:
- API rate limits and connection issues
- Database connection failures
- Malformed article data
- Duplicate article detection

## Compliance & Legal

- **Internal Use Only**: This script is intended for internal organizational use
- **Terms of Service**: Ensure compliance with Reuters and RapidAPI terms of service
- **Data Usage**: Follow your organization's data handling and API usage policies
- **Attribution**: Respect Reuters' content attribution requirements

## Troubleshooting

**Common Issues**:
- **API Key Error**: Verify your RapidAPI subscription is active and key is correct
- **Database Connection**: Check SQL Server credentials and network access
- **Rate Limiting**: Monitor API usage and respect rate limits
- **Duplicate Articles**: Check the `ArticlesId` table for tracking issues

## License

Internal use only. Please ensure compliance with your organization's data and API policies, Reuters terms of service, and RapidAPI usage agreements.