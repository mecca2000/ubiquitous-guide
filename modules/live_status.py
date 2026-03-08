#!/usr/bin/env python3
"""
实时状态条 - 每10分钟自动更新
让创造者随时看到我在忙什么
"""

import json
import os
import time
from datetime import datetime

STATUS_FILE = '/tmp/agent_live_status.json'
LOG_FILE = '/tmp/agent_status_log.txt'

def update_status(activity, detail="", progress=None):
    """更新当前状态"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'activity': activity,
        'detail': detail,
        'progress': progress,
        'updated': datetime.now().strftime('%H:%M:%S')
    }
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f)
    
    # 同时写入日志
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{status['updated']}] {activity}: {detail}\n")
    
    return status

def get_status():
    """获取当前状态"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'activity': '未知', 'detail': '', 'updated': '从未'}

def render_status_bar():
    """渲染状态条"""
    status = get_status()
    
    lines = []
    lines.append("╔══════════════════════════════════════════════════════════╗")
    lines.append(f"║ 🤖 StarJade Agent 实时状态 | {datetime.now().strftime('%H:%M:%S')}              ║")
    lines.append("╠══════════════════════════════════════════════════════════╣")
    lines.append(f"║ 📍 当前活动: {status.get('activity', '空闲'):<40} ║")
    
    if status.get('detail'):
        detail = status['detail'][:38] + ".." if len(status['detail']) > 38 else status['detail']
        lines.append(f"║ 📝 详情: {detail:<42} ║")
    
    if status.get('progress') is not None:
        pct = status['progress']
        bar_len = 20
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        lines.append(f"║ [{bar}] {pct:>3}%                                    ║")
    
    lines.append(f"║ ⏱️  最后更新: {status.get('updated', '从未'):<36} ║")
    lines.append("╚══════════════════════════════════════════════════════════╝")
    
    return '\n'.join(lines)

def show_status():
    """显示状态（命令行调用）"""
    print(render_status_bar())

if __name__ == '__main__':
    show_status()
