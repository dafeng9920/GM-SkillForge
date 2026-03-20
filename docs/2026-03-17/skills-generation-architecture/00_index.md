# 00_index

## 1. 目的

本文件是 `skills-generation-architecture/` 目录的正式入口。

用途：

- 固定阅读顺序
- 固定文档分类
- 固定冻结/半冻结/后置属性
- 避免后续再次依赖“默认文件名顺序”吸收文档

本文件不改变任何冻结文档正文，只定义：

- 读取顺序
- 系统归类
- 当前主链对齐关系

---

## 2. 当前目录的系统定位

本目录中的文档，不是同一层材料，必须分成四类理解：

### A. 宪法与冻结规则

- `《系统宪法》V1.md`
- `《模块权限清单 v1》.md`
- `《治理冻结清单 + 生产主线待建清单》v1.md`
- `《GM-SkillForge 日终收口检查模板 v1》.md`

### B. 生产主线

- `《5层创建流程的数据结构清单 v1》.md`
- `5层流程.md`
- `架构纠偏文档 v1.md`

### C. 包装与交付关系

- `skill-creator和五层构建的区别.md`
- `skill交付形态.md`

### D. 商用扩展层（后置，不抢当前主线）

- `商用skill的构建流程.md`

---

## 3. 正式阅读顺序

### 第 1 组：冻结规则

1. `《系统宪法》V1.md`
2. `《模块权限清单 v1》.md`
3. `《治理冻结清单 + 生产主线待建清单》v1.md`
4. `《GM-SkillForge 日终收口检查模板 v1》.md`

### 第 2 组：生产主线

5. `《5层创建流程的数据结构清单 v1》.md`
6. `5层流程.md`
7. `架构纠偏文档 v1.md`

### 第 3 组：包装与交付关系

8. `skill-creator和五层构建的区别.md`
9. `skill交付形态.md`

### 第 4 组：商用扩展层

10. `商用skill的构建流程.md`

---

## 4. 当前主链路对齐说明

本目录所有当前有效整合，都必须围绕以下主链路服务：

`需求输入 → Intent Draft → Contract Draft → Candidate Skill → Build Validation → Delivery Manifest → skill-creator / 打包层`

补充说明：

- 主审计在打包前
- 打包后只允许轻量交付审计
- `skill-creator` 只负责后段封装与打包
- 最终裁决权只属于 `Kernel / Governor`

---

## 5. 使用纪律

### 允许

- 按本 index 吸收文档
- 建立映射、术语表、handoff 接口
- 产出整合文档

### 禁止

- 直接改冻结文档正文
- 改主链路顺序
- 改 `released / validated / gate_result`
- 改审计归属
- 扩大 `skill-creator` 角色边界

---

## 6. 相关正式整合文档

目录外整合产物见：

- [SYSTEM_INTEGRATION_REPORT_v1.md](/d:/GM-SkillForge/docs/2026-03-17/SYSTEM_INTEGRATION_REPORT_v1.md)
- [DOC_CLASSIFICATION_MATRIX_v1.md](/d:/GM-SkillForge/docs/2026-03-17/DOC_CLASSIFICATION_MATRIX_v1.md)
- [TERMINOLOGY_MAP_v1.md](/d:/GM-SkillForge/docs/2026-03-17/TERMINOLOGY_MAP_v1.md)
- [HANDOFF_INTERFACES_v1.md](/d:/GM-SkillForge/docs/2026-03-17/HANDOFF_INTERFACES_v1.md)

后续归位、冻结标记、schema 落位清单，也以这些正式整合文档为准。
