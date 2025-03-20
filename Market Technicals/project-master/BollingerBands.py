import pandas as pd
import numpy as np


def calculate_bollinger_bands(df, window=20, num_std=2):
    # Calculate middle, upper, and lower bands
    df["BB_middle"] = df["Close"].rolling(window=window).mean()
    df["BB_std"] = df["Close"].rolling(window=window).std()
    df["BB_upper"] = df["BB_middle"] + num_std * df["BB_std"]
    df["BB_lower"] = df["BB_middle"] - num_std * df["BB_std"]
    return df


def normalize_bollingerbands(df, smooth=5):
    # Initialize columns to collect the normalized values.
    normalized = []
    os_prev = 0
    max_val = np.nan
    min_val = np.nan

    for i, row in df.iterrows():
        close = row["Close"]
        # Determine the oscillator state from buy/sell signals.
        if "buy" in df.columns and row["buy"]:
            os_cur = 1
        elif "sell" in df.columns and row["sell"]:
            os_cur = -1
        else:
            os_cur = os_prev

        # For the first row, initialize max and min.
        if pd.isna(max_val) or pd.isna(min_val):
            max_val = close
            min_val = close
        else:
            # When the oscillator rises, reset max; when it falls, reset min.
            if os_cur > os_prev:
                max_val = close
            elif os_cur < os_prev:
                min_val = close
            else:
                max_val = max(close, max_val)
                min_val = min(close, min_val)

        # Avoid division by zero.
        if max_val != min_val:
            norm = (close - min_val) / (max_val - min_val)
        else:
            norm = 0.5

        normalized.append(norm)
        os_prev = os_cur

    # Smooth the normalized values using a simple moving average and multiply by 100.
    df["bb_normalized"] = (
        pd.Series(normalized, index=df.index)
        .rolling(window=smooth, min_periods=1)
        .mean()
        * 100
    )
    return df
