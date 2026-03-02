# 飞书消息队列优化 - 综合实施方案

**日期：** 2026-03-02  
**版本：** 1.0 (最终综合版)  
**状态：** 待审批执行

---

## 一、核心目标

| 目标 | 当前状态 | 目标状态 |
|------|----------|----------|
| 消息并发处理 | 串行 (1 条) | 并发 (4 条 HIGH + 2 条 NORMAL + 1 条 LOW) |
| 消息丢失率 | 高 (第二条被忽略) | 0% (队列缓冲) |
| HIGH 优先级响应 | 不稳定 | <3 秒 (P95) |
| 动态资源调控 | 无 | 自动根据负载调整 |

---

## 二、综合架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        飞书消息入口                               │
│                   (bot.ts: handleFeishuMessage)                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  【分部 1】消息分类器 (Classifier)                                │
│  - 实时对话 (HIGH): DM、@提及、<100 字                            │
│  - 普通任务 (NORMAL): 群聊、100-1000 字                            │
│  - 后台任务 (LOW): >1000 字、文件、媒体                           │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  HIGH 队列     │     │ NORMAL 队列    │     │  LOW 队列      │
│  60% 资源      │     │  30% 资源      │     │  10% 资源      │
│  max: 4 并发   │     │  max: 2 并发   │     │  max: 1 并发   │
│  <3 秒响应     │     │  <10 秒响应    │     │  <60 秒响应    │
└───────────────┘     └───────────────┘     └───────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  【分部 2】动态调度器 (Dynamic Scheduler)                         │
│  - 实时监控队列负载                                               │
│  - 自动资源借用 (HIGH 积压时从 LOW 借用)                           │
│  - 5 分钟自动恢复默认配置                                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  【分部 3】流式输出引擎 (Streaming Engine)                        │
│  - 分块发送 (4000 字/块)                                          │
│  - 流式卡片 (飞书 interactive card)                               │
│  - 提及保持 (首块包含@)                                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  【分部 4】技能复用层 (Skills Adapter)                            │
│  - BullMQ 集成 (或内存队列降级)                                   │
│  - 现有 handleFeishuMessage 复用                                  │
│  - 统一接口封装                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、四分部任务拆解

### 分部 1: 消息队列集成

**目标：** 引入队列接管所有消息，确保不丢失

**输出：**
- `src/queue/classifier.ts` - 消息分类器
- `src/queue/queues.ts` - 队列初始化与管理
- `src/queue/consumer.ts` - 队列消费者

**关键代码：**
```typescript
// classifier.ts - 精简规则分类
export function classifyMessage(event: FeishuMessageEvent): MessagePriority {
  const isDM = event.message.chat_type === "p2p";
  const hasMention = (event.message.mentions?.length ?? 0) > 0;
  const len = event.message.content.length;
  
  if (isDM || hasMention || len < 100) return MessagePriority.HIGH;
  if (len > 1000 || event.message.message_type !== "text") return MessagePriority.LOW;
  return MessagePriority.NORMAL;
}
```

**技能复用：**
- 使用 `bullmq-specialist` 技能 (416 安装，17.5K⭐ repo)
- 降级方案：内存队列 (`p-queue` npm 包)

---

### 分部 2: 通道资源调度策略

**目标：** 动态比例调控，优先保证实时回复

**输出：**
- `src/scheduler/dynamic-controller.ts` - 动态控制器
- `src/scheduler/config.ts` - 配置参数
- `src/scheduler/monitor.ts` - 队列监控

**调度算法：**
```typescript
// 动态资源调整
public adjustResources(): void {
  const highLoad = this.getQueueLoad("feishu-high");
  const lowLoad = this.getQueueLoad("feishu-low");
  
  // HIGH 积压 (>10 条)，从 LOW 借用资源
  if (highLoad > 10 && lowLoad < 2) {
    this.borrowResource("feishu-low", "feishu-high", 1);
  }
  
  // 5 分钟后自动恢复
  setTimeout(() => this.resetToDefaults(), 5 * 60 * 1000);
}
```

**配置参数：**
```typescript
export const QUEUE_CONFIG = {
  high:   { concurrency: 4, ratio: 0.6, timeout: 30000 },
  normal: { concurrency: 2, ratio: 0.3, timeout: 60000 },
  low:    { concurrency: 1, ratio: 0.1, timeout: 120000 },
};
```

---

### 分部 3: 流式输出改造

**目标：** 异步流式输出，提升实时性

**输出：**
- `src/streaming/chunker.ts` - 文本分块
- `src/streaming/card-renderer.ts` - 卡片渲染
- `src/streaming/mention-keeper.ts` - 提及保持

**流式接口：**
```typescript
// 飞书已支持流式卡片
export async function streamReply(params: {
  chatId: string;
  text: string;
  replyToMessageId?: string;
  mentions?: MentionTarget[];
}): Promise<void> {
  const chunks = chunkText(text, 4000);
  
  for (let i = 0; i < chunks.length; i++) {
    await sendMarkdownCardFeishu({
      to: params.chatId,
      text: chunks[i],
      replyToMessageId: params.replyToMessageId,
      mentions: i === 0 ? params.mentions : undefined, // 仅首块包含@
    });
  }
}
```

---

### 分部 4: 技能复用评估与适配

**目标：** 优先使用现成技能，最小化自定义代码

