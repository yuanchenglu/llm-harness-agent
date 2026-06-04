# 07-quantization-kernel-analysis.md — DeepSeek V4 量化与 Kernel 深拆 v0.1

> 日期：2026-06-04  
> 阶段：Phase 7 — Quantization / Kernel 深拆  
> 目标：基于 `inference/kernel.py`、`inference/README.md`、`model.py::Linear`，理解 V4 的 FP4 / FP8 / Sparse Attention / HC kernel 如何支撑低成本、高吞吐、1M context。

---

## 1. 总体结论

DeepSeek V4 的推理效率不是单一技巧，而是一组 kernel-level 设计共同作用：

```text
1. FP8 activation quantization
2. FP8 GEMM
3. FP4 expert weights + FP8 activation GEMM
4. Sparse attention via top-k index gathering
5. HC Sinkhorn custom kernel
6. Model parallel conversion / loading
```

这说明 V4 的经济性来自两层：

```text
模型架构层：MoE + Hybrid Attention + mHC
Kernel 层：FP4 experts + FP8 activations + sparse_attn + TileLang kernels
```

对 DeepSeek Agent 来说，客户端 Harness 不需要实现这些 kernel，但必须理解它们造成的运行物理特性：

- Prefill / decode 成本不同；
- Flash / Pro 的延迟和吞吐不同；
- 1M context 可用但不能乱用；
- FP4/FP8 是服务端经济性的来源；
- 本地部署是高级能力，不应作为默认用户路径。

---

## 2. kernel.py 总览

`kernel.py` 使用：

```python
import tilelang
import tilelang.language as T
```

并定义：

```text
FP8 = float8_e4m3
FP4 = float4_e2m1fn
FE8M0 = float8_e8m0fnu
BF16 = bfloat16
FP32 = float32
```

核心 kernel：

| 函数 | 作用 | 重要性 |
|---|---|---|
| `act_quant` | BF16 activation → FP8 block quant | 高 |
| `fp4_act_quant` | BF16 activation → FP4 block quant / simulation | 高 |
| `fp8_gemm` | FP8 act × FP8 weight GEMM | 高 |
| `fp4_gemm` | FP8 act × FP4 weight GEMM | 极高 |
| `sparse_attn` | top-k gather sparse multi-head attention | 极高 |
| `hc_split_sinkhorn` | mHC pre/post/comb 拆分与 Sinkhorn 归一化 | 高 |

---

## 3. FP8 activation quantization

### 3.1 源码行为

`act_quant` 是 block-wise FP8 quantization：

```text
block_size = 128
input dtype = BF16
output dtype = FP8
scale dtype = FP32 或 FE8M0
```

内部流程：

```text
每 128 个 K 维度一组
  ↓
计算 absmax
  ↓
scale = amax / fp8_max
  ↓
x / scale 后 clamp 到 FP8 范围
  ↓
保存 FP8 values + scale
```

如果 `scale_fmt` 设置，会把 scale round 到 power-of-2，也就是 MXFP 风格。

### 3.2 物理意义

- activation 不是全精度进入 GEMM，而是 FP8 + scale；
- 每 128 维一个 scale；
- 这正好对应后续 `fp8_gemm` 的 per-128 block scaling。

### 3.3 对 Harness 的影响

对客户端而言，这意味着：

- V4 API 的便宜/快来自服务端低精度路径；
- Prompt 越长，prefill 仍然需要大量 FP8 GEMM；
- Harness 应尽量提高 cache hit，减少 repeated prefill；
- 成本面板应区分 prompt cache miss 与 decode 输出。

---

## 4. FP4 activation quantization / simulation

### 4.1 源码行为

`fp4_act_quant`：

```text
block_size = 32
scale dtype = FE8M0
fp4_max = 6.0
scale = power_of_2(amax / fp4_max)
```

输出是：

```text
FP4 packed values + E8M0 scales
```

如果 `inplace=True`，则做 fused quant + dequant，用于模拟低精度误差。

### 4.2 物理意义

- FP4 使用更小 block size：32；
- scale 是 power-of-2；
- FP4 values 沿 K 维打包；
- 这与 expert weights 的 FP4 存储/计算直接相关。

---

## 5. FP8 GEMM

### 5.1 源码行为

`fp8_gemm` 计算：

```text
C[M,N] = A_fp8[M,K] @ B_fp8[N,K]^T
```

量化尺度：

```text
A: per-128 on K
B: per-128 on K
Accumulator: FP32
Output: BF16 / FP32
```

### 5.2 物理意义

- 非 expert 参数大概率走 FP8 GEMM；
- activation 和 weight 都是 FP8，但计算时用 scale 恢复数值；
- 这是 V4 “most other parameters use FP8” 的 kernel 基础。

---

## 6. FP4 GEMM：V4 Instruct 经济性的核心

### 6.1 源码注释

`fp4_gemm_kernel` 注释说明：

```text
FP8 act x FP4 weight GEMM
C[M, N] = A_fp8[M, K] @ B_fp4[N, K]^T
Activation: per-128 quant on K, FP8
Weight: per-32 quant on K, FP4 with E8M0 scale
B stored as [N, K//2] in float4_e2m1fn_x2
FP4 values packed along K dimension
```

