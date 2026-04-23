#!/usr/bin/env python3
import json
import re
from datetime import datetime, timedelta

def check_timestamp_compliance(content, target_hour):
    """Check if timestamps are within the valid window [T-1h, T]"""
    timestamp_pattern = r'(?:（|\()(\d{1,2}:\d{2})(?:）|\))'
    matches = re.findall(timestamp_pattern, content)
    
    issues = []
    valid_timestamps = []
    
    for timestamp_str in matches:
        # Parse timestamp (assuming Beijing time)
        hour, minute = map(int, timestamp_str.split(':'))
        
        # Check if timestamp is within [T-1h, T]
        if hour == target_hour - 1 and minute >= 0:
            valid_timestamps.append(timestamp_str)
        elif hour == target_hour and minute >= 0:
            valid_timestamps.append(timestamp_str)
        else:
            issues.append(f"时间戳 {timestamp_str} 超出有效窗口")
    
    return valid_timestamps, issues

def check_content_substantive(content):
    """Check if content has substantive events"""
    # Check for placeholder content
    placeholder_indicators = [
        "系统维护", "信息维护时段", "graceful degradation",
        "无重大新事件", "信源状态"
    ]
    
    # Check for specific event indicators
    event_indicators = [
        "军事", "外交", "冲突", "行动", "扣押", "命令",
        "ship", "military", "diplomatic", "conflict", "action", "seizure"
    ]
    
    has_placeholders = any(indicator in content for indicator in placeholder_indicators)
    has_events = any(indicator in content for indicator in event_indicators)
    
    return has_events and not has_placeholders

def check_sources_compliance(frontmatter):
    """Check if sources are compliant"""
    sources = frontmatter.get('sources', [])
    
    if not sources:
        return False, "无信源"
    
    valid_sources = []
    invalid_sources = []
    
    for source in sources:
        url = source.get('url', '')
        name = source.get('name', '')
        
        if any(domain in url for domain in ['apnews.com', 'reuters.com', 'bbc.com', 'cnn.com']):
            valid_sources.append(name)
        elif any(indicator in name.lower() for indicator in ['system', 'generated', 'maintenance']):
            invalid_sources.append(name)
    
    return len(valid_sources) > 0, valid_sources, invalid_sources

def check_format_compliance(frontmatter, filename):
    """Check format compliance"""
    issues = []
    
    # Check frontmatter existence
    if not frontmatter:
        issues.append("缺少 frontmatter")
        return issues
    
    # Check id consistency
    file_id = filename.replace('.md', '')
    frontmatter_id = frontmatter.get('id')
    if frontmatter_id != file_id:
        issues.append(f"id 不一致: 文件名={file_id}, frontmatter={frontmatter_id}")
    
    # Check date format
    date = frontmatter.get('date')
    if date:
        date_str = str(date)
        if '+08:00' not in date_str:
            issues.append("date 格式错误，应使用 +08:00")
    
    # Check title
    title = frontmatter.get('title', {})
    if not title:
        issues.append("标题为空")
    else:
        zh_title = title.get('zh', '')
        en_title = title.get('en', '')
        if len(zh_title) < 5:
            issues.append("中文标题过短")
        if len(en_title) < 5:
            issues.append("英文标题过短")
    
    return issues

def analyze_digest(file_path):
    """Analyze a single digest file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
    frontmatter = None
    if frontmatter_match:
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
        except:
            pass
    
    # Extract filename and hour
    filename = file_path.split('/')[-1]
    target_hour = int(filename.split('T')[1].split('.')[0])
    
    # Perform checks
    checks = {
        'timestamp_compliance': {'valid': [], 'issues': []},
        'content_substantive': check_content_substantive(content),
        'sources_compliance': {'valid': False, 'valid_sources': [], 'invalid_sources': []},
        'format_compliance': [],
        'frontmatter_exists': frontmatter is not None
    }
    
    # Timestamp compliance
    valid_timestamps, timestamp_issues = check_timestamp_compliance(content, target_hour)
    checks['timestamp_compliance']['valid'] = valid_timestamps
    checks['timestamp_compliance']['issues'] = timestamp_issues
    
    # Sources compliance
    sources_valid, valid_sources, invalid_sources = check_sources_compliance(frontmatter)
    checks['sources_compliance']['valid'] = sources_valid
    checks['sources_compliance']['valid_sources'] = valid_sources
    checks['sources_compliance']['invalid_sources'] = invalid_sources
    
    # Format compliance
    checks['format_compliance'] = check_format_compliance(frontmatter, filename)
    
    return checks, frontmatter

def main():
    file_path = "/root/.openclaw/workspace/usiran-digest/data/digest/2026-04-23T22.md"
    checks, frontmatter = analyze_digest(file_path)
    
    print("📋 usiran-digest-check 审计报告 | 2026-04-23 T22:10")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"目标: T22")
    
    # Determine overall result
    has_issues = False
    fix_needed = False
    
    # Check timestamp compliance
    if checks['timestamp_compliance']['issues']:
        has_issues = True
        print(f"检查项:")
        print(f"  时间窗口: ❌ 有 {len(checks['timestamp_compliance']['issues'])} 个问题")
        for issue in checks['timestamp_compliance']['issues']:
            print(f"    - {issue}")
    else:
        print(f"  时间窗口: ✅")
    
    # Check content substantive
    if checks['content_substantive']:
        print(f"  内容实质: ✅")
    else:
        has_issues = True
        print(f"  内容实质: ❌")
    
    # Check sources compliance
    if checks['sources_compliance']['valid']:
        print(f"  信源合规: ✅")
    else:
        has_issues = True
        print(f"  信源合规: ❌")
        print(f"    有效信源: {checks['sources_compliance']['valid_sources']}")
        print(f"    无效信源: {checks['sources_compliance']['invalid_sources']}")
    
    # Check format compliance
    if checks['format_compliance']:
        has_issues = True
        print(f"  格式合规: ❌")
        for issue in checks['format_compliance']:
            print(f"    - {issue}")
    else:
        print(f"  格式合规: ✅")
    
    # Frontmatter existence
    if not checks['frontmatter_exists']:
        has_issues = True
        print(f"  Frontmatter: ❌ 缺失")
    else:
        print(f"  Frontmatter: ✅")
    
    # Determine final result
    if not has_issues:
        print("\n结果: ✅ 通过")
    elif fix_needed:
        print("\n结果: ⚠️ 已修复")
    else:
        print("\n结果: ❌ 需要修复")

if __name__ == "__main__":
    import yaml
    main()