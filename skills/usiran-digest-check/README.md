# US-Iran Digest Check Skill

这个技能用于按照 SKILL.md 标准执行 US-Iran Digest 的定时检查和生成任务。

## 功能概述

- **定时检查**: 每小时检查前一个整点时段的 digest 内容
- **质量审核**: 按照严格的质量标准对 digest 内容进行审计
- **内容生成**: 如果没有现有 digest 或检测到新进展，则生成新的 digest
- **GitHub 推送**: 将生成的 digest 推送到 GitHub 仓库

## 主要脚本

### 1. digest_hourly_check.py
主要的每小时检查脚本，用于：
- 检查目标时段的 digest 文件是否存在
- 如果不存在，生成新的 digest 内容
- 推送到 GitHub 仓库

**使用方法:**
```bash
python3 digest_hourly_check.py
```

### 2. audit_digest.py
质量审计脚本，按照 SKILL.md 标准对 digest 内容进行详细审计。

**使用方法:**
```bash
python3 audit_digest.py [digest文件路径]
```

### 3. manual_digest_check.py
手动生成 digest 的脚本，用于测试和手动操作。

**使用方法:**
```bash
python3 manual_digest_check.py
```

## 质量标准

### 必须合规项
- **信源真实性**: 所有引用的新闻链接必须真实存在
- **数据准确性**: 所有数据必须来自可靠信源
- **人物真实性**: 所有提及的人物必须真实存在

### 格式规范项
- **时间戳格式**: 必须使用 ISO 8601 Z 格式
- **前matter结构**: 必须包含 id、date、title、tags、sources 字段
- **内容结构**: 中文摘要和 English Summary 必须完整

### 语言质量项
- **客观性**: 避免主观臆断和情绪化表述
- **专业性**: 使用专业、准确的新闻语言
- **翻译质量**: 中英文内容必须准确对应

## 违规等级划分

### 🔴 紧急违规（立即删除）
- 虚假信源（链接不存在）
- 虚构敏感数据（伤亡、军事数据）
- 虚构官方人物和事件

### ⚠️ 重要违规（需修正）
- 时间格式错误
- 内容时效性问题
- 数据准确性存疑

### 🟡 轻微违规（需改进）
- 翻译质量问题
- 表述不够专业
- 标签选择不够精准

## 输出格式

审计报告包含以下部分：
1. **基本信息**: 时间、目标、总体结果
2. **检查项列表**: 逐项检查结果
3. **详细违规分析**: 按严重程度分类
4. **质量评分**: 最终评分
5. **建议操作**: 具体修改建议

## 定时执行

建议通过 cron 定时执行，每小时执行一次：

```bash
0 * * * * /usr/bin/python3 /root/.openclaw/workspace/skills/usiran-digest-check/digest_hourly_check.py
```

## 示例输出

```
=== US-Iran Digest 每小时检查和生成 ===
开始时间: 2026-05-01 07:08:05 UTC
目标时间段: 2026-04-30T23
找到digest文件: /root/.openclaw/workspace/usiran-digest/data/digest/2026-04-30T23.md
ℹ️ 文件已存在，无需重复生成
✅ 每小时digest任务执行完成
```

## 注意事项

1. 确保脚本执行环境有足够的权限
2. Git 操作需要正确的认证信息
3. 网络连接可能影响新闻源检查
4. 定期检查审计报告的质量评估结果