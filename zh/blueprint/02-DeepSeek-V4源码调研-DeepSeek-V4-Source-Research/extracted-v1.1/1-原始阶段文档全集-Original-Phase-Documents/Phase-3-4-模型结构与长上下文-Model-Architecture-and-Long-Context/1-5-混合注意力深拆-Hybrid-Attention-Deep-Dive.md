# 04-hybrid-attention-deep-dive.md — DeepSeek V4 Hybrid Attention 深拆 v0.1

> 日期：2026-06-04  
> 阶段：Phase 4 — Hybrid Attention 深拆  
> 目标：拆清楚 V4 的 1M context 是如何通过 Sliding Window + HCA + CSA 实现的，以及这对 Agent Harness 的上下文布局有什么要求。

---

## 1. 总体结论

DeepSeek V4 的长上下文能力不是“把 attention window 放到 1M”，而是三层机制叠加：

```text
1. Sliding Window Attention
   - window_size = 128
   - 负责最近 token 的精确局部注意力

2. HCA / Heavily Compressed Attention
   - compress_ratio = 128
   - 把远程历史每 128 个 token 压缩为一个 compressed KV
   - 通过规则 top-k index 接入 sparse_attn

3. CSA / Compressed Sparse Attention
   - compress_ratio = 4
   - 用 learned Compressor 生成更细粒度 compressed KV
   - 用 learned Indexer 选择 top-k compressed KV positions
   - Pro index_topk=1024，Flash index_topk=512
```

所以 1M context 的真实语义是：

> 模型拥有 1M 位置空间，但远程历史主要通过压缩与稀疏检索进入注意力；不是所有 token 都被同等注意。

---

## 2. Attention 层初始化逻辑

源码 `Attention.__init__` 中，每层读：

```python
self.compress_ratio = args.compress_ratios[layer_id]
```

然后：

```python
if self.compress_ratio:
    self.compressor = Compressor(...)
    if self.compress_ratio == 4:
        self.indexer = Indexer(...)
    else:
        self.indexer = None
```

解释：

| `compress_ratio` | 行为 | 机制判断 |
|---:|---|---|
| 0 | 不创建 Compressor / Indexer | 纯 sliding-window attention |
| 4 | 创建 Compressor + Indexer | learned compressed sparse attention，疑似 CSA 主路径 |
| 128 | 创建 Compressor，不创建 Indexer | heavily compressed attention，疑似 HCA 主路径 |

---

## 3. 每层 compress pattern

### 3.1 V4-Pro

```text
[128, 128, 4, 128, 4, 128, ..., 4, 0]
```

特点：

- 第 0、1 层：HCA ratio=128。
- 第 2 层开始：CSA ratio=4 与 HCA ratio=128 交替。
- 最后一层：ratio=0，纯 sliding-window。

### 3.2 V4-Flash

```text
[0, 0, 4, 128, 4, 128, ..., 4, 0]
```

特点：

- 第 0、1 层：纯 sliding-window。
- 第 2 层开始：CSA/HCA 交替。
- 最后一层：纯 sliding-window。

### 3.3 初步解释

Pro 前两层直接压缩历史，说明 Pro 从低层就开始构建远程上下文压缩表征；Flash 前两层保持局部窗口，可能是为了更低成本和更稳定的局部特征提取。

对 Harness 的启发：

- Flash 对 prompt layout 更敏感，早期层无法直接利用压缩历史。
- Pro 更适合“长上下文远程证据召回”。
- 复杂长任务中，Flash 应配合更强的上下文锚点和摘要结构。

---

## 4. Sliding Window 机制

源码通过：

```python
topk_idxs = get_window_topk_idxs(win, bsz, seqlen, start_pos)
```

其中 `win = self.window_size = 128`。

含义：

- 每个 token 默认能精确关注最近 128 个 token。
- decode 阶段 KV cache 是 ring buffer：`start_pos % win`。
- 最近上下文永远是最可靠的精确信息区。

Harness 结论：

- 当前任务目标、当前子步骤、最近工具结果、当前文件 diff 必须靠近上下文尾部。
- 不要把关键验收条件只放在很早的历史里。
- “当前工作区”应永远短而强。

---

