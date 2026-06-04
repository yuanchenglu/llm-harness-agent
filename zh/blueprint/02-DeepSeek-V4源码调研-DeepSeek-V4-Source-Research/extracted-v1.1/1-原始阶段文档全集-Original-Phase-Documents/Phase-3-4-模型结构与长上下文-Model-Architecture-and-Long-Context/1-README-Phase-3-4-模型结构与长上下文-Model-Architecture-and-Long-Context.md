# DeepSeek V4 Phase 3-4 调研包

本包包含第二轮产出：

1. `03-model-architecture-map.md`
2. `04-hybrid-attention-deep-dive.md`
3. `04-context-layout-rules-for-agent.md`

核心结论：

- V4 主结构是 `Embedding → HC expand → N×Block → HC Head → Logits`。
- 每个 Block 是 `mHC → Attention → mHC → MoE → mHC`。
- Attention 候选集合是 `local window + compressed history`。
- `compress_ratio=4` 启用 learned Indexer，疑似 CSA 主路径。
- `compress_ratio=128` 不启用 Indexer，疑似 HCA 主路径。
- DeepSeek Agent 的上下文必须 layout-driven，不能 history-dump。
