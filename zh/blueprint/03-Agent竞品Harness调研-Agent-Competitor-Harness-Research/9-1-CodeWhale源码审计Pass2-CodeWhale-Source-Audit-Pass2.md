# 9-1 CodeWhale 源码审计 Pass 2 CodeWhale Source Audit Pass 2

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.1  
> 仓库：`Hmbown/CodeWhale`  
> 状态：历史 Pass 2；关键链路已完成源码定位，但完整 three-zone request contract 尚未接入，路由与成本收益仍需 benchmark。
> 已读核心：README、ARCHITECTURE、turn_loop.rs、models.rs、pricing.rs、client.rs、prefix_cache.rs。  
> 结论：CodeWhale 是当前调研中最接近 DeepSeek Agent Code Mode 的开源 Harness。

---

## 1. 本轮新增读取文件

| 文件 | 作用 |
|---|---|
| `README.md` | 产品定位、V4、Constitution、auto route、prefix cache、subagents、side-git |
| `docs/ARCHITECTURE.md` | 模块边界、engine、tool flow、LSP、runtime API、checkpoint |
| `crates/tui/src/core/engine/turn_loop.rs` | 主 streaming turn loop、prefix stability、auto compaction、tool loop、LSP diagnostics |
| `crates/tui/src/models.rs` | DeepSeek V4 1M context、reasoning effort、usage fields、reasoning replay |
| `crates/tui/src/pricing.rs` | DeepSeek cache hit/miss 分价、V4 Flash/Pro 计价、cache savings |
| `crates/tui/src/client.rs` | DeepSeek OpenAI-compatible client、reasoning_content、thinking、usage normalization |
| `crates/tui/src/prefix_cache.rs` | PrefixStabilityManager、SHA-256 fingerprint、three-region prefix model |

---

## 2. DeepSeek V4 物理特性如何被 CodeWhale 产品化

### 2.1 1M Context：模型能力 → context window / compaction / output budget

`models.rs` 直接定义：

```text
DEEPSEEK_V4_CONTEXT_WINDOW_TOKENS = 1_000_000
DEEPSEEK_V4 max output tokens = 384_000
legacy DeepSeek context window = 128_000
```

并通过 `context_window_for_model` 根据 model name 判断 V4 context window。  
这不是泛化 LLM wrapper，而是明确知道 DeepSeek V4 的物理窗口。

**对 DeepSeek Agent 的启发：**

```text
ModelProfile 必须内置 V4 Flash / V4 Pro 的 context window、max output、reasoning support、pricing、cache semantics。
```

### 2.2 Cache hit/miss：模型成本特性 → pricing / savings / prefix telemetry

`pricing.rs` 直接按 DeepSeek 官方 cache hit/miss 分价计算成本：

```text
input_cache_hit_per_million
input_cache_miss_per_million
output_per_million
prompt_cache_hit_tokens
prompt_cache_miss_tokens
calculate_cache_savings
```

并且 V4 Pro / V4 Flash 分别有不同价格表。

**对 DeepSeek Agent 的启发：**

```text
CostCacheTelemetry 不能后补；
必须从 MVP 起进入 Usage Parser、Turn Trace、Status Bar、Route Policy。
```

### 2.3 Prefix Cache：模型缓存特性 → PrefixStabilityManager

`prefix_cache.rs` 明确写到 DeepSeek prefix caching 依赖 exact byte prefix matching，任何 system prompt drift、tool list reordering、message rewriting 都会 bust cache。

它实现：

```text
PrefixFingerprint
PrefixChange
PrefixStabilityManager
SHA-256(system prompt)
SHA-256(tool catalog JSON)
combined hash
drift diagnosis: system changed / tools changed / both
stability_ratio
```

还定义三-region model：

```text
IMMUTABLE PREFIX = system + tool_specs
APPEND-ONLY HISTORY = grows monotonically
LATEST USER TURN = only new content
```

**对 DeepSeek Agent 的启发：**

```text
这是 DeepSeek Agent Cache-First Harness 的核心原型。
必须复刻并增强：
- Prefix fingerprint
- Prefix drift event
- stable tool serializer
- append-only history discipline
- UI cache health
```

### 2.4 Three-zone Prefix Contract：模型缓存特性 → turn_loop 检查

`turn_loop.rs` 在每次请求前对 system prompt + tool catalog 做 prefix stability check。完整 three-zone 类型结构位于 `prompt_zones.rs`，但源码明确标注尚未接入 request path：

```text
freeze baseline on first turn
verify against frozen prefix on subsequent turns
drift logged
PrefixStabilityManager reports change
```

**对 DeepSeek Agent 的启发：**

```text
StablePrefix 不能只停留在 prompt 设计；
必须在 Agent Loop 的 request build 之前做 runtime check。
```

### 2.5 Reasoning Effort：模型推理档位 → auto effort

`models.rs` 的 `MessageRequest` 包含：

```text
reasoning_effort: off | low | medium | high | max
thinking field
```

`turn_loop.rs` 每轮调用：

```text
resolve_auto_effort(session.reasoning_effort, session.messages)
```

这说明 CodeWhale 已经把“thinking level”产品化为可自动解析的 per-turn 决策。

