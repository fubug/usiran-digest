#!/usr/bin/env python3
import json
import os
from datetime import datetime

def fix_index():
    # Read current index
    with open('data/digest/index.json', 'r') as f:
        index = json.load(f)
    
    # Get all actual digest files
    digest_files = [f for f in os.listdir('data/digest') if f.endswith('.md') and f != 'index.json']
    
    # Create file entries for all digest files
    file_entries = []
    
    for filename in sorted(digest_files):
        file_id = filename.replace('.md', '')
        
        # Try to read the digest file to extract title
        title_zh = f"美伊局势动态 - {file_id}"
        title_en = f"US-Iran Developments - {file_id}"
        tags = []
        
        try:
            with open(f'data/digest/{filename}', 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract title from frontmatter
                if '---' in content:
                    parts = content.split('---')
                    if len(parts) >= 2:
                        frontmatter = parts[1]
                        if 'title:' in frontmatter:
                            import re
                            title_match = re.search(r'title:\s*\n\s*zh:\s*"([^"]+)"', frontmatter)
                            if title_match:
                                title_zh = title_match.group(1)
                            title_match = re.search(r'title:\s*\n\s*en:\s*"([^"]+)"', frontmatter)
                            if title_match:
                                title_en = title_match.group(1)
                            
                            # Extract tags
                            tags_match = re.search(r'tags:\s*\n\s*-([^\n]+)', frontmatter)
                            if tags_match:
                                tags = [tag.strip().strip('"').strip('-') for tag in tags_match.group(1).split('\n') if tag.strip()]
        except Exception as e:
            print(f"Error reading {filename}: {e}")
        
        file_entry = {
            "id": file_id,
            "file": filename,
            "date": f"{file_id}:00+08:00",
            "title": {
                "zh": title_zh,
                "en": title_en
            },
            "tags": tags
        }
        file_entries.append(file_entry)
    
    # Sort by date (newest first)
    file_entries.sort(key=lambda x: x['id'], reverse=True)
    
    # Update index
    index['files'] = file_entries
    index['updated'] = datetime.now().strftime("%Y-%m-%dT%H:%00:00+08:00")
    
    # Write back
    with open('data/digest/index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"Fixed index: {len(file_entries)} files now included")

if __name__ == "__main__":
    fix_index()