# 09-flash-vs-pro-capability-matrix.md — DeepSeek V4 Flash / Pro 能力差异矩阵 v0.1

> 日期：2026-06-04  
> 阶段：Phase 9 — Flash vs Pro 能力差异与模型路由策略  
> 目标：把官方评测、config 参数、源码结构合并成产品可用的 Flash / Pro 能力矩阵。

---

## 1. 总体判断

DeepSeek V4 Flash 和 Pro 是同架构族的两种规模形态：

```text
共同点：
- deepseek_v4 架构
- 1M context
- Hybrid Attention: CSA + HCA
- mHC
- MoE + shared expert
- num_experts_per_tok = 6
- num_hash_layers = 3
- FP4 + FP8 Mixed（Instruct）
- 支持 Non-think / Think / Think Max

差异点：
- Pro 更宽、更深、更大专家池、更高 index_topk、更高 route_scale
- Flash 更小、更便宜、更适合默认执行
```

一句话：

> Flash 是同构小模型，Pro 是高容量长上下文/复杂 Agentic 模型。

---

## 2. 参数级差异矩阵

| 维度 | V4-Flash | V4-Pro | 产品解释 |
|---|---:|---:|---|
| Total Params | 284B | 1.6T | Pro 知识容量更大 |
| Activated Params | 13B | 49B | Pro 每 token 激活计算能力更强 |
| Context | 1M | 1M | 两者都能长上下文 |
| hidden_size | 4096 | 7168 | Pro 表征维度更大 |
| layers | 43 | 61 | Pro 长链推理更强 |
| attention_heads | 64 | 128 | Pro attention 容量更大 |
| q_lora_rank | 1024 | 1536 | Pro query 表达能力更强 |
| index_topk | 512 | 1024 | Pro 远程压缩历史选择容量更大 |
| n_routed_experts | 256 | 384 | Pro 专家池更大 |
| experts/token | 6 | 6 | Flash 不是靠少激活专家变便宜 |
| shared_experts | 1 | 1 | 两者都有公共能力通道 |
| hash_layers | 3 | 3 | 前 3 层均稳定 hash routing |
| route_scale | 1.5 | 2.5 | Pro 更强调 routed expert 输出 |
| moe_intermediate_size | 2048 | 3072 | Pro 单专家 FFN 更宽 |
| compress pattern | `[0,0,4,128,...]` | `[128,128,4,128,...]` | Pro 更早利用压缩历史 |
| reasoning modes | 3 modes | 3 modes | 两者都支持 Max |

---

## 3. 官方评测观察

### 3.1 知识能力

官方 Comparison across Modes 显示：

- SimpleQA-Verified：Flash Non-Think 23.1，Flash Max 34.1，Pro Non-Think 45.0，Pro Max 57.9。
- Chinese-SimpleQA：Flash Max 78.9，Pro Max 84.4。
- HLE：Flash Max 34.8，Pro Max 37.7。

解释：

- 纯知识能力 Pro 显著强于 Flash。
- Flash 增加 thinking budget 能提升推理，但无法完全弥补参数规模带来的知识差距。

### 3.2 推理 / 代码能力

官方表显示：

- LiveCodeBench：Flash Non-Think 55.2，Flash High 88.4，Flash Max 91.6；Pro Non-Think 56.8，Pro High 89.8，Pro Max 93.5。
- Codeforces：Flash High 2816，Flash Max 3052；Pro High 2919，Pro Max 3206。

解释：

- 在代码推理中，thinking budget 极其重要。
- Flash Max 已经很强，但 Pro Max 仍领先。
- Code 模式应 Flash 执行，Pro 审查/关键规划。

### 3.3 长上下文能力

官方表显示：

- MRCR 1M：Flash Non-Think 37.5，Flash High 76.9，Flash Max 78.7；Pro Non-Think 44.7，Pro High 83.3，Pro Max 83.5。
- CorpusQA 1M：Flash Non-Think 15.5，Flash High 59.3，Flash Max 60.5；Pro Non-Think 35.6，Pro High 56.5，Pro Max 62.0。

解释：

- 长上下文任务中 thinking budget 显著影响结果。
- Pro 在 MRCR 1M 更强，但 CorpusQA 中 Flash High 接近甚至略高于 Pro High，需要具体任务路由。
- 结论不是“长上下文一定 Pro”，而是“长上下文 + 复杂证据冲突/关键审查才 Pro”。

### 3.4 Agentic 能力

官方表显示：

- Terminal Bench 2.0：Flash Max 56.9，Pro Max 67.9。
- SWE Verified：Flash Max 79.0，Pro Max 80.6。
- SWE Pro：Flash Max 52.6，Pro Max 55.4。
- BrowseComp：Flash Max 73.2，Pro Max 83.4。
- Toolathlon：Flash Max 47.8，Pro Max 51.8。

解释：

- 复杂 Agentic workflow 中 Pro 有稳定优势。
- 但 SWE Verified 中 Flash Max 与 Pro Max 差距很小，说明 Flash 可承担大量执行环节。
- BrowseComp 这种搜索/综合/不确定性任务更适合 Pro。

---

## 4. 任务类型能力矩阵

| 任务类型 | 推荐模型 | 原因 |
|---|---|---|
| 普通聊天 | Flash Non-think | 低成本、足够快 |
| 简单摘要 | Flash Non-think | 不需要复杂推理 |
| 文档结构化提取 | Flash Non-think / Think | 可低成本批处理 |
| 小范围代码修改 | Flash Think | 需要步骤推理，但风险可控 |
| 多文件代码修改 | Flash Think → Pro Review | Flash 执行，Pro 检查依赖 |
| 架构设计 | Pro Think / Max | 需要知识、推理、长期一致性 |
| 长上下文事实检索 | Pro Non-think / Think | index_topk 更大，远程证据检索更强 |
| 长上下文普通摘要 | Flash Think | 若 layout 好，Flash 成本更优 |
| 工具调用参数生成 | Flash Non-think | 快速、低风险 |
| 工具调用失败复盘 | Pro Think | 需要根因推理 |
| 最终交付审查 | Pro Think / Max | 高质量验收 |
| 高风险操作 | Pro Think + User Approval | 删除、迁移、生产、法律等 |

---

## 5. 关键产品判断

### J-001：Flash-first 是正确默认策略

原因：

- Flash 保留 V4 全部核心机制；
- Flash 也有 1M context；
- Flash 每 token 仍激活 6 routed experts；
- 官方评测显示 Flash Max 在代码/部分推理任务上非常强。

### J-002：Pro 不应该替代 Flash，而应该作为 checkpoint reviewer

Pro 最适合：

```text
规划
审查
失败复盘
证据冲突判断
最终交付
高风险决策
```

### J-003：Thinking budget 和模型规模是两个独立轴

Flash Max 可能胜过 Pro Non-think。  
因此路由器不能只有 Flash/Pro 两档，必须是：

```text
model_size × reasoning_effort
```

### J-004：长上下文不等于必须 Pro

如果任务只是长文档摘要、结构提取、低风险检索，Flash Think 可能足够。  
如果任务涉及证据冲突、远程依赖、多工具行动、最终判断，应切 Pro。

---

## 6. 推荐默认路由

```text
默认：Flash Non-think
需要多步：Flash Think
复杂规划：Pro Think
长上下文证据冲突：Pro Think
最终审查：Pro Think / Max
失败两次：Pro Think
用户要求最高质量：Pro Max
