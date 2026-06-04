# 05-moe-routing-analysis.md — DeepSeek V4 MoE / Routing / Hash Layer 深拆 v0.1

> 日期：2026-06-04  
> 阶段：Phase 5 — MoE / Routing / Hash Layer 深拆  
> 目标：基于 `inference/model.py::Gate / Expert / MoE` 和 Pro / Flash config，拆清楚 V4 的专家路由机制，以及 Flash / Pro 为什么便宜/为什么强。

---

## 1. 总体结论

DeepSeek V4 的 MoE 机制可以概括为：

```text
每个 token
  ↓
Gate 计算 n_routed_experts 个专家分数
  ↓
前 n_hash_layers 层：使用 token_id → expert_id 的固定 hash routing
后续层：使用 score-based top-k routing
  ↓
选择 top-k routed experts
  ↓
每个 selected expert 输出 SwiGLU FFN
  ↓
按 route weights 加权求和
  ↓
再加 1 个 shared expert 输出
```

核心发现：

1. Pro / Flash 都是 **每 token 6 个 routed experts + 1 个 shared expert**。
2. Flash 不是靠减少每 token 激活专家数变便宜，而是靠：
   - hidden size 更小；
   - layer 数更少；
   - routed expert 总数更少；
   - expert intermediate size 更小；
   - route scaling 更低；
   - index_topk 更小。
3. 前 3 层使用 hash routing，专家索引由 token id 决定；后续层使用 score-based routing。
4. Instruct 版 routed experts 使用 FP4 权重，shared expert 未显式传 `expert_dtype=fp4`，因此 shared expert 走默认 dtype 路径。

---

## 2. Pro / Flash MoE 参数对比

| 字段 | V4-Pro | V4-Flash | 解释 |
|---|---:|---:|---|
| `hidden_size` | 7168 | 4096 | Pro token 表征宽度更大 |
| `num_hidden_layers` | 61 | 43 | Pro 更深 |
| `n_routed_experts` | 384 | 256 | Pro 专家池更大 |
| `num_experts_per_tok` | 6 | 6 | 每 token 激活 routed experts 数相同 |
| `n_shared_experts` | 1 | 1 | 都有 1 个 shared expert |
| `num_hash_layers` | 3 | 3 | 前 3 层 hash routing |
| `moe_intermediate_size` | 3072 | 2048 | Pro 每个 expert 更宽 |
| `routed_scaling_factor` | 2.5 | 1.5 | Pro routed expert 输出权重放大更强 |
| `expert_dtype` | fp4 | fp4 | Instruct 版 routed experts FP4 |
| `scoring_func` | sqrtsoftplus | sqrtsoftplus | 路由分数函数一致 |

---

## 3. Gate 源码拆解

### 3.1 初始化逻辑

`Gate.__init__` 做了几件事：

```python
self.topk = args.n_activated_experts
self.score_func = args.score_func
self.route_scale = args.route_scale
self.hash = layer_id < args.n_hash_layers
self.weight = nn.Parameter(torch.empty(args.n_routed_experts, args.dim))
```

如果是 hash 层：

```python
self.tid2eid = nn.Parameter(
    torch.empty(args.vocab_size, args.n_activated_experts, dtype=torch.int32),
    requires_grad=False
)
self.bias = None
```

如果不是 hash 层：

```python
self.bias = nn.Parameter(torch.empty(args.n_routed_experts, dtype=torch.float32))
```

解释：

- 前 `num_hash_layers=3` 层，不通过 topk score 选专家，而是由 token id 查表得到 expert ids。
- 后续层使用 score + bias 做 top-k expert selection。
- bias 只影响 expert selection，不影响 routing weights。

---

## 4. Gate forward 流程

```text
x
 ↓
linear(x, gate_weight)
 ↓
score_func: softmax / sigmoid / sqrtsoftplus
 ↓
original_scores = scores
 ↓
如果非 hash 层：scores += bias
 ↓
如果 hash 层：indices = tid2eid[input_ids]
否则：indices = topk(scores)
 ↓
weights = original_scores.gather(indices)
 ↓
如果不是 softmax：weights 归一化
 ↓
weights *= route_scale
 ↓
return weights, indices
```

### 4.1 关键点：bias 只影响选专家，不影响权重

源码注释：

```text
Bias shifts scores for expert selection (topk) but does not affect routing weights.
```

也就是说：

```text
专家选择：scores + bias
专家权重：original_scores
```

这是一种把“负载/路由选择”和“语义权重”分离的设计。

### 4.2 `sqrtsoftplus` 路由函数

Pro / Flash 都使用：

```python
scores = F.softplus(scores).sqrt()
```

随后对 selected weights 归一化，再乘 `route_scale`。

初步理解：

- `softplus` 保证正值且更平滑；
- `sqrt` 压缩大分数，可能减少极端 routing weight；
- 再通过 `route_scale` 控制 routed expert 总强度；
- Pro 的 route_scale=2.5，Flash=1.5，说明 Pro 更强依赖 routed experts 的专业能力。

---

## 5. Hash Routing：前三层专家由 token id 决定

### 5.1 源码行为

前 `n_hash_layers=3` 层：

```python
self.hash = layer_id < args.n_hash_layers
indices = self.tid2eid[input_ids]
```

因此前 3 层专家选择不是动态 semantic routing，而是 token-id routing。

### 5.2 物理意义

这意味着 V4 的前几层更像：

```text
token identity / lexical features → fixed experts
```

后续层才是：

```text
contextual hidden state → dynamic experts
```

这可能带来两个好处：

1. 早期层路由更稳定，不受上下文轻微扰动影响；
2. 高频 token / 特殊 token / 结构化 token 可以学到稳定的专家路径。

