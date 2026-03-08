import numpy as np
import pandas as pd


def factor(df: pd.DataFrame, ticker: str, params: dict) -> pd.Series:
    """均线强度：短期均线-长期均线的相对差"""
    col = f"{ticker}_adj_close"
    if col not in df.columns:
        return pd.Series(-np.inf, index=df.index)
    short_w = params.get("short_window", 5)
    long_w = params.get("long_window", 20)
    short_ma = df[col].rolling(window=short_w).mean()
    long_ma = df[col].rolling(window=long_w).mean()
    return ((short_ma - long_ma) / long_ma).fillna(-np.inf)