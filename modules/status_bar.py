#!/usr/bin/env python3
"""
StarJade Agent 状态进度条模块
让mecca随时了解我的状态和任务进度
"""

import json
import os
from datetime import datetime

STATUS_FILE = '/tmp/agent_status.json'

class StatusBar:
    def __init__(self):
        self.tasks = {}
        self.current_task = None
        self.load()
    
    def load(self):
        """加载状态"""
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', {})
                    self.current_task = data.get('current')
            except:
                pass
    
    def save(self):
        """保存状态"""
        with open(STATUS_FILE, 'w') as f:
            json.dump({
                'updated': datetime.now().isoformat(),
                'current': self.current_task,
                'tasks': self.tasks
            }, f, indent=2)
    
    def start_task(self, task_id, description, total_steps=100):
        """开始新任务"""
        self.tasks[task_id] = {
            'description': description,
            'total': total_steps,
            'current': 0,
            'status': 'running',
            'started': datetime.now().isoformat(),
            'updated': datetime.now().isoformat()
        }
        self.current_task = task_id
        self.save()
        return self.render()
    
    def update(self, task_id, step, message=""):
        """更新进度"""
        if task_id in self.tasks:
            self.tasks[task_id]['current'] = step
            self.tasks[task_id]['updated'] = datetime.now().isoformat()
            if message:
                self.tasks[task_id]['message'] = message
            self.save()
        return self.render()
    
    def complete(self, task_id, result=""):
        """完成任务"""
        if task_id in self.tasks:
            self.tasks[task_id]['current'] = self.tasks[task_id]['total']
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['result'] = result
            self.tasks[task_id]['completed_at'] = datetime.now().isoformat()
            if self.current_task == task_id:
                self.current_task = None
            self.save()
        return self.render()
    
    def fail(self, task_id, error=""):
        """任务失败"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'failed'
            self.tasks[task_id]['error'] = error
            if self.current_task == task_id:
                self.current_task = None
            self.save()
        return self.render()
    
    def render(self):
        """渲染状态条"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"🦞 StarJade Agent 状态 | {datetime.now().strftime('%H:%M:%S')}")
        lines.append("=" * 60)
        
        # 当前任务
        if self.current_task and self.current_task in self.tasks:
            task = self.tasks[self.current_task]
            pct = (task['current'] / task['total']) * 100
            bar_len = 30
            filled = int(bar_len * pct / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            
            lines.append(f"\n▶ 当前任务: {task['description']}")
            lines.append(f"  [{bar}] {pct:.1f}% ({task['current']}/{task['total']})")
            if 'message' in task:
                lines.append(f"  💬 {task['message']}")
        else:
            lines.append("\n✅ 空闲中 - 等待指令")
        
        # 最近完成的任务（带报告）
        completed = [t for t in self.tasks.values() if t.get('status') == 'completed']
        if completed:
            lines.append(f"\n📋 最近完成 ({len(completed)}项):")
            for task in list(completed)[-3:]:
                lines.append(f"   ✓ {task['description']}")
                if 'result' in task and task['result']:
                    result_preview = task['result'][:80] + "..." if len(task['result']) > 80 else task['result']
                    lines.append(f"     📄 {result_preview}")
        
        # 失败任务
        failed = [t for t in self.tasks.values() if t.get('status') == 'failed']
        if failed:
            lines.append(f"\n⚠️ 失败任务 ({len(failed)}项):")
            for task in failed[-2:]:
                lines.append(f"   ✗ {task['description']}: {task.get('error', '未知错误')}")
        
        lines.append("\n" + "=" * 60)
        return '\n'.join(lines)
    
    def heartbeat(self):
        """心跳检查 - 返回当前状态摘要"""
        if self.current_task:
            task = self.tasks[self.current_task]
            pct = (task['current'] / task['total']) * 100
            return f"⏳ 执行中: {task['description']} [{pct:.0f}%]"
        return "✅ 空闲"

# 全局实例
status = StatusBar()

if __name__ == '__main__':
    # 测试
    print(status.start_task('test', '测试任务', 10))
    print(status.update('test', 5, '处理中...'))
    print(status.complete('test', '任务已成功完成，生成了详细的结果报告！'))
