# GM LITE Plugin Local Usability And Stability Hardening v1 Change Control Rules

## 允许改动
- 与安装态稳定性直接相关的最小实现
- 命令反馈和状态刷新相关最小修复
- 与重复使用 / 恢复链直接相关的最小修复

## 禁止改动
- 越界到全新功能开发
- 越界到 marketplace 工程
- 大规模 UI 重构
- 破坏现有 `.vsix` 安装态可用性

## 变更原则
- 先稳住本地长期使用
- 再考虑更高一级发布判断
