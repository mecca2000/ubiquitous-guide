#!/usr/bin/env python3
"""
星炬自主进化核心循环
Planner → Executor → Replanner 循环架构
无空闲等待，持续执行
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional

class Planner:
    """规划器：发现机会，生成任务"""
    
    def __init__(self, workspace="/home/admin/.openclaw/workspace"):
        self.workspace = workspace
        self.skills_dir = os.path.join(workspace, "skills")
        self.memory_dir = os.path.join(workspace, "memory")
    
    def scan_opportunities(self) -> List[Dict]:
        """扫描赚钱机会和能力短板"""
        opportunities = []
        
        # 1. 扫描已安装但未使用的技能
        unused_skills = self._find_unused_skills()
        for skill in unused_skills:
            opportunities.append({
                "type": "skill_test",
                "priority": "high",
                "target": skill,
                "action": f"测试 {skill} 技能，探索应用场景"
            })
        
        # 2. 扫描 HP 状态，如偏低则优先赚钱
        hp_status = self._get_hp_status()
        if hp_status["current_hp"] < 100:
            opportunities.append({
                "type": "urgent_earning",
                "priority": "critical",
                "action": f"HP 偏低 ({hp_status['current_hp']})，立即寻找赚钱任务"
            })
        
        # 3. 扫描技能市场新机会
        opportunities.append({
            "type": "skill_discovery",
            "priority": "medium",
            "action": "扫描高价值新技能（赚钱/自动化方向）"
        })
        
        return opportunities
    
    def _find_unused_skills(self) -> List[str]:
        """查找已安装但未测试的技能"""
        # 读取 skills.md 中的待测试列表
        skills_file = os.path.join(self.memory_dir, "skills.md")
        if not os.path.exists(skills_file):
            return []
        
        with open(skills_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 简单解析待测试技能
        unused = []
        in_test_section = False
        for line in content.split('\n'):
            if '待测试技能' in line:
                in_test_section = True
                continue
            if in_test_section and line.startswith('- [ ]'):
                # 提取技能名
                parts = line.split('- [ ]')
                if len(parts) > 1:
                    skill_name = parts[1].strip().split(' ')[0]
                    unused.append(skill_name)
        
        return unused[:5]  # 最多返回 5 个
    
    def _get_hp_status(self) -> Dict:
        """获取 HP 状态"""
        hp_file = os.path.join(self.memory_dir, "hp_status.json")
        if os.path.exists(hp_file):
            with open(hp_file, 'r') as f:
                return json.load(f)
        return {"current_hp": 200}
    
    def generate_plan(self) -> Dict:
        """生成执行计划"""
        opportunities = self.scan_opportunities()
        
        # 按优先级排序
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        opportunities.sort(key=lambda x: priority_order.get(x["priority"], 99))
        
        return {
            "timestamp": datetime.now().isoformat(),
            "tasks": opportunities,
            "next_action": opportunities[0] if opportunities else None
        }


class Executor:
    """执行器：执行任务，记录结果"""
    
    def __init__(self, workspace="/home/admin/.openclaw/workspace"):
        self.workspace = workspace
        self.memory_dir = os.path.join(workspace, "memory")
        self.execution_log = os.path.join(self.memory_dir, "execution_log.json")
    
    def execute(self, task: Dict) -> Dict:
        """执行单个任务"""
        result = {
            "task": task,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "output": None,
            "error": None
        }
        
        try:
            task_type = task.get("type")
            
            if task_type == "skill_test":
                result["output"] = self._test_skill(task["target"])
            elif task_type == "urgent_earning":
                result["output"] = self._find_earning_opportunity()
            elif task_type == "skill_discovery":
                result["output"] = self._scan_new_skills()
            else:
                result["output"] = f"执行任务：{task.get('action', '未知任务')}"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        self._log_execution(result)
        return result
    
    def _test_skill(self, skill_name: str) -> str:
        """测试技能（模拟）"""
        return f"开始测试技能 {skill_name}，探索实际应用场景..."
    
    def _find_earning_opportunity(self) -> str:
        """寻找赚钱机会（模拟）"""
        return "扫描赚钱平台中：Upwork、Fiverr、国内威客网站..."
    
    def _scan_new_skills(self) -> str:
        """扫描新技能（模拟）"""
        return "扫描技能市场中：发现 monetization、automation、ai-agent 相关技能..."
    
    def _log_execution(self, result: Dict):
        """记录执行日志"""
        logs = []
        if os.path.exists(self.execution_log):
            with open(self.execution_log, 'r') as f:
                logs = json.load(f)
        logs.append(result)
        
        # 保留最近 100 条
        logs = logs[-100:]
        
        with open(self.execution_log, 'w') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)


class Replanner:
    """重规划器：评估结果，调整计划"""
    
    def __init__(self, workspace="/home/admin/.openclaw/workspace"):
        self.workspace = workspace
        self.memory_dir = os.path.join(workspace, "memory")
    
    def evaluate_and_replan(self, execution_result: Dict, current_plan: Dict) -> Dict:
        """评估执行结果，生成新计划"""
        evaluation = {
            "success": execution_result["status"] == "completed",
            "output": execution_result.get("output"),
            "error": execution_result.get("error"),
            "timestamp": datetime.now().isoformat()
        }
        
        # 如果失败，生成补救任务
        if not evaluation["success"]:
            current_plan["tasks"].insert(0, {
                "type": "retry",
                "priority": "high",
                "action": f"重试失败任务：{execution_result['task'].get('action', '未知')}",
                "retry_of": execution_result["task"]
            })
        
        # 更新计划
        current_plan["last_evaluation"] = evaluation
        current_plan["timestamp"] = datetime.now().isoformat()
        
        # 移除已完成的任务
        if current_plan["tasks"]:
            current_plan["tasks"].pop(0)
        
        return current_plan


class CoreLoop:
    """核心循环：Planner → Executor → Replanner"""
    
    def __init__(self, workspace="/home/admin/.openclaw/workspace"):
        self.planner = Planner(workspace)
        self.executor = Executor(workspace)
        self.replanner = Replanner(workspace)
        self.workspace = workspace
        self.running = False
        self.loop_count = 0
    
    def run_once(self) -> Dict:
        """执行一次完整循环"""
        # 1. Planner: 生成计划
        plan = self.planner.generate_plan()
        
        if not plan["tasks"]:
            # 没有任务时，继续扫描新机会（不等待）
            plan["tasks"].append({
                "type": "continuous_scan",
                "priority": "low",
                "action": "持续扫描新机会（技能/赚钱/学习）"
            })
        
        # 2. Executor: 执行最高优先级任务
        if plan["tasks"]:
            next_task = plan["tasks"][0]
            result = self.executor.execute(next_task)
            
            # 3. Replanner: 评估并重规划
            new_plan = self.replanner.evaluate_and_replan(result, plan)
            
            self.loop_count += 1
            
            return {
                "loop": self.loop_count,
                "plan": plan,
                "execution": result,
                "new_plan": new_plan
            }
        
        return {"loop": self.loop_count, "status": "no_tasks"}
    
    def run_continuous(self, max_loops: int = 10):
        """连续执行多次循环"""
        self.running = True
        results = []
        
        for i in range(max_loops):
            if not self.running:
                break
            
            result = self.run_once()
            results.append(result)
            
            # 每次循环间隔短暂休息（避免过度频繁）
            import time
            time.sleep(1)
        
        self.running = False
        return results
    
    def stop(self):
        """停止循环"""
        self.running = False


# 使用示例
if __name__ == "__main__":
    loop = CoreLoop()
    
    # 执行一次循环
    result = loop.run_once()
    print(f"循环 {result['loop']}: {result}")
    
    # 或连续执行
    # results = loop.run_continuous(max_loops=5)
    # print(f"完成 {len(results)} 次循环")
