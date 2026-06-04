# 02-config-diff-pro-vs-flash.md — DeepSeek V4 Pro / Flash 配置差异 v0.1

> 日期：2026-06-04  
> 阶段：Phase 2 — config.json 参数拆解  
> 目标：从官方 config 建立 Pro / Flash / Base / Instruct 的结构差异底图。

---

## 1. 四个模型的定位

| 模型 | 类型 | 总参数 | 激活参数 | Context | 精度 |
|---|---|---:|---:|---:|---|
| DeepSeek-V4-Pro | Instruct | 1.6T | 49B | 1M | FP4 + FP8 Mixed |
| DeepSeek-V4-Flash | Instruct | 284B | 13B | 1M | FP4 + FP8 Mixed |
| DeepSeek-V4-Pro-Base | Base | 1.6T | 49B | 1M | FP8 Mixed |
| DeepSeek-V4-Flash-Base | Base | 284B | 13B | 1M | FP8 Mixed |

---

## 2. Pro vs Flash 顶层 config 差异

| 字段 | V4-Pro | V4-Flash | 初步解释 | Harness 影响 |
|---|---:|---:|---|---|
| `architectures` | `DeepseekV4ForCausalLM` | `DeepseekV4ForCausalLM` | 同架构族 | 可共用 Harness 协议 |
| `model_type` | `deepseek_v4` | `deepseek_v4` | 同模型类型 | 可共用 provider |
| `max_position_embeddings` | 1048576 | 1048576 | 均为 1M context | Agent 必须 long-context-first |
| `hidden_size` | 7168 | 4096 | Pro 宽度显著更大 | Pro 更适合复杂知识/推理 |
| `num_hidden_layers` | 61 | 43 | Pro 更深 | Pro 更适合长链路推理 |
| `num_attention_heads` | 128 | 64 | Pro head 数翻倍 | Pro attention 容量更强 |
| `num_key_value_heads` | 1 | 1 | MQA / MLA 风格 KV | 内部 KV 更省 |
| `q_lora_rank` | 1536 | 1024 | Pro query 低秩容量更大 | Pro 对复杂注意力更强 |
| `o_lora_rank` | 1024 | 1024 | 相同 | 暂无差异 |
| `o_groups` | 16 | 8 | Pro 输出分组更多 | Pro attention 输出容量更强 |
| `head_dim` | 512 | 512 | 相同 | 单 head 维度一致 |
| `qk_rope_head_dim` | 64 | 64 | 相同 | RoPE 子维度一致 |
| `index_n_heads` | 64 | 64 | 相同 | Indexer head 数一致 |
| `index_head_dim` | 128 | 128 | 相同 | Indexer 单 head 维度一致 |
| `index_topk` | 1024 | 512 | Pro sparse attention 可选更多压缩 KV 位置 | Pro 更适合 1M 长上下文复杂检索 |
| `sliding_window` | 128 | 128 | 局部窗口相同 | 长上下文依赖压缩/索引，不靠大 window |
| `n_routed_experts` | 384 | 256 | Pro 专家池更大 | Pro 知识/任务覆盖更强 |
| `n_shared_experts` | 1 | 1 | 相同 | 均有 shared expert |
| `num_experts_per_tok` | 6 | 6 | 每 token 激活专家数相同 | Flash 低成本来自专家池/维度/层数更小，而非 top-k 更低 |
| `num_hash_layers` | 3 | 3 | 前 3 层 hash routing | 早期 token-expert 路由更稳定 |
| `moe_intermediate_size` | 3072 | 2048 | Pro expert FFN 更宽 | Pro 单专家能力更强 |
| `routed_scaling_factor` | 2.5 | 1.5 | Pro 路由权重放大更高 | 后续需结合 Gate 代码解释 |
| `expert_dtype` | `fp4` | `fp4` | Instruct 版专家参数 FP4 | 成本/显存优化关键 |
| `quant_method` | `fp8` | `fp8` | 非 expert 多为 FP8 | 服务端效率关键 |
| `hc_mult` | 4 | 4 | mHC copies 相同 | 长链路稳定机制一致 |
| `hc_sinkhorn_iters` | 20 | 20 | mHC Sinkhorn 迭代相同 | 暂无差异 |
| `compress_rope_theta` | 160000 | 160000 | 压缩注意力 RoPE theta 相同 | HCA/CSA 共同设置 |
| `rope_scaling.factor` | 16 | 16 | YaRN 扩展从 64K 到 1M | 位置编码扩展一致 |
| `vocab_size` | 129280 | 129280 | 相同 | tokenizer 协议一致 |
| `num_nextn_predict_layers` | 1 | 1 | MTP 层数相同 | 流式推理体验可能一致 |

---

## 3. Base vs Instruct 的关键差异

### 3.1 `expert_dtype`

| 模型 | `expert_dtype` | 解释 |
|---|---|---|
| Pro-Base | `fp8` | Base 模型为 FP8 mixed |
| Flash-Base | `fp8` | Base 模型为 FP8 mixed |
| Pro Instruct | `fp4` | Instruct 版 MoE experts 使用 FP4 |
| Flash Instruct | `fp4` | Instruct 版 MoE experts 使用 FP4 |

