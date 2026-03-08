# Ads Intel - Google Ads 竞争情报采集

## 触发词
- `/ads-intel`
- `/ads-update`
- `/竞品情报`

## 功能
定期采集 Google Ads 生态的关键数据：
1. 高价词 CPC 趋势
2. 用户抱怨/痛点语料
3. 行业动态/趋势

## 输出格式

```markdown
## 📊 Ads Intel 报告 - {日期}

### 高价词变化
| 关键词 | 上次 CPC | 本次 CPC | 变化 |
|--------|---------|---------|------|
| ... | ... | ... | ↑↓→ |

### 🔴 热门抱怨 (Top 5)
1. [痛点] - [讨论热度]
2. ...

### 📰 行业动态
- [标题] - [影响评估]

### 💡 行动建议
- [基于数据的具体建议]
```

## 数据源

### 高价词
- WordStream: https://www.wordstream.com/blog/ws/2017/06/27/most-expensive-keywords
- Semrush: https://www.semrush.com/blog/google-ads-cost-per-click/
- Ahrefs: https://ahrefs.com/blog/google-ads-cost/

### 抱怨语料
- Google Ads Community: https://support.google.com/google-ads/community
- Search Engine Journal: https://www.searchenginejournal.com/category/ppc/
- PPC Hero: https://www.ppchero.com/

### 行业动态
- Search Engine Land: https://searchengineland.com/
- Google Ads Blog: https://blog.google/products/ads/

## 执行方式

### 手动触发
用户说：`/ads-intel`

### 定期更新（推荐配置）
在 HEARTBEAT.md 中添加：
```
## 每周任务
- [ ] 周一：执行 /ads-intel 更新
```

或在 cron 中配置：
```bash
# 每周一上午 9 点执行
0 9 * * 1 echo "/ads-intel" > /tmp/openclaw-command
```

## 存储
- 历史报告：`memory/ads-intel/YYYY-MM-DD.md`
- 汇总数据：`memory/ads-intel/trends.json`

## 注意事项
1. Reddit 需要 API 或浏览器才能访问
2. 部分网站有反爬，需要轮换 User-Agent
3. CPC 数据更新频率较低（季度/年度）
4. 抱怨语料价值更高，建议重点关注
