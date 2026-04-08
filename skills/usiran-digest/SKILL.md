# US-Iran Digest — 美伊局势自动汇总推送

当收到 cron 触发消息或被要求"更新 usiran-digest"、"推送伊朗局势"时激活。

## 概述

每小时自动从主流媒体抓取美伊战争最新动态，检测是否有新信息，有更新则生成 digest 文件并推送到 GitHub 仓库，触发 GitHub Pages 自动部署。

## 本地仓库

- **路径**: `/root/.openclaw/workspace/usiran-digest/`
- **远程**: `git@github.com:fubug/usiran-digest.git`（main 分支）
- **部署地址**: https://fubug.github.io/usiran-digest/

⚠️ **Git 配置注意**: 全局 git config 中存在 `url.https://github.com/.insteadof` 规则会把 SSH 重写为 HTTPS，已清除。如再次出现，用 `git config --global --unset-all 'url.https://github.com/.insteadof'` 修复。

## 执行流程

### Step 1: 发现最新 Live Blog URL

主流媒体每个重大事件都会开新的 live blog 页面，URL 每天甚至每小时都在变。**不要使用任何写死的 URL**。

用 `web_search` 搜索以下关键词，找到各媒体**当天的** live blog 链接：

```
site:cbsnews.com Iran war live
site:apnews.com Iran war live
site:nytimes.com Iran war live
site:independent.co.uk Iran live
```

从搜索结果中提取最新的 live blog URL（看日期，选当天的）。至少需要拿到 2-3 个 URL。

**降级策略**（按顺序尝试）：
1. `web_search` 找 live blog URL → `web_fetch` 抓取
2. `web_search` 被限流 → 直接用 `web_fetch` 尝试已知的 live blog 模式 URL（见下方）
3. `web_fetch` 也失败 → 仅用 `web_search` 的搜索摘要做信息提取

已知 live blog URL 模式（可作为最后手段尝试，但优先用搜索发现）：
- CBS: `https://www.cbsnews.com/live-updates/iran-war-*`
- AP: `https://apnews.com/live/iran-war-israel-*`
- NYT: `https://www.nytimes.com/live/*/world/iran-war-*`
- Independent: `https://www.independent.co.uk/news/world/middle-east/iran-*-live-*`

### Step 2: 抓取最新信息

拿到 live blog URL 后，用 `web_fetch` 抓取内容（设 maxChars=12000）。

**英文信源（优先级从高到低）**：

| 优先级 | 媒体 | 搜索发现方式 | 可靠性 |
|--------|------|-------------|--------|
| 1 | AP News Live Blog | `web_search` + `web_fetch` | ⭐⭐⭐⭐⭐ |
| 2 | CBS News Live Blog | `web_search` + `web_fetch` | ⭐⭐⭐⭐ |
| 3 | NYT Live Blog | `web_search` + `web_fetch` | ⭐⭐⭐⭐ |
| 4 | Reuters | `web_search` + `web_fetch` | ⭐⭐⭐⭐⭐ |
| 5 | BBC News | `web_search` + `web_fetch` | ⭐⭐⭐⭐⭐ |
| 6 | Al Jazeera Live | `web_search` + `web_fetch` | ⭐⭐⭐⭐ |
| 7 | The Independent Live | `web_search` + `web_fetch` | ⭐⭐⭐ |
| 8 | France 24 | `web_search` + `web_fetch` | ⭐⭐⭐⭐ |

**补充搜索关键词**（live blog 信息不够时）：
- `Iran war latest today 2026`
- `US Iran strikes casualties April 2026`
- `Trump Iran deadline ceasefire`

**中文信源（补充视角）**：

| 媒体 | 方式 | 可靠性 |
|------|------|--------|
| 央视新闻 | `web_fetch` `https://news.cctv.cn/` | ⭐⭐⭐ |
| 联合早报 | `web_fetch` `https://www.zaobao.com.sg/` | ⭐⭐⭐ |
| 华尔街见闻 | `web_search` + `web_fetch` | ⭐⭐ |

**专用情报源（用于交叉验证特定数据）**：

| 来源 | URL | 用途 |
|------|-----|------|
| HRANA（伊朗人权） | `web_fetch` `https://www.en-hrana.org/` | 伊朗平民伤亡数据 |
| UKMTO（英国海事） | `web_fetch` `https://www.ukmto.org/` | 霍尔木兹海峡航运安全 |
| CENTCOM | `web_search` site:centcom.mil | 美军官方数据 |

### Step 3: 检测变化

读取上次推送记录：
```bash
cat /tmp/usiran_digest_last_push.json
```

如果文件不存在，说明是首次运行，直接生成。

