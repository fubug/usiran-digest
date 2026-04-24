import json
import os
import re

def extract_simple_yaml(content):
    """Simple extraction of YAML frontmatter for basic fields"""
    if not content.startswith('---'):
        return None
    
    lines = content.split('\n')
    frontmatter = {}
    
    for line in lines[1:]:  # Skip first ---
        if line.strip() == '---':
            break
            
        # Handle title field specially
        if line.strip().startswith('title:'):
            # Extract the nested title structure
            title_lines = []
            remaining_lines = []
            found_title = False
            
            for i, remaining_line in enumerate(lines[1:]):
                if remaining_line.strip().startswith('title:'):
                    found_title = True
                    title_lines.append(remaining_line)
                elif found_title and remaining_line.strip().startswith(('zh:', 'en:')):
                    title_lines.append(remaining_line)
                elif found_title and (remaining_line.startswith(' ') or remaining_line.startswith('\t')):
                    title_lines.append(remaining_line)
                elif found_title and not remaining_line.startswith(' ') and not remaining_line.startswith('\t'):
                    remaining_lines = [remaining_line] + lines[1+i:]
                    break
                elif not remaining_line.startswith(' ') and not remaining_line.startswith('\t') and remaining_line.strip():
                    remaining_lines = [remaining_line] + lines[1+i:]
                    break
            
            # Parse title
            title_dict = {}
            title_text = '\n'.join(title_lines)
            zh_match = re.search(r'zh:\s*"([^"]*)"', title_text)
            en_match = re.search(r'en:\s*"([^"]*)"', title_text)
            
            if zh_match:
                title_dict['zh'] = zh_match.group(1)
            if en_match:
                title_dict['en'] = en_match.group(1)
            
            frontmatter['title'] = title_dict if title_dict else {}
            
        # Handle tags
        elif line.strip().startswith('tags:'):
            if '[' in line:
                # Extract tags from list format
                tags = re.findall(r'"([^"]*)"', line)
                frontmatter['tags'] = tags
            else:
                # Single tag
                tag = line.split(':', 1)[1].strip().strip('"')
                frontmatter['tags'] = [tag] if tag else []
                
        # Handle simple fields
        elif ':' in line and not line.startswith(' '):
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"')
    
    return frontmatter if frontmatter else None

# Path to digest directory
digest_dir = '/root/.openclaw/workspace/usiran-digest/data/digest'

# Get actual files from disk
actual_files = []
for filename in os.listdir(digest_dir):
    if filename.endswith('.md') and filename != 'index.json':
        file_path = os.path.join(digest_dir, filename)
        
        # Read file to extract frontmatter
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter with simple parser
            frontmatter = extract_simple_yaml(content)
            
            if frontmatter:
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
                    
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            # If file reading fails, skip this file
            pass

# Create new index
index_data = {
    "updated": "2026-04-24T15:00:00+08:00",
    "files": actual_files
}

# Write back to index.json
with open(os.path.join(digest_dir, 'index.json'), 'w', encoding='utf-8') as f:
    json.dump(index_data, f, ensure_ascii=False, indent=2)

print(f"Repaired index.json with {len(actual_files)} valid entries")
print("Files included:")
for entry in actual_files:
    print(f"  - {entry['id']}: {entry['file']} (title: {entry['title']})")