#!/usr/bin/env python3
"""每日信息汇总 - 执行汇总并通过 OpenClaw message 工具发送"""
import subprocess
import sys
import os
from datetime import datetime

def main():
    """执行汇总并准备发送"""

    # 执行主脚本
    result = subprocess.run(
        ['python3', '/root/.openclaw/workspace/skills/daily-hub-summary/scripts/summary_v2.py'],
        capture_output=True,
        text=True
    )

    report = result.stdout

    # 保存完整报告
    with open('/tmp/daily_hub_summary.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    # 解析报告，提取版本状态部分
    lines = report.split('\n')
    
    version_status_lines = []
    in_version_section = False
    
    for i, line in enumerate(lines):
        if '🔄 版本状态' in line:
            in_version_section = True
            continue
        
        if in_version_section:
            # 遇到下一个部分时停止
            if line.startswith('💬') or line.startswith('📰') or line.startswith('🇸🇬'):
                break
            # 跳过分隔线和空行
            if line.startswith('─') or not line.strip():
                continue
            version_status_lines.append(line.strip())

    # 构建简化的版本状态消息（移除emoji前缀，简化格式）
    message_parts = []
    
    if version_status_lines:
        message_parts.append("🔄 版本状态")
        
        for line in version_status_lines:
            # 移除 emoji 前缀和多余空格
            clean_line = line.strip()
            if clean_line.startswith('📦'):
                clean_line = clean_line[1:].strip()
            elif clean_line.startswith('⏳'):
                clean_line = clean_line[1:].strip()
            elif clean_line.startswith('🎉'):
                clean_line = clean_line[1:].strip()
            
            # 缩进处理
            if clean_line.startswith('最新版本:') or clean_line.startswith('检查时间:') or clean_line.startswith('当前:') or clean_line.startswith('✅'):
                clean_line = '   ' + clean_line
            elif clean_line.startswith('🔗'):
                clean_line = '   ' + clean_line
            
            message_parts.append(clean_line)
        
        message_parts.append("")

    # 提取 V2EX, HN, 联合早报 的前5条
    v2ex_lines = []
    hn_lines = []
    zaobao_lines = []
    
    current_section = None
    for line in lines:
        if '💬 V2EX 热门' in line:
            current_section = 'v2ex'
        elif '📰 Hacker News' in line:
            current_section = 'hn'
        elif '🇸🇬 联合早报' in line:
            current_section = 'zaobao'
        elif line.startswith('─'):
            continue
        elif current_section == 'v2ex' and line.strip() and line[0].isdigit():
            # 移除序号，简化格式
            clean_line = line.strip()
            if clean_line[0].isdigit() and '.' in clean_line:
                clean_line = clean_line[clean_line.index('.')+1:].strip()
            v2ex_lines.append(clean_line)
        elif current_section == 'hn' and line.strip() and line[0].isdigit():
            clean_line = line.strip()
            if clean_line[0].isdigit() and '.' in clean_line:
                clean_line = clean_line[clean_line.index('.')+1:].strip()
            hn_lines.append(clean_line)
        elif current_section == 'zaobao' and line.strip() and line[0].isdigit():
            clean_line = line.strip()
            if clean_line[0].isdigit() and '.' in clean_line:
                clean_line = clean_line[clean_line.index('.')+1:].strip()
            zaobao_lines.append(clean_line)

    # V2EX
    if v2ex_lines:
        message_parts.append("💬 V2EX 热门 Top 5")
        for line in v2ex_lines[:5]:
            message_parts.append(line)
        message_parts.append("")

    # Hacker News
    if hn_lines:
        message_parts.append("📰 Hacker News Top 5")
        for line in hn_lines[:5]:
            message_parts.append(line)
        message_parts.append("")

    # 联合早报
    if zaobao_lines:
        message_parts.append("🇸🇬 联合早报 Top 5")
        for line in zaobao_lines[:5]:
            message_parts.append(line)
        message_parts.append("")

    # 时间和数据源
    current_time = subprocess.check_output(['date', '+%H:%M']).decode().strip()
    message_parts.append(f"⏰ 更新时间: {current_time}")
    message_parts.append("📈 数据来源: V2EX + Hacker News + 联合早报 + 版本监控")

    message = '\n'.join(message_parts)

    # 保存消息到文件
    with open('/tmp/daily_hub_message.txt', 'w', encoding='utf-8') as f:
        f.write(message)

    # 保存发送标记
    with open('/tmp/daily_hub_ready.flag', 'w') as f:
        f.write(datetime.now().isoformat())

    print("✅ 汇总已生成，等待发送...")
    print(f"📁 消息文件: /tmp/daily_hub_message.txt")
    print(f"🚩 发送标记: /tmp/daily_hub_ready.flag")

    return 0

if __name__ == "__main__":
    sys.exit(main())
