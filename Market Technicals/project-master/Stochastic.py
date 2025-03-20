import numpy as np


def calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3):
    # Calculate the lowest low and highest high over the specified period
    df["Low_Min"] = df["Low"].rolling(window=period).min()
    df["High_Max"] = df["High"].rolling(window=period).max()

    # Calculate %K
    df["%K"] = 100 * ((df["Close"] - df["Low_Min"]) / (df["High_Max"] - df["Low_Min"]))

    # Smooth %K
    df["%K"] = df["%K"].rolling(window=smooth_k).mean()

    # Calculate %D, which is a moving average of %K
    df["%D"] = df["%K"].rolling(window=smooth_d).mean()

    return df


def stochastic_signal(df):
    df["Stochastic_Buy_Signal"] = (
        (df["%K"] < 20)
        & (df["%K"].shift(1) < df["%D"].shift(1))
        & (df["%K"] > df["%D"])
    ).astype(int)
    df["Stochastic_Sell_Signal"] = (
        (df["%K"] > 80)
        & (df["%K"].shift(1) > df["%D"].shift(1))
        & (df["%K"] < df["%D"])
    ).astype(int)
    return df


def stochastic_interpolation(stoch_val):
    if stoch_val > 80:
        return np.interp(stoch_val, [80, 100], [75, 100])
    elif stoch_val > 50:
        return np.interp(stoch_val, [50, 80], [50, 75])
    elif stoch_val > 20:
        return np.interp(stoch_val, [20, 50], [25, 50])
    else:
        return np.interp(stoch_val, [0, 20], [0, 25])
