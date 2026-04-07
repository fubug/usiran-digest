# US-Iran Digest | 美伊局势追踪

基于全网信源的实时美伊局势汇总，通过 GitHub Pages 部署，以时间线形式展示动态。

## 项目结构

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

## 数据格式约定

### 汇总文件 (`data/digest/YYYY-MM-DDTHH.md`)

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

#### Frontmatter 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识，与文件名一致 |
| `date` | ISO 8601 | 是 | 时段时间戳 |
| `title` | object | 是 | 包含 `zh` 和 `en` 两个键 |
| `tags` | string[] | 否 | 标签，如 `military`, `diplomacy`, `economy`, `politics` |
| `sources` | object[] | 否 | 信源列表，每个包含 `name` 和 `url` |

#### 内容约定

- 正文必须包含 `## 中文摘要` 和 `## English Summary` 两个段落
- 内容使用标准 Markdown 格式
- 支持列表、加粗、链接等常用语法

### 索引文件 (`data/digest/index.json`)

OpenClaw 每次推送新汇总时必须同步更新此文件。

```json
{
  "updated": "2026-04-07T10:00:00Z",
  "files": [
    {
      "id": "2026-04-07T10",
      "file": "2026-04-07T10.md",
      "date": "2026-04-07T10:00:00Z",
      "title": {
        "zh": "中文标题",
        "en": "English Title"
      },
      "tags": ["military", "diplomacy"]
    }
  ]
}
```

## OpenClaw 接入规范

### 推送流程

1. 采集全网信息，去重后生成本时段汇总
2. 创建 `data/digest/YYYY-MM-DDTHH.md` 文件
3. 更新 `data/digest/index.json`，在 `files` 数组**头部**插入新条目
4. Commit 并 push 到 main 分支

### 去重规则

- 如果本时段无新增信息，不生成新文件，不推送
- `id` 全局唯一，不可重复

### 标签体系

| 标签 | 说明 |
|------|------|
| `military` | 军事动态 |
| `diplomacy` | 外交进展 |
| `economy` | 经济影响 |
| `politics` | 政治动向 |

可扩展，新增标签会自动出现在筛选栏。

## 部署

推送到 `main` 分支后，GitHub Actions 自动部署到 GitHub Pages。

在仓库 Settings > Pages 中选择：
- Source: GitHub Actions

## 本地预览

```bash
# 任意静态服务器即可
npx serve .
# 或
python3 -m http.server 8000
```
