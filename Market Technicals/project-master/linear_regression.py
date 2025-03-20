import pandas as pd
import numpy as np


def linear_regression_sentiment(source: pd.Series, length: int) -> pd.Series:
    """
    Calculate a linear regression-based sentiment from a rolling correlation.
    Equivalent to:
        50 * ta.correlation(source, bar_index, length) + 50
    where `bar_index` is assumed to be consecutive integers.
    """
    # Create a series with the bar indices (starting at 0)
    bar_index = pd.Series(np.arange(len(source)), index=source.index)

    # Calculate the rolling Pearson correlation between source and bar index
    rolling_corr = source.rolling(window=length).corr(bar_index)

    # Shift and scale the correlation to a 0-100 range:
    sentiment = 50 * rolling_corr + 50
    return sentiment
