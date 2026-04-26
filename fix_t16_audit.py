#!/usr/bin/env python3
"""
T16 digest质量违规修复脚本
删除违规的2026-04-26T16.md文件并更新索引
"""

import json
import os
from datetime import datetime

# 配置
DIGEST_DIR = "/root/.openclaw/workspace/usiran-digest/data/digest"
INDEX_FILE = os.path.join(DIGEST_DIR, "index.json")
T16_FILE = os.path.join(DIGEST_DIR, "2026-04-26T16.md")

def main():
    print("🔍 T16 digest质量违规修复程序")
    print("=" * 50)
    
    # 1. 检查T16文件是否存在
    if not os.path.exists(T16_FILE):
        print("❌ T16文件不存在，无需删除")
        return
    
    # 2. 读取当前索引
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        print("✅ 索引文件读取成功")
    except Exception as e:
        print(f"❌ 读取索引文件失败: {e}")
        return
    
    # 3. 统计原始文件数量
    original_count = len(index_data.get('files', []))
    print(f"📁 原始索引文件数量: {original_count}")
    
    # 4. 检查T16是否在索引中
    t16_in_index = any(f.get('id') == '2026-04-26T16' for f in index_data.get('files', []))
    if not t16_in_index:
        print("❌ T16文件不在索引中，可能已被处理")
        return
    
    # 5. 删除T16文件
    try:
        os.remove(T16_FILE)
        print("✅ T16.md文件已删除")
    except Exception as e:
        print(f"❌ 删除T16文件失败: {e}")
        return
    
    # 6. 从索引中移除T16条目
    index_data['files'] = [f for f in index_data.get('files', []) if f.get('id') != '2026-04-26T16']
    
    # 7. 更新索引时间戳（使用最新的有效文件时间）
    remaining_files = index_data.get('files', [])
    if remaining_files:
        latest_file = remaining_files[0]  # 第一个是最新的
        index_data['updated'] = latest_file.get('date', datetime.now().isoformat())
    else:
        index_data['updated'] = datetime.now().isoformat()
    
    # 8. 保存更新后的索引
    try:
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        print("✅ 索引文件已更新")
    except Exception as e:
        print(f"❌ 更新索引文件失败: {e}")
        return
    
    # 9. 统计结果
    new_count = len(index_data.get('files', []))
    print(f"📊 修复完成:")
    print(f"   - 删除文件: 1个")
    print(f"   - 剩余文件数: {new_count}")
    print(f"   - 索引更新时间: {index_data['updated']}")
    
    print("\n🎉 T16质量违规修复完成！")
    print("⚠️  请运行git commit提交更改")

if __name__ == "__main__":
    main()