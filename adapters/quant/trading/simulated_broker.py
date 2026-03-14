"""
模拟券商 - Simulated Broker

完整的模拟交易系统，支持：
- 实时A股行情
- 订单管理（限价单、市价单）
- 持仓管理
- 资金管理
- 交易记录
- 绩效计算

版本: 1.0.0
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import json

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.data.china_stock_fetcher import ChinaStockDataFetcher, StockQuote


# ============================================
# 订单类型
# ============================================

class OrderType(Enum):
    """订单类型"""
    MARKET = "market"     # 市价单
    LIMIT = "limit"       # 限价单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"           # 待成交
    PARTIAL_FILLED = "partial"    # 部分成交
    FILLED = "filled"             # 已成交
    CANCELLED = "cancelled"       # 已撤销
    REJECTED = "rejected"         # 已拒绝


# ============================================
# 订单模型
# ============================================

@dataclass
class Order:
    """订单"""
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: int                  # 数量（股）
    price: Optional[float] = None  # 限价单价格
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: int = 0       # 已成交数量
    filled_price: float = 0        # 成交均价
    commission: float = 0          # 手续费
    created_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    reason: str = ""               # 拒绝原因


# ============================================
# 持仓模型
# ============================================

@dataclass
class Position:
    """持仓"""
    symbol: str
    quantity: int                  # 持仓数量
    available_quantity: int        # 可用数量
    avg_price: float               # 成本价
    current_price: float           # 当前价
    market_value: float = 0        # 市值
    unrealized_pnl: float = 0      # 浮动盈亏
    unrealized_pnl_pct: float = 0  # 浮动盈亏比例

    def update_market_value(self, current_price: float):
        """更新市值"""
        self.current_price = current_price
        self.market_value = self.quantity * current_price
        self.unrealized_pnl = (current_price - self.avg_price) * self.quantity
        self.unrealized_pnl_pct = (current_price / self.avg_price - 1) * 100 if self.avg_price > 0 else 0


# ============================================
# 交易记录
# ============================================

@dataclass
class Trade:
    """成交记录"""
    trade_id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    commission: float
    trade_time: datetime
    pnl: float = 0                 # 已实现盈亏（仅平仓）


# ============================================
# 模拟券商
# ============================================

class SimulatedBroker:
    """
    模拟券商

    提供完整的交易功能：
    - 订单下单、撤销
    - 持仓查询
    - 资金查询
    - 成交记录
    """

    def __init__(
        self,
        initial_capital: float = 1000000,
        commission_rate: float = 0.0003,    # 万三佣金
        min_commission: float = 5.0,        # 最低佣金5元
        stamp_duty_rate: float = 0.001,     # 印花税（仅卖出）
    ):
        """
        初始化模拟券商

        Args:
            initial_capital: 初始资金
            commission_rate: 佣金费率
            min_commission: 最低佣金
            stamp_duty_rate: 印花税率
        """
        # 资金
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.frozen_cash = 0  # 冻结资金（挂单占用）

        # 持仓
        self.positions: Dict[str, Position] = {}

        # 订单
        self.orders: Dict[str, Order] = {}
        self.order_counter = 0

        # 成交记录
        self.trades: List[Trade] = []
        self.trade_counter = 0

        # 费率设置
        self.commission_rate = commission_rate
        self.min_commission = min_commission
        self.stamp_duty_rate = stamp_duty_rate

        # 数据源
        self.data_fetcher: Optional[ChinaStockDataFetcher] = None

        print(f"✓ 模拟券商初始化完成")
        print(f"  初始资金: ¥{initial_capital:,.2f}")
        print(f"  佣金费率: {commission_rate*10000:.1f}‰")
        print(f"  最低佣金: ¥{min_commission:.2f}")

    def connect_data_source(self):
        """连接数据源"""
        try:
            self.data_fetcher = ChinaStockDataFetcher(preferred_source="akshare")
            print("✓ 数据源连接成功")
        except Exception as e:
            print(f"✗ 数据源连接失败: {e}")

    def get_account_info(self) -> dict:
        """获取账户信息"""
        # 计算持仓市值
        total_market_value = sum(pos.market_value for pos in self.positions.values())
        total_asset = self.cash + total_market_value

        # 计算总盈亏
        total_pnl = total_asset - self.initial_capital
        total_pnl_pct = (total_asset / self.initial_capital - 1) * 100

        return {
            "total_asset": total_asset,
            "cash": self.cash,
            "frozen_cash": self.frozen_cash,
            "market_value": total_market_value,
            "positions": len(self.positions),
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl_pct,
        }

    def get_positions(self) -> Dict[str, Position]:
        """获取所有持仓"""
        return self.positions.copy()

    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """获取订单列表"""
        orders = list(self.orders.values())
        if status:
            orders = [o for o in orders if o.status == status]
        return orders

    def get_trades(self, symbol: Optional[str] = None, limit: int = 50) -> List[Trade]:
        """获取成交记录"""
        trades = self.trades
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        return trades[-limit:]

    def place_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: int,
        price: Optional[float] = None
    ) -> Order:
        """
        下单

        Args:
            symbol: 股票代码
            side: 买卖方向
            order_type: 订单类型
            quantity: 数量（必须为100的整数倍）
            price: 限价单价格（限价单必填）

        Returns:
            Order: 订单对象
        """
        # 生成订单ID
        self.order_counter += 1
        order_id = f"ORDER{datetime.now().strftime('%Y%m%d%H%M%S')}{self.order_counter:04d}"

        # 创建订单
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            created_at=datetime.now()
        )

        # 检查订单
        error = self._validate_order(order)
        if error:
            order.status = OrderStatus.REJECTED
            order.reason = error
            self.orders[order_id] = order
            print(f"✗ 订单被拒绝: {error}")
            return order

        # 冻结资金/持仓
        self._freeze_assets(order)

        # 保存订单
        self.orders[order_id] = order

        # 立即处理（市价单）或挂起（限价单）
        if order_type == OrderType.MARKET:
            self._execute_market_order(order)
        else:
            print(f"✓ 限价单已挂起: {order_id}")

        return order

    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        if order_id not in self.orders:
            print(f"✗ 订单不存在: {order_id}")
            return False

        order = self.orders[order_id]

        if order.status != OrderStatus.PENDING:
            print(f"✗ 订单状态不允许撤销: {order.status.value}")
            return False

        # 解冻资产
        self._unfreeze_assets(order)

        # 更新订单状态
        order.status = OrderStatus.CANCELLED
        print(f"✓ 订单已撤销: {order_id}")

        return True

    def update_positions(self, quotes: Dict[str, StockQuote]):
        """更新持仓市值（使用实时行情）"""
        for symbol, position in self.positions.items():
            if symbol in quotes:
                position.update_market_value(quotes[symbol].close)

    def _validate_order(self, order: Order) -> Optional[str]:
        """验证订单"""
        # 检查数量
        if order.quantity <= 0:
            return "数量必须大于0"

        if order.quantity % 100 != 0:
            return "数量必须是100的整数倍"

        # 检查价格（限价单）
        if order.order_type == OrderType.LIMIT and order.price is None:
            return "限价单必须指定价格"

        if order.order_type == OrderType.LIMIT and order.price <= 0:
            return "价格必须大于0"

        # 检查资金（买入）
        if order.side == OrderSide.BUY:
            required_cash = order.quantity * (order.price or 0) * 1.1  # 预留10%
            available_cash = self.cash - self.frozen_cash

            if required_cash > available_cash:
                return f"资金不足: 需要 ¥{required_cash:,.2f}, 可用 ¥{available_cash:,.2f}"

        # 检查持仓（卖出）
        if order.side == OrderSide.SELL:
            if order.symbol not in self.positions:
                return "无持仓"

            position = self.positions[order.symbol]
            if order.quantity > position.available_quantity:
                return f"持仓不足: 需要 {order.quantity}, 可用 {position.available_quantity}"

        return None

    def _freeze_assets(self, order: Order):
        """冻结资产"""
        if order.side == OrderSide.BUY:
            # 冻结资金
            freeze_amount = order.quantity * (order.price or 0) * 1.1
            self.frozen_cash += freeze_amount
        else:
            # 冻结持仓
            if order.symbol in self.positions:
                self.positions[order.symbol].available_quantity -= order.quantity

    def _unfreeze_assets(self, order: Order):
        """解冻资产"""
        if order.side == OrderSide.BUY:
            # 解冻资金
            freeze_amount = order.quantity * (order.price or 0) * 1.1
            self.frozen_cash -= freeze_amount
        else:
            # 解冻持仓
            if order.symbol in self.positions:
                self.positions[order.symbol].available_quantity += order.quantity

    def _execute_market_order(self, order: Order):
        """执行市价单"""
        # 获取实时价格
        if self.data_fetcher:
            try:
                quotes = self.data_fetcher.get_realtime_quotes([order.symbol])
                if order.symbol in quotes:
                    execution_price = quotes[order.symbol].close
                else:
                    # 使用最新收盘价
                    execution_price = order.price or 100.0
            except Exception as e:
                print(f"获取实时价格失败: {e}")
                execution_price = order.price or 100.0
        else:
            execution_price = order.price or 100.0

        # 计算手续费
        commission = max(
            order.quantity * execution_price * self.commission_rate,
            self.min_commission
        )

        # 计算印花税（仅卖出）
        stamp_duty = 0
        if order.side == OrderSide.SELL:
            stamp_duty = order.quantity * execution_price * self.stamp_duty_rate

        total_cost = commission + stamp_duty

        # 执行交易
        if order.side == OrderSide.BUY:
            # 买入
            self.cash -= (order.quantity * execution_price + total_cost)
            self.frozen_cash -= (order.quantity * execution_price * 1.1)

            # 更新持仓
            if order.symbol in self.positions:
                # 加仓
                pos = self.positions[order.symbol]
                total_cost = pos.quantity * pos.avg_price + order.quantity * execution_price
                pos.quantity += order.quantity
                pos.available_quantity += order.quantity
                pos.avg_price = total_cost / pos.quantity
            else:
                # 新建仓位
                self.positions[order.symbol] = Position(
                    symbol=order.symbol,
                    quantity=order.quantity,
                    available_quantity=order.quantity,
                    avg_price=execution_price,
                    current_price=execution_price
                )

        else:
            # 卖出
            self.cash += (order.quantity * execution_price - total_cost)

            # 更新持仓
            pos = self.positions[order.symbol]
            pos.quantity -= order.quantity
            # available_quantity 已在下单时扣除

            # 如果持仓为0，删除
            if pos.quantity == 0:
                del self.positions[order.symbol]

        # 更新订单状态
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.filled_price = execution_price
        order.commission = commission
        order.filled_at = datetime.now()

        # 记录成交
        self.trade_counter += 1
        trade = Trade(
            trade_id=f"TRADE{self.trade_counter:06d}",
            order_id=order.order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            commission=commission,
            trade_time=datetime.now()
        )
        self.trades.append(trade)

        print(f"✓ 订单成交: {order.side.value.upper()} {order.symbol} "
              f"{order.quantity}股 @ ¥{execution_price:.2f}")

    def get_daily_snapshot(self) -> dict:
        """获取每日快照"""
        account = self.get_account_info()

        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "account": account,
            "positions": [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "avg_price": pos.avg_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_pct": pos.unrealized_pnl_pct,
                }
                for pos in self.positions.values()
            ],
            "pending_orders": len([o for o in self.orders.values() if o.status == OrderStatus.PENDING]),
            "today_trades": len([t for t in self.trades if t.trade_time.date() == datetime.now().date()]),
        }


# ============================================
# CLI 测试
# ============================================

def main():
    """测试模拟券商"""
    print("=" * 70)
    print("  模拟券商测试")
    print("=" * 70)

    # 创建模拟券商
    broker = SimulatedBroker(initial_capital=1000000)

    # 连接数据源
    broker.connect_data_source()

    # 获取账户信息
    print("\n账户信息:")
    account = broker.get_account_info()
    print(f"  总资产: ¥{account['total_asset']:,.2f}")
    print(f"  现金: ¥{account['cash']:,.2f}")
    print(f"  持仓数量: {account['positions']}")

    # 模拟下单（测试用，假设价格）
    print("\n测试下单...")
    order = broker.place_order(
        symbol="600519.SH",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=100,
        price=1500.0
    )

    print(f"\n订单状态: {order.status.value}")
    print(f"订单ID: {order.order_id}")

    # 撤销订单
    if order.status == OrderStatus.PENDING:
        broker.cancel_order(order.order_id)

    print("\n✓ 测试完成")


if __name__ == "__main__":
    main()
