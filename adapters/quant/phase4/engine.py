"""
Phase 4 盘中同步系统 - 主引擎

核心：只响应，不预测

流程：
1. 感知层：听市场在说什么
2. 确认层：验证信号真伪
3. 决策层：基于确认信号行动
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from .validation import ValidationPointManager, ValidationResult

logger = logging.getLogger(__name__)


class Phase4Engine:
    """
    Phase 4 盘中同步引擎

    核心哲学：
    - 不预测明天会怎样
    - 只确认现在在发生什么
    - 只在市场给出答案的那一刻行动
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 Phase 4 引擎

        Args:
            config: 配置参数
                - min_breakout_amp: 最小突破幅度 (默认 0.02)
                - min_volume_ratio: 最小放量倍数 (默认 1.5)
                - min_resonance: 最小共振信号数 (默认 3)
                - validation_target_gain: 验证点目标涨幅 (默认 0.01)
                - validation_time_window: 验证点时间窗口 (默认 30分钟)
        """
        config = config or {}

        # 感知层参数
        self.min_breakout_amp = config.get('min_breakout_amp', 0.02)
        self.min_volume_ratio = config.get('min_volume_ratio', 1.5)
        self.resistance_lookback = config.get('resistance_lookback', 20)

        # 确认层参数
        self.min_resonance = config.get('min_resonance', 3)
        self.validation_manager = ValidationPointManager(
            target_gain=config.get('validation_target_gain', 0.01),
            time_window=config.get('validation_time_window', 30),
        )

        # 决策层参数
        self.max_position_ratio = config.get('max_position_ratio', 0.3)

        # 内部状态
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}

        logger.info("Phase 4 引擎初始化完成")

    def on_tick(
        self,
        tick_data: Dict[str, Any],
        portfolio_state: Dict[str, Any],
    ) -> List[Dict]:
        """
        处理实时tick数据 - 核心响应循环

        Args:
            tick_data: Tick数据
                {
                    "symbol": str,
                    "timestamp": datetime,
                    "price": float,
                    "volume": int,
                    "bid": float,
                    "ask": float,
                }
            portfolio_state: 投资组合状态
                {
                    "cash": float,
                    "positions": {...},
                    "equity": float,
                }

        Returns:
            List[Dict]: 信号列表
                [{
                    "symbol": str,
                    "timestamp": datetime,
                    "signal_type": str,  # BUY, SELL, HOLD
                    "confidence": float,
                    "price": float,
                    "reason": str,
                }]
        """
        signals = []
        symbol = tick_data['symbol']

        # 0. 先更新历史数据（感知层需要历史数据）
        self._update_history(symbol, tick_data)

        # 1. 感知层：市场在说什么？
        raw_signals = self._perceive(tick_data)

        # 2. 确认层：验证持仓的验证点（优先处理）
        # 使用验证点存在性来判断是否有持仓，而不是portfolio_state
        # 因为portfolio_state在信号处理时还未更新
        if symbol in self.validation_manager.validation_points:
            validation = self.validation_manager.check_validation(
                symbol,
                tick_data['price'],
                tick_data['timestamp']
            )

            if validation.action == 'exit':
                # 验证失败，立即离场
                signals.append({
                    "symbol": symbol,
                    "timestamp": tick_data['timestamp'],
                    "signal_type": "SELL",
                    "confidence": validation.confidence,
                    "price": tick_data['price'],
                    "reason": f"验证点失败: {validation.reason}",
                })
                # 移除验证点
                self.validation_manager.remove_validation_point(symbol)
                return signals  # 优先处理卖出

        # 3. 确认层：验证买入信号
        # 只有在没有验证点时才考虑买入（避免重复开仓）
        has_validation_point = symbol in self.validation_manager.validation_points
        if not has_validation_point:
            confirmed = self._confirm(raw_signals, tick_data)

            # 4. 决策层：基于确认信号决策
            if confirmed.get('buy_signal', False):
                # 买入后立即创建验证点（在返回信号之前）
                self.validation_manager.create_validation_point(
                    symbol=symbol,
                    entry_price=tick_data['price'],
                    entry_time=tick_data['timestamp'],
                )

                signals.append({
                    "symbol": symbol,
                    "timestamp": tick_data['timestamp'],
                    "signal_type": "BUY",
                    "confidence": confirmed.get('confidence', 0.6),
                    "price": tick_data['price'],
                    "reason": confirmed.get('reason', '多信号共振'),
                })

        return signals

    def _perceive(self, tick_data: Dict) -> Dict[str, Any]:
        """
        感知层：听市场在说什么

        只记录，不判断
        """
        symbol = tick_data['symbol']
        price = tick_data['price']
        volume = tick_data.get('volume', 0)

        signals = {
            'symbol': symbol,
            'price': price,
            'volume': volume,
            'breakout_up': False,
            'breakout_down': False,
            'volume_surge': False,
            'resonance_count': 0,
        }

        # 检查价格突破（使用历史数据，不包括当前价格）
        if symbol in self.price_history and len(self.price_history[symbol]) >= self.resistance_lookback:
            # 获取历史数据（不包括当前价格）
            history = self.price_history[symbol][:-1]  # 排除当前价格
            if len(history) >= self.resistance_lookback:
                recent_high = max(history[-self.resistance_lookback:])
                recent_low = min(history[-self.resistance_lookback:])

                # 向上突破
                if price > recent_high * (1 + self.min_breakout_amp):
                    signals['breakout_up'] = True
                    signals['resistance_level'] = recent_high

                # 向下突破
                if price < recent_low * (1 - self.min_breakout_amp):
                    signals['breakout_down'] = True
                    signals['support_level'] = recent_low

        # 检查成交量放大（使用历史数据）
        if symbol in self.volume_history and len(self.volume_history[symbol]) >= 10:
            history = self.volume_history[symbol][:-1]  # 排除当前成交量
            lookback = min(20, len(history))
            avg_volume = sum(history[-lookback:]) / lookback
            if volume > avg_volume * self.min_volume_ratio:
                signals['volume_surge'] = True

        # 计算共振信号数
        resonance_count = 0
        if signals['breakout_up']:
            resonance_count += 1
        if signals['volume_surge']:
            resonance_count += 1
        # 这里可以添加更多信号类型

        signals['resonance_count'] = resonance_count

        return signals

    def _confirm(self, raw_signals: Dict, tick_data: Dict) -> Dict:
        """
        确认层：验证信号的真伪

        Args:
            raw_signals: 感知层输出的原始信号
            tick_data: 当前tick数据

        Returns:
            确认结果
        """
        confirmed = {
            'buy_signal': False,
            'confidence': 0.0,
            'reason': '',
        }

        # 多信号共振验证
        resonance_count = raw_signals['resonance_count']

        # 买入条件（需全部满足）
        conditions = [
            raw_signals.get('breakout_up', False),  # 价格突破
            raw_signals.get('volume_surge', False),  # 成交量放大
            resonance_count >= self.min_resonance,   # 多信号共振
        ]

        if all(conditions):
            # 计算置信度
            confidence = min(0.9, 0.5 + resonance_count * 0.1)

            confirmed['buy_signal'] = True
            confirmed['confidence'] = confidence
            confirmed['reason'] = f'共振信号数: {resonance_count}, 突破幅度: {self._calc_breakout_amp(raw_signals):.2%}'

        return confirmed

    def _update_history(self, symbol: str, tick_data: Dict):
        """更新历史数据"""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
            self.volume_history[symbol] = []

        self.price_history[symbol].append(tick_data['price'])
        self.volume_history[symbol].append(tick_data.get('volume', 0))

        # 保持历史长度合理
        max_history = 100
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol] = self.price_history[symbol][-max_history:]
            self.volume_history[symbol] = self.volume_history[symbol][-max_history:]

    def _calc_breakout_amp(self, signals: Dict) -> float:
        """计算突破幅度"""
        if 'resistance_level' in signals:
            return (signals['price'] - signals['resistance_level']) / signals['resistance_level']
        return 0.0

    def on_position_closed(self, symbol: str):
        """持仓关闭时的清理"""
        self.validation_manager.remove_validation_point(symbol)

    def get_validation_status(self, symbol: str) -> Optional[Dict]:
        """获取验证点状态（用于监控）"""
        if symbol not in self.validation_manager.validation_points:
            return None

        vp = self.validation_manager.validation_points[symbol]
        return {
            'entry_price': vp.entry_price,
            'target_price': vp.target_price,
            'deadline': vp.deadline.isoformat(),
            'status': vp.status,
        }
