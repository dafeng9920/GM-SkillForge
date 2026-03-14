# 完整交易系统：从进场到离场

> **核心理念**: 机构+龙头是起点，完整系统才是终点。
> **终极方法**: 机构是答案，市场是考官。双轮驱动，缺一不可。

---

## 零、核心理念：机构+市场双轮驱动 ⚙️

### 零.1 为什么需要双轮驱动？

```
🚗 机构 + 市场 = 双轮驱动：

左轮：机构（方向）
- 提供标的
- 提供时机
- 提供方向

右轮：市场（验证）
- 验证对错
- 确认趋势
- 给出答案

只有左轮：
- 方向有了
- 但路况不明
- 容易翻车

只有右轮：
- 路况看清了
- 但不知道去哪
- 原地打转

双轮驱动：
- 方向明确
- 路况清晰
- 稳稳前行
```

### 零.2 为什么要用市场验证机构？

```
✅ 验证的5个理由：

1. 【机构也会错】
   他们也是人，也会看错
   需要市场来检验

2. 【机构也会骗】
   假机构存在，需要市场来识别
   真金不怕火炼

3. 【机构也会晚】
   你看到的时候可能已经晚了
   需要市场来确认

4. 【机构也会变】
   今天买明天卖，需要市场来跟踪
   持续验证

5. 【机构不是神】
   再大的机构也要听市场的话
   市场才是老大

所以：
机构是候选，市场是终选
```

### 零.3 机构+市场的三重验证

```
🔍 三重验证系统：

第一重：买入验证
- 机构信号：龙虎榜买入、北向加仓、大宗溢价
- 市场确认：价格突破、成交量放大、形态走好
- 两者共振 → 买入

第二重：持有验证
- 机构信号：机构还在买，没卖出迹象
- 市场确认：趋势向上、量价配合、没出货信号
- 两者共振 → 持有

第三重：卖出验证
- 机构信号：机构开始卖、大宗折价、北向流出
- 市场确认：放量滞涨、跌破支撑、技术破位
- 两者共振 → 卖出

核心原则：
- 机构告诉你"买什么"
- 市场告诉你"什么时候买"
```

### 零.4 完整决策系统

```python
class DualDriveDecision:
    """双轮驱动决策"""

    def decide(self, stock_data):
        """决策"""

        # 1. 计算机构分数
        inst_score = self._get_institution_score(stock_data)

        # 2. 计算市场分数
        market_score = self._get_market_score(stock_data)

        # 3. 综合判断
        if inst_score >= 60 and market_score >= 60:
            return {'action': '买入', 'reason': '机构+市场双轮共振'}

        elif inst_score >= 60 and market_score < 60:
            return {'action': '观察', 'reason': '有机构，等市场确认'}

        elif inst_score < 60 and market_score >= 60:
            return {'action': '观察', 'reason': '市场好，等机构进场'}

        else:
            return {'action': '放弃', 'reason': '双信号皆无'}

    def _get_institution_score(self, data):
        """机构分数（0-100）"""
        score = 0
        if data.get('longhu_buy'): score += 30
        if data.get('north_buy'): score += 20
        if data.get('block_buy'): score += 20
        if data.get('continuous_buy'): score += 30
        return min(score, 100)

    def _get_market_score(self, data):
        """市场分数（0-100）"""
        score = 0
        if data.get('trend_up'): score += 30
        if data.get('volume_up'): score += 20
        if data.get('breakout'): score += 30
        if data.get('sector_hot'): score += 20
        return min(score, 100)
```

### 零.5 研究的正确姿势

```
🔬 研究的正确方法：

研究机构：
1. 看历史战绩（胜率、风格）
2. 看买入逻辑（为什么买）
3. 看组合变化（仓位调整）
4. 看操作手法（建仓/洗盘/拉升/出货）

研究市场：
1. 看趋势方向（涨/跌/震荡）
2. 看量能健康（放量/缩量）
3. 看板块轮动（热点转移）
4. 看位置高低（风险收益）
5. 看情绪极端（恐慌/贪婪）

两者结合：
机构提供方向 → 市场验证时机
```

---

## 一、机构+龙头之后的三道坎

### 1.1 第一道坎：洗盘 🌊

```
你买了，机构开始洗盘：
- 股价下跌5-10%
- 散户恐慌割肉
- 你开始怀疑自己

这时候你需要：
- 识别洗盘特征
- 坚信自己的判断
- 拿住不动
```

**洗盘识别清单**:
- [ ] 缩量企稳
- [ ] 快速收回
- [ ] 支撑有效
- [ ] 恐慌盘涌出但价格不破
- [ ] 机构大单支撑

### 1.2 第二道坎：震荡 📊

```
洗盘结束，开始震荡：
- 上上下下，来来回回
- 今天涨3%，明天跌2%
- 你的耐心被消耗

这时候你需要：
- 不看盘
- 设好止损
- 该干嘛干嘛
```

