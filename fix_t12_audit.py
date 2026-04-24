#!/usr/bin/env python3
"""
Fix T12 digest quality audit issues
1. Add missing T12 entry to index.json
2. Clean up duplicate source URLs
"""

import json
import yaml
import os

def fix_digest_issues():
    # Paths
    digest_file = "data/digest/2026-04-24T12.md"
    index_file = "data/index.json"
    
    # Read digest file to extract metadata
    with open(digest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        frontmatter_str = parts[1].strip()
        body = parts[2].strip()
        
        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(frontmatter_str)
        
        print("=== T12 Digest Metadata ===")
        print(f"ID: {frontmatter['id']}")
        print(f"Date: {frontmatter['date']}")
        print(f"Title.zh: {frontmatter['title']['zh']}")
        print(f"Title.en: {frontmatter['title']['en']}")
        print(f"Tags: {frontmatter['tags']}")
        
        # Clean up duplicate sources
        if len(frontmatter['sources']) > 1:
            urls = [s['url'] for s in frontmatter['sources']]
            if len(set(urls)) < len(urls):
                print("⚠️  Duplicate source URLs detected, cleaning up...")
                # Remove duplicates, keep first occurrence
                seen_urls = set()
                unique_sources = []
                for source in frontmatter['sources']:
                    if source['url'] not in seen_urls:
                        unique_sources.append(source)
                        seen_urls.add(source['url'])
                frontmatter['sources'] = unique_sources
                print(f"Sources reduced from {len(frontmatter['sources'])} to {len(unique_sources)}")
        
        # Create index entry
        index_entry = {
            "id": frontmatter['id'],
            "date": frontmatter['date'],
            "title": frontmatter['title'],
            "tags": frontmatter['tags'],
            "file": digest_file
        }
        
        print("\n=== Index Entry to Add ===")
        print(json.dumps(index_entry, indent=2, ensure_ascii=False))
        
        # Read current index
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # Check if entry already exists
        existing_ids = [entry['id'] for entry in index_data['files']]
        if frontmatter['id'] in existing_ids:
            print("⚠️  Entry already exists in index.json")
            return
        
        # Add new entry
        index_data['files'].append(index_entry)
        index_data['total_files'] = len(index_data['files'])
        
        # Sort by date (newest first)
        index_data['files'].sort(key=lambda x: x['date'], reverse=True)
        
        # Write back
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        print("✅ T12 entry added to index.json successfully")
        
    else:
        print("❌ No frontmatter found in digest file")

if __name__ == "__main__":
    fix_digest_issues()