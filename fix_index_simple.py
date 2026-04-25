import json
import os
from pathlib import Path

# 读取当前索引文件
index_path = "/root/.openclaw/workspace/usiran-digest/data/digest/index.json"
with open(index_path, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

# 获取所有实际的 digest 文件
digest_dir = "/root/.openclaw/workspace/usiran-digest/data/digest"
actual_files = set()
for file in Path(digest_dir).glob("*.md"):
    if file.name != "index.json":
        actual_files.add(file.name)

print(f"Total actual files: {len(actual_files)}")

# 检查索引文件中的文件
indexed_files = set()
cleaned_files = []

# 去重处理：保留第一次出现的条目
seen_ids = set()
for item in index_data['files']:
    file_id = item['id']
    if file_id not in seen_ids:
        seen_ids.add(file_id)
        cleaned_files.append(item)
        indexed_files.add(item['file'])
    else:
        print(f"Duplicate entry found and removed: {file_id}")

print(f"Total indexed files after deduplication: {len(cleaned_files)}")

# 修复索引文件
index_data['files'] = cleaned_files
index_data['updated'] = "2026-04-25T13:00:00+08:00"

# 写回文件
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print("Index file has been fixed and deduplicated.")