# 06-mhc-hyperconnections-analysis.md — DeepSeek V4 mHC / Hyper-Connections 深拆 v0.1

> 日期：2026-06-04  
> 阶段：Phase 6 — mHC / Hyper-Connections 深拆  
> 目标：基于 `Block.hc_pre / hc_post / ParallelHead.hc_head / kernel.hc_split_sinkhorn`，拆清楚 V4 如何替代传统 residual connection，以及这对长任务稳定性有什么启发。

---

## 1. 总体结论

DeepSeek V4 使用 Manifold-Constrained Hyper-Connections（mHC）来增强传统 residual connection。

普通 Transformer block：

```text
x = x + Attention(Norm(x))
x = x + MLP(Norm(x))
```

DeepSeek V4 block：

```text
x has hc_mult copies: [b, s, hc, d]

Attention 前：
  hc_pre: hc copies → 1 hidden stream

Attention 后：
  hc_post: attention output + residual hc copies → hc copies

MoE 前：
  hc_pre: hc copies → 1 hidden stream

MoE 后：
  hc_post: moe output + residual hc copies → hc copies
```

V4 默认 `hc_mult=4`，即每个 token 在模型内部不是一份 hidden state，而是 4 份 hidden state copies。

---

## 2. Transformer 层面的 HC expand / HC head

### 2.1 输入扩展

`Transformer.forward`：

```python
h = self.embed(input_ids)
h = h.unsqueeze(2).repeat(1, 1, self.hc_mult, 1)
```

解释：

```text
[b, s, d] → [b, s, 4, d]
```

从第一层开始，每个 token 就有 4 份 hidden copy。

### 2.2 输出混合

最后：

```python
logits = self.head(h, self.hc_head_fn, self.hc_head_scale, self.hc_head_base, self.norm)
```

`ParallelHead.hc_head` 会通过 sigmoid weights 把 4 份 hidden copy 混成 1 份 hidden stream，再 norm + lm_head。

---

## 3. Block 内部 mHC 流程

每个 Block：

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

这说明 mHC 是：

```text
Attention 子层一套 HC
MoE 子层一套 HC
最终输出 head 一套 HC
```

不是局部 trick，而是贯穿全模型的主结构。

---

## 4. `hc_pre` 源码解释

```python
x = x.flatten(2).float()
rsqrt = torch.rsqrt(x.square().mean(-1, keepdim=True) + norm_eps)
mixes = F.linear(x, hc_fn) * rsqrt
pre, post, comb = hc_split_sinkhorn(...)
y = torch.sum(pre.unsqueeze(-1) * x.view(shape), dim=2)
return y, post, comb
```

### 4.1 输入

```text
x: [batch, seq, hc, dim]
```

### 4.2 输出

```text
y: [batch, seq, dim]
post: [batch, seq, hc]
comb: [batch, seq, hc, hc]
```

### 4.3 作用

`hc_pre` 做两件事：

1. 用 `pre` 权重把 4 份 hidden copy 混成 1 份，供 Attention/MoE 使用；
2. 同时计算 `post` 和 `comb`，供子层输出后写回 4 份 hidden copy。

---

## 5. `hc_post` 源码解释

```python
y = post.unsqueeze(-1) * x.unsqueeze(-2) + torch.sum(
    comb.unsqueeze(-1) * residual.unsqueeze(-2), dim=2
)
```

解释：

```text
new hidden copies =
  post * sublayer_output
  +
  comb * old residual hidden copies
```

也就是说，mHC 的 residual 不是简单加法，而是：

```text
每份新 hidden copy =
  当前子层输出的一部分
  +
  旧 4 份 hidden copy 的一个混合
```

这比传统 residual 更像“多通道记忆状态更新”。

---

## 6. `hc_split_sinkhorn` 核心机制

`hc_split_sinkhorn` 把 `mixes` 切成三类：

```text
pre:  [hc]
post: [hc]
comb: [hc, hc]
```

在 kernel 中：

