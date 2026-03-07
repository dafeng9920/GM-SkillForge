# APH-006: 根目录脚本清理

## 执行摘要

已完成根目录脚本的分类和移动。

## 清理结果

### 移动到 tools/
- `chat_to_md.py` → `tools/chat_to_md.py`
- `extract_template.py` → `tools/extract_template.py`
- `extract_template_v2.py` → `tools/extract_template_v2.py`
- `heal_template.py` → `tools/heal_template.py`

### 移动到 scripts/dev/
- `simple_api.py` → `scripts/dev/simple_api.py`
- `run_api.py` → `scripts/dev/run_api.py`
- `start_full_api.py` → `scripts/dev/start_full_api.py`
- `start_backend.py` → `scripts/dev/start_backend.py`

### 建议删除（已过期/一次性脚本）
- `bulk_patch_imports.py` - 一次性脚本，已完成
- `create_dummy_packs.py` - 一次性脚本
- `create_valid_dummy_packs.py` - 一次性脚本
- `insert_debug.py` - 调试脚本
- `patch_imports.py` - 一次性脚本
- `patch_script.py` - 一次性脚本
- `patch_test.py` - 测试脚本
- `rewrite_registry.py` - 一次性脚本
- `test_regex.py` - 测试脚本
- `test_regex2.py` - 测试脚本
- `test_regex3.py` - 测试脚本
- `test_wave3_verification.py` - 测试脚本

### 保留在根目录
- `requirements.txt` - 项目依赖（必须保留）
- `simple_api.py` - 注意：此文件被移动到 scripts/dev/，如需保留副本请确认

## 下一步

建议执行以下操作：
1. 删除已过期的脚本文件
2. 更新文档中的引用
3. 添加 tools/ 和 scripts/dev/ 的 README.md 说明
