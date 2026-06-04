# 4-C Codex 源码深读报告 Codex Source Audit

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v0.8  
> 状态：源码深读 Pass 1 完成。  
> 已读：README、AGENTS.md、config.schema.json。  
> 未完成：core/model/tools/sandbox/app-server 全量逐文件审计。

---

## 1. 仓库结构扫描

官方仓库 README 明确：

```text
Codex CLI is a coding agent from OpenAI that runs locally on your computer.
```

并区分 IDE、Desktop App、Codex Web。证据：https://github.com/openai/codex/blob/main/README.md。

已读文件：

| 文件 | 证据 | 作用 |
|---|---|---|
| `README.md` | https://github.com/openai/codex/blob/main/README.md | 产品入口、安装、CLI / IDE / App / Web 区分 |
| `AGENTS.md` | https://github.com/openai/codex/blob/main/AGENTS.md | 官方仓库对 agent 修改代码时的内部规则，包含 model-visible context 规则 |
| `codex-rs/core/config.schema.json` | https://github.com/openai/codex/blob/main/codex-rs/core/config.schema.json | 暴露 config 结构：agents、apps、approvals、auto compact、features 等 |

---

## 2. 关键模块清单

根据已读文件和官方结构，当前确认 Codex 至少有以下模块：

| 模块 | 证据 | 说明 |
|---|---|---|
| Rust core | AGENTS.md 说明 `codex-rs/core` crate 名为 `codex-core` | 核心 crate |
| TUI | AGENTS.md 多处提到 `codex-rs/tui` 与 snapshot tests | 终端 UI |
| Context | AGENTS.md 明确 `core/context` 与 `ContextualUserFragment` | model-visible context 注入 |
| Config | config.schema.json | 配置 schema |
| Apps / connectors | config.schema.json `AppConfig` | app/tool approval |
| Approvals | config.schema.json `ApprovalsReviewer` / `AskForApproval` | 权限审批 |
| Auto compact | config.schema.json `AutoCompactTokenLimitScope` | compaction token 计数策略 |
| Skills/Subagents/Agents | config.schema.json `AgentsToml` | 子 agent 配置 |
| MCP | AGENTS.md 提到 `codex-rs/codex-mcp` | MCP 连接管理 |

---

## 3. 逐文件阅读摘录

### 3.1 README.md

关键事实：

```text
Codex CLI 本地运行；
IDE 入口；
Desktop App 入口；
Codex Web / cloud-based agent 入口。
```

### 3.2 AGENTS.md

最关键的源码治理规则是 “Model visible context”：

```text
Codex maintains a context (history of messages) that is sent to the model in inference requests.
1. No history rewrite
2. Avoid frequent changes to context that cause cache misses
3. No unbounded items
4. No items larger than 10K tokens
5. >1k tokens 新项需要 P0 review
6. All injected fragments must be defined as structs in core/context and implement ContextualUserFragment trait
```

这是目前三个竞品中最接近 DeepSeek V4 ContextLayoutManager 的源码级证据。

### 3.3 config.schema.json

已读到以下关键配置结构：

```text
AgentsToml
AgentRoleToml
AppConfig
AppToolApproval
ApprovalsReviewer
AskForApproval
AutoCompactTokenLimitScope
ConfigProfile
features
```

重点字段：

```text
AgentsToml:
  max_threads
  max_depth
  job_max_runtime_seconds
  interrupt_message

AppConfig:
  default_tools_approval_mode
  destructive_enabled
  open_world_enabled
  tools

ApprovalsReviewer:
  user
  auto_review
  guardian_subagent

AskForApproval:
  untrusted
  on-failure
  on-request
  granular
  never

AutoCompactTokenLimitScope:
  total
  body_after_prefix
```

这些说明 Codex 的 Harness 不是普通 CLI，而是有 agent role / thread、tool approval、destructive/open-world capability flags、auto review guardian、auto compact token scope、feature flags。

---

## 4. 函数 / 类 / 配置摘录

### 4.1 `ContextualUserFragment`

`AGENTS.md` 明确要求所有 injected fragments 必须定义在 `core/context` 并实现 `ContextualUserFragment` trait。

迁移判断：高度可借鉴。DeepSeek Agent 应设计类似：

```text
ContextFragment:
  cache_zone
  token_cap
  render
  stability_class
```

### 4.2 `AskForApproval`

`config.schema.json` 中 `AskForApproval` 提供 `untrusted`、`on-failure`、`on-request`、`granular`、`never` 等模式。

迁移判断：可借鉴。

### 4.3 `ApprovalsReviewer`

`ApprovalsReviewer` 支持 `user`、`auto_review`、`guardian_subagent`。

迁移判断：强烈借鉴。DeepSeek Agent 可以把 `auto_review` 改造为 Pro reviewer / policy guardian subagent。

### 4.4 `AutoCompactTokenLimitScope`

支持 `total` 与 `body_after_prefix`。

迁移判断：非常重要。DeepSeek Agent 可设计 stable_prefix 不计入 compact body，active body 超限触发 checkpoint，compressed_history 独立预算。

---

## 5. Model-Harness Fit Matrix

| DeepSeek V4 特性 | Codex 当前源码/Harness 适配 | 评分 |
|---|---|---:|
| 1M context | 有 context window / auto compact / hard cap 思想，但非 V4-specific | B |
| CSA/HCA sparse layout | 未见 | C |
| cache hit/miss | 有 avoid cache misses 规则，但无 DeepSeek usage telemetry | B- |
| Flash/Pro/Thinking/Max | 有 model/reasoning/approval/reviewer 抽象雏形，但非 DeepSeek route | B- |
| V4 DSML encoding | 未见 | D |
| reasoning_content policy | 有 reasoning / auto compact 相关配置线索，但非 V4 四态 | C+ |
| checkpoint-driven review | 有 app/review/approvals 线索，但需继续读 app-server | B- |
| typed context fragments | 强 | A |
| permission profiles | 强 | A |
| app / connector approval | 强 | A- |

---

## 6. 对 DeepSeek Agent 的迁移判断

### 可直接借鉴

```text
Model visible context rules
ContextualUserFragment 思想
hard token cap
avoid cache misses
no history rewrite
AutoCompactTokenLimitScope
ApprovalsReviewer
AskForApproval
AppConfig tool approval model
```

### 需要 DeepSeek V4-native 重写

```text
DeepSeekV4MessageCompiler
DSMLToolParser
Flash/Pro/Thinking/Max Router
DeepSeek cache hit/miss telemetry
CSA/HCA-aware context layout
ReasoningContentPolicy
```

### 需继续读源码

```text
core/session
core/context
model provider
tool execution
sandbox enforcement
app-server
MCP runtime
```

---

## 7. 审计结论

Codex 的源码级价值已经明显高于普通 Agent：它在代码治理层面明确把 model-visible context 当成核心工程对象，并把 cache misses、hard caps、typed fragments、approval reviewer、auto compact 都写进了规则/配置。

但它仍不是 DeepSeek V4-native。DeepSeek Agent 应吸收其 context engineering 和 approval/sandbox 设计，然后重写 DeepSeek 专属的 Context Layout、Routing、Encoding、Telemetry。
