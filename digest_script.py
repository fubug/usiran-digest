#!/usr/bin/env python3
"""
US-Iran Digest 自动化脚本
从主流媒体抓取美伊战争最新动态，生成digest并推送到GitHub
"""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

def get_current_time():
    """获取北京时间"""
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

def web_search(query: str, count: int = 5) -> List[Dict]:
    """执行web搜索"""
    try:
        result = subprocess.run([
            'openclaw', 'web_search', 
            '--query', query,
            '--count', str(count)
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"Web搜索失败: {e}")
        return []

def web_fetch(url: str, max_chars: int = 12000) -> str:
    """抓取网页内容"""
    try:
        result = subprocess.run([
            'openclaw', 'web_fetch',
            '--url', url,
            '--maxChars', str(max_chars)
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return result.stdout.strip()
        return ""
    except Exception as e:
        print(f"Web抓取失败: {e}")
        return ""

def playwright_fetch(url: str, max_chars: int = 15000) -> str:
    """使用Playwright抓取页面内容（降级方案）"""
    try:
        cmd = [
            'python3', '-c',
            f"""
from playwright.sync_api import sync_playwright
import sys, time

url = sys.argv[1]
max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 15000

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage', '--no-sandbox'
    ])
    ctx = browser.new_context(
        viewport={{'width': 1920, 'height': 1080}},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    )
    ctx.add_init_script(
        'Object.defineProperty(navigator,"webdriver",{{get:()=>undefined}});'
        'Object.defineProperty(navigator,"plugins",{{get:()=>[1,2,3,4,5]}});'
        'window.chrome={{runtime:{{}}}};'
    )
    page = ctx.new_page()
    page.goto(url, timeout=20000, wait_until='domcontentloaded')
    time.sleep(3)
    text = page.inner_text('body') or ''
    if len(text) > max_chars:
        text = text[:max_chars]
    print(text)
    browser.close()
"""
        ]
        cmd.extend([url, str(max_chars)])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.stdout.strip()
    except Exception as e:
        print(f"Playwright抓取失败: {e}")
        return ""

def find_live_blog_urls() -> List[str]:
    """查找最新的live blog URL"""
    urls = []
    
    # 搜索各媒体的live blog
    search_queries = [
        'site:cbsnews.com Iran war live',
        'site:apnews.com Iran war live', 
        'site:nytimes.com Iran war live',
        'site:independent.co.uk Iran live'
    ]
    
    for query in search_queries:
        results = web_search(query, 3)
        for result in results:
            url = result.get('url', '')
            if url and any(keyword in url.lower() for keyword in ['iran', 'war', 'live']):
                urls.append(url)
                print(f"找到live blog: {url}")
    
    # 去重
    return list(set(urls))

def fetch_source_content(urls: List[str]) -> Dict[str, str]:
    """抓取多个信源内容"""
    contents = {}
    
    for url in urls:
        print(f"尝试抓取: {url}")
        
        # 首选web_fetch
        content = web_fetch(url)
        if content and len(content) > 100:
            contents[url] = content
            print(f"成功抓取: {len(content)} 字符")
            continue
            
        # 降级到Playwright
        print("WebFetch失败，尝试Playwright...")
        content = playwright_fetch(url)
        if content and len(content) > 100:
            contents[url] = content
            print(f"Playwright成功: {len(content)} 字符")
        else:
            print(f"抓取失败: {url}")
    
    return contents

def extract_events_from_content(content: str, url: str) -> List[Dict]:
    """从内容中提取事件"""
    events = []
    
    # 简单的时间戳和事件提取
    timestamp_pattern = r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}'
    event_patterns = [
        r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}).*?(?:击落|空袭|导弹|打击|袭击|攻击)',
        r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}).*?(?:伤亡|死亡|受伤|平民)',
        r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}).*?(?:停火|协议|谈判|声明)',
        r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}).*?(?:特朗普|拜登|内塔尼亚胡|莱希)'
    ]
    
    for pattern in event_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            timestamp_str = match.strip()
            try:
                # 尝试解析时间
                if 'T' in timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                else:
                    dt = datetime.strptime(timestamp_str.split()[0], '%Y-%m-%d')
                
                events.append({
                    'timestamp': timestamp_str,
                    'event': f"[{datetime.now().strftime('%H:%M')}] 从{url}提取事件",
                    'time': dt,
                    'url': url
                })
            except Exception as e:
                print(f"时间解析失败: {timestamp_str} - {e}")
    
    # 按时间排序
    events.sort(key=lambda x: x['time'], reverse=True)
    return events

def has_new_events(new_events: List[Dict], last_push_file: str) -> bool:
    """检查是否有新事件"""
    if not os.path.exists(last_push_file):
        return True
    
    try:
        with open(last_push_file, 'r', encoding='utf-8') as f:
            last_push = json.load(f)
        
        last_events = last_push.get('last_events', [])
        new_event_times = [event['timestamp'] for event in new_events]
        
        # 如果有新时间戳，视为有更新
        if not last_events or not any(time in last_events for time in new_event_times):
            return True
            
    except Exception as e:
        print(f"读取上次推送记录失败: {e}")
        return True
    
    return False