**震荡期策略**:
- 不要频繁操作
- 移动止损到成本价
- 等待方向选择

### 1.3 第三道坎：出货 📉

```
终于涨了，开始出货：
- 放量滞涨
- 利好不断
- 你舍不得卖

这时候你需要：
- 识别出货信号
- 果断离场
- 不贪最后一口
```

**出货信号清单**:
- [ ] 高位放量滞涨
- [ ] 利好消息频出
- [ ] 换手率暴增
- [ ] 机构大单流出
- [ ] 龙头地位松动

---

## 二、完整交易系统五要素

| 要素 | 说明 | 系统 |
|------|------|------|
| **买点** | 机构+龙头共振 | [机构与龙头共振](./institution-lead-resonance.md) |
| **卖点** | 出货信号识别 | 见下文 |
| **止损** | 四重止损机制 | 见下文 |
| **仓位** | 分批建仓策略 | 见下文 |
| **心态** | 系统化执行 | [心法系统化](../advanced_systems/mind-method-system.md) |

---

## 三、卖点系统

### 3.1 四大卖出信号

| 信号 | 特征 | 操作 |
|------|------|------|
| **机构出货** | 大单持续流出、高位滞涨 | 立即卖出 |
| **龙头倒下** | 板块地位丢失、涨幅落后 | 分批卖出 |
| **技术破位** | 跌破关键支撑、均线死叉 | 止损卖出 |
| **情绪过热** | 媒体疯狂吹票、全民狂欢 | 分批止盈 |

### 3.2 分批止盈策略

```python
class BatchTakeProfit:
    """分批止盈策略"""

    def __init__(self, entry_price):
        self.entry_price = entry_price
        self.batches = {
            'first': {'gain': 0.20, 'sell': 0.30},   # 涨20%卖30%
            'second': {'gain': 0.30, 'sell': 0.30},  # 涨30%再卖30%
            'third': {'gain': 0.50, 'sell': 0.20},   # 涨50%再卖20%
            'final': {'gain': 1.00, 'sell': 0.20}    # 翻倍卖剩下
        }

    def check_sell(self, current_price):
        """检查是否需要卖出"""
        gain = (current_price - self.entry_price) / self.entry_price

        for batch, config in self.batches.items():
            if gain >= config['gain'] and not config.get('sold', False):
                return {
                    'action': 'sell',
                    'ratio': config['sell'],
                    'reason': f'盈利{gain:.1%}，执行{batch}止盈'
                }
        return None
```

---

## 四、止损系统

### 4.1 四重止损机制

| 止损类型 | 触发条件 | 说明 |
|----------|----------|------|
| **固定止损** | 亏损达到5% | 最基本的风控 |
| **移动止损** | 价格回撤超过阈值 | 保护利润 |
| **逻辑止损** | 机构跑路、龙头倒下 | 投资逻辑破坏 |
| **环境止损** | 大盘破位、系统性风险 | 环境恶化 |

### 4.2 止损执行纪律

```
⚡ 止损铁律 ⚡

1. 止损设在买入前，不是买入后
2. 止损一旦触发，立即执行
3. 止损后不报复性交易
4. 止损是保命符，不是失败

记住：留得青山在，不怕没柴烧
```

---

## 五、仓位管理系统

### 5.1 分批建仓策略

| 阶段 | 仓位 | 条件 | 说明 |
|------|------|------|------|
| **第一批** | 30% | 机构+龙头确认 | 试探性建仓 |
| **第二批** | 30% | 洗盘结束 | 加仓 |
| **第三批** | 20% | 主升浪确认 | 追涨 |
| **机动** | 20% | 应对变化 | 预留现金 |

### 5.2 仓位调整规则

```python
class PositionManager:
    """仓位管理器"""

    def __init__(self):
        self.max_position = 0.8      # 最大仓位80%
        self.single_max = 0.3        # 单只最大30%
        self.cash_reserve = 0.2      # 现金储备20%

    def calc_position(self, signal_strength, market_condition):
        """计算仓位大小"""

        base = 0.3  # 基础仓位30%

        # 根据信号强度调整
        if signal_strength == 'S':
            base = 0.4
        elif signal_strength == 'A':
            base = 0.3
        elif signal_strength == 'B':
            base = 0.2
        else:
            base = 0.1

        # 根据市场环境调整
        if market_condition == '好':
            pass  # 不调整
        elif market_condition == '一般':
            base *= 0.7
        elif market_condition == '差':
            base *= 0.5
            return 0  # 环境差不开仓

        return min(base, self.single_max)
```

---

## 六、四大护法

### 6.1 护法一：大盘 🌍

