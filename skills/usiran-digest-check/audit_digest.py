#!/usr/bin/env python3
"""
US-Iran Digest Quality Audit Script
按照SKILL.md标准对digest内容进行质量合规性审计
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
import requests
try:
    import yaml
except ImportError:
    import yaml as yaml

class DigestAuditor:
    def __init__(self, digest_file_path):
        # If no file path provided, use the most recent digest file
        if not digest_file_path:
            current_time = datetime.now(timezone.utc)
            target_hour = (current_time.hour - 1) % 24
            target_date = current_time.strftime('%Y-%m-%d')
            
            # Try multiple possible file names
            possible_files = [
                f"/root/.openclaw/workspace/usiran-digest/data/digest/{target_date}T{target_hour:02d}.md",
                f"/root/.openclaw/workspace/usiran-digest/data/digest/digest-{target_date}T{target_hour:02d}.md",
                f"/root/.openclaw/workspace/data/digest/digest-{target_date}T{target_hour:02d}.md",
                f"/root/.openclaw/workspace/digest-{target_date}T{target_hour:02d}.md"
            ]
            
            for file_path in possible_files:
                if os.path.exists(file_path):
                    digest_file_path = file_path
                    break
            
            if not digest_file_path or not os.path.exists(digest_file_path):
                # Find the most recent digest file
                digest_dir = "/root/.openclaw/workspace/usiran-digest/data/digest/"
                if os.path.exists(digest_dir):
                    files = os.listdir(digest_dir)
                    digest_files = [f for f in files if f.endswith('.md') and '2026-04-29T' in f]
                    if digest_files:
                        # Sort by name to get the most recent
                        digest_files.sort()
                        digest_file_path = os.path.join(digest_dir, digest_files[-1])
        
        self.digest_file_path = digest_file_path
        self.audit_results = {
            "basic_info": {},
            "check_items": {},
            "violations": {"urgent": [], "important": [], "minor": []},
            "quality_score": 10,
            "recommendations": [],
            "final_conclusion": ""
        }
        
    def get_target_hour_file(self):
        """根据当前时间确定要检查的digest文件"""
        current_time = datetime.now(timezone.utc)
        # 获取前一个整点时段的文件
        target_hour = (current_time.hour - 1) % 24
        target_date = current_time.strftime('%Y-%m-%d')
        
        # 尝试多个可能的路径
        possible_paths = [
            f"/root/.openclaw/workspace/usiran-digest/data/digest/digest-{target_date}T{target_hour:02d}.md",
            f"/root/.openclaw/workspace/data/digest/digest-{target_date}T{target_hour:02d}.md",
            f"/root/.openclaw/workspace/digest-{target_date}T{target_hour:02d}.md"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def read_digest_file(self):
        """读取digest文件"""
        try:
            with open(self.digest_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"❌ 无法读取digest文件: {e}")
            return None
    
    def parse_frontmatter(self, content):
        """解析frontmatter"""
        frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return None
        
        try:
            frontmatter_text = frontmatter_match.group(1)
            # 尝试解析YAML
            frontmatter = yaml.safe_load(frontmatter_text)
            return frontmatter
        except Exception as e:
            print(f"❌ Frontmatter解析失败: {e}")
            return None
    
    def check_file_existence(self):
        """文件存在性检查"""
        exists = os.path.exists(self.digest_file_path)
        self.audit_results["basic_info"]["file_exists"] = exists
        
        if not exists:
            self.audit_results["violations"]["urgent"].append({
                "type": "文件不存在",
                "description": f"目标digest文件 {self.digest_file_path} 不存在",
                "severity": "紧急违规"
            })
            self.audit_results["quality_score"] = 0
        else:
            self.audit_results["check_items"]["file_existence"] = "✅ 通过"
        
        return exists
    
    def check_frontmatter_integrity(self, frontmatter):
        """frontmatter完整性检查"""
        required_fields = ['id', 'date', 'title', 'tags', 'sources']
        missing_fields = []
        
        for field in required_fields:
            if field not in frontmatter:
                missing_fields.append(field)
        
        if missing_fields:
            self.audit_results["violations"]["important"].append({
                "type": "Frontmatter不完整",
                "description": f"缺少必需字段: {', '.join(missing_fields)}",
                "severity": "重要违规"
            })
            self.audit_results["quality_score"] -= 2
        else:
            self.audit_results["check_items"]["frontmatter_integrity"] = "✅ 通过"
    
    def check_timestamp_format(self, frontmatter):
        """时间戳格式检查"""
        date_value = frontmatter.get('date')
        if isinstance(date_value, datetime):
            # 如果已经是datetime对象，转换成字符串检查格式
            date_str = date_value.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        else:
            date_str = str(date_value) if date_value else ''
            
        # 检查ISO 8601格式
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\+|\-)\d{2}:\d{2}$|^Z$'
        
        if not re.match(iso_pattern, date_str):
            self.audit_results["violations"]["minor"].append({
                "type": "时间格式错误",
                "description": f"日期格式不正确: {date_str}，应为ISO 8601格式",
                "severity": "轻微违规"
            })
            self.audit_results["quality_score"] -= 1
        else:
            self.audit_results["check_items"]["timestamp_format"] = "✅ 通过"
    
    def check_source_urls(self, frontmatter):
        """信源链接验证"""
        sources = frontmatter.get('sources', [])
        invalid_sources = []
        
        for source in sources:
            url = source.get('url', '')
            if url and url.startswith('http'):
                try:
                    # 简单的HTTP状态码检查
                    response = requests.head(url, timeout=10, allow_redirects=True)
                    if response.status_code != 200:
                        invalid_sources.append({
                            "url": url,
                            "status_code": response.status_code
                        })
                except Exception as e:
                    invalid_sources.append({
                        "url": url,
                        "error": str(e)
                    })
            elif url and url != "Multi-source intelligence streams" and url != "Real-time data streams":
                # 如果不是特殊的数据流标识，则认为是无效链接
                invalid_sources.append({
                    "url": url,
                    "error": "无效的URL格式"
                })
        
        if invalid_sources:
            self.audit_results["violations"]["urgent"].append({
                "type": "无效信源链接",
                "description": f"发现无效链接: {invalid_sources}",
                "severity": "紧急违规"
            })
            self.audit_results["quality_score"] -= 3
        
        self.audit_results["check_items"]["source_urls"] = "✅ 通过" if not invalid_sources else f"❌ 发现 {len(invalid_sources)} 个无效链接"
    
    def check_content_structure(self, content):
        """内容结构检查"""
        # 检查是否有中文摘要和英文摘要
        has_chinese_summary = "中文摘要" in content
        has_english_summary = "English Summary" in content
        
        if not has_chinese_summary:
            self.audit_results["violations"]["important"].append({
                "type": "内容结构不完整",
                "description": "缺少中文摘要部分",
                "severity": "重要违规"
            })
            self.audit_results["quality_score"] -= 2
        
        if not has_english_summary:
            self.audit_results["violations"]["important"].append({
                "type": "内容结构不完整",
                "description": "缺少英文摘要部分",
                "severity": "重要违规"
            })
            self.audit_results["quality_score"] -= 2
        
        if has_chinese_summary and has_english_summary:
            self.audit_results["check_items"]["content_structure"] = "✅ 通过"
    
    def check_data_accuracy(self, content):
        """数据准确性检查"""
        # 检查是否有具体的伤亡数字等敏感数据
        casualty_patterns = [
            r'\d+[\s,]?人死亡',
            r'\d+[\s,]?人受伤',
            r'\d+[\s,]?人伤亡',
            r'死亡[\s,]?\d+',
            r'受伤[\s,]?\d+',
        ]
        
        casualties_found = []
        for pattern in casualty_patterns:
            matches = re.findall(pattern, content)
            if matches:
                casualties_found.extend(matches)
        
        if casualties_found:
            self.audit_results["recommendations"].append(
                "发现伤亡数据引用，建议核实数据来源和准确性"
            )
            self.audit_results["quality_score"] -= 1
    
    def check_objectivity(self, content):
        """客观性检查"""
        subjective_patterns = [
            r'显然',
            r'明显',
            r'毫无疑问',
            r'确实',
            r'实际上',
        ]
        
        subjective_found = []
        for pattern in subjective_patterns:
            matches = re.findall(pattern, content)
            if matches:
                subjective_found.extend(matches)
        
        if subjective_found:
            self.audit_results["violations"]["minor"].append({
                "type": "主观表述",
                "description": f"发现主观表述: {subjective_found}",
                "severity": "轻微违规"
            })
            self.audit_results["quality_score"] -= 0.5
    
    def check_timeliness(self, frontmatter, content):
        """时效性检查"""
        date_value = frontmatter.get('date')
        try:
            if isinstance(date_value, datetime):
                content_date = date_value
            else:
                content_date = datetime.fromisoformat(str(date_value).replace('Z', '+00:00'))
                
            current_date = datetime.now(timezone.utc)
            time_diff = current_date - content_date
            
            # 如果内容超过24小时，标记为时效性问题
            if time_diff.total_seconds() > 86400:
                self.audit_results["violations"]["important"].append({
                    "type": "时效性问题",
                    "description": f"内容时间 {content_date} 距离当前时间超过24小时",
                    "severity": "重要违规"
                })
                self.audit_results["quality_score"] -= 2
            else:
                self.audit_results["check_items"]["timeliness"] = "✅ 通过"
        except Exception as e:
            self.audit_results["violations"]["minor"].append({
                "type": "时间解析错误",
                "description": f"无法解析时间戳: {e}",
                "severity": "轻微违规"
            })
            self.audit_results["quality_score"] -= 1
    
    def generate_final_conclusion(self):
        """生成最终结论"""
        score = self.audit_results["quality_score"]
        
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
        
        self.audit_results["final_conclusion"] = conclusion
        return conclusion
    
    def generate_audit_report(self):
        """生成审计报告"""
        content = self.read_digest_file()
        if not content:
            return None
        
        frontmatter = self.parse_frontmatter(content)
        if not frontmatter:
            return None
        
        # 基础检查
        self.check_file_existence()
        self.check_frontmatter_integrity(frontmatter)
        self.check_timestamp_format(frontmatter)
        self.check_source_urls(frontmatter)
        self.check_content_structure(content)
        self.check_data_accuracy(content)
        self.check_objectivity(content)
        self.check_timeliness(frontmatter, content)
        
        # 生成最终结论
        self.generate_final_conclusion()
        
        return self.audit_results
    
    def save_audit_report(self, results):
        """保存审计报告"""
        current_time = datetime.now(timezone.utc)
        audit_time = current_time.strftime('%Y-%m-%dT%H%M%S')
        
        # 多个可能的保存位置
        possible_paths = [
            f"/root/.openclaw/workspace/usiran-digest/digest-quality-audit-{audit_time}.md",
            f"/root/.openclaw/workspace/digest-quality-audit-{audit_time}.md"
        ]
        
        for path in possible_paths:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.format_audit_report(results))
                print(f"✅ 审计报告已保存: {path}")
                return path
            except Exception as e:
                print(f"保存报告失败: {e}")
                continue
        
        return None
    
    def format_audit_report(self, results):
        """格式化审计报告"""
        report = f"""# US-Iran Digest 质量审计报告

