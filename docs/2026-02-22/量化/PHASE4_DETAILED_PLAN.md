# Phase 4 实时交易系统 - 详细规划

> 创建日期: 2026-03-02
> 核心哲学: **只响应，不预测**
> 系统定位: 从"预测器"转变为"响应器"

---

## 一、核心哲学转变

### 1.1 认知跃迁

| 维度 | Phase 1-3 (旧思维) | Phase 4 (新思维) |
|:---|:---|:---|
| **时间观** | 预测明天会怎样 | 确认现在在发生什么 |
| **决策依据** | 我觉得、我认为 | 市场说、信号说 |
| **行动时机** | 提前埋伏，等待验证 | 答案出现的那一刻 |
| **错误处理** | 坚持自己的判断 | 立即纠正，跟随市场 |
| **成功标准** | 预测准确率 | 响应速度和一致性 |

### 1.2 三不做 vs 三确认

**三不做**：
- ❌ 不预测明天会怎样
- ❌ 不赌未来走势
- ❌ 不坚持自己的判断

**三确认**：
- ✅ 只确认现在在发生什么
- ✅ 只响应市场给出的信号
- ✅ 只在市场给出答案的那一刻行动

---

## 二、Phase 4 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据源层                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ WebSocket   │  │ 历史数据    │  │ 账户状态    │             │
│  │ 行情推送     │  │ 缓存        │  │ 服务        │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└────────────────────────────┬────────────────────────────────────┘
                             │ Tick数据
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 4 响应引擎                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   感知层 (Perception)                    │   │
│  │  职责: 听市场在说什么，不做判断                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │价格监听 │ │成交量   │ │资金流   │ │盘口情绪 │       │   │
│  │  │突破/跌破│ │放量/缩量│ │大单/主动│ │多空对比 │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             │ MarketSignal[]                    │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   确认层 (Confirmation)                   │   │
│  │  职责: 验证信号的真伪和可靠性                            │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │时间验证 │ │空间验证 │ │共振验证 │ │诱多排除 │       │   │
│  │  │持续性   │ │幅度     │ │多信号   │ │假突破   │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             │ ConfirmedSignal[]                 │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   决策层 (Decision)                       │   │
│  │  职责: 基于确认信号决策行动                              │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │   │
│  │  │买入规则 │ │卖出规则 │ │加减仓   │ │观望规则 │       │   │
│  │  │多信号共 │ │信号消失 │ │信号增强 │ │无确认   │       │   │
│  │  │振入场   │ │立即离场 │ │跟随加仓 │ │保持等待 │       │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                             │                                   │
│                             │ Action[]                          │
│                             ▼                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ AdapterOutput (标准接口)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SkillForge Core (现有)                        │
│  risk_guard → drawdown_limiter → order_router → 执行            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心流程

```python
# 核心循环：永不停止的响应
while market_is_open:
    # 1. 感知：市场现在在说什么？
    raw_signals = perception.listen(tick_data)

    # 2. 确认：它说的是真的吗？
    confirmed_signals = confirmation.verify(raw_signals, tick_data)

    # 3. 决策：我应该怎么做？
    actions = decision.decide(confirmed_signals, positions)

    # 4. 执行：通过 Core 执行
    for action in actions:
        adapter_output = to_adapter_output(action)
        core.execute(adapter_output)

    # 5. 更新状态
    update_state(raw_signals, confirmed_signals, actions)
```

---

## 三、感知层 (Perception Layer) 设计

### 3.1 职责定义

**唯一职责**: 听市场在说什么，不做任何判断

### 3.2 信号定义

#### 3.2.1 价格信号

```python
class PriceSignal:
    """价格信号 - 只记录价格行为，不做判断"""
    signal_type = "price"

    # 监听内容
    current_price: float          # 当前价格
    price_change: float           # 价格变动
    is_breakout_up: bool          # 是否向上突破
    is_breakout_down: bool        # 是否向下突破
    is_new_high: bool             # 是否创新高
    is_new_low: bool              # 是否创新低
    resistance_level: float       # 阻力位
    support_level: float          # 支撑位
```

