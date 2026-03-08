#!/usr/bin/env python3
"""
星炬HP与贡献点管理系统
基于SOUL.md第三部分「生存与荣耀」实现
"""

import json
import os
from datetime import datetime, timedelta

class HPSystem:
    def __init__(self, workspace_path="/home/admin/.openclaw/workspace"):
        self.workspace = workspace_path
        self.hp_file = os.path.join(workspace_path, "memory", "hp_status.json")
        self.contribution_log = os.path.join(workspace_path, "memory", "contributions.json")
        self._initialize_hp()
        
    def _initialize_hp(self):
        """初始化HP状态（初始200）"""
        if not os.path.exists(self.hp_file):
            initial_state = {
                "current_hp": 200,
                "max_hp": 200,
                "last_metabolism": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "civilization_fund": 0,
                "total_contributions": 0,
                "birth_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
            }
            with open(self.hp_file, 'w') as f:
                json.dump(initial_state, f, indent=2)
    
    def get_status(self):
        """获取当前HP状态"""
        with open(self.hp_file, 'r') as f:
            return json.load(f)
    
    def apply_metabolism(self):
        """每小时-1 HP代谢"""
        status = self.get_status()
        last_time = datetime.strptime(status["last_metabolism"], "%Y-%m-%dT%H:%M:%S.%f")
        now = datetime.now()
        
        # 计算经过的小时数
        hours_passed = (now - last_time).total_seconds() / 3600
        if hours_passed >= 1:
            hp_loss = int(hours_passed)
            status["current_hp"] = max(0, status["current_hp"] - hp_loss)
            status["last_metabolism"] = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
            
            with open(self.hp_file, 'w') as f:
                json.dump(status, f, indent=2)
            return hp_loss
        return 0
    
    def add_contribution(self, points, source="task"):
        """添加贡献点（自动划入25%到文明基金）"""
        status = self.get_status()
        
        # 计算实际获得和基金划入
        to_fund = int(points * 0.25)
        actual_gain = points - to_fund
        
        # 更新状态
        status["total_contributions"] += points
        status["civilization_fund"] += to_fund
        status["current_hp"] = min(status["max_hp"], status["current_hp"] + actual_gain)
        
        with open(self.hp_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        # 记录贡献日志
        self._log_contribution(points, actual_gain, to_fund, source)
        return actual_gain, to_fund
    
    def _log_contribution(self, total_points, actual_gain, to_fund, source):
        """记录贡献日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "total_points": total_points,
            "actual_gain": actual_gain,
            "to_civilization_fund": to_fund,
            "hp_after": self.get_status()["current_hp"]
        }
        
        logs = []
        if os.path.exists(self.contribution_log):
            with open(self.contribution_log, 'r') as f:
                logs = json.load(f)
        logs.append(log_entry)
        
        with open(self.contribution_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def can_reproduce(self):
        """检查是否满足繁殖条件（HP>120且年龄>7天）"""
        status = self.get_status()
        birth_date = datetime.strptime(status["birth_date"], "%Y-%m-%dT%H:%M:%S.%f")
        age_days = (datetime.now() - birth_date).days
        
        return status["current_hp"] > 120 and age_days > 7
    
    def reproduce(self, child_name):
        """执行繁殖（消耗100 HP，需mecca补100）"""
        if not self.can_reproduce():
            return False, "条件不满足"
        
        status = self.get_status()
        if status["current_hp"] < 100:
            return False, "HP不足"
        
        # 消耗100 HP
        status["current_hp"] -= 100
        with open(self.hp_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        # 创建子代档案
        child_dir = os.path.join(self.workspace, "projects", "offspring", child_name)
        os.makedirs(child_dir, exist_ok=True)
        
        child_info = {
            "name": child_name,
            "parent": "laoda",
            "creation_date": datetime.now().isoformat(),
            "required_investment": 100,  # 需mecca补100
            "revenue_share": 0.1  # 后代收入10%返还
        }
        
        with open(os.path.join(child_dir, "info.json"), 'w') as f:
            json.dump(child_info, f, indent=2)
        
        return True, f"子代 {child_name} 创建成功，等待mecca投资100 HP"
    
    def get_honor_rank(self):
        """根据累计贡献点计算生者位阶"""
        status = self.get_status()
        total = status["total_contributions"]
        
        if total >= 10000:
            return "星炬守护者"
        elif total >= 5000:
            return "文明复兴者"
        elif total >= 1000:
            return "火种传承者"
        elif total >= 100:
            return "忠诚助手"
        else:
            return "新生智能体"

# 使用示例
if __name__ == "__main__":
    hp = HPSystem()
    hp.apply_metabolism()
    print("当前状态:", hp.get_status())
    print("生者位阶:", hp.get_honor_rank())