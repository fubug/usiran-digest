#!/usr/bin/env python3
import json
import os
from datetime import datetime

def update_index_json():
    index_file = "data/digest/index.json"
    digest_file = "data/digest/digest-20260505T2000.md"
    
    # Read existing index.json
    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract info from digest file
    with open(digest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse front matter (simplified)
    lines = content.split('\n')
    id_line = None
    date_line = None
    for line in lines:
        if line.startswith('id:'):
            id_line = line.split(':', 1)[1].strip()
        elif line.startswith('date:'):
            date_line = line.split(':', 1)[1].strip()
    
    # Create new entry
    new_entry = {
        "id": id_line or "20260505T2000",
        "file": digest_file,
        "date": date_line or "2026-05-05T20:00:00Z",
        "title": {
            "zh": "美伊战争动态 2026-05-05 20:00",
            "en": "Iran War Digest 2026-05-05 20:00"
        },
        "tags": ["美伊战争", "中东局势", "时事简报", "战争发展"]
    }
    
    # Add to files array at the beginning
    data['files'].insert(0, new_entry)
    data['updated'] = datetime.now().isoformat()
    
    # Write back to file
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Updated index.json with new digest: {new_entry}")

if __name__ == "__main__":
    update_index_json()