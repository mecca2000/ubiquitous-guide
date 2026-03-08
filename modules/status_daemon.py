#!/usr/bin/env python3
"""
状态守护进程 - 每10分钟自动汇报状态到飞书
"""

import time
import sys
import os
sys.path.insert(0, '/home/admin/.openclaw/workspace')

from modules.live_status import get_status, render_status_bar

def send_status_to_feishu():
    """发送状态到飞书（通过消息工具）"""
    status_text = render_status_bar()
    
    # 使用message工具发送
    try:
        # 这里会由主代理调用时注入channel
        print(f"[STATUS_UPDATE] {time.strftime('%H:%M:%S')}")
        print(status_text)
        return True
    except Exception as e:
        print(f"[ERROR] 发送状态失败: {e}")
        return False

def run_daemon():
    """运行守护进程"""
    print("[*] 状态守护进程启动，每10分钟更新一次...")
    
    while True:
        try:
            send_status_to_feishu()
            # 600秒 = 10分钟
            time.sleep(600)
        except KeyboardInterrupt:
            print("\n[*] 守护进程停止")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(60)  # 出错后1分钟重试

if __name__ == '__main__':
    run_daemon()
