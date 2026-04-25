#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path

# 读取当前索引文件
index_path = "data/digest/index.json"
with open(index_path, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

print(f"Original files count: {len(index_data['files'])}")

# 检查并修复标题长度 < 10 的条目
fixed_count = 0
for i, item in enumerate(index_data['files']):
    title_zh = item.get('title', {}).get('zh', '')
    title_en = item.get('title', {}).get('en', '')
    
    # 如果标题为空或长度 < 10
    if len(title_zh) < 10 or len(title_en) < 10:
        file_id = item['id']
        file_path = f"data/digest/{file_id}.md"
        
        if os.path.exists(file_path):
            try:
                # 读取对应的 markdown 文件提取标题
                with open(file_path, 'r', encoding='utf-8') as md_file:
                    content = md_file.read()
                    
                    # 提取中文标题（在 --- 分隔符下的 title.zh）
                    zh_match = re.search(r'title:\s*\n\s*zh:\s*["\']([^"\']+)["\']', content)
                    en_match = re.search(r'title:\s*\n\s*en:\s*["\']([^"\']+)["\']', content)
                    
                    if zh_match and en_match:
                        new_title_zh = zh_match.group(1)
                        new_title_en = en_match.group(1)
                        
                        # 更新索引
                        if 'title' not in item:
                            item['title'] = {}
                        item['title']['zh'] = new_title_zh
                        item['title']['en'] = new_title_en
                        
                        fixed_count += 1
                        print(f"Fixed title for {file_id}: zh=\"{new_title_zh[:30]}...\", en=\"{new_title_en[:30]}...\"")
                    else:
                        # 如果文件中找不到标题，设置默认标题
                        if 'title' not in item:
                            item['title'] = {}
                        item['title']['zh'] = f"美伊局势动态 - {file_id}"
                        item['title']['en'] = f"US-Iran Developments - {file_id}"
                        fixed_count += 1
                        print(f"Set default title for {file_id}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

print(f"Fixed {fixed_count} titles")

# 更新时间戳
index_data['updated'] = "2026-04-25T13:00:00+08:00"

# 写回文件
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print("Empty titles have been fixed.")