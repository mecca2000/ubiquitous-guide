# 专业交易员方向技能报告

**扫描时间：** 2026-03-01 18:35  
**扫描人：** 老大  
**方向：** 专业交易员能力建设

---

## 📊 技能生态扫描总览

| 类别 | 扫描技能数 | 高下载量候选 (>1K) | 最高下载量 |
|------|-----------|-------------------|-----------|
| **trading** | 6 | 2 | 1.6K |
| **finance** | 6 | 2 | 1.6K |
| **crypto** | 6 | 2 | 534 |
| **stock** | 6 | 2 | 2.4K |
| **analysis** | 6 | 6 | 2.4K |
| **data** | 6 | 6 | 9.2K |
| **chart** | 6 | 1 | 2.3K |

---

## 🏆 核心交易技能候选

### 1️⃣ 风险管理类

| 技能 | 下载量 | 开发者 | 核心能力 | 风险等级 |
|------|--------|--------|----------|----------|
| **0xhubed/agent-trading-arena@risk-management** | 613 | 0xhubed | 基于 13,385 笔交易样本的风险规则库 | 🟢 LOW |

**核心规则摘录：**
- ✅ 单笔交易风险不超过 equity 的 2%
- ✅ 每笔交易必须设置止损
- ✅ 高波动 regime 降低仓位
- ✅ 不向亏损仓位加仓
- ✅ 震荡市场：24 小时内最多 0-10 笔交易
- ✅ 温和牛市：24 小时内最多 0-30 笔交易
- ✅ 超过 100 笔交易/天与亏损相关 (-$50 to -$264)

**置信度：** 60-99%（基于历史交易数据）

---

### 2️⃣ 股票分析类

| 技能 | 下载量 | 开发者 | 核心能力 | 风险等级 |
|------|--------|--------|----------|----------|
| **gracefullight/stock-checker@stock-analysis** | 2.4K | gracefullight | 股票基本面/技术面分析 | 🟡 MEDIUM |
| **sugarforever/01coder-agent-skills@china-stock-analysis** | 1.5K | sugarforever | A 股/港股分析 | 🟡 MEDIUM |

**预期功能：**
- Yahoo Finance 数据获取
- 财务报表分析
- 技术指标计算
- 估值模型

---

### 3️⃣ 交易策略类

| 技能 | 下载量 | 开发者 | 核心能力 | 风险等级 |
|------|--------|--------|----------|----------|
| **jeremylongshore/...@backtesting-trading-strategies** | 1.6K | jeremylongshore | 策略回测 | 🟡 MEDIUM |
| **jamesrochabrun/skills@trading-plan-generator** | 388 | jamesrochabrun | 交易计划生成 | 🟢 LOW |
| **0xhubed/agent-trading-arena@trading-wisdom** | 350 | 0xhubed | 交易智慧库 | 🟢 LOW |
| **0xhubed/agent-trading-arena@market-regimes** | 311 | 0xhubed | 市场状态识别 | 🟢 LOW |

---

### 4️⃣ 数据分析与可视化

| 技能 | 下载量 | 开发者 | 核心能力 | 风险等级 |
|------|--------|--------|----------|----------|
| **inference-sh-9/skills@data-visualization** | 4.3K | inference-sh-9 | 数据可视化 | 🟡 MEDIUM |
| **wshobson/agents@data-storytelling** | 2.8K | wshobson (29.8K★) | 数据叙事 | 🟢 LOW |
| **expo/skills@native-data-fetching** | 9.2K | Expo | 数据获取 | 🟢 LOW |

---

### 5️⃣ 通用分析能力

| 技能 | 下载量 | 开发者 | 核心能力 | 风险等级 |
|------|--------|--------|----------|----------|
| **wshobson/agents@market-sizing-analysis** | 2.3K | wshobson (29.8K★) | 市场规模分析 | 🟢 LOW |
| **supercent-io/skills-template@data-analysis** | 1.7K | supercent-io | 数据分析 | 🟢 LOW |

---

## 🎯 推荐安装优先级

### 第一阶段：基础能力（立即安装候选）

| 优先级 | 技能 | 理由 | 规则 6 符合性 |
|--------|------|------|--------------|
| **P0** | 0xhubed/agent-trading-arena@risk-management | 交易核心能力，基于真实数据 | ✅ 高概率符合 |
| **P0** | 0xhubed/agent-trading-arena@trading-wisdom | 交易决策辅助 | ✅ 高概率符合 |
| **P0** | 0xhubed/agent-trading-arena@market-regimes | 市场状态识别 | ✅ 高概率符合 |
| **P1** | wshobson/agents@data-storytelling | 数据呈现能力，高信誉开发者 | ✅ 高概率符合 |
| **P1** | wshobson/agents@market-sizing-analysis | 市场分析能力，高信誉开发者 | ✅ 高概率符合 |

### 第二阶段：进阶能力（需 vetting 后决定）

| 优先级 | 技能 | 理由 | 注意事项 |
|--------|------|------|----------|
| **P2** | gracefullight/stock-checker@stock-analysis | 股票分析核心 | 需确认是否访问外部 API |
| **P2** | inference-sh-9/skills@data-visualization | 图表生成 | 需确认依赖项 |
| **P3** | jeremylongshore/...@backtesting-trading-strategies | 策略回测 | 需确认数据源和计算权限 |

---

## ⚠️ 风险评估

### 红线检查（基于 skill-vetter 协议）

| 风险类型 | 交易技能特有风险 | 缓解措施 |
|----------|-----------------|----------|
| **外部 API 依赖** | Yahoo Finance、Tushare 等 | 确认 API key 管理方式 |
| **实时数据请求** | 市场价格获取 | 评估频率限制和成本 |
| **交易执行权限** | 下单/平仓操作 | ❌ 禁止自动交易，仅分析 |
| **凭证存储** | 交易所 API keys | 仅读取环境变量，不写入文件 |

### 建议安全边界

1. **只读模式**：所有交易技能仅限分析/回测，禁止实盘交易
2. **数据隔离**：交易数据存储在独立目录 (`~/master/trading/`)
3. **人工确认**：任何交易建议需用户确认后方可执行
4. **审计日志**：所有分析操作记录至 `memory/trading-logs/`

---

## 📋 下一步行动

### 立即执行（等待用户批准）
1. 对 P0 优先级技能执行完整 skill-vetter 扫描
2. 创建交易专用目录结构 (`~/master/trading/`)
3. 初始化交易日志系统

### 待用户决定
- 是否授权安装 0xhubed/agent-trading-arena 系列技能（3 个）
- 是否授权安装 wshobson/agents 分析技能（2 个）
- 交易数据边界确认（仅分析 vs 允许模拟交易）

---

**报告完成。** 等待创造者指令。