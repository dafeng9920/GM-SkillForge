# Phase 1: 数据层Skills实施指南

> 时间: 2周
> 目标: 实现数据获取和管理的6个Skills
> 状态: 准备开始

---

## Skill清单

### 1. openbb-fetch Skill
**职责**: 多源数据获取

**输入**:
- symbols: 标的代码列表
- data_type: 数据类型 (历史价格/基本面/经济指标)
- provider: 数据提供商 (yahoo/fmp/polygon)
- start_date/end_date: 时间范围

**输出**:
- status: 完成状态
- data: OHLCV数据框
- provenance: 数据来源信息
- metrics: 获取行数、延迟

**文件结构**:
```
skills/openbb-fetch/
├── schemas/
│   ├── input.schema.json
│   └── output.schema.json
├── implementation/
│   └── openbb_fetch.py
├── tests/
│   └── test_openbb_fetch.py
└── README.md
```

---

### 2. data-cleaner Skill
**职责**: 数据清洗（缺失值、异常值）

**输入**:
- raw_df: 原始数据框
- rules: 清洗规则配置

**输出**:
- cleaned_df: 清洗后数据框
- cleaning_report: 清洗报告
- metrics: 清洗统计

**功能**:
- 缺失值处理 (前向填充/删除/插值)
- 异常值检测 (3-sigma/IQR)
- 数据类型转换
- 重复数据处理

---

### 3. data-validator Skill
**职责**: 数据质量校验

**输入**:
- df: 待校验数据框
- schema: 数据模式定义

**输出**:
- validation_report: 校验报告
- is_valid: 是否通过校验
- errors: 错误列表
- warnings: 警告列表

**校验项**:
- 必填字段检查
- 数据类型检查
- 取值范围检查
- 业务规则检查
- 时间序列连续性

---

### 4. data-versioner Skill
**职责**: 数据版本控制

**输入**:
- df: 数据框
- snapshot_id: 快照ID

**输出**:
- version_ref: 版本引用
- data_hash: 数据哈希
- metadata: 版本元数据

**功能**:
- 生成数据哈希
- 创建版本标签
- 存储到MinIO
- Git/DVC集成

---

### 5. data-enricher Skill
**职责**: 数据增强（衍生指标）

**输入**:
- df: 基础OHLCV数据
- indicators: 指标列表

**输出**:
- enriched_df: 增强后数据
- indicator_results: 指标计算结果

**支持的指标**:
- 移动平均 (SMA/EMA)
- 动量指标 (RSI/MACD)
- 波动率指标 (ATR/Bollinger)
- 成交量指标 (OBV)

---

### 6. data-syncer Skill
**职责**: 增量数据同步

**输入**:
- symbols: 标的列表
- last_timestamp: 上次同步时间

**输出**:
- delta_df: 增量数据
- sync_status: 同步状态
- next_update_time: 下次更新时间

**功能**:
- 增量拉取
- 数据去重
- 断点续传
- 数据合并

---

## 实施计划

### Week 1: 核心数据获取

**Day 1-2: openbb-fetch Skill**
- [ ] 创建输入/输出schema
- [ ] 实现核心逻辑
- [ ] 编写单元测试
- [ ] 集成OpenBB SDK

**Day 3-4: data-cleaner Skill**
- [ ] 创建清洗规则框架
- [ ] 实现缺失值处理
- [ ] 实现异常值检测
- [ ] 编写测试用例

**Day 5: data-validator Skill**
- [ ] 定义schema格式
- [ ] 实现校验逻辑
- [ ] 支持自定义规则
- [ ] 性能优化

### Week 2: 数据管理

**Day 1-2: data-versioner Skill**
- [ ] 实现哈希算法
- [ ] 集成MinIO
- [ ] 版本元数据管理
- [ ] 回滚功能

**Day 3-4: data-enricher Skill**
- [ ] 集成TA-Lib
- [ ] 实现常用指标
- [ ] 批量计算优化
- [ ] 指标缓存

**Day 5: data-syncer Skill**
- [ ] 增量拉取逻辑
- [ ] 数据合并策略
- [ ] 定时任务调度
- [ ] 错误重试

**Day 6-7: 集成测试**
- [ ] 端到端流程测试
- [ ] 性能压测
- [ ] 文档完善
- [ ] 示例代码

---

## 技术要点

### 1. OpenBB集成

```python
from openbb import obb

# 获取历史价格
data = obb.equity.price.historical(
    symbol="AAPL",
    provider="yahoo",
    start_date="2023-01-01",
    end_date="2023-12-31"
)
df = data.to_dataframe()
```

### 2. TA-Lib指标计算

```python
import talib

# 移动平均
sma = talib.SMA(df['close'], timeperiod=20)

# RSI
rsi = talib.RSI(df['close'], timeperiod=14)

# MACD
macd, signal, hist = talib.MACD(df['close'])
```

### 3. MinIO对象存储

```python
from minio import Minio

client = Minio(
    'localhost:9001',
    access_key='minioadmin',
    secret_key='minioadmin_change_me'
)

# 上传数据
client.fput_object(
    'backtest-reports',
    'report_20240309.csv',
    'report_data.csv'
)
```

### 4. PostgreSQL元数据

```python
import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='quant_meta',
    user='quant_admin',
    password='quant_secure_change_me'
)

# 查询策略配置
cursor = conn.cursor()
cursor.execute("""
    SELECT name, version, config
    FROM quant_config.strategies
    WHERE status = 'active'
""")
strategies = cursor.fetchall()
```

---

## 测试策略

### 单元测试

每个Skill需要以下测试:
- 正常流程测试
- 异常处理测试
- 边界条件测试
- 性能测试

### 集成测试

- 数据流测试: 从获取到清洗到校验
- 存储测试: 验证数据正确存储
- API测试: 验证接口调用

---

## 交付物

Week 1:
- [ ] openbb-fetch Skill
- [ ] data-cleaner Skill
- [ ] data-validator Skill
- [ ] 单元测试通过

Week 2:
- [ ] data-versioner Skill
- [ ] data-enricher Skill
- [ ] data-syncer Skill
- [ ] 集成测试通过
- [ ] API文档

---

## 验收标准

### 功能验收
- [ ] 所有6个Skills能独立运行
- [ ] 数据管道完整打通
- [ ] 支持多数据源
- [ ] 增量同步正常工作

### 性能验收
- [ ] 单次数据获取 < 5秒
- [ ] 清洗处理 > 10000行/秒
- [ ] 数据校验延迟 < 100ms
- [ ] 存储吞吐 > 1000条/秒

### 质量验收
- [ ] 单元测试覆盖率 > 80%
- [ ] 集成测试通过率 100%
- [ ] 文档完整度 100%
- [ ] 代码审查通过

---

## 下一步

Phase 1完成后，进入 **Phase 2: 研发层Skills**

详见: [PHASE2_RESEARCH_LAYER.md](./PHASE2_RESEARCH_LAYER.md)

---

*更新时间: 2026-03-09*
