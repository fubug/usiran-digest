#!/usr/bin/env python3
import os
import json
import yaml

def extract_frontmatter(content):
    """Extract frontmatter from markdown content"""
    if not content.startswith('---'):
        return None
    
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = True
    
    for line in lines:
        if line.strip() == '---':
            if in_frontmatter:
                in_frontmatter = False
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)
    
    if frontmatter_lines:
        return '\n'.join(frontmatter_lines)
    return None

def fix_titles_in_index():
    digest_dir = "/root/.openclaw/workspace/usiran-digest/data/digest"
    index_file = os.path.join(digest_dir, "index.json")
    
    # Read current index
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    # Update titles for each file
    for file_entry in index_data['files']:
        filename = file_entry['file']
        filepath = os.path.join(digest_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple text extraction for titles
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'title:' in line:
                    # Look for zh title in next few lines
                    for j in range(i+1, min(i+5, len(lines))):
                        if 'zh:' in lines[j]:
                            # Extract title between quotes
                            import re
                            match = re.search(r'zh:\s*"([^"]*)"', lines[j])
                            if match:
                                file_entry['title']['zh'] = match.group(1).strip()
                        
                        if 'en:' in lines[j]:
                            # Extract title between quotes
                            import re
                            match = re.search(r'en:\s*"([^"]*)"', lines[j])
                            if match:
                                file_entry['title']['en'] = match.group(1).strip()
                    break
            
            print(f"Fixed {filename}: {file_entry['title']['zh']}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Write updated index
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {len(index_data['files'])} file titles")

if __name__ == "__main__":
    fix_titles_in_index()