#!/usr/bin/env python3
import json

# Read the current index.json
with open('data/digest/index.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get existing files for today
import os
existing_files = set()
digest_dir = 'data/digest'
for filename in os.listdir(digest_dir):
    if filename.startswith('2026-04-24') and filename.endswith('.md'):
        existing_files.add(filename)

# Remove entries that don't correspond to existing files
filtered_files = []
for entry in data['files']:
    file_name = entry['file']
    if file_name in existing_files:
        filtered_files.append(entry)
    elif not file_name.startswith('2026-04-24'):
        # Keep entries from other dates
        filtered_files.append(entry)

# Update the data
data['files'] = filtered_files
data['updated'] = "2026-04-24T09:10:00+08:00"

# Write back
with open('data/digest/index.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Index cleaned. Kept {len(filtered_files)} entries, removed {len(data['files']) - len(filtered_files)} orphaned entries.")