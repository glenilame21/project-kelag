from RSI import calculate_rsi , rsi_interpolate
from Stochastic import calculate_stochastic, stochastic_interpolation
from Stochastic_RSI import calculate_stochastic_rsi , interpolate_stochastic_rsi
from CCI import calculate_cci, interpolate_cci
from Bull_Bear_Power import calculate_bull_bear_power , interpolate_bbp
from SMA import cal_SMA , normalize_SMA
from VolumeWeighted import calculate_daily_vwap_bands, normalize_indicator
from BollingerBands import calculate_bollinger_bands, normalize_bollingerbands
from SuperTrend import calculate_atr, calculate_supertrend , normalize_supertrend
from linear_regression import linear_regression_sentiment
from market_structure import market_structure



import pandas as pd
import pyodbc
import requests
from Forward_MarketData import get_OHLC
import pyodbc

## open connection to SQL Server
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=SQLBI01;"
    "DATABASE=DH_SANDBOX;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()


with open("access_token.txt") as f:
    token = f.read().strip()

# get data
data = get_OHLC(token)


ohlc = data.copy()


# STARTING WITH RSI FIRST, STOCHASTIC NEXT AND STOCHASTIC RSI LAST
data["RSI"] = calculate_rsi(data)
calculate_stochastic(data)
calculate_stochastic_rsi(data)


# Stochastic %K NEXT
data["RSI"] = data["RSI"].apply(rsi_interpolate)
data["%K"] = data["%K"].apply(stochastic_interpolation)
data["Stoch_RSI"] = data["Stoch_RSI"].apply(interpolate_stochastic_rsi)


calculate_cci(data)

data["CCI"] = data["CCI"].apply(interpolate_cci)


data = calculate_bull_bear_power(data)
data["Interpolated_BBP"] = interpolate_bbp(data['BBP'], data['BBP_upper'],data['BBP_lower'])


data = cal_SMA(data, 20)
data = normalize_SMA(data, period=20, smooth=3)

# Cal & Normalize VWAP
df = calculate_daily_vwap_bands(data, stdev=2)
df = normalize_indicator(df, smooth=3)


df = calculate_bollinger_bands(df)
df = normalize_bollingerbands(df, smooth=5)


df = calculate_supertrend(df)
df = normalize_supertrend(df, supertrend=df["supertrend"], smooth=5)

df["sentiment_lr"] = linear_regression_sentiment(df["Close"], length=25)

ms = market_structure(df["Close"], length=5, smooth=3)

df["market_structure"] = ms


names = [
    "RSI",
    "%K",
    "Stoch_RSI",
    "CCI",
    "Interpolated_BBP",
    "SMA_Normalized",
    "bb_normalized",
    "normalized",
    "SuperTrend_Normalized",
    "sentiment_lr",
    "market_structure",
]


df_names = ["Open", "High", "Low", "Close", "Volume", "Date"]

df = df.dropna(subset=names)


final = df[names]

final["Market Sentiment"] = final.mean(axis=1)


df1 = df[df_names]

joined_df = pd.concat([df1, final], axis=1)
print(joined_df.shape)


print(joined_df)

# because data repaints I delete everything and store only the new data
# this still causes repainting though
cursor.execute("DELETE FROM mercurius.Sentiment_Technical_Indicators")
conn.commit()


for index, row in joined_df.iterrows():
    cursor.execute(
        """ INSERT INTO mercurius.Sentiment_Technical_Indicators(
        [Open], [High], [Low], [Close], Volume, Date,
        "RSI", "%K", "Stoch_RSI", "CCI", "Interpolated_BBP",
        "SMA", "BollingerBands", "Normalized_VWAP", "SuperTrend_Normalized",
        "sentiment_lr", "market_structure", "Market Sentiment"
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        float(row.Open),
        float(row.High),
        float(row.Low),
        float(row.Close),
        float(row.Volume),
        row.Date,
        float(row.RSI),
        float(row["%K"]),
        float(row.Stoch_RSI),
        float(row.CCI),
        float(row.Interpolated_BBP),
        float(row.SMA_Normalized),
        float(row.bb_normalized),
        float(row.normalized),
        float(row.SuperTrend_Normalized),
        float(row.sentiment_lr),
        float(row.market_structure),
        float(row["Market Sentiment"])
    )

conn.commit()
cursor.close()
conn.close()