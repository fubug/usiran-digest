#!/usr/bin/env python3
import os
import json
import re

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

def extract_title_from_frontmatter(frontmatter_content):
    """Extract zh and en titles from frontmatter"""
    title_zh = "Missing Title"
    title_en = "Missing Title"
    
    # Use regex to find title section
    title_match = re.search(r'title:\s*\n\s*zh:\s*"([^"]*)"', frontmatter_content)
    if title_match:
        title_zh = title_match.group(1).strip()
    
    title_match = re.search(r'title:\s*\n\s*en:\s*"([^"]*)"', frontmatter_content)
    if title_match:
        title_en = title_match.group(1).strip()
    
    return title_zh, title_en

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
            
            frontmatter = extract_frontmatter(content)
            if frontmatter:
                title_zh, title_en = extract_title_from_frontmatter(frontmatter)
                file_entry['title']['zh'] = title_zh
                file_entry['title']['en'] = title_en
                print(f"Fixed {filename}: {title_zh}")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
    
    # Write updated index
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {len(index_data['files'])} file titles")

if __name__ == "__main__":
    fix_titles_in_index()