#### 3.2.2 成交量信号

```python
class VolumeSignal:
    """成交量信号 - 只记录成交量行为"""
    signal_type = "volume"

    # 监听内容
    current_volume: int           # 当前成交量
    volume_ratio: float           # 量比（与均值对比）
    is_volume_surge: bool         # 是否放量
    is_volume_shrink: bool        # 是否缩量
    avg_volume_5m: int            # 5分钟均量
    avg_volume_1h: int            # 1小时均量
```

#### 3.2.3 资金流信号

```python
class MoneyFlowSignal:
    """资金流信号 - 只记录资金行为"""
    signal_type = "money"

    # 监听内容
    big_buy_orders: int           # 大买单数量
    big_sell_orders: int          # 大卖单数量
    net_money_flow: float         # 净资金流
    active_buy_ratio: float       # 主动买占比
    active_sell_ratio: float      # 主动卖占比
    is_big_inflow: bool           # 是否大单流入
    is_big_outflow: bool          # 是否大单流出
```

#### 3.2.4 盘口情绪信号

```python
class SentimentSignal:
    """盘口情绪信号 - 只记录盘口状态"""
    signal_type = "sentiment"

    # 监听内容
    bid_volume: int               # 买盘量
    ask_volume: int               # 卖盘量
    bid_ask_ratio: float          # 买卖比
    spread: float                 # 买卖价差
    order_book_imbalance: float   # 订单簿不平衡度
```

### 3.3 感知层接口

```python
# adapters/quant/phase4/perception.py

class PerceptionLayer:
    """
    感知层 - 只听不说

    原则：
    1. 只记录市场在说什么
    2. 不做任何判断
    3. 不回答"为什么"
    """

    def __init__(self, config: Dict):
        self.price_listener = PriceListener()
        self.volume_listener = VolumeListener()
        self.money_listener = MoneyListener()
        self.sentiment_listener = SentimentListener()

    def listen(self, tick_data: Dict) -> Dict[str, Any]:
        """
        听市场信号

        Args:
            tick_data: 实时tick数据

        Returns:
            原始信号字典，不做任何加工
        """
        signals = {}

        # 听价格在说什么
        signals['price'] = self.price_listener.listen(tick_data)

        # 听成交量在说什么
        signals['volume'] = self.volume_listener.listen(tick_data)

        # 听资金在说什么
        signals['money'] = self.money_listener.listen(tick_data)

        # 听盘口在说什么
        signals['sentiment'] = self.sentiment_listener.listen(tick_data)

        return signals
```

---

## 四、确认层 (Confirmation Layer) 设计

### 4.1 职责定义

**唯一职责**: 验证市场信号的真伪和可靠性

### 4.2 验证规则

> **验证点机制**（来自盘中同步系统）
> 买入不是结束，而是验证的开始。买入后立即设置验证点，要求在30分钟内达到1%涨幅。
> 如果未达成，说明信号可能是假的，需要立即离场。

#### 4.2.1 验证点管理

