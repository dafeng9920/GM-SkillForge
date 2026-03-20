# GM LITE Controller Console Minimal Implementation v1 Boundary Rules

## 模块边界
- 本模块只做 controller console 最小实现，不做完整插件界面
- 本模块只落只读控制台骨架与视图对象
- 本模块不实现自动状态同步

## 实现边界
- 允许：目录、文件、schema、example、view model、README
- 受控：最小 projector / loader 占位
- 禁止：UI 渲染、watcher、adapter、自动 dispatch

## 数据边界
- 控制台读取 `.gm_bus` 与 verification
- 控制台不作为权威状态源
- 控制台不改写执行流转结果

## change control
- 允许：命名收紧、视图对象补充、样板数据完善
- 受控：最小 loader / projector 占位补充
- 禁止：提前做 UI / adapter / runtime
