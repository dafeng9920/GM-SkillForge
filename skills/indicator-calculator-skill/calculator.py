"""
技术指标计算器
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union, Any


class IndicatorCalculator:
    """
    技术指标计算器

    支持趋势、动量、波动率、成交量等各类技术指标计算
    """

    def __init__(self):
        self._indicators = {
            # 趋势指标
            "SMA": self._sma,
            "EMA": self._ema,
            "WMA": self._wma,
            "MACD": self._macd,

            # 动量指标
            "RSI": self._rsi,
            "STOCH": self._stochastic,
            "MOMENTUM": self._momentum,
            "ROC": self._roc,

            # 波动率指标
            "BOLLINGER_BANDS": self._bollinger_bands,
            "ATR": self._atr,
            "KELTNER": self._keltner_channels,

            # 成交量指标
            "OBV": self._obv,
            "VWAP": self._vwap,
            "VOLUME_MA": self._volume_ma,
        }

    async def calculate(
        self,
        data: pd.DataFrame,
        indicators: List[Dict[str, Any]]
    ) -> Dict[str, pd.Series]:
        """
        计算多个技术指标

        Args:
            data: OHLCV 数据，必须包含 open, high, low, close, volume 列
            indicators: 指标配置列表

        Returns:
            {指标名称: pd.Series}
        """
        results = {}

        for indicator_config in indicators:
            name = indicator_config["name"]
            params = indicator_config.get("params", {})

            if name not in self._indicators:
                print(f"Warning: Unknown indicator {name}")
                continue

            try:
                result = await self._indicators[name](data, **params)
                results[name] = result
            except Exception as e:
                print(f"Error calculating {name}: {e}")

        return results

    # ==================== 趋势指标 ====================

    async def _sma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """简单移动平均"""
        return data["close"].rolling(window=period).mean()

    async def _ema(self, data: pd.DataFrame, period: int) -> pd.Series:
        """指数移动平均"""
        return data["close"].ewm(span=period, adjust=False).mean()

    async def _wma(self, data: pd.DataFrame, period: int) -> pd.Series:
        """加权移动平均"""
        weights = np.arange(1, period + 1)
        return data["close"].rolling(window=period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )

    async def _macd(
        self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9
    ) -> Dict[str, pd.Series]:
        """MACD 指标"""
        ema_fast = data["close"].ewm(span=fast, adjust=False).mean()
        ema_slow = data["close"].ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }

    # ==================== 动量指标 ====================

    async def _rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """相对强弱指标"""
        delta = data["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def _stochastic(
        self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3
    ) -> Dict[str, pd.Series]:
        """随机指标"""
        low_min = data["low"].rolling(window=k_period).min()
        high_max = data["high"].rolling(window=k_period).max()

        k = 100 * (data["close"] - low_min) / (high_max - low_min)
        d = k.rolling(window=d_period).mean()

        return {"k": k, "d": d}

    async def _momentum(self, data: pd.DataFrame, period: int = 10) -> pd.Series:
        """动量指标"""
        return data["close"].diff(period)

    async def _roc(self, data: pd.DataFrame, period: int = 12) -> pd.Series:
        """变动率"""
        return ((data["close"] - data["close"].shift(period)) / data["close"].shift(period)) * 100

    # ==================== 波动率指标 ====================

    async def _bollinger_bands(
        self, data: pd.DataFrame, period: int = 20, std_dev: float = 2
    ) -> Dict[str, pd.Series]:
        """布林带"""
        sma = data["close"].rolling(window=period).mean()
        std = data["close"].rolling(window=period).std()

        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        return {
            "upper": upper,
            "middle": sma,
            "lower": lower,
        }

    async def _atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """真实波幅"""
        high_low = data["high"] - data["low"]
        high_close = np.abs(data["high"] - data["close"].shift())
        low_close = np.abs(data["low"] - data["close"].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    async def _keltner_channels(
        self, data: pd.DataFrame, period: int = 20, multiplier: float = 2
    ) -> Dict[str, pd.Series]:
        """肯特纳通道"""
        ema = data["close"].ewm(span=period, adjust=False).mean()
        atr = await self._atr(data, period)

        upper = ema + (atr * multiplier)
        lower = ema - (atr * multiplier)

        return {
            "upper": upper,
            "middle": ema,
            "lower": lower,
        }

    # ==================== 成交量指标 ====================

    async def _obv(self, data: pd.DataFrame) -> pd.Series:
        """能量潮"""
        obv = pd.Series(index=data.index, dtype=float)
        obv.iloc[0] = data["volume"].iloc[0]

        for i in range(1, len(data)):
            if data["close"].iloc[i] > data["close"].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] + data["volume"].iloc[i]
            elif data["close"].iloc[i] < data["close"].iloc[i - 1]:
                obv.iloc[i] = obv.iloc[i - 1] - data["volume"].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i - 1]

        return obv

    async def _vwap(self, data: pd.DataFrame) -> pd.Series:
        """成交量加权平均价"""
        typical_price = (data["high"] + data["low"] + data["close"]) / 3
        vwap = (typical_price * data["volume"]).cumsum() / data["volume"].cumsum()
        return vwap

    async def _volume_ma(self, data: pd.DataFrame, period: int = 20) -> pd.Series:
        """成交量移动平均"""
        return data["volume"].rolling(window=period).mean()

    # ==================== 便捷方法 ====================

    async def calculate_all(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算所有支持的指标"""
        result = data.copy()

        # 趋势指标
        result["SMA_20"] = await self._sma(data, 20)
        result["SMA_50"] = await self._sma(data, 50)
        result["EMA_12"] = await self._ema(data, 12)
        result["EMA_26"] = await self._ema(data, 26)

        macd = await self._macd(data)
        result["MACD"] = macd["macd"]
        result["MACD_SIGNAL"] = macd["signal"]
        result["MACD_HIST"] = macd["histogram"]

        # 动量指标
        result["RSI_14"] = await self._rsi(data, 14)

        stoch = await self._stochastic(data)
        result["STOCH_K"] = stoch["k"]
        result["STOCH_D"] = stoch["d"]

        # 波动率指标
        bb = await self._bollinger_bands(data)
        result["BB_UPPER"] = bb["upper"]
        result["BB_MIDDLE"] = bb["middle"]
        result["BB_LOWER"] = bb["lower"]

        result["ATR_14"] = await self._atr(data, 14)

        # 成交量指标
        result["OBV"] = await self._obv(data)
        result["VWAP"] = await self._vwap(data)
        result["VOLUME_MA_20"] = await self._volume_ma(data, 20)

        return result
