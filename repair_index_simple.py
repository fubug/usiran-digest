import json
import os

# Path to digest directory
digest_dir = '/root/.openclaw/workspace/usiran-digest/data/digest'

# Get actual files from disk
actual_files = []
for filename in os.listdir(digest_dir):
    if filename.endswith('.md') and filename != 'index.json':
        file_path = os.path.join(digest_dir, filename)
        
        # Read file to extract frontmatter
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract frontmatter
            if content.startswith('---'):
                lines = content.split('\n')
                frontmatter_end = 0
                for i, line in enumerate(lines):
                    if line.strip() == '---' and i > 0:
                        frontmatter_end = i
                        break
                
                if frontmatter_end > 0:
                    frontmatter_str = '\n'.join(lines[1:frontmatter_end])
                    try:
                        # Simple parsing for basic fields
                        frontmatter = {}
                        for line in frontmatter_str.split('\n'):
                            if ':' in line and not line.startswith('#'):
                                key, value = line.split(':', 1)
                                key = key.strip()
                                value = value.strip()
                                
                                # Handle nested structures
                                if key == 'title':
                                    title_dict = {}
                            if 'zh:' in value:
                                title_dict['zh'] = value.split('zh:')[1].strip().strip('"')
                            elif 'en:' in value:
                                title_dict['en'] = value.split('en:')[1].strip().strip('"')
                                frontmatter['title'] = title_dict
                            elif key == 'tags':
                                if value.startswith('['):
                                    tags = [tag.strip().strip('"') for tag in value[1:-1].split(',')]
                                else:
                                    tags = [value.strip().strip('"')]
                                frontmatter[key] = tags
                            else:
                                frontmatter[key] = value.strip().strip('"')
                        
                        # Create index entry
                        entry = {
                            'id': frontmatter.get('id'),
                            'file': filename,
                            'date': frontmatter.get('date'),
                            'title': frontmatter.get('title', {}),
                            'tags': frontmatter.get('tags', [])
                        }
                        
                        # Validate required fields
                        if entry['id'] and entry['file'] and entry['date']:
                            actual_files.append(entry)
                    except:
                        # If parsing fails, skip this file
                        pass
        except:
            # If file reading fails, skip this file
            pass

# Create new index
index_data = {
    "updated": "2026-04-24T15:00:00+08:00",
    "files": actual_files
}

# Write back to index.json
with open(os.path.join(digest_dir, 'index.json'), 'w') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"Repaired index.json with {len(actual_files)} valid entries")
print("Files included:")
for entry in actual_files:
    print(f"  - {entry['id']}: {entry['file']}")