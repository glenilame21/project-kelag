import numpy as np
import pandas as pd

def calculate_bull_bear_power(df, period=13):
    """
    Calculate the raw Bull Bear Power (BBP) and its Bollinger Bands.
    
    BBP = High + Low - 2 * EMA(Close, period)
    Bollinger Bands are computed on BBP using a 100-period SMA and a StdDev multiplier of 2.
    """
    df["EMA"] = df["Close"].ewm(span=period, adjust=False).mean()
    df["BBP"] = df["High"] + df["Low"] - 2 * df["EMA"]
    
    bb_period = 100
    bb_mult = 2
    # Adjust min_periods to 1 to avoid excessive NaNs with small datasets
    df["BBP_basis"] = df["BBP"].rolling(window=bb_period, min_periods=1).mean()
    df["BBP_std"]   = df["BBP"].rolling(window=bb_period, min_periods=1).std()
    df["BBP_upper"] = df["BBP_basis"] + bb_mult * df["BBP_std"]
    df["BBP_lower"] = df["BBP_basis"] - bb_mult * df["BBP_std"]
    
    return df

def interpolate_bbp(bbp, upper, lower):
    """
    Normalize the Bull Bear Power value according to the following rules:
    
    - If bbp > upper:
         If bbp > 1.5 * upper, return 100.
         Else interpolate bbp from [upper, 1.5*upper] to [75, 100].
         
    - If bbp is positive (but not above upper):
         Interpolate bbp from [0, upper] to [50, 75].
         
    - If bbp < lower:
         If bbp < 1.5 * lower, return 0.
         Else interpolate bbp from [lower, 1.5*lower] to [25, 0]
         (remember lower is negative, so 1.5*lower is more negative).
          
    - If bbp is negative (but not below lower):
         Interpolate bbp from [lower, 0] to [50, 25].
    """
    # If inputs are not scalars, vectorize the function
    if not np.isscalar(bbp):
        vector_func = np.vectorize(interpolate_bbp)
        return vector_func(bbp, upper, lower)

    # For scalar values, do standard processing
    if np.isnan(bbp) or np.isnan(upper) or np.isnan(lower):
        return np.nan

    if bbp > upper:
        if bbp > 1.5 * upper:
            return 100
        else:
            return np.interp(bbp, [upper, 1.5 * upper], [75, 100])
    elif bbp > 0:
        return np.interp(bbp, [0, upper], [50, 75])
    elif bbp < lower:
        if bbp < 1.5 * lower:
            return 0
        else:
            return np.interp(bbp, [lower, 1.5 * lower], [25, 0])
    elif bbp < 0:
        return np.interp(bbp, [lower, 0], [50, 25])
    else:
        return 50