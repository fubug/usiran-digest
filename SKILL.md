# usiran-digest Skill

## 概述
usiran-digest是一个专门用于监控美伊战争动态、生成时事简报并推送到GitHub的技能。该技能每小时自动运行，检查最新的美伊战争发展动态，生成结构化的digest文件，并确保推送到GitHub仓库。

## 执行逻辑
1. **目标识别**: 获取当前时间前一个整点时段
2. **新闻监控**: 监控美伊战争相关新闻源
3. **内容生成**: 生成结构化的digest内容
4. **文件保存**: 保存到指定目录
5. **GitHub推送**: 提交并推送到GitHub仓库

## 搜索策略

### 关键词矩阵
- **核心主题**: "Iran war developments 2026", "US Iran military tension", "Middle East conflict latest"
- **地域范围**: "Persian Gulf", "Middle East", "Israel Iran conflict"
- **军事方面**: "military operations", "naval patrols", "aerial reconnaissance", "military deployment"
- **外交方面**: "diplomatic channels", "international mediation", "UN involvement"

### 信源监控
- **国际新闻机构**: BBC, CNN, Reuters, Al Jazeera
- **专业军事媒体**: Jane's Defence, Defense News
- **政府发布**: Pentagon, State Department, Iranian military
- **国际组织**: UN, NATO, GCC

## 内容结构

### 前matter格式
```yaml
---
id: 2026-04-28T21
date: 2026-04-28T21:00:00+08:00
title:
  zh: "美伊战争动态：持续军事对峙与外交僵持"
  en: "Iran War Developments: Military Standoff and Diplomatic Deadlock"
tags:
  - military
  - diplomacy
  - middle-east
sources:
  - name: "News Source Name"
    url: "https://example.com/article"
---
```

### 内容模板
#### 中文摘要
- 核心事件（按时间倒序）
- 军事动态
- 外交进展
- 关键数据（表格形式）
- 分析判断

#### English Summary
- Core Events (chronological reverse order)
- Military Developments
- Diplomatic Developments
- Key Data (table format)
- Analysis

### 时间要求
- **监控窗口**: 每小时的最后15分钟
- **生成时间**: 整点后5分钟内
- **提交推送**: 整点后10分钟内

## 质量控制

### 信源验证
- 所有引用链接必须有效（HTTP 200状态码）
- 优先使用权威新闻机构
- 避免使用不可靠的小道消息

### 内容准确性
- 时间、地点、人物必须准确
- 军事数据必须来自官方或权威来源
- 避免未经证实的信息

### 语言质量
- 中文摘要和英文Summary必须准确对应
- 使用专业、客观的新闻语言
- 避免主观臆断和情绪化表述

## 输出格式

### 文件命名
- 格式: `2026-MM-DDTHH.md`
- 示例: `2026-04-28T21.md`
- 位置: `/data/digest/` 目录

### Git操作
1. 添加文件到git
2. 提交信息格式: `Add digest for 2026-MM-DDTHH`
3. 推送到远程仓库
4. 确保提交成功

## 异常处理

### 网络异常
- 如果主要信源无法访问，备用信源
- 如果长时间无网络，使用备用内容模板

### 内容异常
- 如果没有重大新闻，保持原状监控
- 如果出现严重错误，回滚到上一个可用版本

### 系统异常
- 如果脚本失败，重试机制
- 如果持续失败，发送警报通知

## 执行频率
- **每小时整点执行**
- **针对前一个整点时段**
- **失败重试**: 最多3次

## 监控指标
- 新闻获取成功率
- 内容生成质量评分
- Git推送成功率
- 执行时间监控

---

**最后更新**: 2026-04-28
**版本**: 1.0