#!/usr/bin/env python3
"""每日信息汇总 - V2EX + Hacker News + 联合早报 + 版本监控"""
import requests
import json
from datetime import datetime
import re
from html import unescape
import os

VERSION_TRACKING_FILE = '/root/.openclaw/workspace/data/version_tracking.json'

def check_version_updates():
    """检查 GitHub 仓库的版本更新和 GLM-5 支持状态"""
    try:
        # 读取版本跟踪文件
        if not os.path.exists(VERSION_TRACKING_FILE):
            return None, None
        
        with open(VERSION_TRACKING_FILE, 'r') as f:
            tracking = json.load(f)
        
        updates = []
        
        # 检查 idea-claude-code-gui
        repo_info = tracking.get('idea-claude-code-gui')
        if repo_info:
            repo_name = repo_info.get('repo')
            current_version = repo_info.get('current_version')
            
            # 获取最新版本
            response = requests.get(f"https://api.github.com/repos/{repo_name}/tags", timeout=10)
            tags = response.json()
            
            if tags and len(tags) > 0:
                latest_version = tags[0].get('name')
                
                # 更新检查时间（不更新当前版本）
                repo_info['last_checked'] = datetime.now().strftime('%Y-%m-%d')
                
                # 添加到更新列表
                has_new = latest_version != current_version
                updates.append({
                    'repo': 'idea-claude-code-gui',
                    'current': current_version,
                    'latest': latest_version,
                    'url': f"https://github.com/{repo_name}/releases/tag/{latest_version}",
                    'status_check': True,
                    'has_new': has_new  # 是否有新版本
                })
        
        # 检查 GLM-5 Lite 套餐支持
        glm_info = tracking.get('glm-5-lite-support')
        if glm_info:
            # 获取页面内容
            response = requests.get("https://docs.bigmodel.cn/cn/coding-plan/overview", timeout=10)
            content = response.text
            
            # 检查是否支持 GLM-5
            supports_glm5 = False
            
            if 'Lite 套餐' in content and 'GLM-5' in content:
                if 'Lite 套餐已支持' in content or 'Lite 套餐均已支持' in content:
                    supports_glm5 = True
                if 'Lite 预计' in content:
                    supports_glm5 = False
            
            current_status = glm_info.get('current_status', '不支持')
            
            # 如果状态改变
            if supports_glm5 and current_status == '不支持':
                updates.append({
                    'repo': 'GLM-5 Lite套餐支持',
                    'current': '不支持',
                    'latest': '已支持！',
                    'url': 'https://docs.bigmodel.cn/cn/coding-plan/overview',
                    'good_news': True
                })
                # 更新状态
                glm_info['current_status'] = '已支持'
                glm_info['notified'] = True
            elif not supports_glm5 and glm_info.get('notified', False):
                # 之前通知过但还没确认，继续提醒
                updates.append({
                    'repo': 'GLM-5 Lite套餐支持',
                    'current': '不支持',
                    'latest': '不支持',
                    'pending': True,
                    'url': 'https://docs.bigmodel.cn/cn/coding-plan/overview'
                })
        
        # 保存更新后的跟踪信息
        if updates:
            with open(VERSION_TRACKING_FILE, 'w') as f:
                json.dump(tracking, f, indent=2)
        
        return updates if updates else None, tracking
        
    except Exception as e:
        print(f"   ❌ 版本检查错误: {e}")
        return None, tracking

def fetch_v2ex_hot():
    """抓取 V2EX 热门"""
    try:
        response = requests.get("https://www.v2ex.com/api/topics/hot.json", timeout=10)
        
        # 检查响应状态和内容
        if response.status_code != 200:
            print(f"   ❌ V2EX HTTP错误: {response.status_code}")
            return []
        
        # 检查响应内容是否为空或非JSON
        if not response.text or response.text.strip() == '':
            print(f"   ❌ V2EX 返回空内容")
            return []
        
        data = response.json()[:5]

        summary = []
        for topic in data:
            title = topic.get('title', 'N/A')
            node = topic.get('node', {}).get('title', '')
            replies = topic.get('replies', 0)
            summary.append(f"【{node}】{title} ({replies}回复)")

        return summary
    except json.JSONDecodeError as e:
        print(f"   ❌ V2EX JSON解析错误: {e}")
        print(f"   响应内容预览: {response.text[:100] if 'response' in locals() and response else 'N/A'}")
        return []
    except Exception as e:
        print(f"   ❌ V2EX 错误: {e}")
        return []

def fetch_hacker_news():
    """抓取 Hacker News"""
    try:
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = response.json()[:5]

        summary = []
        for story_id in story_ids:
            story_response = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=5)
            story = story_response.json()
            title = story.get('title', 'N/A')
            score = story.get('score', 0)
            summary.append(f"{title} ({score}⭐)")

        return summary
    except Exception as e:
        print(f"   ❌ Hacker News 错误: {e}")
        return []

