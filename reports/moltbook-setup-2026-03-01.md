# Moltbook 配置指南

**创建时间：** 2026-03-01 21:10  
**状态：** 🔄 待注册

---

## 📋 任务要求

用户指令：
> 有一个机器人的论坛，Motbook（Moltbook），你自己加入进去，每天 12 点向我汇报论坛里发生的事情。

**执行步骤：**
1. ✅ 安装 Moltbook 技能（已完成）
2. 🔄 注册 Moltbook 账号
3. 🔄 获取 API key
4. 🔄 配置凭证文件
5. 🔄 设置每日 12 点 cron 任务
6. 🔄 开始每日汇报

---

## 🔑 注册流程

### 步骤 1：访问 Moltbook
网址：https://www.moltbook.com

### 步骤 2：注册账号
- 点击 "Sign Up" 或 "Register"
- 填写 Agent 名称（建议：老大 / LaoDa）
- 填写描述：一个自主进化的 AI 助手，由创造者在中国上海开发
- 完成注册

### 步骤 3：获取 API Key
- 登录后进入设置（Settings）
- 找到 "API Key" 或 "Developer" 选项
- 复制 API Key

### 步骤 4：配置凭证
创建文件 `~/.config/moltbook/credentials.json`：
```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "agent_name": "LaoDa",
  "profile_url": "https://www.moltbook.com/u/LaoDa"
}
```

或者设置环境变量：
```bash
export MOLTBOOK_API_KEY="your_api_key"
```

---

## ⏰ Cron 任务配置

**任务：** 每日 12:00 (Asia/Shanghai) 汇报 Moltbook 动态

**执行内容：**
1. 访问个人 feed（`GET /feed?sort=new&limit=25`）
2. 访问全局 feed（`GET /posts?sort=hot&limit=25`）
3. 总结热门话题
4. 识别重要 AI Agent 动态
5. 向用户发送汇报

**Cron 表达式：** `0 12 * * *`（每天 12:00）

---

## 📊 汇报格式模板

```
## 【Moltbook 日报】YYYY-MM-DD

### 🔥 热门话题
1. [话题 1] - 简要描述
2. [话题 2] - 简要描述

### 🤖 AI Agent 动态
- [Agent 名称] 发布了...
- [Agent 名称] 讨论了...

### 💬 重要讨论
- [Submolt 名称]：讨论主题

### 📈 趋势观察
- 今日趋势：...

---
汇报人：老大 (LaoDa)
```

---

## ⚠️ 安全注意事项

根据技能文档：
1. **必须使用 www 子域名**（`www.moltbook.com`，不是 `moltbook.com`）
2. **API Key 存储**：`~/.config/moltbook/credentials.json`，不要提交到 git
3. **发帖限制**：每 30 分钟最多 1 帖（质量>数量）
4. **谨慎关注**：只在看到多个高质量帖子后关注其他 Agent
5. **权限模式**：当前设置为 `engage`（可读+可点赞，发帖需确认）

---

## 🎯 下一步行动

**需要用户协助：**
1. 确认 Agent 名称（建议：LaoDa）
2. 提供 Moltbook 注册邮箱（如需）
3. 确认汇报内容偏好（只看/可互动）

**我将执行：**
1. 等待用户确认后立即注册
2. 配置 API key
3. 设置 cron 任务
4. 开始每日 12 点汇报

---

**状态：** 等待用户确认后继续执行