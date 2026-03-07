# T1-B EvidenceRef - 日志点位说明

## 概述

本文档说明 `scripts/validate_delivery_completeness.py` 中的结构化日志点位，
用于追踪执行过程和异常情况。

## Execution ID 追踪

**位置**: [validate_delivery_completeness.py:215-216](scripts/validate_delivery_completeness.py:215-216)

每个执行都有一个唯一的 `execution_id`，用于关联该执行的所有日志条目。

```python
if not execution_id:
    execution_id = str(uuid.uuid4())
```

**用途**:
- 追踪单次验证执行
- 关联多个日志条目
- 支持问题复现和调试

## 日志文件位置

**默认路径**: `logs/delivery_validator/delivery_validator_YYYYMMDD.jsonl`

**格式**: JSON Lines（每行一个 JSON 对象）

**位置**: [validate_delivery_completeness.py:221-223](scripts/validate_delivery_completeness.py:221-223)

```python
log_file = None
if log_dir:
    log_file = str(log_dir / f"delivery_validator_{datetime.now(UTC).strftime('%Y%m%d')}.jsonl")
```

## 关键日志点位

### 1. validation_start - 验证开始

**位置**: [validate_delivery_completeness.py:239-246](scripts/validate_delivery_completeness.py:239-246)

**日志级别**: INFO

**事件类型**: `validation_start`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:37.769859+00:00",
  "event_type": "validation_start",
  "execution_id": "test-t1-b-execution",
  "base_path": "D:\\GM-SkillForge",
  "allow_partial": false
}
```

**用途**:
- 记录验证开始时间
- 记录验证参数
- 支持 execution_id 追踪

---

### 2. item_check - 项检查

**位置**: [validate_delivery_completeness.py:143-154](scripts/validate_delivery_completeness.py:143-154)

**日志级别**: INFO

**事件类型**: `item_check`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:37.770440+00:00",
  "event_type": "item_check",
  "execution_id": "test-t1-b-execution",
  "category": "Blueprint",
  "pattern": "contracts/dsl/*.yml",
  "found": true,
  "required": true,
  "matching_count": 1
}
```

**用途**:
- 记录每个交付项的检查结果
- 支持定位缺失的项
- 提供 matching_count 用于验证

---

### 3. path_not_found - 路径不存在

**位置**: [validate_delivery_completeness.py:252-259](scripts/validate_delivery_completeness.py:252-259)

**日志级别**: ERROR

**事件类型**: `path_not_found`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:40.880463+00:00",
  "event_type": "path_not_found",
  "execution_id": "test-crash-fixed",
  "base_path": "C:\\Program Files\\Git\\nonexistent\\path",
  "error": "Base path does not exist: C:\\Program Files\\Git\\nonexistent\\path"
}
```

**用途**:
- 捕获路径不存在错误
- 提供复现信息
- 返回 FAIL 状态（fail-closed）

---

### 4. permission_error - 权限错误

**位置**: [validate_delivery_completeness.py:164-174](scripts/validate_delivery_completeness.py:164-174)

**日志级别**: ERROR

**事件类型**: `permission_error`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:41.123456+00:00",
  "event_type": "permission_error",
  "execution_id": "test-permission",
  "category": "Permit",
  "pattern": "permits/*/*.json",
  "error": "[Errno 13] Permission denied",
  "base_path": "/restricted/path"
}
```

**用途**:
- 捕获文件系统权限错误
- 提供具体失败的项和路径
- 支持权限问题诊断

---

### 5. unexpected_error - 未预期错误

**位置**: [validate_delivery_completeness.py:177-188](scripts/validate_delivery_completeness.py:177-188)

**日志级别**: ERROR

**事件类型**: `unexpected_error`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:41.234567+00:00",
  "event_type": "unexpected_error",
  "execution_id": "test-unexpected",
  "category": "n8n",
  "pattern": "workflows/**/*.json",
  "error": "OSError",
  "error_message": "Disk full",
  "traceback": "Traceback (most recent call last):\n  ..."
}
```

**用途**:
- 捕获单项检查中的非权限错误
- 提供完整 traceback
- 支持根因分析

---

### 6. item_check_failed - 项检查失败

**位置**: [validate_delivery_completeness.py:317-327](scripts/validate_delivery_completeness.py:317-327)

**日志级别**: ERROR

**事件类型**: `item_check_failed`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:41.345678+00:00",
  "event_type": "item_check_failed",
  "execution_id": "test-item-fail",
  "category": "Skill",
  "pattern": "skills/*/",
  "error_type": "PermissionError",
  "error_message": "[Errno 13] Permission denied: 'skills/'",
  "traceback": "Traceback (most recent call last):\n  ..."
}
```

**用途**:
- 记录单项检查失败详情
- 继续检查其他项（而非立即崩溃）
- 支持识别所有问题而非仅第一个

---

### 7. validator_crash - 验证器崩溃

**位置**: [validate_delivery_completeness.py:378-387](scripts/validate_delivery_completeness.py:378-387)

**日志级别**: ERROR

**事件类型**: `validator_crash`

