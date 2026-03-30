# GM LITE Plugin Local Release Judgment v1 Scope

## 模块目标
- 对 `GM-LITE` 插件当前本地安装包态进行 release judgment
- 判断其是否已经达到“仅自己本地长期使用”的 release 水位
- 明确进入更高一级分发前仍需补齐的 gap

## 本轮唯一目标
1. 判断当前 `.vsix` 本地安装包态是否达到 local-use release 条件
2. 判断当前入口、sidebar、命令、最小 flow 是否足以支撑持续本地使用
3. 判断当前 gap 是否只是已知可接受缺口，还是 release blocker
4. 输出 local release decision 与下一刀方向

## 完成定义
- 至少一轮 local release judgment 完成
- 有明确 `PASS / PASS with documented gaps / REQUIRES_CHANGES / FAIL`
- 有 blocker / non-blocker 区分
- `RJ1-RJ4` 三件套齐全
