# B6. HuggingGPT：用 ChatGPT 及其 Hugging Face 伙伴解决 AI 任务

**标题：** HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face
**作者：** Yongliang Shen 等（Microsoft）
**出处：** NeurIPS 2023（CCF-A）
**编号：** arXiv:2303.17580

---

**核心贡献：** LLM 作为"任务规划器/控制器"连接 Hugging Face 上的众多专业 AI 模型。四阶段：(1) 任务规划——ChatGPT 将用户请求解析为结构化子任务；(2) 模型选择——从 Hugging Face 选择合适的专家模型；(3) 任务执行——运行各模型并收集结果；(4) 响应生成——综合结果。展示了 LLM 作为异构 AI 生态系统的"中央大脑"。

**Harness 启示：** 装备层即编排器的早期实例——LLM 充当"大脑"而模型选择、执行和结果整合由装备层处理。直接对应工具注册表（T）和执行循环（E）。
