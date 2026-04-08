#!/bin/bash
# 监控脚本 - 检查并发送每日汇总

MESSAGE_FILE="/tmp/daily_hub_message.txt"
READY_FLAG="/tmp/daily_hub_ready.flag"
SENT_FLAG="/tmp/daily_hub_sent.flag"
CHAT_ID="8755129385"

# 检查是否有准备发送的消息
if [ -f "$READY_FLAG" ]; then
    # 检查是否已经发送过
    if [ -f "$SENT_FLAG" ]; then
        # 比较时间戳
        READY_TIME=$(stat -c %Y "$READY_FLAG" 2>/dev/null || echo 0)
        SENT_TIME=$(stat -c %Y "$SENT_FLAG" 2>/dev/null || echo 0)
        
        # 如果已经发送过，且发送时间晚于准备时间，跳过
        if [ "$SENT_TIME" -gt "$READY_TIME" ]; then
            exit 0
        fi
    fi
    
    # 检查消息文件是否存在且有内容
    if [ -f "$MESSAGE_FILE" ] && [ -s "$MESSAGE_FILE" ]; then
        # 读取消息内容
        MESSAGE=$(cat "$MESSAGE_FILE")
        
        # 发送到 Telegram（通过 OpenClaw）
        # 注意：这里我们创建一个命令文件，由 OpenClaw 主会话执行
        echo "$MESSAGE" > /tmp/daily_hub_to_send.txt
        
        # 标记为已准备发送
        touch /tmp/daily_hub_needs_send.flag
        
        echo "✅ 消息已准备，等待发送"
    fi
fi