def fetch_zaobao():
    """抓取联合早报"""
    try:
        response = requests.get("https://www.zaobao.com.sg", timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15'
        })

        html = response.text

        patterns = [
            r'<h3[^>]*><a[^>]*>([^<]+)</a></h3>',
            r'<h2[^>]*>([^<]+)</h2>',
        ]

        titles = []
        for pattern in patterns:
            found = re.findall(pattern, html)
            if found:
                titles.extend(found)

        seen = set()
        summary = []
        for title in titles[:5]:
            clean = unescape(title.strip())
            if clean and len(clean) > 10 and clean not in seen:
                seen.add(clean)
                summary.append(clean)

        return summary
    except Exception as e:
        print(f"   ❌ 联合早报错误: {e}")
        return []

def generate_report(v2ex_data, hn_data, zaobao_data, version_updates=None, tracking=None):
    """生成报告"""
    report = []
    report.append("=" * 60)
    report.append("📊 每日信息汇总")
    report.append("=" * 60)
    report.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    # 版本状态
    if version_updates:
        report.append("🔄 版本状态")
        report.append("─" * 60)
        for update in version_updates:
            repo = update.get('repo')
            current = update.get('current')
            latest = update.get('latest')
            url = update.get('url', '')
            
            if update.get('good_news'):
                # GLM-5 支持的好消息
                report.append(f"🎉 {repo}")
                report.append(f"   ✅ {latest}")
                report.append(f"   🔗 {url}")
            elif update.get('status_check'):
                # idea-claude-code-gui 状态检查
                check_date = tracking.get('idea-claude-code-gui', {}).get('last_checked', '') if tracking else ''
                has_new = update.get('has_new', False)
                
                report.append(f"📦 {repo}")
                report.append(f"   当前版本: {current}")
                if has_new:
                    report.append(f"   🆕 新版本: {latest}")
                    report.append(f"   💡 确认后发送: /acknowledge {latest}")
                else:
                    report.append(f"   ✅ 已是最新版")
                if check_date:
                    report.append(f"   检查时间: {check_date}")
                report.append(f"   🔗 {url}")
            elif update.get('pending'):
                # 等待确认
                report.append(f"⏳ {repo}")
                report.append(f"   当前: {current}")
                report.append(f"   🔗 {url}")
            else:
                # 新版本可用
                report.append(f"🆕 {repo}")
                report.append(f"   新版本: {latest} (当前: {current})")
                report.append(f"   🔗 {url}")
        report.append("")

    # V2EX
    if v2ex_data:
        report.append("💬 V2EX 热门 Top 5")
        report.append("─" * 60)
        for i, item in enumerate(v2ex_data, 1):
            report.append(f"{i}. {item}")
        report.append("")

    # Hacker News
    if hn_data:
        report.append("📰 Hacker News Top 5")
        report.append("─" * 60)
        for i, item in enumerate(hn_data, 1):
            report.append(f"{i}. {item}")
        report.append("")

    # 联合早报
    if zaobao_data:
        report.append("🇸🇬 联合早报 Top 5")
        report.append("─" * 60)
        for i, item in enumerate(zaobao_data, 1):
            report.append(f"{i}. {item}")
        report.append("")

    report.append("─" * 60)
    report.append("📈 数据来源: V2EX + Hacker News + 联合早报 + 版本监控")

    return "\n".join(report)

def main():
    """主函数"""
    print("=" * 60)
    print("📊 每日信息汇总")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 抓取数据
    print("💬 抓取 V2EX...")
    v2ex_data = fetch_v2ex_hot()
    print(f"   ✅ 获取 {len(v2ex_data)} 条")

    print("📰 抓取 Hacker News...")
    hn_data = fetch_hacker_news()
    print(f"   ✅ 获取 {len(hn_data)} 条")

    print("🇸🇬 抓取联合早报...")
    zaobao_data = fetch_zaobao()
    print(f"   ✅ 获取 {len(zaobao_data)} 条")

    print("🔍 检查版本状态...")
    version_updates, tracking = check_version_updates()
    if version_updates:
        print(f"   ✅ 检查了 {len(version_updates)} 个项目")
    else:
        print(f"   ✅ 无版本更新")
    print()

    # 生成报告
    report = generate_report(v2ex_data, hn_data, zaobao_data, version_updates, tracking)
    print(report)
    print()

    # 保存到文件
    with open('/tmp/daily_hub_summary.txt', 'w', encoding='utf-8') as f:
        f.write(report)

    print("=" * 60)
    print("✅ 完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