初步判断：

- Base 用 FP8 expert，Instruct 用 FP4 expert。
- 这与模型卡中 “FP4 + FP8 Mixed: MoE expert parameters use FP4 precision; most other parameters use FP8” 一致。
- 对 Agent Harness 的直接影响不是“客户端要处理 FP4”，而是：Instruct API/部署版的成本、吞吐、显存模型与 Base 不同，模型路由和成本估计必须按 Instruct 版看。

---

## 4. `compress_ratios` 层级差异

### 4.1 Pro

```text
[128, 128, 4, 128, 4, 128, 4, 128, ... , 4, 0]
```

### 4.2 Flash

```text
[0, 0, 4, 128, 4, 128, 4, 128, ... , 4, 0]
```

### 4.3 初步解释

结合 `Attention` 源码：

- `compress_ratio = 0`：不启用 compressor，走纯 sliding-window attention。
- `compress_ratio = 4`：启用 `Compressor`，且创建 `Indexer`，也就是 learned top-k sparse attention 路径。
- `compress_ratio = 128`：启用 `Compressor`，但不创建 learned `Indexer`，而使用规则型 compressed top-k index。

因此：

- Pro 前两层已经启用 ratio=128 的压缩注意力。
- Flash 前两层是 ratio=0，即纯 sliding-window attention。
- 从第 3 层开始，二者都交替出现 ratio=4 和 ratio=128。
- 最后一层 ratio=0，回到纯 sliding-window。

### 4.4 对 Harness 的初步影响

这说明 1M context 在模型内部不是单一机制，而是分层混合机制：

1. 局部窗口负责最近上下文。
2. ratio=4 + Indexer 负责 learned sparse retrieval。
3. ratio=128 负责高度压缩的远程历史。
4. 不同层承担不同上下文聚合角色。

Agent Harness 不能把 1M context 当成普通长字符串。必须做：

- 当前目标 / hard constraints / Plan KR 放高可见度位置；
- 执行日志进入 checkpoint，而不是全量堆积；
- 历史文件和旧对话进入 index/summary；
- 对 1M 长任务设计“锚点区 + 当前工作区 + 压缩历史区”。

---

## 5. 第一批可确认物理特性

### P-001：Pro 和 Flash 是同架构族，不是两个完全不同模型

证据：`architectures = DeepseekV4ForCausalLM`，`model_type = deepseek_v4`。

Harness 影响：可以设计统一 DeepSeek V4 provider，然后在模型路由层切 Flash / Pro。

### P-002：Pro 的容量优势主要来自宽度、深度、专家池、index_topk

Pro 相比 Flash：

- hidden_size：7168 vs 4096
- num_layers：61 vs 43
- routed_experts：384 vs 256
- index_topk：1024 vs 512
- attention_heads：128 vs 64
- activated params：49B vs 13B

Harness 影响：Pro 应用于复杂规划、长上下文检索、关键审查、复杂 Agentic 任务。

### P-003：Flash 并不是“弱化到不能推理”，而是同机制小规模版本

Flash 保留：

- 1M context
- CSA/HCA 相关参数
- mHC
- 6 experts per token
- 3 hash layers
- FP4 + FP8 mixed
- thinking / non-thinking / max thinking

Harness 影响：默认 Flash-first 是合理的，复杂阶段再切 Pro。

### P-004：`index_topk` 是长上下文可见性的关键差异点

Pro top-k 1024，Flash top-k 512。

Harness 影响：同样 1M context，Pro 在 sparse attention 中可选择的压缩 KV 位置更多。长上下文任务中，Flash 需要更强的 Harness 帮它组织上下文；Pro 可以承载更复杂的长上下文检索。

### P-005：`sliding_window=128` 很小，说明最近上下文窗口只是局部机制

Harness 影响：不要以为模型会靠大 window 直接扫全局；它依赖 compressed/sparse attention 机制。Prompt 设计必须有结构化锚点。

### P-006：前三层 hash routing 提示早期路由有稳定性设计

Harness 影响：前几层专家选择与 token id 绑定，更偏稳定；后续 score routing 更动态。这个后续要和 Gate 源码一起拆。

### P-007：Instruct 版 MoE experts 使用 FP4

Harness 影响：成本/延迟估计应以 Instruct 版为准；FP4 expert 可能是 V4 API 经济性的核心来源之一。

---

## 6. 待继续验证的问题

1. `compress_ratios` 的每层分布是否与技术报告中的 HCA/CSA 层级设计完全对应？
2. `ratio=4` 的 Indexer top-k 是否就是 CSA？
3. `ratio=128` 是否对应 HCA 的 heavily compressed path？
4. Pro 前两层 ratio=128、Flash 前两层 ratio=0 的设计动机是什么？
5. `routed_scaling_factor` Pro=2.5 / Flash=1.5 对专家输出权重有什么影响？
6. mHC 的 `hc_mult=4` 是否意味着每层维持 4 份 hidden state manifold？
7. Max thinking 是否只是 prompt / decoding 策略，还是模型内部有不同控制路径？
