import numpy as np
import pandas as pd


def factor(df: pd.DataFrame, ticker: str, params: dict) -> pd.Series:
    """反转：近N日负收益率（跌得多得分高）"""
    col = f"{ticker}_adj_close"
    if col not in df.columns:
        return pd.Series(-np.inf, index=df.index)
    window = params.get("window", 5)
    rev = -df[col].pct_change(periods=window, fill_method=None)
    return rev.fillna(-np.inf)