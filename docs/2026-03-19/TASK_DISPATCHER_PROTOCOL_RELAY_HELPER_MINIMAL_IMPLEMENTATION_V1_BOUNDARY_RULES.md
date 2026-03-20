# Task Dispatcher Protocol Relay Helper Minimal Implementation v1 Boundary Rules

## 功能边界
- helper 只做“检测 + 生成”
- helper 不做“发送 + 调度 + 裁决”

## 输入边界
- 只读取 task_id 对应的标准 writeback 文件
- 只读取显式传入的 verification 目录
- 不扫描模块外任务

## 输出边界
- 只生成：
  - review envelope
  - compliance envelope
  - final_gate_input
  - escalation_pack
  - 状态摘要
- 不直接修改任务卡
- 不直接更新主控结论

## 裁决边界
- helper 只能产出 `GATE_READY` 候选输入
- 是否最终通过，仍由 Codex 主控官决定

## 技术边界
- 单文件脚本
- 本地文件系统
- 无网络
- 无守护进程

