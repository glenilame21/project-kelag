# Lang Chain Sentiment Analysis Pipeline

This project provides a workflow for classifying the sentiment and impact timeframe of energy news articles using large language models (LLMs) and storing the results in a SQL Server database.

## Project Structure

- [`structured_output.py`](Lang%20Chain/structured_output.py): Defines the LLM prompt logic, model classes, and the main `SENTIMENT_CLF` function for sentiment and timeframe classification.
- [`sentiment.py`](Lang%20Chain/sentiment.py): Loads news articles with missing sentiment, runs classification, and saves results to the database.
- [`SQL_Data.py`](Lang%20Chain/SQL_Data.py): Handles database connections and provides methods for reading and updating sentiment data.

## How It Works

1. **Database Connection**: [`SQLData`](Lang%20Chain/SQL_Data.py) connects to the SQL Server database and fetches articles without sentiment classification.
2. **Sentiment Classification**: [`SENTIMENT_CLF`](Lang%20Chain/structured_output.py) uses LLMs (e.g., Azure OpenAI) to classify each article as Bullish, Bearish, or Neutral, assign a weighted score, and determine the likely impact timeframe.
3. **Result Storage**: The results are saved back to the `mercurius.DT_SCRAPER` table in SQL Server.

## Usage

1. **Set up environment variables**  
   Ensure your Azure OpenAI API key is set as `AZURE_OPENAI_API_KEY` in your environment.

2. **Prepare few-shot examples**  
   Place a JSON file with few-shot examples at `C:/Users/Z_LAME/Desktop/Crawler/Lang Chain/fewshotsrandom.json`.

3. **Run the pipeline**  
   Execute [`sentiment.py`](Lang%20Chain/sentiment.py):

   ```sh
   python sentiment.py
   ```

   This will process all articles missing sentiment and update the database.

## Requirements

- Python 3.8+
- [langchain](https://python.langchain.com/)
- [pydantic](https://docs.pydantic.dev/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [pyodbc](https://github.com/mkleehammer/pyodbc)
- Azure OpenAI access

## Database Schema

The main table used is `mercurius.DT_SCRAPER` with at least the following columns:

- `id`: Primary key
- `title`, `subtitle`, `body`: Article content
- `sentiment`: Classification result (Bullish/Bearish/Neutral)
- `score`: Weighted score (-3 to 3)
- `effect`: Timeframe impact (Short/Long/Neutral)

## Customization

- Update the few-shot examples path or add more examples for better LLM performance.
- Adjust the LLM deployment or prompt logic in [`structured_output.py`](Lang%20Chain/structured_output.py) as needed.

## License

This project is for internal use. Please ensure compliance with your organization's data and API