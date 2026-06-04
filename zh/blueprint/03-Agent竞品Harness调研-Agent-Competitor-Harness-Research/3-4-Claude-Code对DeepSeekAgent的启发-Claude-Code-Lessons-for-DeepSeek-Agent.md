# 3-4 Claude Code 对 DeepSeek Agent 的启发 Claude Code Lessons for DeepSeek Agent

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

## 1. 目标

本文件把 Claude Code 调研结论转成 DeepSeek Agent 可借鉴 / 不可照搬 / 需要超越的设计点。

---

## 2. 可直接借鉴的通用 Harness 模式

### 2.1 Agent Loop

Claude Code 的 loop 是：

```text
gather context
take action
verify results
```

证据：[Claude Code agentic loop](https://code.claude.com/docs/en/how-claude-code-works)。

DeepSeek Agent 可借鉴，但应增强：

```text
Context Layout
Model Router
Checkpoint
Pro Review
Cache Telemetry
```

### 2.2 Runtime 权限强制

Claude Code 明确说明权限由 Claude Code 执行，不由模型执行。证据：[Permissions enforced by Claude Code](https://code.claude.com/docs/en/permissions)。

DeepSeek Agent 必须同样设计 Runtime Permission Layer，不能依靠 prompt 约束模型。

### 2.3 Session / Checkpoint

Claude Code 将 session 保存为 JSONL，并在文件编辑前 snapshot。证据：[Sessions and snapshots](https://code.claude.com/docs/en/how-claude-code-works)。

DeepSeek Agent 应借鉴：

```text
task trace
tool trace
file snapshot
checkpoint
resume / fork
```

### 2.4 Skills / Subagents / Hooks

Claude Code 的扩展体系非常完整。证据：[Skills](https://code.claude.com/docs/en/skills)、[Subagents](https://code.claude.com/docs/en/sub-agents)、[Hooks](https://code.claude.com/docs/en/hooks)。

DeepSeek Agent 可借鉴为：

```text
Skills = 可复用流程
Subagents = context isolation
Hooks = runtime lifecycle events
MCP = external capability protocol
Plugins = 组合分发机制
```

---

## 3. 不能直接照搬的地方

### 3.1 Prompt cache 不能照搬，需要 DeepSeek 化

Claude Code prompt cache 是 Anthropic API 机制；DeepSeek API 也有 prefix cache 和 hit/miss，但成本结构、返回字段、1M context 物理机制不同。Claude Code cache 文档强调 exact prefix，且无 per-file/per-segment caching。证据：[Claude Code prompt caching](https://code.claude.com/docs/en/prompt-caching)。

DeepSeek Agent 应做：

```text
prompt_cache_hit_tokens / miss_tokens telemetry
byte-stable prefix
V4 Context Layout
Flash/Pro route-aware cost model
```

### 3.2 Model Router 不能照搬

Claude Code 文档中说明 Sonnet 处理大多数编码任务，Opus 更适合复杂架构决策。证据：[Models in Claude Code](https://code.claude.com/docs/en/how-claude-code-works)。

DeepSeek Agent 的路由应是：

```text
Flash Non-think
Flash Think
Pro Non-think
Pro Think
Pro Max
```

这是由 DeepSeek V4 Flash / Pro 和 thinking modes 决定的，不是 Claude Code 的 Sonnet / Opus 路由。

### 3.3 Desktop / Web / Cloud 不应作为 MVP 全量复制

Claude Code 已经有 Desktop、Web、Cloud、Remote Control、Routines 等完整体系。证据：[Overview multi-surface](https://code.claude.com/docs/en/overview)。

DeepSeek Agent MVP 应先做：

```text
Desktop local-first
API / private endpoint model backend
File / Shell / Git tools
Context Layout
Checkpoint
Pro Review
Cost Telemetry
```

云端异步、routine、remote control 可作为后续阶段。

---

## 4. DeepSeek Agent 应超越 Claude Code 的地方

### 4.1 Cache Telemetry 产品化

Claude Code prompt cache 文档强调可查看 cache hit rate，但 DeepSeek Agent 应把 cache hit/miss 变成核心 UI，因为 DeepSeek 官方 API 直接按 cache hit / miss 计价。

### 4.2 V4-aware Context Layout

Claude Code 有 context compaction 和 subagent isolation，但 DeepSeek V4 的 `sliding_window=128`、CSA/HCA、index_topk 决定我们必须做更强的 layout-driven context。

### 4.3 Checkpoint-driven Pro Review

Claude Code 可以用强模型处理复杂任务；DeepSeek Agent 应更系统化地执行：

```text
Flash 执行
Checkpoint
Pro Review
Flash 继续
Pro Final Review
```

### 4.4 V4 Message Compiler

Claude Code 面向 Anthropic API；DeepSeek Agent 需要 V4 DSML / encoding / reasoning_content policy / tool result merge。

---

## 5. 初步模块映射

| Claude Code 模块 | DeepSeek Agent 对应模块 | 是否照搬 |
|---|---|---|
| CLAUDE.md | Project Memory / Agent Manifest | 借鉴，但需 byte-stable |
| Auto memory | Memory Writer | 借鉴，需用户可控 |
| Prompt caching | Cache Strategy Manager | 借鉴机制，DeepSeek 化 |
| Permissions | Permission Runtime | 必须借鉴 |
| Checkpoints | Checkpoint Snapshotter | 必须借鉴并增强 |
| Skills | Skill Registry | 借鉴，采用 index-in-prefix/body-on-demand |
| Subagents | Subagent Runtime | 借鉴，配合 Flash/Pro route |
| Hooks | Event Bus / Hook Runtime | 借鉴，但 MVP 简化 |
| Plugins | Plugin System | 后期，不进 MVP |
| Cloud sessions | Cloud/Remote Runtime | 后期 |
| Routines | Automation Scheduler | 后期 |

---

## 6. 结论

Claude Code 的核心价值不是某个 UI 或某个工具，而是一个成熟 Harness 范式：

```text
Agent Loop
+ Tool Runtime
+ Permission Runtime
+ Context / Memory / Compaction
+ Session / Checkpoint
+ Skills / Subagents / Hooks / Plugins
+ Multi-surface UI
```

DeepSeek Agent 应借鉴这个 Harness 范式，但最终架构必须围绕 DeepSeek V4 的物理特性重写。


---

## 7. 如果 Claude Code 接入 DeepSeek V4，会发生什么？

这一节是 v0.3 新增的标准问题：每个竞品都必须回答“如果接 DeepSeek V4，它能发挥什么、发挥不了什么、为什么、如何迭代”。

### 7.1 能发挥 DeepSeek V4 的哪些能力？

#### 7.1.1 能发挥：工具型 Agent Loop 能力

Claude Code 已经有成熟的 agentic loop：

```text
gather context
take action
verify results
```

并且具备 file / search / execution / web / code intelligence 等工具类别。因此，如果它能把 DeepSeek V4 接入模型层，DeepSeek V4 的代码理解、长任务推理、工具调用决策能力，理论上能被 Claude Code 的工具 runtime 承接。

原因：

```text
Claude Code 已经不是普通聊天 UI，而是完整 Agent Harness。
模型只需要输出计划、解释、工具调用意图、编辑建议，Runtime 负责实际执行。
```

对 DeepSeek Agent 的启发：

```text
我们不需要重新发明工具循环的基本形态；
但要把工具循环 DeepSeek 化：V4 message compiler、cache telemetry、Flash/Pro router、checkpoint review。
```

#### 7.1.2 能发挥：长任务上下文与项目记忆能力的一部分

Claude Code 已经有：

```text
CLAUDE.md
auto memory
context compaction
session resume / fork / rewind
subagent isolated context
skills body-on-demand
```

这些机制可以帮助 DeepSeek V4 使用 1M context，尤其是在大型代码库任务、长 session、复杂 refactor、测试修复中。

原因：

```text
DeepSeek V4 的 1M context 需要 Harness 做上下文组织；
Claude Code 已经有 manifest / memory / compaction / subagent / skill 这些上下文工程组件。
```

但注意：这只能发挥“一部分”1M context 能力，因为 Claude Code 的上下文机制是为 Claude 模型和 Anthropic API 设计的，不是为 V4 的 CSA / HCA / sliding_window=128 / index_topk 设计的。

#### 7.1.3 能发挥：权限、checkpoint、session 可靠性

Claude Code 的 permissions、checkpoints、session JSONL、file snapshot 设计，可以直接帮助 DeepSeek V4 做更安全的本地执行。

原因：

```text
模型是否强，不等于执行是否安全。
权限、checkpoint、snapshot 必须由 Harness Runtime 执行。
```

DeepSeek Agent 应直接吸收这一点。

#### 7.1.4 能发挥：Skills / Subagents / Hooks 扩展能力

Claude Code 的 skills、subagents、hooks、plugins 让 Agent 能力可扩展。如果接入 DeepSeek V4，这些扩展机制依然有价值。

尤其是：

```text
Skills ≈ DeepSeek Agent 的 procedure package
Subagents ≈ 长上下文隔离 / Flash 子任务 / Pro reviewer
Hooks ≈ Tool Runtime event bus
Plugins ≈ 后期生态分发
```

---

### 7.2 发挥不了 DeepSeek V4 的哪些能力？

#### 7.2.1 发挥不了：DeepSeek V4 的 cache hit / miss 成本优势

Claude Code 的 prompt caching 是围绕 Anthropic API 的 exact prefix matching 设计的。即使它的思想和 DeepSeek cache 类似，也不会天然使用 DeepSeek API 的：

```text
prompt_cache_hit_tokens
prompt_cache_miss_tokens
cache hit / miss differential pricing
DeepSeek-specific prefix unit behavior
```

如果只是把模型 endpoint 换成 DeepSeek V4，它可能可以“调用成功”，但很难把 DeepSeek 的低成本优势最大化。

原因：

```text
DeepSeek 的成本优势不是只靠模型便宜；
而是靠 Harness 主动制造 byte-stable prefix、稳定 tool schema、稳定 memory/skill index、动态信息 ride tail，并在 UI 中显示 cache hit/miss。
Claude Code 的产品 UI 和 telemetry 不是为 DeepSeek cache pricing 定制的。
```

DeepSeek Agent 应该做：

```text
CostCacheTelemetry
PrefixDriftDetector
StableToolSchemaSerializer
CacheHitMissDashboard
```

#### 7.2.2 发挥不了：V4 的 CSA / HCA 所要求的 context layout

DeepSeek V4 的长上下文不是 dense 1M attention，而是：

```text
local window + compressed history + sparse top-k retrieval
```

Claude Code 有 compaction 和 memory，但它不会天然知道：

```text
sliding_window=128
compress_ratio=4 / 128
index_topk=512 / 1024
Flash 前两层 compress=0
Pro 前两层 compress=128
```

所以它无法自动为 V4 设计：

```text
Task Anchor Zone
Active Working Set
Compressed History Zone
Turn Tail
attention-anchor plan graph
checkpoint-driven context
```

结果是：

```text
DeepSeek V4 可以吃 1M context；
但 Claude Code 未必能把最该被 V4 看见的信息放在最合适的位置。
```

#### 7.2.3 发挥不了：Flash / Pro / Thinking / Max 的精细路由

Claude Code 的模型路由围绕 Claude 家族，例如 Sonnet / Opus 的能力成本差异。它不会天然支持 DeepSeek V4 的五档路由：

```text
Flash Non-think
Flash Think
Pro Non-think
Pro Think
Pro Max
```

因此如果接 DeepSeek V4，它可能会出现：

```text
简单任务用 Pro，浪费成本；
复杂 review 用 Flash，质量不足；
局部 edit 用 thinking，浪费；
最终审查没有 Pro Max；
失败复盘没有自动升级。
```

DeepSeek Agent 必须自己实现 ModelRouter。

#### 7.2.4 发挥不了：V4 encoding / DSML tool calling 的全部细节

Claude Code 面向 Anthropic 模型协议。DeepSeek V4 的官方 encoding 则有：

```text
专用 encoding_dsv4.py
DSML tool_calls
tool results merge into user message
thinking / non-thinking block
reasoning_effort=max special prefix
drop_thinking 策略
```

如果 Claude Code 只是通过 OpenAI-compatible endpoint 接 DeepSeek V4，可能可以完成普通对话和部分工具调用，但很难完整利用 V4 的原生 message protocol。

DeepSeek Agent 应该实现：

```text
DeepSeekV4MessageCompiler
DSMLToolParser
ToolResultMerger
ReasoningContentPolicy
```

#### 7.2.5 发挥不了：DeepSeek reasoning_content 的最优管理

Claude Code 有自己的 context compaction 和 reasoning 隐藏策略，但 DeepSeek V4 的 reasoning_content 管理需要结合：

```text
drop old reasoning
tools 时 reasoning 可能保留
reasoning 不等于 memory
reasoning → checkpoint / skill / failure note
```

Claude Code 不会天然按 DeepSeek V4 的 encoding 逻辑去管理 reasoning 原文、摘要、归档和回传。

---

### 7.3 Claude Code 若要更好适配 DeepSeek V4，需要怎么迭代？

如果 Claude Code 要真正成为优秀的 DeepSeek V4 Harness，需要至少做以下迭代。

#### 7.3.1 增加 DeepSeekV4 Provider

```text
支持 deepseek-v4-flash / deepseek-v4-pro
支持 thinking / non-thinking / max
支持 DeepSeek usage 字段
支持 cache hit/miss telemetry
支持 V4 max output / 1M context 能力探测
```

#### 7.3.2 增加 DeepSeekV4MessageCompiler

```text
OpenAI / Anthropic internal messages
→ DeepSeek V4 encoding
→ DSML tool calling
→ tool result merge
→ reasoning_content policy
```

#### 7.3.3 增加 V4-aware Context Layout

```text
Stable Prefix
Task Anchor
Active Working Set
Compressed History
Turn Tail
```

并且要针对 Flash / Pro 的不同 index_topk 和 compress pattern 做不同布局。

#### 7.3.4 增加 Flash / Pro Router

```text
Flash 执行
Pro 规划
Pro review
Pro failure analysis
Pro final review
Max only for critical decisions
```

#### 7.3.5 增加 DeepSeek Cost Dashboard

```text
cache_hit_tokens
cache_miss_tokens
output_tokens
thinking mode
route reason
estimated marginal cost
prefix drift warnings
```

---

### 7.4 Claude Code 自己会不会做这些迭代？

#### 判断：大概率不会为 DeepSeek V4 做深度专属优化

原因：

```text
Claude Code 是 Anthropic 自家的模型产品和生态入口；
它的战略目标是发挥 Claude 模型能力，而不是成为任意模型的通用最优 Harness。
```

它可能会做：

```text
更好的 Claude 模型路由
更好的 Claude prompt caching
更好的 CLAUDE.md / skills / hooks / subagents
更强 Desktop / Web / GitHub / Slack 体验
```

但它不太可能做：

```text
DeepSeek cache hit/miss UI
DeepSeek V4 DSML message compiler
DeepSeek Flash/Pro/Max route
DeepSeek CSA/HCA-aware context layout
DeepSeek-specific cost optimizer
```

所以 Claude Code 对我们最大的价值不是“拿来即用接 DeepSeek”，而是：

```text
学习成熟 Agent Harness 范式；
然后围绕 DeepSeek V4 重写关键层。
```

---

### 7.5 对 DeepSeek Agent 的最终启发

Claude Code 证明了顶级 Agent 产品应该具备：

```text
多端入口
统一 Agent Runtime
成熟 Tool Runtime
强权限系统
Memory / Skills / Subagents / Hooks
Session / Checkpoint
可解释执行日志
IDE / Desktop / CLI 协同
```

但 DeepSeek Agent 必须在以下方面做得比 Claude Code 更 DeepSeek-native：

```text
1. V4-aware Context Layout
2. DeepSeek cache hit/miss optimization
3. Flash / Pro / Thinking / Max Router
4. V4MessageCompiler + DSML Tool Runtime
5. Checkpoint-driven Pro Review
6. ReasoningContentPolicy
7. CostCacheTelemetry
8. Local-first endpoint-based desktop product
```

最终结论：

```text
Claude Code 是 Harness 形态标杆；
但不是 DeepSeek V4 的最优 Harness。
DeepSeek Agent 的机会就在这里。
```
