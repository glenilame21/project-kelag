import pandas as pd
import numpy as np


def calculate_atr(df, period):
    df["hl"] = df["High"] - df["Low"]
    df["hc"] = (df["High"] - df["Close"].shift(1)).abs()
    df["lc"] = (df["Low"] - df["Close"].shift(1)).abs()
    df["tr"] = df[["hl", "hc", "lc"]].max(axis=1)
    atr = df["tr"].rolling(window=period, min_periods=period).mean()
    return atr


def calculate_supertrend(df, period=10, factor=3):
    """
    Computes the raw Supertrend values.
    Returns a DataFrame with added columns for bands and the supertrend.
    """
    df = df.copy()
    atr = calculate_atr(df, period)
    hl2 = (df["High"] + df["Low"]) / 2

    df["basic_upperband"] = hl2 + factor * atr
    df["basic_Lowerband"] = hl2 - factor * atr

    final_upper = [np.nan] * len(df)
    final_Lower = [np.nan] * len(df)
    supertrend = [np.nan] * len(df)

    for i in range(len(df)):
        if i == 0:
            final_upper[i] = df.iloc[i]["basic_upperband"]
            final_Lower[i] = df.iloc[i]["basic_Lowerband"]
            supertrend[i] = np.nan
        else:
            current_basic_upper = df.iloc[i]["basic_upperband"]
            current_basic_Lower = df.iloc[i]["basic_Lowerband"]
            prev_final_upper = final_upper[i - 1]
            prev_final_Lower = final_Lower[i - 1]
            prev_Close = df.iloc[i - 1]["Close"]

            if not np.isnan(prev_final_upper):
                if (current_basic_upper < prev_final_upper) or (
                    prev_Close > prev_final_upper
                ):
                    final_upper[i] = current_basic_upper
                else:
                    final_upper[i] = prev_final_upper
            else:
                final_upper[i] = current_basic_upper

            if not np.isnan(prev_final_Lower):
                if (current_basic_Lower > prev_final_Lower) or (
                    prev_Close < prev_final_Lower
                ):
                    final_Lower[i] = current_basic_Lower
                else:
                    final_Lower[i] = prev_final_Lower
            else:
                final_Lower[i] = current_basic_Lower

            if not np.isnan(final_upper[i]) and not np.isnan(final_Lower[i]):
                if df.iloc[i]["Close"] <= final_upper[i]:
                    supertrend[i] = final_upper[i]
                else:
                    supertrend[i] = final_Lower[i]

    df["final_upperband"] = final_upper
    df["final_Lowerband"] = final_Lower
    df["supertrend"] = supertrend

    return df


def normalize_supertrend(df, supertrend, smooth):
    """
    It uses the condition (Close > supertrend) as buy and (Close < supertrend) as sell.
    Then it tracks a directional os and running High/Low of Close to calculate the raw normalized value.
    Finally, the raw ratio is smoothed (SMA over `smooth` period) and multiplied by 100.
    """
    n = len(df)
    os_list = [0] * n
    run_max = [np.nan] * n
    run_min = [np.nan] * n
    raw_norm = [np.nan] * n

    for i in range(n):
        Close_val = df["Close"].iloc[i]
        indicator = supertrend.iloc[i]
        if i == 0:
            # initial os based on condition
            os_val = 1 if Close_val > indicator else -1 if Close_val < indicator else 0
            os_list[i] = os_val
            run_max[i] = Close_val
            run_min[i] = Close_val
            raw_norm[i] = 0  # starting point
        else:
            prev_os = os_list[i - 1]
            # update os based on condition
            if Close_val > indicator:
                os_val = 1
            elif Close_val < indicator:
                os_val = -1
            else:
                os_val = prev_os
            os_list[i] = os_val

            # update running maximum:
            if os_val > prev_os:
                max_val = Close_val
            elif os_val < prev_os:
                max_val = run_max[i - 1]  # keep previous max if direction reversed
            else:
                max_val = max(run_max[i - 1], Close_val)
            run_max[i] = max_val

            # update running minimum:
            if os_val < prev_os:
                min_val = Close_val
            elif os_val > prev_os:
                min_val = run_min[i - 1]  # keep previous min if direction reversed
            else:
                min_val = min(run_min[i - 1], Close_val)
            run_min[i] = min_val

            diff = max_val - min_val
            raw_norm[i] = (Close_val - min_val) / diff if diff != 0 else 0

    # Apply SMA smoothing to the raw normalized values:
    raw_norm_series = pd.Series(raw_norm, index=df.index)
    smoothed = raw_norm_series.rolling(window=smooth, min_periods=1).mean()
    normalized = smoothed * 100

    # Add the normalized column to the DataFrame
    df["SuperTrend_Normalized"] = normalized

    return df