## 5. Compressor：HCA / compressed KV 的核心

### 5.1 Compressor 做什么

源码注释：

```python
Compresses KV cache via learned gated pooling over `compress_ratio` consecutive tokens.
When overlap=True (ratio==4), uses overlapping windows for smoother compression boundaries.
```

也就是说，Compressor 不是简单平均池化，而是：

```text
x
 ↓
wkv(x)    → 候选 KV
wgate(x)  → token-level gate score
ape       → absolute position embedding inside compression block
softmax(score)
 ↓
weighted sum over compress_ratio tokens
 ↓
compressed KV
```

### 5.2 ratio=4 的 overlap

```python
self.overlap = compress_ratio == 4
coff = 1 + self.overlap
```

当 ratio=4 时，Compressor 使用 overlapping windows：

- 一半维度用于 overlapping compression。
- 一半维度用于 normal compression。
- 这使边界更平滑，减少 “4 token block” 的割裂。

推论：

- ratio=4 是更精细、可学习、边界更平滑的压缩注意力。
- 它很可能对应 CSA 的核心压缩路径。

### 5.3 ratio=128 的无 overlap

当 ratio=128：

- 每 128 tokens 被压缩成一个 KV。
- 不使用 learned Indexer。
- 后续通过 `get_compress_topk_idxs` 规则接入。

推论：

- ratio=128 是极强压缩的远程历史路径。
- 更像 HCA，用很少 KV cache 承载长上下文大范围历史。

---

## 6. Indexer：CSA 的 learned retrieval

### 6.1 Indexer 做什么

源码注释：

```python
Selects top-k compressed KV positions for sparse attention via learned scoring.
Has its own Compressor (with Hadamard rotation) to build compressed KV for scoring.
```

流程：

```text
qr from Attention low-rank query
 ↓
Indexer wq_b
 ↓
RoPE
 ↓
Hadamard rotation
 ↓
FP4 quant simulation
 ↓
Indexer internal Compressor builds scoring KV
 ↓
einsum(q, kv_cache)
 ↓
relu + learned weights projection
 ↓
sum over index heads
 ↓
topk(index_topk)
```

### 6.2 Pro vs Flash 的 Indexer 容量

| 模型 | index_topk | 含义 |
|---|---:|---|
| Pro | 1024 | 每个 token 最多选择 1024 个 compressed positions |
| Flash | 512 | 每个 token 最多选择 512 个 compressed positions |

注意：这个 top-k 是 compressed KV position，不是原始 token position。若 ratio=4，则：

- Pro 理论覆盖约 1024 × 4 = 4096 原始 token 粒度的候选压缩窗口。
- Flash 理论覆盖约 512 × 4 = 2048 原始 token 粒度的候选压缩窗口。

这是粗略直觉，不等于真实可见 token 数，因为 compressed KV 是 learned pooling 后的信息载体。

Harness 结论：

- Pro 在长上下文 selective retrieval 上更强。
- Flash 在 1M 上下文里更需要“少而强”的上下文锚点。
- 对 Flash，必须避免无意义历史噪声挤占 indexer 选择预算。

---

## 7. Attention forward 的真实路径

### 7.1 查询 q

```python
qr = q = q_norm(wq_a(x))
q = wq_b(q)
q = normalize(q)
RoPE(q[..., -rd:])
```

V4 使用 low-rank query projection：

```text
hidden dim → q_lora_rank → q heads
```

Pro 的 `q_lora_rank=1536`，Flash 是 1024。

### 7.2 当前 window KV

```python
kv = wkv(x)
kv = kv_norm(kv)
RoPE(kv[..., -rd:])
act_quant(kv[..., :-rd])
topk_idxs = get_window_topk_idxs(window_size=128)
```

最近 128 token 是精确信息通道。

### 7.3 压缩路径

如果 `compress_ratio != 0`：

```python
if indexer:
    compress_topk_idxs = indexer(...)
else:
    compress_topk_idxs = get_compress_topk_idxs(...)
topk_idxs = concat(window_topk, compress_topk)
```

也就是说，最终 sparse attention 的候选集合是：

```text
局部 window candidates + compressed history candidates
```

### 7.4 sparse_attn

最终：

