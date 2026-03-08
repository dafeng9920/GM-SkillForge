import numpy as np
import pandas as pd


def factor(df: pd.DataFrame, ticker: str, params: dict) -> pd.Series:
    """成交量放大率：近期均量/历史均量"""
    vol_col = f"{ticker}_成交量"
    if vol_col not in df.columns:
        return pd.Series(-np.inf, index=df.index)
    window = params.get("window", 20)
    hist_w = params.get("history_window", 60)
    recent = df[vol_col].rolling(window=window).mean()
    history = df[vol_col].rolling(window=hist_w).mean()
    return (recent / history).fillna(-np.inf)