对比逻辑：
1. 提取抓取内容中的关键事件（时间戳 + 事件摘要）
2. 与 `/tmp/usiran_digest_last_push.json` 中的 `last_events` 对比
3. 判断是否有**实质性新信息**（不仅仅是措辞变化，而是新的事件发生）

实质性新信息包括但不限于：
- 新的军事行动（空袭、导弹发射、地面进攻）
- 伤亡数字变化
- 外交进展（谈判结果、新提案）
- 重要人物表态或声明
- Deadline 变化
- 油价/市场重大变动
- 联合国或其他国际组织行动

**如果没有实质性新信息**：不生成新文件，不推送，仅记录日志后结束。

### Step 4: 生成 Digest 文件

如果检测到新信息，在仓库中创建新的 digest 文件。

**文件路径**: `/root/.openclaw/workspace/usiran-digest/data/digest/YYYY-MM-DDTHH.md`

文件名中的 `HH` 为当前整点小时（**北京时间 Asia/Shanghai UTC+8**）。如果同一小时已有文件，追加更新而非覆盖。

⚠️ **重要**：始终使用北京时间（Asia/Shanghai）作为文件名和 frontmatter date 的时间基准，与 cron 触发时间保持一致，方便中文用户理解。不要使用 UTC 时间。

**文件格式**:

```markdown
---
id: YYYY-MM-DDTHH
date: YYYY-MM-DDTHH:00:00+08:00
title:
  zh: "中文标题（概括本时段最重要的1-2个事件）"
  en: "English Title (summarize the 1-2 most important events)"
tags:
  - military
  - diplomacy
sources:
  - name: "Source Name"
    url: "https://example.com/article"
---

## 中文摘要

### 核心事件

（最重要的1-2个事件，放在最前面）

### 军事动态

（按时间倒序列出军事相关事件，每条一行，用 - 开头）

### 外交进展

（外交相关事件）

### 关键数据

| 指标 | 数据 | 来源 |
|------|------|------|
| ... | ... | ... |

### 分析判断

（2-3句简洁分析，不要长篇大论）

---

## English Summary

### Core Events

(Mirror of 中文摘要 content in English)

### Military Developments

### Diplomatic Developments

### Key Data

| Metric | Data | Source |
|--------|------|--------|

### Analysis
```

**标签选择**:
- `military` — 军事动态
- `diplomacy` — 外交进展
- `economy` — 经济影响（油价、市场、制裁）
- `politics` — 政治动向（选举、国内政治）

### Step 5: 更新索引

更新 `data/digest/index.json`，在 `files` 数组**头部**插入新条目：

```json
{
  "updated": "YYYY-MM-DDTHH:00:00+08:00",
  "files": [
    {
      "id": "YYYY-MM-DDTHH",
      "file": "YYYY-MM-DDTHH.md",
      "date": "YYYY-MM-DDTHH:00:00+08:00",
      "title": {
        "zh": "...",
        "en": "..."
      },
      "tags": ["..."]
    }
    // ... 历史文件保持不变
  ]
}
```

### Step 6: Git 提交推送

```bash
cd /root/.openclaw/workspace/usiran-digest
git add -A
git commit -m "update: YYYY-MM-DDTHH digest - 简短描述关键事件"
git push origin main
```

### Step 7: 更新状态

写入推送记录：
```bash
echo '{"last_push": "YYYY-MM-DDTHH:00:00+08:00", "last_events": ["事件1", "事件2", ...]}' > /tmp/usiran_digest_last_push.json
```

## 信息质量要求

- **多源交叉验证**：至少2个可靠来源报道才视为事实
- **区分已发生/正在考虑/政治表态**：不要把政治表态当作既定事实
- **标注来源**：每个关键数据点必须标注来源
- **简洁为王**：每条事件1-2句话，不要展开叙述
- **时间敏感**：优先报道最新事件，过时信息不重复
- **避免重复**：与上一份 digest 对比，已有信息不重复写入

## 信源可靠性评级

- ⭐⭐⭐⭐⭐ AP News, Reuters, BBC News
- ⭐⭐⭐⭐ CBS News, NYT, Al Jazeera English, France 24
- ⭐⭐⭐ CNN, Fox News, The Independent
- ⭐⭐⭐ 央视新闻, 联合早报
- ⭐⭐ 华尔街见闻, 搜狐, 网易

## 注意事项

- **永远不要写死 live blog URL**，每次执行都用 `web_search` 发现最新链接
- `web_search` 被限流（bot-detection challenge）时，跳过搜索直接尝试已知 URL 模式
- `web_fetch` 失败时（403/timeout），跳过该源继续下一个
- 每次执行控制在 3-5 分钟内完成
- 不要为了"有内容"而生造信息，宁可跳过推送也不要发布低质量内容
- commit message 用英文，保持简洁
