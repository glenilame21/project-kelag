import numpy as np


def calculate_stochastic_rsi(
    df, rsi_period=14, stoch_period=14, smooth_k=3, smooth_d=3
):
    # Calculate the lowest RSI and highest RSI over the specified period
    df["RSI_Low"] = df["RSI"].rolling(window=stoch_period).min()
    df["RSI_High"] = df["RSI"].rolling(window=stoch_period).max()

    # Calculate Stochastic RSI
    df["Stoch_RSI"] = (
        (df["RSI"] - df["RSI_Low"]) / (df["RSI_High"] - df["RSI_Low"]) * 100
    )
    return df


def interpolate_stochastic_rsi(stoch_val):
    if stoch_val > 80:
        return np.interp(stoch_val, [80, 100], [75, 100])
    elif stoch_val > 50:
        return np.interp(stoch_val, [50, 80], [50, 75])
    elif stoch_val > 20:
        return np.interp(stoch_val, [20, 50], [25, 50])
    else:
        return np.interp(stoch_val, [0, 20], [0, 25])
