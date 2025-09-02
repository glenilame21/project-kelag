import pyodbc
import pandas as pd
from datetime import datetime

class SQLData:
    def __init__(
        self,
        driver="{ODBC Driver 17 for SQL Server}",
        server="SQLBI01",
        database="DH_SANDBOX",
    ):
        self.conn = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )

    def fetch_table_to_dataframe(self, table_name):
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql(query, self.conn)
    
    def null_sentiment(self):
        query = """
            SELECT id, title, subtitle, body
            FROM mercurius.DT_SCRAPER
            WHERE sentiment IS NULL
            AND score IS NULL
            ORDER BY datetime
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [{"id": row[0], "text": f"{row[1]} {row[2]} {row[3]}"} for row in rows]
        return data


    def save_sentiment(self, id, sentiment, score, effect):
        cursor = self.conn.cursor()
        query = """
            UPDATE mercurius.DT_SCRAPER
            SET sentiment = ?, score = ?, effect = ?
            WHERE id = ?
        """
        cursor.execute(query, (sentiment, score, effect, id))
        self.conn.commit()

    def get_sentiment(self, start_date, end_date):
        query = """
            SELECT sentiment, score, date
            FROM mercurius.DT_SCRAPER
            WHERE sentiment IS NOT NULL AND score IS NOT NULL
            AND date BETWEEN ? AND ?
        """
        df = pd.read_sql(query, self.conn, params=[start_date, end_date])
        return df

    def OHCL(self, start, end):
        query = """
            SELECT date, [open], [high], [low], [close], [Settlement]
            FROM mercurius.[Sentiment_Technical_Indicators]
            WHERE CAST(date AS DATE) BETWEEN ? AND ?
            ORDER BY date
        """
        data = pd.read_sql(query, self.conn, params=[start, end])
        return data


# Example usage
if __name__ == "__main__":
    # Initialize connection
    sql = SQLData()

    """
    # Example 1: Fetch entire table
    full_table_df = sql.fetch_table_to_dataframe('mercurius.SinceStart')
    print("Full table shape:", full_table_df.shape)
    print("First 5 rows:\n", full_table_df.head())
    
    # Example 2: Get today's data
    today_data = sql.get_today()
    print("\nToday's entries:", len(today_data))
    
    # Example 3: Get OHCL data
    market_data = sql.OHCL('2023-01-01', '2023-12-31')
    print("\nMarket data columns:", market_data.columns.tolist())
    """

    # Example 4: Get Today
    today = sql.get_today()
    print("\nToday's entries:", len(today))
