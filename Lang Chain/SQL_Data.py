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
        """
        Fetch entire table contents into a pandas DataFrame
        Args:
            table_name (str): Fully qualified table name (e.g., 'schema.TableName')
        Returns:
            pd.DataFrame: DataFrame containing all data from the specified table
        """
        query = f"SELECT * FROM {table_name}"
        return pd.read_sql(query, self.conn)

    def get_today(self):
        today = datetime.now().date()
        yesterday = today - pd.Timedelta(days=1)
        query = """
                SELECT id, title, subtitle, body
                FROM mercurius.DT_SCRAPER
                WHERE datetime >= CAST(GETDATE() AS DATE) 
                AND datetime < DATEADD(DAY, 1, CAST(GETDATE() AS DATE))
                AND sentiment IS NULL
                AND score IS NULL
                ORDER BY datetime
            """
        cursor = self.conn.cursor()
        cursor.execute(query, (yesterday,today))
        rows = cursor.fetchall()
        data = [{"id": row[0], "text": f"{row[1]} {row[2]} {row[3]}"} for row in rows]
        return data
    
    def null_sentiment(self):
        query = """
            SELECT id, title, subtitle, body
            FROM mercurius.DT_SCRAPER
            WHERE sentiment IS NULL
            AND score IS NULL
            AND DATEPART(YEAR, datetime) = 2025
            ORDER BY datetime
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        data = [{"id": row[0], "text": f"{row[1]} {row[2]} {row[3]}"} for row in rows]
        return data

    def get_historical_data(self, start_date, end_date):
        cursor = self.conn.cursor()
        query = """
            SELECT id, title, subtitle, body
            FROM mercurius.Scraper
            WHERE CAST(date AS DATE) BETWEEN ? AND ?
            ORDER BY date
        """
        cursor.execute(query, (start_date, end_date))
        rows = cursor.fetchall()
        data = [{"id": row[0], "text": f"{row[1]} {row[2]} {row[3]}"} for row in rows]
        return data

    def since_start(self, start_date, end_date):
        query = """
            SELECT id, title, subtitle, body, datetime, category, source
            FROM mercurius.DT_SCRAPER
            WHERE CAST(datetime AS DATE) BETWEEN ? AND ?
            ORDER BY datetime
        """
        df = pd.read_sql(query, self.conn, params=[start_date, end_date])
        return df

    def save_sentiment(self, id, sentiment, score):
        cursor = self.conn.cursor()
        query = """
            UPDATE mercurius.DT_SCRAPER
            SET sentiment = ?, score = ?
            WHERE id = ?
        """
        cursor.execute(query, (sentiment, score, id))
        self.conn.commit()

    def get_sentiment(self, start_date, end_date):
        query = """
            SELECT sentiment, score, date
            FROM mercurius.SinceStart
            WHERE sentiment IS NOT NULL AND score IS NOT NULL
            AND date BETWEEN ? AND ?
        """
        df = pd.read_sql(query, self.conn, params=[start_date, end_date])
        return df

    def OHCL(self, start, end):
        query = """
            SELECT date, [open], [high], [low], [close], [Settlement]
            FROM mercurius.MarketTechnicals1
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
