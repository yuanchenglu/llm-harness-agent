# 1-1 资料定位与证据规范 Source Map and Evidence Standard

## 1. 官方源码位置

DeepSeek V4 的官方模型仓库、权重、配置、技术报告、推理源码主要在 Hugging Face 的 `deepseek-ai` 组织下；V4 Pro 的模型卡明确给出模型介绍、下载表、评测、chat template / encoding 说明。证据：[V4 Pro 模型卡 Introduction / Model Downloads](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222)、[Model Downloads 表](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231)。

## 2. 本次调研使用的官方文件

| 文件 | 用途 | 官方证据 |
|---|---|---|
| `README.md` | 模型规模、架构升级、评测、reasoning modes、encoding 说明 | [README Introduction](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L214-L222) |
| `config.json` | Pro / Flash 模型结构参数 | [Pro config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/config.json#L206-L245) / [Flash config](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/blob/main/config.json#L203-L242) |
| `inference/model.py` | 模型结构源码：Attention、Compressor、Indexer、Gate、MoE、Block、Transformer | [Transformer 源码注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L1470-L1472) |
| `inference/kernel.py` | FP4/FP8 GEMM、sparse attention、HC Sinkhorn kernel | [FP4 GEMM kernel](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L921-L938) |
| `encoding/README.md` | V4 message encoding、thinking、tool calling、quick tasks | [Encoding 概览](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/encoding/README.md#L194-L214) |
| DeepSeek API Docs | context caching、cache hit/miss、pricing、model features | [Pricing](https://api-docs.deepseek.com/quick_start/pricing#L47-L64) / [Context caching](https://api-docs.deepseek.com/guides/kv_cache#L44-L57) |

## 3. 证据写法规范

之后所有文档采用如下格式：

```text
论点：V4 的 attention 候选集合由 local window + compressed history 组成。
证据：model.py 中 Attention.forward 先构造 window topk，再根据 compress_ratio 合并 compressed topk。
官方链接：...
推论：Harness 不能 history dump，而要做 context layout。
```

## 4. 重要边界

- 只要是源码或官方文档没有直接证明的内容，统一写为“推论”。
- 不把第三方说法写成事实。
- 不把 API 行为和开源 inference demo 完全等同；若两者差异未验证，标注“需实测”。
