# CLOUD SKILL SYNC INSTALL PROTOCOL v1（Gemini 执行版）

- 日期：`2026-03-08`
- 适用对象：Gemini（桥接执行者） / 云端执行容器 / OpenClaw 工作区
- 本地 SSOT：`SSOT_ROOT`

## 目标

把本地主仓中新增的云端执行协议 skill，通过 Gemini 桥接同步到云端可读、可引用、可验证的位置。

本协议解决的问题不是“让云端自动理解原则”，而是：

- 让 Gemini 作为桥梁，把本地同版本的 skill 文件送到云端
- 让云端后续执行时可以引用真实 skill 路径
- 让主控能够验证“云端已装载哪些 skill”

## 角色分工

- 本地 Codex：
  - 负责写 skill
  - 负责维护主仓 authoritative 版本
- Gemini：
  - 负责桥接同步
  - 负责把本地 skill 副本送入云端可读路径
  - 负责输出同步结果和阻断原因
- 云端 Codex：
  - 只负责消费已同步的 skill
  - 不负责从本地主仓主动抓取 skill

## 路径变量

- `SSOT_ROOT`: 本地主仓 authoritative 根
- `APP_ROOT`: 云端工作源码根
- `DROPZONE_ROOT`: 云端可写交付出口
- `DOCS_ROOT`: 宿主机或主仓文档吸收根

## 本次必须同步的 skill

以下 3 个 skill 为本轮必同步对象：

1. `skills/gm-multi-agent-orchestrator-skill/`
2. `skills/lobster-task-package-skill/`
3. `skills/lobster-absorb-gate-skill/`

建议同时保留既有依赖 skill 的只读副本或引用：

4. `skills/lobster-cloud-execution-governor-skill/`

## 同步原则

1. 本地主仓是唯一事实来源（SSOT）
2. Gemini 只做副本同步，不在云端私自改写 skill 内容
3. 云端同步后的 skill 只用于执行与引用，不用于替代主仓 authoritative 版本
4. 若云端副本与主仓冲突，以主仓为准

## 云端目标路径

建议云端统一落到：

- `APP_ROOT/skills/`

如果容器内该路径为只读，则允许同步到：

- `DROPZONE_ROOT/skills_sync/<skill_name>/`

但必须记录最终实际落点。

## 最低交付结果

Gemini 完成同步后，必须能提供：

1. 同步结果清单
2. 每个 skill 的实际落点
3. 每个 `SKILL.md` 的存在性验证
4. 同步时间戳
5. 如存在只读阻断，明确标记 `BLOCKED`

## 验证标准

对每个 skill，至少验证：

- 目录存在
- `SKILL.md` 存在
- 内容非空
- 云端路径可被后续任务引用

推荐输出格式：

```text
skill_name: gm-multi-agent-orchestrator-skill
status: INSTALLED
path: APP_ROOT/skills/gm-multi-agent-orchestrator-skill/SKILL.md
size_bytes: 1234
```

## 禁止事项

Gemini 与云端 Codex 均不得：

1. 改写主仓 skill 内容并反向宣称为 authoritative
2. 在云端自行创造同名替代 skill
3. 把“同步完成”写成“已完成业务接入”
4. 省略实际落点与验证结果

## 失败处理

如果发生以下情况，直接标记 `BLOCKED`：

- Gemini 无法访问本地主仓同步源
- 容器路径只读且无替代落点
- skill 目录可创建但 `SKILL.md` 不可写
- 只完成部分 skill 同步

不得在上述情况下伪装 `INSTALLED`。

## 建议同步步骤

1. 由 Gemini 确认可访问的本地同步源
2. 确认目标路径是 `APP_ROOT/skills/` 还是 `DROPZONE_ROOT/skills_sync/`
3. 创建缺失目录
4. 复制 skill 目录
5. 逐个检查 `SKILL.md`
6. 输出同步报告

## 建议同步报告文件

建议由 Gemini 在云端侧生成：

- `DOCS_ROOT/2026-03-08/cloud_skill_sync_report.md`

至少包含：

- 同步对象
- 实际落点
- 成功/失败状态
- 阻断原因

## 给 Gemini 的直接执行指令

```text
你现在执行 Cloud Skill Sync Install v1（Gemini 桥接版）。

目标：
把以下本地主仓已定义的 skill，同步到云端可读路径，并输出真实安装结果：

1. gm-multi-agent-orchestrator-skill
2. lobster-task-package-skill
3. lobster-absorb-gate-skill
4. lobster-cloud-execution-governor-skill（依赖项，可一并同步）

约束：
1. 主仓 authoritative 仍在本地，不得擅自改写 skill 内容
2. 你负责桥接同步，云端 Codex 不负责主动抓取本地 skill
3. 云端只保留副本与存在性验证
4. 若 `APP_ROOT/skills/` 不可写，可改用 `DROPZONE_ROOT/skills_sync/`
5. 不得伪装 INSTALLED

你必须输出：
1. 每个 skill 的实际落点
2. 每个 SKILL.md 是否存在
3. INSTALLED / BLOCKED / PARTIAL 状态
4. 如失败，给出明确阻断原因
5. 生成 cloud_skill_sync_report.md

通过标准：
- 至少 3 个新 skill 已在云端有真实副本
- 每个 skill 都能给出实际路径
- 每个 skill 的 SKILL.md 可读取
- 不得只给口头“已理解”
```
