#!/bin/bash
VERSION_TRACKING_FILE="/root/.openclaw/workspace/data/version_tracking.json"

# 读取当前版本
REPO="idea-claude-code-gui"
NEW_VERSION="$1"

if [ -z "$NEW_VERSION" ]; then
    echo "❌ 请提供新版本号"
    echo "用法: $0 <新版本号>"
    echo "示例: $0 v0.3.0"
    exit 1
fi

# 更新 tracking 文件
python3 << PYTHON
import json

tracking_file = '/root/.openclaw/workspace/data/version_tracking.json'

with open(tracking_file, 'r') as f:
    tracking = json.load(f)

# 更新当前版本
tracking['idea-claude-code-gui']['current_version'] = '$NEW_VERSION'
tracking['idea-claude-code-gui']['acknowledged'] = False  # 重置确认状态
tracking['idea-claude-code-gui']['notified'] = False
tracking['idea-claude-code-gui']['last_checked'] = '$(date +%Y-%m-%d)'

# 保存
with open(tracking_file, 'w') as f:
    json.dump(tracking, f, indent=2)

print(f"✅ 已更新 idea-claude-code-gui 当前版本为 $NEW_VERSION")
print(f"✅ 继续监控下一个版本...")
PYTHON

