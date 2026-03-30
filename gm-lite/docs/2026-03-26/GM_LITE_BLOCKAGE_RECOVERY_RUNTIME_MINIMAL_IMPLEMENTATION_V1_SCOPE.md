# GM LITE Blockage Recovery Runtime Minimal Implementation v1 Scope

## 模块目标
- 把 `FT2` 暴露出来的 blockage / recovery 缺口从 schema 层推进到 runtime 层
- 为当前插件壳与最小自动流转补齐最小可用的阻塞检测、挂起、恢复、升级链

## 本轮唯一目标
1. 实现最小 blockage detection runtime
2. 实现最小 recovery / resume runtime
3. 让 escalation / writeback / state progression 形成最小闭环
4. 明确本轮不做的完整 auto-orchestrator 范围

## 完成定义
- 现场验证中的 blockage 不再只有 schema 表达
- 至少一条 `blocked -> memo -> remediation -> resumed` 最小链路真实存在
- 有最小运行命令、样板证据、写回结果
- `BR1-BR4` 三件套齐全
