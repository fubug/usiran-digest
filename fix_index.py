#!/usr/bin/env python3

import json
import re

# Read the backup file
with open('data/digest/index.json.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the JSON by removing the problematic T07 entry
# Find the T07 entry and remove it completely
pattern = r'\s*\{\s*"id": "2026-04-24T07"[^}]*\},?'
content = re.sub(pattern, '', content, flags=re.MULTILINE | re.DOTALL)

# Remove any trailing commas
content = re.sub(r',\s*([\]}])', r'\1', content)

# Parse to validate JSON
try:
    data = json.loads(content)
    print("JSON is now valid!")
    
    # Write the fixed version
    with open('data/digest/index.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("Fixed index.json written successfully")
    
    # Count entries for today
    today_entries = [e for e in data['files'] if e['id'].startswith('2026-04-24')]
    print(f"Entries for today (2026-04-24): {len(today_entries)}")
    
except json.JSONDecodeError as e:
    print(f"Still invalid JSON: {e}")