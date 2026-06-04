# 3-2 Claude Code Harness 架构调研 Claude Code Harness Architecture

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

## 1. 目标

本文件回答：Claude Code 的 Harness 如何把 Claude 模型变成 coding agent？

---

## 2. Agent Loop

官方 Docs 明确说，Claude Code 在任务中经历三个阶段：

```text
gather context
take action
verify results
```

这些阶段会交织发生；Claude 会使用工具搜索文件、编辑、运行测试，并基于上一轮结果不断调整；用户可随时 interrupt 和 steer。证据：[The agentic loop](https://code.claude.com/docs/en/how-claude-code-works)。

官方还明确说，Claude Code serves as the agentic harness around Claude，提供 tools、context management、execution environment，使语言模型变成 coding agent。证据：[How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works)。

---

## 3. Tool Runtime

官方将 built-in tools 分成五类：

```text
File operations
Search
Execution
Web
Code intelligence
```

证据：[Tools categories](https://code.claude.com/docs/en/how-claude-code-works)。

官方示例中，“fix failing tests”会触发：

```text
run tests
read errors
search source files
read files
edit files
rerun tests
```

证据：[Tools example loop](https://code.claude.com/docs/en/how-claude-code-works)。

---

## 4. Execution Environment

官方定义三种执行环境：

```text
Local：用户机器
Cloud：Anthropic-managed VMs
Remote Control：浏览器控制用户机器，本地执行
```

证据：[Execution environments](https://code.claude.com/docs/en/how-claude-code-works)。

### 对 DeepSeek Agent 的初步启发

MVP 应采用：

```text
Local-first desktop tool execution
DeepSeek API / private endpoint model execution
未来再扩展 cloud/offload
```

---

## 5. Session / State

官方说明 Claude Code 将 conversation 存为 plaintext JSONL，包含每条 message、tool use、result，位于 `~/.claude/projects/`；支持 rewind、resume、fork；文件编辑前还 snapshot affected files。证据：[Work with sessions](https://code.claude.com/docs/en/how-claude-code-works)。

### DeepSeek Agent 启发

需要：

```text
Task DB
Session trace
Tool call log
Checkpoint snapshot
Resume / fork
Diff / file snapshot
```

---

## 6. Safety Harness

Claude Code 的安全基础是：

```text
permissions
checkpoints
```

官方说明权限控制 Claude Code 可以做什么，checkpoint 允许撤销本地文件编辑；远程系统副作用无法 checkpoint，需要询问用户。证据：[Stay safe with checkpoints and permissions](https://code.claude.com/docs/en/how-claude-code-works)。

---

## 7. Extensibility

Claude Code 的扩展体系包括：

```text
Skills
MCP
Hooks
Subagents
Plugins
Agent SDK
```

证据：[Extensions on top of core loop](https://code.claude.com/docs/en/how-claude-code-works)、[Skills](https://code.claude.com/docs/en/skills)、[Hooks](https://code.claude.com/docs/en/hooks)、[Subagents](https://code.claude.com/docs/en/sub-agents)、[official plugins repo](https://github.com/anthropics/claude-code/tree/main/plugins)。

### 架构抽象

```text
Agent Loop
+ Tool Runtime
+ Context Manager
+ Permission Runtime
+ Session / Checkpoint Store
+ Memory / Manifest Layer
+ Extension Layer
+ Multi-surface UI
+ Execution Environment Abstraction
```

---

## 8. 与 DeepSeek Agent 的关系

Claude Code 的通用 Harness 经验可以借鉴：

```text
工具循环必须可验证
权限必须由 Runtime 执行
上下文必须可压缩、可观察
Memory / Manifest 是跨会话入口
Subagents 是 context isolation 机制
Skills 是 procedure packaging
Hooks 是生命周期扩展点
Session / checkpoint 是长任务可靠性基础
```

DeepSeek Agent 的差异化必须体现在：

```text
DeepSeek V4 Context Layout Manager
DeepSeek API cache hit/miss telemetry
Flash / Pro / Thinking Router
V4 Message Compiler
Checkpoint-driven Pro Review
```
