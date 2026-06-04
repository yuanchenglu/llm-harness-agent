# 1-11 证据索引 Evidence Index

## 1. 官方模型卡 / README

| 结论 | 官方链接 |
|---|---|
| V4-Pro 1.6T / 49B activated，V4-Flash 284B / 13B activated，均支持 1M context | [README Introduction](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222) |
| CSA + HCA、mHC、Muon 是 V4 关键升级 | [README Introduction](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222) |
| 模型下载表与 FP4 + FP8 Mixed 注释 | [Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) |
| Reasoning modes: Non-think / Think / Think Max | [Reasoning modes](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L268-L272) |
| Comparison across Modes 评测表 | [Comparison across Modes](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L300-L326) |
| 不提供 Jinja template，提供 encoding 目录 | [Chat Template](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L327-L329) |

## 2. 官方 config

| 结论 | 官方链接 |
|---|---|
| Pro hidden_size=7168、index_topk=1024、max_position_embeddings=1048576、n_routed_experts=384、num_experts_per_tok=6、num_hidden_layers=61、num_hash_layers=3 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) |
| Pro quantization_config: fp8 | [Pro quantization_config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L259-L277) |
| Flash hidden_size=4096、index_topk=512、max_position_embeddings=1048576、n_routed_experts=256、num_experts_per_tok=6、num_hidden_layers=43、num_hash_layers=3 | [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| Flash routed_scaling_factor=1.5、sliding_window=128 | [Flash config tail](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L248-L297) |

## 3. `inference/model.py`

| 结论 | 官方链接 |
|---|---|
| Linear 支持 FP4 packed weight 与 FP8 weight scale | [Linear FP4/FP8](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L411-L428) |
| Compressor 负责压缩 KV | [Compressor](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L636-L810) |
| Indexer 通过 learned scoring 选择 top-k compressed KV positions | [Indexer](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L812-L895) |
| Attention 是 MLA + sliding window + optional KV compression | [Attention](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989) |
| Attention.forward 合并 window topk 与 compressed topk，并调用 sparse_attn | [Attention.forward](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L991-L1095) |
| Gate 支持 hash-based routing 和 score-based routing | [Gate](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1097-L1103) |
| MoE = routed experts + shared expert | [MoE](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1206-L1268) |
| Block 使用 Hyper-Connections | [Block](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1272-L1329) |
| Transformer 总结构：embed → HC-expand → N blocks → HC-head → logits | [Transformer](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1470-L1472) |

## 4. `inference/kernel.py`

| 结论 | 官方链接 |
|---|---|
| act_quant 是 block-wise FP8 quantization | [act_quant](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L358-L396) |
| sparse attention 通过 index gathering + online softmax 实现 | [sparse_attn](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L650-L656) |
| sparse attention 输入包含 topk_idxs | [topk_idxs](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L679-L689) |
| kernel 中根据 topk_idxs gather KV | [KV gather](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L725-L733) |
| sparse attention 使用 attn_sink | [attn_sink](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L769-L772) |
| hc_split_sinkhorn 返回 pre/post/comb | [hc_split_sinkhorn](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L902-L917) |
| comb 经过 Sinkhorn-like 行列归一化 | [HC Sinkhorn](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L843-L872) |
| FP4 GEMM 是 FP8 act × FP4 weight | [FP4 GEMM](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L921-L938) |

## 5. Encoding

| 结论 | 官方链接 |
|---|---|
| Encoding 处理多轮对话、工具调用、extended thinking、quick instruction tasks | [Encoding overview](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L194-L214) |
| chat mode / thinking mode / drop_thinking 行为 | [Thinking and drop_thinking](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L217-L250) |
| DSML tool calling 和 tool_result 行为 | [DSML tool calling](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L251-L293) |
| reasoning_effort=max 的特殊前缀 | [Reasoning effort max](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L294-L309) |

## 6. DeepSeek API Docs

| 结论 | 官方链接 |
|---|---|
| V4 Flash / Pro 支持 1M context、384K max output、tool calls、FIM non-thinking only、cache hit/miss 价格 | [Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing#L47-L64) |
| Context caching 默认开启，缓存重叠 prefix | [Context Caching](https://api-docs.deepseek.com/guides/kv_cache#L44-L57) |
| cache prefix unit 必须完整匹配 | [Cache hit rules](https://api-docs.deepseek.com/guides/kv_cache#L44-L57) |
| usage 返回 prompt_cache_hit_tokens / prompt_cache_miss_tokens | [Cache usage fields](https://api-docs.deepseek.com/guides/kv_cache#L101-L107) |

## 7. 待后续实测

1. API 实际返回的 reasoning_content 与开源 encoding 的一致性。
2. DSML tool call 在官方 API 中的稳定性。
3. V4 Flash / Pro 在真实 Agent Loop 下的 cache hit 率。
4. Stable labels 是否实际提升长任务稳定性。
5. Checkpoint-driven Pro review 相比 raw history review 的收益。
