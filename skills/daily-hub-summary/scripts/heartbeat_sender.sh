#!/bin/bash

MESSAGE_FILE="/tmp/daily_hub_message.txt"
READY_FLAG="/tmp/daily_hub_ready.flag"
SENT_FLAG="/tmp/daily_hub_sent.flag"

# 检查是否有准备好的消息
if [ ! -f "$READY_FLAG" ]; then
    exit 0
fi

# 检查消息文件是否存在
if [ ! -f "$MESSAGE_FILE" ]; then
    exit 0
fi

# 检查是否已经发送过
if [ -f "$SENT_FLAG" ]; then
    READY_TIME=$(stat -c %Y "$READY_FLAG" 2>/dev/null || echo 0)
    SENT_TIME=$(stat -c %Y "$SENT_FLAG" 2>/dev/null || echo 0)
    
    # 如果发送时间晚于准备时间，说明已发送
    if [ "$SENT_TIME" -ge "$READY_TIME" ]; then
        exit 0
    fi
fi

# 读取消息
MESSAGE=$(cat "$MESSAGE_FILE")

# 创建触发文件（通过 OpenClaw 系统事件触发）
echo "$MESSAGE" > /tmp/daily_hub_trigger.txt

# 标记为已发送
touch "$SENT_FLAG"

echo "✅ 消息已触发发送"

