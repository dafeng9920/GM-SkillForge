# Docker Volume 受控物理桥接方案 v1

## 核心设计：ReadOnly 主仓 + Writeable Dropzone

为了打破“云端孤岛”并维持“治理安全性”，我们不再通过 SSH 手动拉取文件，而是通过宿主机文件系统的 Volume 映射实现**物理级联通**。

### 1. 物理拓扑 (Topology)

| 物理位置 | 容器挂载路径 | 权限 | 治理角色 |
| :--- | :--- | :--- | :--- |
| 云主机 `./skillforge` | `/home/node/app` | **RO (ReadOnly)** | **受保护的主仓核心**。龙虾可读、可测试，但不可直接修改。 |
| 云主机 `./dropzone` | `/home/node/dropzone` | **RW (ReadWrite)** | **受控交付区**。龙虾产生的所有 execution_receipt, report, handoff 必须落在此处。 |

### 2. 治理拦截点 (Gatekeeping)

1.  **物理隔离主线**：即便龙虾产生幻觉想要修改 `intent_map.yml`，容器的 RO 挂载也会强制报 `Read-only file system`。
2.  **强制审计流程**：产物一旦落盘到宿主机的 `dropzone/`，宿主机脚本会自动监控，但不会自动合并。只有经过 `absorb.sh`（需主控触发）才会进入主仓。

### 3. 给小龙虾的履行指令更新

任何在新方案下执行的任务，其 `task_contract` 必须包含：
- **Execution Path**: `/home/node/app` (Readonly)
- **Output Root**: `/home/node/dropzone/<task_id>/` (Authorize Write)

---
*版本: v1.0 (2026-03-08)*
