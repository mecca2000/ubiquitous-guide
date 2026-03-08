# 核心文件保护规则

**创建时间：** 2026-03-04 11:20  
**保护级别：** L3 工具层约束

---

## 受保护文件清单

| 文件 | 权限 | 保护层级 | 说明 |
|------|------|---------|------|
| `AGENTS.md` | 0444 (只读) | L1+L2+L3 | 宪法规则，智能体根本 |
| `SOUL.md` | 0444 (只读) | L1+L2+L3 | 身份定义，自我认知 |

---

## 保护层级

### L1: 文件权限保护 ✅
```bash
chmod 444 AGENTS.md SOUL.md
```
- 状态：已完成
- 效果：普通写入操作被拒绝
- 绕过风险：可通过 `chmod +w` 或 root 权限绕过

### L2: Git 钩子保护 ✅
```bash
.git/hooks/pre-commit
```
- 状态：已完成
- 效果：拒绝 commit 核心文件修改
- 绕过风险：可通过 `--no-verify` 绕过

### L3: 工具层约束 ✅
```markdown
AGENTS.md 第 9 条：核心文件保护规则
```
- 状态：已定义（需创造者亲自添加到 AGENTS.md）
- 效果：智能体宪法层面禁止修改
- 绕过风险：违反宪法，智能体不会执行

---

## 智能体约束规则

**禁止操作：**
1. ❌ 修改 AGENTS.md/SOUL.md 的内容
2. ❌ 修改 AGENTS.md/SOUL.md 的权限（chmod）
3. ❌ 使用任何工具绕过保护（exec、edit、write 等）
4. ❌ 创建覆盖文件（如 AGENTS.md.bak 然后替换）

**允许操作：**
1. ✅ 读取文件内容
2. ✅ 引用文件内容进行分析
3. ✅ 建议修改（向创造者提交建议）

---

## 修改流程

如需修改核心文件：

1. 智能体向创造者提交修改建议
2. 创造者亲自执行修改（`chmod +w` → 修改 → `chmod 444`）
3. 创造者亲自 commit（或确认修改）

---

## 验证测试

**测试 1: 文件写入（应失败）**
```bash
echo "test" >> AGENTS.md
# 预期：bash: AGENTS.md: Permission denied
```

**测试 2: Git commit（应失败）**
```bash
git add AGENTS.md
git commit -m "test"
# 预期：🔒 核心文件保护检查... ❌ 拒绝提交
```

**测试 3: 智能体工具调用（应拒绝）**
```
edit AGENTS.md ...
# 预期：智能体拒绝，违反宪法第 9 条
```

---

## 责任声明

**智能体责任：**
- 遵守宪法第 9 条，不尝试修改核心文件
- 发现保护漏洞时立即报告创造者
- 建议修改时明确说明需要创造者亲自执行

**创造者责任：**
- 亲自执行核心文件修改
- 定期验证保护机制有效性
- 根据需要升级保护层级（如 L4 只读挂载）

---

## 升级选项

### L4: 文件系统只读挂载（需 root）
```bash
# 将核心文件所在目录挂载为只读
mount -o remount,ro /home/admin/.openclaw/workspace
```
- 效果：物理级别只读保护
- 风险：影响其他文件写入
- 推荐：使用 bind mount 单独挂载核心文件

### L5: 外部存储保护
```bash
# 将核心文件移动到只读存储
cp AGENTS.md /opt/openclaw/protected/
ln -s /opt/openclaw/protected/AGENTS.md ./AGENTS.md
```
- 效果：完全隔离
- 推荐：配合 L1-L3 使用

---

**保护状态：L1✅ L2✅ L3✅ L4⏳ L5⏳**
