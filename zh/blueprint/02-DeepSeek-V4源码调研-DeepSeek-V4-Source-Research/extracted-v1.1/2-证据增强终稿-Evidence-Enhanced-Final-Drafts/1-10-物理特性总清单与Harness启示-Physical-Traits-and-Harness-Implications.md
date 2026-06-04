# 1-10 物理特性总清单与Harness启示 Physical Traits and Harness Implications

## 1. 物理特性总清单

| 编号 | 物理特性 | 证据 | Harness 启示 |
|---|---|---|---|
| P-001 | V4 Pro / Flash 均支持 1M context | [Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) | 支持长任务，但不能 history dump |
| P-002 | V4 使用 CSA + HCA Hybrid Attention | [README Hybrid Attention](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222) | 需要 layout-driven context |
| P-003 | `sliding_window=128` | [Flash config tail](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L248-L297) | 当前工作信息必须靠近尾部 |
| P-004 | `compress_ratio=4` 时创建 Indexer | [Attention 初始化](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989) | 关键历史要变成可检索 anchor |
| P-005 | sparse attention 使用 `topk_idxs` gather KV | [sparse topk gather](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L725-L733) | 保护 top-k candidate budget |
| P-006 | Pro `index_topk=1024`，Flash `index_topk=512` | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) | Pro 更适合长上下文审查 |
| P-007 | Pro/Flash 都是每 token 6 routed experts | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) | Flash 是同构小模型 |
| P-008 | Gate 支持前若干层 hash routing | [Gate 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1097-L1103) | Prompt 控制标签应稳定 |
| P-009 | MoE 输出 = routed experts + shared expert | [MoE 源码](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1206-L1268) | Flash 也有通用能力通道 |
| P-010 | mHC 使用 `hc_mult=4` | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) | Prompt 应多信号分层 |
| P-011 | mHC 使用 Sinkhorn-like comb 归一化 | [HC Sinkhorn kernel](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L843-L872) | 支持长链路稳定，但仍需 checkpoint |
| P-012 | Instruct 版 MoE experts 使用 FP4，多数其他参数 FP8 | [Model Downloads precision note](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) | Pro-on-demand 成本可控但不能滥用 |
| P-013 | FP4 GEMM 是 FP8 act × FP4 weight | [FP4 GEMM kernel](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L921-L938) | 服务端 kernel 是经济性来源 |
| P-014 | V4 不使用 Jinja template，使用 dedicated encoding | [Chat Template](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L327-L329) | 需要 V4MessageCompiler |
| P-015 | Tool calling 使用 DSML | [DSML tool calling](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L251-L293) | 需要 DSML parser / repair |
| P-016 | reasoning_content 默认 drop old thinking | [drop_thinking](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L217-L250) | reasoning 不是 memory |
| P-017 | API cache hit/miss 分价与 usage 字段 | [Pricing](https://api-docs.deepseek.com/quick_start/pricing#L47-L64) / [usage fields](https://api-docs.deepseek.com/guides/kv_cache#L101-L107) | 成本与 cache telemetry 必须产品化 |

## 2. 不可直接推出的结论

以下内容是工程推论，不是官方源码直接写明：

1. 稳定标签会提升 hash routing 表征稳定性。
2. 多信号 prompt 能更好配合 mHC。
3. Flash 对 context layout 更敏感。
4. Pro 更适合 checkpoint review。
5. Reasoning 应结晶为 checkpoint / skill / memory。

这些推论都有源码依据，但仍需要后续 API 实验和产品任务验证。

## 3. 最终 Harness 启示

DeepSeek Agent 的 Harness 不应先抄竞品，而应带着 V4 约束去调研竞品：

```text
Cache-first
Layout-driven
Checkpoint-gated
Flash/Pro-routed
V4-message-protocol-aware
Reasoning-not-memory
```
