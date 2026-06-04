# 4-0 Codex 证据索引 Codex Evidence Index

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

> 阶段：Stage 2B  
> 版本：v0.4  
> 证据标准：OpenAI 官方 GitHub / 官方 Developers Docs 优先。  
> 重要边界：`openai/codex` 是官方开源仓库，主要覆盖 Codex CLI / Rust codebase / SDK / app-server 等；Codex App 的完整产品 UI/客户端实现未必全部在该仓库中公开，App 能力以官方 Docs 为主证据。

---

## 1. 官方源码与文档入口

| 类型 | 来源 | 用途 |
|---|---|---|
| 官方 GitHub | [openai/codex](https://github.com/openai/codex) | CLI / Rust 源码 / repo 结构 / AGENTS.md |
| README | [README.md](https://github.com/openai/codex/blob/main/README.md) | 说明 CLI、IDE、App、Web 三种入口 |
| AGENTS.md | [AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md) | 官方仓库内部给 Codex 的代码贡献规则、模型可见上下文规则 |
| Codex Docs | [Codex Overview](https://developers.openai.com/codex) | 产品总览 |
| CLI Docs | [Codex CLI](https://developers.openai.com/codex/cli) | CLI 本地 Agent |
| App Docs | [Codex App](https://developers.openai.com/codex/app) | 桌面客户端 / command center |
| Web Docs | [Codex Web](https://developers.openai.com/codex/cloud) | 云端 background/parallel tasks |
| Permissions | [Permissions](https://developers.openai.com/codex/permissions) | sandbox / approval / filesystem / network |
| Config Reference | [Config Reference](https://developers.openai.com/codex/config-reference) | custom provider、context window、auto compact 等 |
| MCP | [MCP](https://developers.openai.com/codex/mcp) | 外部工具与上下文 |
| Skills | [Skills](https://developers.openai.com/codex/skills) | reusable workflow |
| Subagents | [Subagents](https://developers.openai.com/codex/subagents) | parallel specialized agents |

---

## 2. 关键事实索引

### 2.1 产品入口

- Codex CLI 是 OpenAI 的本地 terminal coding agent，可以读取、修改、运行本机选定目录中的代码；官方文档还说明它是 open source、Rust 实现。来源：[Codex CLI docs](https://developers.openai.com/codex/cli)。
- `openai/codex` README 明确区分：CLI、IDE、Desktop App、Codex Web/Cloud。来源：[README](https://github.com/openai/codex/blob/main/README.md)。
- Codex App 是 focused desktop experience / command center，支持 parallel threads、worktrees、automations、Git functionality。来源：[Codex App docs](https://developers.openai.com/codex/app)。
- Codex Web / Cloud 可在自己的云环境中 background/parallel 处理任务。来源：[Codex Web docs](https://developers.openai.com/codex/cloud)。

### 2.2 源码结构

- GitHub 页面显示仓库包含 `codex-cli`、`codex-rs`、`docs`、`sdk` 等目录，语言以 Rust 为主。来源：[openai/codex repo](https://github.com/openai/codex)。
- `package.json` 显示仓库是 `codex-monorepo`，并有脚本写 hooks schema。来源：[package.json](https://github.com/openai/codex/blob/main/package.json)。
- `AGENTS.md` 明确 Rust crate 命名、测试、代码组织、model visible context 等规则。来源：[AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)。

### 2.3 上下文工程

- `AGENTS.md` 中“Model visible context”要求：context 必须增量构建、避免频繁修改造成 cache misses、所有注入项必须有硬上限、不得有超过 10K tokens 的项、超过 1K tokens 的新项要 P0 review、所有 injected fragments 要定义为 `core/context` 的 structs 并实现 `ContextualUserFragment`。来源：[AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)。
- Config Reference 暴露 `model_context_window`、`model_auto_compact_token_limit`、`model_instructions_file` 等配置。来源：[Config Reference](https://developers.openai.com/codex/config-reference)。

### 2.4 权限 / 沙箱

- Codex 有 permission profiles：`:read-only`、`:workspace`、`:danger-full-access`。来源：[Permissions profiles](https://developers.openai.com/codex/permissions)。
- Codex 的 network permissions 支持 enabled、domain allow/deny、Unix socket rules、local/private network guard。来源：[Permissions network](https://developers.openai.com/codex/permissions)。
- Enforcement：macOS 用 Seatbelt，Linux/WSL 用 bubblewrap/seccomp/Landlock，Windows 有 native sandbox/elevated sandboxing。来源：[Permissions enforcement](https://developers.openai.com/codex/permissions)。

### 2.5 App / Client

- Codex App 支持 Local / Worktree / Cloud thread mode。来源：[Codex App features](https://developers.openai.com/codex/app/features)。
- App review pane 显示 git diff、支持 inline comments、stage/revert、PR feedback loop。来源：[Review pane](https://developers.openai.com/codex/app/review)。
- App task sidebar 可展示 agent plan、sources、generated artifacts、task summary，便于用户 steer 和 inspect。来源：[Task sidebar](https://developers.openai.com/codex/app/features)。

---

## 3. 本轮调研边界

本轮先完成官方层面的第一轮深度调研：

```text
4-1 Codex 产品形态调研
4-2 Codex 官方源码与CLI架构调研
4-3 Codex App / Cloud / Review / Sandbox 调研
4-4 Codex 对 DeepSeek Agent 的启发
```

后续如果要做更细源码阅读，应继续深入：

```text
codex-rs/core
codex-rs/tui
codex-rs/app-server
codex-rs/codex-mcp
sdk
```
