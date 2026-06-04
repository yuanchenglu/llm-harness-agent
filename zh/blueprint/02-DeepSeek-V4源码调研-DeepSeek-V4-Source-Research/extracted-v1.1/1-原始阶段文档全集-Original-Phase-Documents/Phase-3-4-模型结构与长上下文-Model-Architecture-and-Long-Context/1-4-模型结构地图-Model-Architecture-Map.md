# 03-model-architecture-map.md — DeepSeek V4 模型结构拆解 v0.1

> 日期：2026-06-04  
> 阶段：Phase 3 — ModelArgs 与模型总结构拆解  
> 目标：从 `inference/model.py` 建立 DeepSeek V4 的主结构、模块职责、forward 主流程。

---

## 1. 总体判断

DeepSeek V4 不是“普通 Transformer + MoE”的简单版本，而是由以下机制组合而成：

```text
Token Embedding
  ↓
Hyper-Connections expand: [b, s, d] → [b, s, hc_mult, d]
  ↓
N × Block:
    HC pre-mix: hc_mult hidden copies → 1 hidden stream
    RMSNorm
    MLA + Sliding Window + HCA/CSA Hybrid Attention
    HC post-mix: attention output + residual hc copies → hc_mult copies
    HC pre-mix
    RMSNorm
    MoE FFN: routed experts + shared expert
    HC post-mix
  ↓
HC Head: hc_mult copies → 1 hidden stream
  ↓
RMSNorm + ParallelHead
  ↓
Logits
```

关键点：V4 的 residual 不是传统 `x + f(norm(x))`，而是 mHC 维护 `hc_mult=4` 份 hidden state，在每个 Attention / MoE 前后做 learned mixing。

---

## 2. `ModelArgs` 参数分组

源码 `ModelArgs` 的字段可以分为 8 类。

### 2.1 基础运行参数

| 字段 | 含义 | Pro | Flash |
|---|---|---:|---:|
| `max_batch_size` | demo 最大 batch | config 外推 | config 外推 |
| `max_seq_len` / `max_position_embeddings` | 最大上下文长度 | 1,048,576 | 1,048,576 |
| `dtype` | 默认权重 dtype | fp8 | fp8 |
| `scale_fmt` | scale 格式 | ue8m0 | ue8m0 |
| `scale_dtype` | scale dtype | fp8 | fp8 |
| `expert_dtype` | MoE expert dtype | fp4 | fp4 |

### 2.2 模型宽度与深度

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `dim` / `hidden_size` | 7168 | 4096 | Pro 宽度更大 |
| `n_layers` / `num_hidden_layers` | 61 | 43 | Pro 更深 |
| `vocab_size` | 129280 | 129280 | tokenizer 一致 |

### 2.3 Attention / MLA

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `n_heads` | 128 | 64 | Pro attention heads 更多 |
| `head_dim` | 512 | 512 | 单 head 维度一致 |
| `rope_head_dim` | 64 | 64 | RoPE 子维度一致 |
| `q_lora_rank` | 1536 | 1024 | Pro query 低秩容量更大 |
| `o_lora_rank` | 1024 | 1024 | 一致 |
| `o_groups` | 16 | 8 | Pro 输出分组更多 |
| `window_size` | 128 | 128 | 局部窗口一致，且非常小 |

### 2.4 Hybrid Attention / Index

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `compress_ratios` | `[128,128,4,128,...,0]` | `[0,0,4,128,...,0]` | Pro 前两层启用压缩，Flash 前两层纯 window |
| `index_n_heads` | 64 | 64 | Indexer head 数一致 |
| `index_head_dim` | 128 | 128 | Indexer 单 head 维度一致 |
| `index_topk` | 1024 | 512 | Pro sparse retrieval 容量更大 |
| `compress_rope_theta` | 160000 | 160000 | 压缩路径位置编码一致 |

### 2.5 MoE

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `n_routed_experts` | 384 | 256 | Pro 专家池更大 |
| `n_shared_experts` | 1 | 1 | 均有 shared expert |
| `n_activated_experts` / `num_experts_per_tok` | 6 | 6 | 每 token 激活专家数一致 |
| `n_hash_layers` | 3 | 3 | 前 3 层 hash routing |
| `moe_inter_dim` | 3072 | 2048 | Pro expert FFN 更宽 |
| `score_func` | sqrtsoftplus | sqrtsoftplus | 一致 |
| `route_scale` | 2.5 | 1.5 | Pro 路由权重放大更高 |

### 2.6 mHC

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `hc_mult` | 4 | 4 | 每 token 维持 4 份 hidden copy |
| `hc_sinkhorn_iters` | 20 | 20 | Sinkhorn 混合迭代一致 |
| `hc_eps` | 1e-6 | 1e-6 | 稳定项一致 |

### 2.7 YaRN / RoPE

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `original_seq_len` / `original_max_position_embeddings` | 65536 | 65536 | 从 64K 扩到 1M |
| `rope_factor` | 16 | 16 | 64K × 16 = 1M |
| `beta_fast` | 32 | 32 | 一致 |
| `beta_slow` | 1 | 1 | 一致 |

### 2.8 MTP

