#!/usr/bin/env python3
import subprocess
from datetime import datetime

def send_email_report():
    """发送邮件报告"""
    # 获取当前时间
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # 执行主脚本获取报告
    result = subprocess.run(
        ['python3', '/root/.openclaw/workspace/skills/daily-hub-summary/scripts/trends.py'],
        capture_output=True,
        text=True
    )
    
    report = result.stdout
    
    # 保存到文件（作为邮件内容）
    report_file = '/root/.openclaw/workspace/logs/latest_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"📊 每日信息汇总\n")
        f.write(f"⏰ {timestamp}\n")
        f.write("=" * 60 + "\n\n")
        f.write(report)
    
    print(f"✅ 报告已保存: {report_file}")
    return report_file

if __name__ == "__main__":
    send_email_report()
