#!/usr/bin/env python3
"""
Rebuild index.json with all missing digest entries
"""

import json
import yaml
import os
import glob

def rebuild_index():
    index_file = "data/index.json"
    
    # Read current index
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # Get all digest files
    digest_files = glob.glob("data/digest/2026-04-*.md")
    
    print(f"Found {len(digest_files)} digest files")
    
    # Track existing IDs
    existing_ids = set(entry['id'] for entry in index_data['files'])
    print(f"Existing entries in index: {len(existing_ids)}")
    
    # Process each digest file
    new_entries = []
    for file_path in digest_files:
        filename = os.path.basename(file_path)
        file_id = filename.replace('.md', '')
        
        if file_id in existing_ids:
            print(f"✅ {file_id} already in index")
            continue
        
        print(f"📝 Adding {file_id} to index...")
        
        # Extract frontmatter
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            frontmatter_str = parts[1].strip()
            frontmatter = yaml.safe_load(frontmatter_str)
            
            # Verify ID matches
            if frontmatter['id'] != file_id:
                print(f"❌ ID mismatch: file={file_id}, frontmatter={frontmatter['id']}")
                continue
            
            # Create index entry
            entry = {
                "id": frontmatter['id'],
                "date": frontmatter['date'],
                "title": frontmatter['title'],
                "tags": frontmatter['tags'],
                "file": filename
            }
            
            new_entries.append(entry)
            print(f"   Added: {entry['title']['zh']}")
    
    # Add new entries to index
    index_data['files'].extend(new_entries)
    index_data['total_files'] = len(index_data['files'])
    
    # Sort by date (newest first)
    index_data['files'].sort(key=lambda x: x['date'], reverse=True)
    
    # Write back
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Summary:")
    print(f"Total entries in index: {len(index_data['files'])}")
    print(f"New entries added: {len(new_entries)}")
    
    return len(new_entries)

if __name__ == "__main__":
    rebuild_index()