# C1. ToolLLM：让 LLM 掌握 16000+ 真实世界 API

**标题：** ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs
**作者：** Yujia Qin 等（清华大学）
**出处：** ICLR 2024（CCF-A）
**编号：** arXiv:2307.16789

---

**核心：** ToolBench（16,464 个真实 API 的指令数据集）+ DFSDT（深度优先搜索决策树）算法 + ToolEval 评估。ToolLLaMA 在需要多步规划和 API 组合的复杂任务上达到与 GPT-4 竞争的性能。

**Harness 启示：** 管理 16,000+ API 需要模型之外的专用基础设施（检索、规划、评估）——直接对应工具注册表（T）和评估接口（V）。
