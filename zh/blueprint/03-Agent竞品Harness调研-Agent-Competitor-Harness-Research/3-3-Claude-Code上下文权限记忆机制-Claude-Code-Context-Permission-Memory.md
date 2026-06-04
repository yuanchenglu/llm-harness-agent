# 3-3 Claude Code 上下文权限记忆机制 Claude Code Context Permission Memory

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

## 1. 目标

本文件拆解 Claude Code 的 context、memory、permission、prompt cache、skills、subagents、hooks。

---

## 2. Context Window

官方 context window 页面说明，在用户输入前，CLAUDE.md、auto memory、MCP tool names、skill descriptions 都会加载进 context；Claude 工作过程中，读取的文件会进入 context，path-scoped rules 会随匹配文件加载。证据：[Context window timeline](https://code.claude.com/docs/en/context-window)。

官方还说明，subagent 能在独立 context window 中处理 research，主会话只接收 summary 和 metadata trailer。证据：[Subagent separate context](https://code.claude.com/docs/en/context-window)。

---

## 3. Compaction

官方说明 `/compact` 会将 conversation 替换为 structured summary；compaction 后：

```text
system prompt / output style 不变
project-root CLAUDE.md 和 unscoped rules 从磁盘重新注入
auto memory 重新注入
path-scoped rules / nested CLAUDE.md 会丢失，直到匹配文件再次读取
invoked skill bodies 会重新注入，但有 token cap
```

证据：[What survives compaction](https://code.claude.com/docs/en/context-window)。

### 对 DeepSeek Agent 的启发

DeepSeek Agent 应有：

```text
Checkpoint Snapshot
Stable Memory / Skill Index
Context Compaction Policy
Post-compaction Re-injection Rules
```

---

## 4. Prompt Caching

官方 prompt caching 页面说明，每轮请求会重新发送 full context，但 API 根据请求开头 prefix 精确匹配来复用已处理内容；任何 prefix 中的变化都会导致后续内容重算；没有 per-file 或 per-segment caching。证据：[Prompt caching exact prefix](https://code.claude.com/docs/en/prompt-caching)。

### 对 DeepSeek Agent 的启发

这与 DeepSeek API 的 cache hit / miss 高度同构。DeepSeek Agent 要更进一步产品化：

```text
Stable prefix
Stable tool schema
Stable memory / skill index
Dynamic tail
Cache hit/miss telemetry
Prefix drift detector
```

---

## 5. Memory

官方 memory 页面说明，每个 session 都从 fresh context window 开始；跨 session 有两种机制：

```text
CLAUDE.md：用户写
Auto memory：Claude 根据纠正和偏好自动写
```

证据：[Memory overview](https://code.claude.com/docs/en/memory)。

官方还说明，CLAUDE.md 和 auto memory 都是 context，不是 enforced configuration；如果要强制阻止动作，应使用 PreToolUse hook。证据：[CLAUDE.md vs auto memory](https://code.claude.com/docs/en/memory)。

### DeepSeek Agent 启发

```text
Memory = 提醒模型
Permission = Runtime 强制
Policy = 工具层规则
```

不要用 prompt memory 替代权限系统。

---

## 6. Permissions

官方 permissions 页面说明，Claude Code 支持 allow / ask / deny，规则顺序 deny → ask → allow；权限由 Claude Code 执行，不由模型执行。证据：[Permission system](https://code.claude.com/docs/en/permissions)。

官方 permission modes：

```text
default
acceptEdits
plan
auto
dontAsk
bypassPermissions
```

证据：[Permission modes](https://code.claude.com/docs/en/permissions)。

### DeepSeek Agent 启发

MVP 权限模式建议：

```text
read：默认允许
edit/write：询问或 acceptEdits
shell：询问，可 allowlist
delete / remote side effects：强询问或禁止
plan mode：只读
bypass：仅隔离环境
```

---

## 7. Subagents

官方说明，subagent 是专门处理特定任务的 AI assistant，拥有独立 context window、自定义 system prompt、specific tool access、independent permissions，并返回结果 summary。证据：[Subagents overview](https://code.claude.com/docs/en/sub-agents)。

### DeepSeek Agent 启发

Subagent 是解决长上下文污染的关键方式：

```text
研究任务给 subagent
主线程只接收 summary
高噪声日志分析给 subagent
低成本 Flash subagent / 高质量 Pro reviewer 可分工
```

---

## 8. Skills

官方说明，skills 用 `SKILL.md` 扩展 Claude 能力；skill body 只在使用时加载，所以长参考材料在不用时几乎不消耗 context；适合把重复流程从 CLAUDE.md 中抽离。证据：[Skills overview](https://code.claude.com/docs/en/skills)。

### DeepSeek Agent 启发

这正好对应我们在 V4 调研中提出的：

```text
index in prefix
body on demand
```

即 prefix 只放 skill index，真正的 skill body 按需加载进 active working set。

---

## 9. Hooks

官方 hooks reference 列出大量事件，包括：

```text
SessionStart
InstructionsLoaded
UserPromptSubmit
PreToolUse
PermissionRequest
PostToolUse
PostToolUseFailure
SubagentStart
SubagentStop
TaskCreated
TaskCompleted
PreCompact
PostCompact
SessionEnd
```

证据：[Hooks reference](https://code.claude.com/docs/en/hooks)。

### DeepSeek Agent 启发

DeepSeek Agent 的 Tool Runtime 也应有 event bus：

```text
BeforeToolUse
AfterToolUse
ToolFailed
BeforeCompact
AfterCompact
BeforeReview
AfterReview
TaskCompleted
```

但 MVP 可先做最小集：PreToolUse / PostToolUse / ToolFailed / CheckpointCreated。
