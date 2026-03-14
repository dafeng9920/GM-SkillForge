"""
增强多因子动量策略 - Enhanced Multi-Factor Strategy

技术面 + 机构面共振策略

技术面因子：
- 动量因子
- 波动率因子
- 成交量因子
- RSI因子

机构面因子（新增）：
- 机构持仓因子
- 龙虎榜因子
- 北向资金因子
- 大宗交易因子

版本: 2.0.0
创建日期: 2026-03-09
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

# 添加项目路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.strategies.multi_factor_momentum import (
    MarketData,
    TradingSignal,
    StrategyConfig
)
from adapters.quant.data.institution_data_fetcher import InstitutionDataFetcher, InstitutionScore


# ============================================
# 增强配置
# ============================================

@dataclass
class EnhancedStrategyConfig(StrategyConfig):
    """增强策略配置"""
    # 技术面权重（保持原有）
    momentum_weight: float = 0.25
    volatility_weight: float = 0.10
    volume_weight: float = 0.10
    rsi_weight: float = 0.05

    # 机构面权重（新增）
    institution_holding_weight: float = 0.15    # 机构持仓权重
    dragon_tiger_weight: float = 0.10          # 龙虎榜权重
    north_bound_weight: float = 0.15           # 北向资金权重
    block_trade_weight: float = 0.10           # 大宗交易权重

    # 机构面阈值
    min_institution_score: float = 0.3         # 最低机构得分
    institution_bonus: float = 0.2             # 机构加持加分

    # 综合阈值
    min_composite_score: float = 0.25          # 降低买入阈值（因为有了机构加持）
    max_composite_score: float = -0.25
    min_confidence: float = 0.55

    # 仓位管理
    max_position_size: float = 0.25
    base_position_size: float = 0.12
    stop_loss_pct: float = 0.08
    take_profit_pct: float = 0.20


# ============================================
# 增强策略
# ============================================

class EnhancedMultiFactorStrategy:
    """
    增强多因子动量策略

    技术面 + 机构面共振
    """

    def __init__(self, config: Optional[EnhancedStrategyConfig] = None):
        """初始化策略"""
        self.config = config or EnhancedStrategyConfig()

        # 导入基础策略类（用于计算技术面因子）
        from adapters.quant.strategies.multi_factor_momentum import MultiFactorMomentumStrategy
        self.base_strategy = MultiFactorMomentumStrategy(config=config)

        # 机构数据获取器
        self.institution_fetcher = InstitutionDataFetcher()

        # 机构数据缓存
        self.institution_cache: Dict[str, InstitutionScore] = {}
        self.cache_timestamps: Dict[str, float] = {}

        logger.info("增强多因子策略初始化完成")

    def generate_signal(self, data: MarketData) -> TradingSignal:
        """
        生成交易信号（技术面 + 机构面）

        Args:
            data: 市场数据

        Returns:
            交易信号
        """
        # 1. 计算技术面因子得分
        tech_signal = self.base_strategy.generate_signal(data)
        tech_factors = tech_signal.factors
        tech_composite = tech_factors['composite']

        # 2. 获取机构面因子得分
        inst_score = self._get_institution_score(data.symbol)
        inst_factors = {
            'institution_holding': inst_score.holding_score,
            'dragon_tiger': inst_score.dragon_tiger_score,
            'north_bound': inst_score.north_bound_score,
            'block_trade': inst_score.block_trade_score,
            'institution_composite': inst_score.composite_score
        }

        # 3. 计算综合得分
        composite_score = self._calculate_composite_score(tech_composite, inst_score.composite_score)

        # 4. 计算置信度
        confidence = self._calculate_confidence(tech_composite, inst_score.composite_score, tech_signal.confidence)

        # 5. 确定交易动作
        action, reasoning = self._determine_action(
            composite_score,
            confidence,
            tech_factors,
            inst_factors
        )

        # 6. 计算目标价和止损价
        target_price, stop_loss = self._calculate_targets(
            data.close, action, tech_factors, inst_factors
        )

        # 7. 计算仓位大小
        position_size = self._calculate_position_size(
            composite_score, inst_score.composite_score
        )

        # 8. 构建信号
        all_factors = {**tech_factors, **inst_factors}

        return TradingSignal(
            symbol=data.symbol,
            action=action,
            confidence=confidence,
            target_price=target_price,
            stop_loss=stop_loss,
            position_size=position_size,
            reasoning=reasoning,
            factors=all_factors,
            timestamp=data.timestamp
        )

    def _get_institution_score(self, symbol: str) -> InstitutionScore:
        """获取机构得分（带缓存）"""
        import time
        now = time.time()

        # 检查缓存
        if symbol in self.institution_cache:
            cache_time = self.cache_timestamps.get(symbol, 0)
            if now - cache_time < 3600:  # 缓存1小时
                return self.institution_cache[symbol]

        # 获取新数据
        try:
            score = self.institution_fetcher.get_full_institution_data(symbol)
            self.institution_cache[symbol] = score
            self.cache_timestamps[symbol] = now
            return score
        except Exception as e:
            logger.error(f"获取{symbol}机构数据失败: {e}")
            # 返回中性得分
            return InstitutionScore(
                symbol=symbol,
                holding_score=0,
                dragon_tiger_score=0,
                north_bound_score=0,
                block_trade_score=0,
                composite_score=0,
                details={}
            )

    def _calculate_composite_score(
        self,
        tech_score: float,
        inst_score: float
    ) -> float:
        """计算综合得分"""
        # 技术面权重
        tech_weight = (
            self.config.momentum_weight +
            self.config.volatility_weight +
            self.config.volume_weight +
            self.config.rsi_weight
        )

        # 机构面权重
        inst_weight = (
            self.config.institution_holding_weight +
            self.config.dragon_tiger_weight +
            self.config.north_bound_weight +
            self.config.block_trade_weight
        )

        # 加权平均
        total_weight = tech_weight + inst_weight
        composite = (tech_score * tech_weight + inst_score * inst_weight) / total_weight

        # 机构加持加分
        if inst_score > self.config.min_institution_score:
            composite += self.config.institution_bonus

        return composite

    def _calculate_confidence(
        self,
        tech_score: float,
        inst_score: float,
        base_confidence: float
    ) -> float:
        """计算置信度"""
        # 基础置信度
        confidence = base_confidence

        # 机构加持提升置信度
        if inst_score > 0.5:
            confidence = min(confidence + 0.15, 1.0)
        elif inst_score > 0.3:
            confidence = min(confidence + 0.10, 1.0)

        # 技术面和机构面都好时，置信度最高
        if tech_score > 0.3 and inst_score > 0.3:
            confidence = min(confidence + 0.10, 1.0)

        return confidence

    def _determine_action(
        self,
        composite_score: float,
        confidence: float,
        tech_factors: Dict,
        inst_factors: Dict
    ) -> tuple[str, str]:
        """确定交易动作和理由（带调试信息）"""
        inst_composite = inst_factors.get('institution_composite', 0)

        # 调试信息
        print(f"\n     [调试] 综合得分: {composite_score:.3f} (阈值: {self.config.min_composite_score})")
        print(f"     [调试] 置信度: {confidence:.1%} (阈值: {self.config.min_confidence})")
        print(f"     [调试] 机构得分: {inst_composite:.3f}")

        # 买入条件
        """确定交易动作和理由"""
        inst_composite = inst_factors.get('institution_composite', 0)

        # 买入条件
        if composite_score >= self.config.min_composite_score and confidence >= self.config.min_confidence:
            action = "BUY"

            # 生成详细理由
            reasons = []

            # 技术面理由
            if tech_factors['momentum'] > 0.3:
                reasons.append(f"动量强劲({tech_factors['momentum']:.2f})")
            if tech_factors['volume'] > 0.3:
                reasons.append(f"资金流入({tech_factors['volume']:.2f})")

            # 机构面理由
            if inst_factors['institution_holding'] > 0.3:
                reasons.append(f"基金重仓({inst_factors['institution_holding']:.2f})")
            if inst_factors['dragon_tiger'] > 0.3:
                reasons.append(f"龙虎榜活跃({inst_factors['dragon_tiger']:.2f})")
            if inst_factors['north_bound'] > 0.3:
                reasons.append(f"北向加仓({inst_factors['north_bound']:.2f})")

            # 综合说明
            tech_desc = "、".join(reasons[:2]) if reasons else "技术面稳健"
            inst_desc = f"机构加持({inst_composite:.2f})" if inst_composite > 0.3 else "机构中性"

            reasoning = f"{tech_desc}，{inst_desc}，综合得分{composite_score:.2f}，置信度{confidence:.0%}"

        # 卖出条件
        elif composite_score <= self.config.max_composite_score:
            action = "SELL"

            reasons = []
            if tech_factors['momentum'] < -0.3:
                reasons.append(f"动量疲弱({tech_factors['momentum']:.2f})")

            if inst_composite < -0.2:
                reasons.append("机构撤离")

            desc = "、".join(reasons) if reasons else "多指标转弱"
            reasoning = f"{desc}，综合得分{composite_score:.2f}，触发卖出"

        # 观望
        else:
            action = "HOLD"
            reasoning = f"综合得分{composite_score:.2f}，等待共振确认"

        return action, reasoning

    def _calculate_targets(
        self,
        current_price: float,
        action: str,
        tech_factors: Dict,
        inst_factors: Dict
    ) -> tuple[Optional[float], Optional[float]]:
        """计算目标价和止损价"""
        if action == "HOLD":
            return None, None

        # 机构加持可以提高目标价
        inst_bonus = 1.0
        if inst_factors['institution_composite'] > 0.5:
            inst_bonus = 1.1  # 提高目标价10%

        if action == "BUY":
            target_price = current_price * (1 + self.config.take_profit_pct * inst_bonus)
            stop_loss = current_price * (1 - self.config.stop_loss_pct)
        else:
            target_price = None
            stop_loss = None

        return target_price, stop_loss

    def _calculate_position_size(
        self,
        composite_score: float,
        inst_score: float
    ) -> float:
        """计算仓位大小"""
        # 基础仓位
        size = self.config.base_position_size

        # 根据综合得分调整
        if composite_score > 0.5:
            size = self.config.max_position_size
        elif composite_score > 0.3:
            size = (self.config.base_position_size + self.config.max_position_size) / 2

        # 机构加持增加仓位
        if inst_score > 0.5:
            size = min(size * 1.2, self.config.max_position_size)

        return size


# ============================================
# 便捷函数
# ============================================

def create_enhanced_strategy(config: Optional[EnhancedStrategyConfig] = None) -> EnhancedMultiFactorStrategy:
    """创建增强策略实例"""
    return EnhancedMultiFactorStrategy(config=config)


# ============================================
# CLI 测试
# ============================================

def main():
    """测试增强策略"""
    print("=" * 70)
    print("  增强多因子策略测试")
    print("=" * 70)

    from adapters.quant.data.china_stock_fetcher import get_popular_stocks

    # 创建策略
    config = EnhancedStrategyConfig(
        min_composite_score=0.2,
        min_institution_score=0.3
    )
    strategy = create_enhanced_strategy(config)

    # 测试股票
    symbols = get_popular_stocks()[:3]

    print(f"\n测试股票: {', '.join(symbols)}\n")

    for symbol in symbols:
        print(f"\n{'=' * 70}")
        print(f"  {symbol}")
        print(f"{'=' * 70}")

        try:
            # 获取机构得分
            inst_score = strategy._get_institution_score(symbol)

            print(f"\n机构分析:")
            print(f"  持仓得分: {inst_score.holding_score:+.2f}")
            print(f"  龙虎榜得分: {inst_score.dragon_tiger_score:+.2f}")
            print(f"  北向资金得分: {inst_score.north_bound_score:+.2f}")
            print(f"  大宗交易得分: {inst_score.block_trade_score:+.2f}")
            print(f"  综合得分: {inst_score.composite_score:+.2f}")

            if inst_score.details:
                print(f"\n详细信息:")
                print(f"  基金数量: {inst_score.details.get('fund_count', 0)} 家")
                print(f"  基金比例: {inst_score.details.get('fund_ratio', 0):.2f}%")
                print(f"  龙虎榜: {inst_score.details.get('dragon_tiger_count', 0)} 次")
                print(f"  北向比例: {inst_score.details.get('north_bound_ratio', 0):.2f}%")

        except Exception as e:
            print(f"\n错误: {e}")

    print("\n" + "=" * 70)
    print("  测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
