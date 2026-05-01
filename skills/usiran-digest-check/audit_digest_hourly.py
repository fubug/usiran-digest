#!/usr/bin/env python3
"""
Hourly digest audit script for US-Iran war developments
Based on the quality standards in SKILL.md
"""

import json
import os
import re
import subprocess
import requests
from datetime import datetime, timezone, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DigestQualityAuditor:
    def __init__(self):
        self.current_time = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))
        # For audit, we check the previous hour's digest
        self.target_hour = (self.current_time.hour - 1) % 24
        self.target_date = self.current_time.strftime('%Y-%m-%d')
        self.digest_file = f"/root/.openclaw/workspace/data/digest/{self.target_date}T{self.target_hour:02d}.md"
        
        # Quality standards
        self.must_comply_items = [
            "信源真实性", "数据准确性", "人物真实性"
        ]
        
        self.format_standards = [
            "时间戳格式", "前matter结构", "内容结构", "标签准确性"
        ]
        
        self.language_quality_items = [
            "客观性", "专业性", "翻译质量", "时效性"
        ]
        
        self.violation_levels = {
            "紧急违规": {
                "score_deduction": 10,
                "severity": "immediate_deletion"
            },
            "重要违规": {
                "score_deduction": 5,
                "severity": "requires_correction"
            },
            "轻微违规": {
                "score_deduction": 2,
                "severity": "needs_improvement"
            }
        }
        
    def get_previous_hour_digest_file(self):
        """获取前一个小时的目标digest文件"""
        # 格式: YYYY-MM-DDTHH.md
        hour_ago = self.current_time - timedelta(hours=1)
        target_hour = hour_ago.hour
        target_date = hour_ago.strftime('%Y-%m-%d')
        
        # 检查不同可能的位置
        possible_paths = [
            f"/root/.openclaw/workspace/data/digest/{target_date}T{target_hour:02d}.md",
            f"/root/.openclaw/workspace/usiran-digest/data/digest/{target_date}T{target_hour:02d}.md",
            f"/root/.openclaw/workspace/usiran-digest/usiran-digest/{target_date}T{target_hour:02d}.md"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found digest file: {path}")
                return path
        
        logger.warning(f"No digest file found for {target_date}T{target_hour:02d}")
        return None
    
    def check_file_existence(self, file_path):
        """第一阶段：基础检查"""
        issues = []
        
        if not os.path.exists(file_path):
            issues.append({
                "level": "紧急违规",
                "category": "文件完整性",
                "description": "Digest文件不存在",
                "severity": "immediate_deletion"
            })
            return False, issues
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 检查文件是否为空
                if len(content.strip()) == 0:
                    issues.append({
                        "level": "紧急违规",
                        "category": "文件完整性",
                        "description": "Digest文件为空",
                        "severity": "immediate_deletion"
                    })
                    return False, issues
                
                # 检查前matter结构
                if not content.startswith('---'):
                    issues.append({
                        "level": "重要违规",
                        "category": "格式规范",
                        "description": "前matter结构缺失",
                        "severity": "requires_correction"
                    })
                
                # 尝试解析YAML前matter
                yaml_end = content.find('---', 3)
                if yaml_end == -1:
                    issues.append({
                        "level": "重要违规",
                        "category": "格式规范",
                        "description": "前matter结束标记缺失",
                        "severity": "requires_correction"
                    })
                else:
                    try:
                        yaml_content = content[3:yaml_end].strip()
                        metadata = yaml.safe_load(yaml_content)
                        
                        # 检查必需字段
                        required_fields = ['id', 'date', 'title', 'tags', 'sources']
                        for field in required_fields:
                            if field not in metadata:
                                issues.append({
                                    "level": "重要违规",
                                    "category": "格式规范",
                                    "description": f"缺少必需字段: {field}",
                                    "severity": "requires_correction"
                                })
                        
                        # 检查时间戳格式
                        if 'date' in metadata:
                            date_str = metadata['date']
                            if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$', date_str):
                                issues.append({
                                    "level": "重要违规",
                                    "category": "格式规范",
                                    "description": f"时间戳格式错误: {date_str}",
                                    "severity": "requires_correction"
                                })
                        
                    except Exception as e:
                        issues.append({
                            "level": "重要违规",
                            "category": "格式规范",
                            "description": f"前matter解析失败: {str(e)}",
                            "severity": "requires_correction"
                        })
                
        except Exception as e:
            issues.append({
                "level": "紧急违规",
                "category": "文件完整性",
                "description": f"文件读取失败: {str(e)}",
                "severity": "immediate_deletion"
            })
        
        return len(issues) == 0, issues
    
    def verify_sources(self, content):
        """第二阶段：信源验证"""
        issues = []
        
        # 查找所有URL
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
                # 如果是网络问题，标记为重要违规而不是紧急违规
                issues.append({
                    "level": "重要违规",
                    "category": "信源真实性",
                    "description": f"链接验证失败（网络问题）: {url} ({str(e)})",
                    "severity": "requires_correction"
                })
        
        return issues
    
    def check_content_accuracy(self, content):
        """检查数据准确性"""
        issues = []
        
        # 检查是否有虚构的数据
        # 查找可能的数据模式：数字+单位，百分比等
        data_patterns = [
            r'\d+%',
            r'\$\d+\.?\d*',
            r'\d+\.\d+',
            r'\d+:\d+',
            r'\d+月\d+日',
            r'\d+时\d+分'
        ]
        
        for pattern in data_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # 这里应该有更复杂的数据验证逻辑
                # 简化版本：检查数据是否合理
                for match in matches:
                    if isinstance(match, str):
                        # 检查百分比是否在合理范围内
                        if '%' in match and (not match.replace('%', '').isdigit() or int(match.replace('%', '')) > 100):
                            issues.append({
                                "level": "重要违规",
                                "category": "数据准确性",
                                "description": f"数据格式异常: {match}",
                                "severity": "requires_correction"
                            })
        
        return issues
    
    def check_objectivity(self, content):
        """检查客观性"""
        issues = []
        
        # 检查主观表述
        subjective_keywords = [
            '显然', '明显', '毫无疑问', '肯定', '必然',
            '应该', '必须', '需要', '建议'
        ]
        
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
        
        return issues
    
    def check_translation_quality(self, content):
        """检查翻译质量"""
        issues = []
        
        # 查找中文和英文部分的分隔
        if 'English Summary' in content:
            chinese_section = content.split('English Summary')[0]
            english_section = content.split('English Summary')[1]
            
            # 检查中英文内容的对应性
            # 这里可以添加更复杂的翻译质量检查
            chinese_word_count = len(chinese_section.split())
            english_word_count = len(english_section.split())
            
            # 理想的翻译比例应该在1:1.5到1:2之间
            if chinese_word_count > 0 and english_word_count > 0:
                ratio = english_word_count / chinese_word_count
                if ratio < 0.8 or ratio > 3:
                    issues.append({
                        "level": "轻微违规",
                        "category": "语言质量",
                        "description": f"中英文内容比例异常 ({chinese_word_count}:{english_word_count})",
                        "severity": "needs_improvement"
                    })
        
        return issues
    
    def calculate_quality_score(self, issues):
        """计算质量评分"""
        total_deduction = 0
        
        for issue in issues:
            level = issue.get("level", "轻微违规")
            if level in self.violation_levels:
                total_deduction += self.violation_levels[level]["score_deduction"]
        
        # 基础分10分
        score = max(0, 10 - total_deduction)
        return score
    
    def generate_audit_report(self, file_path, issues, score):
        """生成审计报告"""
        report = f"""# Digest质量审计报告

## 基本信息
- **审计时间**: {self.current_time.strftime('%Y-%m-%d %H:%M:%S')}
- **目标文件**: {os.path.basename(file_path)}
- **审计时段**: {self.target_date}T{self.target_hour:02d}
- **总体评分**: {score}/10

## 检查结果概览
- **检查项目总数**: {len(self.must_comply_items) + len(self.format_standards) + len(self.language_quality_items)}
- **发现问题总数**: {len(issues)}
- **紧急违规数**: len([i for i in issues if i['level'] == '紧急违规'])
- **重要违规数**: len([i for i in issues if i['level'] == '重要违规'])
- **轻微违规数**: len([i for i in issues if i['level'] == '轻微违规'])

## 详细违规分析

"""
        
        # 按级别分类
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
        
        # 根据评分给出建议
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
        
        return report
    
    def audit_digest(self):
        """执行完整的digest审计"""
        logger.info("Starting hourly digest audit...")
        
        # 获取目标digest文件
        digest_file = self.get_previous_hour_digest_file()
        
        if not digest_file:
            logger.error("No digest file found for audit")
            return None
        
        logger.info(f"Auditing digest file: {digest_file}")
        
        issues = []
        
        # 第一阶段：基础检查
        is_valid, basic_issues = self.check_file_existence(digest_file)
        issues.extend(basic_issues)
        
        if is_valid:
            # 读取文件内容
            try:
                with open(digest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 第二阶段：内容质量检查
                source_issues = self.verify_sources(content)
                issues.extend(source_issues)
                
                data_issues = self.check_content_accuracy(content)
                issues.extend(data_issues)
                
                # 第三阶段：规范性和语言检查
                objectivity_issues = self.check_objectivity(content)
                issues.extend(objectivity_issues)
                
                translation_issues = self.check_translation_quality(content)
                issues.extend(translation_issues)
                
            except Exception as e:
                issues.append({
                    "level": "紧急违规",
                    "category": "文件处理",
                    "description": f"文件处理失败: {str(e)}",
                    "severity": "immediate_deletion"
                })
        
        # 计算质量评分
        score = self.calculate_quality_score(issues)
        
        # 生成审计报告
        report = self.generate_audit_report(digest_file, issues, score)
        
        # 保存审计报告
        report_filename = f"/root/.openclaw/workspace/skills/usiran-digest-check/audit-report-{self.target_date}T{self.target_hour:02d}.md"
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Audit completed. Report saved: {report_filename}")
        logger.info(f"Quality score: {score}/10")
        
        return {
            "file_path": digest_file,
            "score": score,
            "issues_count": len(issues),
            "report_path": report_filename,
            "status": "passed" if score >= 7 else "failed"
        }

def main():
    auditor = DigestQualityAuditor()
    result = auditor.audit_digest()
    
    if result:
        print(f"✅ Audit completed for {result['file_path']}")
        print(f"Quality score: {result['score']}/10")
        print(f"Issues found: {result['issues_count']}")
        print(f"Status: {result['status']}")
        print(f"Report: {result['report_path']}")
    else:
        print("❌ Audit failed - no digest file found")

if __name__ == "__main__":
    import yaml
    main()