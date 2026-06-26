# D2. MemAgent：用多轮 RL 记忆智能体重塑长上下文 LLM

**标题：** MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent
**作者：** Guangming Yu 等
**出处：** arXiv:2507.02259, 2025
**状态：** 预印本

---

**核心：** 将上下文管理建模为 MDP，训练记忆智能体决定跨对话轮次中保留/压缩/丢弃的信息。学习型记忆管理优于朴素拼接方法。

**Harness 启示：** 注意力稀释问题的纯装备层解决方案——上下文管理作为独立优化问题，由专用机制而非 LLM 原始窗口解决。直接对应上下文管理器（C）。
