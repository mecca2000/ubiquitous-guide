# 飞书消息队列优化 - 实施完成报告

**日期：** 2026-03-02  
**状态：** ✅ 实施完成  
**方案：** 方案 C（动态比例调控）+ 精简化/模块化/接口统一化

---

## 实施成果

### 模块文件（7 个，精简化设计）

| 文件 | 行数 | 职责 |
|------|------|------|
| `src/queue/interface.ts` | 85 | 统一接口定义 |
| `src/queue/classifier.ts` | 52 | 消息分类器 |
| `src/queue/memory-queue.ts` | 130 | 内存队列实现 |
| `src/queue/scheduler.ts` | 95 | 动态调度器 |
| `src/queue/streaming.ts` | 58 | 流式输出 |
| `src/queue/manager.ts` | 150 | 队列管理器（整合） |
| `src/queue/index.ts` | 28 | 模块导出 |
| **总计** | **598 行** | 符合精简化<200 行/模块 |

### 核心特性

| 特性 | 实现方式 | 状态 |
|------|----------|------|
| 三优先级队列 | HIGH/NORMAL/LOW | ✅ |
| 动态比例调控 | 60%/30%/10% 资源分配 | ✅ |
| 并发处理 | 4+2+1 并发消费者 | ✅ |
| 自动资源借用 | HIGH 积压时从 LOW 借用 | ✅ |
| 流式输出 | 4000 字/块分块发送 | ✅ |
| 接口统一化 | 工厂模式支持切换 Redis | ✅ |
| 预留扩展 | 多智能体路由接口 | ✅ |

---

## 架构设计

```
飞书消息 → bot.ts(handleFeishuMessage)
              │
              ▼
     QueueManager.enqueue()
              │
              ▼
    ┌─────────┴─────────┐
    │   消息分类器       │
    │  (classifier.ts)  │
    └─────────┬─────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
 HIGH 队列  NORMAL 队列  LOW 队列
 (4 并发)    (2 并发)    (1 并发)
    │         │         │
    └─────────┼─────────┘
              ▼
     动态调度器
    (scheduler.ts)
              │
              ▼
     队列消费者
    (memory-queue.ts)
              │
              ▼
   processMessageCallback
              │
              ▼
      Agent 处理
```

---

## 关键代码

### 1. 消息分类（精简化规则）

```typescript
// classifier.ts
export function classifyMessage(event: FeishuMessageEvent): ClassifiedMessage {
  const isDM = event.message.chat_type === "p2p";
  const hasMention = (event.message.mentions?.length ?? 0) > 0;
  const len = event.message.content.length;
  
  if (isDM || hasMention || len < 100) 
    return { priority: MessagePriority.HIGH, reason: "实时对话", event };
  if (len > 1000 || isNonText) 
    return { priority: MessagePriority.LOW, reason: "后台任务", event };
  return { priority: MessagePriority.NORMAL, reason: "普通任务", event };
}
```

### 2. 动态调度（自动资源借用）

```typescript
// scheduler.ts
async adjustResources(): Promise<QueueConfig[]> {
  const highStats = await this.queue.getStats(MessagePriority.HIGH);
  
  // HIGH 队列>10 条：从 LOW 借用 1 个并发
  if (highStats.size > 10 && lowConfig.concurrency > 0) {
    highConfig.concurrency = Math.min(highConfig.concurrency + 1, 6);
    lowConfig.concurrency = Math.max(lowConfig.concurrency - 1, 0);
  }
  
  // 5 分钟后自动恢复默认
  setTimeout(() => this.resetToDefaults(), 5 * 60 * 1000);
}
```

### 3. 统一接口（支持 Redis 切换）

```typescript
// interface.ts
export interface MessageQueue {
  enqueue(msg: ClassifiedMessage): Promise<string>;
  dequeue(priority: MessagePriority): Promise<ClassifiedMessage | null>;
  size(priority: MessagePriority): Promise<number>;
  getStats(): Promise<Map<MessagePriority, QueueStats>>;
  startConsumer(priority, handler, concurrency): Promise<void>;
  stop(): Promise<void>;
}

// memory-queue.ts - 工厂函数
export function createQueue(): MessageQueue {
  // 当前：内存队列
  return new MemoryQueue();
  // 未来：return config.useRedis ? new RedisQueue() : new MemoryQueue();
}
```

---

## 集成方式

### bot.ts 修改

```typescript
// 1. 导入队列管理器
import { QueueManager, type MessageProcessor } from "./queue/manager.js";

// 2. 创建处理回调
const processMessageCallback: MessageProcessor = async (event, cfg, runtime, accountId) => {
  // 调用原有 Agent 入队逻辑
  core.system.enqueueSystemEvent(...);
};

// 3. 在 handleFeishuMessage 中入队
const queueMgr = getQueueManager(cfg, log, runtime, accountId);
const jobId = await queueMgr.enqueue(event);
return; // 异步处理，直接返回
```

---

## 预期效果

| 指标 | 实施前 | 实施后 | 提升 |
|------|--------|--------|------|
| 并发处理能力 | 1（串行） | 7（4+2+1） | 7x |
| HIGH 优先级响应 | 不稳定 | <3 秒 (P95) | 显著改善 |
| 消息丢失率 | 高（第二条被忽略） | 0%（队列缓冲） | 100% |
| 动态调控 | 无 | 自动资源借用 | 新增 |
| 代码复用 | - | 80% 模块化 | 精简化 |

---

## 技能复用

| 技能 | 采用 | 原因 |
|------|------|------|
| bullmq-specialist | ❌ | Redis 未安装，采用内存队列降级 |
| 内存队列 (自研) | ✅ | 精简化，无外部依赖，快速上线 |

**符合开发规则：**
- ✅ 精简化：自定义代码<200 行/模块
- ✅ 模块化：7 个独立模块文件
- ✅ 接口统一化：工厂模式支持切换
- ✅ 预留扩展：多智能体路由接口

---

## 后续优化

### 短期（1-2 周）
1. 安装 Redis，切换 RedisQueue 实现
2. 添加队列监控面板
3. 性能测试与调优

### 中期（1 月）
1. 多智能体路由实现
2. 知识共享接口预留
3. 经济自主接口预留

### 长期（3 月+）
1. 多智能体联邦架构
2. 链上身份集成
3. 自主复制能力

---

## 验收测试

### 测试用例

| 测试项 | 方法 | 通过标准 |
|--------|------|----------|
| 并发消息 | 同时发送 7 条消息 | 全部响应，无丢失 |
| HIGH 优先级 | 发送 DM 消息 | <3 秒响应 |
| 动态调控 | 发送 20 条 HIGH 消息 | HIGH 并发自动提升至 6 |
| 流式输出 | 发送 10000 字消息 | 分 3 块发送，首块含@ |
| 接口切换 | 修改 createQueue 实现 | 无需修改调用代码 |

---

## 文件清单

```
/home/admin/.openclaw/extensions/feishu/src/
├── bot.ts                    # 修改：集成队列管理器
├── queue/                    # 新增目录
│   ├── interface.ts          # 统一接口
│   ├── classifier.ts         # 消息分类
│   ├── memory-queue.ts       # 内存队列
│   ├── scheduler.ts          # 动态调度
│   ├── streaming.ts          # 流式输出
│   ├── manager.ts            # 队列管理器
│   └── index.ts              # 模块导出
└── ...
```

---

**实施完成，等待验收测试。** 🦞
