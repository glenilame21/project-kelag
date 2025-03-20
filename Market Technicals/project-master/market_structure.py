import pandas as pd
import numpy as np


def is_pivot_high(series: pd.Series, i: int, length: int) -> bool:
    # Ensure we have enough bars on both sides
    if i < length or i > len(series) - length - 1:
        return False
    window = series.iloc[i - length : i + length + 1]
    return series.iloc[i] == window.max()


def is_pivot_low(series: pd.Series, i: int, length: int) -> bool:
    if i < length or i > len(series) - length - 1:
        return False
    window = series.iloc[i - length : i + length + 1]
    return series.iloc[i] == window.min()


def market_structure(close: pd.Series, length: int, smooth: int) -> pd.Series:
    """
      - It tracks the most recent pivot high (ph_y) and pivot low (pl_y)
      - When close exceeds ph_y (and not already crossed) a bullish signal is triggered
      - When close drops below pl_y (and not already crossed) a bearish signal is triggered
      - Then a normalization is applied over the ratio (close - min)/(max - min) using an SMA smoothing window.
    Returns a series with values in [0, 100].
    """
    # Initialize persistent variables
    ph_y = None
    pl_y = None
    ph_cross = False
    pl_cross = False
    # os stores the last signal state (0 = neutral, 1 = bullish, -1 = bearish)
    os_val = 0
    prev_os = 0
    # initialize running min and max for normalization using the first close value
    norm_max = close.iloc[0]
    norm_min = close.iloc[0]
    # For smoothing the ratio
    sma_window = []

    ms_values = [np.nan] * len(close)

    # Iterate over every bar
    for i in range(len(close)):
        price = close.iloc[i]
        bull = False
        bear = False

        # Update pivot high/low if we detect a pivot at this bar (using lookback/lookahead windows)
        if is_pivot_high(close, i, length):
            ph_y = price
            ph_cross = False
        if is_pivot_low(close, i, length):
            pl_y = price
            pl_cross = False

        # Check for bullish condition (if ph_y exists and hasn't been crossed already)
        if ph_y is not None and price > ph_y and not ph_cross:
            bull = True
            ph_cross = True

        # Check for bearish condition (if pl_y exists and hasn't been crossed already)
        if pl_y is not None and price < pl_y and not pl_cross:
            bear = True
            pl_cross = True

        # Update the signal state like in PineScript
        if bull:
            os_val = 1
        elif bear:
            os_val = -1
        # Otherwise keep previous state
        else:
            os_val = prev_os

        # Update norm_max and norm_min following PineScript logic:
        # If the signal goes up, reset norm_max to current price.
        # If the signal goes down, reset norm_min to current price.
        # Otherwise, update them gradually.
        if os_val > prev_os:
            norm_max = price
        elif os_val < prev_os:
            norm_min = price
        else:
            norm_max = max(price, norm_max)
            norm_min = min(price, norm_min)

        # Compute ratio (guarding against division by zero)
        if norm_max != norm_min:
            ratio = (price - norm_min) / (norm_max - norm_min)
        else:
            ratio = 0.5

        # Append new ratio to the smoothing window and compute a simple moving average
        sma_window.append(ratio)
        if len(sma_window) > smooth:
            sma_window.pop(0)
        smoothed = np.mean(sma_window)
        # Scale to 0-100
        normalized = smoothed * 100

        ms_values[i] = normalized

        prev_os = os_val

    return pd.Series(ms_values, index=close.index)
