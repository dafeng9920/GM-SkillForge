# GM LITE Plugin VSIX Packaging And Local Installation v1 Change Control Rules

## 允许改动
- `vscode-extension/package.json` 中与 packaging 直接相关的最小元数据
- 本地打包、安装、重装所需最小脚本或说明
- `.vscode` / README 中与本地安装态验证直接相关的最小说明

## 禁止改动
- 无关业务逻辑重写
- 扩成 marketplace 发布工程
- 为了过安装包态而破坏开发加载态
- 把本轮变成 UI 功能扩展轮

## 变更原则
- 先保证可打包 / 可安装 / 可验证
- 再考虑发布美化与完整分发
