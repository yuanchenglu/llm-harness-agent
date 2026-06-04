# 1-6 mHC超连接机制 mHC Hyper-Connections

## 1. 官方说明

DeepSeek 官方模型卡说明，V4 引入 Manifold-Constrained Hyper-Connections（mHC）来增强传统 residual connections，提高跨层信号传播稳定性并保持表达能力。证据：[README mHC 描述](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222)。

## 2. 源码结构

论点：`Block` 使用 Hyper-Connections，而不是简单 residual；源码注释写明 HC 维护 `hc_mult` copies of hidden state。证据：[Block 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1272-L1329)。

论点：config 中 `hc_mult=4`、`hc_sinkhorn_iters=20`。证据：[Pro hc config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)、[Flash hc config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242)。

论点：`hc_split_sinkhorn` 返回 `pre`、`post`、`comb`，用于 mHC 的 pre/post/comb mixing。证据：[hc_split_sinkhorn 函数](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L902-L917)。

论点：`comb` 在 kernel 中经过 softmax 和行列归一化，体现 Sinkhorn-like 约束。证据：[HC Sinkhorn kernel](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L843-L872)。

## 3. Harness 推论

mHC 表明 V4 内部不是单一 hidden stream，而是多通道信号混合。推论：Prompt 也应多信号分层，而不是混成一段自然语言。

推荐分层：

```text
[GOAL_SIGNAL]
[CONSTRAINT_SIGNAL]
[EVIDENCE_SIGNAL]
[EXECUTION_SIGNAL]
[REVIEW_SIGNAL]
[NEXT_ACTION_SIGNAL]
```

该结论是基于 mHC 源码的 Harness 推论，不是官方文档直接要求。