```python
class ValidationPointManager:
    """
    验证点管理器 - 买入后持续验证

    这是盘中同步系统的核心：买入不是结束，而是验证的开始
    """

    def __init__(self):
        self.validation_points = {}  # symbol -> ValidationPoint

    def create_validation_point(
        self,
        symbol: str,
        entry_price: float,
        entry_time: datetime,
        target_gain: float = 0.01,     # 默认目标1%
        time_window: int = 30           # 默认30分钟
    ) -> ValidationPoint:
        """
        创建验证点 - 买入后立即调用

        验证逻辑：
        - 30分钟内价格需要上涨1%
        - 如果达成，验证通过，继续持有
        - 如果未达成，验证失败，立即离场
        """
        vp = ValidationPoint(
            symbol=symbol,
            entry_price=entry_price,
            entry_time=entry_time,
            target_price=entry_price * (1 + target_gain),
            deadline=entry_time + timedelta(minutes=time_window),
            status='pending'
        )
        self.validation_points[symbol] = vp
        return vp

    def check_validation(self, symbol: str, current_price: float, current_time: datetime) -> ValidationResult:
        """
        检查验证点状态 - 每个tick都调用

        返回行动建议：
        - hold: 继续持有（验证中或已通过）
        - exit: 立即离场（验证失败）
        """
        if symbol not in self.validation_points:
            return ValidationResult(status='no_validation_point')

        vp = self.validation_points[symbol]

        # 检查是否超时
        if current_time > vp.deadline:
            if current_price < vp.target_price:
                # 超时且未达标，验证失败
                vp.status = 'failed'
                return ValidationResult(
                    status='failed',
                    action='exit',
                    reason=f'验证点未达成: 要求30分钟内涨1%, 实际{self._calc_gain(vp.entry_price, current_price):.2%}',
                    confidence=0.8
                )
            else:
                # 超时但已达标，验证通过
                vp.status = 'passed'
                return ValidationResult(
                    status='passed',
                    action='hold',
                    reason='验证点已达成',
                    confidence=0.9
                )

        # 检查是否已达标
        if current_price >= vp.target_price:
            vp.status = 'passed'
            return ValidationResult(
                status='passed',
                action='hold',
                reason=f'验证点达成: {self._calc_gain(vp.entry_price, current_price):.2%}',
                confidence=0.9
            )

        # 还在验证中
        time_remaining = (vp.deadline - current_time).total_seconds() / 60
        return ValidationResult(
            status='pending',
            action='hold',
            reason=f'验证中: 剩余{time_remaining:.1f}分钟, 当前{self._calc_gain(vp.entry_price, current_price):.2%}',
            confidence=0.5
        )
```

#### 4.2.2 时间验证

```python
class TimeConfirmation:
    """时间验证 - 验证信号的持续性"""

    # 规则参数
    MIN_TICKS_SUSTAINED = 3       # 信号至少持续3个tick
    MIN_SECONDS_SUSTAINED = 60    # 信号至少持续60秒

    def verify(self, signal: MarketSignal, history: List) -> bool:
        """
        验证信号是否持续足够时间

        原理：真信号通常会持续，假信号往往是脉冲
        """
        signal_duration = self._calculate_duration(signal, history)
        return signal_duration >= self.MIN_SECONDS_SUSTAINED
```

#### 4.2.2 空间验证

```python
class SpaceConfirmation:
    """空间验证 - 验证信号的幅度"""

    # 规则参数
    MIN_BREAKOUT_AMPLITUDE = 0.02  # 突破幅度至少2%
    MIN_VOLUME_SURGE_RATIO = 1.5   # 放量至少1.5倍

    def verify(self, signal: MarketSignal, tick_data: Dict) -> bool:
        """
        验证信号幅度是否足够

        原理：真突破通常有明显幅度，假突破往往幅度小
        """
        if signal.signal_type == 'price':
            return self._verify_price_amplitude(signal, tick_data)
        elif signal.signal_type == 'volume':
            return self._verify_volume_surge(signal, tick_data)
```

#### 4.2.3 共振验证

```python
class ResonanceConfirmation:
    """共振验证 - 验证多信号是否同步"""

    # 规则参数
    MIN_RESONANCE_COUNT = 2       # 至少2个信号共振（共3个）

    def verify(self, signals: Dict[str, Any]) -> Tuple[bool, int]:
        """
        验证是否有多信号共振

        原理：多信号同时出现，可靠性更高
        """
        resonance_count = 0

        # 统计看涨信号数量
        if signals['price']['breakout_up']: resonance_count += 1
        if signals['volume']['surge']: resonance_count += 1
        if signals['money']['big_inflow']: resonance_count += 1
        if signals['sentiment']['bid_dominant']: resonance_count += 1

        is_resonance = resonance_count >= (self.MIN_RESONANCE_COUNT + 1)
        return is_resonance, resonance_count
```

#### 4.2.4 验证点机制

