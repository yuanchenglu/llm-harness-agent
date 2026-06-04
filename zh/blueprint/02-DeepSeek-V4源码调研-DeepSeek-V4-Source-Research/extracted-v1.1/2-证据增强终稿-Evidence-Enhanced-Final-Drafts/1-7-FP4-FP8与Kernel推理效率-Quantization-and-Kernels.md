# 1-7 FP4-FP8与Kernel推理效率 Quantization and Kernels

## 1. 精度说明

官方模型下载表说明，Instruct 版是 FP4 + FP8 Mixed，且注释写明 MoE expert parameters 使用 FP4，多数其他参数使用 FP8。证据：[Model Downloads precision note](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/README.md#L226-L231)。

## 2. Linear 层中的 FP4 / FP8 结构

`model.py` 中 `Linear` 根据 dtype 创建 FP4 packed weight 或 FP8 weight，并带 scale。证据：[Linear FP4/FP8 权重实现](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/model.py#L411-L428)。

## 3. activation FP8 quantization

`kernel.py` 中 `act_quant` 是 block-wise FP8 quantization，默认 block size 为 128。证据：[act_quant 源码](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L358-L396)。

## 4. FP4 expert GEMM

`fp4_gemm_kernel` 注释明确写到：这是 FP8 activation × FP4 weight GEMM；activation 按 K 维每 128 量化，weight 按 K 维每 32 量化，FP4 values 沿 K 维打包。证据：[fp4_gemm_kernel 注释](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/kernel.py#L921-L938)。

## 5. 本地推理边界

官方 inference README 要求先转换权重，再使用 `torchrun --nproc-per-node MP generate.py`；示例中 `EXPERTS=384`、`MP=8`，并说明可移除 `expert_dtype=fp4` 改用 fp8。证据：[inference README](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/inference/README.md#L194-L214)。

## 6. 产品推论

这些证据说明：V4 的低成本和高吞吐很大程度依赖服务端 kernel / 量化 / 并行部署。桌面产品 MVP 不应默认承诺本地跑 V4，而应默认接入 DeepSeek API 或私有 endpoint。