```python
o = sparse_attn(q, kv_or_kv_cache, attn_sink, topk_idxs, softmax_scale)
```

这说明 attention 本身不是 dense 矩阵，而是按 topk_idxs 提供的稀疏位置执行。

---

## 8. 上下文布局规则：给 DeepSeek Agent Harness

### Rule 1：上下文必须分层

建议 DeepSeek Agent 每轮上下文布局：

```text
[Stable System Prefix]
  - Agent identity
  - Tool schema
  - Hard constraints
  - Memory / Skill index

[Task Anchor Zone]
  - Current objective
  - Plan KR
  - Success criteria
  - Safety/permission constraints

[Active Working Set]
  - 当前文件片段
  - 当前 diff
  - 最近工具结果
  - 当前错误日志

[Compressed History Zone]
  - checkpoint snapshots
  - architecture decisions
  - compacted execution history
  - document indexes

[Turn Tail]
  - 用户最新请求
  - 本轮临时信息
```

### Rule 2：最近 128 token 是最可靠精确信息区

由于 `window_size=128`，每次关键工具调用前，应把“当前意图 + 约束 + 操作对象”重新放到尾部附近。

### Rule 3：长历史不要原样堆，改成 checkpoint snapshot

原始执行日志在远程历史里会被压缩，细节无法保证恢复。应该生成：

```text
目标
已完成步骤
关键输出
失败/异常
剩余计划
当前约束
下一步需要模型判断的问题
```

### Rule 4：Plan 应是 attention-anchor plan graph

Plan 不应只是长 checklist，而应分为：

```text
Plan ID
Current Step ID
Parent Goal
Key Result
Dependencies
Blocking Constraints
Rollback Condition
```

这些字段短、稳定、结构化，适合被 sparse attention / indexer 选中。

### Rule 5：Flash-first 需要更强布局纪律

Flash index_topk=512，Pro=1024。Flash 用 1M context 时，Harness 应：

- 限制历史噪声；
- 强化当前目标；
- 更频繁生成 checkpoint；
- 对复杂长上下文 review 切 Pro。

### Rule 6：System Prefix 必须 byte-stable

这不是本文件的核心，但与 Hybrid Attention 共同决定 Harness：

- API prefix cache 要求字节稳定；
- 模型内部 long-context retrieval 要求上下文结构稳定；
- 因此 Agent Harness 必须有稳定的 prefix protocol 和可变的 turn tail。

---

## 9. 新增物理特性编号

### P-013：V4 的 attention 候选集合 = local window + compressed history

证据：`Attention.forward` 先取 `get_window_topk_idxs`，再 concat compressed top-k indices。

Harness 影响：当前工作区和压缩历史区都必须设计，不可只依赖其中之一。

### P-014：`compress_ratio=4` 会启用 learned Indexer

证据：`if self.compress_ratio == 4: self.indexer = Indexer(...)`。

Harness 影响：ratio=4 层承担 learned sparse retrieval，关键历史内容应短而可识别。

### P-015：`compress_ratio=128` 不启用 learned Indexer

证据：ratio 非 4 时 `self.indexer = None`，使用 `get_compress_topk_idxs`。

Harness 影响：这一路更像规则型远程压缩历史，适合承载概览而非精细证据。

### P-016：窗口大小只有 128

证据：config `sliding_window=128`，源码 `window_size=args.window_size`。

Harness 影响：最近上下文窗口非常宝贵，必须放当前操作的必要信息。

### P-017：Indexer 自带 Compressor，并用 Hadamard rotation + FP4 quant simulation

证据：`Indexer` 内部 `self.compressor = Compressor(..., rotate=True)`，forward 中 `rotate_activation(q)` 与 `fp4_act_quant(q)`。

Harness 影响：V4 的检索路径是为低精度/高效 sparse selection 训练的，不适合无结构噪声上下文。

---

## 10. 待技术报告确认

1. 官方是否把 ratio=4 明确定义为 CSA。
2. 官方是否把 ratio=128 明确定义为 HCA。
3. CSA / HCA 在训练中的具体配比和层级原因。
4. mHC 与 Hybrid Attention 的交互关系。
5. V4-Pro 27% FLOPs / 10% KV cache 的精确定义。