```python
class ValidationPointManager:
    """
    验证点管理器 - 买入后持续验证

    这是盘中同步系统的核心：买入不是结束，而是验证的开始
    """

    def __init__(self):
        self.validation_points = {}  # symbol -> ValidationPoint

    def create_validation_point(
        self,
        symbol: str,
        entry_price: float,
        entry_time: datetime,
        target_gain: float = 0.01,     # 默认目标1%
        time_window: int = 30           # 默认30分钟
    ) -> ValidationPoint:
        """
        创建验证点

        买入后立即设置验证点，要求在一定时间内达到目标涨幅
        如果未达到，说明信号可能是假的
        """
        vp = ValidationPoint(
            symbol=symbol,
            entry_price=entry_price,
            entry_time=entry_time,
            target_price=entry_price * (1 + target_gain),
            deadline=entry_time + timedelta(minutes=time_window),
            status='pending'
        )
        self.validation_points[symbol] = vp
        return vp

    def check_validation(self, symbol: str, current_price: float, current_time: datetime) -> ValidationResult:
        """
        检查验证点状态

        Returns:
            ValidationResult: 包含验证结果和行动建议
        """
        if symbol not in self.validation_points:
            return ValidationResult(status='no_validation_point')

        vp = self.validation_points[symbol]

        # 检查是否超时
        if current_time > vp.deadline:
            if current_price < vp.target_price:
                # 超时且未达标，验证失败
                vp.status = 'failed'
                return ValidationResult(
                    status='failed',
                    action='exit',
                    reason=f'验证点未达成: 要求30分钟内涨1%, 实际{self._calc_gain(vp.entry_price, current_price):.2%}',
                    confidence=0.8
                )
            else:
                # 超时但已达标，验证通过
                vp.status = 'passed'
                return ValidationResult(
                    status='passed',
                    action='hold',
                    reason='验证点已达成',
                    confidence=0.9
                )

        # 检查是否已达标
        if current_price >= vp.target_price:
            vp.status = 'passed'
            return ValidationResult(
                status='passed',
                action='hold',
                reason=f'验证点达成: {self._calc_gain(vp.entry_price, current_price):.2%}',
                confidence=0.9
            )

        # 还在验证中
        time_remaining = (vp.deadline - current_time).total_seconds() / 60
        return ValidationResult(
            status='pending',
            action='hold',
            reason=f'验证中: 剩余{time_remaining:.1f}分钟, 当前{self._calc_gain(vp.entry_price, current_price):.2%}',
            confidence=0.5
        )

    def _calc_gain(self, entry_price: float, current_price: float) -> float:
        """计算涨幅"""
        return (current_price - entry_price) / entry_price


@dataclass
class ValidationPoint:
    """验证点数据结构"""
    symbol: str
    entry_price: float
    entry_time: datetime
    target_price: float
    deadline: datetime
    status: str  # pending, passed, failed


@dataclass
class ValidationResult:
    """验证结果"""
    status: str    # pending, passed, failed, no_validation_point
    action: str = 'hold'  # hold, exit, add
    reason: str = ''
    confidence: float = 0.0
```

#### 4.2.5 诱多排除

```python
class TrapDetector:
    """诱多检测器 - 识别假突破"""

    def detect(self, signals: Dict[str, Any], history: List) -> bool:
        """
        检测是否是诱多

        特征：
        1. 突破后迅速回落
        2. 放量不涨
        3. 大单流出但价格上涨
        """
        trap_score = 0

        # 特征1：突破后迅速回落
        if self._is_quick_pullback(signals, history):
            trap_score += 2

        # 特征2：放量滞涨
        if self._is_volume_stagnation(signals):
            trap_score += 1

        # 特征3：资金背离
        if self._is_money_divergence(signals):
            trap_score += 2

        return trap_score >= 2  # 达到2分即判定为诱多
```

### 4.3 确认层接口

