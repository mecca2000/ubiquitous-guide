#!/usr/bin/env node
/**
 * 子代理 Worker - 执行耗时任务
 * 版本：2.0 (支持多类型子代理)
 */

// 子代理类型定义（精简版 v3.0 - 2 个子代理）
export const AGENT_TYPES = {
  'worker-task': {
    label: 'worker-task',
    name: '任务执行者',
    memoryLimit: '256MB',
    cpuLimit: 0.5,
    timeoutSeconds: 300,      // 5 分钟
    maxConcurrent: 2,         // 最多 2 个并发
    networkAccess: true,
    fileWrite: true,
    shellAccess: false,
    taskTypes: ['搜索', '查找', '调研', '分析', '创建', '写入', '生成', '报告', '下载', '安装', '整理', '研究']
  },
  'worker-cron': {
    label: 'worker-cron',
    name: '定时任务执行者',
    memoryLimit: '128MB',
    cpuLimit: 0.25,
    timeoutSeconds: 180,      // 3 分钟
    maxConcurrent: 1,
    networkAccess: true,
    fileWrite: true,
    shellAccess: false,
    taskTypes: ['心跳', '检查', '监控', '扫描', '日志', '总结', '反思']
  }
};

/**
 * 根据任务内容选择子代理类型
 */
export function selectAgentType(taskText) {
  const text = taskText.toLowerCase();
  
  for (const [type, config] of Object.entries(AGENT_TYPES)) {
    if (config.taskTypes.some(keyword => text.includes(keyword))) {
      return type;
    }
  }
  
  // 默认返回搜索员
  return 'worker-search';
}

/**
 * 生成子代理配置
 */
export function createAgentConfig(agentType, taskText) {
  const config = AGENT_TYPES[agentType];
  
  return {
    task: createTaskPrompt(taskText, config),
    label: config.label,
    cleanup: 'delete',
    timeoutSeconds: config.timeoutSeconds
  };
}

/**
 * 生成子代理任务描述
 */
export function createTaskPrompt(userMessage, agentConfig) {
  return `你是${agentConfig.name}（${agentConfig.label}），请完成以下任务：

**任务内容：** ${userMessage}

**执行要求：**
1. 专注完成指定任务
2. 所有结果写入文件（/home/admin/.openclaw/workspace/reports/）
3. 完成后简要总结关键发现
4. 遇到错误立即记录并停止
5. 超时限制：${agentConfig.timeoutSeconds}秒

**权限范围：**
- 读取文件：✅ 允许
- 写入文件：✅ 允许（仅 reports/）
- 网络访问：${agentConfig.networkAccess ? '✅ 允许' : '❌ 禁止'}
- Shell 命令：❌ 禁止

**输出位置：** 工作区 reports/ 目录

开始执行任务吧！`;
}

/**
 * 任务完成后的汇报模板
 */
export function createCompletionReport(taskName, result, duration, agentType) {
  const agent = AGENT_TYPES[agentType];
  return `## ✅ 任务完成汇报

**任务：** ${taskName}  
**执行者：** ${agent.name} (${agent.label})  
**耗时：** ${duration}秒  
**状态：** 成功

**关键结果：**
${result}

---
*子代理 worker 自动生成*`;
}

// 导出配置供主代理使用
export default {
  AGENT_TYPES,
  selectAgentType,
  createAgentConfig
};
