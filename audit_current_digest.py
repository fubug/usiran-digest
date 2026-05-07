#!/usr/bin/env python3
import json
import re
from datetime import datetime, timedelta

def audit_digest():
    digest_file = "data/digest/digest-20260505T2000.md"
    
    # Read digest file
    with open(digest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"=== US-Iran Digest 质量审计 ===")
    print(f"当前时间: {datetime.now().isoformat()}")
    print(f"目标文件: {digest_file}")
    print(f"🔍 开始质量审计...\n")
    
    violations = []
    warnings = []
    
    # Check front matter
    if "id:" not in content:
        violations.append("缺少id字段")
    if "date:" not in content:
        violations.append("缺少date字段")
    if "title:" not in content:
        violations.append("缺少title字段")
    if "tags:" not in content:
        violations.append("缺少tags字段")
    
    # Check content structure
    if "## 📊 美伊战争时事简报" not in content:
        violations.append("缺少中文标题部分")
    if "## English Summary" not in content:
        warnings.append("缺少英文摘要部分")
    if "### 核心发展" not in content:
        warnings.append("缺少核心发展部分")
    if "### 最新动态" not in content:
        warnings.append("缺少最新动态部分")
    
    # Check sources
    if "sources:" not in content:
        warnings.append("缺少sources字段")
    
    # Check timestamp format
    if "2026-05-05T20:00:00Z" not in content:
        warnings.append("时间戳格式可能不正确")
    
    # Check content length
    if len(content) < 500:
        violations.append("内容过短，可能不完整")
    elif len(content) > 2000:
        warnings.append("内容较长，建议精简")
    
    # Generate audit report
    print(f"📊 审计结果:")
    score = 10
    
    if violations:
        print(f"🔴 违规 ({len(violations)}项):")
        for violation in violations:
            print(f"  - {violation}")
            score -= 3
        print()
    
    if warnings:
        print(f"⚠️ 警告 ({len(warnings)}项):")
        for warning in warnings:
            print(f"  - {warning}")
            score -= 1
        print()
    
    if not violations and not warnings:
        print(f"✅ 无违规，内容完整")
    
    print(f"质量评分: {max(0, score)}/10")
    
    if score >= 8:
        print(f"最终结论: ✅ 优秀 - 内容完整，质量良好")
    elif score >= 6:
        print(f"最终结论: ✅ 合格 - 基本满足要求")
    elif score >= 4:
        print(f"最终结论: ⚠️ 一般 - 存在一些问题")
    else:
        print(f"最终结论: ❌ 不合格 - 存在严重问题")
    
    # Save audit report
    audit_time = datetime.now().strftime("%Y%m%dT%H%M%S")
    audit_report = {
        "audit_time": audit_time,
        "target_file": digest_file,
        "score": max(0, score),
        "violations": violations,
        "warnings": warnings,
        "conclusion": "优秀" if score >= 8 else "合格" if score >= 6 else "一般" if score >= 4 else "不合格"
    }
    
    audit_file = f"data/digest/digest-quality-audit-{audit_time}.md"
    with open(audit_file, 'w', encoding='utf-8') as f:
        f.write(f"# Digest Quality Audit Report\n\n")
        f.write(f"**Audit Time**: {audit_time}\n")
        f.write(f"**Target File**: {digest_file}\n")
        f.write(f"**Score**: {max(0, score)}/10\n")
        f.write(f"**Conclusion**: {audit_report['conclusion']}\n\n")
        f.write(f"## Violations ({len(violations)})\n")
        for violation in violations:
            f.write(f"- {violation}\n")
        f.write(f"\n## Warnings ({len(warnings)})\n")
        for warning in warnings:
            f.write(f"- {warning}\n")
    
    print(f"\n✅ 审计报告已保存: {audit_file}")
    
    return audit_report

if __name__ == "__main__":
    audit_digest()