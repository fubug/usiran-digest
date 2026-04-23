#!/usr/bin/env python3
import json
import os
from datetime import datetime

def rebuild_index():
    digest_dir = "data/digest"
    index_file = os.path.join(digest_dir, "index.json")
    
    # Get all digest files
    digest_files = []
    for filename in os.listdir(digest_dir):
        if filename.endswith('.md') and filename != 'complete_index.json':
            filepath = os.path.join(digest_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract frontmatter
                import re
                frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
                if frontmatter_match:
                    import yaml
                    frontmatter = yaml.safe_load(frontmatter_match.group(1))
                    
                    if frontmatter:
                        entry = {
                            'id': frontmatter.get('id'),
                            'file': filename,
                            'date': frontmatter.get('date'),
                            'title': frontmatter.get('title', {}),
                            'tags': frontmatter.get('tags', [])
                        }
                        digest_files.append(entry)
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Sort by date
    digest_files.sort(key=lambda x: x['date'])
    
    # Create new index
    new_index = {
        'updated': datetime.now().isoformat() + '+08:00',
        'files': digest_files
    }
    
    # Write updated index
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(new_index, f, ensure_ascii=False, indent=2)
    
    print(f"Index rebuilt with {len(digest_files)} entries")
    return len(digest_files)

if __name__ == "__main__":
    rebuild_index()