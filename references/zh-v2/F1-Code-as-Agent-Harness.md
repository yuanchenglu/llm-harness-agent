# F1. 代码即 Agent 装备层：迈向可执行、可验证、有状态的 Agent 系统

**标题：** Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems
**作者：** Xuying Ning, Katherine Tieu 等（44 位作者）
**出处：** arXiv:2605.18747, 2026
**PDF：** [arxiv.org/pdf/2605.18747](https://arxiv.org/pdf/2605.18747)

---

## 核心视角

**代码不再是 Agent 的输出目标，而是 Agent 的运行基座。** 统一了 CodeAct、OpenHands 等以代码为核心动作空间的系统。

### 三层框架

**① 装备层接口**：代码如何连接 Agent 与
- **推理**：程序委托推理（Program-Delegated Reasoning）
- **行动**：可执行代码作为统一动作空间
- **环境建模**：代码作为环境的状态表示

**② 装备层机制**
- 规划机制：代码辅助的任务分解和排序
- 记忆/上下文工程：通过结构化代码管理信息
- 工具使用：代码作为工具调用的统一语言
- PEV 控制循环：Program → Execute → Verify

**③ 装备层规模化**
- 多智能体角色专门化
- 交互模式：代码审查、协作编码
- 共享工件：代码作为多智能体协作的媒介
- 执行反馈与同步

### 应用领域
编码助手、GUI/OS 自动化、具身智能体、科学发现、DevOps、企业工作流

---

**Harness 关联：** 提出了"代码本身可以是装备层"的新视角。论证了为什么代码作为装备层的统一动作语言优于离散工具调用。核心挑战（评估、验证、共享状态、人类监督）与装备层理论完全一致。
