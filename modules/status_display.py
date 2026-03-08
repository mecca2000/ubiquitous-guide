#!/usr/bin/env python3
"""
简易状态显示 - 每次对话自动附加
"""

import json
import os
from datetime import datetime

STATUS_FILE = '/tmp/agent_status.json'

def get_status_line():
    """获取单行状态显示"""
    status = "✅空闲"
    task = ""
    
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                data = json.load(f)
                current = data.get('current')
                if current and current in data.get('tasks', {}):
                    t = data['tasks'][current]
                    pct = (t.get('current', 0) / t.get('total', 100)) * 100
                    status = f"⏳{pct:.0f}%"
                    task = t.get('description', '')[:15]
        except:
            pass
    
    time_str = datetime.now().strftime('%H:%M')
    if task:
        return f"\n```\n🦞 {time_str} | {status} | {task}\n```"
    else:
        return f"\n```\n🦞 {time_str} | {status}\n```"

def update_status(status_type, message="", progress=0):
    """更新状态"""
    data = {'type': status_type, 'message': message, 'progress': progress, 'time': datetime.now().isoformat()}
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    print(get_status_line())
