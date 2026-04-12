import json
import os
import re
from datetime import datetime

files = [f for f in os.listdir('.') if f.endswith('.md') and f != 'index.json']
files.sort(reverse=True)

index = {
    "updated": "2026-04-13T07:00:00+08:00",
    "files": []
}

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.MULTILINE | re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match[1]
            
            id_match = re.search(r'id:\s*(\S+)', frontmatter)
            date_match = re.search(r'date:\s*(\S+)', frontmatter)
            title_zh_match = re.search(r'zh:\s*"([^"]*)"', frontmatter)
            title_en_match = re.search(r'en:\s*"([^"]*)"', frontmatter)
            tags_match = re.search(r'tags:\s*\n((?:\s+-\s+.*\n)*)', frontmatter)
            
            id_val = id_match.group(1) if id_match else file.replace('.md', '')
            date_val = date_match.group(1) if date_match else None
            title_zh = title_zh_match.group(1) if title_zh_match else "No Chinese Title"
            title_en = title_en_match.group(1) if title_en_match else "No English Title"
            
            tags = []
            if tags_match:
                tags = [line.strip().replace('- ', '') for line in tags_match.group(1).split('\n') if line.strip()]
            
            index["files"].append({
                "id": id_val,
                "file": file,
                "date": date_val,
                "title": {
                    "zh": title_zh,
                    "en": title_en
                },
                "tags": tags
            })
            
    except Exception as e:
        print(f"Error processing {file}: {e}")

with open('index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, indent=2, ensure_ascii=False)

print(f"Built index with {len(index['files'])} files")
