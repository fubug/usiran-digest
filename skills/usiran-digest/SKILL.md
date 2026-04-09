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
2. `web_search` 被限流（bot-detection challenge） → 直接用 `web_fetch` 尝试已知的 live blog 模式 URL（见下方）
3. `web_fetch` 也失败（403/空内容/Cloudflare） → **用 Playwright + agent-browser 抓取**（见下方详细步骤）
4. 所有方法都失败 → 仅用 `web_search` 的搜索摘要做信息提取

**⚠️ 绝对不要因为单个工具被拦截就放弃抓取！必须尝试所有可用方法。**

**Playwright 降级方案**（当 web_fetch 被拦截时使用）：

通过 `exec` 工具调用以下 Python 脚本，用 Playwright 无头浏览器抓取页面内容：

```bash
python3 -c "
from playwright.sync_api import sync_playwright
import sys, time

url = sys.argv[1]
max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 15000

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage', '--no-sandbox'
    ])
    ctx = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    )
    ctx.add_init_script(
        'Object.defineProperty(navigator,\"webdriver\",{get:()=>undefined});'
        'Object.defineProperty(navigator,\"plugins\",{get:()=>[1,2,3,4,5]});'
        'window.chrome={runtime:{}};'
    )
    page = ctx.new_page()
    page.goto(url, timeout=20000, wait_until='domcontentloaded')
    time.sleep(3)
    text = page.inner_text('body') or ''
    if len(text) > max_chars:
        text = text[:max_chars]
    print(text)
    browser.close()
" '<URL>' 15000
```

对每个需要抓取的 URL 执行上述命令。环境变量 DISPLAY 已配置为 :99。Playwright 已安装（Chromium 145）。

如果 Playwright 也失败，尝试用 agent-browser CLI：
```bash
agent-browser open '<URL>' --headless
sleep 3
agent-browser snapshot --headless
agent-browser close --headless
```

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
- 新的军事行动（空袭、导弹发射、地面进攻、新打击目标）
- 伤亡数字变化
- 外交进展（谈判结果、新提案、国际组织行动）
- 重要人物表态或声明（总统、外长、军方高层）
- Deadline 变化
- 油价/市场重大变动
- 联合国或其他国际组织行动
- 新的具体地点/目标被打击
- 新的具体数据点（志愿者人数、难民数、拦截数等）

**判断标准要严格**：
- ⚠️ 宁可多推送也不要漏掉重要信息
- ⚠️ 如果抓取到的 live blog 内容与上次 digest 有**任何新的时间戳条目**，都应该视为有更新
- ⚠️ 如果 web_fetch 抓取失败（只拿到导航栏、空内容），**不要判断为无新信息**，应该尝试其他信源
- ⚠️ 如果只抓到搜索摘要，有新的时间线索就视为有更新

**⚠️ 信息战背景下的特别规则**：
- 双方都在进行信息战，假消息、夸大宣传、伪造视频/图片层出不穷
- 对任何单一来源的戏剧性声明（如"击落X架飞机""俘虏飞行员"）保持高度怀疑，**必须有第二个独立信源交叉确认才能写入 digest**
- 伊朗国家媒体倾向夸大战果、伪造证据（如已被 Snopes 辟谣的"被俘飞行员视频"）
- 美方倾向淡化己方伤亡，特朗普关于"零伤亡"的声明曾与 CBS 报道矛盾
- 特朗普言论需要额外审查，其关于伤亡/军事成就的声明经常与独立信源矛盾
- Times of Israel 作为以色列视角的一手来源可用，但需注意其立场偏向性
- 对于无法交叉验证的争议性声明，**在 digest 中标注"未经独立验证"**

**⚠️ 时间窗口过滤（红线规则，违反即质量事故）**：
- digest 中引用的所有事件，**必须是在抓取时间前1小时内发生或发布的**
- **计算方式**：如果当前执行时间为 T02:00，则只收录 01:00-02:00 之间的事件；T02 的事件绝对不能包含 00:xx 时间戳的条目
- 如果 live blog 中的事件只有时间戳但没有具体发布时间，且该事件明显早于1小时前，**不要收入 digest**
- 对于持续时间较长的事件（如停火协议），只有当该时段有新的进展（新声明、新数据、新变化）时才写入
- **不要把前几期已经写过的旧事件换个措辞重新写入**
- ⚠️ **宁可只写1条新事件也不要混入旧事件。如果过滤后只有0条，则跳过推送**
- ⚠️ **生成 digest 后必须逐一检查每条事件的时间戳，确保全部落在 [T-1h, T] 窗口内**

