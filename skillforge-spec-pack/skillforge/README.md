# SkillForge - 开工骨架

> 版本: 0.1.0

SkillForge 是 GM OS 生态中的 Skill 生产线产品。

## 目录结构

```
skillforge/
├── docs/
│   ├── ARCHITECTURE.md    # 架构说明
│   ├── ARTIFACTS.md       # 产物清单
│   └── UI_STATES.md       # UI 状态机
├── src/
│   ├── adapters/          # 预留: 外部适配器
│   │   ├── github_fetch/
│   │   ├── sandbox_runner/
│   │   └── registry_client/
│   └── orchestration/     # 预留: 编排器实现
└── README.md
```

## 对接 gm-os-core

SkillForge 依赖 gm-os-core 的合同和策略：

```python
# 引用 schemas
from gm_os_core.schemas import load_schema

gate_schema = load_schema("gate_decision")

# 引用 error_codes
from gm_os_core.error_codes import get_error_code

error = get_error_code("GATE_POLICY_DENY")
```

## 运行契约测试

```bash
# 在 gm-os-core 目录下
cd ../
pytest -q

# 应该全部通过
```

## 开发规范

1. **单向依赖**: 只能依赖 gm-os-core，不能反向
2. **合同优先**: 所有接口必须符合 gm-os-core 的 schema
3. **错误码统一**: 使用 error_codes.yml 定义的错误码

## 下一步

1. 实现 `adapters/github_fetch` - GitHub 仓库拉取
2. 实现 `adapters/sandbox_runner` - 沙箱执行器
3. 实现 `orchestration/pipeline` - 8 节点编排器
