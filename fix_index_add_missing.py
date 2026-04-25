#!/usr/bin/env python3
import json
import os
from pathlib import Path

# 读取当前索引文件
index_path = "data/digest/index.json"
with open(index_path, 'r', encoding='utf-8') as f:
    index_data = json.load(f)

print(f"Original files count: {len(index_data['files'])}")

# 需要添加的缺失文件
missing_files = [
    "2026-04-08T09",
    "2026-04-25T01", 
    "2026-04-25T02",
    "2026-04-25T04",
    "2026-04-25T05",
    "2026-04-25T07"
]

# 为每个缺失的文件创建索引条目
for file_id in missing_files:
    file_path = f"data/digest/{file_id}.md"
    if os.path.exists(file_path):
        new_entry = {
            "id": file_id,
            "file": f"{file_id}.md",
            "date": f"{file_id}:00+08:00",
            "title": {},
            "tags": []
        }
        index_data['files'].append(new_entry)
        print(f"Added missing file to index: {file_id}")
    else:
        print(f"Warning: File {file_path} does not exist")

print(f"Updated files count: {len(index_data['files'])}")
index_data['updated'] = "2026-04-25T13:00:00+08:00"

# 写回文件
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print("Missing files have been added to index.")