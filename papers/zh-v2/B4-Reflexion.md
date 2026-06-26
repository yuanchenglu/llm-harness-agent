# B4. Reflexion：具备语言化强化学习的语言智能体

**标题：** Reflexion: Language Agents with Verbal Reinforcement Learning
**作者：** Noah Shinn 等
**出处：** NeurIPS 2023（CCF-A）
**编号：** arXiv:2303.11366

---

**核心贡献：** 提出 Reflexion 框架，Agent 从先前错误中学习——获取"反思"（对哪里出错、如何改进的文字总结），存储在情景记忆中并在后续尝试中注入上下文。这种语言化强化比传统 RL 更灵活、样本效率更高，Agent 在不更新权重的情况下通过自我修正显著提升性能。

**实验：** AlfWorld（71% 基线→90% Reflexion）、HotPotQA（34%→40%）、HumanEval（67%→91%）。

**Harness 启示：** 纯装备层创新——仅通过修改进入上下文窗口的信息（不改变模型权重）就产生巨大收益。直接对应装备层模型中的状态存储（S）和上下文管理器（C）。