### 5.3 对 Agent Harness 的启发

结构化 token 和固定标记可能更有价值，例如：

```text
[CURRENT_GOAL]
[PLAN_STEP]
[CONSTRAINT]
[ACTIVE_FILE]
[ERROR]
[CHECKPOINT]
```

由于前三层有 token-id based routing，稳定的标签和格式可能帮助模型形成更稳定的早期表征路径。

---

## 6. Expert 源码拆解

每个 Expert 是 SwiGLU FFN：

```python
gate = w1(x).float()
up = w3(x).float()
x = silu(gate) * up
if weights is not None:
    x = weights * x
return w2(x.to(dtype))
```

关键点：

1. `w1/w2/w3` 都是 `Linear`，可走 FP4 / FP8 / BF16。
2. gate 和 up 在 float32 中计算，提高稳定性。
3. routed expert 的输出在 expert 内部被 route weight 加权。
4. `swiglu_limit=10.0` 时，会 clamp up/gate，抑制极端激活。

### 对 Harness 的启发

这不是直接客户端可控的机制，但它说明：

- V4 在 MoE 输出稳定性上有显式工程约束；
- 对于长任务，不能假设模型完全确定性，专家路由仍可能受上下文扰动；
- 因此 Harness 要用 checkpoint/review 保证任务稳定性，而不是依赖一次长上下文自洽。

---

## 7. MoE forward 源码拆解

核心流程：

```python
shape = x.size()
x = x.view(-1, dim)

weights, indices = gate(x, input_ids.flatten())

y = zeros_like(x, float32)
counts = bincount(indices.flatten())

for each local expert:
    if counts[i] == 0: continue
    idx, top = where(indices == i)
    y[idx] += expert(x[idx], weights[idx, top, None])

if world_size > 1:
    all_reduce(y)

y += shared_experts(x)

return y.view(shape)
```

解释：

- 每个 token 可以进入多个专家；
- 每个 expert 批量处理被分配到它的 token；
- routed expert 输出加权累加；
- 最后加 shared expert；
- TP 多卡时做 all_reduce。

---

## 8. Shared Expert 的特殊性

源码中：

```python
expert_dtype = torch.float4_e2m1fn_x2 if args.expert_dtype == "fp4" else None
self.experts = Expert(..., dtype=expert_dtype)
self.shared_experts = Expert(args.dim, args.moe_inter_dim, swiglu_limit=args.swiglu_limit)
```

注意：`shared_experts` 没有传入 `dtype=expert_dtype`。

这意味着在官方 inference demo 里：

- routed experts 使用 FP4；
- shared expert 使用默认 dtype，即 `default_dtype`，通常是 FP8。

初步推断：

- Routed experts 是海量专家池，参数量最大，所以用 FP4 压缩；
- Shared expert 是全 token 都会走的公共能力通道，保留更高精度可能更稳定。

这需要后续结合 `convert.py` 和权重 dtype 进一步确认。

---

## 9. Pro 为什么强，Flash 为什么便宜

### 9.1 Pro 的强来自哪里

Pro 相比 Flash：

```text
hidden_size: 7168 vs 4096
layers: 61 vs 43
routed_experts: 384 vs 256
moe_intermediate_size: 3072 vs 2048
attention_heads: 128 vs 64
q_lora_rank: 1536 vs 1024
index_topk: 1024 vs 512
route_scale: 2.5 vs 1.5
activated params: 49B vs 13B
```

因此 Pro 更强主要来自：

1. 更大的表征维度；
2. 更深的层数；
3. 更大的专家池；
4. 更大的专家 FFN；
5. 更高的 sparse retrieval top-k；
6. 更强的 routed expert scale。

### 9.2 Flash 为什么便宜

Flash 并没有减少 `num_experts_per_tok`，仍然是 6 个 routed experts + 1 shared expert。

Flash 低成本来自：

1. hidden size 小；
2. layers 少；
3. experts 总数少；
4. expert FFN 小；
5. index_topk 小；
6. 前两层无压缩 attention；
7. activated params 只有 13B。

---

## 10. 新增物理特性编号

### P-018：V4 前 3 层使用 token-id hash routing

证据：`Gate` 中 `self.hash = layer_id < args.n_hash_layers`，hash 层通过 `tid2eid[input_ids]` 获得专家索引。

Harness 影响：稳定结构化标签可能帮助早期 token 表征；Agent prompt 格式应固定、短标签化、少变化。

### P-019：Pro / Flash 每 token activated routed experts 数相同

证据：Pro / Flash config 均 `num_experts_per_tok=6`。

Harness 影响：Flash 低成本不是因为每 token 少激活专家；不能简单认为 Flash 是“少思考版”，而是小型同构模型。

### P-020：Pro route scale 高于 Flash

证据：Pro `routed_scaling_factor=2.5`，Flash `1.5`。

Harness 影响：Pro 对 routed expert 的专业输出依赖更强，适合复杂知识、架构、审查、agentic workflow。

### P-021：Routed experts 使用 FP4，shared expert 保持默认 dtype

证据：`MoE` 中 routed experts 传 `expert_dtype`，shared expert 未传。

Harness 影响：V4 的经济性高度依赖专家池低精度压缩；复杂公共能力可能通过 shared expert 稳定承载。

### P-022：MoE 输出是 routed experts 加权和 + shared expert

证据：`MoE.forward` 中 `y[idx] += expert(...)` 后 `y += self.shared_experts(x)`。

Harness 影响：每个 token 既走专业路径也走公共路径；这支持“Flash 能做大量通用任务，Pro 做复杂专业任务”的产品路由。
