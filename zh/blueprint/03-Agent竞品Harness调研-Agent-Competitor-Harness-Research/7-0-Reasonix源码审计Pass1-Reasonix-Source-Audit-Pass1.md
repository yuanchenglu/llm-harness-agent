# 7-0 Reasonix 源码审计 Pass 1 Reasonix Source Audit Pass 1

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.0  
> 仓库：`esengine/DeepSeek-Reasonix`  
> 分支：`main-v2`  
> 状态：源码结构扫描 + 关键模块 Pass 1 完成；后续仍需继续读 `internal/agent/*.go`、`internal/provider/openai/*`、`internal/tool/*` 的具体函数实现。

---

## 1. 仓库定位

Reasonix 是一个 DeepSeek-native terminal coding agent。仓库 README 明确写到：

```text
A DeepSeek-native AI coding agent for your terminal.
A config- and plugin-driven harness — a single static Go binary,
tuned around DeepSeek's prefix cache so token costs stay low across long sessions.
```

官方仓库页面显示分支 `main-v2` 是当前默认开发分支，Reasonix 1.0 是 Go ground-up rewrite，早期 TypeScript 0.x 只在 v1 分支维护。

证据：

- `README.md`：DeepSeek-native、Go rewrite、prefix cache、config/plugin harness
- 仓库目录：`cmd/`、`desktop/`、`internal/`、`docs/`、`.reasonix/commands`
- `internal/` 下有 `agent`、`provider`、`tool`、`permission`、`sandbox`、`skill`、`plugin`、`memory`、`checkpoint`、`lsp` 等模块

---

## 2. 仓库结构扫描

根目录关键结构：

```text
cmd/
desktop/
docs/
internal/
npm/
site/
reasonix.example.toml
go.mod
```

`internal/` 目录关键模块：

```text
agent
checkpoint
cli
codegraph
command
config
control
diff
event
evidence
hook
instruction
jobs
lsp
memory
permission
plugin
provider
sandbox
skill
tool
```

`internal/agent` 目录包含：

```text
agent.go
ask.go
branch.go
cachehit_e2e_test.go
compact.go
coordinator.go
loop_e2e_test.go
planmode_test.go
postllmcall_flow_test.go
session.go
task.go
```

`internal/provider` 目录包含：

```text
anthropic/
openai/
provider.go
retry.go
schema_canonicalize.go
pairing_probe_test.go
```

---

## 3. 关键源码级事实

### 3.1 DeepSeek-native 配置

README 的配置示例直接把默认模型设置为：

```toml
default_model = "deepseek-flash"

[[providers]]
name        = "deepseek-flash"
kind        = "openai"
base_url    = "https://api.deepseek.com"
model       = "deepseek-v4-flash"
api_key_env = "DEEPSEEK_API_KEY"
```

并提到 preset 包括 `deepseek-pro`、`mimo-pro`、`mimo-flash`。

### 3.2 两模型协作

README 明确支持 executor + planner 两模型协作：

```toml
[agent]
planner_model = "deepseek-pro"
```

并写到这两个模型运行在 separate, cache-stable sessions。

这点非常重要：Reasonix 已经把 DeepSeek V4 的 Flash/Pro 分工产品化为：

```text
executor = DeepSeek Flash
planner = DeepSeek Pro
```

### 3.3 Auto Plan

README 写到：

```toml
auto_plan = "ask"
auto_plan_classifier = "deepseek-flash"
```

并说明复杂任务先进入 read-only plan mode，用户批准后才编辑或运行 side-effecting commands。

这对应我们 DeepSeek Agent 里的：

```text
Plan Mode
Pro/Flash Router
Permission-gated execution
```

### 3.4 Permission + Sandbox

README 明确区分：

```text
Permissions are policy.
The sandbox is enforcement.
```

权限规则顺序：

```text
deny > ask > allow > fallback
```

file-writer 工具被限制在 workspace_root，解析 symlink 和 `..` 防止逃逸；macOS 下 bash 默认使用 Seatbelt jail。

### 3.5 MCP / Plugin

Reasonix 是 MCP client，`[[plugins]]` 可配置 stdio 或 http transport；MCP tools 暴露为 `mcp__<server>__<tool>`，prompts 暴露为 slash commands，resources 用 `@<server>:<uri>` 注入。

### 3.6 Slash Commands / @ References

内置命令：

```text
/compact
/new
/rewind
/tree
/branch
/switch
/todo
/model
/effort
/mcp
/memory
/help
```

Custom commands 是 `.reasonix/commands/*.md`，`@path` 注入文件或目录，`@server:uri` 注入 MCP resource。

---

## 4. Model-Harness Fit Matrix

| DeepSeek V4 物理特性 | Reasonix 适配程度 | 判断 |
|---|---:|---|
| 1M context | B+ | 有 long session / compact / @reference / branch / memory，但需继续看具体 context builder |
| DeepSeek cache hit/miss | A- | 明确以 DeepSeek prefix cache 为核心产品卖点；有 cachehit e2e 测试 |
| Flash / Pro 路由 | A- | executor + planner、subagent_model、auto_plan_classifier 已有 |
| Thinking / Max | B | 有 `/effort`、auto plan，但需看 provider 参数映射 |
| V4 DSML encoding | 未确认 | 当前看起来走 OpenAI-compatible tool calling，需读 provider/openai |
| Tool runtime | A | built-ins + MCP plugin + permission + sandbox |
| Permission / sandbox | A | policy/enforcement 明确分离 |
| Checkpoint / rewind | A- | `/rewind`、`/branch`、checkpoint 模块存在 |
| Memory / skills | B+ | memory / skill 模块存在，需继续读实现 |
| Cost telemetry | B+ | README 强调 token costs/cache，需读 billing/usage |

---

## 5. 对 DeepSeek Agent 的迁移判断

### 可直接借鉴

```text
DeepSeek Flash executor + Pro planner
cache-stable separate sessions
auto_plan_classifier = cheap Flash
permission policy 与 sandbox enforcement 分离
MCP plugin + stdio/http transport
slash command system
@file / @resource 注入
branch / rewind / session tree
config-driven provider/tool/skill/plugin
```

### 需要进一步验证

```text
是否真正解析 DeepSeek prompt_cache_hit_tokens / miss_tokens
provider/openai 是否有 DeepSeek V4-specific 参数
/effort 是否映射 thinking/high/max
compact.go 如何压缩上下文
cachehit_e2e_test 覆盖了哪些 cache-stability 场景
```

### 需要 DeepSeek Agent 自研或增强

```text
V4 DSML compiler
V4 CSA/HCA-aware context layout
Flash/Pro/Think/Max router 的细粒度策略
DeepSeek cache telemetry UI
Checkpoint-driven Pro review
```

---

## 6. 初步结论

Reasonix 是目前最接近 DeepSeek-native Harness 的开源项目。它不是通用多模型 Agent，而是已经把 DeepSeek 的 prefix cache、Flash/Pro、planner/executor、cache-stable sessions、permissions/sandbox、MCP plugins 作为核心架构点。

下一轮必须继续深读：

```text
internal/agent/agent.go
internal/agent/compact.go
internal/agent/cachehit_e2e_test.go
internal/provider/openai/*
internal/provider/schema_canonicalize.go
internal/billing/*
internal/checkpoint/*
internal/permission/*
internal/sandbox/*
internal/tool/*
```
