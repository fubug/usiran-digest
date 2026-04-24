#!/usr/bin/env python3
import json
import os

# Path to digest directory
digest_dir = '/root/.openclaw/workspace/usiran-digest/data/digest'

# Read current index.json
with open(os.path.join(digest_dir, 'index.json'), 'r') as f:
    index_data = json.load(f)

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
                        import yaml
                        frontmatter = yaml.safe_load(frontmatter_str)
                        
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
                        # If YAML parsing fails, skip this file
                        pass
        except:
            # If file reading fails, skip this file
            pass

# Update index_data with only existing files
index_data['files'] = actual_files

# Write back to index.json
with open(os.path.join(digest_dir, 'index.json'), 'w') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"Repaired index.json with {len(actual_files)} valid entries")
print("Files included:")
for entry in actual_files:
    print(f"  - {entry['id']}: {entry['file']}")