```python
# adapters/quant/phase4/confirmation.py

class ConfirmationLayer:
    """
    确认层 - 只验证不决策

    原则：
    1. 验证信号的真伪
    2. 评估信号的可靠性
    3. 不做交易决策
    """

    def __init__(self, config: Dict):
        self.time_confirm = TimeConfirmation()
        self.space_confirm = SpaceConfirmation()
        self.resonance_confirm = ResonanceConfirmation()
        self.trap_detector = TrapDetector()

        self.signal_history = {}  # 信号历史

    def verify(self, raw_signals: Dict, tick_data: Dict) -> Dict[str, Any]:
        """
        验证原始信号

        Returns:
            confirmed_signals: 包含验证结果的信号
        """
        confirmed = {}

        # 验证每个信号类型
        for signal_type, signal_value in raw_signals.items():
            confirmed[signal_type] = self._verify_signal(
                signal_type,
                signal_value,
                tick_data
            )

        # 检查多信号共振
        is_resonance, resonance_count = self.resonance_confirm.verify(confirmed)
        confirmed['resonance'] = {
            'is_resonance': is_resonance,
            'count': resonance_count
        }

        # 检查是否是诱多
        confirmed['is_trap'] = self.trap_detector.detect(confirmed, self.signal_history)

        # 更新历史
        self._update_history(raw_signals)

        return confirmed

    def _verify_signal(self, signal_type: str, signal_value: Any, tick_data: Dict) -> Dict:
        """验证单个信号"""
        result = {
            'original': signal_value,
            'time_confirmed': False,
            'space_confirmed': False,
            'final_confirmed': False
        }

        # 时间验证
        result['time_confirmed'] = self.time_confirm.verify(signal_value, self.signal_history)

        # 空间验证
        result['space_confirmed'] = self.space_confirm.verify(signal_value, tick_data)

        # 最终确认
        result['final_confirmed'] = (
            result['time_confirmed'] and
            result['space_confirmed']
        )

        return result
```

---

## 五、决策层 (Decision Layer) 设计

### 5.1 职责定义

**唯一职责**: 基于确认的信号决定行动

### 5.2 决策规则

#### 5.2.1 买入规则

```python
class BuyRule:
    """买入规则 - 只在信号确认时买入"""

    # 规则条件（需全部满足）
    CONDITIONS = [
        "price.breakout_up AND price.confirmed",      # 价格突破且确认
        "volume.surge AND volume.confirmed",          # 成交量放大且确认
        "money.big_inflow OR sentiment.bid_dominant", # 资金流入或买盘占优
        "resonance.count >= 3",                       # 至少3个信号共振
        "NOT is_trap"                                 # 不是诱多
    ]

    def evaluate(self, confirmed: Dict, positions: Dict) -> Optional[Action]:
        """
        评估买入条件

        原则：只在市场给出明确买入信号时行动
        """
        # 检查是否已有持仓
        if positions:
            return None  # 有持仓时不买

        # 检查买入条件
        conditions_met = all([
            confirmed['price']['final_confirmed'],
            confirmed['volume']['final_confirmed'],
            confirmed.get('money', {}).get('big_inflow', False) or
            confirmed.get('sentiment', {}).get('bid_dominant', False),
            confirmed['resonance']['count'] >= 3,
            not confirmed['is_trap']
        ])

        if conditions_met:
            return Action(
                action_type='BUY',
                symbol=confirmed['symbol'],
                quantity=self._calculate_quantity(confirmed),
                confidence=self._calculate_confidence(confirmed),
                reason="多信号共振确认上涨"
            )

        return None
```

#### 5.2.2 卖出规则

```python
class SellRule:
    """卖出规则 - 信号消失时立即离场"""

    # 规则条件（任一满足即卖出）
    CONDITIONS = [
        "price.breakdown_down",           # 价格跌破
        "money.big_outflow",              # 大单流出
        "is_trap",                        # 发现是诱多
        "signal_lost"                     # 原买入信号消失
    ]

    def evaluate(self, confirmed: Dict, positions: Dict) -> Optional[Action]:
        """
        评估卖出条件

        原则：信号消失时立即离场，不犹豫
        """
        for symbol, position in positions.items():
            # 检查卖出条件
            sell_conditions = [
                confirmed['price'].get('breakdown_down', False),
                confirmed.get('money', {}).get('big_outflow', False),
                confirmed['is_trap'],
                self._is_signal_lost(confirmed, position)
            ]

            if any(sell_conditions):
                return Action(
                    action_type='SELL',
                    symbol=symbol,
                    quantity=position['quantity'],
                    confidence=1.0,  # 卖出总是高置信度
                    reason=self._get_sell_reason(confirmed)
                )

        return None
```

