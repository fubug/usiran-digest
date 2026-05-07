#!/usr/bin/env python3
"""
更新index.json并添加14:00 digest条目
"""

import json
import datetime
from pathlib import Path
import subprocess

def update_1400_index():
    skill_root = Path("/root/.openclaw/workspace/skills/usiran-digest")
    index_file = skill_root / "data" / "digest" / "index.json"
    
    try:
        # 读取现有index.json
        with open(index_file, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 创建14:00的新条目
        target_time = datetime.datetime(2026, 5, 6, 14, 0, 0)
        
        new_entry = {
            "id": target_time.strftime("%Y-%m-%dT%H%M"),
            "file": f"data/digest/digest-{target_time.strftime('%Y%m%dT%H')}.md",
            "date": target_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "title": {
                "zh": f"美伊战争时事简报 - {target_time.strftime('%Y年%m月%d日 %H:%M')}",
                "en": f"US-Iran War Briefing - {target_time.strftime('%Y-%m-%d %H:%M')}"
            },
            "tags": ["美伊战争", "中东局势", "时事简报", "战争发展"]
        }
        
        # 检查是否已存在相同ID的条目
        existing_ids = [entry["id"] for entry in index_data["files"]]
        if new_entry["id"] not in existing_ids:
            # 在头部插入新条目
            index_data["files"].insert(0, new_entry)
            index_data["updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # 写回文件
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            
            print(f"Index.json已更新，新条目ID: {new_entry['id']}")
            
            # 添加文件到本地Git仓库
            subprocess.run(['git', 'add', 'data/digest/index.json'], check=True)
            subprocess.run(['git', 'add', 'data/digest/digest-20260506T1400.md'], check=True)
            
            # 提交
            commit_msg = f"Add digest for {new_entry['date']} and update index.json"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # 推送到GitHub
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            print("Git推送完成")
            return True
        else:
            print(f"条目 {new_entry['id']} 已存在，跳过更新")
            return False
        
    except Exception as e:
        print(f"执行过程中出错: {e}")
        return False

if __name__ == "__main__":
    update_1400_index()