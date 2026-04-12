import os
import json
import re
from datetime import datetime

# Get all digest files
digest_dir = './data/digest'
files = []

for filename in os.listdir(digest_dir):
    if filename.endswith('.md'):
        filepath = os.path.join(digest_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract frontmatter
        frontmatter_match = re.match(r'^---\s*\n([\s\S]*?)\n---\s*\n', content)
        if not frontmatter_match:
            print(f"⚠️ No frontmatter in {filename}")
            continue
        
        frontmatter = frontmatter_match.group(1)
        data = {'id': '', 'date': '', 'tags': [], 'sources': [], 'title': {'zh': '', 'en': ''}}
        
        for line in frontmatter.split('\n'):
            line = line.strip()
            if line.startswith('id:'):
                data['id'] = line.split(':')[1].strip().replace('"', '')
            elif line.startswith('date:'):
                data['date'] = line.split(':')[1].strip().replace('"', '')
            elif line.startswith('tags:'):
                tags = line.split(':')[1].strip()
                data['tags'] = json.loads(tags.replace("'", '"'))
            elif line.startswith('sources:'):
                sources = line.split(':')[1].strip()
                data['sources'] = json.loads(sources.replace("'", '"'))
            elif line.startswith('title:'):
                title = line.split(':')[1].strip()
                data['title'] = json.loads(title.replace("'", '"'))
        
        entry = {
            'id': data['id'],
            'date': data['date'],
            'file': filename,
            'title': data['title'],
            'tags': data['tags'],
            'sources_count': len(data['sources'])
        }
        files.append(entry)

# Sort by date descending
files.sort(key=lambda x: x['date'], reverse=True)

# Generate index
index = {
    'updated': datetime.now().isoformat().replace('Z', '+08:00'),
    'files': files
}

print(f"Generated index with {len(files)} files:")
for f in files:
    print(f"  {f['id']} - {f['file']}")

# Write index
with open('./data/digest/index.json', 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)