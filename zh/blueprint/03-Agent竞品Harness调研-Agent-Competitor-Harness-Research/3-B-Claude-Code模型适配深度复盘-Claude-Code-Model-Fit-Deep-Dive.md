# 3-B Claude Code 模型适配深度复盘 Claude Code Model Fit Deep Dive

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

> 本文件是对 v0.2 Claude Code 调研的升级版。  
> 目标：不再只问 Claude Code 有哪些功能，而是问：Claude Code 如何把 Claude 模型能力变成 Agent 能力？如果接入 DeepSeek V4，它能发挥什么、发挥不了什么、为什么？

---

## 1. Claude Code 与 Claude 模型的协作方式

Claude Code 官方文档明确说，它的 agentic loop 是：

```text
gather context → take action → verify results
```

并且 Claude Code serves as the agentic harness around Claude，提供 tools、context management、execution environment，把语言模型变成 coding agent。证据：[Claude Code How it works](https://code.claude.com/docs/en/how-claude-code-works)。

这句话很关键：

```text
模型负责理解、推理、决策；
Harness 负责工具、上下文、执行环境。
```

所以 Claude Code 的本质不是“工具壳”，而是把 Claude 模型的长上下文、推理、工具选择、代码理解能力映射到真实文件/命令/版本控制环境。

---

## 2. Claude Code 对 Claude 模型做了哪些物理特性适配？

### 2.1 上下文适配：让 Claude 看见项目，而不是只看当前文件

官方文档说明，Claude Code 可以访问 project files、terminal、git state、CLAUDE.md、auto memory、extensions，并通过搜索、读取多文件、运行测试来处理跨项目任务。证据：[What Claude can access](https://code.claude.com/docs/en/how-claude-code-works)。

这说明 Claude Code 针对 Claude 的长上下文和代码理解能力做了 Harness 适配：

```text
项目级上下文
多文件读取
git state
terminal output
CLAUDE.md
auto memory
extensions
```

### 2.2 Compaction / Memory：适配有限 context window

Claude Code context docs 说明，`/compact` 会把 conversation 替换为 structured summary；compaction 后 project-root CLAUDE.md、auto memory 会重新注入，path-scoped rules / nested CLAUDE.md 可能丢失直到再次触发。证据：[Claude Code context window](https://code.claude.com/docs/en/context-window)。

这说明 Claude Code 针对 Claude context window 做了：

```text
structured summary
memory re-injection
skill body re-injection
path-scoped rules lazy reload
```

### 2.3 Prompt caching：适配 Anthropic prefix cache

Claude Code prompt caching 文档强调 exact prefix matching；任何 prefix 中的变化都会导致后续内容重算。证据：[Claude Code prompt caching](https://code.claude.com/docs/en/prompt-caching)。

这说明 Claude Code 已经有“prefix stability”意识，但它面向的是 Anthropic API，不是 DeepSeek API 的 cache hit/miss 字段和价格结构。

### 2.4 Skills / Subagents：适配长上下文污染和任务分解

Skills 的 body only loaded when used，适合把重复流程从 CLAUDE.md 抽离。证据：[Claude Code Skills](https://code.claude.com/docs/en/skills)。

Subagents 有独立 context window、独立 prompt、tool access、permissions，并返回 summary。证据：[Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)。

这说明 Claude Code 已经通过：

```text
Skill progressive loading
Subagent context isolation
```

适配了模型 context budget 和任务分解问题。

---

## 3. DeepSeek V4 物理特性适配矩阵

| DeepSeek V4 物理特性 | Claude Code 当前 Harness 是否能发挥 | 评分 | 原因 |
|---|---|---:|---|
| 1M context | 部分能 | B | 有项目上下文、memory、compaction、skills、subagents，但不是 V4-specific layout |
| CSA/HCA sparse long context | 基本不能 | C | 没有 evidence 显示其理解 sliding_window=128 / index_topk / compressed history |
| DeepSeek cache hit/miss | 基本不能 | C | 有 prompt caching 思想，但不是 DeepSeek cache telemetry 和 pricing |
| Flash/Pro/Thinking/Max 路由 | 不能 | D | Claude Code 路由围绕 Claude 模型，Sonnet/Opus；不支持 V4 五档路由 |
| V4 encoding / DSML | 不能 | D | Claude Code 使用 Anthropic 协议，不会原生编译 DeepSeek DSML |
| reasoning_content policy | 部分能 | C | 有 compaction，但不是 DeepSeek reasoning_content display/archive/summarize/prompt 四态 |
| checkpoint-driven review | 部分能 | B | 有 checkpoints、sessions，但没有 Flash 执行 + Pro review 的 DeepSeek pattern |
| Permission / sandbox | 能 | A | 权限由 runtime 执行，不依赖模型。证据：[Claude permissions](https://code.claude.com/docs/en/permissions) |
| Tool runtime | 能 | A | 文件、搜索、执行、web、code intelligence 工具体系完整。证据：[Claude tools](https://code.claude.com/docs/en/how-claude-code-works) |
| Skills / subagents | 能 | A | 可直接借鉴为 skill registry 和 subagent runtime |

---

## 4. 如果 Claude Code 接 DeepSeek V4，哪里会“看起来能跑，但吃不满”？

### 4.1 会跑：因为 Claude Code 有成熟 Agent Loop

只要模型能输出合适的文本/工具意图，Claude Code 的 runtime 可以继续读文件、改文件、跑测试。

### 4.2 吃不满：因为 V4 的关键优势需要专属 Harness

DeepSeek V4 的价值不只是“模型回答能力”，而是：

```text
1M context 的布局使用
cache hit/miss 的工程化
Flash/Pro/Thinking/Max 的动态路由
DSML / encoding 的协议适配
reasoning_content 的生命周期管理
```

Claude Code 如果只是换 endpoint，不会天然得到这些。

---

## 5. Claude Code 后续会不会针对 DeepSeek V4 迭代？

判断：**几乎不会深度适配**。

原因：

```text
Claude Code 是 Anthropic 自家模型产品；
它的核心优化目标是 Claude 模型、Anthropic cache、Claude 工具协议和 Anthropic 生态。
```

它会持续强化：

```text
Claude 模型路由
Claude context / memory / skills
Claude prompt caching
Claude subagents / hooks / MCP
Desktop / Web / Remote Control
```

但不太可能做：

```text
DeepSeek V4 DSML compiler
DeepSeek cache hit/miss pricing dashboard
V4 CSA/HCA-aware context layout
Flash/Pro/Max router
DeepSeek-specific cost optimizer
```

---

## 6. DeepSeek Agent 必须怎么超越 Claude Code？

Claude Code 是成熟 Harness 范式标杆，但 DeepSeek Agent 要做的是 **V4-native Harness**：

```text
1. Stable Prefix + CacheHitTelemetry
2. V4 Context Layout：Stable Prefix / Task Anchor / Active Working Set / Compressed History / Turn Tail
3. Flash / Pro / Thinking / Max Router
4. DeepSeekV4MessageCompiler + DSMLToolParser
5. ReasoningContentPolicy
6. Checkpoint-driven Pro Review
7. Cost-aware UI
```

最终结论：

```text
Claude Code 的工具、权限、session、skills、subagents 值得学；
但它没有、也大概率不会有 DeepSeek V4 的最优物理特性适配。
```
