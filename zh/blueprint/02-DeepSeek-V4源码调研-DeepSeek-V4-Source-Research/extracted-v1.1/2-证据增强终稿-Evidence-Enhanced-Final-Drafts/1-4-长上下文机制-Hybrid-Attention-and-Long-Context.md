# 1-4 长上下文机制 Hybrid Attention and Long Context

## 1. 官方模型卡结论

DeepSeek 官方模型卡说明，V4 使用 Hybrid Attention，将 Compressed Sparse Attention（CSA）与 Heavily Compressed Attention（HCA）结合，以提升长上下文效率；在 1M context 下，V4-Pro 相比 V3.2 只需要 27% single-token inference FLOPs 和 10% KV cache。证据：[README Hybrid Attention 描述](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222)。

## 2. 源码中的 Attention 路径

论点：`Attention` 是 MLA + sliding window + optional KV compression。证据：[Attention 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989)。

源码行为：

1. `self.window_size = args.window_size`，config 中 `sliding_window=128`。证据：[Attention 初始化](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989)、[Flash sliding_window=128](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L248-L297)。
2. `self.compress_ratio = args.compress_ratios[layer_id]`。证据：[Attention compress_ratio 初始化](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989)。
3. 如果 `compress_ratio` 非 0，则创建 `Compressor`。证据：[Attention 创建 Compressor](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989)。
4. 如果 `compress_ratio == 4`，则创建 `Indexer`；否则 `indexer = None`。证据：[Attention 创建 Indexer](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989)。
5. `forward` 先构造 window topk，再根据 `compress_ratio` 合并 compressed topk，最后调用 `sparse_attn`。证据：[Attention.forward 合并 topk 并 sparse_attn](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L991-L1095)。

## 3. Indexer 的作用

论点：`Indexer` 通过 learned scoring 选择 top-k compressed KV positions。证据：[Indexer 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L812-L895)。

论点：`Indexer` 使用 `index_score.topk(min(self.index_topk, end_pos // ratio))` 选择 top-k。证据：[Indexer topk 选择](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L812-L895)。

## 4. sparse attention 的 kernel 证据

论点：V4 的 sparse attention 是通过 `topk_idxs` 显式 gather KV positions，而不是 dense attention。证据：[sparse attention kernel 注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L650-L656)、[topk_idxs 参数](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L679-L689)、[KV gather 实现](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L725-L733)。

论点：sparse attention 还有 `attn_sink`，在 softmax 分母中加入稳定项。证据：[attn_sink 使用](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L769-L772)。

## 5. Harness 推论

由于 `sliding_window=128`，且远程历史通过 compressed / sparse path 进入 attention，1M context 不能等价理解为“所有 token 同等可见”。证据基础：[window + compressed topk 源码](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L991-L1095)。

推论：DeepSeek Agent 必须使用 layout-driven context：

```text
Stable Prefix
Task Anchor Zone
Active Working Set
Compressed History Zone
Turn Tail
```

其中当前操作、当前目标、硬约束应靠近尾部或进入稳定 anchor；历史日志应转为 checkpoint，而不是 raw history dump。
