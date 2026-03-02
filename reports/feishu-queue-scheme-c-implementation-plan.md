# 飞书消息队列方案 C 实施计划

**日期：** 2026-03-02  
**状态：** 待实施  
**原则：** 精简化、模块化、接口统一化、优先使用现成技能

---

## 核心设计

### 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                     飞书消息入口                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  消息分类器 (Classifier Module)                              │
│  - 实时对话 (HIGH): DM 消息、@提及、简短问题                   │
│  - 普通任务 (NORMAL): 群聊消息、中等复杂度任务                 │
│  - 后台任务 (LOW): 长文本、文件处理、周期性任务                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ HIGH 队列 │   │NORMAL 队列│   │ LOW 队列 │
        │ 60% 资源  │   │ 30% 资源  │   │ 10% 资源  │
        │ 优先处理  │   │ 普通处理  │   │ 空闲处理  │
        └──────────┘   └──────────┘   └──────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  统一处理器 (Unified Processor)                              │
│  - 基于 BullMQ (现成技能)                                     │
│  - 动态比例调控                                               │
│  - 并发控制 (maxConcurrent: 4)                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  飞书回复模块 (Reply Module)                                 │
│  - 实时回复 (<3 秒 P95)                                       │
│  - 流式输出                                                   │
│  - 提及保持                                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 模块设计

### 模块 1: 消息分类器 (`classifier.ts`)

```typescript
// 精简实现：基于规则的分类
export enum MessagePriority {
  HIGH = "high",      // 60% 资源，目标 <3 秒响应
  NORMAL = "normal",  // 30% 资源，目标 <10 秒响应
  LOW = "low"         // 10% 资源，后台处理
}

export interface ClassifiedMessage {
  priority: MessagePriority;
  reason: string;
  originalMessage: FeishuMessageEvent;
}

export function classifyMessage(event: FeishuMessageEvent): ClassifiedMessage {
  const content = event.message.content;
  const isDM = event.message.chat_type === "p2p";
  const hasMention = (event.message.mentions?.length ?? 0) > 0;
  const contentLength = content.length;
  
  // HIGH: DM 消息、@提及、简短问题 (<100 字)
  if (isDM || hasMention || contentLength < 100) {
    return { priority: MessagePriority.HIGH, reason: "实时对话", originalMessage: event };
  }
  
  // LOW: 长文本 (>1000 字)、文件消息
  if (contentLength > 1000 || event.message.message_type !== "text") {
    return { priority: MessagePriority.LOW, reason: "后台任务", originalMessage: event };
  }
  
  // NORMAL: 其他
  return { priority: MessagePriority.NORMAL, reason: "普通任务", originalMessage: event };
}
```

---

### 模块 2: 队列配置 (`queue-config.ts`)

```typescript
// 使用 BullMQ 现成技能
export interface QueueConfig {
  name: string;
  priority: MessagePriority;
  concurrency: number;  // 并发数
  resourceRatio: number; // 资源比例
  maxRetries: number;
  timeoutMs: number;
}

export const QUEUE_CONFIGS: QueueConfig[] = [
  {
    name: "feishu-high",
    priority: MessagePriority.HIGH,
    concurrency: 4,      // 60% of maxConcurrent:4 ≈ 2.4 → 向上取整 4 保证实时
    resourceRatio: 0.6,
    maxRetries: 3,
    timeoutMs: 30000,    // 30 秒超时
  },
  {
    name: "feishu-normal",
    priority: MessagePriority.NORMAL,
    concurrency: 2,      // 30% ≈ 1.2 → 2
    resourceRatio: 0.3,
    maxRetries: 3,
    timeoutMs: 60000,
  },
  {
    name: "feishu-low",
    priority: MessagePriority.LOW,
    concurrency: 1,      // 10% ≈ 0.4 → 1
    resourceRatio: 0.1,
    maxRetries: 5,
    timeoutMs: 120000,
  },
];
```

---

### 模块 3: 动态比例调控器 (`dynamic-controller.ts`)