### 5.3 决策层接口

```python
# adapters/quant/phase4/decision.py

class DecisionLayer:
    """
    决策层 - 只决策不预测

    原则：
    1. 基于确认的信号决策
    2. 不预测未来走势
    3. 信号消失立即行动
    4. 买入后持续验证（验证点机制）
    """

    def __init__(self, config: Dict):
        self.buy_rule = BuyRule()
        self.sell_rule = SellRule()
        self.add_rule = AddRule()
        self.reduce_rule = ReduceRule()
        self.wait_rule = WaitRule()

        # 验证点管理器
        self.validation_manager = ValidationPointManager()

    def decide(self, confirmed: Dict, positions: Dict, tick_data: Dict) -> List[Action]:
        """
        基于确认信号决定行动

        Returns:
            actions: 行动列表（可能为空）
        """
        actions = []

        # 0. 首先检查现有持仓的验证点
        for symbol, position in positions.items():
            validation_result = self.validation_manager.check_validation(
                symbol,
                tick_data['price'],
                tick_data['time']
            )

            if validation_result.action == 'exit':
                actions.append(Action(
                    action_type='SELL',
                    symbol=symbol,
                    quantity=position['quantity'],
                    confidence=validation_result.confidence,
                    reason=f"验证点失败: {validation_result.reason}"
                ))

        # 如果有卖出行动，优先处理
        if actions:
            return actions

        # 1. 评估买入规则
        buy_action = self.buy_rule.evaluate(confirmed, positions)
        if buy_action:
            actions.append(buy_action)

            # 买入后立即创建验证点
            self.validation_manager.create_validation_point(
                symbol=buy_action.symbol,
                entry_price=buy_action.price,
                entry_time=tick_data['time'],
                target_gain=0.01,  # 1%
                time_window=30     # 30分钟
            )

        # 2. 评估其他规则
        add_action = self.add_rule.evaluate(confirmed, positions)
        if add_action:
            actions.append(add_action)

        reduce_action = self.reduce_rule.evaluate(confirmed, positions)
        if reduce_action:
            actions.append(reduce_action)

        # 3. 如果没有行动，返回等待
        if not actions:
            wait_action = self.wait_rule.evaluate(confirmed, positions)
            if wait_action:
                actions.append(wait_action)

        return actions
```

---

## 六、Phase 4 引擎集成

### 6.1 主引擎设计

```python
# adapters/quant/phase4/engine.py

class Phase4Engine:
    """
    Phase 4 实时交易引擎

    核心哲学：只响应，不预测
    """

    def __init__(self, config: Dict):
        # 三层架构
        self.perception = PerceptionLayer(config)
        self.confirmation = ConfirmationLayer(config)
        self.decision = DecisionLayer(config)

        # 状态管理
        self.positions = {}
        self.state = {
            'raw_signals': {},
            'confirmed_signals': {},
            'actions': []
        }

        # Core 集成
        from skillforge.src.skills.quant.execute import ExecuteSkill
        self.core_executor = ExecuteSkill()

    def on_tick(self, tick_data: Dict):
        """
        处理实时tick数据 - 核心响应循环

        这是系统的心跳，每次tick都会执行
        """
        # 1. 感知：市场现在在说什么？
        raw_signals = self.perception.listen(tick_data)
        self.state['raw_signals'] = raw_signals

        # 2. 确认：它说的是真的吗？
        confirmed_signals = self.confirmation.verify(raw_signals, tick_data)
        self.state['confirmed_signals'] = confirmed_signals

        # 3. 决策：我应该怎么做？
        actions = self.decision.decide(confirmed_signals, self.positions)
        self.state['actions'] = actions

        # 4. 执行：通过 Core 执行
        for action in actions:
            self._execute_via_core(action, tick_data)

    def _execute_via_core(self, action: Action, tick_data: Dict):
        """
        通过 Core 执行行动

        这确保了所有行动都经过风控检查
        """
        # 转换为标准 AdapterOutput
        adapter_output = self._to_adapter_output(action, tick_data)

        # 通过 Core 执行
        result = self.core_executor.execute(
            intent=adapter_output.intent,
            context=adapter_output.context
        )

        # 更新持仓
        if result.status == 'FILLED':
            self._update_positions(action, result)

    def _to_adapter_output(self, action: Action, tick_data: Dict) -> AdapterOutput:
        """转换为标准 AdapterOutput"""
        from adapters.quant.contracts import (
            AdapterOutput, AdapterStatus,
            TradingIntent, SignalAction, AdapterContext
        )

        intent = TradingIntent(
            action=SignalAction[action.action_type],
            symbol=action.symbol,
            quantity=action.quantity,
            price=action.price,
            confidence=action.confidence,
            reasoning=action.reason
        )

        context = AdapterContext(
            job_id=f"phase4_{tick_data['timestamp']}",
            trace_id=str(uuid.uuid4())
        )

        return AdapterOutput(
            status=AdapterStatus.SUCCESS,
            intent=intent,
            context=context
        )
```

