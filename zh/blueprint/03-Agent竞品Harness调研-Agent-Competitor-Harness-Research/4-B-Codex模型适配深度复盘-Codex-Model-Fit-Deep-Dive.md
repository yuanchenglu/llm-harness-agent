# 4-B Codex 模型适配深度复盘 Codex Model Fit Deep Dive

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

> 本文件是对 v0.4 Codex 调研的升级版。  
> 目标：深入分析 Codex 产品/源码如何配合 OpenAI 模型能力；如果接入 DeepSeek V4，哪些能力能发挥，哪些无法发挥。

---

## 1. Codex 与 OpenAI 模型的协作方式

官方 README 明确区分 Codex CLI、IDE、Codex App、Codex Web/Cloud。证据：[openai/codex README](https://github.com/openai/codex/blob/main/README.md)。

Codex CLI 官方文档说明，它是本地 terminal coding agent，可以读取、修改、运行本机目录中的代码，且 open source、Rust 实现。证据：[Codex CLI docs](https://developers.openai.com/codex/cli)。

Codex App 官方文档称其为 Codex command center，支持 parallel threads、worktrees、automations、Git functionality。证据：[Codex App docs](https://developers.openai.com/codex/app)。

这说明 Codex 的模型协作不止是 CLI：

```text
CLI：本地 agent runtime
App：桌面 task/thread/review/worktree 工作台
Web/Cloud：云端异步任务系统
```

---

## 2. Codex 针对 OpenAI 模型做了哪些适配？

### 2.1 Reasoning level / model capability 适配

Codex 的源码 `TurnContext` 中有 `model_info`、`tool_mode`、`reasoning_effort`、`reasoning_summary`、`truncation_policy`、`available_models` 等字段，并有 `effective_reasoning_effort`、`model_context_window`、`with_model` 等逻辑。源码证据：`openai/codex` `codex-rs/core/src/session/turn_context.rs`，官方仓库：[openai/codex](https://github.com/openai/codex)。

这说明 Codex 不是只调用一个模型，而是在 runtime 层理解：

```text
模型支持哪些 reasoning levels
模型 context window 多大
模型使用什么 tool mode
模型切换后 reasoning_effort 如何调整
```

这比普通 wrapper 深得多。

### 2.2 Typed context / cache-aware context discipline

`AGENTS.md` 中 “Model visible context” 规则要求：

```text
No history rewrite
Avoid frequent changes to context that cause cache misses
No unbounded items
No items larger than 10K tokens
>1K tokens 新项需要 P0 review
injected fragments 必须定义为 core/context structs 并实现 ContextualUserFragment
```

证据：[AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)。

这说明 Codex 对模型 context 的适配比 Claude Code 更工程化：

```text
不是随便拼 prompt；
而是 typed context fragments + hard cap + cache miss awareness。
```

### 2.3 App 层对模型工作流的适配

Codex App 支持 worktrees、integrated terminal、review pane、task sidebar、automations。证据：[Codex App features](https://developers.openai.com/codex/app/features)。

这说明 Codex 把模型的代码修改能力转化成 UI 上的：

```text
thread
worktree
diff review
terminal verification
artifact / summary
task sidebar
```

模型不是孤立回答，而是嵌入“代码任务操作台”。

### 2.4 权限 / 沙箱适配

Codex permissions 支持 read-only、workspace、danger-full-access，且有网络规则和 OS-level sandbox enforcement。证据：[Codex permissions](https://developers.openai.com/codex/permissions)。

这说明 Codex 明确把模型动作限制在 runtime policy 中。

---

## 3. DeepSeek V4 物理特性适配矩阵

| DeepSeek V4 物理特性 | Codex 当前 Harness 是否能发挥 | 评分 | 原因 |
|---|---|---:|---|
| 1M context | 部分能 | B | 有 context window、auto compact、typed fragments、hard caps，但不是 V4 layout |
| CSA/HCA sparse context | 基本不能 | C | 没有证据显示它按 sliding_window=128 / index_topk / compressed history 布局 |
| DeepSeek cache hit/miss | 部分能 | B- | AGENTS.md 已强调 cache misses，但不是 DeepSeek pricing / telemetry |
| Flash/Pro/Thinking/Max | 部分能 | B- | 有 model / reasoning_effort runtime，但不懂 DeepSeek Flash/Pro 五档路由 |
| V4 encoding / DSML | 不能 | D | Codex 适配 OpenAI Responses/Codex 协议，不会天然使用 V4 DSML |
| reasoning_content policy | 部分能 | C | 有 reasoning_effort/summary 字段，但不是 DeepSeek reasoning_content 四态 |
| checkpoint-driven Pro review | 部分能 | B | App 有 review pane / worktree / task summary，但不是 Flash execute + Pro review |
| typed context fragments | 能 | A | AGENTS.md 明确要求 ContextualUserFragment |
| App-level task workstation | 能 | A | App 是 command center，适合 DeepSeek Agent 桌面形态 |
| OS sandbox / permissions | 能 | A | 权限 profile 和 OS sandbox 很强 |

---

## 4. Codex 如果接 DeepSeek V4，能发挥什么？

### 4.1 能发挥：本地/桌面/云任务工作流

Codex 的 CLI/App/Web 三形态非常成熟。DeepSeek V4 如果接入，能利用：

```text
local file/shell/git
worktree isolation
review pane
integrated terminal
task sidebar
MCP
skills
subagents
permissions
```

### 4.2 能发挥：部分 long context discipline

Codex 的 typed context fragment 和 hard cap 规则非常适合 DeepSeek V4，尤其是：

```text
No unbounded items
No item >10K tokens
large item P0 review
context structs
```

这些可以直接升级为 DeepSeek Agent 的 ContextFragment / CacheZone / TokenBudget。

### 4.3 能发挥：一部分 reasoning route

Codex runtime 已有 reasoning_effort 和 model context window 概念，所以比普通 Agent 更容易适配 DeepSeek Flash/Pro/Think/Max。

---

## 5. Codex 发挥不了什么？

### 5.1 发挥不了 V4 原生 encoding

Codex 的协议是 OpenAI/Codex 协议；DeepSeek V4 有独立 encoding、DSML tool calling、tool result merge、drop_thinking、reasoning_effort=max special prefix。

如果只接 custom provider，大概率只能走 generic adapter，吃不到 V4 原生协议细节。

### 5.2 发挥不了 V4 sparse attention layout

Codex typed context 能避免无限膨胀，但没有证据显示它会针对：

```text
sliding_window=128
CSA/HCA
compress_ratio=4/128
index_topk=512/1024
Flash/Pro compress pattern
```

做布局。因此它能“控制上下文规模”，但不能“针对 V4 物理注意力路径优化上下文位置”。

### 5.3 发挥不了 DeepSeek cache pricing

Codex 已经关注 cache misses，但 DeepSeek 的核心是：

```text
prompt_cache_hit_tokens
prompt_cache_miss_tokens
cache hit/miss price differential
```

这需要 UI、telemetry、route policy、prefix drift detection 联动。Codex 作为 OpenAI 产品不会天然做 DeepSeek-specific dashboard。

### 5.4 发挥不了 checkpoint-driven Pro Review

Codex App 有 review pane，但 DeepSeek Agent 需要更模型侧的 pattern：

```text
Flash execute
checkpoint
Pro review
Flash continue
Pro final review
```

Codex 的 review 更偏 Git/diff/task UI，不是 DeepSeek model router 原生策略。

---

## 6. Codex 是否可能做 DeepSeek V4 专属迭代？

判断：**通用 provider 层可能，DeepSeek-specific 物理特性适配概率低。**

Codex 可能继续做：

```text
custom provider
model context window
reasoning level
tool/runtime permissions
App command center
worktree/review/cloud tasks
```

但不太可能做：

```text
DeepSeek V4 DSML compiler
DeepSeek cache hit/miss dashboard
DeepSeek CSA/HCA-aware layout
DeepSeek Flash/Pro/Max router
DeepSeek reasoning_content four-state policy
```

原因：Codex 是 OpenAI 自家 coding agent，它会把最深优化留给 OpenAI 模型与 Codex App/Web/Responses/Codex 协议。

---

## 7. DeepSeek Agent 应该如何借鉴 Codex？

### 必须借鉴

```text
1. App command center，而不是纯 chat
2. Task/thread/worktree/review/terminal 一体化
3. typed context fragments
4. hard token caps
5. no history rewrite
6. avoid cache misses
7. permission profiles + OS sandbox
8. review pane + inline comments
9. subagents / skills / MCP
```

### 必须超越

```text
1. DeepSeek V4 Context Layout Manager
2. DeepSeek cache hit/miss telemetry
3. Flash / Pro / Thinking / Max Router
4. DeepSeekV4MessageCompiler
5. DSMLToolParser
6. ReasoningContentPolicy
7. Checkpoint-driven Pro Review
8. V4-specific cost-quality policy
```

最终结论：

```text
Codex 比 Claude Code 更接近“DeepSeek Agent 桌面工作台”的产品形态；
但它仍不是 DeepSeek V4-native Harness。
```