| 字段 | Pro | Flash | 影响 |
|---|---:|---:|---|
| `n_mtp_layers` / `num_nextn_predict_layers` | 1 | 1 | 均有一个 MTP block |

---

## 3. 核心类职责表

| 类 / 函数 | 职责 | 是否 V4 关键 |
|---|---|---|
| `ParallelEmbedding` | vocab 维度并行 embedding | 中 |
| `Linear` | 自动选择 BF16 / FP8 / FP4 GEMM | 高 |
| `precompute_freqs_cis` | YaRN RoPE 频率预计算 | 高 |
| `get_window_topk_idxs` | 局部 window top-k index | 高 |
| `get_compress_topk_idxs` | 规则压缩路径 index | 高 |
| `Compressor` | HCA：把连续 token 压缩成 compressed KV | 极高 |
| `Indexer` | CSA：learned scoring 选择 top-k compressed KV | 极高 |
| `Attention` | MLA + window + compressor + indexer + sparse_attn | 极高 |
| `Gate` | MoE 专家路由：hash routing / score routing | 高 |
| `Expert` | SwiGLU expert FFN | 中 |
| `MoE` | top-k routed experts + shared expert | 高 |
| `Block` | mHC + Attention + MoE | 极高 |
| `ParallelHead` | HC head + logits | 中 |
| `MTPBlock` | 多 token prediction 辅助预测 | 中 |
| `Transformer` | 总模型主流程 | 极高 |

---

## 4. V4 forward 主流程

### 4.1 Transformer forward

```python
h = embed(input_ids)                         # [b, s, d]
h = h.unsqueeze(2).repeat(1, 1, hc_mult, 1)   # [b, s, 4, d]
for layer in layers:
    h = layer(h, start_pos, input_ids)
logits = head(h, hc_head_fn, hc_head_scale, hc_head_base, norm)
```

关键解释：

- 输入 embedding 后不直接进入 block，而是复制成 `hc_mult=4` 份。
- 每个 block 都在 4 份 hidden copies 上工作。
- 最后 head 再把 4 份 hidden copy 混合成一个 hidden stream 计算 logits。

### 4.2 Block forward

每个 block 结构：

```python
residual = x
x, post, comb = hc_pre(x, hc_attn_fn, ...)
x = attn_norm(x)
x = attn(x, start_pos)
x = hc_post(x, residual, post, comb)

residual = x
x, post, comb = hc_pre(x, hc_ffn_fn, ...)
x = ffn_norm(x)
x = ffn(x, input_ids)
x = hc_post(x, residual, post, comb)
```

这说明：

- Attention 前先把 4 份 hidden copy 通过 `hc_pre` 混成 1 份。
- Attention 输出后，通过 `hc_post` 与 residual hidden copies 重新混成 4 份。
- MoE 前后重复同样模式。
- 所以 mHC 是贯穿全模型的信号传播机制，不是边缘优化。

---

## 5. 与普通 Transformer 的差异

| 普通 Transformer | DeepSeek V4 |
|---|---|
| residual 是 `x + f(norm(x))` | residual 是 mHC 多副本 manifold mixing |
| dense attention 或简单 sparse attention | sliding window + HCA + CSA hybrid attention |
| KV cache 常规存储 | compressed KV cache + window KV cache |
| 所有层 attention 机制基本一致 | 每层由 `compress_ratios` 决定是否纯 window / HCA / CSA |
| MLP 是 dense FFN 或普通 MoE | hash routing + score routing MoE + shared expert |
| 长上下文靠扩大 window / RoPE | YaRN + compressed sparse retrieval + HCA |
| 输出 head 直接 norm+linear | HC head 混合后再 norm+linear |

---

## 6. 对 DeepSeek Agent Harness 的初步约束

### H-001：不要把 1M context 当作“平铺记忆”

因为模型内部 attention 是 window + compressed sparse retrieval。Harness 应设计上下文布局，而不是简单累积历史。

### H-002：关键 token 必须成为“可检索锚点”

由于远程历史依赖 compressed/indexed KV，hard constraints、Plan KR、当前目标、活动文件索引应短、稳定、结构化，并在上下文中有高可见度。

### H-003：Flash 需要更强 Harness 辅助

Flash 的 `index_topk=512`，Pro 是 1024；Flash 前两层还是纯 window，不启用压缩。相同 1M context 下，Flash 对上下文组织更敏感。

### H-004：长任务应切 checkpoint，不应把执行日志全量塞入

历史执行日志很容易进入 compressed 历史区，不保证细节被精确恢复。应在关键节点生成 checkpoint snapshot。

### H-005：Pro 用于复杂长上下文检索和关键审查

Pro 更深、更宽、index_topk 更大、专家池更大，适合复杂 planning、review、long-context QA、agentic workflows。

---

## 7. 待继续验证

1. `compress_ratio=4` 是否与论文中的 CSA 完全对应。
2. `compress_ratio=128` 是否与 HCA 完全对应。
3. mHC 在技术报告中如何定义 manifold constraint。
4. MTP 在推理时是否实际用于 speculative / next-token acceleration。
5. `attn_sink` 在 sparse_attn 中如何影响 attention 分布。
