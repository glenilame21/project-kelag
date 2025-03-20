import numpy as np


def calculate_cci(df, n=20):
    # Calculate the Typical Price (TP)
    TP = (df["High"] + df["Low"] + df["Close"]) / 3

    # Calculate the Simple Moving Average (SMA) of TP
    SMA = TP.rolling(window=n).mean()

    # Calculate the Mean Deviation
    def mean_deviation(series):
        mean = series.mean()
        return (series - mean).abs().mean()

    mean_deviation = TP.rolling(window=n).apply(mean_deviation)

    # Calculate the CCI
    CCI = (TP - SMA) / (0.015 * mean_deviation)

    # Add the CCI to the DataFrame
    df["CCI"] = CCI

    return df


def interpolate_cci(cci_val):
    if cci_val > 100:
        return 100 if cci_val > 300 else np.interp(cci_val, [100, 300], [75, 100])
    elif cci_val >= 0:
        return np.interp(cci_val, [0, 100], [50, 75])
    elif cci_val < -100:
        return 0 if cci_val < -300 else np.interp(cci_val, [-300, -100], [0, 25])
    else:  # cci_val < 0 and cci_val >= -100
        return np.interp(cci_val, [-100, 0], [25, 50])
