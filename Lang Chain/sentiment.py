import os
import time
import random
from SQL_Data import SQLData
from structured_output import SENTIMENT_CLF

def process_item(item, conn):
    """Process a single item"""
    try:
        bullbear = SENTIMENT_CLF(item["text"])
        print(f"Item {item['id']}: {bullbear}")
        conn.save_sentiment(item["id"], bullbear[0], bullbear[1], bullbear[2])
        return True
    except Exception as e:
        print(f"Error processing item {item['id']}: {e}")
        return False


conn = SQLData()
data = conn.null_sentiment()

results = []
for item in data:
    result = process_item(item, conn)
    results.append(result)

successful = sum(results)
print(f"Successfully processed {successful}/{len(data)} items")