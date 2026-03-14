# 🦞 OpenClaw 商业级远程部署方案 v1.0

**日期**: 2026-03-04  
**目标**: 提供一套标准化的、安全的、可用于商业交付的 OpenClaw 安装包。

## 📦 包含组件

1.  **[Install_OpenClaw.ps1](file:///d:/GM-SkillForge/docs/2026-03-04/%E8%BF%9C%E7%A8%8B%E5%AE%89%E8%A3%85%E5%B0%8F%E9%BE%99%E8%99%BE/Install_OpenClaw.ps1)**  
    *   Windows 一键安装脚本。支持自动环境检查、目录创建、配置生成。
2.  **[openclaw.json.template](file:///d:/GM-SkillForge/docs/2026-03-04/%E8%BF%9C%E7%A8%8B%E5%AE%89%E8%A3%85%E5%B0%8F%E9%BE%99%E8%99%BE/openclaw.json.template)**  
    *   商业加固版配置模板。预设了 Host Header 屏蔽、Loopback 绑定、安全沙箱等策略。
3.  **[User_Manual_Boss.md](file:///d:/GM-SkillForge/docs/2026-03-04/%E8%BF%9C%E7%A8%8B%E5%AE%89%E8%A3%85%E5%B0%8F%E9%BE%99%E8%99%BE/User_Manual_Boss.md)**  
    *   给终端客户（老板）看的使用说明书。强调价值、安全与简单易用。

## 🛠️ 交付流程建议

1.  **远程确认**：确认对方安装了 Docker Desktop。
2.  **执行脚本**：将此文件夹打包发给对方，让他以管理员身份运行 `Install_OpenClaw.ps1`。
3.  **配置 Token**：指导对方填入 Discord Bot Token。
4.  **启动服务**：在终端运行 `docker compose up -d`。
5.  **交付手册**：将 `User_Manual_Boss.md` 发给对方。

---
*加固经验点：已固化 `dangerouslyAllowHostHeaderOriginFallback: false`。*
