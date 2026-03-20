# SKILL: STEALTH_SCRAPER_CORE

## 🏷️ 技能定义
一个高度隐匿、硬件加速的网页抓取引擎。专为绕过 WebGL 指纹检测、WebDriver 标志检测以及针对 KOL（如 X/Twitter）的大规模内容采集而设计。

## 🚀 核心架构
- **隔离层**: 基于 NVIDIA CUDA 的 Docker 容器。
- **物理加速**: 直通宿主机 GPU (RTX 5070 Ti) 进行真实渲染。
- **自愈显示**: 自动管理 Xvfb 虚拟显示服务。
- **人类抖动**: 内置鼠标随机轨迹与阅读时长模拟。
- **安全熔断**: 自动感应 CAPTCHA 并撤退以保护 IP。

## 🛠️ API 契约

### 1. 采集 X (Twitter) 内容
`GET /v1/scrape/x?target_user={user}&depth={5}&proxy={opt}`

**输入参数:**
| 参数 | 类型 | 描述 |
| :--- | :--- | :--- |
| `target_user` | String | X 的用户名 (如 `elonmusk`) |
| `depth` | Int | 深度（滚动次数，默认 5） |
| `proxy` | String | 可选代理地址 |

**输出示例:**
```json
{
  "status": "success",
  "user": "elonmusk",
  "total_captured": 12,
  "data": [
    {
      "text": "...",
      "engagement": {"likes": "4.2M", "retweets": "755K", "replies": "168K"},
      "scraped_at": "2026-03-18T14:40:00Z"
    }
  ]
}
```

## ⚠️ 治理与合规 (Guardrails)
1. **频率限制**: 单一 IP 建议抓取间隔 > 5 分钟。
2. **账号保护**: 严禁在容器内登录个人主账号，默认使用 Guest 模式。
3. **熔断逻辑**: 当返回 `BOT_DETECTION_TRIGGERED` 时，必须人工介入或更换代理。