**只有在以下情况才跳过推送**：
- 成功抓取到至少2个信源的完整内容
- 对比后发现所有事件、数据、声明都与上次完全一致
- 确认没有新的时间戳条目
- 筛选1小时时间窗口后，没有符合条件的实质性新事件

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

**⚠️ 关键规则：绝对禁止覆盖 index.json！**

更新 `data/digest/index.json` 时，**必须**先读取现有文件，在 `files` 数组**头部**插入新条目，**保留所有历史条目不变**。如果直接覆盖导致历史记录丢失，属于严重质量事故。

正确做法：
1. 先用 `read` 读取当前 `data/digest/index.json`
2. 解析 JSON，在 `files` 数组第0位插入新条目
3. 更新 `updated` 为最新时间
4. 写回文件

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
    },
    {
      "id": "YYYY-MM-DDTHH-1",
      "file": "YYYY-MM-DDTHH-1.md",
      ...保留所有历史条目，不要删除任何一条...
    }
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

### Step 7: 推送后验证（必执行）

推送完成后，**必须**执行以下检查，确保上线内容符合预期：

1. **index.json 完整性检查**
   - 读取 `data/digest/index.json`，检查 `files` 数组长度
   - 与 `data/digest/` 目录下实际 `.md` 文件数量对比
   - 如果 `files.length` < 实际文件数，说明有条目丢失 → **立即修复并再次推送**

2. **标题完整性检查**
   - 遍历 `files`，检查每条 `title.zh` 和 `title.en` 长度
   - 标题字符数 < 10 的为异常截断 → 需要从对应 `.md` 文件重新提取并修复

3. **线上页面可用性抽查**
   - 用 `web_fetch` 访问 `https://fubug.github.io/usiran-digest/`
   - 确认页面能正常加载，digest 列表展示正常
   - 如页面异常，记录问题但不阻塞（可能是 GitHub Pages 缓存延迟）

**验证失败处理**：如果完整性检查不通过，修复后重新 commit + push，并在日志中记录问题和修复过程。

### Step 8: 更新状态

写入推送记录：
```bash
echo '{"last_push": "YYYY-MM-DDTHH:00:00+08:00", "last_events": ["事件1", "事件2", ...]}' > /tmp/usiran_digest_last_push.json
```

## 信息质量红线（违反则不推送）

以下情况**必须跳过推送**，宁可没有新内容也不要发布低质量 digest：

1. **无具体文章链接**：sources 里的 url 不能是媒体首页（如 `news.cctv.cn/`），必须是**具体文章 URL**
2. **无发布时间**：每个信源的事件必须有可确认的时间点
3. **内容空泛**：只有"局势升级""冲突持续"等泛泛描述，没有任何具体事件细节（地点、人物、数据）
4. **无法交叉验证**：关键事件只有一个模糊来源，无法找到第二个独立报道
5. **可能捏造**：无法追溯到原始报道的内容

## 信息质量要求

- **多源交叉验证**：至少2个可靠来源报道才视为事实
- **区分已发生/正在考虑/政治表态**：不要把政治表态当作既定事实
- **标注来源**：每个关键数据点必须标注来源
- **简洁为王**：每条事件1-2句话，不要展开叙述
- **时间敏感**：优先报道最新事件，过时信息不重复
- **避免重复**：与上一份 digest 对比，已有信息不重复写入

## 信源可靠性评级

- ⭐⭐⭐⭐⭐ AP News, Reuters, BBC News, PBS NewsHour
- ⭐⭐⭐⭐ CBS News, NYT, Al Jazeera English, France 24
- ⭐⭐⭐ CNN, Times of Israel
- ⭐⭐ 联合早报, The Independent
- ❌ 不使用：华尔街见闻、搜狐、网易、央视新闻（聚合平台/无法抓取具体文章）

## 注意事项

- `web_search` 被限流（bot-detection challenge）时，跳过搜索直接尝试已知 URL 模式
- `web_fetch` 失败时（403/timeout/Cloudflare），**必须尝试 Playwright 降级方案**，不能直接放弃
- Playwright 脚本已预配置，直接通过 `exec` 调用 Python 即可
- 即使部分信源不可用，只要拿到 1-2 个可靠信源的内容就足够生成 digest
- 每次执行控制在 5-8 分钟内完成（Playwright 需要额外时间）
- 不要为了"有内容"而生造信息，宁可跳过推送也不要发布低质量内容
- commit message 用英文，保持简洁
- **永远不要写死 live blog URL**，每次执行都用 `web_search` 发现最新链接
