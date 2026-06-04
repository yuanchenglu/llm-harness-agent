# 1-3 模型结构总览 Model Architecture Map

## 1. 总结构

官方 `model.py` 对 `Transformer` 的注释写明，完整模型是 `embed -> HC-expand -> N blocks -> HC-head -> logits`。证据：[Transformer 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1470-L1472)。

论点：V4 不是普通 Transformer block 叠加，而是在 embedding 后将 hidden state 扩展为 `hc_mult` 份 copy，再经过多个 block，最后由 HC head 汇聚输出。证据：[Transformer 源码](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1470-L1472)、[hc_mult=4 config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245)。

## 2. 核心模块

| 模块 | 职责 | 官方证据 |
|---|---|---|
| `Compressor` | 压缩 KV cache，服务长上下文历史压缩 | [Compressor 源码](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L636-L810) |
| `Indexer` | learned scoring 选择 top-k compressed KV positions | [Indexer 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L812-L895) |
| `Attention` | MLA + sliding window + optional KV compression | [Attention 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989) |
| `Gate` | MoE gating，支持 hash-based 和 score-based routing | [Gate 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1097-L1103) |
| `MoE` | 每 token 路由到 top-k experts + 1 shared expert | [MoE 源码注释与实现](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1206-L1268) |
| `Block` | 使用 Hyper-Connections 的 Transformer block | [Block 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1272-L1329) |
| `Linear` | 支持 FP4/FP8 权重结构 | [Linear FP4/FP8 权重实现](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L411-L428) |

## 3. 结论

论点：V4 的结构由 long-context attention、MoE routing、mHC residual、FP4/FP8 kernel 共同构成，不能按普通 Transformer / 普通 MoE 理解。证据：[模型卡架构升级](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222)、[model.py 模块](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L908-L989)、[kernel.py FP4 GEMM](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L921-L938)。

推论：Agent Harness 的上下文、模型路由、工具循环、reasoning 管理都要围绕这些物理结构设计。
