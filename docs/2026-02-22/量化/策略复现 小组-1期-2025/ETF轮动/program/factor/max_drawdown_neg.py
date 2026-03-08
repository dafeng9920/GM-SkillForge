import numpy as np
import pandas as pd


def factor(df: pd.DataFrame, ticker: str, params: dict) -> pd.Series:
    """最大回撤的负值（近N日）"""
    col = f"{ticker}_adj_close"
    if col not in df.columns:
        return pd.Series(-np.inf, index=df.index)
    window = params.get("window", 30)
    rolling_cummax = df[col].rolling(window=window).max()
    mdd = (df[col] / rolling_cummax) - 1
    return (-mdd).fillna(-np.inf)