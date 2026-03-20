# DOCUMENT_RELOCATION_PLAN_v1

## 1. 目的

本文件用于给出当前 2026-03-17 架构文档的正式归位方案。

目标不是立即移动文件，而是先定义：

- 哪些文档属于冻结区
- 哪些文档属于生产主线
- 哪些文档属于交付/包装层
- 哪些文档属于商用扩展层
- 哪些整合文档应作为正式入口和中间索引

本文件不触碰冻结正文，不调整主链路顺序，不改变写口。

---

## 2. 推荐目录骨架

```text
docs/
  frozen/
    constitution/
    governance/
    strategy/
  checks/
  production/
    flow/
    objects/
    architecture/
  delivery/
  commercial-extension/
  integration/
```

---

## 3. 当前文档归位建议

### A. 冻结区

#### `docs/frozen/constitution/`

- `《系统宪法》V1.md`

#### `docs/frozen/governance/`

- `《模块权限清单 v1》.md`

#### `docs/frozen/strategy/`

- `《治理冻结清单 + 生产主线待建清单》v1.md`

### B. 检查区

#### `docs/checks/`

- `《GM-SkillForge 日终收口检查模板 v1》.md`

### C. 生产主线区

#### `docs/production/objects/`

- `《5层创建流程的数据结构清单 v1》.md`

#### `docs/production/flow/`

- `5层流程.md`

#### `docs/production/architecture/`

- `架构纠偏文档 v1.md`

### D. 交付/包装区

#### `docs/delivery/`

- `skill-creator和五层构建的区别.md`
- `skill交付形态.md`

### E. 商用扩展区

#### `docs/commercial-extension/`

- `商用skill的构建流程.md`

### F. 整合层

#### `docs/integration/`

建议最终归位：

- `SYSTEM_INTEGRATION_REPORT_v1.md`
- `DOC_CLASSIFICATION_MATRIX_v1.md`
- `TERMINOLOGY_MAP_v1.md`
- `HANDOFF_INTERFACES_v1.md`
- `DOCUMENT_RELOCATION_PLAN_v1.md`
- `FROZEN_AND_READONLY_MARKERS_v1.md`
- `SCHEMA_PLACEMENT_CHECKLIST_v1.md`

---

## 4. 当前阶段的执行口径

### 现在做

- 先产出正式归位方案
- 先锁定文档分类
- 先给冻结/半冻结文档补只读说明

### 现在不做

- 不直接批量移动文件
- 不重命名冻结文档
- 不为了目录好看而整体重构
- 不借归位之名修改正文

---

## 5. 归位优先级

### P0

- 确立正式入口：`00_index.md`
- 确立正式整合文档集
- 确立冻结/半冻结标记

### P1

- 把生产对象相关文档与 schema 落位清单对齐
- 把包装/交付文档从生产主线中显式分层

### P2

- 未来如需迁移目录，再按本方案实施实体移动

---

## 6. 风险提醒

- 若先移动再定义归位规则，容易造成二次返工
- 若不把整合文档单列，后续仍会回到“散文档 + 聊天结论”状态
- 若把商用扩展提前并入当前主链，主线会再次发散
