# 心跳机制问题分析报告

## 问题确认
心跳机制确实存在异常，主要原因是 **Gateway 认证令牌不匹配** 导致 cron 系统无法正常工作。

## 根本原因分析

### 1. Gateway Token 配置问题
- **配置文件**: `/home/admin/.openclaw/openclaw.json`
- **当前设置**: 
  ```json
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "06d61b1adf6ff8da62f95f8d22c25d1e"
    }
  }
  ```
- **问题**: CLI 工具无法自动读取配置文件中的 token，需要手动设置环境变量

### 2. Cron 系统依赖 Gateway
- 所有定时任务（包括心跳机制）都通过 Gateway 的 cron 服务管理
- Gateway 连接失败 → cron 服务不可用 → 心跳任务无法执行

### 3. 日志证据
从 systemd 日志可以看到重复的错误：
```
[ws] unauthorized conn=... reason=token_mismatch
gateway connect failed: Error: unauthorized: gateway token mismatch
[tools] cron failed: gateway closed (1008): unauthorized: gateway token mismatch
```

## 影响范围
- ❌ **心跳任务完全停止**: 每15分钟的主动探索任务无法执行
- ❌ **定时任务失效**: 每日/每周的自动化任务无法运行  
- ❌ **Proactive Agent 功能受限**: 虽然技能已安装，但依赖的 cron 系统无法工作

## 解决方案

### 立即修复（临时）
```bash
# 设置环境变量后重新启动 Gateway
export GATEWAY_TOKEN="06d61b1adf6ff8da62f95f8d22c25d1e"
openclaw gateway restart
```

### 永久修复（推荐）
在 OpenClaw 配置中添加 `gateway.remote.token` 字段：

```json
"gateway": {
  "auth": {
    "mode": "token",
    "token": "06d61b1adf6ff8da62f95f8d22c25d1e"
  },
  "remote": {
    "token": "06d61b1adf6ff8da62f95f8d22c25d1e"
  }
}
```

### 验证步骤
1. 应用配置修复
2. 重启 Gateway 服务
3. 运行 `openclaw gateway status` 确认连接正常
4. 运行 `cron list` 确认定时任务可见
5. 等待下一个心跳周期（15分钟）验证自动执行

## 当前状态总结
- **心跳机制状态**: ❌ 停止（由于 Gateway 认证问题）
- **根本原因**: Gateway token 配置不完整
- **修复难度**: ⭐⭐ 简单（配置文件修改）
- **预计恢复时间**: 5分钟（应用修复后）

## 建议行动
立即应用永久修复方案，确保心跳机制和所有定时任务恢复正常运行。