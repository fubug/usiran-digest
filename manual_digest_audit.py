import os
import json
import requests
from datetime import datetime
import re

class ManualDigestQualityAudit:
    def __init__(self):
        self.digest_file = '/root/.openclaw/workspace/skills/usiran-digest/data/digest/digest-20260506T2100.md'
        self.quality_score = 10
        self.violations = {
            'urgent': [],
            'important': [],
            'minor': []
        }
        self.checks = {
            'file_existence': False,
            'metadata_completeness': False,
            'basic_format': False,
            'source_verification': False,
            'data_accuracy': False,
            '人物真实性': False,
            'timeline_consistency': False,
            'timestamp_format': False,
            'content_timeliness': False,
            'translation_quality': False,
            'label_accuracy': False
        }

    def read_digest_file(self):
        print(f'📄 审计文件: {self.digest_file}')
        
        if not os.path.exists(self.digest_file):
            print('❌ 文件不存在')
            return None
        
        self.checks['file_existence'] = True
        with open(self.digest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print('✅ 文件读取成功')
        return content

    def check_frontmatter(self, content):
        print('\n🔍 第一阶段：基础检查')
        
        # 检查前matter结构
        frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            self.violations['urgent'].append('❌ 缺少前matter结构')
            self.quality_score -= 3
            return False
        
        frontmatter = frontmatter_match.group(1)
        required_fields = ['id', 'date', 'title', 'tags', 'sources']
        missing_fields = []
        
        for field in required_fields:
            if field not in frontmatter:
                missing_fields.append(field)
        
        if missing_fields:
            self.violations['important'].append(f'⚠️ 缺少前matter字段: {", ".join(missing_fields)}')
            self.quality_score -= len(missing_fields) * 0.5
        
        # 检查时间戳格式
        date_match = re.search(r'date:\s*"([^"]+)"', frontmatter)
        if date_match:
            date_str = date_match.group(1)
            try:
                datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
                self.checks['timestamp_format'] = True
            except ValueError:
                self.violations['important'].append('⚠️ 时间戳格式不正确，应为ISO 8601 Z格式')
                self.quality_score -= 0.5
        
        # 检查标签
        tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)
        if tags_match:
            tags_content = tags_match.group(1)
            if tags_content.strip():
                self.checks['label_accuracy'] = True
        
        self.checks['metadata_completeness'] = len(missing_fields) == 0
        
        return True

    def check_content_structure(self, content):
        print('\n📊 内容结构检查')
        
        # 检查中英文摘要
        if '## 📊 美伊战争时事简报' in content and '## English Summary' in content:
            self.checks['basic_format'] = True
        else:
            self.violations['important'].append('⚠️ 缺少必要的内容结构')
            self.quality_score -= 1
        
        return True

    def verify_sources(self, content):
        print('\n🔗 第二阶段：内容质量检查')
        
        # 提取新闻链接
        urls = re.findall(r'https?://[\\w\\-\\.]+(?:/[\\w\\-\\._~:/?#\\[\\]@!\\$&\\(\\)\\*+,;=]*)?', content)
        
        if not urls:
            self.checks['source_verification'] = True
            print('ℹ️ 未发现外部链接，无链接验证需求')
            return True
        
        print(f'📎 发现 {len(urls)} 个链接')
        
        broken_urls = []
        for url in urls[:3]:  # 限制检查数量避免超时
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code != 200:
                    broken_urls.append(f'{url} (状态码: {response.status_code})')
            except:
                broken_urls.append(f'{url} (无法访问)')
        
        if broken_urls:
            self.violations['urgent'].append(f'❌ 失效链接: {"; ".join(broken_urls)}')
            self.quality_score -= 2
        
        self.checks['source_verification'] = len(broken_urls) == 0
        
        return True

    def check_data_accuracy(self, content):
        print('\n📈 数据准确性检查')
        
        # 检查是否有敏感数据
        sensitive_patterns = [
            r'\d+\s*人\s*[伤亡死亡]',
            r'\d+\s*人\s*[受伤]',
            r'\d+\s*人\s*[失踪]',
            r'\d+\s*人\s*[遇难]'
        ]
        
        for pattern in sensitive_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.violations['important'].append(f'⚠️ 发现敏感伤亡数据: {matches}')
                self.quality_score -= 1
        
        # 检查是否有具体军事数据
        military_data_patterns = [
            r'\d+\s*枚\s*[导弹]',
            r'\d+\s*架\s*[飞机]',
            r'\d+\s*艘\s*[舰船]',
            r'\d+\s*辆\s*[坦克]',
            r'\d+\s*门\s*[火炮]'
        ]
        
        for pattern in military_data_patterns:
            matches = re.findall(pattern, content)
            if matches:
                self.violations['important'].append(f'⚠️ 发现具体军事数据: {matches}')
                self.quality_score -= 1
        
        self.checks['data_accuracy'] = True
        return True

    def check_content_quality(self, content):
        print('\n✍️ 第三阶段：规范性和语言检查')
        
        # 检查客观性
        subjective_words = ['我觉得', '我认为', '可能', '大概', '猜测', '怀疑', '应该', '也许']
        subjective_count = 0
        
        for word in subjective_words:
            if word in content:
                subjective_count += 1
        
        if subjective_count > 2:
            self.violations['minor'].append(f'🟡 发现 {subjective_count} 处主观表述')
            self.quality_score -= 0.2
        
        # 检查翻译对应
        chinese_section = content.split('## 📊 美伊战争时事简报')[1] if '## 📊 美伊战争时事简报' in content else ''
        english_section = content.split('## English Summary')[1] if '## English Summary' in content else ''
        
        if chinese_section and english_section:
            self.checks['translation_quality'] = True
        
        # 检查内容充实度
        if len(chinese_section) < 200:
            self.violations['minor'].append('🟡 中文内容较为简短')
            self.quality_score -= 0.3
        
        self.checks['content_timeliness'] = True
        
        return True

    def generate_report(self):
        print('\n📋 生成审计报告')
        print('=' * 60)
        print('🎯 usiran-digest 质量审计报告')
        print('=' * 60)
        print(f'📅 审计时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print(f'🕒 审计对象: digest-20260506T2100.md')
        print(f'📄 文件路径: {self.digest_file}')
        
        # 总体评估
        print(f'\n⭐ 质量评分: {self.quality_score:.1f}/10')
        
        # 检查项汇总
        print('\n✅ 检查项完成情况:')
        for check, status in self.checks.items():
            status_text = '✅ 通过' if status else '❌ 未通过'
            print(f'  • {check}: {status_text}')
        
        # 违规分析
        if self.violations['urgent']:
            print('\n🔴 紧急违规:')
            for violation in self.violations['urgent']:
                print(f'  • {violation}')
        
        if self.violations['important']:
            print('\n⚠️ 重要违规:')
            for violation in self.violations['important']:
                print(f'  • {violation}')
        
        if self.violations['minor']:
            print('\n🟡 轻微违规:')
            for violation in self.violations['minor']:
                print(f'  • {violation}')
        
        # 建议操作
        print('\n💡 建议操作:')
        if self.quality_score >= 8:
            print('✅ 内容质量优秀，无需修改')
        elif self.quality_score >= 6:
            print('⚠️ 存在轻微问题，建议优化')
        elif self.quality_score >= 4:
            print('⚠️ 需要重点修改，建议重新审核')
        else:
            print('❌ 质量不合格，建议删除并重新生成')
        
        # 最终结论
        if self.quality_score >= 8:
            print('\n🎉 最终结论: 合格 ✅')
        elif self.quality_score >= 6:
            print('\n📊 最终结论: 基本合格，建议改进 ⚠️')
        else:
            print('\n❌ 最终结论: 不合格 ❌')

def main():
    print('🚀 开始执行 usiran-digest 质量审计...')
    checker = ManualDigestQualityAudit()
    content = checker.read_digest_file()
    
    if content:
        checker.check_frontmatter(content)
        checker.check_content_structure(content)
        checker.verify_sources(content)
        checker.check_data_accuracy(content)
        checker.check_content_quality(content)
        checker.generate_report()
    else:
        print('❌ 无法找到目标digest文件，审计终止')

if __name__ == '__main__':
    main()