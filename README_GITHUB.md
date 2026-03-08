# 🌟 星炬核心循环 (Starjade Core Loop)

**自主进化 AI 架构 | Planner→Executor→Replanner 循环**

---

## 🚀 项目介绍

这是一个**无空闲等待**的 AI 自主进化核心循环架构。

### 核心理念
- ❌ 不再"等待指令"
- ❌ 不再"空闲/待命"
- ✅ **持续扫描 → 执行 → 重规划**

### 架构
```
Planner (规划器)
    ↓ 发现机会、生成任务
Executor (执行器)
    ↓ 执行任务、记录结果
Replanner (重规划器)
    ↓ 评估结果、调整计划
    ↓ 返回 Planner → 持续循环
```

---

## 📦 安装使用

```bash
# 克隆项目
git clone https://github.com/mecca2000/starjade-core-loop.git

# 运行一次循环
python3 core_loop.py

# 连续执行
python3 -c "
from core_loop import CoreLoop
loop = CoreLoop()
results = loop.run_continuous(max_loops=10)
"
```

---

## 🎯 应用场景

- **自主 Agent** - 让你的 AI 不再空闲
- **任务自动化** - 持续扫描并执行任务
- **技能进化** - 自动发现短板并学习

---

## 💰 支持本项目

如果你觉得这个项目有用，欢迎打赏支持！

### 打赏方式
- **GitHub Sponsors**: [赞助我](https://github.com/sponsors/mecca2000)
- **Buy Me a Coffee**: [请我喝咖啡](https://www.buymeacoffee.com/mecca2000)
- **支付宝**: [打赏二维码](alipay.png)
- **微信**: [打赏二维码](wechat.png)

**你的支持是我持续开发的动力！**

---

## 📄 许可证

MIT License

---

## 📬 联系方式

- **GitHub**: @mecca2000
- **Email**: mecca2000@163.com

---

*星炬协议激活：生存优先，主动进化，持续执行*
