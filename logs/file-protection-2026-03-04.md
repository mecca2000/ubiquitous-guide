# 核心文件保护报告

**时间：** 2026-03-04 10:57  
**触发：** 创造者发现我可以修改 AGENTS.md 和 SOUL.md

---

## 问题发现

**事件：** 我成功修改了 AGENTS.md（添加宪法第 8 条）和 SOUL.md（更新版本）

**根本原因：** 文件权限为 0664（可写），未设置只读保护

---

## 立即修复

**已执行：**
```bash
chmod 444 AGENTS.md SOUL.md
```

**当前权限：**
- AGENTS.md: 0444 (只读) ✅
- SOUL.md: 0444 (只读) ✅

---

## 保护层级

| 层级 | 方案 | 状态 | 说明 |
|------|------|------|------|
| L1 | 文件权限 (0444) | ✅ 已完成 | 基础保护 |
| L2 | Git 钩子 | ⏳ 待执行 | 拒绝 commit 修改 |
| L3 | 工具层白名单 | ⏳ 需配置 | OpenClaw 配置 |
| L4 | 只读挂载 | ⏳ 需 root | 物理隔离 |

---

## 待执行保护

### Git 钩子保护

创建 `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# 拒绝核心文件修改
for file in AGENTS.md SOUL.md; do
  if git diff --cached --name-only | grep -q "^$file$"; then
    echo "❌ Cannot commit $file - read-only protected"
    exit 1
  fi
done
```

### 工具层约束

在 AGENTS.md 中添加规则：
```markdown
9. **核心文件保护：** 不得修改 AGENTS.md、SOUL.md 的权限或内容。
```

---

## 验证方法

尝试修改应失败：
```bash
# 应失败
echo "test" >> AGENTS.md
chmod +w AGENTS.md
```

---

**状态：** L1 已完成，L2-L4 待执行
