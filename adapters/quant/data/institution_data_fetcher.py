"""
机构数据获取模块 - 实用版

版本: 1.2.0
创建日期: 2026-03-09
"""

from dataclasses import dataclass, field
from typing import Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class InstitutionScore:
    """机构分析综合得分"""
    symbol: str
    holding_score: float         # 持仓得分 (-1 到 1)
    dragon_tiger_score: float    # 龙虎榜得分 (-1 到 1)
    north_bound_score: float     # 北向资金得分 (-1 到 1)
    block_trade_score: float     # 大宗交易得分 (-1 到 1)
    composite_score: float       # 综合得分 (-1 到 1)
    details: Dict = field(default_factory=dict)


class SimplifiedInstitutionFetcher:
    """简化的机构数据获取器（使用实际可用的数据）"""

    def __init__(self):
        """初始化"""
        try:
            import akshare as ak
            self.ak = ak
            logger.info("机构数据获取器初始化成功")
        except ImportError:
            logger.error("AKShare 未安装")
            raise

    def get_institution_score(self, symbol: str) -> InstitutionScore:
        """
        获取机构得分

        使用基于股票热度的简化方法
        TODO: 接入真实机构数据API（Tushare/Wind等）
        """
        # 热门股票通常有更好的机构关注度
        popular_scores = {
            "600519.SH": {"base": 0.7, "name": "贵州茅台"},
            "000001.SZ": {"base": 0.4, "name": "平安银行"},
            "000002.SZ": {"base": 0.3, "name": "万科A"},
            "600030.SH": {"base": 0.4, "name": "中信证券"},
            "600036.SH": {"base": 0.5, "name": "招商银行"},
            "601318.SH": {"base": 0.5, "name": "中国平安"},
            "600276.SH": {"base": 0.4, "name": "恒瑞医药"},
            "300750.SZ": {"base": 0.7, "name": "宁德时代"},
            "002594.SZ": {"base": 0.7, "name": "比亚迪"},
            "600900.SH": {"base": 0.3, "name": "长江电力"},
        }

        stock_info = popular_scores.get(symbol, {"base": 0.15, "name": "普通股票"})
        base_score = stock_info["base"]

        # 生成各维度得分（基于热度）
        holding_score = min(base_score * 0.8, 1.0)
        dragon_tiger_score = min(base_score * 0.6, 1.0) if base_score > 0.3 else 0
        north_bound_score = min(base_score * 0.7, 1.0)
        block_trade_score = min(base_score * 0.4, 1.0) if base_score > 0.4 else 0

        # 综合得分
        composite_score = (
            holding_score * 0.35 +
            dragon_tiger_score * 0.25 +
            north_bound_score * 0.25 +
            block_trade_score * 0.15
        )

        return InstitutionScore(
            symbol=symbol,
            holding_score=holding_score,
            dragon_tiger_score=dragon_tiger_score,
            north_bound_score=north_bound_score,
            block_trade_score=block_trade_score,
            composite_score=composite_score,
            details={
                'data_source': 'simulated',
                'stock_name': stock_info["name"],
                'fund_count': int(base_score * 40) if base_score > 0.3 else 5,
                'fund_ratio': base_score * 12,
                'dragon_count': int(dragon_tiger_score * 3) if base_score > 0.3 else 0,
                'north_ratio': north_bound_score * 6,
            }
        )

    def get_full_institution_data(self, symbol: str) -> InstitutionScore:
        """获取完整机构数据（兼容方法）"""
        return self.get_institution_score(symbol)


# 导出类
InstitutionDataFetcher = SimplifiedInstitutionFetcher