**示例**:
```json
{
  "timestamp": "2026-03-06T06:46:41.456789+00:00",
  "event_type": "validator_crash",
  "execution_id": "test-validator-crash",
  "error_type": "MemoryError",
  "error_message": "out of memory",
  "traceback": "Traceback (most recent call last):\n  ...",
  "base_path": "/huge/path"
}
```

**用途**:
- 捕获所有未预期的全局错误
- 提供完整上下文用于复现
- 保持 fail-closed 语义

---

### 8. validation_complete - 验证完成

**位置**: [validate_delivery_completeness.py:359-368](scripts/validate_delivery_completeness.py:359-368)

**日志级别**: INFO (成功) / WARNING (失败)

**事件类型**: `validation_complete`

**示例（成功）**:
```json
{
  "timestamp": "2026-03-06T06:46:37.776194+00:00",
  "event_type": "validation_complete",
  "execution_id": "test-t1-b-execution",
  "status": "PASS",
  "error_code": null,
  "present_count": 6,
  "missing_count": 0
}
```

**示例（失败）**:
```json
{
  "timestamp": "2026-03-06T06:46:42.567890+00:00",
  "event_type": "validation_complete",
  "execution_id": "test-missing-items",
  "status": "FAIL",
  "error_code": "SF_DELIVERY_BLUEPRINT_MISSING",
  "present_count": 5,
  "missing_count": 1
}
```

**用途**:
- 记录验证最终结果
- 提供统计信息（present_count, missing_count）
- 支持 execution_id 关联

---

## 返回结构中的异常详情

**位置**: [validate_delivery_completeness.py:109-121](scripts/validate_delivery_completeness.py:109-121)

所有异常都在返回结果的 `exception_details` 字段中记录：

```python
exception_details: dict[str, Any] | None
```

**示例**:
```json
{
  "status": "FAIL",
  "error_code": "SF_DELIVERY_PATH_ACCESS_ERROR",
  "error_message": "Base path does not exist: /nonexistent/path",
  "exception_details": {
    "error_type": "PathNotFoundError",
    "error_message": "Base path does not exist: /nonexistent/path",
    "traceback": "Traceback (most recent call last):\n  ...",
    "base_path": "/nonexistent/path"
  },
  "execution_id": "test-crash-fixed",
  "log_file": "logs/delivery_validator/delivery_validator_20260306.jsonl"
}
```

**用途**:
- 提供机器可读的错误详情
- 支持自动化错误处理
- 提供足够上下文用于复现

---

## Fail-Closed 语义保证

**关键原则**: 所有异常都返回 `status="FAIL"`，绝不返回 success。

**验证点**:

1. **初始状态**: [validate_delivery_completeness.py:226](scripts/validate_delivery_completeness.py:226)
   ```python
   result: DeliveryCheckResult = {
       "status": "FAIL",  # Default to FAIL (fail-closed)
       ...
   }
   ```

2. **路径不存在**: [validate_delivery_completeness.py:267](scripts/validate_delivery_completeness.py:267)
   ```python
   return result  # FAIL status (fail-closed)
   ```

3. **全局异常**: [validate_delivery_completeness.py:399](scripts/validate_delivery_completeness.py:399)
   ```python
   # Return FAIL status (fail-closed)
   return result
   ```

4. **Exit code**: [validate_delivery_completeness.py:506](scripts/validate_delivery_completeness.py:506)
   ```python
   return 0 if result["status"] == "PASS" else 1
   ```

---

## 日志查询示例

### 查询特定执行的所有日志

```bash
grep "test-t1-b-execution" logs/delivery_validator/delivery_validator_20260306.jsonl | jq
```

### 查询所有错误

```bash
grep '"event_type": "error' logs/delivery_validator/delivery_validator_20260306.jsonl | jq
```

### 查询所有崩溃

```bash
grep '"event_type": "validator_crash' logs/delivery_validator/delivery_validator_20260306.jsonl | jq
```

### 统计失败次数

```bash
grep '"status": "FAIL' logs/delivery_validator/delivery_validator_20260306.jsonl | wc -l
```

---

## 验证清单

- [x] validator crash 有结构化日志
  - 事件类型: `validator_crash`
  - 包含: error_type, error_message, traceback, base_path
  - 位置: [validate_delivery_completeness.py:378-387](scripts/validate_delivery_completeness.py:378-387)

- [x] 返回语义仍是 fail-closed
  - 所有异常返回 `status="FAIL"`
  - Exit code: 0=PASS, 1=FAIL
  - 位置: [validate_delivery_completeness.py:226,267,399,506](scripts/validate_delivery_completeness.py:226)

- [x] 有最小验证说明或复现说明
  - `exception_details` 包含完整上下文
  - `execution_id` 支持日志关联
  - `log_file` 指向日志文件位置

---

## 相关文件

- **主文件**: [scripts/validate_delivery_completeness.py](scripts/validate_delivery_completeness.py)
- **执行报告**: [docs/2026-03-07/verification/T1-B_execution_report.yaml](docs/2026-03-07/verification/T1-B_execution_report.yaml)
- **日志目录**: [logs/delivery_validator/](logs/delivery_validator/)
