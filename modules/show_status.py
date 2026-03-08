#!/usr/bin/env python3
"""
快速查看Agent状态
用法: python show_status.py
"""

import sys
sys.path.insert(0, '/home/admin/.openclaw/workspace/modules')
from status_bar import status

print(status.render())
