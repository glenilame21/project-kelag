import os
import time
import random
from SQL_Data import SQLData
from structured_output import SENTIMENT_CLF


# Main code
conn = SQLData()
#data = conn.get_today()
data = conn.null_sentiment()
# data = conn.since_start("2024-01-01", "2024-12-31")
# print(data)

# Get sentiment
sentiment = []
score = []

for item in data:
    bullbear = SENTIMENT_CLF(item["text"])
    print(bullbear)
    sentiment.append(bullbear[0])
    score.append(bullbear[1])
    conn.save_sentiment(item["id"], sentiment[-1], score[-1])
        # conn.save_sentiment(item["id"], sentiment[-1], score[-1])
        # on each iteration sleep for 60 seconds to avoid rate limiting
    time.sleep(60)