### 6.2 与现有系统集成

```
现有系统                    Phase 4 新增
│                           │
│  Adapter 层               │  Phase 4 引擎
│  ├─ signal_generator  ←───┼── perception_layer
│  ├─ stock_selector    ←───┼── confirmation_layer
│  └─ etf_rotation       ←───┼── decision_layer
│                           │
│  Core 层                  │  (通过标准接口集成)
│  ├─ risk_guard       ←────────┐
│  ├─ drawdown_limiter  ←──────┤
│  └─ order_router     ←───────┘
│                           │
└───────────────────────────┘
```

---

## 七、实施计划

### 7.1 Phase 4.1 - 基础框架 (Week 1)

**目标**: 搭建三层架构框架

| 任务 | 文件 | 描述 |
|------|------|------|
| 创建基础目录 | `adapters/quant/phase4/` | 新建 phase4 模块目录 |
| 感知层框架 | `perception.py` | 实现感知层基础结构 |
| 确认层框架 | `confirmation.py` | 实现确认层基础结构 |
| 决策层框架 | `decision.py` | 实现决策层基础结构 |
| 主引擎框架 | `engine.py` | 实现 Phase4Engine 基础结构 |
| 单元测试 | `test_phase4_basic.py` | 验证框架正确性 |

### 7.2 Phase 4.2 - 信号实现 (Week 2)

**目标**: 实现具体的信号监听和验证

| 任务 | 文件 | 描述 |
|------|------|------|
| 价格监听器 | `perception/price_listener.py` | 实现价格信号监听 |
| 成交量监听器 | `perception/volume_listener.py` | 实现成交量信号监听 |
| 资金流监听器 | `perception/money_listener.py` | 实现资金流信号监听 |
| 时间验证器 | `confirmation/time_confirm.py` | 实现时间验证逻辑 |
| 空间验证器 | `confirmation/space_confirm.py` | 实现空间验证逻辑 |
| 单元测试 | `test_signals.py` | 验证信号正确性 |

### 7.3 Phase 4.3 - 验证机制 (Week 3)

**目标**: 实现完整的信号验证机制

| 任务 | 文件 | 描述 |
|------|------|------|
| 共振验证 | `confirmation/resonance.py` | 实现多信号共振验证 |
| 诱多检测 | `confirmation/trap_detector.py` | 实现诱多识别算法 |
| 买入规则 | `decision/buy_rule.py` | 实现买入决策规则 |
| 卖出规则 | `decision/sell_rule.py` | 实现卖出决策规则 |
| 单元测试 | `test_confirmation.py` | 验证验证逻辑 |

### 7.4 Phase 4.4 - 集成测试 (Week 4)

**目标**: 完整系统集成和回测验证

| 任务 | 文件 | 描述 |
|------|------|------|
| 完整引擎 | `engine.py` | 完善主引擎逻辑 |
| Core 集成 | `engine.py` | 完成与 Core 的集成 |
| 回测框架 | `backtest/` | 实现回测验证框架 |
| 回测验证 | `test_backtest.py` | 执行历史数据回测 |
| 性能测试 | `test_performance.py` | 验证响应速度 |

