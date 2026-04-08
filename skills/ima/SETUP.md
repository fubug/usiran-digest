# IMA 技能配置指南

## 🎯 功能简介

IMA 技能（腾讯笔记）支持：
- 📝 **笔记管理**：搜索、浏览、创建、追加笔记
- 📚 **知识库操作**：上传文件、添加网页、搜索知识库

---

## 📋 获取 API Key

### 第一步：访问 IMA 开放平台

打开浏览器，访问：**https://ima.qq.com/agent-interface**

### 第二步：获取凭证

登录后，你会看到：
- **Client ID**：类似 `abc123def456` 的字符串
- **API Key**：类似 `sk_xxxxxxxxxxxxxxxx` 的密钥

---

## 🔧 配置方法

### 方法 A：配置文件（推荐）

创建配置目录并保存凭证：

```bash
# 创建配置目录
mkdir -p ~/.config/ima

# 保存 Client ID
echo "你的Client ID" > ~/.config/ima/client_id

# 保存 API Key
echo "你的API Key" > ~/.config/ima/api_key
```

**示例**：
```bash
mkdir -p ~/.config/ima
echo "abc123def456" > ~/.config/ima/client_id
echo "sk_xxxxxxxxxxxxxxxx" > ~/.config/ima/api_key
```

### 方法 B：环境变量

设置环境变量（临时有效，重启后失效）：

```bash
export IMA_OPENAPI_CLIENTID="你的Client ID"
export IMA_OPENAPI_APIKEY="你的API Key"
```

**永久生效**（添加到 `~/.bashrc` 或 `~/.zshrc`）：

```bash
echo 'export IMA_OPENAPI_CLIENTID="你的Client ID"' >> ~/.bashrc
echo 'export IMA_OPENAPI_APIKEY="你的API Key"' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ 验证配置

配置完成后，可以通过以下命令验证：

```bash
# 检查配置文件
cat ~/.config/ima/client_id
cat ~/.config/ima/api_key

# 或者检查环境变量
echo $IMA_OPENAPI_CLIENTID
echo $IMA_OPENAPI_APIKEY
```

---

## 🔒 安全说明

- ✅ 凭证**仅**发送到 IMA 官方 API (`ima.qq.com`)
- ✅ 凭证**不会**被记录到日志或其他文件
- ✅ 凭证**不会**发送到任何第三方服务
- ⚠️ 请妥善保管你的 API Key，不要泄露给他人

---

## 📖 使用示例

配置完成后，你就可以对 AI 说：

- "搜索我的笔记"
- "新建一篇笔记记录今天的会议"
- "把这段内容追加到《学习笔记》里"
- "上传这个文件到知识库"
- "搜索知识库里的相关内容"

---

## 🆘 常见问题

### Q: 配置后还是不能用？
A: 检查 Client ID 和 API Key 是否正确，确保没有多余的空格或换行。

### Q: 提示"缺少凭证"？
A: 确认配置文件路径正确：`~/.config/ima/client_id` 和 `~/.config/ima/api_key`

### Q: API Key 在哪里？
A: 访问 https://ima.qq.com/agent-interface 登录后即可看到

---

**安装时间**：2026-03-26  
**技能版本**：1.1.2  
**文档位置**：`/root/.openclaw/workspace/skills/ima-skill/`
