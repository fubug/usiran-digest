#!/usr/bin/env python3
import os
import json
from datetime import datetime
import glob

def build_complete_index():
    # Get all digest files
    digest_dir = "/root/.openclaw/workspace/usiran-digest/data/digest"
    md_files = glob.glob(os.path.join(digest_dir, "*.md"))
    
    # Remove index.json from the list if it exists
    md_files = [f for f in md_files if not f.endswith("index.json")]
    
    # Sort files by name (which includes timestamp)
    md_files.sort()
    
    files_list = []
    
    for md_file in md_files:
        filename = os.path.basename(md_file)
        
        # Extract ID from filename (remove .md extension)
        file_id = filename.replace('.md', '')
        
        # Extract timestamp for date
        try:
            # Parse the timestamp from filename
            dt = datetime.strptime(file_id, "%Y-%m-%dT%H")
            file_date = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        except ValueError:
            # Fallback to current time
            file_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        
        # Read the digest file to extract title
        title_zh = "Missing Title"
        title_en = "Missing Title"
        tags = ["military", "diplomacy"]
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract title from frontmatter
            lines = content.split('\n')
            in_frontmatter = False
            frontmatter_content = []
            
            for line in lines:
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True
                        continue
                    else:
                        break
                if in_frontmatter:
                    frontmatter_content.append(line)
            
            # Parse frontmatter
            if frontmatter_content:
                frontmatter_text = '\n'.join(frontmatter_content)
                try:
                    # Simple YAML-like parsing for titles
                    for line in frontmatter_text.split('\n'):
                        if 'title:' in line:
                            # Extract zh title
                            if 'zh:' in line:
                                zh_part = line.split('zh:')[1].strip()
                                # Remove quotes and clean up
                                title_zh = zh_part.strip('"\'').strip()
                            # Extract en title
                            if 'en:' in line:
                                en_part = line.split('en:')[1].strip()
                                # Remove quotes and clean up
                                title_en = en_part.strip('"\'').strip()
                        elif 'tags:' in line:
                            tags_part = line.split('tags:')[1].strip()
                            # Parse tags (simple array format)
                            if '[' in tags_part and ']' in tags_part:
                                tags_str = tags_part.split('[')[1].split(']')[0]
                                tags = [tag.strip().strip('"\'') for tag in tags_str.split(',') if tag.strip()]
                                # Filter out empty strings
                                tags = [tag for tag in tags if tag]
                except Exception as e:
                    print(f"Error parsing frontmatter in {filename}: {e}")
        
        except Exception as e:
            print(f"Error reading {filename}: {e}")
        
        # Create file entry
        file_entry = {
            "id": file_id,
            "file": filename,
            "date": file_date,
            "title": {
                "zh": title_zh,
                "en": title_en
            },
            "tags": tags
        }
        
        files_list.append(file_entry)
        print(f"Processed {filename}: {title_zh}")
    
    # Sort files by date (most recent first)
    files_list.sort(key=lambda x: x['date'], reverse=True)
    
    # Create complete index
    complete_index = {
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "files": files_list
    }
    
    # Write complete index
    with open(os.path.join(digest_dir, "index.json"), 'w', encoding='utf-8') as f:
        json.dump(complete_index, f, indent=2, ensure_ascii=False)
    
    print(f"\nComplete index rebuilt with {len(files_list)} files")
    return len(files_list)

if __name__ == "__main__":
    file_count = build_complete_index()
    print(f"Total digest files processed: {file_count}")