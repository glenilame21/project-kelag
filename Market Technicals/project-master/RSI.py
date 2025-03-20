import pandas as pd
import numpy as np


def calculate_rsi(data, period=14, column="Close"):
    delta = data[column].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def rsi_interpolate(rsi_val):
    if rsi_val > 70:
        # Interpolate between 100 and 75 for RSI > 70
        return np.interp(rsi_val, [70, 100], [75, 100])
    elif rsi_val > 50:
        # Interpolate between 75 and 50 for 50 < RSI <= 70
        return np.interp(rsi_val, [50, 70], [50, 75])
    elif rsi_val > 30:
        # Interpolate between 50 and 25 for 30 < RSI <= 50
        return np.interp(rsi_val, [30, 50], [25, 50])
    else:
        # Interpolate between 25 and 0 for RSI <= 30
        return np.interp(rsi_val, [0, 30], [0, 25])
