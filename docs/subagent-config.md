# 子代理系统配置规范

**版本：** 1.0  
**创建时间：** 2026-03-03  
**设计原则：** 精简化、模块化、安全优先

---

## 🎯 子代理命名体系

### 主代理
- **名称：** "老大"（我）
- **角色：** 主控中心、对话接口、任务调度器
- **会话：** `agent:main:main`

### 子代理分类

| 代号 | 名称 | 用途 | 优先级 |
|------|------|------|--------|
| `worker-search` | 搜索员 | 网络搜索、信息收集 | HIGH |
| `worker-writer` | 文书员 | 文档生成、报告撰写 | MEDIUM |
| `worker-analyst` | 分析师 | 数据分析、深度调研 | MEDIUM |
| `worker-monitor` | 监控员 | 心跳任务、定期检查 | LOW |

---

## 📊 资源利用规则

### 全局资源池（服务器：2GB RAM, 2 核）

```
总资源分配：
├─ 主代理（对话）     800MB   1 核    (40% RAM, 50% CPU)
├─ 子代理池          512MB   0.5 核  (25% RAM, 25% CPU)
├─ 系统开销          256MB   -      (12% RAM)
└─ 缓冲预留          432MB   0.5 核  (23% RAM, 25% CPU)
```

### 子代理资源配置

#### worker-search（搜索员）
```javascript
{
  label: 'worker-search',
  memoryLimit: '128MB',
  cpuLimit: 0.25,
  timeoutSeconds: 180,      // 3 分钟
  maxConcurrent: 2,         // 最多 2 个并发
  networkAccess: true,      // ✅ 需要网络
  fileWrite: true,          // ✅ 写入结果
  shellAccess: false        // ❌ 禁止 shell
}
```

#### worker-writer（文书员）
```javascript
{
  label: 'worker-writer',
  memoryLimit: '128MB',
  cpuLimit: 0.25,
  timeoutSeconds: 300,      // 5 分钟
  maxConcurrent: 1,         // 单线程保证质量
  networkAccess: false,     // ❌ 不需要网络
  fileWrite: true,          // ✅ 写入文档
  shellAccess: false        // ❌ 禁止 shell
}
```

#### worker-analyst（分析师）
```javascript
{
  label: 'worker-analyst',
  memoryLimit: '256MB',
  cpuLimit: 0.5,            // 需要更多计算
  timeoutSeconds: 600,      // 10 分钟
  maxConcurrent: 1,         // 单线程深度分析
  networkAccess: true,      // ✅ 需要查资料
  fileWrite: true,          // ✅ 写入报告
  shellAccess: false        // ❌ 禁止 shell
}
```

#### worker-monitor（监控员）
```javascript
{
  label: 'worker-monitor',
  memoryLimit: '64MB',      // 轻量级
  cpuLimit: 0.1,
  timeoutSeconds: 120,      // 2 分钟
  maxConcurrent: 1,
  networkAccess: false,     // ❌ 本地检查
  fileWrite: true,          // ✅ 写入日志
  shellAccess: false        // ❌ 禁止 shell
}
```

### 资源调度策略

```javascript
// 动态资源分配
function allocateResource(taskType, currentLoad) {
  if (currentLoad > 0.8) {
    // 高负载：限制并发
    return { maxConcurrent: 1, priority: 'low' };
  } else if (currentLoad > 0.5) {
    // 中负载：正常分配
    return { maxConcurrent: 2, priority: 'normal' };
  } else {
    // 低负载：允许突发
    return { maxConcurrent: 3, priority: 'high' };
  }
}
```

---

## 📋 任务范围分工

### 主代理（我）负责任务

| 类型 | 具体任务 | 说明 |
|------|----------|------|
| **对话交互** | 问候、聊天、答疑 | 立即回复，不延迟 |
| **状态查询** | 系统状态、模型信息 | 快速响应 |
| **任务调度** | 判断任务类型、分配子代理 | 核心职责 |
| **结果汇总** | 整合子代理报告、汇报给用户 | 最终输出 |
| **决策判断** | 需要人类确认的事项 | 暂停并请示 |

### 子代理负责任务

#### worker-search（搜索员）
✅ **负责任务：**
- 网络搜索（searxng/tavily）
- 信息收集（网页抓取）
- 数据查询（API 调用）
- 论坛/社区内容浏览（Moltbook 等）
- 新闻/文章摘要

❌ **不负责：**
- 文件写入（只返回原始数据）
- 复杂分析（只收集不分析）
- 对话交互

**示例：**
```
用户："搜索 moltbook 上有什么好玩的"
→ worker-search 执行
→ 返回搜索结果列表
→ 主代理整理后汇报
```

#### worker-writer（文书员）
✅ **负责任务：**
- 文档生成（markdown 文件）
- 报告撰写（格式化输出）
- 内容整理（结构化数据）
- 日志记录（对话/任务日志）
- 文件归档（备份/整理）

❌ **不负责：**
- 网络访问（只处理本地数据）
- 复杂分析（只格式化不分析）
- 决策判断

**示例：**
```
用户："创建一份系统状态报告"
→ 主代理收集数据
→ worker-writer 格式化写入文件
→ 返回文件路径
```

#### worker-analyst（分析师）
✅ **负责任务：**
- 深度调研（多源数据整合）
- 数据分析（趋势/模式识别）
- 对比研究（多方案比较）
- 策略建议（基于分析结果）
- 复杂报告（综合型文档）

