import numpy as np


def cal_SMA(df, period=20):

    df["SMA"] = df["Close"].rolling(window=period).mean()
    return df


def normalize_SMA(df, period=20, smooth=3):
    df["os"] = np.where(
        df["Close"] > df["SMA"], 1, np.where(df["Close"] < df["SMA"], -1, 0)
    )

    df["max"] = df["Close"].cummax()
    df["min"] = df["Close"].cummin()

    df["max"] = np.where(
        df["os"] > df["os"].shift(1),
        df["Close"],
        np.where(
            df["os"] < df["os"].shift(1),
            df["max"].shift(1),
            np.maximum(df["Close"], df["max"].shift(1)),
        ),
    )
    df["min"] = np.where(
        df["os"] < df["os"].shift(1),
        df["Close"],
        np.where(
            df["os"] > df["os"].shift(1),
            df["min"].shift(1),
            np.minimum(df["Close"], df["min"].shift(1)),
        ),
    )

    df["SMA_Normalized"] = (
        (df["Close"] - df["min"]) / (df["max"] - df["min"])
    ).rolling(window=smooth).mean() * 100

    return df
