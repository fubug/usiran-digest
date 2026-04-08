#!/usr/bin/env python3
"""自动发送服务 - 在后台持续监控并发送每日汇总"""
import time
import subprocess
from datetime import datetime
import os

MESSAGE_FILE = "/tmp/daily_hub_message.txt"
READY_FLAG = "/tmp/daily_hub_ready.flag"
SENT_TIME_FILE = "/tmp/daily_hub_last_sent.txt"

def send_telegram_message(message):
    """发送消息到 Telegram（通过调用 message 工具）"""
    try:
        # 这里我们只是记录要发送的消息
        # 实际发送会在主会话中通过 heartbeat 检查
        with open('/tmp/daily_hub_pending.txt', 'w') as f:
            f.write(message)
        
        # 创建发送请求标记
        with open('/tmp/daily_hub_request_send.flag', 'w') as f:
            f.write(datetime.now().isoformat())
        
        return True
    except Exception as e:
        print(f"发送错误: {e}")
        return False

def check_and_send():
    """检查并发送消息"""
    # 检查 flag
    if not os.path.exists(READY_FLAG):
        return False
    
    # 检查消息文件
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
    
    # 如果 flag 时间 > 上次发送时间，需要发送
    if ready_time > last_sent:
        # 读取消息
        with open(MESSAGE_FILE, 'r') as f:
            message = f.read()
        
        # 发送
        if send_telegram_message(message):
            # 更新发送时间
            with open(SENT_TIME_FILE, 'w') as f:
                f.write(str(int(time.time())))
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ 已发送汇总")
            return True
    
    return False

def main():
    """主循环"""
    print("🚀 自动发送服务启动")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 立即检查一次
    print("🔍 首次检查...")
    if check_and_send():
        print()
    
    # 持续监控
    while True:
        try:
            time.sleep(30)  # 每30秒检查一次
            check_and_send()
        except KeyboardInterrupt:
            print("\n⏹️  服务已停止")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
            time.sleep(60)  # 出错后等待1分钟再重试

if __name__ == "__main__":
    main()
