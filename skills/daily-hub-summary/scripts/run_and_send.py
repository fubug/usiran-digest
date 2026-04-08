#!/usr/bin/env python3
import subprocess
import sys

def main():
    """执行每日信息汇总并发送到 Telegram"""
    
    # 执行主脚本
    result = subprocess.run(
        ['python3', '/root/.openclaw/workspace/skills/daily-hub-summary/scripts/trends.py'],
        capture_output=True,
        text=True
    )
    
    report = result.stdout
    
    # 提取关键信息
    lines = report.split('\n')
    
    # 找到 Polymarket 部分
    polymarket_section = []
    v2ex_section = []
    hn_section = []
    
    current_section = None
    for line in lines:
        if 'Polymarket Top 10' in line:
            current_section = 'polymarket'
        elif 'V2EX 热门' in line:
            current_section = 'v2ex'
        elif 'Hacker News' in line:
            current_section = 'hn'
        elif current_section == 'polymarket' and line.strip():
            if line.startswith('#'):
                polymarket_section.append(line)
        elif current_section == 'v2ex' and line.strip():
            if line[0].isdigit() and '.' in line:
                v2ex_section.append(line)
        elif current_section == 'hn' and line.strip():
            if line[0].isdigit() and '.' in line:
                hn_section.append(line)
    
    # 构建消息
    message_parts = [
        "📊 每日信息汇总",
        "",
        "🔥 Polymarket Top 3（按24小时成交量）"
    ]
    
    # 添加 Polymarket 前3条
    for i, line in enumerate(polymarket_section[:3]):
        if line.strip():
            message_parts.append(f"{i+1}. {line.strip()}")
    
    message_parts.extend([
        "",
        "💬 V2EX 热门 Top 3"
    ])
    
    # 添加 V2EX 前3条
    for i, line in enumerate(v2ex_section[:3]):
        if line.strip():
            message_parts.append(f"{i+1}. {line.strip()}")
    
    message_parts.extend([
        "",
        "📰 Hacker News Top 3"
    ])
    
    # 添加 HN 前3条
    for i, line in enumerate(hn_section[:3]):
        if line.strip():
            message_parts.append(f"{i+1}. {line.strip()}")
    
    message_parts.extend([
        "",
        f"⏰ 更新时间: {subprocess.check_output(['date', '+%H:%M']).decode().strip()}",
        "📈 数据来源: Polymarket Gamma API + V2EX + Hacker News"
    ])
    
    message = '\n'.join(message_parts)
    
    # 打印消息（用于日志）
    print(message)
    
    # 保存到文件
    with open('/tmp/daily_hub_summary.txt', 'w', encoding='utf-8') as f:
        f.write(message)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