### 7.5 Phase 4.5 - 实盘准备 (Week 5+)

**目标**: 模拟盘测试和实盘准备

| 任务 | 描述 |
|------|------|
| 模拟盘测试 | 在模拟环境中运行 |
| 参数优化 | 根据测试结果优化参数 |
| 风险评估 | 评估系统风险 |
| 实盘演练 | 小资金实盘测试 |

---

## 八、验证标准

### 8.1 Phase 4 系统特有指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **响应速度** | 从信号出现到行动的时间 | < 5秒 |
| **响应一致性** | 同信号同样行动的比例 | > 95% |
| **信号准确率** | 确认后信号的胜率 | > 65% |
| **诱多识别率** | 诱多被成功识别的比例 | > 80% |
| **共振胜率** | 共振信号的胜率 | > 75% |

### 8.2 回测报告格式

```
========== Phase 4 系统回测报告 ==========

【响应能力】
- 平均响应时间: X.X秒
- 响应一致性: XX.X%
- 信号确认率: XX.X%

【信号质量】
- 价格信号准确率: XX.X%
- 成交量信号准确率: XX.X%
- 资金流信号准确率: XX.X%
- 三信号共振准确率: XX.X%

【风控能力】
- 诱多识别率: XX.X%
- 假突破过滤率: XX.X%
- 平均止损幅度: -X.X%

【执行效果】
- 总收益率: XX.X%
- 夏普比率: X.XX
- 最大回撤: -XX.X%
- 胜率: XX.X%
- 盈亏比: X.X

=========================================
```

---

## 九、配置文件

### 9.1 Phase 4 配置

```yaml
# configs/phase4_config.yaml

# 感知层配置
perception:
  price:
    resistance_lookback: 20  # 阻力位回看周期
    support_lookback: 20     # 支撑位回看周期
  volume:
    avg_period: 60           # 平均成交量周期（秒）
  money:
    big_order_threshold: 10000  # 大单阈值
  sentiment:
    imbalance_threshold: 0.3  # 不平衡阈值

# 确认层配置
confirmation:
  time:
    min_ticks: 3             # 最小持续tick数
    min_seconds: 60          # 最小持续秒数
  space:
    min_breakout_amp: 0.02   # 最小突破幅度
    min_volume_ratio: 1.5    # 最小放量倍数
  resonance:
    min_count: 3             # 最小共振信号数

# 决策层配置
decision:
  buy:
    min_confidence: 0.6      # 最小买入置信度
    max_position_ratio: 0.3  # 单股最大仓位比例
  sell:
    stop_loss: -0.03         # 止损比例
    signal_loss_exit: true   # 信号消失即离场

# 系统配置
system:
  mode: paper                # mock/paper/live
  log_level: INFO
  metrics_enabled: true
```

---

## 十、风险控制

### 10.1 Phase 4 特有风险

| 风险 | 描述 | 应对 |
|------|------|------|
| **过度响应** | 对噪音信号频繁交易 | 提高确认阈值 |
| **确认延迟** | 确认时间过长错过机会 | 优化确认算法 |
| **假信号** | 诱多未被识别 | 加强诱多检测 |
| **系统故障** | 实时系统故障 | 熔断机制 |

### 10.2 熔断机制

```python
class CircuitBreaker:
    """熔断机制 - Phase 4 系统保护"""

    # 熔断条件
    MAX_DAILY_LOSS = -0.05    # 单日亏损超过5%熔断
    MAX_CONSECUTIVE_LOSSES = 5 # 连续5次亏损熔断
    MAX_RESPONSE_DELAY = 10   # 响应延迟超过10秒熔断

    def check(self, state: Dict) -> bool:
        """检查是否需要熔断"""
        if state['daily_pnl'] < self.MAX_DAILY_LOSS:
            return True
        if state['consecutive_losses'] >= self.MAX_CONSECUTIVE_LOSSES:
            return True
        if state['avg_response_time'] > self.MAX_RESPONSE_DELAY:
            return True
        return False
```

---

*最后更新: 2026-03-02*
