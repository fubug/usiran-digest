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

---

## 伊朗战争监控 — 已恢复 ✅

**状态**: 2026-04-23 用户确认恢复
**OpenClaw Cron**: `usiran-digest-hourly` — 每小时整点自动执行
**累计产出**: 58 份摘要，覆盖战事升级→停火→谈判全周期
**部署**: https://fubug.github.io/usiran-digest/
**备注**: index.json 已于 2026-04-23 完整重建（12→58条）

---

## 其他检查

- 邮件（如果有）
- 日历（如果有）
- 天气（如果需要）
