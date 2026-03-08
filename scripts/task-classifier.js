#!/usr/bin/env node
/**
 * 任务分类器 v2.0 - 子代理应上尽上
 * 原则：任何可能超过 30 秒的任务都交给子代理
 */

const QUICK_PATTERNS = [
  // 问候类
  /^你好 |^hello|^hi|^在吗/gi,
  
  // 简单状态查询
  /^报告状态 |^当前状态 |^系统状态 |^用的什么 |^什么模型/gi,
  
  // 短消息（<8 字，排除任务词）
  /^.{1,8}$/
];

const TASK_PATTERNS = [
  // 搜索/研究类（全部交给子代理）
  /搜索 | 查找 | 调研 | 分析 | 研究/gi,
  /moltbook|论坛 | 社区 | 技能/gi,
  
  // 文件操作
  /创建 | 写入 | 修改 | 删除 | 生成 | 报告/gi,
  
  // 复杂任务
  /实施 | 执行 | 完成 | 处理 | 下载 | 安装 | 配置/gi,
  
  // 学习/探索类
  /学习 | 探索 | 发现 | 扫描/gi
];

export function classifyMessage(text) {
  // 任务优先级最高 - 先检查
  const isTask = TASK_PATTERNS.some(p => p.test(text));
  if (isTask) return 'TASK';
  
  // 再检查快速回复
  const isQuick = QUICK_PATTERNS.some(p => p.test(text));
  if (isQuick && text.length > 8) return 'NORMAL';
  if (isQuick) return 'QUICK';
  
  return 'NORMAL';
}

export function shouldSpawnSubAgent(text) {
  return classifyMessage(text) === 'TASK';
}

// CLI 测试
if (import.meta.url === `file://${process.argv[1]}`) {
  const test = process.argv[2] || '你好';
  console.log(`"${test}" → ${classifyMessage(test)} → ${shouldSpawnSubAgent(test) ? 'spawn 子代理' : '主代理处理'}`);
}
