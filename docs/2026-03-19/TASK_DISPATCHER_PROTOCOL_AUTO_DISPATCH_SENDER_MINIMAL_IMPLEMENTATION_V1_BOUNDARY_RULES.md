# Task Dispatcher Protocol Auto Dispatch Sender Minimal Implementation v1 Boundary Rules

## 功能边界
- sender 只负责“读取 + 封包 + 生成可转发消息”
- sender 不负责“真实发送 + 确认送达 + 重试”

## 输入边界
- 只读取 relay-helper 已生成的：
  - `*_review_envelope.json`
  - `*_compliance_envelope.json`
  - `*_final_gate_input.json`
  - `*_escalation_pack.json`

## 输出边界
- 只生成：
  - `*_dispatch_packet.json`
  - `*_dispatch_message.txt`
  - `dispatch_summary.json`
- 不直接改动 verification 目录

## 裁决边界
- sender 不做协议解释
- sender 不决定是否通过
- sender 不修改 task board 状态

## 技术边界
- 单文件脚本
- 本地文件系统
- 无网络
- 无守护进程

