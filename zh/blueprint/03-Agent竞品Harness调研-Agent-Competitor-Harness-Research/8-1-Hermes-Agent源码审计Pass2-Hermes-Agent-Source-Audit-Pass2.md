# 8-1 Hermes Agent 源码审计 Pass 2 Hermes Agent Source Audit Pass 2

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.1  
> 仓库：`NousResearch/hermes-agent`  
> 状态：历史 Pass 2；核心 Agent OS 机制已完成源码定位，设计动机、质量收益与安全性仍需实验验证。
> 已读核心：README、run_agent.py、model_tools.py、tools/registry.py、tools/tool_search.py、trajectory_compressor.py。

---

## 1. 本轮新增读取文件

| 文件 | 作用 |
|---|---|
| `run_agent.py` | AIAgent 主运行器、多 provider、多平台、callbacks、reasoning、checkpoints、credential pool |
| `model_tools.py` | 工具定义装配、tool registry orchestration、async bridge、schema caching |
| `tools/registry.py` | tool self-registration、toolset、availability checks、dynamic schema、dispatch |
| `tools/tool_search.py` | progressive tool disclosure、BM25 tool search、bridge tools |
| `trajectory_compressor.py` | 轨迹压缩、训练数据保真、protected head/tail、middle summary |

---

## 2. Hermes 如何把模型能力产品化

### 2.1 Agent OS：模型能力 → 多入口长期运行器

`run_agent.py` 的文件说明：它处理 conversation loop、tool execution、response management，支持 automatic tool calling loop、multiple model providers、error recovery、message history management。

`AIAgent.__init__` 参数极多，覆盖：

```text
provider/base_url/api_mode/model
max_iterations
toolsets
trajectory saving
callbacks
thinking_callback / reasoning_callback / stream_delta_callback
max_tokens / reasoning_config
gateway platform/user/chat/session
fallback_model
credential_pool
checkpoints_enabled
```

这说明 Hermes 不是单任务 coding agent，而是一个长期多入口 Agent OS。

### 2.2 Tool Registry：模型工具能力 → 自注册工具系统

`tools/registry.py` 明确：

```text
Each tool file calls registry.register() at module level
schema, handler, toolset membership, availability check
model_tools.py queries registry
```

`ToolEntry` 包含：

```text
name
toolset
schema
handler
check_fn
requires_env
is_async
description
emoji
max_result_size_chars
dynamic_schema_overrides
```

这比普通工具列表强很多，因为它支持：

```text
toolset
availability
dynamic schema
generation counter
thread-safe mutation
MCP refresh
plugin override protection
```

### 2.3 Tool schema caching：模型上下文成本 → tool defs cache

`model_tools.py` 对 `get_tool_definitions` 做 memoization，cache key 包含：

```text
enabled_toolsets
disabled_toolsets
registry._generation
config mtime / size
HERMES_KANBAN_TASK
skip_tool_search_assembly
```

这说明 Hermes 对“工具 schema 很大且会进入模型上下文”的成本非常敏感。

虽然这不是 DeepSeek-specific cache hit/miss，但思想可迁移。

### 2.4 Progressive Tool Disclosure：大工具集 → tool_search/tool_describe/tool_call

`tools/tool_search.py` 说明当 MCP 和 non-core plugin tools 太多时，用三个 bridge tools 替换：

```text
tool_search
tool_describe
tool_call
```

核心约束：

```text
core tools never defer
threshold gate every assembly
catalog stateless across turns
bridge tools route through normal handle_function_call
display and trajectory unwrap underlying tool
```

这对 DeepSeek Agent 非常重要，因为 DeepSeek cache-first Harness 不可能每轮都把几百个 MCP tools 全量塞进 prefix。

### 2.5 Tool error sanitation：工具结果 → 防 prompt injection / role confusion

`model_tools.py` 中有大量工具错误清洗、tool args coercion、schema rewrite、防 duplicate tool names 的逻辑。  
这说明 Hermes 在工具层做了大量“模型鲁棒性工程”。

### 2.6 Trajectory Compression：运行轨迹 → 训练/自进化资产

`trajectory_compressor.py` 的策略：

```text
Protect first turns
Protect last N turns
Compress middle turns only
Replace compressed region with one human summary message
Keep remaining tool calls intact
Preserve training signal quality
```

这不是普通日志压缩，而是为了让轨迹能成为训练下一代 tool-calling model 的数据。

---

## 3. Hermes Model-Harness Fit Matrix 终版

| DeepSeek V4 特性 | Hermes 适配程度 | 源码证据级别 | 迁移判断 |
|---|---:|---|---|
| 1M context | B | trajectory compressor / tool search / memory | 借鉴但需 V4 layout |
| cache hit/miss | C+ | tool schema caching | 需 DeepSeek-native telemetry |
| Flash/Pro/Think/Max | C+ | provider/fallback/reasoning_config | 需自研 router |
| V4 DSML | D | 未见 | 自研 |
| tool registry | A | registry.py | 强借鉴 |
| dynamic schema | A | registry.py / model_tools.py | 强借鉴 |
| progressive tool disclosure | A | tool_search.py | 强借鉴 |
| memory/skills | A- | README / run_agent | 借鉴，但需 provenance |
| trajectory compression | A | trajectory_compressor.py | 强借鉴 |
| gateway/multi-platform | A | README / run_agent | Agent Mode 借鉴 |
| cron/automation | A- | README / run_agent | 借鉴但需强权限 |
| security/provenance | 风险高 | 代码结构 | 必须增强隔离 |

---

## 4. DeepSeek Agent 应吸收 Hermes 的哪些能力

### 4.1 Tool Registry

```text
tool self-registration
toolset
check_fn availability
dynamic_schema_overrides
generation counter
dispatch
max_result_size
```

### 4.2 Progressive Tool Disclosure

```text
core tools always loaded
MCP/plugin tools deferred
tool_search / tool_describe / tool_call
stateless catalog
threshold based on context window
trajectory unwrap underlying tool
```

### 4.3 Trajectory Compression

```text
protect head
protect tail
compress middle
preserve tool calls
replace with summary
metrics
```

### 4.4 Agent Mode OS

```text
memory
skills
cron
gateway
multi-platform session
credential pool
fallback model
callbacks
```

---

## 5. DeepSeek Agent 必须比 Hermes 更强的地方

Hermes 是强 Agent OS，但安全边界复杂。DeepSeek Agent 要吸收 Hermes，必须加：

```text
Provenance gate
Memory provenance
Skill provenance
Cron job owner attestation
Tool authority isolation
Gateway platform separation
Scheduled action review digest
Persistent instruction quarantine
Cache-first tool schema protocol
```

否则 memory + skill + cron + shell + gateway 放在一起，会产生长期 prompt injection / sleeper-channel 风险。

---

## 6. Hermes 最终评价

Hermes 对 DeepSeek Agent 的价值不是 Code Mode，而是 Agent Mode：

```text
Personal Agent OS
Memory/Skills self-evolution
Tool registry
Progressive tool disclosure
Gateway
Cron
Trajectory compression
```

它不是 DeepSeek V4-native，但它告诉我们：  
如果 DeepSeek Agent 要从 coding agent 变成真正 Agent，就必须有：

```text
长期记忆
可沉淀技能
可调度任务
多入口
工具生态
轨迹资产化
```

但这些能力必须被 DeepSeek 的 cache-first、permission-first、provenance-first Runtime 包起来。