### 6.1 pre

```text
pre = sigmoid(mix * scale + base) + eps
```

用于把 hc copies 混成单一 stream。

### 6.2 post

```text
post = 2 * sigmoid(mix * scale + base)
```

用于把子层输出注入每个 copy。

### 6.3 comb

`comb` 先 softmax，再反复做行/列归一化，也就是 Sinkhorn normalization。

最终 `comb` 近似一个双随机矩阵：

```text
每一行约归一
每一列约归一
```

### 6.4 为什么重要

这意味着 old hidden copies 的混合不是任意矩阵，而是被约束到稳定的 manifold 上，防止信号在深层中爆炸/坍缩。

---

## 7. mHC 的物理意义

### 7.1 它不是简单提高参数量

mHC 的重点不是多几个参数，而是改变信号传播方式：

```text
传统 residual: 单状态 + 加法
mHC: 多状态 copies + constrained mixing
```

### 7.2 它可能解决深层模型的信号稳定问题

官方模型卡说 mHC 用来增强 conventional residual connections，并提升跨层信号传播稳定性，同时保留表达能力。

源码能看到：

- 4 copies；
- per-token learned mixing；
- Sinkhorn-constrained comb；
- attention 和 ffn 各自独立 HC 参数；
- final head 也通过 HC mixing 输出。

### 7.3 对长上下文和 agentic workflow 的意义

长任务/长上下文中，模型需要在很多层里保持：

```text
当前目标
远程证据
局部上下文
推理中间状态
安全约束
```

mHC 可能使这些信号在深层传播中更稳定，但 Harness 不能因此放弃显式 checkpoint。mHC 是模型内部稳定机制，不是任务级可靠性保证。

---

## 8. mHC 与 Harness 的关系

### 8.1 mHC 提高模型长链路稳定性

这解释了为什么 V4-Pro-Max 在复杂 reasoning / agentic 任务上更强。

### 8.2 但 mHC 不等于外部任务记忆

mHC 只在一次 forward 内传播 hidden states，不会替代：

```text
Memory
Plan
Checkpoint
Tool logs
Code diff
External state
```

### 8.3 Harness 应该顺应 mHC

由于 mHC 支持多信号流混合，Harness 应提供清晰分层信号：

```text
目标信号
约束信号
证据信号
执行信号
审查信号
```

而不是混成一大段自然语言。

---

## 9. 新增物理特性编号

### P-023：V4 每个 token 维护 `hc_mult=4` 份 hidden state copies

证据：`Transformer.forward` 中 `h.unsqueeze(2).repeat(..., hc_mult, ...)`。

Harness 影响：模型内部具备多通道信号传播能力；Prompt 应提供清晰可分离的信号，而不是混杂叙述。

### P-024：每个 Block 的 Attention 和 MoE 都独立使用 hc_pre/hc_post

证据：`Block.forward` 对 Attention 和 FFN 两次调用 `hc_pre/hc_post`。

Harness 影响：V4 在每层都对 attention/ffn 信号做稳定混合，适合复杂任务，但仍需要外部 checkpoint 管控。

### P-025：mHC 的 comb 使用 Sinkhorn 归一化

证据：`hc_split_sinkhorn_kernel` 对 `comb` 反复行/列归一化。

Harness 影响：模型内部残差信号受约束，长链路推理更稳定；Harness 可更大胆做长任务，但不能取消 review。

### P-026：HC head 在输出 logits 前也做 hidden copies 混合

证据：`ParallelHead.hc_head` 使用 sigmoid weights 混合 hc copies。

Harness 影响：多通道 hidden state 最终被动态汇聚；输出受全部 signal copies 影响。

---

## 10. 待技术报告继续确认

1. mHC 的数学定义和 manifold constraint 具体形式。
2. mHC 与传统 residual / Hyper-Connections 的理论差异。
3. Sinkhorn 迭代次数 20 的经验依据。
4. mHC 对长上下文/长链推理 benchmark 的贡献消融。
