# GM LITE Plugin Local Release Judgment v1 Boundary Rules

## In Scope
- `.vsix` 本地安装包态的 local-use release 判断
- 当前入口、sidebar、命令、安装稳定性、最小可观测性判断
- blocker / non-blocker 分层
- 仅自己本地使用的 release direction

## Out Of Scope
- 插件市场正式发布判断
- 跨机器 / 跨团队分发
- 完整产品化 UI 改造
- 大规模功能扩展
- 将本轮扩成 marketplace readiness review

## 红线
- 不把“本地可长期使用”误判成“适合公开上架”
- 不为了拿到 PASS 而忽略已知 blocker
- 不在 judgment 轮偷偷实现新功能
