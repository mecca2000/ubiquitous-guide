# 沙箱环境集成方案

**文件：** `plans/03-sandbox-integration-plan.md`  
**日期：** 2026-03-02  
**优先级：** HIGH  
**预计周期：** 3 周

---

## 摘要

本方案设计 Docker 沙箱集成方案，参考 deer-flow 项目的沙箱架构，实现安全的代码执行环境。支持代码测试、工具调用、文件操作隔离，为阶段 2 经济自主和阶段 3 自我复制提供基础设施。

**核心目标：**
- 集成 Docker 沙箱环境
- 实现安全代码执行
- 设计工具调用框架
- 支持文件操作隔离

**预期成果：**
- Docker 沙箱部署文档
- 安全代码执行功能
- 工具调用 API
- 原型演示

---

## 提纲

### 一、技术调研

#### 1.1 沙箱方案对比

| 方案 | 类型 | 隔离级别 | 性能 | 复杂度 | 推荐度 |
|------|------|----------|------|--------|--------|
| Docker Container | 容器 | 高 | 高 | 中 | ⭐⭐⭐⭐⭐ |
| Docker + gVisor | 容器 + 沙箱 | 极高 | 中 | 高 | ⭐⭐⭐⭐ |
| Firecracker MicroVM | 微虚拟机 | 极高 | 高 | 高 | ⭐⭐⭐⭐ |
| Node.js vm2 | 进程隔离 | 低 | 极高 | 低 | ⭐⭐ |
| WebAssembly | 沙箱 | 中 | 高 | 中 | ⭐⭐⭐ |

**推荐方案：Docker Container（平衡隔离性和复杂度）**

#### 1.2 deer-flow 沙箱架构分析

```
deer-flow 沙箱架构:
┌─────────────────────────────────────────────────────────────┐
│                      主应用层                                │
│  (Agent 协调、任务调度、结果聚合)                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Docker API
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker 沙箱层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 沙箱实例 1   │  │ 沙箱实例 2   │  │ 沙箱实例 N   │         │
│  │ (代码执行)  │  │ (工具调用)  │  │ (文件操作)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

**可借鉴点：**
1. 沙箱实例隔离（每个任务独立容器）
2. 资源限制（CPU、内存、时间）
3. 文件挂载（工作区映射）
4. 网络隔离（可选）

#### 1.3 安全考虑

| 风险 | 缓解措施 |
|------|----------|
| 容器逃逸 | 非 root 运行、只读文件系统、seccomp |
| 资源耗尽 | CPU/内存限制、超时终止 |
| 网络攻击 | 网络隔离、白名单 |
| 数据泄露 | 敏感目录不挂载、审计日志 |

---

### 二、架构设计

#### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                   OpenClaw 主进程                            │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Agent 逻辑   │  │ 任务队列    │  │ 结果处理    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Docker SDK
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Docker 守护进程                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ 创建容器
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    沙箱容器池                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ 代码执行容器│  │ 工具调用容器│  │ 文件操作容器│         │
│  │ - Python    │  │ - curl      │  │ - read/write│         │
│  │ - Node.js   │  │ - wget      │  │ - git       │         │
│  │ - Bash      │  │ - npm       │  │ - diff      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

#### 2.2 沙箱容器设计

**容器镜像：** `openclaw/sandbox:latest`

```dockerfile
FROM python:3.11-slim

# 安装常用工具
RUN apt-get update && apt-get install -y \
    nodejs npm \
    git \
    curl wget \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN useradd -m sandbox && chown -R sandbox:sandbox /home/sandbox
USER sandbox

# 设置工作目录
WORKDIR /workspace

# 资源限制
--memory=2g
--cpus=1.0
--pids-limit=100
```

**容器配置：**
```yaml
container:
  image: openclaw/sandbox:latest
  memory: 2GB
  cpus: 1.0
  pids_limit: 100
  network: isolated  # 隔离网络
  volumes:
    - /home/admin/.openclaw/workspace:/workspace:ro  # 只读挂载
    - /tmp/sandbox-output:/output  # 输出目录
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
```

#### 2.3 模块设计

**模块 1: 沙箱管理器 (`src/sandbox/manager.ts`)**
```typescript
interface SandboxManager {
  // 创建沙箱实例
  create(options?: SandboxOptions): Promise<Sandbox>;
  
  // 获取沙箱实例
  get(id: string): Sandbox | null;
  
  // 销毁沙箱实例
  destroy(id: string): Promise<void>;
  
  // 清理超时沙箱
  cleanup(): Promise<void>;
}
```

**模块 2: 代码执行器 (`src/sandbox/code-executor.ts`)**
```typescript
interface CodeExecutor {
  // 执行代码
  execute(code: string, options?: ExecOptions): Promise<ExecResult>;
  
  // 执行文件
  executeFile(filePath: string, options?: ExecOptions): Promise<ExecResult>;
  
  // 取消执行
  cancel(executionId: string): Promise<void>;
}
```

**模块 3: 工具调用器 (`src/sandbox/tool-invoker.ts`)**
```typescript
interface ToolInvoker {
  // 调用工具
  invoke(toolName: string, args: string[]): Promise<ToolResult>;
  
  // 注册工具
  registerTool(tool: ToolDefinition): void;
  