**对 DeepSeek Agent 的启发：**

```text
ModelRouter 不应只选 Flash/Pro；
还要同时选 thinking_effort = off/high/max。
```

### 2.6 DeepSeek Client：模型协议 → OpenAI-compatible + thinking/reasoning normalization

`client.rs` 是 DeepSeek 的 OpenAI-compatible chat completions client。关键点：

```text
ReasoningEffort
Thinking { type: "enabled" }
stream_options.include_usage = true
reasoning_content delta streamed as ChunkReasoning
normaliseUsage folds DeepSeek prompt_cache_hit/miss and OpenAI prompt_tokens_details.cached_tokens
reasoning_tokens normalized
```

它还明确不把 `reasoning_content` 重发回去，原因是 DeepSeek 会把 re-sent reasoning 计入 billable prompt input。

**对 DeepSeek Agent 的启发：**

```text
ReasoningContentPolicy 必须明确：
- display/archive 可以保留
- prompt replay 默认禁止
- tool-call state 需要另行结构化保留
```

### 2.7 Tool Execution Loop：模型工具能力 → tool planning / approval / hooks / LSP

`turn_loop.rs` 的工具流包括：

```text
active_tools
strict_tool_mode
tool planning/execution
loop guard
approval summary
LSP diagnostics flush before next request
stream retry
context overflow recovery
auto compaction
```

**对 DeepSeek Agent 的启发：**

```text
Code Mode 的质量提升不是来自模型本身，而是：
- 编辑后 LSP diagnostics 注入
- failed build/test 输出进入 next turn
- tool loop guard 防止重复死循环
- approval summary 让用户知道将要执行什么
```

---

## 3. CodeWhale Model-Harness Fit Matrix 终版

| DeepSeek V4 特性 | CodeWhale 适配程度 | 源码证据级别 | 迁移判断 |
|---|---:|---|---|
| 1M context | A | models.rs | 直接借鉴 ModelProfile |
| max output 384K | A | models.rs | 直接借鉴 |
| cache hit/miss pricing | A | pricing.rs | 直接借鉴并产品化 UI |
| cache savings | A | pricing.rs | 直接借鉴 |
| prefix exact matching | A | prefix_cache.rs | 直接借鉴 |
| prefix drift detector | A | prefix_cache.rs + turn_loop.rs | 直接借鉴 |
| prefix drift check（system + tools） | A | prefix_cache.rs + turn_loop.rs | 已接入，可借鉴 |
| 完整 three-zone request contract | B-/未完成 | prompt_zones.rs 明确标注 not yet wired | 只能借鉴概念，不得视为现成功能 |
| Flash/Pro model route | A- | README / turn_loop / models | 借鉴并增强为 risk/failure/checkpoint router |
| thinking level route | A- | models.rs / turn_loop | 借鉴 |
| reasoning_content replay policy | A- | client.rs | 借鉴并扩展四态管理 |
| tool loop | A | turn_loop.rs | 借鉴 |
| LSP diagnostics | A | turn_loop.rs / architecture | 借鉴 |
| side-git checkpoint | A- | README / architecture | 借鉴 |
| subagents/RLM | B+ | README / architecture | 继续深读实现 |
| V4 DSML | 未确认 | client.rs 以 OpenAI-compatible 为主 | DeepSeek Agent 仍需自研 DSML compiler |

---

## 4. 对 DeepSeek Agent 的直接迁移设计

### 4.1 DeepSeekV4ModelProfile

```text
model_id
family = deepseek-v4
variant = flash/pro
context_window = 1_000_000
max_output_tokens = 384_000
supports_reasoning = true
reasoning_effort = off/high/max
pricing = cache_hit/cache_miss/output
```

### 4.2 PrefixStabilityManager

```text
stable_prefix = system + tools + skills index + static policy
append_only_history
turn_tail
sha256 fingerprint
drift diagnosis
cache health event
```

### 4.3 CostCacheTelemetry

```text
prompt_cache_hit_tokens
prompt_cache_miss_tokens
cache_savings
hit_rate
miss_cost
output_cost
reasoning_tokens
reasoning_replay_tokens
```

### 4.4 ReasoningContentPolicy

```text
visible stream
archive
summarize into checkpoint
do not replay raw reasoning by default
```

### 4.5 LSP + Tool Feedback Loop

```text
post-edit diagnostics
test/build output
tool error classifier
loop guard
tool retry policy
```

---

## 5. CodeWhale 最终评价

CodeWhale 是目前所有调研项目中最接近 DeepSeek Agent Code Mode 的实现。  
它已经把 DeepSeek V4 的物理特性转成产品能力：

```text
1M context → model profile / compaction
prefix cache → prefix stability manager / three-zone prefix
cache pricing → cost estimator / cache savings
thinking → reasoning_effort route
tool loop → LSP diagnostics / approval / loop guard
```

DeepSeek Agent 可以把 CodeWhale 当作 V4-native coding harness 的核心参考，但不能直接止步于它；我们还要补：

```text
DSML native compiler
CSA/HCA-aware context layout
Agent Mode 多格式 workspace
checkpoint-driven Pro review
desktop UX
```
