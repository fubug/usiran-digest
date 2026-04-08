# MEMORY.md - 长期记忆

> **最后更新**: 2026-03-26
> **维护者**: void

---

## 🤖 GLM 模型信息

### 当前使用
- **模型**: glmcode/glm-4.7
- **提供商**: glmcode
- **状态**: ✅ 正常使用中

### GLM-5 Lite套餐支持状态
- **之前**: ❌ 不支持
- **现在**: ⏰ 预计3月底支持
- **GLM-5-Turbo**: ⏰ 预计4月内支持

### 待办事项
- [ ] 3月底检查 GLM-5 Lite套餐支持状态
- [ ] 测试 GLM-5 的实际性能表现

---

## 💻 工具配置

### 浏览器工具
- **OpenClaw browser**: ❌ 不可用（持续超时）
- **agent-browser CLI**: ✅ 可用
  - 路径: `/root/.local/share/pnpm/agent-browser`
  - 版本: 0.20.13
  - 命令: `agent-browser open <URL> --headless`

### 数据获取方案
| 方法 | 状态 | 用途 |
|------|------|------|
| V2EX API | ✅ | 热门话题 |
| Hacker News API | ✅ | 科技新闻 |
| 联合早报正则 | ✅ | 新闻 |
| web_fetch | ✅ | 静态页面 |
| agent-browser CLI | ✅ | 动态页面（备用） |
| 腾讯财经API | ✅ | A股实时行情（如茅台） |
| TickFlow | ✅ | A股历史数据（24年完整K线） |

---

## 📦 项目监控

### idea-claude-code-gui
- **当前版本**: v0.3.0
- **更新日期**: 2026-03-17
- **状态**: ✅ 已更新

---

## ⏰ 定时任务

### 每日信息汇总
- **执行时间**: 每天 10:00
- **数据源**: V2EX + Hacker News + 联合早报
- **状态**: ✅ 正常运行

### Cron 任务提醒
- **脚本**: `/tmp/minute_time_reminder.py`
- **频率**: 每分钟
- **状态**: ✅ 已设置（测试中）

---

## 🔧 SkillHub

### 已安装技能
- **cron-scheduling**: ✅ 已安装
- **glm-config**: ✅ 已创建（2026-03-26）
- **ima**: ✅ 已安装（2026-03-26）
  - 路径: `/root/.openclaw/workspace/skills/ima`
  - 功能: 笔记管理 + 知识库操作
  - 官网: https://ima.qq.com
  - 需要凭证: Client ID + API Key
- **find-skills**: ✅ 已有
- **skill-creator**: ✅ 已有

---

## 📝 重要决策

### 2026-03-17
- 确认使用 agent-browser CLI 替代 OpenClaw browser 工具
- 更新 idea-claude-code-gui 到 v0.3.0

### 2026-03-25
- 成功获取 Arena.ai 排行榜数据
- 确认 Arena.ai 提供公开的 JSON API

### 2026-03-26
- 创建 glm-config skill
- 设置每分钟时间提醒（测试中）
- 安装 ima skill（笔记管理 + 知识库操作）
- 测试 TickFlow 和腾讯财经API获取股票数据

---

## 🎯 待办事项

### 优先级高
- [ ] 3月底检查 GLM-5 Lite套餐支持状态
- [ ] 测试 cron 时间提醒功能

### 优先级中
- [ ] 监控 idea-claude-code-gui 新版本
- [ ] 优化每日信息汇总推送时间

### 优先级低
- [ ] 整理更多技术文档
- [ ] 清理旧的临时文件

---

## 💰 金融数据工具

### 腾讯财经API
**用途**: A股实时行情查询
**特点**:
- ✅ 实时数据（当前价格、涨跌幅）
- ✅ 无需API Key，直接使用
- ✅ 支持A股、指数查询
- ❌ 不支持美股、港股

**使用示例**:
```bash
# 查询茅台 (600519.SH)
curl -s "http://qt.gtimg.cn/q=sh600519" | iconv -f GBK -t UTF-8
```

**返回数据**:
- 当前价、涨跌幅、成交量、成交额
- 今开、最高、最低、昨收
- 52周最高/最低、市盈率等

**限制**:
- 只支持中国市场
- 数据格式需要解析
- 不提供历史K线

---

### TickFlow
**官网**: https://tickflow.org
**GitHub**: https://github.com/tickflow-org/tickflow
**文档**: https://docs.tickflow.org
**用途**: A股、美股、港股、期货历史数据
**特点**:
- ✅ Python SDK，易用性强
- ✅ 免费版提供24年完整历史数据
- ✅ pandas DataFrame格式
- ✅ 从上市日开始的完整K线
- ❌ 免费版只有历史数据，无实时行情

**免费服务**:
```python
from tickflow import TickFlow

# 免费服务（无需注册）
tf = TickFlow.free()

# 获取日K线数据
df = tf.klines.get("600519.SH", period="1d", count=100, as_dataframe=True)

# 获取标的信息
instruments = tf.instruments.batch(symbols=["600519.SH", "000001.SZ"])
```

**数据范围**:
- 最多: 5,961条日K线数据
- 时间跨度: 约24.6年
- 日期范围: 2001-08-27 → 2026-03-26（茅台为例）
- 支持市场: A股、美股、港股、期货

**完整服务**（需要注册）:
- 实时行情
- 分钟级K线（1m、5m、15m、30m、60m）
- 盘中实时更新
- 更高频率访问

**安装**:
```bash
pip install "tickflow[all]" --upgrade
```

---

**备注**: 此文件保存重要的长期记忆和配置信息，定期更新。