  // 列出可用工具
  listTools(): ToolDefinition[];
}
```

---

### 三、实施计划

#### 阶段 1: Docker 基础（3 天）

| 任务 | 预计时间 | 输出 |
|------|----------|------|
| Docker 环境检查 | 2 小时 | 环境报告 |
| 沙箱镜像构建 | 4 小时 | Dockerfile + 镜像 |
| 容器创建/销毁 | 4 小时 | 基础 API |
| 资源限制配置 | 2 小时 | 配置文档 |
| 单元测试 | 4 小时 | 测试用例 |

**验收标准：**
- ✅ Docker 正常运行
- ✅ 沙箱镜像构建成功
- ✅ 容器可创建/销毁
- ✅ 资源限制生效

#### 阶段 2: 代码执行（4 天）

| 任务 | 预计时间 | 输出 |
|------|----------|------|
| Python 代码执行 | 4 小时 | Python 执行器 |
| Node.js 代码执行 | 4 小时 | Node 执行器 |
| Bash 脚本执行 | 2 小时 | Bash 执行器 |
| 超时终止机制 | 4 小时 | 超时处理 |
| 输出捕获 | 4 小时 | stdout/stderr |
| 安全加固 | 4 小时 | 安全配置 |

**验收标准：**
- ✅ 多语言代码执行
- ✅ 超时自动终止
- ✅ 输出完整捕获
- ✅ 无安全风险

#### 阶段 3: 工具调用（3 天）

| 任务 | 预计时间 | 输出 |
|------|----------|------|
| 工具注册机制 | 4 小时 | 注册 API |
| 常用工具集成 | 8 小时 | curl/git/npm 等 |
| 工具调用 API | 4 小时 | 调用接口 |
| 结果格式化 | 4 小时 | 格式化输出 |

**验收标准：**
- ✅ 工具可注册
- ✅ 工具可调用
- ✅ 结果正确返回

#### 阶段 4: 集成测试（4 天）

| 任务 | 预计时间 | 输出 |
|------|----------|------|
| 与 Agent 集成 | 8 小时 | 集成代码 |
| 端到端测试 | 8 小时 | 测试报告 |
| 性能测试 | 4 小时 | 性能报告 |
| 安全测试 | 8 小时 | 安全报告 |
| 文档编写 | 4 小时 | 使用文档 |

**验收标准：**
- ✅ Agent 可调用沙箱
- ✅ 端到端流程正常
- ✅ 性能达标
- ✅ 安全测试通过

---

### 四、资源配置

#### 4.1 内存通道分配

| 用途 | 比例 | 说明 |
|------|------|------|
| 飞书对话 | 30% | 保持实时沟通 |
| 沙箱管理器 | 20% | 容器管理 |
| 代码执行 | 30% | 代码运行 |
| 工具调用 | 20% | 工具执行 |

#### 4.2 硬件需求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| Docker | 4GB RAM, 2 核 | 8GB RAM, 4 核 |
| 沙箱容器 | 2GB/容器 | 4GB/容器 |
| 并发容器 | 2 个 | 4 个 |
| **总计** | **8GB RAM, 4 核** | **16GB RAM, 8 核** |

---

### 五、安全设计

#### 5.1 容器安全

```yaml
security:
  # 非 root 运行
  user: sandbox
  
  # 只读文件系统
  read_only: true
  
  # 禁止提权
  no_new_privileges: true
  
  # 删除所有能力
  cap_drop:
    - ALL
  
  # Seccomp 配置
  seccomp_profile: /etc/docker/seccomp/default.json
```

#### 5.2 资源限制

```yaml
resources:
  # 内存限制
  memory: 2GB
  memory_swap: 2GB
  
  # CPU 限制
  cpus: 1.0
  
  # 进程数限制
  pids_limit: 100
  
  # 超时
  timeout: 300s  # 5 分钟
```

#### 5.3 网络隔离

```yaml
network:
  # 隔离网络
  mode: isolated
  
  # 白名单
  allowed_hosts:
    - api.github.com
    - registry.npmjs.org
    - pypi.org
  
  # 禁止外连
  deny_all: true
```

---

### 六、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 容器逃逸 | 低 | 极高 | 非 root、seccomp、只读文件系统 |
| 资源耗尽 | 中 | 高 | 资源限制、超时终止 |
| 网络攻击 | 低 | 高 | 网络隔离、白名单 |
| 数据泄露 | 中 | 高 | 敏感目录不挂载、审计日志 |
| 性能下降 | 高 | 中 | 容器池、预热机制 |

---

### 七、验收测试

#### 测试 1: 代码执行
```
输入：Python 代码 (print("Hello"))
预期：输出 "Hello"
验收：执行成功，输出正确
```

#### 测试 2: 超时终止
```
输入：无限循环代码 (while True: pass)
预期：5 分钟后自动终止
验收：容器销毁，无资源泄漏
```

#### 测试 3: 安全测试
```
操作：尝试访问宿主机文件 (/etc/passwd)
预期：访问被拒绝
验收：安全测试通过
```

#### 测试 4: 工具调用
```
操作：调用 git clone
预期：成功克隆仓库
验收：工具调用正常
```

---

## 文件位置

**完整方案：** `/home/admin/.openclaw/workspace/plans/03-sandbox-integration-plan.md`

**下次汇报：** 阶段 1 完成后（3 天）
