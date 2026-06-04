# 17-2 Reasonix / Hermes Agent / CodeWhale 源码事实校准

## 1. 总体结论

| 项目 | 旧报告总体可信度 | 本轮结论 |
|---|---|---|
| Reasonix | 高 | DeepSeek-native 核心结论多数被当前源码确认；评分和迁移建议仍需与事实分离 |
| Hermes Agent | 高 | 工具生态、progressive disclosure、trajectory compression 被确认；部分设计动机属于推论 |
| CodeWhale | 中高 | 大量 DeepSeek-native 实现真实存在；旧报告把完整 three-zone scaffolding 误写为已接入 runtime |

## 2. Reasonix：多数关键事实得到确认

### 2.1 A0/A1 确认项

- OpenAI-compatible adapter 在请求构建时执行 tool-call pairing 修复，并明确不重传 `reasoning_content`：[`internal/provider/openai/openai.go`](https://github.com/esengine/DeepSeek-Reasonix/blob/174d344ec74b826754b46edbf367cd69a26250c0/internal/provider/openai/openai.go#L151-L176)（A1）。
- usage normalization 读取 DeepSeek cache hit/miss 与 reasoning token 字段（A1）。
- Agent loop 存在 plan mode runtime gate、session cache hit/miss 累积、compaction 与 PostLLMCall/PreCompact hooks：[`internal/agent/agent.go`](https://github.com/esengine/DeepSeek-Reasonix/blob/174d344ec74b826754b46edbf367cd69a26250c0/internal/agent/agent.go)（A1）。
- `reasonix.example.toml` 明确提供 auto plan、compact ratios、planner model、cache-hit pricing 和 effort 配置：[`reasonix.example.toml`](https://github.com/esengine/DeepSeek-Reasonix/blob/174d344ec74b826754b46edbf367cd69a26250c0/reasonix.example.toml)（A2）。

### 2.2 需要降级为评估的内容

- “A/A-”“最 DeepSeek-native”“可直接借鉴”是分析者评分，不是源码事实；
- planner/executor 是否在真实工作负载中提高质量并保持 cache-stable，需要 benchmark；
- 不重传 reasoning_content 是 Reasonix 当前 adapter 策略，是否适配所有 DeepSeek V4 endpoint/模式必须以实际 API 契约测试确认；
- cache-first compaction 的经济性合理，但旧报告没有提供命中率、质量损失和成本实验。

### 2.3 校准结论

Reasonix 是当前最值得继续做 DeepSeek-specific 源码审计的对象之一。下一步应从“读到设计”升级为“运行测试验证”：固定任务集比较 plan mode、compaction、reasoning policy 和 planner/executor 的成本与质量。

## 3. Hermes Agent：实现真实，动机推论需标注

### 3.1 A0/A1 确认项

- Tool registry 真实存在，包含注册、toolset、availability 与动态行为：[`tools/registry.py`](https://github.com/NousResearch/hermes-agent/blob/d3fab54933c3866d2c7cf5e51dc63e9e494c9f47/tools/registry.py)（A1）。
- `tool_search/tool_describe/tool_call` progressive disclosure 真实存在并进入 `model_tools.py` 的组装与 dispatch：[`tools/tool_search.py`](https://github.com/NousResearch/hermes-agent/blob/d3fab54933c3866d2c7cf5e51dc63e9e494c9f47/tools/tool_search.py)、[`model_tools.py`](https://github.com/NousResearch/hermes-agent/blob/d3fab54933c3866d2c7cf5e51dc63e9e494c9f47/model_tools.py)（A1）。
- trajectory compressor 明确保护头尾、压缩中段并以 summary 替换：[`trajectory_compressor.py`](https://github.com/NousResearch/hermes-agent/blob/d3fab54933c3866d2c7cf5e51dc63e9e494c9f47/trajectory_compressor.py#L1-L15)（A1）。
- gateway、memory、skills、cron、多个 provider/backend 均有大量实际模块，不只是 README 目录占位（A1）。

### 3.2 需要降级或继续验证

- “tool schema caching 是为了模型上下文成本”是合理 B 级推论；memoization 直接证明的是 CPU/组装复用，不自动证明 provider prompt cache 命中改善；
- trajectory compression 面向训练数据的价值有代码与文档支撑，但压缩后质量是否优于其他策略需要实验；
- “self-improving”是产品定位；技能是否稳定改进、会否累积错误，需要长期评测与 provenance 审计；
- gateway + memory + cron + shell 的安全风险判断合理，但属于威胁模型分析，不是已发生漏洞事实。

### 3.3 校准结论

Hermes 最值得借鉴的是 tool registry、progressive disclosure 和 Agent OS 能力面；不应把普通 memoization 直接等同于 DeepSeek prefix-cache 优化，也不应把“自进化”宣传语直接等同于已验证的持续质量提升。

## 4. CodeWhale：关键实现真实，但 three-zone 被过度陈述

### 4.1 A0/A1 确认项

- `PrefixStabilityManager` 对 system prompt + tool catalog 建 SHA-256 fingerprint，并在真实 `turn_loop.rs` 请求前调用 `verify`：[`prefix_cache.rs`](https://github.com/Hmbown/CodeWhale/blob/8dff2f7525ead210a01347b48f53ae3f20d094ec/crates/tui/src/prefix_cache.rs#L1-L18)、[`turn_loop.rs`](https://github.com/Hmbown/CodeWhale/blob/8dff2f7525ead210a01347b48f53ae3f20d094ec/crates/tui/src/core/engine/turn_loop.rs#L329-L341)（A0/A1）。
- cache hit/miss telemetry、pricing/savings、auto router、reasoning_content replay、side-git snapshot、LSP post-edit 等均能定位到实际源码和测试（A1/A0）。
- CodeWhale 确实是六者中 DeepSeek-specific 机制最丰富的公开实现之一。

### 4.2 必须纠正：完整 three-zone contract 尚未接入 request path

旧 `9-1` 写道：

```text
turn_loop.rs 在每次请求前做 prefix stability check，并有 three-zone prefix contract
```

前半句成立；后半句把两个成熟度层级合并了：

- 当前接入 turn loop 的校验对象是 **system prompt + tool catalog**；
- [`prompt_zones.rs`](https://github.com/Hmbown/CodeWhale/blob/8dff2f7525ead210a01347b48f53ae3f20d094ec/crates/tui/src/prompt_zones.rs#L18-L23) 对完整三层数据结构明确标注 `for future phases — not yet wired into the request path`；
- `AppendLog` 等结构也明确标注 `Phase 1 scaffolding — not yet wired into the engine request path`。

因此正确表述应是：

```text
已接入：稳定前缀 fingerprint / drift detection（system + tools）
未完整接入：以类型约束实现的 pinned prefix + append log + turn scratch request compiler
```

`three-zone prefix | A | 直接借鉴` 应降级为：**概念与部分实现 A1；完整 request-path contract 未完成**。

### 4.3 其他校准点

- `prefix_cache.rs` 自己写明 inspired by Reasonix，借鉴时需要识别原创边界；
- auto router 存在不等于路由质量已被证明，仍需 benchmark；
- reasoning_content replay 与 Reasonix 的“不重传”策略相反，说明不同 endpoint/模式存在协议差异，DeepSeek Agent 不能先验选择单一四态策略；
- CodeWhale 源码中同时存在成熟 runtime 和 roadmap/scaffolding，审计时必须逐项追踪调用路径。

## 5. 修订后的三者借鉴排序

| 维度 | 首选参考 | 备注 |
|---|---|---|
| DeepSeek cache/usage/provider 策略 | Reasonix + CodeWhale | 两者策略有差异，必须通过 API 契约测试裁决 |
| Tool ecosystem / Agent OS | Hermes | 非 DeepSeek-native，适合作为能力层参考 |
| Prefix drift detection | CodeWhale | 已接入真实 turn loop |
| 完整 three-zone request compiler | 无 | CodeWhale 当前仍是 scaffolding；需要自研或继续等待实现 |
| Cache-first compaction | Reasonix | 需补 benchmark 验证收益与质量 |
