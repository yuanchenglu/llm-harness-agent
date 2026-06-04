# 10-v4-physical-traits-inventory.md — DeepSeek V4 物理特性总清单 v0.1

> 阶段：Phase 10  
> 目标：把 Phase 1-9 的所有源码/配置/模型卡发现统一编号，为 Harness 架构提供证据底座。

---

## 1. Context / Attention

| 编号 | 物理特性 | Harness 影响 |
|---|---|---|
| P-001 | V4 Flash / Pro 均支持 1M context | 必须 long-context-first |
| P-002 | 最大输出 384K | 需长输出管理 |
| P-013 | attention 候选集合 = local window + compressed history | 不能 history dump |
| P-014 | compress_ratio=4 启用 learned Indexer | 关键历史应成为 anchor |
| P-015 | compress_ratio=128 不启用 Indexer | 远程历史应摘要化 |
| P-016 | sliding_window=128 | 当前操作信息必须靠近尾部 |
| P-017 | Indexer 自带 Compressor + FP4 quant simulation | 上下文噪声会影响 top-k 预算 |
| P-030 | sparse_attn 由 topk_idxs gather KV | 需要保护 top-k candidate budget |
| P-031 | sparse attention 有 attn_sink | 模型有稳定兜底，但不能替代布局 |

---

## 2. Cache / Serving

| 编号 | 物理特性 | Harness 影响 |
|---|---|---|
| P-003 | input token 按 cache hit/miss 分价 | 成本面板必须拆 hit/miss |
| P-004 | Context caching 默认开启 | Harness 要制造稳定前缀 |
| P-005 | cache prefix unit 要完整匹配 | Byte-stable prefix 是一级约束 |
| P-006 | cache 在请求边界/公共前缀/固定 token 间隔持久化 | 设计 prefix warming / stable turn loop |
| P-027 | 官方推理使用 TileLang custom kernels | 客户端默认接 API，不内置推理 |
| P-028 | activation FP8 per-128 block quant | cache miss prefill 仍昂贵 |
| P-029 | routed expert 使用 FP8 act × FP4 weight GEMM | API 经济性来自服务端优化 |
| P-032 | mHC Sinkhorn 是 kernel-level 实现 | mHC 是核心推理路径 |

---

## 3. MoE / Routing

| 编号 | 物理特性 | Harness 影响 |
|---|---|---|
| P-018 | 前 3 层 token-id hash routing | Prompt 标签应稳定 |
| P-019 | Pro/Flash 每 token routed experts 数相同 | Flash 是小型同构模型 |
| P-020 | Pro route_scale 高于 Flash | Pro 更适合专业复杂任务 |
| P-021 | routed experts FP4，shared expert 默认 dtype | Flash 可做通用执行，Pro 做复杂判断 |
| P-022 | MoE 输出 = routed experts + shared expert | 模型有专业/公共双通道 |

---

## 4. mHC / Depth Stability

| 编号 | 物理特性 | Harness 影响 |
|---|---|---|
| P-023 | 每 token 维护 hc_mult=4 hidden copies | Prompt 应多信号分层 |
| P-024 | Attention 和 MoE 都有 hc_pre/hc_post | 长链路信号更稳定 |
| P-025 | mHC comb 使用 Sinkhorn 归一化 | 支持复杂任务但仍需 review |
| P-026 | HC head 输出前混合 hidden copies | 输出受多通道信号影响 |

---

## 5. Reasoning / Encoding

| 编号 | 物理特性 | Harness 影响 |
|---|---|---|
| P-007 | Flash/Pro 支持 thinking / non-thinking | 路由必须双轴 |
| P-008 | FIM 仅 non-thinking | 局部补全不用 thinking |
| P-033 | V4 不使用 Jinja template，而是 encoding 实现 | 需要 V4MessageCompiler |
| P-034 | chat mode 通过关闭 thinking block 实现 | Non-think 是协议级控制 |
| P-035 | Max reasoning 是 special prefix | Max 会影响 cache，应少用 |
| P-036 | 默认 drop old reasoning_content | reasoning 不应长期回传 |
| P-037 | 有 tools 时 drop_thinking 自动 disabled | 工具循环需 checkpoint 压缩 |
| P-038 | Tool calling 使用 DSML | 需要 DSML parser/repair |
| P-039 | tool results merge into user message | 不能机械照搬 OpenAI tool role |

---

## 6. Flash / Pro 差异

| 编号 | 物理特性 | Harness 影响 |
|---|---|---|
| P-040 | Pro 1.6T / 49B activated，Flash 284B / 13B activated | Flash 执行，Pro 判断 |
| P-041 | Pro index_topk=1024，Flash=512 | Pro 更适合长上下文审查 |
| P-042 | Pro 前两层 compress=128，Flash 前两层 compress=0 | Flash 更依赖 Harness layout |
| P-043 | Pro layers=61，Flash=43 | Pro 长链推理更强 |
| P-044 | Pro hidden_size=7168，Flash=4096 | Pro 表征容量更强 |

---

## 7. 总结

DeepSeek V4 的独特性不是单点，而是组合：

```text
1M context
+ CSA/HCA hybrid attention
+ tiny local window
+ sparse top-k retrieval
+ MoE routed/shared expert
+ mHC multi-copy residual
+ FP4/FP8 kernels
+ DSML tool protocol
+ thinking effort modes
+ cache hit/miss pricing
```

DeepSeek Agent Harness 必须围绕这些物理特性重写。
