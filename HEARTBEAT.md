# HEARTBEAT.md

## 每日信息汇总 - 自动发送检查

**重要**：每次收到用户消息时，检查并发送未发送的汇总！

### **自动化流程**
1. **每个整点（00分）** - 系统级 cron 自动执行汇总脚本
2. **生成消息** - 保存到 `/tmp/daily_hub_message.txt`
3. **创建标记** - `/tmp/daily_hub_ready.flag`

### **发送检查逻辑**
每次收到用户消息时，执行：
1. 检查 `/tmp/daily_hub_ready.flag` 是否存在
2. 检查 `/tmp/daily_hub_message.txt` 是否有内容
3. 读取上次发送时间 `/tmp/daily_hub_last_sent.txt`
4. 如果 flag 时间 > 上次发送时间，**记录为已发送**（更新时间戳）
5. ⚠️ **注意**：当前 Telegram 发送不可用，仅更新发送时间戳以避免重复通知

### **数据源**
- V2EX（中文技术社区）
- Hacker News（科技新闻）
- 联合早报（新加坡新闻）

### **版本监控**
- idea-claude-code-gui (v0.2.9) - 持续监控新版本
- GLM-5 Lite套餐支持状态 - 持续监控支持情况

---

## 伊朗战争监控 - 多源验证系统

**定时任务**: 每6小时运行一次（00:00, 06:00, 12:00, 18:00）

**监控内容**:
- 地面部队部署情况
- 美军伤亡数据
- 伊朗浓缩铀问题
- 和平谈判进展
- 信息冲突分析

**数据源**（按可靠性排序）:
- ⭐⭐⭐⭐⭐ AP News (美联社)
- ⭐⭐⭐⭐⭐ Reuters (路透社)
- ⭐⭐⭐⭐⭐ BBC News
- ⭐⭐⭐⭐ Al Jazeera English
- ⭐⭐⭐⭐ France 24

**专题信息聚合网站**（定期扫描）:
- 🗺️ iranisrael.live — 免费 AI 危机情报仪表盘（飞机/船舶追踪、地震/火灾探测）
- 🗺️ wartrackr.com — 实时交互地图（空袭/导弹/无人机），每15分钟更新
- 📊 epicfurylive.com — 战争成本计时器、伤亡统计、军事力量对比
- 🚢 iranwarroom.com — 实时船舶追踪 + 防务股走势 + AI威胁分析
- ⏰ iran.openintel.news — 每小时自动更新，引用多家主流信源
- 🗺️ iranwarlive.com — 实时地图 + 霍尔木兹海峡状态
- ✈️ thewarstatus.com — 机场关闭 + 航班状态 + 领空限制 + 使馆信息

**特朗普发言追踪**:
- 📱 trumpstruth.org — Truth Social 全文存档（第三方项目，无需登录）
- 📊 natesilver.net/p/iran-war-polls-popularity-approval — Nate Silver 战争民调追踪

**主要媒体实时博客**:
- CNN Live / NYT Live / Al Jazeera Live / CBS Live / AP Live

**快速查看报告**:
```bash
cat /tmp/iran_war_report.txt
```

**手动运行监控**:
```bash
python3 /root/.openclaw/workspace/scripts/iran_war_monitor.py
```

**关键判断原则**:
1. ✅ 关注具体行动（部队部署、伤亡数据）而非政治表态
2. ✅ 多源交叉验证：至少2个可靠来源报道才视为事实
3. ✅ 区分'已发生'、'正在考虑'和'政治表态'
4. ⚠️  警惕选举年言论和谈判策略
5. ⚠️  警惕双方信息战：伊朗夸大战果/伪造证据（如 Snopes 辟谣的'被俘飞行员视频'），特朗普美化叙事（如'零伤亡'与 CBS 报道矛盾）
6. 📊 关注关键时间点（如4月6日最后期限）

**⚡ 关键事件追踪**（截至2026-04-10 17:35 Beijing）:
- 🚨 **停火进一步恶化（Day 2）**：特朗普公开质疑停火存续，科威特遭无人机打击
  - 特朗普Truth Social：伊朗海峡通行"very poor job, dishonourable"（Independent/多源）
 - 科威特遭无人机打击并指责伊朗（U.S. News/Media Line）
- ⚠️ 海峡航运仍严重受阻，停火条件未全面生效（Independent）
- ✅ **美伊2周停火协议**（4月8日达成，多源确认）
  - 特朗普要求海峡开放"without limitation, including tolls"（CNBC/白宫）
  - 巴基斯坦斡旋，下周华盛顿谈判
- 🇨🇳 **中国积极斡旋**——CNBC: "Business trumps politics"
- 🇮🇱 以色列周三打击黎巴嫩杀死303人；内塔尼亚胡授权与黎巴嫩直接谈判
- 🇺🇸 特朗普考虑从欧洲撤军（Reuters），因北约未协助确保海峡安全
- 🏛️ 民主党推动第三次弹劾特朗普 + 舒默推动《战争权力决议》
- 累计（停火前）：伊朗1900+死，黎巴嫩1700+死（+303），以色列20死，美军13死

## 其他检查

- 邮件（如果有）
- 日历（如果有）
- 天气（如果需要）
