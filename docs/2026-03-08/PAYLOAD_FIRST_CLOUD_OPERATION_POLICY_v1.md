# PAYLOAD-FIRST CLOUD OPERATION POLICY v1

- 日期：`2026-03-08`
- 适用对象：本地 Codex / Gemini / 云端 Codex / 云端执行容器
- 状态：`ACTIVE`

## 1. 目标

在本地到云端直连不可用、链路被云平台或运营商阻断时，仍然维持：

- 治理资产可交付
- 云端执行可继续
- 交付结果可审计
- 最终验收仍由本地主控完成

本政策的核心不是“恢复直连”，而是：

**把离线/半离线载荷交付变成正式主路径。**

## 2. 一句话原则

**主仓是 SSOT；云端靠载荷接收治理资产；最终结论只以本地吸收与验收为准。**

## 3. 适用触发条件

出现以下任一情况，立即切换到 Payload-First 模式：

1. 本地无法稳定 `ssh/scp/rsync` 到云端
2. 云平台入口外链路被阻断
3. 安全组已放通但云端抓包无入站 SYN
4. 直连修复成本高于短期业务收益
5. 主控明确下令“停止追直连，改走载荷”

## 4. 角色分工

### 4.1 本地 Codex

- 维护主仓 authoritative 版本
- 编写 skill / script / protocol / contract
- 产出标准载荷
- 审核云端回传
- 执行最终吸收与业务验收

### 4.2 Gemini

- 充当桥接执行者
- 将载荷送至云端
- 在云端落盘或安装
- 输出安装/同步/阻断报告

### 4.3 云端 Codex

- 只消费已送达的载荷
- 不主动从本地主仓抓取
- 按已装载 skill 执行
- 回传任务包和执行证据

## 5. 允许交付的载荷类型

Payload-First 模式下允许交付：

1. `skill` 载荷
2. `script` 载荷
3. `protocol` / `policy` 文档载荷
4. `prompt` / `contract` / `task package spec` 载荷
5. `patch.diff` / `changes.diff` 载荷
6. 任务包证据载荷

## 6. 标准流程

### Phase A: 本地产出

本地 Codex 先在主仓完成：

- 内容定稿
- 审计口径统一
- 路径和变量定义收敛

### Phase B: 生成纯载荷包

使用统一模板生成：

- `payload_manifest.json`
- `INSTALL_ORDER.md`
- `VERIFY_STEPS.md`
- 载荷正文文件

### Phase C: Gemini 桥接上云

Gemini 负责：

- 将载荷包送上云端
- 在云端安装或写入指定路径
- 输出实际落点
- 输出 `INSTALLED / PARTIAL / BLOCKED`

### Phase D: 云端执行消费

云端 Codex 仅在以下前提下执行：

- 对应 skill 已真实可读
- 对应脚本已真实存在
- 对应协议路径已可引用

### Phase E: 本地吸收与验收

仍由本地执行：

- `pre_absorb_check`
- `absorb`
- review
- compliance
- final accept

## 7. 硬边界

1. 载荷送达不等于安装成功
2. 安装成功不等于业务接入成功
3. 云端预检通过不等于最终验收通过
4. 云端副本永远不是 authoritative source
5. 任何“已完成”都必须有主仓或云端真实落点支撑

## 8. 优先级判断

当直连不可用时，优先级如下：

1. `Payload-First` 连续可执行
2. 云端执行不中断
3. 本地主控可审计
4. 再考虑恢复直连

## 9. 禁止事项

禁止：

1. 因直连失败而停止全部云端执行
2. 把 Gemini 口头播报当安装完成
3. 把云端 Codex 理解原则当成已装载 skill
4. 在未吸收前把云端结果视为主仓事实

## 10. 成功判据

满足以下 4 条，即视为 Payload-First 模式可用：

1. 本地能持续产出标准载荷
2. Gemini 能把载荷送到云端并给出真实落点
3. 云端能基于载荷执行而非口头理解执行
4. 本地仍能完成 absorb + final accept

## 11. 当前结论

截至 `2026-03-08`：

- 直连链路不可依赖
- Payload-First 模式已成为当前正式主路径
- 以后恢复直连，只能算性能优化，不再是制度前提

---

*由本地 Codex 制定，作为当前云端治理默认操作政策。*
