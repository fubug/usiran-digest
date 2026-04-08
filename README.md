# US-Iran Digest | 美伊局势追踪

[English](#english) | [中文](#中文)

---

## 中文

**在线访问：[https://fubug.github.io/usiran-digest/](https://fubug.github.io/usiran-digest/)**

美伊冲突期间，双方信息战激烈，真假消息满天飞，社交平台上信息严重过载，难以分辨真伪。

本项目旨在从海量信息中筛选可信度较高的信源，按时间线汇总关键动态，提供一份清晰、可追溯的局势追踪记录。

- **信息筛选** — 优先采信主流通讯社、官方声明、战地记者等高可信度信源
- **去重降噪** — 同一事件多方报道合并归纳，剔除未经证实的传言
- **时间线呈现** — 按时段梳理，便于回溯局势演变脉络
- **中英双语** — 同时呈现中外媒体报道视角

### 项目结构

```
usiran-digest/
├── index.html              # 首页
├── css/style.css           # 样式
├── js/app.js               # 应用逻辑
├── data/
│   └── digest/             # OpenClaw 推送目标
│       ├── index.json      # 汇总索引（必须）
│       ├── YYYY-MM-DDTHH.md  # 每时段汇总文件
│       └── ...
├── .github/workflows/
│   └── deploy.yml          # GitHub Pages 自动部署
└── README.md
```

### 数据格式约定

#### 汇总文件 (`data/digest/YYYY-MM-DDTHH.md`)

每个文件代表一个时段的汇总，文件名格式为日期+小时，如 `2026-04-07T10.md`。

```markdown
---
id: 2026-04-07T10
date: 2026-04-07T10:00:00Z
title:
  zh: "中文标题"
  en: "English Title"
tags:
  - military
  - diplomacy
sources:
  - name: "信源名称"
    url: "https://example.com/article"
---

## 中文摘要

中文内容...

## English Summary

English content...
```

##### Frontmatter 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识，与文件名一致 |
| `date` | ISO 8601 | 是 | 时段时间戳 |
| `title` | object | 是 | 包含 `zh` 和 `en` 两个键 |
| `tags` | string[] | 否 | 标签，如 `military`, `diplomacy`, `economy`, `politics` |
| `sources` | object[] | 否 | 信源列表，每个包含 `name` 和 `url` |

##### 内容约定

- 正文必须包含 `## 中文摘要` 和 `## English Summary` 两个段落
- 内容使用标准 Markdown 格式
- 支持列表、加粗、链接等常用语法

#### 索引文件 (`data/digest/index.json`)

OpenClaw 每次推送新汇总时必须同步更新此文件。

```json
{
  "updated": "2026-04-07T10:00:00Z",
  "files": [
    {
      "id": "2026-04-07T10",
      "file": "2026-04-07T10.md",
      "date": "2026-04-07T10:00:00Z",
      "title": { "zh": "中文标题", "en": "English Title" },
      "tags": ["military", "diplomacy"]
    }
  ]
}
```

### OpenClaw 接入规范

#### 推送流程

1. 采集全网信息，去重后生成本时段汇总
2. 创建 `data/digest/YYYY-MM-DDTHH.md` 文件
3. 更新 `data/digest/index.json`，在 `files` 数组**头部**插入新条目
4. Commit 并 push 到 main 分支

#### 去重规则

- 如果本时段无新增信息，不生成新文件，不推送
- `id` 全局唯一，不可重复

#### 标签体系

| 标签 | 说明 |
|------|------|
| `military` | 军事动态 |
| `diplomacy` | 外交进展 |
| `economy` | 经济影响 |
| `politics` | 政治动向 |

可扩展，新增标签会自动出现在筛选栏。

### 部署

推送到 `main` 分支后，GitHub Actions 自动部署到 GitHub Pages。

在仓库 Settings > Pages 中选择 Source: **GitHub Actions**

### 本地预览

```bash
npx serve .
# 或
python3 -m http.server 8000
```

---

## English

**Live site: [https://fubug.github.io/usiran-digest/](https://fubug.github.io/usiran-digest/)**

During the US-Iran conflict, information warfare is intense — unverified claims and fake news flood social media, making it nearly impossible to distinguish fact from fiction.

This project filters high-credibility sources from the noise, summarizes key developments on a timeline, and provides a clear, traceable record of the situation.

- **Source filtering** — Prioritize mainstream wire services, official statements, and frontline reporters
- **Deduplication** — Merge multi-source reports of the same event, exclude unverified claims
- **Timeline view** — Organized by time period for easy review of how the situation evolved
- **Bilingual** — Presenting both Chinese and international media perspectives

### Project Structure

```
usiran-digest/
├── index.html              # Homepage
├── css/style.css           # Styles
├── js/app.js               # App logic
├── data/
│   └── digest/             # OpenClaw push target
│       ├── index.json      # Digest index (required)
│       ├── YYYY-MM-DDTHH.md  # Per-period digest files
│       └── ...
├── .github/workflows/
│   └── deploy.yml          # GitHub Pages auto-deploy
└── README.md
```

### Data Format Specification

#### Digest File (`data/digest/YYYY-MM-DDTHH.md`)

Each file represents a time period's digest. Filename format: date + hour, e.g. `2026-04-07T10.md`.

```markdown
---
id: 2026-04-07T10
date: 2026-04-07T10:00:00Z
title:
  zh: "中文标题"
  en: "English Title"
tags:
  - military
  - diplomacy
sources:
  - name: "Source Name"
    url: "https://example.com/article"
---

## 中文摘要

Chinese content...

## English Summary

English content...
```

##### Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID, matches filename |
| `date` | ISO 8601 | Yes | Period timestamp |
| `title` | object | Yes | Contains `zh` and `en` keys |
| `tags` | string[] | No | Tags: `military`, `diplomacy`, `economy`, `politics` |
| `sources` | object[] | No | Source list with `name` and `url` per entry |

##### Content Convention

- Body must include both `## 中文摘要` and `## English Summary` sections
- Standard Markdown format
- Supports lists, bold, links, and common syntax

#### Index File (`data/digest/index.json`)

OpenClaw must update this file when pushing new digests.

```json
{
  "updated": "2026-04-07T10:00:00Z",
  "files": [
    {
      "id": "2026-04-07T10",
      "file": "2026-04-07T10.md",
      "date": "2026-04-07T10:00:00Z",
      "title": { "zh": "中文标题", "en": "English Title" },
      "tags": ["military", "diplomacy"]
    }
  ]
}
```

### OpenClaw Integration

#### Push Workflow

1. Collect global sources, deduplicate, and generate digest for the period
2. Create `data/digest/YYYY-MM-DDTHH.md`
3. Update `data/digest/index.json`, prepend new entry to `files` array
4. Commit and push to main branch

#### Deduplication Rules

- If no new information this period, do not generate a file or push
- `id` must be globally unique

#### Tag System

| Tag | Description |
|-----|-------------|
| `military` | Military developments |
| `diplomacy` | Diplomatic progress |
| `economy` | Economic impact |
| `politics` | Political developments |

Extensible — new tags automatically appear in the filter bar.

### Deployment

Pushing to `main` triggers GitHub Actions auto-deploy to GitHub Pages.

In repo Settings > Pages, set Source to: **GitHub Actions**

### Local Preview

```bash
npx serve .
# or
python3 -m http.server 8000
```