```typescript
// 根据队列状态动态调整资源分配
export class DynamicQueueController {
  private configs: QueueConfig[];
  private queueStats = new Map<string, { size: number; avgProcessTime: number }>();
  
  // 动态调整：如果 HIGH 队列积压，从 LOW 借用资源
  public adjustResources(): QueueConfig[] {
    const highStats = this.queueStats.get("feishu-high");
    const lowStats = this.queueStats.get("feishu-low");
    
    if (highStats && highStats.size > 10) {
      // HIGH 队列积压，临时提升并发
      const highConfig = this.configs.find(c => c.name === "feishu-high")!;
      const lowConfig = this.configs.find(c => c.name === "feishu-low")!;
      
      // 从 LOW 借用 1 个并发
      highConfig.concurrency = Math.min(highConfig.concurrency + 1, 6);
      lowConfig.concurrency = Math.max(lowConfig.concurrency - 1, 0);
    }
    
    return this.configs;
  }
  
  // 定期恢复默认配置
  public resetToDefaults(): void {
    // 每 5 分钟恢复默认比例
  }
}
```

---

### 模块 4: 统一处理器 (`unified-processor.ts`)

```typescript
// 基于 BullMQ 的统一处理接口
import { Queue, Worker } from "bullmq";

export class UnifiedMessageProcessor {
  private queues: Map<MessagePriority, Queue>;
  private workers: Map<MessagePriority, Worker>;
  
  constructor() {
    this.queues = new Map();
    this.workers = new Map();
    this.initializeQueues();
  }
  
  private initializeQueues(): void {
    QUEUE_CONFIGS.forEach(config => {
      const queue = new Queue(config.name, {
        connection: { host: "localhost", port: 6379 }, // Redis
        defaultJobOptions: {
          attempts: config.maxRetries,
          backoff: { type: "exponential", delay: 1000 },
        },
      });
      this.queues.set(config.priority, queue);
      
      const worker = new Worker(config.name, 
        async (job) => this.processMessage(job),
        {
          connection: { host: "localhost", port: 6379 },
          concurrency: config.concurrency,
        }
      );
      this.workers.set(config.priority, worker);
    });
  }
  
  public async enqueueMessage(classified: ClassifiedMessage): Promise<string> {
    const queue = this.queues.get(classified.priority)!;
    const job = await queue.add("feishu-message", {
      event: classified.originalMessage,
      priority: classified.priority,
      enqueuedAt: Date.now(),
    }, {
      priority: this.getJobPriority(classified.priority),
    });
    return job.id!;
  }
  
  private getJobPriority(priority: MessagePriority): number {
    switch (priority) {
      case MessagePriority.HIGH: return 10;
      case MessagePriority.NORMAL: return 5;
      case MessagePriority.LOW: return 1;
    }
  }
  
  private async processMessage(job: Job): Promise<void> {
    // 调用现有的 handleFeishuMessage 处理
  }
}
```

---

## 实施步骤

### 阶段 1: 基础队列（1 小时）
1. ✅ 安装 BullMQ 技能：`npx skills add sickn33/antigravity-awesome-skills@bullmq-specialist`
2. ⏳ 创建 4 个模块文件（classifier, queue-config, dynamic-controller, unified-processor）
3. ⏳ 修改飞书插件入口（bot.ts）集成消息分类

### 阶段 2: 动态调控（30 分钟）
4. ⏳ 实现动态资源调整逻辑
5. ⏳ 添加队列监控和日志

### 阶段 3: 测试优化（30 分钟）
6. ⏳ 并发消息测试
7. ⏳ 性能调优

---

## 依赖项

| 组件 | 来源 | 状态 |
|------|------|------|
| BullMQ | sickn33/antigravity-awesome-skills@bullmq-specialist | 待安装 |
| Redis | 系统服务 | 需确认是否已安装 |
| 飞书插件 | @openclaw/feishu | 已安装 |

---

## 预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| HIGH 优先级响应时间 | 串行 | <3 秒 (P95) |
| 并发处理能力 | 1 | 4 (HIGH) + 2 (NORMAL) + 1 (LOW) |
| 消息丢失率 | 高 | 0% |
| 动态调整 | 无 | 自动根据负载调整 |

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| Redis 未安装 | 使用内存队列降级方案 |
| 技能兼容性问题 | 先测试后上线 |
| 配置复杂 | 保持默认配置可用 |

---

**请创造者审批后开始实施。**
