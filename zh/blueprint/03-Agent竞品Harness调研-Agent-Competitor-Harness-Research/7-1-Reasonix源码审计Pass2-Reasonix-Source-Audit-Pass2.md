# 7-1 Reasonix 源码审计 Pass 2 Reasonix Source Audit Pass 2

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.1  
> 仓库：`esengine/DeepSeek-Reasonix`  
> 分支：`main-v2`  
> 状态：历史 Pass 2；核心机制已完成源码定位，但成本、质量与生产成熟度仍需 benchmark 验证。
> 已读核心：README、agent.go、compact.go、provider.go、provider/openai/openai.go。

---

## 1. 本轮新增读取文件

| 文件 | 作用 |
|---|---|
| `internal/agent/agent.go` | Agent 主结构、plan mode、permission gate、hooks、cache telemetry、compaction config、memory queue、tool context |
| `internal/agent/compact.go` | cache-first compaction、tail budget、summary prompt、archive、fold economics |
| `internal/provider/provider.go` | provider abstraction、message/tool schema、Usage、Pricing、tool pairing sanitization |
| `internal/provider/openai/openai.go` | OpenAI-compatible provider、DeepSeek detection、reasoning_effort、thinking、reasoning_content policy、usage normalization |

---

## 2. DeepSeek 物理特性如何被 Reasonix 产品化

### 2.1 Prefix Cache：模型成本特性 → session cache telemetry

`agent.go` 中 Agent 维护：

```text
sessCacheHit
sessCacheMiss
lastPrefixShape
haveLastPrefixShape
```

注释明确这些字段用于累计 session 级 cache hit/miss prompt tokens，让 frontend 可以显示 aggregate hit-rate；并且不会因为 compaction reset，因为 compaction 只是 rewrite session.Messages，aggregate hit-rate 不应崩掉。

**启发：**

```text
DeepSeek Agent 的 cache hit-rate 要分两层：
- per-turn cache hit/miss
- session aggregate cache hit/miss
```

### 2.2 Plan Mode：产品权限模式 → cache-friendly execution gate

`agent.go` 的 `planMode` 注释非常关键：planMode 为 true 时拒绝所有非 ReadOnly 工具调用；但 system prompt 和 tool list 不随 toggle 改变，所以 prompt-cache prefix 仍有效。

**启发：**

```text
不要通过修改 system prompt/tool list 来切换模式；
Plan/Agent/YOLO/Review 模式尽量在 runtime gate 层实现，避免 bust prefix cache。
```

### 2.3 Permission Gate：模型工具能力 → runtime enforcement

Reasonix 的 `Gate` 接口：

```go
Check(ctx, toolName, args, readOnly) (allow, reason, err)
```

Agent 在 execute time 咨询 gate。  
这与 DeepSeek Agent 需要的权限边界完全一致：模型可以建议，runtime 决定是否执行。

### 2.4 Tool Hooks：工具生命周期 → pre/post hook + PostLLMCall

`ToolHooks` 支持：

```text
PreToolUse
PostToolUse
PostLLMCall
SubagentStop
PreCompact
```

特别是 `PostLLMCall` 可以在 reasoning_content 存储前翻译/处理 reasoning，`PreCompact` 可以给 summary prompt 增加额外指导。

**启发：**

```text
ReasoningContentPolicy / CompactionPolicy 应开放 hook seam。
```

### 2.5 Compaction：缓存经济性 → low-frequency cache-reset point

`compact.go` 开头直接定义：

```text
Compaction is a low-frequency cache-reset point
prompt grows append-only (high cache hits)
until near compactRatio
then compacted down to tail budget
```

这非常 DeepSeek-native，因为它把 compaction 视为“少数必要的 cache reset”，而不是普通上下文管理。

它还设置：

```text
softCompactRatio = 0.5
compactRatio = 0.8
compactForceRatio = 0.9
tailTokens = 16384
```

soft ratio 只提示，不 compact，因为过早 compact 会 crater cache。

### 2.6 Compaction Summary：模型长期任务 → structured briefing

Reasonix 的 `summarySystemPrompt` 要求摘要包含：

```text
Goal
Decisions & rationale
Files & code
Commands & outcomes
Errors & fixes
Pending & next step
```

