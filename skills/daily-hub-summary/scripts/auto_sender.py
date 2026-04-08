#!/usr/bin/env python3
import time
import subprocess
from datetime import datetime

print("🚀 自动发送服务启动")
print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
print()

last_sent_hour = -1

while True:
    now = datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    # 检查是否需要发送（整点后1-2分钟）
    if current_minute >= 1 and current_minute <= 2 and current_hour != last_sent_hour:
        # 检查是否有新消息
        try:
            with open('/tmp/daily_hub_message.txt', 'r') as f:
                message = f.read()
            
            if message:
                print(f"📱 [{now.strftime('%H:%M')}] 发送消息到 Telegram...")
                print(f"📝 消息长度: {len(message)} 字符")
                
                # 创建发送标记
                with open('/tmp/daily_hub_auto_send.txt', 'w') as f:
                    f.write(message)
                
                # 标记已发送
                last_sent_hour = current_hour
                print(f"✅ 已准备发送")
                
        except FileNotFoundError:
            pass
    
    # 每30秒检查一次
    time.sleep(30)

