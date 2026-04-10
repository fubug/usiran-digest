#!/usr/bin/env python3

import json
import os
import re

# Read all digest files
digest_files = []
for file in os.listdir('data/digest/'):
    if file.endswith('.md') and file.startswith('2026-04-'):
        file_path = f'data/digest/{file}'
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter manually
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_content = parts[1]
                # Parse simple YAML-like structure
                frontmatter = {}
                for line in fm_content.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        if key == 'id':
                            frontmatter[key] = value.strip('"')
                        elif key == 'date':
                            frontmatter[key] = value.strip('"')
                        elif key == 'tags':
                            if value.startswith('['):
                                # Parse simple array
                                tags = [tag.strip(' "') for tag in value[1:-1].split(',') if tag.strip()]
                                frontmatter[key] = tags
                            else:
                                frontmatter[key] = [value.strip(' "')]
                        elif key == 'title':
                            # Handle title object
                            if value.startswith('{'):
                                # Simple object parsing
                                zh_match = re.search(r'zh:\s*"([^"]*)"', value)
                                en_match = re.search(r'en:\s*"([^"]*)"', value)
                                frontmatter[key] = {
                                    'zh': zh_match.group(1) if zh_match else '',
                                    'en': en_match.group(1) if en_match else ''
                                }
                            else:
                                frontmatter[key] = {'zh': value.strip('"'), 'en': value.strip('"')}
                
                digest_files.append({
                    'id': frontmatter.get('id', file.replace('.md', '')),
                    'file': file,
                    'date': frontmatter.get('date', '2026-04-11T04:00:00+08:00'),
                    'title': frontmatter.get('title', {'zh': f'Generated: {file}', 'en': f'Generated: {file}'}),
                    'tags': frontmatter.get('tags', ['generated'])
                })
            else:
                # Fallback for corrupted frontmatter
                digest_files.append({
                    'id': file.replace('.md', ''),
                    'file': file,
                    'date': '2026-04-11T04:00:00+08:00',
                    'title': {'zh': f'Generated: {file}', 'en': f'Generated: {file}'},
                    'tags': ['generated']
                })

# Sort by date
digest_files.sort(key=lambda x: x['date'], reverse=True)

# Create complete index
index_data = {
    'title': '美伊战争实时局势摘要',
    'description': '基于 CBS/AP/NYT/Independent 等主流媒体的实时战况更新',
    'updated': '2026-04-11T04:10:00+08:00',
    'files': digest_files
}

# Write complete index
with open('data/digest/index.json', 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f'Regenerated index with {len(digest_files)} files')