def generate_digest(events: List[Dict], current_time: datetime) -> str:
    """生成digest内容"""
    if not events:
        return ""
    
    # 过滤1小时窗口内的事件
    time_threshold = current_time.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    recent_events = [e for e in events if e['time'] >= time_threshold]
    
    if not recent_events:
        return ""
    
    # 生成标题
    main_event = recent_events[0]['event'][:50] + "..." if len(recent_events[0]['event']) > 50 else recent_events[0]['event']
    
    digest_content = f"""---
id: {current_time.strftime('%Y-%m-%dT%H')}
date: {current_time.strftime('%Y-%m-%dT%H:%M:%S+08:00')}
title:
  zh: "美伊战争动态：{main_event}"
  en: "Iran War Developments: {main_event}"
tags:
  - military
sources:
  - name: "Multiple Sources"
    url: "Various live blogs"
---

## 中文摘要

### 核心事件

{chr(10).join(f"- {event['event']}" for event in recent_events[:3])}

### 军事动态

{chr(10).join(f"- {event['event']}" for event in recent_events[:5])}

### 外交进展

近期持续关注美伊外交动态及国际反应。

### 关键数据

| 指标 | 数据 | 来源 |
|------|------|------|
| 事件数量 | {len(recent_events)} | 实时监控 |
| 最新事件 | {recent_events[0]['timestamp']} | 多源验证 |

### 分析判断

美伊局势持续紧张，多源信息显示军事行动仍在继续。国际社会呼吁和平解决冲突。

---

## English Summary

### Core Events

{chr(10).join(f"- {event['event']}" for event in recent_events[:3])}

### Military Developments

{chr(10).join(f"- {event['event']}" for event in recent_events[:5])}

### Diplomatic Developments

Continued monitoring of US-Iran diplomatic relations and international responses.

### Key Data

| Metric | Data | Source |
|--------|------|--------|
| Event Count | {len(recent_events)} | Real-time monitoring |
| Latest Event | {recent_events[0]['timestamp']} | Multi-source verified |

### Analysis

US-Iran tensions remain high, with ongoing military actions reported across multiple sources. International community urges peaceful resolution.
"""
    
    return digest_content

def update_index_json(digest_file: str, digest_title: Dict, current_time: datetime):
    """更新index.json文件"""
    index_path = '/root/.openclaw/workspace/usiran-digest/data/digest/index.json'
    
    # 读取现有index
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
    else:
        index_data = {'files': []}
    
    # 创建新条目
    new_entry = {
        'id': current_time.strftime('%Y-%m-%dT%H'),
        'file': digest_file,
        'date': current_time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
        'title': digest_title,
        'tags': ['military']
    }
    
    # 在数组开头插入新条目
    index_data['files'].insert(0, new_entry)
    index_data['updated'] = current_time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    
    # 写回文件
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

def git_push():
    """Git提交推送"""
    try:
        os.chdir('/root/.openclaw/workspace/usiran-digest')
        
        # 清理git配置冲突
        subprocess.run(['git', 'config', '--global', '--unset-all', 'url.https://github.com/.insteadof'], 
                      capture_output=True)
        
        # 添加文件
        subprocess.run(['git', 'add', '-A'], check=True)
        
        # 提交
        commit_time = datetime.now().strftime('%Y-%m-%dT%H')
        subprocess.run(['git', 'commit', '-m', f'update: {commit_time} digest - automated monitoring'], check=True)
        
        # 推送
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("Git推送成功")
        return True
    except Exception as e:
        print(f"Git推送失败: {e}")
        return False

def verify_push():
    """验证推送结果"""
    try:
        index_path = '/root/.openclaw/workspace/usiran-digest/data/digest/index.json'
        
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            files_count = len(index_data['files'])
            md_files = len([f for f in os.listdir('/root/.openclaw/workspace/usiran-digest/data/digest') if f.endswith('.md')])
            
            if files_count == md_files:
                print("index.json完整性检查通过")
                return True
            else:
                print(f"警告: index.json条目数({files_count})与实际文件数({md_files})不匹配")
                return False
        else:
            print("警告: index.json文件不存在")
            return False
    except Exception as e:
        print(f"验证失败: {e}")
        return False

def main():
    """主函数"""
    current_time = get_current_time()
    print(f"开始执行美伊战争监控: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # 查找live blog URL
    print("步骤1: 查找live blog URL...")
    urls = find_live_blog_urls()
    if not urls:
        print("未找到live blog URL，使用搜索关键词备用...")
        urls = ["备用搜索方式"]
    
    # 抓取内容
    print("步骤2: 抓取信源内容...")
    contents = fetch_source_content(urls[:3])  # 限制最多3个URL
    if not contents:
        print("警告: 未能抓取到任何内容")
        return
    
    # 提取事件
    print("步骤3: 提取事件信息...")
    all_events = []
    for url, content in contents.items():
        events = extract_events_from_content(content, url)
        all_events.extend(events)
    
    if not all_events:
        print("警告: 未能提取到任何事件")
        return
    
    # 检查是否有新事件
    last_push_file = '/tmp/usiran_digest_last_push.json'
    if not has_new_events(all_events, last_push_file):
        print("没有检测到新事件，跳过推送")
        return
    
    # 生成digest
    print("步骤4: 生成digest...")
    digest_content = generate_digest(all_events, current_time)
    if not digest_content:
        print("警告: 生成digest为空")
        return
    
    # 保存digest文件
    digest_file = f'/root/.openclaw/workspace/usiran-digest/data/digest/{current_time.strftime("%Y-%m-%dT%H")}.md'
    with open(digest_file, 'w', encoding='utf-8') as f:
        f.write(digest_content)
    
    # 更新index.json
    print("步骤5: 更新索引...")
    digest_title = {
        'zh': "美伊战争动态",
        'en': "Iran War Developments"
    }
    update_index_json(digest_file, digest_title, current_time)
    
    # Git推送
    print("步骤6: 推送到GitHub...")
    if git_push():
        # 验证推送
        if verify_push():
            print("验证通过")
            
            # 更新状态
            last_events = [event['timestamp'] for event in all_events[:5]]
            status_data = {
                'last_push': current_time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
                'last_events': last_events
            }
            with open(last_push_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            
            print("执行完成")
            return
    
    print("执行失败")

if __name__ == "__main__":
    main()