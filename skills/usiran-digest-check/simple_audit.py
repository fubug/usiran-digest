#!/usr/bin/env python3
"""
Simple audit script for US-Iran digest
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import requests

def main():
    print("=== US-Iran Digest 质量审计 ===")
    
    # Use the specific digest file we found
    target_file = "/root/.openclaw/workspace/usiran-digest/data/digest/2026-04-29T16.md"
    
    print(f"📁 目标文件: {target_file}")
    
    # Check if file exists
    if not os.path.exists(target_file):
        print("❌ 目标digest文件不存在")
        return False
    
    # Read the file
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print("✅ 文件读取成功")
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return False
    
    # Parse frontmatter
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print("❌ Frontmatter格式错误")
        return False
    
    # Extract frontmatter content and try to parse it as YAML
    frontmatter_text = frontmatter_match.group(1)
    try:
        import yaml
        frontmatter = yaml.safe_load(frontmatter_text)
        print("✅ Frontmatter解析成功")
    except:
        # If yaml parsing fails, do basic validation
        print("⚠️ YAML解析失败，进行基本验证")
        frontmatter = {}
    
    # Basic validation
    violations = []
    score = 10
    
    # Check required fields
    required_fields = ['id', 'date', 'title', 'tags', 'sources']
    missing_fields = [field for field in required_fields if field not in frontmatter]
    
    if missing_fields:
        violations.append({
            "type": "Frontmatter不完整",
            "description": f"缺少必需字段: {', '.join(missing_fields)}",
            "severity": "重要违规"
        })
        score -= 2
    
    # Check timestamp format
    date_value = frontmatter.get('date', '')
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+|\-)\d{2}:\d{2}$|^Z$', str(date_value)):
        violations.append({
            "type": "时间格式错误",
            "description": f"日期格式不正确: {date_value}",
            "severity": "轻微违规"
        })
        score -= 1
    
    # Check source URLs
    sources = frontmatter.get('sources', [])
    invalid_sources = []
    for source in sources:
        url = source.get('url', '')
        if url and url.startswith('http') and 'Real-time data streams' not in url:
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                if response.status_code != 200:
                    invalid_sources.append({
                        "url": url,
                        "status_code": response.status_code
                    })
            except:
                invalid_sources.append({
                    "url": url,
                    "error": "无法访问"
                })
    
    if invalid_sources:
        violations.append({
            "type": "无效信源链接",
            "description": f"发现无效链接: {invalid_sources}",
            "severity": "紧急违规"
        })
        score -= 3
    
    # Check content structure
    has_chinese_summary = "中文摘要" in content
    has_english_summary = "English Summary" in content
    
    if not has_chinese_summary:
        violations.append({
            "type": "内容结构不完整",
            "description": "缺少中文摘要部分",
            "severity": "重要违规"
        })
        score -= 2
    
    if not has_english_summary:
        violations.append({
            "type": "内容结构不完整",
            "description": "缺少英文摘要部分",
            "severity": "重要违规"
        })
        score -= 2
    
    # Check for sensitive data
    casualty_patterns = [
        r'\d+[\s,]?人死亡',
        r'\d+[\s,]?人受伤',
        r'\d+[\s,]?人伤亡',
    ]
    
    casualties_found = []
    for pattern in casualty_patterns:
        matches = re.findall(pattern, content)
        if matches:
            casualties_found.extend(matches)
    
    if casualties_found:
        violations.append({
            "type": "敏感数据",
            "description": f"发现伤亡数据: {casualties_found}",
            "severity": "重要违规"
        })
        score -= 2
    
    # Check for subjective language
    subjective_patterns = [
        r'显然',
        r'明显',
        r'毫无疑问',
    ]
    
    subjective_found = []
    for pattern in subjective_patterns:
        matches = re.findall(pattern, content)
        if matches:
            subjective_found.extend(matches)
    
    if subjective_found:
        violations.append({
            "type": "主观表述",
            "description": f"发现主观表述: {subjective_found}",
            "severity": "轻微违规"
        })
        score -= 0.5
    
    # Generate final conclusion
    if score >= 9:
        conclusion = "✅ 优秀 - 完全符合质量标准"
    elif score >= 7:
        conclusion = "✅ 良好 - 基本符合质量标准，有轻微改进空间"
    elif score >= 5:
        conclusion = "⚠️ 中等 - 存在需要修正的问题，建议改进"
    elif score >= 3:
        conclusion = "❌ 较差 - 存在较多问题，需要重点修改"
    elif score >= 1:
        conclusion = "❌ 严重 - 存在严重违规问题，可能需要重新生成"
    else:
        conclusion = "❌ 完全不合格 - 必须重新生成"
    
    # Display results
    print(f"\n📊 审计结果:")
    print(f"质量评分: {score}/10")
    print(f"最终结论: {conclusion}")
    
    if violations:
        print(f"\n🔍 发现问题:")
        for i, violation in enumerate(violations, 1):
            print(f"{i}. {violation['type']}: {violation['description']} ({violation['severity']})")
    else:
        print("\n✅ 未发现问题，质量良好")
    
    # Generate audit report
    audit_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%S')
    report_content = f"""# US-Iran Digest 质量审计报告

## 基本信息

- **审计时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
- **目标文件**: {target_file}
- **总体结果**: {conclusion}

## 详细违规分析

"""
    
    if violations:
        for violation in violations:
            report_content += f"- **{violation['type']}**: {violation['description']} ({violation['severity']})\n"
    else:
        report_content += "未发现问题\n"
    
    report_content += f"""
## 质量评分

**最终评分**: {score}/10

## 最终结论

{conclusion}

---
*审计完成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
    
    # Save audit report
    report_file = f"/root/.openclaw/workspace/usiran-digest/digest-quality-audit-{audit_time}.md"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n✅ 审计报告已保存: {report_file}")
        
        # Commit to Git
        try:
            subprocess.run(['git', 'add', report_file], cwd='/root/.openclaw/workspace/usiran-digest', check=True)
            subprocess.run(['git', 'commit', '-m', 'Add digest quality audit for 2026-04-29T16', '--author', 'US-Iran Digest Auditor <auditor@example.com>'], cwd='/root/.openclaw/workspace/usiran-digest', check=True)
            subprocess.run(['git', 'push'], cwd='/root/.openclaw/workspace/usiran-digest', check=True)
            print("✅ 已推送到GitHub")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 保存审计报告失败: {e}")
        return False

if __name__ == "__main__":
    main()