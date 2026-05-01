#!/usr/bin/env python3
"""
Specific audit script for hour 12 digest
"""

import yaml
import re
import requests
from datetime import datetime, timezone, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def audit_specific_hour(file_path):
    """Audit a specific digest file"""
    
    issues = []
    
    # Read and parse the digest file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check YAML frontmatter
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                yaml_content = content[3:yaml_end].strip()
                try:
                    metadata = yaml.safe_load(yaml_content)
                    
                    # Check required fields
                    required_fields = ['id', 'date', 'title', 'tags', 'sources']
                    for field in required_fields:
                        if field not in metadata:
                            issues.append({
                                "level": "重要违规",
                                "category": "格式规范",
                                "description": f"缺少必需字段: {field}",
                                "severity": "requires_correction"
                            })
                    
                except Exception as e:
                    issues.append({
                        "level": "重要违规",
                        "category": "格式规范",
                        "description": f"前matter解析失败: {str(e)}",
                        "severity": "requires_correction"
                    })
        
        # Verify sources
        urls = re.findall(r'https?://[^\s"\'<>]+', content)
        for url in urls:
            try:
                response = requests.head(url, timeout=10, allow_redirects=True)
                if response.status_code != 200:
                    issues.append({
                        "level": "紧急违规",
                        "category": "信源真实性",
                        "description": f"链接无法访问: {url} (状态码: {response.status_code})",
                        "severity": "immediate_deletion"
                    })
            except requests.exceptions.RequestException as e:
                issues.append({
                    "level": "重要违规",
                    "category": "信源真实性",
                    "description": f"链接验证失败（网络问题）: {url} ({str(e)})",
                    "severity": "requires_correction"
                })
        
        # Check objectivity
        subjective_keywords = ['显然', '明显', '毫无疑问', '肯定', '必然', '应该', '必须', '需要', '建议']
        subjective_count = 0
        for keyword in subjective_keywords:
            count = len(re.findall(keyword, content))
            subjective_count += count
        
        if subjective_count > 5:
            issues.append({
                "level": "轻微违规",
                "category": "语言质量",
                "description": f"主观表述过多 ({subjective_count}处)",
                "severity": "needs_improvement"
            })
        
        # Check translation quality
        if 'English Summary' in content:
            chinese_section = content.split('English Summary')[0]
            english_section = content.split('English Summary')[1]
            
            chinese_word_count = len(chinese_section.split())
            english_word_count = len(english_section.split())
            
            if chinese_word_count > 0 and english_word_count > 0:
                ratio = english_word_count / chinese_word_count
                if ratio < 0.8 or ratio > 3:
                    issues.append({
                        "level": "轻微违规",
                        "category": "语言质量",
                        "description": f"中英文内容比例异常 ({chinese_word_count}:{english_word_count})",
                        "severity": "needs_improvement"
                    })
        
        # Calculate score
        total_deduction = 0
        for issue in issues:
            level = issue.get("level", "轻微违规")
            if level == "紧急违规":
                total_deduction += 10
            elif level == "重要违规":
                total_deduction += 5
            else:
                total_deduction += 2
        
        score = max(0, 10 - total_deduction)
        
        # Generate report
        report = f"""# Digest质量审计报告 - 特殊审计

## 基本信息
- **审计时间**: {datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')}
- **目标文件**: {os.path.basename(file_path)}
- **审计时段**: 2026-05-01T12
- **总体评分**: {score}/10

## 检查结果概览
- **检查项目总数**: 11
- **发现问题总数**: {len(issues)}
- **紧急违规数**: len([i for i in issues if i['level'] == '紧急违规'])
- **重要违规数**: len([i for i in issues if i['level'] == '重要违规'])
- **轻微违规数**: len([i for i in issues if i['level'] == '轻微违规'])

## 详细违规分析

"""
        
        by_level = {}
        for issue in issues:
            level = issue['level']
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(issue)
        
        for level, level_issues in by_level.items():
            report += f"### {level}\n"
            for issue in level_issues:
                report += f"- **{issue['category']}**: {issue['description']}\n"
            report += "\n"
        
        report += f"""## 质量评分说明
- **基础分**: 10分
- **违规扣分**: 
  - 紧急违规: -10分
  - 重要违规: -5分
  - 轻微违规: -2分
- **最终得分**: {score}/10

## 建议操作

"""
        
        if score >= 9:
            report += "✅ **优秀**: 质量优秀，无需修改\n"
        elif score >= 7:
            report += "🟡 **良好**: 存在轻微问题，建议改进\n"
        elif score >= 5:
            report += "🟠 **一般**: 存在较多问题，需要重点修改\n"
        elif score >= 3:
            report += "🔴 **较差**: 问题严重，建议重新审核\n"
        else:
            report += "🚨 **不合格**: 存在严重违规，建议删除\n"
        
        report += f"""
## 最终结论
"""
        
        if score >= 7:
            report += f"✅ **通过**: Digest质量评分{score}/10，符合质量标准\n"
        else:
            report += f"❌ **未通过**: Digest质量评分{score}/10，未达到质量标准\n"
        
        return report, score
        
    except Exception as e:
        return f"审计失败: {str(e)}", 0

if __name__ == "__main__":
    import os
    file_path = "/root/.openclaw/workspace/data/digest/2026-05-01T12.md"
    
    if os.path.exists(file_path):
        report, score = audit_specific_hour(file_path)
        
        # Save report
        report_filename = "/root/.openclaw/workspace/skills/usiran-digest-check/audit-report-2026-05-01T12.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Audit completed for {file_path}")
        print(f"Quality score: {score}/10")
        print(f"Report saved: {report_filename}")
    else:
        print(f"❌ File not found: {file_path}")