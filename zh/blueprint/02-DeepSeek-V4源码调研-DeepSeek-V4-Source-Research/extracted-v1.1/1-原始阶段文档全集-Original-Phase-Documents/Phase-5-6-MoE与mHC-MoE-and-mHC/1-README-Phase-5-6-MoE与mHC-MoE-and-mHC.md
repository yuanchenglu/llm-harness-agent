# DeepSeek V4 Phase 5-6 调研包

本包包含第三轮产出：

1. `05-moe-routing-analysis.md`
2. `05-agent-model-router-rules.md`
3. `06-mhc-hyperconnections-analysis.md`
4. `06-harness-implications-for-long-reasoning.md`

核心结论：

- V4 的 MoE 是 token 级 top-k routed experts + shared expert。
- Pro/Flash 都是每 token 6 个 routed experts，不是 Flash 少激活专家。
- 前 3 层 hash routing，由 token id 决定 expert ids。
- 后续层 score-based routing，score_func=sqrtsoftplus。
- Pro 强来自更宽、更深、更大专家池、更大 index_topk、更高 route_scale。
- V4 的 residual 不是简单加法，而是 mHC 四份 hidden copies + Sinkhorn-constrained mixing。
- DeepSeek Agent Harness 必须变成多信号分层架构。
