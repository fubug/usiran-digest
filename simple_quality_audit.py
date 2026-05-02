#!/usr/bin/env python3
"""
Simple quality audit script for US-Iran digest files
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

def quality_audit_digest(digest_file):
    """对digest文件进行质量审计"""
    print(f"=== 质量审计: {digest_file} ===")
    
    try:
        with open(digest_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 文件读取失败: {e}")
        return None
    
    audit_results = {
        'basic_check': {},
        'content_quality': {},
        'format_compliance': {},
        'language_quality': {},
        'total_score': 0,
        'compliance_rate': 0,
        'violations': []
    }
    
    # 基础检查
    print("\n--- 基础检查 ---")
    
    # 检查文件结构
    has_frontmatter = '---' in content
    has_chinese_section = '中文摘要' in content
    has_english_section = 'English Summary' in content
    has_timestamp = re.search(r'date:\s*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', content)
    has_sources = 'sources:' in content
    
    audit_results['basic_check'] = {
        'frontmatter_complete': has_frontmatter,
        'chinese_section': has_chinese_section,
        'english_section': has_english_section,
        'timestamp_format': bool(has_timestamp),
        'sources_included': has_sources
    }
    
    basic_score = sum(audit_results['basic_check'].values()) / len(audit_results['basic_check']) * 10
    print(f"基础检查得分: {basic_score}/10")
    
    # 内容质量检查
    print("\n--- 内容质量检查 ---")
    
    # 检查内容长度
    chinese_content = re.search(r'## 中文摘要\s*(.*?)(?=##|\Z)', content, re.DOTALL)
    english_content = re.search(r'## English Summary\s*(.*?)(?=##|\Z)', content, re.DOTALL)
    
    has_chinese_content = bool(chinese_content and len(chinese_content.group(1)) > 500)
    has_english_content = bool(english_content and len(english_content.group(1)) > 500)
    has_key_data = '关键数据' in content or 'Key Data' in content
    has_analysis = '分析判断' in content or 'Analysis' in content
    
    audit_results['content_quality'] = {
        'chinese_content_length': has_chinese_content,
        'english_content_length': has_english_content,
        'key_data_included': has_key_data,
        'analysis_included': has_analysis
    }
    
    content_score = sum(audit_results['content_quality'].values()) / len(audit_results['content_quality']) * 10
    print(f"内容质量得分: {content_score}/10")
    
    # 格式合规检查
    print("\n--- 格式合规检查 ---")
    
    # 检查时间戳格式 (简化版)
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', content)
    has_id_field = re.search(r'id:\s*(\d{4}-\d{2}-\d{2}T\d{2})', content)
    has_tags_field = 'tags:' in content
    
    audit_results['format_compliance'] = {
        'timestamp_format': bool(timestamp_match),
        'id_field_present': bool(has_id_field),
        'tags_field_present': has_tags_field
    }
    
    format_score = sum(audit_results['format_compliance'].values()) / len(audit_results['format_compliance']) * 10
    print(f"格式合规得分: {format_score}/10")
    
    # 语言质量检查
    print("\n--- 语言质量检查 ---")
    
    # 检查语言结构
    has_military_terms = '军事' in content or 'military' in content.lower()
    has_diplomatic_terms = '外交' in content or 'diplomatic' in content.lower()
    has_data_table = '|' in content  # 简化的表格检测
    
    audit_results['language_quality'] = {
        'military_terms_present': has_military_terms,
        'diplomatic_terms_present': has_diplomatic_terms,
        'data_structure_present': has_data_table
    }
    
    language_score = sum(audit_results['language_quality'].values()) / len(audit_results['language_quality']) * 10
    print(f"语言质量得分: {language_score}/10")
    
    # 计算总分和合规率
    total_score = (basic_score + content_score + format_score + language_score) / 4
    compliance_rate = sum([
        sum(audit_results['basic_check'].values()),
        sum(audit_results['content_quality'].values()),
        sum(audit_results['format_compliance'].values()),
        sum(audit_results['language_quality'].values())
    ]) / (4 * len(audit_results['basic_check'])) * 100
    
    audit_results['total_score'] = round(total_score, 1)
    audit_results['compliance_rate'] = round(compliance_rate, 1)
    
    # 违规项检测
    violations = []
    if not has_frontmatter:
        violations.append("❌ 缺少前matter结构")
    if not has_chinese_content:
        violations.append("❌ 中文内容不足")
    if not has_english_content:
        violations.append("❌ 英文内容不足")
    if not has_key_data:
        violations.append("❌ 缺少关键数据")
    
    audit_results['violations'] = violations
    
    print(f"\n--- 审计结果 ---")
    print(f"总分: {audit_results['total_score']}/10")
    print(f"合规率: {audit_results['compliance_rate']}%")
    
    if violations:
        print("\n违规项:")
        for violation in violations:
            print(f"  {violation}")
    else:
        print("✅ 无严重违规项")
    
    # 生成质量评级
    if total_score >= 9:
        rating = "A+ (优秀)"
    elif total_score >= 8:
        rating = "A (优秀)"
    elif total_score >= 7:
        rating = "B+ (良好)"
    elif total_score >= 6:
        rating = "B (良好)"
    else:
        rating = "C (需改进)"
    
    print(f"质量评级: {rating}")
    
    return audit_results

def main():
    if len(sys.argv) < 2:
        print("用法: python3 simple_quality_audit.py <digest_file>")
        sys.exit(1)
    
    digest_file = sys.argv[1]
    if not os.path.exists(digest_file):
        print(f"文件不存在: {digest_file}")
        sys.exit(1)
    
    result = quality_audit_digest(digest_file)
    
    if result:
        # 保存审计报告
        audit_file = digest_file.replace('.md', f'-quality-audit-{datetime.now().strftime("%Y%m%dT%H%M%S")}.md')
        
        audit_report = f"""# 质量审计报告 - {digest_file}

