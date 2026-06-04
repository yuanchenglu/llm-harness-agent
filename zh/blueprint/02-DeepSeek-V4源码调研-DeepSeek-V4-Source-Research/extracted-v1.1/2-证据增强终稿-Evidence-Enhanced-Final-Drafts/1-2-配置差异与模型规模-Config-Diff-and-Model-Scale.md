# 1-2 配置差异与模型规模 Config Diff and Model Scale

## 1. 模型规模

DeepSeek 官方模型卡明确写到：V4 系列包含两个 MoE 模型，V4-Pro 为 1.6T 参数、49B activated，V4-Flash 为 284B 参数、13B activated，二者都支持 1M context。证据：[README Introduction lines 214-222](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222)。

模型下载表进一步确认：

| 模型 | 总参数 | 激活参数 | Context | 精度 | 证据 |
|---|---:|---:|---:|---|---|
| DeepSeek-V4-Flash-Base | 284B | 13B | 1M | FP8 Mixed | [Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) |
| DeepSeek-V4-Flash | 284B | 13B | 1M | FP4 + FP8 Mixed | [Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) |
| DeepSeek-V4-Pro-Base | 1.6T | 49B | 1M | FP8 Mixed | [Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) |
| DeepSeek-V4-Pro | 1.6T | 49B | 1M | FP4 + FP8 Mixed | [Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231) |

## 2. Pro / Flash config 核心差异

| 字段 | V4-Pro | V4-Flash | 证据 |
|---|---:|---:|---|
| `hidden_size` | 7168 | 4096 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `num_hidden_layers` | 61 | 43 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `num_attention_heads` | 128 | 64 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `index_topk` | 1024 | 512 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `n_routed_experts` | 384 | 256 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `num_experts_per_tok` | 6 | 6 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `num_hash_layers` | 3 | 3 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `hc_mult` | 4 | 4 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `sliding_window` | 128 | 128 | [Flash config tail](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L248-L297) |

## 3. 初步结论

### 3.1 Flash 不是“少激活专家版”

论点：Flash 并不是通过减少每 token 激活专家数来降低成本；Pro 和 Flash 的 `num_experts_per_tok` 都是 6。证据：[Pro num_experts_per_tok=6](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)、[Flash num_experts_per_tok=6](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)。

推论：Flash-first 是合理默认策略，因为它保留 V4 的核心机制；Pro 应用于关键规划、长上下文审查、失败复盘、最终验收。

### 3.2 Pro 的优势来自容量、深度、专家池、Indexer 预算

论点：Pro 的 `hidden_size`、`num_hidden_layers`、`n_routed_experts`、`index_topk` 都显著高于 Flash。证据：[Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)、[Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)。

推论：Pro 更适合复杂知识、架构决策、长上下文证据冲突判断、复杂 Agentic workflow。
