"""
数据质量验证器
"""

import pandas as pd
from typing import Dict, List, Any


class DataQualityValidator:
    """验证数据质量"""

    def __init__(self):
        self.rules = []

    def add_rule(self, rule_name: str, check_func, severity: str = "medium"):
        """添加验证规则"""
        self.rules.append({
            "name": rule_name,
            "check": check_func,
            "severity": severity,
        })

    def validate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """执行验证"""
        results = {
            "status": "PASSED",
            "total_rows": len(data),
            "valid_rows": len(data),
            "invalid_rows": 0,
            "issues": [],
        }

        for rule in self.rules:
            try:
                invalid_mask = ~rule["check"](data)
                invalid_count = invalid_mask.sum()

                if invalid_count > 0:
                    results["invalid_rows"] += invalid_count
                    results["valid_rows"] -= invalid_count
                    results["issues"].append({
                        "type": rule["name"],
                        "count": int(invalid_count),
                        "severity": rule["severity"],
                    })

            except Exception as e:
                results["issues"].append({
                    "type": f"rule_error_{rule['name']}",
                    "count": 0,
                    "severity": "high",
                    "error": str(e),
                })

        if results["invalid_rows"] > 0:
            results["status"] = "FAILED"

        return results

    @staticmethod
    def check_price_positive(data: pd.DataFrame) -> pd.Series:
        """检查价格是否为正"""
        return (data["open"] > 0) & (data["high"] > 0) & \
               (data["low"] > 0) & (data["close"] > 0)

    @staticmethod
    def check_volume_non_negative(data: pd.DataFrame) -> pd.Series:
        """检查成交量是否非负"""
        return data["volume"] >= 0

    @staticmethod
    def check_ohlc_consistency(data: pd.DataFrame) -> pd.Series:
        """检查 OHLC 逻辑一致性"""
        return (data["low"] <= data["close"]) & \
               (data["close"] <= data["high"]) & \
               (data["low"] <= data["high"])

    @staticmethod
    def check_no_duplicates(data: pd.DataFrame) -> pd.Series:
        """检查无重复记录"""
        return ~data.index.duplicated(keep=False)
