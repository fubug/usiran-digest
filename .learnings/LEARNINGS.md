# Learnings

记录用户纠正、知识缺口、最佳实践。

## [LRN-20260315-001] best_practice

**Logged**: 2026-03-15T13:59:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
A股实时数据获取最佳方案对比

### Details
测试了7个A股数据源：

**✅ 推荐使用：**
1. **腾讯行情** (https://qt.gtimg.cn/q=sh600519)
   - 免费、无需认证
   - 数据完整（价格、成交量、买卖盘、市盈率）
   - 15-20秒延迟
   - 支持A股（sh/sz）和港股（hk）
   - 测试成功率100%
   - ⭐⭐⭐⭐⭐

2. **集思录** (www.jisilu.cn)
   - 分级基金数据国内最全 ⭐⭐⭐⭐⭐
   - 可转债数据完整 ⭐⭐⭐⭐⭐
   - 套利机会提醒 ⭐⭐⭐⭐
   - 需要Cookie认证
   - 适合专业投资者

**❌ 不推荐：**
- 新浪财经 - HTTP 403被限制
- 网易财经 - DNS解析失败
- 东方财富 - API异常
- 雪球API - HTTP 400

**代码格式：**
- 上海：sh + 6位代码（如 sh600519）
- 深圳：sz + 6位代码（如 sz000001）
- 港股：hk + 4位代码（如 hk0700）

### Suggested Action
1. 普通股票用腾讯行情接口
2. 分级基金/可转债用集思录
3. 创建统一的股票数据获取函数
4. 支持多数据源备份

### Metadata
- Source: testing
- Related Files: skills/agent-browser/SKILL.md
- Tags: stock-api, a-share, data-source, jisilu, tencent-finance
- Pattern-Key: stock.data_source.selection
- Recurrence-Count: 2
- First-Seen: 2026-03-15
- Last-Seen: 2026-03-15

---

## [LRN-20260315-002] best_practice

**Logged**: 2026-03-15T14:01:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
集思录数据需要Cookie认证

### Details
集思录的API接口（如分级基金、可转债）需要登录后的Cookie。

**测试结果：**
- ✅ 网页可以访问（320KB数据）
- ❌ API需要Cookie（HTTP 404或空响应）
- ⚠️ 需要模拟登录或手动获取Cookie

**集思录特色数据：**
1. 分级基金：折溢价率、A/B份额价格
2. 可转债：转股价、溢价率、剩余规模
3. 套利机会：实时提醒
4. 社区观点：投资者情绪

### Suggested Action
1. 创建集思录Cookie获取指南
2. 提供Selenium自动登录方案
3. 或手动复制Cookie后使用

### Metadata
- Source: testing
- Related Files: None
- Tags: jisilu, cookie, authentication, structured-fund, convertible-bond
- Pattern-Key: jisilu.auth.requirement
- Recurrence-Count: 1
- First-Seen: 2026-03-15
- Last-Seen: 2026-03-15

---

## [LRN-20260315-003] data_source

**Logged**: 2026-03-15T14:04:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
Polymarket预测市场API可用，数据结构为嵌套字典

### Details
**测试结果：**
- ✅ **Clob API**: https://clob.polymarket.com/markets 可用
- ✅ 返回格式：`{"data": [...], "next_cursor": "...", "limit": ..., "count": ...}`
- ⚠️ 数据在 `data` 字段中，不是直接的列表
- ⚠️ 测试时数据较旧（2023年），可能是测试数据

**API参数：**
```python
params = {
    'active': 'true',        # 只显示活跃市场
    'limit': 15,             # 返回数量
    'order': 'volume',       # 排序字段
    'order_direction': 'desc' # 排序方向
}
```

**主要字段：**
- `market_id`: 市场唯一标识
- `question`: 预测问题
- `price`: 当前概率（0-1之间）
- `volume`: 成交量（美元）
- `condition_id`: 条件ID
- `ticker`: 市场代码（如果有）

**市场类型：**
- 🏛️ 政治/选举
- 💎 加密货币
- ⚽ 体育赛事
- 🌍 地缘政治
- 📈 经济指标

**使用示例：**
```python
import requests

url = "https://clob.polymarket.com/markets"
params = {'active': 'true', 'limit': 10, 'order': 'volume', 'order_direction': 'desc'}
response = requests.get(url, params=params)
result = response.json()
markets = result['data']  # 注意：数据在data字段中
```

### Suggested Action
1. 创建Polymarket数据获取函数
2. 支持按类型过滤（政治、加密等）
3. 添加价格变化监控
4. 与实际结果对比验证

### Metadata
- Source: testing
- Related Files: None
- Tags: polymarket, prediction-market, api, data-source
- Pattern-Key: polymarket.api.structure
- Recurrence-Count: 1
- First-Seen: 2026-03-15
- Last-Seen: 2026-03-15

---

## [LRN-20260315-004] best_practice

**Logged**: 2026-03-15T14:30:00Z
**Priority**: **critical**
**Status**: pending
**Area**: infra

### Summary
**重要：动态网页必须使用 agent-browser，不能用 web_fetch**

### Details
**错误案例：**
- 任务：获取 Polymarket Breaking 板块第一条新闻
- 我的做法：用 `web_fetch` 抓取 https://polymarket.com
- 结果：得到的是静态HTML（原油价格），不是真实用户界面
- 用户看到的：JavaScript渲染后的真实数据（欧足联欧洲联赛：大多数红牌）

**问题根源：**
1. **web_fetch 的局限**：只能抓取静态HTML，无法执行JavaScript
2. **现代网站架构**：Polymarket使用 Next.js + React，数据通过JS动态加载
3. **数据准确性**：web_fetch 得到的是预渲染或缓存数据，不是实时内容

**用户纠正：**
- 用户看到的第一条："欧足联欧洲联赛：大多数红牌"
- 我抓取到的："原油价格突破$100（84%概率）"
- **用户的数据才是准确的！**

### Suggested Action
**✅ 必须使用 agent-browser**
- 对于动态网页（JavaScript渲染）
- 对于需要登录的页面
- 对于SPA（单页应用）
- 对于实时数据（股票、预测市场等）

**❌ 不要使用 web_fetch**
- 对于需要JavaScript的网站
- 对于实时性要求高的数据

**工作流程：**
1. 优先使用 agent-browser + snapshot
2. 获取用户界面的真实数据
3. 用 refs 定位元素
4. 验证数据的实时性

### Metadata
- Source: user_feedback
- Related Files: skills/agent-browser/SKILL.md
- Tags: agent-browser, web-fetch, dynamic-content, javascript-rendering, critical-lesson
- Pattern-Key: web.fetch.vs.agent.browser
- Recurrence-Count: 1
- First-Seen: 2026-03-15
- Last-Seen: 2026-03-15

---

## [LRN-20260315-005] environment_limitation

**Logged**: 2026-03-15T14:32:00Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
当前环境缺少Chrome浏览器，无法使用agent-browser

### Details
**测试结果：**
- ❌ Chrome未安装：`which google-chrome` 返回空
- ❌ agent-browser失败：Missing X server or $DISPLAY
- ❌ Playwright超时：Page.goto timeout 30000ms exceeded

**环境限制：**
- 服务器是无图形界面环境（无X11）
- 未安装Chrome浏览器
- 网络连接可能有限制

**可用工具：**
- ✅ Playwright CLI：已安装但网络超时
- ✅ Python requests：可用于简单API
- ✅ curl：命令行工具

**临时方案：**
1. 依赖用户提供的信息（最准确）
2. 使用官方API（如Polymarket Clob API）
3. 等待环境配置好Chrome后再使用agent-browser

### Suggested Action
1. 记录环境限制
2. 在有GUI的环境中使用agent-browser
3. 当前优先使用API或用户输入

### Metadata
- Source: testing
- Related Files: None
- Tags: environment, chrome, agent-browser, limitation, x11
- Pattern-Key: environment.chrome.missing
- Recurrence-Count: 1
- First-Seen: 2026-03-15
- Last-Seen: 2026-03-15

---
