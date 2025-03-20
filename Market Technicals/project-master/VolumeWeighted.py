import pandas as pd
import numpy as np

def calculate_daily_vwap_bands(df, stdev=2):
    """
    Calculates VWAP bands with daily anchoring.
    Assumes df has a 'Date' column along with 'Close' and 'Volume'.
    Returns a DataFrame with columns: VWAP, upper, lower.
    """
    df = df.copy()
    df['VWAP'] = np.nan
    df['upper'] = np.nan
    df['lower'] = np.nan

    df['Date'] = pd.to_datetime(df['Date'])

    # Group by day (anchor = 'Day')
    for day, group in df.groupby(df['Date'].dt.date):
        group = group.copy()
        group['cum_vol'] = group['Volume'].cumsum()
        group['cum_pv'] = (group['Close'] * group['Volume']).cumsum()
        group['VWAP'] = group['cum_pv'] / group['cum_vol']
        # Compute a rolling standard deviation for the day's Close prices
        group['std'] = group['Close'].rolling(window=len(group), min_periods=1).std()
        group['upper'] = group['VWAP'] + stdev * group['std']
        group['lower'] = group['VWAP'] - stdev * group['std']
        df.loc[group.index, 'VWAP'] = group['VWAP']
        df.loc[group.index, 'upper'] = group['upper']
        df.loc[group.index, 'lower'] = group['lower']
    return df

def normalize_indicator(df, smooth=3):
    """
    Normalizes the Close price with respect to the VWAP bands.
    Mimics the Pine Script logic:
      - If Close > upper, signal becomes 1. If Close < lower, signal becomes -1.
      - When the signal changes from the previous row, only the corresponding running extreme is reset:
          * If new signal > previous signal, set running max = Close.
          * If new signal < previous signal, set running min = Close.
      - Otherwise, update running max = max(running max, Close) and running min = min(running min, Close).
      - Compute normalized value = (Close - run_min) / (run_max - run_min), smoothed and scaled to 0–100.
    
    Assumes df includes columns: 'Close', 'upper', 'lower'.
    """
    df = df.copy()
    norm_raw = []
    run_max = None
    run_min = None
    os = 0
    prev_os = 0

    for i, row in df.iterrows():
        buy = row['Close'] > row['upper']
        sell = row['Close'] < row['lower']
        if buy:
            os = 1
        elif sell:
            os = -1
        else:
            os = prev_os
        
        if run_max is None:
            # Initialize on first row
            run_max = row['Close']
            run_min = row['Close']
        else:
            # Reset only the corresponding extreme when signal changes
            if os > prev_os:
                run_max = row['Close']
            else:
                run_max = max(run_max, row['Close'])
            
            if os < prev_os:
                run_min = row['Close']
            else:
                run_min = min(run_min, row['Close'])
        
        # Compute normalized value between 0 and 1
        if run_max - run_min == 0:
            norm_val = 0.5
        else:
            norm_val = (row['Close'] - run_min) / (run_max - run_min)
        norm_raw.append(norm_val)
        prev_os = os

    df['norm_raw'] = norm_raw
    # Smooth and scale the value to 0 to 100
    df['normalized'] = df['norm_raw'].rolling(window=smooth, min_periods=1).mean() * 100
    return df