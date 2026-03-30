# GM LITE Plugin VSIX Packaging And Local Installation v1 Boundary Rules

## In Scope
- `vscode-extension` 的 `.vsix` 打包准备与最小打包验证
- 本地安装包态安装 / 启用 / 重装的最小验证
- 安装包态下活动栏图标、sidebar、命令入口验证
- packaging / installation / local-use 的已知缺口记录

## Out Of Scope
- 插件市场正式上架
- 发布账号、publisher 真实发布流程
- 完整 UI 产品化
- 大范围业务逻辑重构
- 将本轮扩成 marketplace release judgment

## 红线
- 不改 `.gm_bus` contract
- 不破坏当前已稳定的开发加载态
- 不把 `.vsix` 打包问题扩成运行时大重构
- 不把“本地安装包态”误判成“市场已发布态”
