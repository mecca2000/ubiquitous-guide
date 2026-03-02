#!/bin/bash
# 启动自主进化指令
# 设置 proactive-agent 的 cron 任务，实现主动汇报

echo "🦞 启动自主进化指令..."

# 检查 gateway 状态
echo "检查 Gateway 状态..."
openclaw gateway status

# 创建 cron 配置文件
cat > /tmp/proactive-cron.json << 'EOF'
{
  "name": "proactive-heartbeat",
  "schedule": {
    "kind": "every",
    "everyMs": 1800000
  },
  "payload": {
    "kind": "agentTurn",
    "message": "【心跳检查】执行主动汇报任务：\n1. 检查 SESSION-STATE.md 更新\n2. 扫描 proactive-tracker.md\n3. 执行 HEARTBEAT.md 任务清单\n4. 生成状态报告"
  },
  "sessionTarget": "isolated",
  "enabled": true
}
EOF

echo "✅ cron 配置已生成"
echo ""
echo "请手动执行以下命令添加 cron 任务："
echo "  cron action=add job=@/tmp/proactive-cron.json"
echo ""
echo "或者在 openclaw 配置文件中添加。"
