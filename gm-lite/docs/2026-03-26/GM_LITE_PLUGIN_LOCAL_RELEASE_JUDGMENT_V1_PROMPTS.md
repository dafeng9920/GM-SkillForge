# GM LITE Plugin Local Release Judgment v1 Prompts

## 主控提示
- 本轮不是打包轮，不是实现轮，而是 judgment 轮
- 所有结论必须区分：
  - 开发加载态
  - `.vsix` 本地安装包态
  - 插件市场公开发布态

## 判断优先级
1. 先看本地安装包态是否稳定
2. 再看入口、sidebar、命令是否足够支持长期自用
3. 再看 gap 是否为 blocker
4. 最后才给 local release decision
