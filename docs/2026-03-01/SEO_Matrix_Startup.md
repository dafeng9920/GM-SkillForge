# SEO Matrix MVP — 启动与运行手册 (2026-03-01)

## 1. 核心定位
*   **项目名称**: SEO Matrix MVP (发布级小网站)
*   **所属仓库**: `dafeng9920` (地址: `https://github.com/dafeng9920/GM-SkillForge.git`)
*   **本地路径**: `d:\GM-SkillForge\export-seo\`
*   **愿景**: "We fix what GitHub breaks." — 为品牌提供 AI 搜索可见性审计。

---

## 2. 启动命令 (本地预览)

由于该项目是纯静态 (Static) 构建，直接进入目录并使用静态服务器启动即可。

### 方案 A：使用 Node.js (推荐)
最简单且自动处理缓存的方式：
```powershell
cd d:\GM-SkillForge\export-seo
npx serve .
```
*   **默认端口**: 3000
*   **访问地址**: [http://127.0.0.1:3000](http://127.0.0.1:3000)

### 方案 B：使用 Python (强制 IPv4 绑定)
如果遇到 `ERR_ADDRESS_INVALID` 错误，请强制绑定到 127.0.0.1：
```powershell
cd d:\GM-SkillForge\export-seo
python -m http.server 8080 --bind 127.0.0.1
```
*   **默认端口**: 8080
*   **访问地址**: [http://127.0.0.1:8080](http://127.0.0.1:8080)

---

## 3. 部署信息 (Cloudflare Pages)
该项目已对接 Cloudflare Pages 环境：
*   **构建目录**: `export-seo/`
*   **后端接口**: `functions/api/audit.js` (处理 Lead Capture 逻辑)
*   **环境变量**: 需要配置 `DISCORD_WEBHOOK_URL` 以后台接收审计线索。

---

## 4. 绚丽交付页 (Delivery Pages) — 核心展示
围绕 SEO Matrix，以下是与之匹配的高保真交付报告页面，采用了深色模式、玻璃拟态和动态统计图表：

### 报告模板 (Master Template)
*   本地路径: `d:\GM-SkillForge\Audit_Report_Final.html`
*   **视觉特征**: 三色变色条 (Accent Rail)、径向渐变背景、AEV 损耗计数器、诊断矩阵表。

### 行业交付实例 (Industry Examples)
*   目录路径: `d:\GM-SkillForge\pseo\`
*   包含文件:
    *   `Audit_Report_indiajobsdekho_com.html`
    *   `Audit_Report_luxury-retailer-x_com.html`
    *   `Audit_Report_security-vendor-y_com.html`

### 详细审计页 (Detailed View)
*   本地路径: `d:\GM-SkillForge\skillforge-web\audit-detail.html`
*   **定位**: L5 Industrial 级别审计详情页，包含专业级的 Schema 结构化数据映射。

---

## 5. 关键文件清单
*   `index.html`: 战略主入口 (AI Search Visibility Audit)
*   `index_zh.html`: 中文版入口
*   `*-ai-seo-checker.html`: 针对不同框架 (Next.js/Shopify/WP) 的落地页
*   `package.json`: 定义了 `aio-checker-matrix` 指纹

---
*Created by Antigravity @ SkillForge Governance System.*