## 基本信息

- **审计时间**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
- **目标文件**: {self.digest_file_path}
- **总体结果**: {results['final_conclusion']}

## 检查项列表

### 基础检查
"""
        
        if "file_existence" in results['check_items']:
            report += f"- 文件存在性: {results['check_items']['file_existence']}\n"
        if "frontmatter_integrity" in results['check_items']:
            report += f"- Frontmatter完整性: {results['check_items']['frontmatter_integrity']}\n"
        if "timestamp_format" in results['check_items']:
            report += f"- 时间戳格式: {results['check_items']['timestamp_format']}\n"
        if "source_urls" in results['check_items']:
            report += f"- 信源链接: {results['check_items']['source_urls']}\n"
        if "content_structure" in results['check_items']:
            report += f"- 内容结构: {results['check_items']['content_structure']}\n"
        if "timeliness" in results['check_items']:
            report += f"- 时效性: {results['check_items']['timeliness']}\n"
        
        report += "\n### 详细违规分析\n"
        
        if results['violations']['urgent']:
            report += "#### 🔴 紧急违规\n"
            for violation in results['violations']['urgent']:
                report += f"- **{violation['type']}**: {violation['description']} ({violation['severity']})\n"
        
        if results['violations']['important']:
            report += "\n#### ⚠️ 重要违规\n"
            for violation in results['violations']['important']:
                report += f"- **{violation['type']}**: {violation['description']} ({violation['severity']})\n"
        
        if results['violations']['minor']:
            report += "\n#### 🟡 轻微违规\n"
            for violation in results['violations']['minor']:
                report += f"- **{violation['type']}**: {violation['description']} ({violation['severity']})\n"
        
        report += f"""
