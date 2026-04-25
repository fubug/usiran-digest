#!/usr/bin/env python3
import json
import os
from pathlib import Path

# 读取当前索引文件
index_path = "data/digest/index.json"
with open(index_path, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

print(f"Original files count: {len(index_data['files'])}")

# 获取所有实际的 digest 文件
digest_dir = "data/digest"
actual_files = set()
for file in Path(digest_dir).glob("*.md"):
    if file.name != "index.json":
        actual_files.add(file.name)

print(f"Actual files count: {len(actual_files)}")

# 创建一个只包含实际存在的文件的干净索引
cleaned_files = []
seen_files = set()

for item in index_data['files']:
    file_name = item['file']
    if file_name in actual_files and file_name not in seen_files:
        cleaned_files.append(item)
        seen_files.add(file_name)
    else:
        print(f"Skipping missing or duplicate file: {file_name}")

print(f"Cleaned files count: {len(cleaned_files)}")

# 更新索引数据
index_data['files'] = cleaned_files
index_data['updated'] = "2026-04-25T13:00:00+08:00"

# 写回文件
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print("Index file has been manually fixed.")