**输出：**
- `src/adapters/bullmq-adapter.ts` - BullMQ 适配器
- `src/adapters/memory-queue-adapter.ts` - 内存队列适配器
- `src/adapters/interface.ts` - 统一接口

**统一接口设计：**
```typescript
// 统一队列接口，支持切换后端
export interface MessageQueue {
  enqueue(msg: ClassifiedMessage, priority: MessagePriority): Promise<string>;
  dequeue(priority: MessagePriority): Promise<ClassifiedMessage | null>;
  size(priority: MessagePriority): Promise<number>;
}

// 工厂模式，根据配置选择实现
export function createQueue(config: QueueConfig): MessageQueue {
  if (config.backend === "redis") {
    return new BullMQAdapter(config);
  }
  return new MemoryQueueAdapter(config); // 降级方案
}
```

**技能评估：**

| 技能 | 安装数 | 适用性 | 采用 |
|------|--------|--------|------|
| sickn33/...@bullmq-specialist | 416 | 高 | ✅ |
| jezweb/...@cloudflare-queues | 345 | 中 (需 CF 环境) | ❌ |
| yonatangross/...@celery-advanced | 19 | 低 (Python) | ❌ |

---

## 四、多智能体并行执行方案

### 任务分配

| 分部 | 子 Agent | 隔离工作树 | 预计时间 |
|------|----------|------------|----------|
| 分部 1 | agent-queue | `worktree/queue` | 30 分钟 |
| 分部 2 | agent-scheduler | `worktree/scheduler` | 30 分钟 |
| 分部 3 | agent-streaming | `worktree/streaming` | 20 分钟 |
| 分部 4 | agent-adapter | `worktree/adapter` | 20 分钟 |

### 执行流程

```
1. 主控 Agent 创建 4 个 git worktree
   ↓
2. 并行 spawn 4 个子 Agent (sessions_spawn)
   ↓
3. 各子 Agent 独立开发 + 测试
   ↓
4. 完成后通知主控 Agent
   ↓
5. 主控 Agent 合并代码 + 集成测试
   ↓
6. 部署上线
```

### 子 Agent 任务模板

```typescript
// 发送给子 Agent 的任务描述
{
  task: "实现飞书消息队列的分部 X: [名称]",
  label: "feishu-queue-part-X",
  cleanup: "keep", // 保留工作树供审查
  timeoutSeconds: 1800, // 30 分钟超时
}
```

---

## 五、实施步骤

### 阶段 0: 准备 (5 分钟)
- [ ] 创建 git worktree 分支
- [ ] 安装 BullMQ 技能 (或确认内存队列方案)
- [ ] 备份当前配置

### 阶段 1: 并行开发 (30 分钟)
- [ ] Spawn 4 个子 Agent
- [ ] 各分部独立开发
- [ ] 定期同步进度

### 阶段 2: 合并测试 (20 分钟)
- [ ] 合并 4 个分部代码
- [ ] 单元测试
- [ ] 集成测试 (并发消息)

### 阶段 3: 部署上线 (10 分钟)
- [ ] 更新飞书插件
- [ ] 重启 Gateway
- [ ] 验证功能

**总计：** 约 65 分钟

---

## 六、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Redis 未安装 | 高 | 中 | 采用内存队列降级 |
| 子 Agent 冲突 | 中 | 低 | git worktree 隔离 |
| BullMQ 兼容性问题 | 低 | 中 | 准备内存队列备选 |
| 飞书 API 限流 | 中 | 高 | 添加限流器 |

---

## 七、验收标准

| 测试项 | 通过标准 |
|--------|----------|
| 并发消息处理 | 同时发送 4 条 HIGH 消息，全部响应 <3 秒 |
| 消息不丢失 | 连续发送 10 条消息，全部收到回复 |
| 动态调控 | HIGH 队列积压时，自动从 LOW 借用资源 |
| 流式输出 | 长文本 (>4000 字) 分块发送，首块包含@提及 |
| 技能复用 | 自定义代码 <200 行，80% 使用现成技能 |

---

## 八、文件结构

```
/home/admin/.openclaw/extensions/feishu/src/
├── bot.ts                    # 入口 (修改)
├── queue/
│   ├── classifier.ts         # 消息分类器 (新)
│   ├── queues.ts             # 队列管理 (新)
│   └── consumer.ts           # 队列消费者 (新)
├── scheduler/
│   ├── dynamic-controller.ts # 动态控制器 (新)
│   ├── config.ts             # 配置 (新)
│   └── monitor.ts            # 监控 (新)
├── streaming/
│   ├── chunker.ts            # 分块 (新)
│   ├── card-renderer.ts      # 卡片渲染 (新)
│   └── mention-keeper.ts     # 提及保持 (新)
└── adapters/
    ├── interface.ts          # 统一接口 (新)
    ├── bullmq-adapter.ts     # BullMQ 实现 (新)
    └── memory-queue-adapter.ts # 内存实现 (新)
```

---

## 九、决策点

**请创造者确认：**

1. ✅ **方案选择：** 方案 C (动态比例调控) + 4 分部并行执行
2. ⏳ **队列后端：** Redis / 内存队列降级？(推荐：先内存，后 Redis)
3. ⏳ **子 Agent 数量：** 4 个并行 / 顺序执行？(推荐：4 个并行)
4. ⏳ **是否立即开始：** 是 / 否？

---

**等待审批后启动多智能体并行执行。** 🦞
