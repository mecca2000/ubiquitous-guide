# 飞书消息队列优化方案

**日期：** 2026-03-02  
**创建者：** 老大  
**状态：** 待审批

---

## 问题分析

### 当前状况

1. **串行处理问题**
   - 飞书插件的消息处理是串行的
   - 当机器人正在处理一条消息时，第二条消息被忽略或没有响应
   - 原因：`core.system.enqueueSystemEvent` 入队后没有队列缓冲机制

2. **配置缺失**
   ```json
   "messages": {
     "ackReactionScope": "all",
     "queue": {}  // 空的，未配置
   }
   ```

3. **并发能力未充分利用**
   - Agent 配置了 `maxConcurrent: 4`（可同时处理 4 个会话）
   - 但消息入队是串行的，导致并发能力浪费

---

## 解决方案

### 方案 A：配置层优化（推荐先实施）

在 `openclaw.json` 中配置消息队列参数：

```json
{
  "messages": {
    "ackReactionScope": "all",
    "queue": {
      "maxSize": 100,
      "maxConcurrent": 4,
      "timeoutMs": 30000,
      "retryAttempts": 3
    }
  },
  "agents": {
    "defaults": {
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      }
    }
  }
}
```

**参数说明：**
- `maxSize`: 队列最大容量（防止内存溢出）
- `maxConcurrent`: 最大并发处理数（与 Agent 并发能力匹配）
- `timeoutMs`: 消息处理超时时间
- `retryAttempts`: 失败重试次数

### 方案 B：插件层优化（飞书插件实现消息队列）

参考 QQbot 的实现，在飞书插件中增加消息队列层：

```typescript
// 消息队列配置
const MESSAGE_QUEUE_SIZE = 100;
const MESSAGE_QUEUE_CONCURRENCY = 4;

interface QueuedFeishuMessage {
  type: "dm" | "group";
  senderId: string;
  senderName?: string;
  content: string;
  messageId: string;
  chatId: string;
  timestamp: number;
  accountId?: string;
}

// 消息队列
const messageQueue: QueuedFeishuMessage[] = [];
let messageProcessorRunning = false;

// 入队函数（非阻塞）
const enqueueMessage = (msg: QueuedFeishuMessage): void => {
  if (messageQueue.length >= MESSAGE_QUEUE_SIZE) {
    // 队列满了，丢弃最旧的消息
    const dropped = messageQueue.shift();
    log?.error(`[feishu] Message queue full, dropping oldest message from ${dropped?.senderId}`);
  }
  messageQueue.push(msg);
  log?.debug?.(`[feishu] Message enqueued, queue size: ${messageQueue.length}`);
  
  // 启动处理循环（如果未运行）
  if (!messageProcessorRunning) {
    startMessageProcessor();
  }
};

// 消息处理循环（独立并发）
const startMessageProcessor = (): void => {
  if (messageProcessorRunning) return;
  messageProcessorRunning = true;

  const processLoop = async () => {
    // 并发处理：同时处理 maxConcurrent 条消息
    const processingPromises: Promise<void>[] = [];
    
    while (!isAborted && messageQueue.length > 0) {
      // 控制并发数
      if (processingPromises.length >= MESSAGE_QUEUE_CONCURRENCY) {
        await Promise.race(processingPromises);
        // 移除已完成的 promise
        const completed = processingPromises.filter(p => 
          // 检查是否已完成（简化处理）
          false
        );
        processingPromises.splice(0, completed.length);
      }
      
      const msg = messageQueue.shift()!;
      const promise = handleMessageFn(msg).catch(err => {
        log?.error(`[feishu] Message processor error: ${err}`);
      });
      processingPromises.push(promise);
    }
    
    // 等待所有处理完成
    await Promise.all(processingPromises);
    messageProcessorRunning = false;
  };

  processLoop().catch(err => {
    log?.error(`[feishu] Message processor crashed: ${err}`);
    messageProcessorRunning = false;
  });
};
```

### 方案 C：动态比例调控（实时回复 vs 异步任务）

实现消息优先级分类：

```typescript
enum MessagePriority {
  HIGH = "high",      // 实时回复（用户直接对话）
  NORMAL = "normal",  // 普通任务
  LOW = "low"         // 后台异步任务
}

interface PrioritizedMessage {
  priority: MessagePriority;
  message: QueuedFeishuMessage;
  enqueuedAt: number;
}

// 优先级队列（高优先级优先处理）
const priorityQueue = {
  high: [],
  normal: [],
  low: []
};

// 动态比例调控
const PROCESSING_RATIO = {
  high: 0.6,    // 60% 资源处理高优先级
  normal: 0.3,  // 30% 资源处理普通任务
  low: 0.1      // 10% 资源处理后台任务
};
```

---

## 实施步骤

### 第一步：配置层优化（立即实施）

1. 修改 `openclaw.json` 的 `messages.queue` 配置
2. 重启 Gateway 使配置生效
3. 测试并发消息处理

### 第二步：插件层优化（如需更深入控制）

1. 修改 `/home/admin/.openclaw/extensions/feishu/src/bot.ts`
2. 增加消息队列层（参考 QQbot 实现）
3. 实现并发处理循环
4. 测试并验证

### 第三步：动态比例调控（高级功能）

1. 实现消息优先级分类
2. 实现动态资源分配
3. 监控队列状态并自动调整

---

## 预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| 并发处理能力 | 1（串行） | 4（并发） |
| 消息丢失率 | 高（第二条被忽略） | 0%（队列缓冲） |
| 响应延迟 | 不稳定 | <3 秒（P95） |
| 队列容量 | 0 | 100 条 |

---

## 风险与缓解

| 风险 | 缓解措施 |
|------|----------|
| 内存溢出 | 设置队列上限（100 条），超限丢弃最旧 |
| 消息乱序 | 同一会话的消息保持顺序（会话级队列） |
| 配置错误 | 先备份配置，支持快速回滚 |

---

## 建议

**推荐实施方案 A + B 组合：**

1. **立即实施**：配置层优化（5 分钟，无代码改动）
2. **短期实施**：插件层优化（30 分钟，参考 QQbot 实现）
3. **长期优化**：动态比例调控（按需实施）

---

## 附录：QQbot 参考实现

QQbot 已成功实现消息队列，关键代码位置：
- `/home/admin/.openclaw/extensions/qqbot/src/gateway.ts`
- 消息队列大小：1000 条
- 告警阈值：800 条
- 并发处理：独立消息处理循环

---

**请创造者审批后执行。**
