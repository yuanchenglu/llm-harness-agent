# 4-2 Codex 官方源码与 CLI 架构调研 Codex Official Source and CLI Architecture

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

## 1. 目标

回答：`openai/codex` 官方开源仓库暴露了哪些架构事实？CLI 与核心 runtime 大致如何组织？

---

## 2. 官方仓库事实

GitHub 页面显示 `openai/codex` 是 Public 仓库，描述为 lightweight coding agent that runs in your terminal，并包含：

```text
.codex
.devcontainer
.github
.vscode
codex-cli
codex-rs
docs
patches
scripts
sdk
third_party
tools
AGENTS.md
```

来源：[openai/codex repo](https://github.com/openai/codex)。

README 说明 Codex CLI 可以通过 install script、npm、Homebrew、release binary 安装，并支持 ChatGPT plan 或 API key。来源：[README Quickstart](https://github.com/openai/codex/blob/main/README.md)。

---

## 3. Rust-first 结构

官方 CLI 文档说明 Codex CLI 是 open source，并 built in Rust for speed and efficiency。来源：[Codex CLI docs](https://developers.openai.com/codex/cli)。

AGENTS.md 明确 `codex-rs` 下 crate 命名以 `codex-` 为前缀，例如 `core` crate 是 `codex-core`。来源：[AGENTS.md](https://github.com/openai/codex/blob/main/AGENTS.md)。

### 推论

Codex CLI 的核心架构大概率是：

```text
codex-rs/core：Agent core / context / model client / protocol
codex-rs/tui：terminal UI
codex-rs/codex-mcp：MCP 连接
codex-rs/app-server：App / 外部客户端协议
sdk：外部编程接口
```

注意：这是基于仓库结构与 AGENTS.md 的工程推论，后续需要继续逐文件读源码验证。

---

## 4. Model visible context 规则

AGENTS.md 的 “Model visible context” 是本轮最关键的源码级证据之一。它要求：

```text
1. No history rewrite：context 必须增量构建
2. Avoid frequent changes：避免频繁变化导致 cache misses
3. No unbounded items：所有注入项必须有边界和 hard cap
4. No items larger than 10K tokens
5. 可能超过 1K tokens 的新项需要 P0 review
6. 所有 injected fragments 必须定义为 core/context structs 并实现 ContextualUserFragment
```

来源：[AGENTS.md model visible context](https://github.com/openai/codex/blob/main/AGENTS.md)。

### 对 DeepSeek Agent 的启发

这与我们 DeepSeek V4 的结论高度一致：

```text
禁止 history rewrite
稳定 prefix
bounded context fragments
large fragment review
typed context injection
```

DeepSeek Agent 应该把它升级为：

```text
ContextFragment trait
CacheZone enum
TokenBudget cap
PrefixDriftDetector
ContextLayoutManager
```

---

## 5. Custom provider 与模型配置

Codex Config Reference 说明：

```text
model_provider：provider id，默认 openai
model_providers.<id>：custom provider definition
model_context_window：active model context window
model_auto_compact_token_limit：history compaction threshold
model_instructions_file：替代 AGENTS.md 的 instructions file
```

来源：[Config Reference model_provider / context window](https://developers.openai.com/codex/config-reference)。

### 结论

Codex CLI 是可以支持 custom provider 的，这意味着“接 DeepSeek V4”在技术上可能有入口。  
但 custom provider 只解决“能调用模型”，不等于能发挥 DeepSeek V4 的 cache、V4 encoding、Flash/Pro routing、DSML tool calling 等专属能力。

---

## 6. MCP 与外部工具

Codex MCP 文档说明 MCP 用于给 Codex 接入第三方工具与上下文，CLI 和 IDE extension 都支持 MCP servers，并共享配置。来源：[Codex MCP](https://developers.openai.com/codex/mcp)。

MCP 支持 STDIO servers、Streamable HTTP servers、server instructions、OAuth、tool approval mode、插件提供的 MCP servers。来源：[MCP supported features](https://developers.openai.com/codex/mcp)。

---

## 7. 源码层可借鉴点

```text
Rust-first local runtime
typed model-visible context
incremental context construction
custom provider framework
permission profiles
MCP config/runtime
TUI snapshot tests
integration tests around agent logic
app-server protocol
```

## 8. 源码层待继续深入

下一轮若要深挖 Codex 源码，应读：

```text
codex-rs/core/context
codex-rs/core/config
codex-rs/core/model client
codex-rs/tui
codex-rs/app-server
codex-rs/codex-mcp
sdk
```
