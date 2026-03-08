import numpy as np
import pandas as pd


def factor(df: pd.DataFrame, ticker: str, params: dict) -> pd.Series:
    """动量：近N日收益率"""
    col = f"{ticker}_adj_close"
    if col not in df.columns:
        return pd.Series(-np.inf, index=df.index)
    window = params.get("window", 20)
    return df[col].pct_change(periods=window, fill_method=None).fillna(-np.inf)