#!/bin/bash
# 监控脚本 - 每5分钟执行一次主脚本

LOG_FILE="/root/.openclaw/workspace/logs/trends_test.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "$(date '+%Y-%m-%d %H:%M:%S') 监控启动" >> "$LOG_FILE"
echo "⏰ 每5分钟执行一次主脚本" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

while true; do
    # 获取当前时间
    current_time=$(date '+%H:%M')
    
    # 记录开始执行
    echo "$(date '+%Y-%m-%d %H:%M:%S') ========== 开始执行 ==========" >> "$LOG_FILE"
    
    # 执行主脚本
    python3 /root/.openclaw/workspace/skills/daily-hub-summary/scripts/trends.py >> "$LOG_FILE" 2>&1
    
    # 记录执行完成
    echo "$(date '+%Y-%m-%d %H:%M:%S') ========== 执行完成 ==========" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # 等待5分钟
    sleep 300
done