## 基本信息
- **审计时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **目标文件**: {digest_file}
- **总体结果**: {'✅ 通过' if result['total_score'] >= 6 else '❌ 需改进'}

## 检查项列表

### 基础检查
- 前matter完整度: {'✅' if result['basic_check']['frontmatter_complete'] else '❌'}
- 中文摘要存在: {'✅' if result['basic_check']['chinese_section'] else '❌'}
- 英文摘要存在: {'✅' if result['basic_check']['english_section'] else '❌'}
- 时间戳格式: {'✅' if result['basic_check']['timestamp_format'] else '❌'}
- 信源信息: {'✅' if result['basic_check']['sources_included'] else '❌'}

### 内容质量
- 中文内容长度: {'✅' if result['content_quality']['chinese_content_length'] else '❌'}
- 英文内容长度: {'✅' if result['content_quality']['english_content_length'] else '❌'}
- 关键数据包含: {'✅' if result['content_quality']['key_data_included'] else '❌'}
- 分析内容包含: {'✅' if result['content_quality']['analysis_included'] else '❌'}

### 格式合规
- 时间戳格式: {'✅' if result['format_compliance']['timestamp_format'] else '❌'}
- ID字段存在: {'✅' if result['format_compliance']['id_field_present'] else '❌'}
- 标签字段存在: {'✅' if result['format_compliance']['tags_field_present'] else '❌'}

### 语言质量
- 军事术语存在: {'✅' if result['language_quality']['military_terms_present'] else '❌'}
- 外交术语存在: {'✅' if result['language_quality']['diplomatic_terms_present'] else '❌'}
- 数据结构存在: {'✅' if result['language_quality']['data_structure_present'] else '❌'}

## 详细违规分析
{''.join(f'- {violation}\\n' for violation in result['violations'])}

## 质量评分
- **总分**: {result['total_score']}/10
- **合规率**: {result['compliance_rate']}%
- **质量评级**: {'A+ (优秀)' if result['total_score'] >= 9 else 'A (优秀)' if result['total_score'] >= 8 else 'B+ (良好)' if result['total_score'] >= 7 else 'B (良好)' if result['total_score'] >= 6 else 'C (需改进)'}

## 建议操作
{'✅ 建议通过，无需重大修改' if result['total_score'] >= 8 else '⚠️ 建议修正，存在中等问题' if result['total_score'] >= 6 else '❌ 建议重点修改，存在较多问题'}

---
**审计工具**: Simple Quality Audit Script
**完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(audit_file, 'w', encoding='utf-8') as f:
            f.write(audit_report)
        
        print(f"\n审计报告已保存: {audit_file}")
        
        # 提交到git
        try:
            os.system(f'git add "{audit_file}"')
            os.system(f'git commit -m "Add quality audit for {os.path.basename(digest_file)}"')
            os.system('git push origin main')
            print("✅ 审计报告已推送到GitHub")
        except Exception as e:
            print(f"❌ Git提交失败: {e}")

if __name__ == "__main__":
    main()