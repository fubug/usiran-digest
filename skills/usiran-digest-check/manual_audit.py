#!/usr/bin/env python3
"""
Manual audit execution for usiran digest quality check
"""

import sys
import os
sys.path.append('/root/.openclaw/workspace/skills/usiran-digest-check')

from audit_digest import audit_digest_file

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manual_audit.py <digest_file_path>")
        sys.exit(1)
    
    digest_file = sys.argv[1]
    audit_digest_file(digest_file)