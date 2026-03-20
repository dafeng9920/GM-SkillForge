# 最小修正阶段报告 v1

## 1. 本轮问题定义

- 当前唯一阻断项：
  - builder / pipeline 的导入路径与实际文件命名不一致
  - 导致 sample 驱动的最小装配在导入阶段失败：
    - `ModuleNotFoundError: No module named 'contracts.production.candidate.candidate_skill'`

- 为什么它属于结构级问题，而不是业务/治理问题：
  - 问题发生在 Python 模块导入层
  - 与对象语义、治理判定、发布判定、workflow 执行无关
  - 属于“模块落位 / 文件命名 / import path”一致性错误

## 2. 根因定位

- 不一致的文件类型：
  - `*.model.py`
  - `*.builder.py`
  - `*.types.py`

- 具体错误点：
  - 代码使用例如：
    - `from contracts.production.candidate.candidate_skill.model import CandidateSkill`
  - 但实际文件是：
    - `contracts/production/candidate/candidate_skill.model.py`
  - Python 无法把 `candidate_skill.model.py` 解析成
    - `candidate_skill/model.py`
    - 或 `candidate_skill.model` 模块结构

- 受影响文件：
  - 5 个模型文件
  - 5 个 builder 文件
  - 2 个 handoff 类型占位文件
  - `production_chain_minimal.py`

## 3. 采用的最小修正策略

- 选择的策略：
  - **策略 B：极小范围文件命名调整 + import 同步**

- 为什么这是影响面最小的修复方式：
  - 仅修正 Python 可导入性
  - 不改 schema
  - 不改 sample
  - 不改对象字段
  - 不改 builder 行为逻辑
  - 不改 pipeline 顺序
  - 不做目录整体重构

- 改动的文件：
  - 重命名：
    - `intent_draft.model.py` -> `intent_draft_model.py`
    - `contract_bundle.model.py` -> `contract_bundle_model.py`
    - `candidate_skill.model.py` -> `candidate_skill_model.py`
    - `build_validation_report.model.py` -> `build_validation_report_model.py`
    - `delivery_manifest.model.py` -> `delivery_manifest_model.py`
    - `intent_draft.builder.py` -> `intent_draft_builder.py`
    - `contract_bundle.builder.py` -> `contract_bundle_builder.py`
    - `candidate_skill.builder.py` -> `candidate_skill_builder.py`
    - `build_validation_report.builder.py` -> `build_validation_report_builder.py`
    - `delivery_manifest.builder.py` -> `delivery_manifest_builder.py`
    - `candidate_handoff.types.py` -> `candidate_handoff_types.py`
    - `validation_handoff.types.py` -> `validation_handoff_types.py`
  - 同步 import：
    - 所有当前主链内部引用均改为下划线命名模块路径

## 4. 修正结果

- 导入阻断是否消失：
  - **是**

- 最小装配是否通过导入阶段：
  - **是**

- 最小主链是否能完成对象级装配启动：
  - **是**

- 复跑结果：
  - 旧导入模式搜索结果为空：
    - `rg -n \"\\.model import|\\.builder import|\\.types import\" contracts/production -g \"*.py\"`
  - sample 驱动装配成功，返回：
    - `intent = generate_skill_from_requirement`
    - `contract = contract-generate-skill-v1`
    - `candidate = cand-generate-skill-v1`
    - `validation_report = bvr-generate-skill-v1`
    - `delivery = delivery-generate-skill-v1`

- 是否仍存在残余问题：
  - 未发现新的路径断裂
  - 当前无新的结构阻断项

## 5. 本轮未触碰的边界

- 冻结文档正文未改
- 主链路未改
- 正式写口未改
- 审计归属未改
- `skill-creator` 角色边界未改
- 未进入治理逻辑
- 未进入发布逻辑
- 未进入 workflow / orchestrator
- 未进入 handoff 执行实现
- 未扩大修正范围

## 6. 当前阶段判断

- 是否已修复阻断项：
  - **是**
- 是否具备重新进入 `Production Chain v0 Frozen` 判断阶段的条件：
  - **是**

## 7. 下一步建议

- 进入 **Production Chain v0 Frozen 判断阶段**