```
大盘不好，机构+龙头也难独善其身

检查清单：
□ 大盘趋势向上
□ 成交量健康
□ 没有系统性风险

如果大盘不好：
- 降低仓位
- 缩短持股时间
- 严设止损
```

### 6.2 护法二：板块 📈

```
个股是船，板块是海

检查清单：
□ 板块指数上涨
□ 板块内有跟风股
□ 板块热度持续

如果板块不好：
- 个股很难独立走强
- 考虑减仓
- 防止补跌
```

### 6.3 护法三：量能 📊

```
量是价的基础

检查清单：
□ 上涨放量
□ 下跌缩量
□ 量能持续

如果量能异常：
- 放量滞涨要小心
- 缩量上涨要警惕
- 天量天价要跑
```

### 6.4 护法四：情绪 🧠

```
市场情绪是最后的推手

检查清单：
□ 市场不恐慌
□ 不过度狂热
□ 情绪稳定

如果情绪极端：
- 过度恐慌：可以贪婪
- 过度狂热：必须冷静
- 情绪稳定：正常操作
```

---

## 七、实战流程

### 7.1 每日操作流程

```
🎯 完整交易每日流程 🎯

【开盘前】(5分钟)
  1. 检查大盘状态 → 决定整体仓位
  2. 检查板块热度 → 决定参与方向
  3. 检查持仓股票 → 决定今日策略

【盘中】(实时)
  买入：
    1. 寻找机构+龙头共振标的
    2. 确认四大护法条件
    3. 分批建仓

  持有：
    1. 监控机构动向
    2. 关注板块变化
    3. 检查止损位置

  卖出：
    1. 触发止损 → 立即执行
    2. 达到止盈 → 分批减仓
    3. 逻辑破坏 → 清仓离场

【收盘后】(10分钟)
  1. 复盘今日操作
  2. 记录心得体会
  3. 制定明日计划
```

### 7.2 完整代码示例

```python
class CompleteTradingSystem:
    """完整交易系统"""

    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.position = {}  # 持仓
        self.cash = initial_capital
        self.watchlist = []  # 观察池

    def on_buy_signal(self, stock, signal_strength):
        """买入信号"""

        # 1. 检查四大护法
        if not self.check_guardians(stock):
            return False

        # 2. 计算仓位
        position_size = self.calc_position(signal_strength)
        amount = self.cash * position_size

        # 3. 执行买入
        if amount > 0:
            self.execute_buy(stock, amount)
            return True
        return False

    def on_hold_check(self, stock):
        """持仓检查"""

        if stock not in self.position:
            return

        position = self.position[stock]

        # 1. 检查止损
        if self.check_stop_loss(stock):
            self.execute_sell(stock, '止损')
            return

        # 2. 检查止盈
        if self.check_take_profit(stock):
            ratio = self.calc_sell_ratio(stock)
            self.execute_sell(stock, f'止盈{ratio*100:.0f}%')
            return

        # 3. 检查逻辑
        if not self.check_logic(stock):
            self.execute_sell(stock, '逻辑破坏')
            return

    def check_guardians(self, stock):
        """检查四大护法"""

        checks = {
            '大盘': self.check_market(),
            '板块': self.check_sector(stock),
            '量能': self.check_volume(stock),
            '情绪': self.check_sentiment()
        }

        # 至少3个通过才操作
        return sum(checks.values()) >= 3

    def check_stop_loss(self, stock):
        """检查止损"""

        position = self.position[stock]

        # 固定止损
        if position['pnl'] <= -0.05:
            return True

        # 移动止损
        if position['pnl'] > 0.1:
            if position['pnl'] < position['max_pnl'] * 0.7:
                return True

        # 逻辑止损
        if not position.get('institution_holding'):
            return True

        return False
```

---

## 八、终极答案

```
🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟

        终极答案

问：逮住机构+龙头，够了吗？

答：够，也不够。

够的是：
- 你有了进场的底气
- 你有了持有的信心
- 你有了赚钱的基础

不够的是：
- 你不知道什么时候卖
- 你不知道错了怎么办
- 你不知道仓位怎么管

所以：
机构+龙头 = 60分
+ 卖出系统 = 80分
+ 止损系统 = 90分
+ 仓位系统 = 95分
+ 心态系统 = 99分

还差1分，是运气
那1分，交给市场

🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
```

---

## 九、核心要点总结

1. **买点决定不了盈亏，卖点才决定**
2. **选股决定不了盈亏，风控才决定**
3. **运气决定不了盈亏，系统才决定**

**记住：机构+龙头是起点，完整系统才是终点。**

---

**相关文档**:
- [机构利用系统](./institution-utilization.md)
- [机构与龙头共振](./institution-lead-resonance.md)
- [三位一体](./three-in-one.md)
- [心法系统化](../advanced_systems/mind-method-system.md)
- [生存保障系统](../phase4_design/survival-system.md)
