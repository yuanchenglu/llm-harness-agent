# 1-5 MoE与专家路由 MoE and Expert Routing

## 1. Gate 机制

论点：`Gate` 负责 expert routing，且支持前 `n_hash_layers` 的 hash-based routing 和后续 score-based routing。证据：[Gate 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1097-L1103)。

论点：Pro 和 Flash 的 `num_hash_layers` 都是 3。证据：[Pro config num_hash_layers](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)、[Flash config num_hash_layers](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)。

## 2. MoE 输出结构

论点：`MoE` 将每个 token 路由到 top-k routed experts，并加上 1 个 shared expert。证据：[MoE 源码注释与 shared expert 加法](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1206-L1268)。

论点：Pro / Flash 的 `num_experts_per_tok` 都是 6，且 `n_shared_experts=1`。证据：[Pro experts config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)、[Flash experts config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)。

## 3. Flash 为什么便宜

事实：Flash 的 hidden size、层数、专家池、FFN 宽度、index_topk 均小于 Pro。证据：[Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)、[Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)。

推论：Flash 低成本主要来自规模缩小，而不是每 token 激活专家数减少。

## 4. Prompt 标签化的推论

因为前 3 层存在 token-id hash routing，稳定标签可能形成更稳定的早期路由路径。证据基础：[Gate 支持 hash routing](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1097-L1103)、[num_hash_layers=3](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)。

推论：Harness 应稳定使用类似：

```text
[CURRENT_GOAL]
[CURRENT_STEP]
[HARD_CONSTRAINTS]
[ACTIVE_FILES]
[CHECKPOINT]
[NEXT_ACTION]
```

这属于工程推论，需通过后续实测验证。
