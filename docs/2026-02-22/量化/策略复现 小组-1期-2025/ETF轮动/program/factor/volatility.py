import numpy as np
import pandas as pd


def factor(df: pd.DataFrame, ticker: str, params: dict) -> pd.Series:
    """波动率（取负）：近N日年化波动率"""
    col = f"{ticker}_adj_amp"
    if col not in df.columns:
        return pd.Series(-np.inf, index=df.index)
    window = params.get("window", 20)
    daily_std = df[col].rolling(window=window).std()
    annual_vol = daily_std * np.sqrt(252)
    return (-annual_vol).fillna(-np.inf)