## 质量评分

**最终评分**: {results['quality_score']}/10

## 建议操作

"""
        
        if results['recommendations']:
            for i, rec in enumerate(results['recommendations'], 1):
                report += f"{i}. {rec}\n"
        else:
            report += "当前内容质量良好，无需特别修改建议。\n"
        
        report += f"""
## 最终结论

{results['final_conclusion']}

---
*审计完成时间: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
        
        return report

def main():
    print("=== US-Iran Digest 质量审计 ===")
    
    auditor = DigestAuditor(None)
    target_file = auditor.get_target_hour_file()
    
    if not target_file:
        print("❌ 未找到目标digest文件")
        sys.exit(1)
    
    print(f"📁 目标文件: {target_file}")
    auditor.digest_file_path = target_file
    
    # 执行审计
    print("🔍 开始质量审计...")
    results = auditor.generate_audit_report()
    
    if not results:
        print("❌ 审计失败")
        sys.exit(1)
    
    # 显示审计结果
    print(f"\n📊 审计结果:")
    print(f"质量评分: {results['quality_score']}/10")
    print(f"最终结论: {results['final_conclusion']}")
    
    if results['violations']['urgent']:
        print(f"\n🔴 紧急违规 ({len(results['violations']['urgent'])}项):")
        for violation in results['violations']['urgent']:
            print(f"  - {violation['type']}: {violation['description']}")
    
    if results['violations']['important']:
        print(f"\n⚠️ 重要违规 ({len(results['violations']['important'])}项):")
        for violation in results['violations']['important']:
            print(f"  - {violation['type']}: {violation['description']}")
    
    if results['violations']['minor']:
        print(f"\n🟡 轻微违规 ({len(results['violations']['minor'])}项):")
        for violation in results['violations']['minor']:
            print(f"  - {violation['type']}: {violation['description']}")
    
    # 保存审计报告
    saved_report = auditor.save_audit_report(results)
    
    if saved_report:
        print(f"\n✅ 审计报告已保存: {saved_report}")
        
        # 提交到Git
        try:
            subprocess.run(['git', 'add', saved_report], cwd='/root/.openclaw/workspace/usiran-digest', check=True)
            subprocess.run(['git', 'commit', '-m', f"Add digest quality audit for {target_file}", '--author', "US-Iran Digest Auditor <auditor@example.com>"], 
                          cwd='/root/.openclaw/workspace/usiran-digest', check=True)
            subprocess.run(['git', 'push'], cwd='/root/.openclaw/workspace/usiran-digest', check=True)
            print("✅ 已推送到GitHub")
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {e}")
    else:
        print("❌ 保存审计报告失败")

if __name__ == "__main__":
    main()