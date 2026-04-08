---
name: daily-hub-summary
description: 每日信息汇总技能 - 抓取 Polymarket Breaking、V2EX 热门、Hacker News 等多个数据源，汇总分析并发送报告。支持定时任务和自定义数据源。
version: 1.0.0
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["python3"],"env":[]}}}
---

# Daily Hub Summary - 每日信息汇总

每日信息汇总技能，自动抓取多个数据源并生成分析报告。

## 功能特性

- 🔥 **Polymarket Breaking** - 前10条突发新闻及预测走势
- 💬 **V2EX 热门** - 最热门的讨论话题
- 📰 **Hacker News** - 科技圈热门新闻
- 📊 **趋势分析** - 预测概率变化、热门话题趋势
- 📬 **定时推送** - 支持 cron 定时任务
- 💬 **多渠道发送** - Telegram、邮件等

## 快速开始

### 安装依赖
```bash
pip3 install requests playwright lxml beautifulsoup4
playwright install chromium
```

### 一次性运行
```bash
python3 /root/.openclaw/workspace/skills/daily-hub-summary/scripts/summary.py
```

### 定时任务（每天9点、18点运行）
```bash
# 添加到 crontab
0 9,18 * * * /usr/bin/python3 /root/.openclaw/workspace/skills/daily-hub-summary/scripts/summary.py
```

## 数据源说明

### 1. Polymarket Breaking
**URL**: https://polymarket.com/breaking

**抓取内容**：
- 前10条 Breaking 事件
- 事件标题
- 预测概率
- 成交量
- 截止时间

**API方式**（备用）：
```bash
curl "https://clob.polymarket.com/markets?active=true&limit=10&order=volume&order_direction=desc"
```

### 2. V2EX 热门
**URL**: https://www.v2ex.com/api/topics/hot.json

**抓取内容**：
- 前10条热门话题
- 标题
- 作者
- 回复数
- 节点分类

### 3. Hacker News
**URL**: https://hacker-news.firebaseio.com/v0/topstories.json

**抓取内容**：
- 前10条热门新闻
- 标题
- URL
- 点数
- 评论数

## 脚本位置

- 主脚本：`scripts/summary.py`
- 配置文件：`config.json`
- 数据缓存：`data/cache.json`

## 配置说明

创建 `config.json`：
```json
{
  "sources": {
    "polymarket": {
      "enabled": true,
      "count": 10
    },
    "v2ex": {
      "enabled": true,
      "count": 10
    },
    "hackernews": {
      "enabled": true,
      "count": 10
    }
  },
  "output": {
    "telegram": {
      "enabled": false,
      "chat_id": ""
    },
    "email": {
      "enabled": false,
      "to": ""
    }
  },
  "trends": {
    "track_changes": true,
    "cache_hours": 24
  }
}
```

## 趋势分析

### Polymarket 预测走势
- 对比历史数据，分析概率变化
- 识别概率大幅波动的事件
- 标注高风险/高机会市场

### V2EX 热门话题
- 识别技术趋势
- 追踪热点讨论
- 提取关键信息

### Hacker News
- 科技圈热点
- 创业动态
- 技术讨论

## 输出格式

```
📊 每日信息汇总 | 2026-03-15

🔥 Polymarket Breaking (Top 10)
──────────────────────────
1. U.S. evacuates Baghdad Embassy by March 31?
   概率: 67% | 成交量: $23M
   
2. Will Consensys IPO by December 31 2026?
   概率: 45% | 成交量: $15M

...

💬 V2EX 热门 (Top 10)
────────────────────
1. 【职场话题】三本计科毕业 gap 两年，还有机会入行吗
   回复: 43 | 节点:职场话题

2. 【问与答】求教哪里能买到廉价而保真的 claude api
   回复: 37 | 节点:程序员

...

📰 Hacker News (Top 10)
───────────────────────
1. Show HN: I built a tool for...
   点数: 234 | 评论: 56

2. OpenAI releases GPT-5
   点数: 567 | 评论: 123

...

📈 趋势分析
──────────
• Polymarket: 地缘政治事件概率上升
• V2EX: AI工具讨论热度不减
• Hacker News: 开源项目关注度提升

⏰ 更新时间: 2026-03-15 18:00
```

## 高级功能

### 1. 趋势追踪
启用 `track_changes` 后，会：
- 缓存每次抓取的数据
- 对比上次结果
- 标注新增/删除/变化的项目
- 高亮概率大幅变化的事件

### 2. 关键词过滤
配置关注的主题：
```json
{
  "keywords": {
    "include": ["AI", "加密货币", "选举"],
    "exclude": ["广告", "spam"]
  }
}
```

### 3. 自定义数据源
在 `scripts/` 目录下添加新的抓取脚本，遵循现有格式。

## 故障排除

### Playwright 无法启动
```bash
# 检查 Chromium
which chromium-browser

# 重新安装
apt install -y chromium-browser
```

### API 请求失败
```bash
# 测试网络连接
curl -I https://polymarket.com
curl -I https://www.v2ex.com
curl -I https://hacker-news.firebaseio.com
```

### 数据缓存过期
```bash
# 清除缓存
rm /root/.openclaw/workspace/skills/daily-hub-summary/data/cache.json
```

## 定时任务设置

### crontab 示例
```bash
# 每天 9:00 和 18:00 运行
0 9,18 * * * /usr/bin/python3 /root/.openclaw/workspace/skills/daily-hub-summary/scripts/summary.py >> /var/log/daily-summary.log 2>&1
```

### systemd timer（推荐）
```bash
# 创建服务文件
cat > /etc/systemd/system/daily-summary.service << EOF
[Unit]
Description=Daily Hub Summary
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /root/.openclaw/workspace/skills/daily-hub-summary/scripts/summary.py
EOF

# 创建定时器
cat > /etc/systemd/system/daily-summary.timer << EOF
[Unit]
Description=Run Daily Summary twice daily

[Timer]
OnCalendar=*-*-* 09,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 启用
systemctl enable daily-summary.timer
systemctl start daily-summary.timer
```

## 开发计划

- [ ] 支持 Telegram Bot 推送
- [ ] 支持邮件发送
- [ ] 添加更多数据源（Twitter、Reddit等）
- [ ] AI 驱动的摘要生成
- [ ] 趋势预测和预警

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 趋势分析功能详解

### 预测市场走势变化

脚本会自动检测 Polymarket Breaking 事件的变化：

1. **新增事件** 🆕
   - 第一次出现在 Breaking 板块的事件
   - 可能是刚刚发生的突发事件
   - 值得关注其后续发展

2. **消失事件** ❌
   - 从 Breaking 板块消失的事件
   - 可能已解决或失去热度
   - 可以回顾其结果

3. **持续事件** ✅
   - 仍然在 Breaking 板块的事件
   - 可以追踪其概率变化（未来版本）

### 趋势分析的实际应用

**地缘政治监控**：
- 新增战争/冲突相关事件 → 局势升级
- 消失相关事件 → 局势缓和

**选举预测**：
- 新增候选人民调 → 选情变化
- 概率大幅波动 → 重要事件发生

**经济指标**：
- 新增经济相关事件 → 新的关注点
- 消失事件 → 问题解决或失去关注

### 趋势检测原理

脚本使用缓存机制：
1. 第一次运行：建立基线缓存
2. 后续运行：对比当前数据与缓存
3. 检测变化：新增、消失、持续
4. 生成报告：标注变化趋势

### 缓存管理

缓存文件：`data/cache.json`
- 保存上次抓取的数据
- 用于趋势对比
- 自动更新（每次运行时覆盖）
- 可手动删除以重置基线
