# 9-0 CodeWhale 源码审计 Pass 1 CodeWhale Source Audit Pass 1

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.0  
> 仓库：`Hmbown/CodeWhale`  
> 状态：README + docs/ARCHITECTURE.md + 仓库结构 Pass 1 完成；后续需继续读 `crates/tui`、`crates/core`、`crates/agent`、`crates/execpolicy`、`crates/mcp`、`crates/state`。

---

## 1. 仓库定位

CodeWhale README 明确写到：

```text
Terminal coding agent for DeepSeek V4.
Streams reasoning blocks.
Edits local workspaces with approval gates.
Includes an auto mode that chooses both model and thinking level per turn.
```

它还明确说：

```text
CodeWhale is a harness built around DeepSeek V4.
DeepSeek V4's prefix caching makes the long Constitution practical.
```

---

## 2. 仓库结构扫描

根目录关键结构：

```text
.codewhale/
crates/
docs/
integrations/
web/
Cargo.toml
config.example.toml
package.json
```

这说明 CodeWhale 是 Rust workspace，以 `codewhale` / `codewhale-tui` 二进制方式发布。

---

## 3. README 关键源码级/架构级事实

### 3.1 Constitution

README 提到：

```text
CodeWhale answers conflicting instructions with a Constitution (`prompts/base.md`).
Article VII ranks nine tiers from Constitution down to prior-session handoffs.
Current user message outranks stale project instructions.
Live tool output outranks assumptions.
Verification outranks confidence.
```

这说明 CodeWhale 针对模型漂移/指令冲突做了 prompt protocol 层适配。

### 3.2 DeepSeek Prefix Cache

README 明确说：

```text
DeepSeek V4's prefix caching makes this practical.
The Constitution is long and detailed, but once cached it costs roughly 100× less per turn than a cold read.
```

这比 Claude/Codex/Trae 都更 DeepSeek-native。

### 3.3 Auto Mode

README 写到：

```text
--model auto
/model auto

Auto mode controls:
Model: deepseek-v4-flash or deepseek-v4-pro
Thinking: off, high, max

Before the real turn, app makes a small deepseek-v4-flash routing call with thinking off.
```

这是非常接近我们要的：

```text
Flash cheap router
V4 Flash/Pro/Thinking router
```

### 3.4 Subagents

README 写到 subagents 可并行运行，`agent_open` 非阻塞返回，完成后注入 `<codewhale:subagent.done>` sentinel；完整子 transcript 通过 handle 读取，避免父上下文膨胀。

### 3.5 Side-git snapshot

README 写到每轮记录 side-git snapshot，不污染用户 `.git`，`/restore` 与 `revert_turn` 可回滚 workspace。

---

## 4. ARCHITECTURE.md 关键事实

Architecture 文档说明当前真实运行边界：

```text
crates/tui is still the live end-user runtime for TUI, runtime API, task manager, and tool execution loop.
```

并列出核心架构：

```text
TUI / one-shot / config CLI
Core Engine
Agent Loop
Session
Turn Mgmt
Tool Orchestration
Tool & Extension Layer
Runtime API + Task Management
LLM Layer
```

关键模块：

```text
core/engine.rs
core/engine/turn_loop.rs
core/engine/capacity_flow.rs
session.rs
turn.rs
events.rs
ops.rs
client.rs
llm_client.rs
models.rs
tools/
mcp.rs
skills.rs
hooks.rs
lsp/
sandbox/
compaction.rs
purge.rs
pricing.rs
runtime_api.rs
runtime_threads.rs
task_manager.rs
```

### 4.1 LSP after edit

Architecture 文档明确：LSP subsystem 已接入 post-tool-execution path，`edit_file/apply_patch/write_file` 成功后收集 diagnostics，并在下一次 API request 前作为 synthetic user message 注入。

这对 DeepSeek Agent Code Mode 非常重要。

### 4.2 Tool execution data flow

Architecture 文档列出工具执行：

```text
LLM requests tool via tool_use content block
Tool registry looks up handler
Pre-execution hooks run
Approval requested if needed
Tool executed
Post-execution hooks run
Result metadata retained
LSP post-edit hook runs
Diagnostics injected before next request
Result returned to agent loop
```

### 4.3 Crash recovery + offline queue

Architecture 文档列出：

```text
before user input, write checkpoint snapshot
offline prompts mirrored to offline_queue.json
successful turn clears active checkpoint and writes durable session snapshot
Agent/Yolo turns take pre/post-turn side-git snapshots
```

---

## 5. Model-Harness Fit Matrix

| DeepSeek V4 特性 | CodeWhale 适配程度 | 判断 |
|---|---:|---|
| 1M context | B+ | Constitution、RLM、subagent handle、compaction 等支撑，但需继续读 context layout |
| DeepSeek cache hit/miss | A | 明确围绕 DeepSeek prefix caching，README 甚至量化约 100× cold/read 差异 |
| Flash/Pro/Thinking/Max | A | auto mode 明确选择 flash/pro + off/high/max |
| V4 DSML encoding | 未确认 | 需读 client.rs / models.rs |
| Tool runtime | A | typed registry、hooks、approval、LSP diagnostics |
| Permission/sandbox | A- | Plan/Agent/YOLO + macOS Seatbelt |
| Checkpoint/restore | A | side-git snapshot + checkpoint + restore |
| Subagents | A | concurrent subagents + transcript handle |
| Cost telemetry | A- | README 写 live cost tracking with cache hit/miss breakdown |
| LSP diagnostics | A | post-edit diagnostics 注入模型上下文 |
| RLM sessions | A- | recursive language model sessions / handle-based context |

---

## 6. 对 DeepSeek Agent 的迁移判断

### 必须借鉴

```text
Constitution / authority hierarchy
Flash routing call with thinking off
Auto model + thinking mode route
side-git snapshots
subagent summary + transcript handle
LSP diagnostics before next request
live cost tracking with cache hit/miss
Plan / Agent / YOLO 三模式
Runtime API + task manager
```

### 需要继续读源码确认

```text
client.rs 如何调用 DeepSeek beta endpoint
models.rs 如何表示 reasoning blocks
pricing.rs 如何解析 cache hit/miss
turn_loop.rs 如何执行 auto route
capacity_flow.rs 如何做 guardrails
compaction.rs / purge.rs 如何管理 context
subagent.rs / rlm.rs 如何保持 bounded handles
```

### DeepSeek Agent 应该超越

```text
把 Constitution 拆成可缓存 stable prefix + 可变 task anchor
把 auto route 扩展为 Flash/Pro/Think/Max + risk/failure/checkpoint route
把 cost tracking 做成产品 UI
把 LSP diagnostics、tool results、checkpoint 合并进 V4 layout
```

---

## 7. 初步结论

CodeWhale 是三者中最接近我们目标的 V4-native coding harness。它已经明确围绕：

```text
DeepSeek V4
prefix caching
Flash/Pro auto route
thinking level route
Constitution authority hierarchy
side-git checkpoint
subagents
LSP diagnostics
cache hit/miss cost tracking
```

做了深度适配。

下一轮必须继续读 Rust 核心：

```text
crates/tui/src/core/engine/turn_loop.rs
crates/tui/src/client.rs
crates/tui/src/models.rs
crates/tui/src/pricing.rs
crates/tui/src/compaction.rs
crates/tui/src/tools/subagent.rs
crates/tui/src/tools/rlm.rs
crates/agent/*
crates/core/*
crates/execpolicy/*
crates/state/*
```
