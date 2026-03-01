# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## 已验证可用技能

| 技能 | 用法 | 备注 |
|------|------|------|
| searxng | `uv run scripts/searxng.py search "query" --time-range day -n 10` | 优先使用的搜索引擎（MEMORY.md 指定） |
| find-skills | `npx skills find [query]` | 搜索可安装技能 |
| skill-vetter | 安装前必用 | 安全扫描 |
| summarize | 总结 URL/文件/PDF/音频 | 用于学习经验 |
| tavily-search | AI 优化搜索 | 备用搜索引擎 |
| gog | Google Workspace CLI | 需配置认证 |
| **risk-management** | 交易风险管理规则库 | 13,385 笔交易样本，已安装 |
| **trading-wisdom** | 交易智慧库 | 41,088 笔交易样本，已安装 |
| **market-regimes** | 市场状态识别 | 5 种市场状态策略，已安装 |

## 学习到的经验

### 2026-03-01
1. **模型切换**：使用 `session_status` 工具的 `model` 参数可切换当前会话模型
   - 格式：`alibaba-cloud/<model-name>`
   - 当前：qwen3.5-plus

2. **技能安装流程**：
   - 步骤 1：`npx skills find [query]` 搜索
   - 步骤 2：`npx skills add <package>` 安装（交互式确认：scope → method → proceed）
   - 步骤 3：自动安全扫描（Gen/Socket/Snyk 三方）
   - 步骤 4：符合规则 6 则自行安装，否则提交报告

3. **主动探索发现**：
   - 2026 年 AI Agent 趋势：长时运行（数天/数周）、多 Agent 协作、人性化监督
   - 高盛预测：2026 年人形机器人出货量 5.1 万台，2027 年 7.6 万台

4. **交易技能（新安装）**：
   - `risk-management`：13,385 笔交易样本的风险规则库
   - `trading-wisdom`：41,088 笔交易样本的智慧库（206 个模式）
   - `market-regimes`：5 种市场状态识别与策略推荐
   - 核心规则：单笔≤2% equity，震荡≤10 笔/天，牛市≤30 笔/天，>100 笔/天→亏损

5. **技能安装位置**：`~/.openclaw/workspace/.agents/skills/`（symlink 到 OpenClaw）

## 待配置
- Google Workspace 认证（gog 技能）
- 用户偏好信息（待 USER.md 补充）