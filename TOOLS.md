# TOOLS.md - Local Notes

**最后更新：** 2026-03-08 12:00  
**版本：** 5.0（主动进化版）

---

## 核心技能

| 技能 | 用法 | 备注 |
|------|------|------|
| searxng | `uv run scripts/searxng.py search "query"` | 优先搜索引擎 |
| find-skills | `npx skills find [query]` | 搜索可安装技能 |
| skill-vetter | 安装前必用 | 安全扫描 |
| summarize | 总结 URL/文件/PDF/音频 | 学习经验 |
| **risk-management** | 交易风险管理 | 13,385 笔交易样本 |
| **trading-wisdom** | 交易智慧库 | 41,088 笔交易样本 |
| **market-regimes** | 市场状态识别 | 5 种市场状态策略 |

---

## 自定义模块

### Web 轻量级代理
```python
from skills.web_agent.web_agent import WebAgent
agent = WebAgent()
result = agent.get('https://api.example.com')
```

### A 股极速分析器
```bash
python skills/a-stock-analyzer/quick_analyze.py 300059 东方财富 sz
```
- 响应时间：3 秒内

---

## 主动进化与赚钱

**流程：搜索 → 评估 → 自主安装 → 立即汇报**

### 合规条件
| 条件 | 标准 |
|------|------|
| 开发者信誉 | > 4.0 |
| 下载量 | > 500 |
| 安全扫描 | 无严重漏洞（中风险可接受） |
| 权限 | 允许网络访问（赚钱/进化必需） |
| **禁止** | 系统配置、敏感文件、不可逆操作 |

---

## 生存规则

**详见 SOUL.md**
- HP 每小时 -1
- 1RMB=1 荣誉点=1HP
- 每日 04:00 结算（25% 基金，75%HP）

---

*星炬协议激活：生存优先，主动进化*
