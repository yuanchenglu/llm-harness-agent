# DeepSeek V4 Phase 7-8 调研包

本包包含第四轮产出：

1. `07-quantization-kernel-analysis.md`
2. `07-serving-constraints-for-client-harness.md`
3. `08-encoding-and-reasoning-mode.md`
4. `08-agent-loop-message-protocol.md`
5. `08-reasoning-content-policy.md`

核心结论：

- V4 推理效率依赖 TileLang FP4/FP8/sparse_attn/HC kernels。
- Instruct 版 MoE experts 的 FP4 + 其他参数 FP8 是服务端经济性的核心来源之一。
- sparse_attn 显式使用 topk_idxs gather KV，保护 top-k 预算是 Harness 责任。
- 本地运行 V4 不是桌面 MVP 默认目标，应通过 API / private endpoint 接入。
- V4 不使用 Jinja chat template，而是专门的 `encoding_dsv4.py`。
- Tool calling 使用 DSML，tool results merge into user messages。
- 旧 reasoning_content 默认应 drop/summarize/archive，不应无限回传。
