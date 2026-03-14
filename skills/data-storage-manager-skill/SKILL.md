---
name: data-storage-manager-skill
description: 数据存储管理（分区、归档、清理）
---

# data-storage-manager-skill

## 触发条件

- 定期数据归档
- 存储空间管理
- 数据生命周期管理

## 输入

```yaml
input:
  action: "archive"
  data_type: "market_data"
  retention_days: 365
  archive_format: "parquet"
  compression: "snappy"
```

## 输出

```yaml
output:
  status: "SUCCESS"
  archived_rows: 1000000
  archived_size_gb: 2.5
  storage_freed_gb: 1.8
  archive_location: "s3://market-data-archive/2024/Q1/"
```

## 核心功能

### 数据生命周期

| 阶段 | 存储位置 | 保留期 |
|------|----------|--------|
| 热数据 | PostgreSQL | 30 天 |
| 温数据 | PostgreSQL 分区 | 1 年 |
| 冷数据 | MinIO (Parquet) | 永久 |

### 管理操作

- **分区管理**: 按时间分区
- **数据归档**: 迁移到冷存储
- **数据清理**: 删除过期数据
- **压缩优化**: 减少存储占用

## DoD

- [ ] 自动分区创建
- [ ] 自动数据归档
- [ ] 过期数据清理
- [ ] 存储使用监控
- [ ] 归档数据可恢复