❌ **不负责：**
- 简单搜索（交给 search）
- 快速响应（需要时间思考）
- 对话交互

**示例：**
```
用户："分析 AI 智能体发展趋势"
→ worker-analyst 执行
→ 搜索 + 整理 + 分析
→ 生成深度报告（10 分钟）
```

#### worker-monitor（监控员）
✅ **负责任务：**
- 心跳检查（定期任务）
- 系统监控（资源使用率）
- 日志扫描（错误模式检测）
- 技能更新检查（find-skills）
- 安全审计（配置检查）

❌ **不负责：**
- 用户对话（后台任务）
- 复杂分析（只报告状态）
- 网络搜索（除非需要）

**示例：**
```
HEARTBEAT 任务
→ worker-monitor 执行
→ 检查各项指标
→ 写入日志文件
→ 异常时通知主代理
```

---

## 🔄 任务流转流程

### 标准流程

```
用户消息
   ↓
主代理（分类判断）
   ├─ QUICK → 立即回复
   ├─ NORMAL → 正常对话
   └─ TASK → 任务类型判断
              ├─ 搜索类 → worker-search
              ├─ 写作类 → worker-writer
              ├─ 分析类 → worker-analyst
              └─ 监控类 → worker-monitor
   ↓
子代理执行（后台）
   ↓
结果写入 reports/
   ↓
主代理汇总 → 飞书通知用户
```

### 任务优先级

| 优先级 | 任务类型 | 响应时间 | 示例 |
|--------|----------|----------|------|
| **P0** | 用户对话 | <1 秒 | "你好" |
| **P1** | 状态查询 | <3 秒 | "当前状态" |
| **P2** | 搜索任务 | <3 分钟 | "搜索 XXX" |
| **P3** | 文档生成 | <5 分钟 | "创建报告" |
| **P4** | 深度分析 | <10 分钟 | "分析趋势" |
| **P5** | 监控任务 | 后台执行 | 心跳检查 |

---

## 🔒 安全与限制

### 权限控制

| 权限 | 主代理 | 子代理 | 说明 |
|------|--------|--------|------|
| 读取工作区 | ✅ | ✅ | 所有文件 |
| 写入工作区 | ✅ | ⚠️ | 仅 reports/ |
| 网络访问 | ✅ | ⚠️ | 按需分配 |
| Shell 命令 | ✅ | ❌ | 子代理禁止 |
| 敏感文件 | ✅ | ❌ | 子代理禁止 |
| 技能安装 | ✅ | ❌ | 需用户确认 |

### 超时保护

```javascript
const TIMEOUT_RULES = {
  'worker-search': 180,    // 3 分钟
  'worker-writer': 300,    // 5 分钟
  'worker-analyst': 600,   // 10 分钟
  'worker-monitor': 120    // 2 分钟
};

// 超时后自动终止并记录
function handleTimeout(agentId) {
  logError(`子代理 ${agentId} 超时终止`);
  notifyUser(`任务超时，已终止。请检查 reports/ 中的部分结果。`);
}
```

### 资源保护

```javascript
// 防止资源耗尽
const RESOURCE_LIMITS = {
  maxMemory: '512MB',      // 子代理总内存
  maxConcurrent: 3,        // 最多 3 个并发
  minFreeMemory: '256MB'   // 保留缓冲
};

function checkResourceBeforeSpawn() {
  const currentUsage = getMemoryUsage();
  if (currentUsage > RESOURCE_LIMITS.maxMemory) {
    throw new Error('资源不足，请稍后重试');
  }
}
```

---

## 📈 监控与优化

### 性能指标

| 指标 | 目标值 | 监控方式 |
|------|--------|----------|
| 对话响应时间 | <1 秒 | 每次对话记录 |
| 任务完成率 | >95% | 子代理日志 |
| 资源使用率 | <80% | 定期检查 |
| 超时率 | <5% | 任务统计 |

### 优化策略

1. **动态调整并发** - 根据负载自动调整
2. **任务合并** - 相似任务合并执行
3. **结果缓存** - 重复查询返回缓存
4. **优先级调度** - 紧急任务优先

---

## 🎯 使用示例

### 示例 1：搜索任务
```
用户："搜索 moltbook 上有什么好玩的"
   ↓
主代理：分类 → TASK (搜索类)
   ↓
spawn worker-search
   ↓
[后台执行 searxng 搜索]
   ↓
写入 reports/moltbook-search-*.md
   ↓
主代理："搜索完成！发现 3 个有趣话题..."
```

### 示例 2：分析报告
```
用户："分析 AI 智能体发展趋势"
   ↓
主代理：分类 → TASK (分析类)
   ↓
spawn worker-analyst
   ↓
[搜索 + 整理 + 分析，10 分钟]
   ↓
写入 reports/ai-trend-analysis-*.md
   ↓
主代理："深度分析完成！关键发现..."
```

### 示例 3：多任务并发
```
用户："搜索 moltbook 并创建报告"
   ↓
主代理：拆分为两个任务
   ├─ spawn worker-search (搜索)
   └─ 等待完成后 → spawn worker-writer (报告)
   ↓
[并行/串行执行]
   ↓
汇总结果 → 汇报
```

---

*本文档将随子代理系统进化持续更新*