### 6.2 物理意义

这是 Instruct 版 MoE experts 使用 FP4 的直接计算路径：

```text
routed expert weights: FP4
activation: FP8
compute: FP8-like GEMM with FP4 weights cast to FP8 during tile computation
accumulation: FP32
output: BF16
```

### 6.3 为什么重要

MoE 的 routed experts 是参数大头。把 routed experts 压到 FP4，同时让 activation 保持 FP8，是 V4 Instruct 能做到大规模、低成本、可部署的核心原因之一。

### 6.4 对 Agent Harness 的影响

- Pro 虽然 1.6T total，但 activated 49B + FP4 experts 让 API 成本可控；
- Flash 284B / 13B activated 更适合默认执行；
- 但上下文太长仍会触发 prefill 成本，不能因为 FP4 就随便塞 1M；
- Harness 的核心优化目标仍是 cache hit 和 layout，而不是“模型足够便宜”。

---

## 7. Sparse Attention Kernel

### 7.1 源码行为

`sparse_attn` 的输入：

```text
q: [batch, seq, heads, dim]
kv: [batch, kv_len, dim]
attn_sink: [heads]
topk_idxs: [batch, seq, topk]
```

核心机制：

```text
对每个 batch / seq position:
  读取 topk_idxs 指定的 KV positions
  gather KV
  q @ kv
  online softmax
  加入 learnable attn_sink
  输出 attention result
```

源码注释明确是：

```text
Sparse multi-head attention via index gathering + online softmax (FlashAttention-style).
```

### 7.2 `attn_sink`

kernel 在 softmax 分母中加入：

```text
sum_exp += exp(attn_sink[i] - scores_max[i])
```

物理意义：

- 每个 head 有一个 learnable sink bias；
- 这提供一种“不关注任何具体 KV 位置”的稳定项；
- 可帮助 sparse attention 在 top-k 候选不足或噪声大时保持稳定。

### 7.3 对 Harness 的影响

- V4 的远程历史 attention 是由 `topk_idxs` 明确控制的；
- 噪声历史会消耗 top-k candidate budget；
- 关键历史必须被压缩成短而强的 anchor；
- `attn_sink` 提供稳定项，但不能替代 Harness 的上下文整理。

---

## 8. HC Sinkhorn Kernel

### 8.1 源码行为

`hc_split_sinkhorn` 计算：

```text
mixes → pre, post, comb
```

其中：

```text
pre = sigmoid(...) + eps
post = 2 * sigmoid(...)
comb = softmax + repeated row/column normalization
```

`comb` 经过 `sinkhorn_iters=20` 的行列归一化，近似双随机矩阵。

### 8.2 物理意义

- mHC 的 residual mixing 被约束，不是任意矩阵；
- 这帮助稳定深层信号传播；
- 与 V4 61 层 Pro / 43 层 Flash 的深度相配合。

---

## 9. 本地推理路径

`inference/README.md` 说明：

```bash
export EXPERTS=384
export MP=8
python convert.py --hf-ckpt-path ${HF_CKPT_PATH} --save-path ${SAVE_PATH} --n-experts ${EXPERTS} --model-parallel ${MP}
torchrun --nproc-per-node ${MP} generate.py --ckpt-path ${SAVE_PATH} --config ${CONFIG} --interactive
```

并说明：

```text
If you want to use fp8, just remove "expert_dtype": "fp4" in config.json and specify --expert-dtype fp8 in convert.py.
```

### 9.1 物理意义

- 官方 demo 面向多 GPU / model parallel；
- Pro 默认示例 `EXPERTS=384`、`MP=8`；
- 本地部署不是普通桌面用户路径；
- FP4 / FP8 可以通过 conversion 影响权重格式。

---

## 10. 新增物理特性编号

### P-027：V4 官方推理 kernel 使用 TileLang 自定义实现

证据：`kernel.py` import tilelang 并用 `@tilelang.jit` 定义核心 kernel。

Harness 影响：客户端默认不应假设可本地运行 Pro/Flash；本地部署应作为高级/服务器模式。

### P-028：activation FP8 quantization 是 per-128 block

证据：`act_quant(block_size=128)`。

Harness 影响：长 prompt prefill 仍有真实计算成本；cache hit 是关键。

### P-029：routed expert 计算使用 FP8 act × FP4 weight GEMM

证据：`fp4_gemm_kernel` 注释和实现。

Harness 影响：V4 Instruct 成本优势高度依赖 FP4 experts；Pro-on-demand 成本可控但不能滥用。

### P-030：sparse attention 由 topk_idxs 显式 gather KV positions

证据：`sparse_attn_kernel` 以 topk_idxs gather KV。

Harness 影响：上下文布局要减少噪声，保护 top-k candidate budget。

### P-031：sparse attention 有 learnable attn_sink bias

证据：`sparse_attn_kernel` 在 softmax 分母加入 attn_sink。

Harness 影响：模型有稳定兜底，但 Harness 仍要提供明确证据锚点。

### P-032：mHC Sinkhorn 是 kernel-level 实现，不是 Python 高层逻辑

证据：`hc_split_sinkhorn_kernel`。

Harness 影响：mHC 是核心推理路径，说明长链路稳定性是 V4 架构级目标。
