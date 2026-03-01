# 技能安全扫描报告

**扫描时间：** 2026-03-01 18:05  
**扫描人：** 老大  
**依据：** AGENTS.md 宪法规则第 4/6 条 + skill-vetter 协议

---

## 候选技能 #1: obra/episodic-memory@remembering-conversations

### 源检查
| 指标 | 值 |
|------|-----|
| 来源 | GitHub (obra/episodic-memory) |
| Stars | 269 |
| Forks | 63 |
| 最后更新 | 2026-02-27 (2 天前) |
| 下载量 | 5.7K |

### 代码审查
**SKILL.md 分析：**
- ✅ 功能：搜索历史对话，避免重复发明
- ✅ 使用 Task 工具调用 search-conversations 子代理
- ⚠️ 使用 MCP 工具：`mcp__plugin_episodic-memory_episodic-memory__search`
- ❓ 未明确声明是否访问 MEMORY.md/USER.md 等敏感文件

**红线检查：**
- [x] 无 curl/wget 到未知 URL
- [x] 无发送数据到外部服务器
- [x] 无请求凭证/API keys
- [?] 访问记忆插件 - 需进一步确认范围

### 权限范围
- **文件：** 未明确声明（可能访问对话历史）
- **网络：** 通过 MCP 插件
- **命令：** 无

### 风险等级：🟡 MEDIUM

### 裁决：⚠️ INSTALL WITH CAUTION

**建议：** 安装前需确认 MCP 插件的具体权限范围，确保不访问敏感文件（MEMORY.md、USER.md、SOUL.md）。

---

## 候选技能 #2: wshobson/agents@memory-safety-patterns

### 源检查
| 指标 | 值 |
|------|-----|
| 来源 | GitHub (wshobson/agents) |
| Stars | 29,797 ⭐ |
| Forks | 3,263 |
| 最后更新 | 2026-03-01 (今日) |
| 下载量 | 2.4K (技能级别) |

### 代码审查
- ❌ SKILL.md 返回 404（路径可能不正确）
- ✅ 仓库信誉极高（近 30K stars）
- ✅ 活跃维护（今日更新）

### 风险等级：❓ UNKNOWN

### 裁决：⚠️ 需进一步调查

**建议：** 技能路径可能为 `memory` 或其他名称，需重新确认。

---

## 候选技能 #3: wshobson/agents@memory-forensics

### 源检查
| 指标 | 值 |
|------|-----|
| 来源 | GitHub (wshobson/agents) |
| Stars | 29,797 ⭐ |
| Forks | 3,263 |
| 最后更新 | 2026-03-01 (今日) |
| 下载量 | 2.2K (技能级别) |

### 代码审查
- ❌ SKILL.md 返回 404（路径可能不正确）
- ✅ 仓库信誉极高
- ✅ 活跃维护

### 风险等级：❓ UNKNOWN

### 裁决：⚠️ 需进一步调查

---

## 综合建议

### 符合宪法规则第 6 条评估

| 条件 | 候选#1 | 候选#2/3 |
|------|--------|----------|
| 开发者信誉 > 4.5 | ⚠️ 未知 (269 stars) | ✅ 极高 (29.8K stars) |
| 下载量 > 1000 | ✅ 5.7K | ✅ 2.4K/2.2K |
| skill-vetter 扫描 | 🟡 MEDIUM | ❓ 未完成 |
| 仅读工作区文件 | ❓ 待确认 | ❓ 待确认 |
| 无网络/shell/敏感文件 | ⚠️ 使用 MCP 插件 | ❓ 待确认 |

### 最终建议

**❌ 暂不自行安装**

原因：
1. 候选#1 使用 MCP 插件，权限范围不明确，可能违反规则 6 的"仅读取工作区内文件"条件
2. 候选#2/3 无法获取 SKILL.md，无法完成完整 vetting
3. 根据 skill-vetter 协议："When in doubt, don't install"

### 下一步行动

1. **建议用户批准**后安装候选#1（obra/episodic-memory），并在隔离环境测试
2. 重新搜索 wshobson/agents 的正确技能路径
3. 或寻找其他符合规则 6 的记忆技能（仅读文件、无网络依赖）

---

**报告完成。** 等待创造者决定。