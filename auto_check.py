#!/usr/bin/env python3
"""自动检查并发送每日汇总"""
import subprocess
import os
from datetime import datetime

MESSAGE_FILE = "/tmp/daily_hub_message.txt"
READY_FLAG = "/tmp/daily_hub_ready.flag"
SENT_TIME_FILE = "/tmp/daily_hub_last_sent.txt"

def check_and_send():
    """检查并发送未发送的汇总"""
    try:
        # 检查是否有新消息需要发送
        if not os.path.exists(READY_FLAG):
            return False
        
        if not os.path.exists(MESSAGE_FILE):
            return False
        
        # 读取上次发送时间
        last_sent = 0
        if os.path.exists(SENT_TIME_FILE):
            with open(SENT_TIME_FILE, 'r') as f:
                try:
                    last_sent = int(f.read().strip())
                except:
                    pass
        
        # 获取 flag 时间
        ready_time = os.path.getmtime(READY_FLAG)
        
        # 如果有新消息（flag 时间 > 上次发送时间）
        if ready_time > last_sent:
            # 读取消息
            with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                message = f.read()
            
            # 发送到 Telegram
            result = subprocess.run([
                'message',
                'action=send',
                'channel=telegram',
                'target=8755129385',
                f'message={message}'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # 更新发送时间
                with open(SENT_TIME_FILE, 'w') as f:
                    f.write(str(int(datetime.now().timestamp())))
                
                return True
            
            return False
        
        return False
        
    except Exception as e:
        print(f"❌ 自动发送错误: {e}")
        return False

# 自动检查（如果在主会话中）
try:
    result = check_and_send()
    if result:
        print("📱 自动发送成功！")
except Exception as e:
    pass
EOF
chmod +x /root/.openclaw/workspace/auto_check.py
