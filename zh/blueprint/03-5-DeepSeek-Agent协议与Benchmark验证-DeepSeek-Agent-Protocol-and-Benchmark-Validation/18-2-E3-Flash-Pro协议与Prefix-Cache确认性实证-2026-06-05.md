# Stage 2.5 E3：Flash / Pro 协议与 Prefix Cache 确认性实证

> 运行日期：2026-06-05。证据等级：E3。结论只覆盖本账号、本 endpoint、本时间窗口内的 DeepSeek V4 Flash / Pro API 行为；不等于 E4 真实任务质量或生产 SLA。

## 1. 证据包

| 类型 | 路径 | 说明 |
|---|---|---|
| 有效主矩阵 | `benchmarks/results/e3/20260605T013303Z-all-wave-1-ba21d4a8` | TLS 修复后运行；470 scheduled events |
| cross-time 追加 wave | `benchmarks/results/e3/20260605T014427Z-cross-time-wave-2-52b158cf` | 同一 `experiment_id` 的独立后续 wave；10 scheduled events |
| 环境失败记录 | `benchmarks/results/e3/20260605T013117Z-all-wave-0-62d5d426` | Python CA 信任链失败；不计入通过结论 |

原始 trace 使用结构化脱敏格式：保留 request hash、request/response shape、status、usage、cache token、request id presence、错误类别；不保存 API key、明文回复文本或 reasoning 内容。

## 2. 主矩阵结果

| 模型 | cases | runs | HTTP 200 | 预期 HTTP 400 | 主体成功率 | 语义标记失败 |
|---|---:|---:|---:|---:|---:|---:|
| `deepseek-v4-flash` | 40 | 235 | 230 | 5 | 97.87% | 0 |
| `deepseek-v4-pro` | 40 | 235 | 230 | 5 | 97.87% | 2 case groups |

解释：

- `P09.invalid-tool-schema` 在两个模型上均为 5/5 HTTP 400，符合 invalid schema case 预期，不能计为 provider 功能失败。
- Flash 的所有被检查语义标记均通过。
- Pro 的 `P03.thinking-max` 与 `P20.ordinary-reasoning` 有少量 exact-marker 未命中，说明不能把 Pro 当作严格逐字服从的 deterministic executor；架构上需要保留 verifier / retry。
- Streaming 在两个模型上均返回 `content` 与 `reasoning_content` delta shape。
- Thinking tool-loop replay case 显示可用，但必须由 Harness 保留 assistant message shape，不能丢弃 provider 协议字段。

## 3. Prefix Cache 结果

主矩阵中 39 个 cache 相关 case groups 在两个模型上均出现非零 cache token。典型结果：

| 模型 | case | hit tokens | miss tokens | hit rate |
|---|---|---:|---:|---:|
| Flash | `C01.exact-probe` | 14,720 | 420 | 97.23% |
| Flash | `C10.tools-exact` | 16,640 | 50 | 99.70% |
| Pro | `C01.exact-probe` | 14,720 | 420 | 97.23% |
| Pro | `C10.tools-exact` | 16,640 | 50 | 99.70% |

cross-time 追加 wave：

| 模型 | case | runs | HTTP 200 | hit tokens | miss tokens | hit rate |
|---|---|---:|---:|---:|---:|---:|
| Flash | `C50.cross-time-exact` | 5 | 5 | 14,720 | 420 | 97.23% |
| Pro | `C50.cross-time-exact` | 5 | 5 | 14,720 | 420 | 97.23% |

结论：在本时间窗口内，Flash / Pro 均表现出可观测 Prefix Cache 命中。Cache 策略可进入 Stage 4 架构，但必须作为可观测优化，不得假设永久稳定或跨账号等价。

## 4. 对后续 Stage 的约束

1. Provider adapter 必须记录 `usage.prompt_tokens_details` 中的 cache hit/miss 字段，并在缺失时降级为 unknown。
2. Planner / router 不应依赖 Pro 的 exact text determinism；所有生产任务必须经过 deterministic verifier。
3. Tool loop 必须保留 assistant message 的 provider 字段；不得在中间轮次删除 reasoning 协议字段后声称等价。
4. Cache-first context compiler 可以进入架构定稿，但必须输出 request hash、prefix segment hash 与 hit-rate evidence。
5. Stage 2.5 可以关闭；真实任务收益仍必须由 Stage 6 E4 验收集证明。
