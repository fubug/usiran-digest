#!/usr/bin/env python3

import sys
import os

# Add the skills directory to path
sys.path.append('/root/.openclaw/workspace/skills/usiran-digest-check')

try:
    from audit_digest import DigestAuditor
    
    # Create auditor for the digest file
    auditor = DigestAuditor()
    
    # Run audit on the generated digest
    target_file = '/root/.openclaw/workspace/data/digest/digest-2026-04-30T08.md'
    auditor.digest_file_path = target_file
    
    print(f"🔍 开始审计: {target_file}")
    
    # Perform audit
    results = auditor.generate_audit_report()
    
    if results:
        print(f"\n📊 审计结果:")
        print(f"质量评分: {results['quality_score']}/10")
        print(f"最终结论: {results['final_conclusion']}")
        print(f"合规状态: {results['compliance_status']}")
        
        print(f"\n📝 检查摘要:")
        print(f"✅ 通过检查: {len(results['passed_checks'])}项")
        print(f"❌ 失败检查: {len(results['failed_checks'])}项")
        print(f"⚠️  风险项: {len(results['risk_items'])}项")
        
        if results['violations']['urgent']:
            print(f"\n🔴 紧急违规: {len(results['violations']['urgent'])}项")
            for violation in results['violations']['urgent']:
                print(f"  - {violation['type']}: {violation['description']}")
        
        if results['violations']['important']:
            print(f"\n⚠️ 重要违规: {len(results['violations']['important'])}项")
            for violation in results['violations']['important']:
                print(f"  - {violation['type']}: {violation['description']}")
        
        if results['violations']['minor']:
            print(f"\n🟡 轻微违规: {len(results['violations']['minor'])}项")
            for violation in results['violations']['minor']:
                print(f"  - {violation['type']}: {violation['description']}")
        
        print(f"\n✅ 审计完成")
        return 0
    else:
        print("❌ 审计失败")
        return 1

except ImportError as e:
    print(f"导入错误: {e}")
    return 1
except Exception as e:
    print(f"运行错误: {e}")
    return 1