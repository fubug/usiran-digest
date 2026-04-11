#!/usr/bin/env python3
import json
import os

# Read current index.json
with open('data/digest/index.json', 'r', encoding='utf-8') as f:
    index = json.load(f)

# Check if T23 already exists (shouldn't be there based on audit)
t23_exists = any(entry['id'] == '2026-04-11T23' for entry in index['files'])

if not t23_exists:
    # Add T23 entry based on the digest file content
    t23_entry = {
        "id": "2026-04-11T23",
        "file": "2026-04-11T23.md",
        "date": "2026-04-11T23:00:00+08:00",
        "title": {
            "zh": "美伊直接谈判启动：历史性会晤，以黎谈判确定下周",
            "en": "Historic US-Iran Direct Talks Begin: Lebanon-Israel Talks Set for Next Week"
        },
        "tags": ["diplomacy", "military"]
    }
    
    index['files'].append(t23_entry)
    index['total_files'] = len(index['files'])
    index['generated_at'] = "2026-04-11T23:10:00+08:00"
    
    # Write back
    with open('data/digest/index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print("✅ Added T23 entry to index.json")
else:
    print("⚠️ T23 entry already exists in index.json")