这与我们 DeepSeek Agent 的 checkpoint summary schema 高度一致。

### 2.7 Reasoning Content：思考内容 → 不重传以省钱

`provider/openai/openai.go` 中 `buildRequest` 明确写到：`reasoning_content` 是 response-only field，不会被重新发送；DeepSeek 会把重发 reasoning 计入 billable prompt input，Reasonix 仍在 session 里保留它用于 display/archive，但不付费重传。

这条非常重要，直接支撑我们之前的 `ReasoningContentPolicy`。

### 2.8 DeepSeek thinking：provider 配置 → effort high/max

`openai.go` 检测 base_url 是否 DeepSeek。若是 DeepSeek，则 effort 只能是：

```text
high
max
```

空或 off 会 fallback 到 high。非 DeepSeek 则走 OpenAI low/medium/high，max 会 clamp 到 high。

**启发：**

```text
DeepSeek V4 thinking 参数必须在 provider adapter 层做校验和映射，不应让 UI 任意传。
```

### 2.9 Usage Normalization：模型 usage → cache/cost telemetry

`provider.go` 的 `Usage` 包含：

```text
PromptTokens
CompletionTokens
TotalTokens
CacheHitTokens
CacheMissTokens
ReasoningTokens
FinishReason
```

`Pricing` 包含：

```text
CacheHit
Input
Output
Currency
```

并提供 `Cost(u)`。

**启发：**

```text
ProviderUsage 是 DeepSeek Agent 的核心数据结构，不能只保留 input/output tokens。
```

---

## 3. Reasonix Model-Harness Fit Matrix 终版

| DeepSeek V4 特性 | Reasonix 适配程度 | 源码证据级别 | 迁移判断 |
|---|---:|---|---|
| prefix cache | A | agent.go / compact.go | 强借鉴 |
| session aggregate cache hit-rate | A | agent.go | 强借鉴 |
| cache-first compaction | A | compact.go | 强借鉴 |
| Flash/Pro planner/executor | A- | README / config | 强借鉴 |
| thinking effort | B+ | openai.go | 借鉴，但需扩展 off/high/max |
| reasoning_content policy | A- | openai.go | 强借鉴 |
| provider abstraction | A- | provider.go | 借鉴 |
| tool pairing sanitization | A | provider.go | 强借鉴 |
| permission runtime | A | agent.go | 强借鉴 |
| plan-mode cache preservation | A | agent.go | 强借鉴 |
| hooks | A- | agent.go | 借鉴 |
| memory queue | B+ | agent.go | 继续读 memory 模块 |
| V4 DSML | 未确认 | openai-compatible | DeepSeek Agent 仍需自研 |
| CSA/HCA layout | C | 未见 | DeepSeek Agent 自研 |

---

## 4. DeepSeek Agent 迁移设计

### 4.1 Runtime Mode 不改 Prefix

```text
不要用 system prompt/tool list 变化切换 Plan/Agent/YOLO；
用 runtime gate / approval policy / permission policy 切换。
```

### 4.2 Session Cache Metrics

```text
per_turn_hit/miss
session_hit/miss
cache_savings
prefix_shape_diff
compaction_event
```

### 4.3 Cache-first Compaction

```text
soft notice at 50%
compact at 80%
force at 90%
fixed tail budget
archive originals
structured summary
precompact hook
```

### 4.4 Reasoning Content 四态

```text
stream/display
store/archive
summarize/checkpoint
do_not_replay
```

### 4.5 Tool Pairing Sanitizer

```text
repair unanswered assistant tool_calls
drop orphan tool messages
preserve call order
synthesize interrupted result
```

---

## 5. Reasonix 最终评价

Reasonix 是最值得借鉴的 DeepSeek-native Go Agent。  
它最强的不是 UI，而是工程哲学：

```text
Cache-first
Runtime gating, not prompt rewriting
Reasoning not replayed
Compaction as rare cache reset
Session aggregate cache metrics
Tool-pairing sanitization
```

相比 CodeWhale，Reasonix 更像“简洁、工程正确、DeepSeek-native 的 terminal core”。  
DeepSeek Agent 可以把 Reasonix 的 cache-first discipline 吸收进底层 runtime。
