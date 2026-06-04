# 8-0 Hermes Agent 源码审计 Pass 1 Hermes Agent Source Audit Pass 1

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.0  
> 仓库：`NousResearch/hermes-agent`  
> 状态：仓库结构、README、run_agent.py、model_tools.py、trajectory_compressor.py Pass 1 完成；后续需要继续读 agent/*、tools/*、gateway/*、cron/*、skills/*、providers/*。

---

## 1. 仓库定位

Hermes Agent README 明确定位为：

```text
The self-improving AI agent built by Nous Research.
The only agent with a built-in learning loop.
It creates skills from experience, improves them during use,
nudges itself to persist knowledge, searches its own past conversations,
and builds a deepening model of who you are across sessions.
```

它同时强调：

```text
Use any model you want
Telegram / Discord / Slack / WhatsApp / Signal / CLI from a single gateway process
Agent-curated memory
Autonomous skill creation
Skills self-improve during use
FTS5 session search
Scheduled automations
Subagents
Six terminal backends: local, Docker, SSH, Singularity, Modal, Daytona
Batch trajectory generation and trajectory compression
```

---

## 2. 仓库结构扫描

根目录关键结构：

```text
agent/
apps/
cron/
gateway/
hermes_cli/
providers/
skills/
tools/
web/
trajectory_compressor.py
model_tools.py
run_agent.py
hermes_state.py
mcp_serve.py
toolsets.py
```

这说明 Hermes 是一个完整个人 Agent 栈，而不是单纯 coding agent。

---

## 3. run_agent.py 关键源码事实

`run_agent.py` 文件头部说明它是：

```text
AI Agent Runner with Tool Calling
handles conversation loop, tool execution, response management
supports automatic tool calling loop until completion
supports multiple model providers
```

`AIAgent.__init__` 参数极多，包含：

```text
base_url
provider
api_mode
model
max_iterations
enabled_toolsets / disabled_toolsets
save_trajectories
session_id
tool callbacks
thinking_callback / reasoning_callback
stream_delta_callback
max_tokens
reasoning_config
prefill_messages
platform / user_id / chat_id / gateway_session_key
skip_memory
session_db
fallback_model
credential_pool
checkpoints_enabled
```

这说明 Hermes 的 runtime 是长期多入口、多平台、多 provider 的 Agent Loop。

---

## 4. model_tools.py 关键源码事实

`model_tools.py` 说明自己是：

```text
Thin orchestration layer over the tool registry.
Each tool file in tools/ self-registers its schema, handler, and metadata via tools.registry.register().
```

它导出：

```text
get_tool_definitions
handle_function_call
TOOL_TO_TOOLSET_MAP
TOOLSET_REQUIREMENTS
get_all_tool_names
get_toolset_for_tool
get_available_toolsets
check_toolset_requirements
```

它还有几个非常关键的工程点：

1. 长生命周期 event loop，避免 `asyncio.run()` 每次创建/关闭导致 cached httpx / AsyncOpenAI clients 绑定到 dead loop。
2. `quiet_mode` 下缓存 tool definitions，cache key 包含 registry generation 和 config mtime。
3. 会根据实际可用工具重写 execute_code / discord / browser schemas，防止模型看到不存在工具。
4. 支持 tool search progressive disclosure：当 MCP/plugin 工具太多时，用 `tool_search / tool_describe / tool_call` 折叠非核心工具。
5. 对 tool error 做清洗，去掉结构化 framing tokens，限制长度，防 prompt injection / role confusion。
6. 对 tool args 做类型 coercion，解决开源模型把数字/布尔/数组参数输出成字符串的问题。

---

## 5. Trajectory / Compression

仓库 README 明确说 Hermes 支持：

```text
Batch trajectory generation
Trajectory compression for training next generation tool-calling models
```

`trajectory_compressor.py` 是专门的轨迹压缩模块。它说明 Hermes 不只是跑 Agent，而是把 Agent 轨迹作为训练/自进化资产。

---

## 6. Model-Harness Fit Matrix

| DeepSeek V4 特性 | Hermes 适配程度 | 判断 |
|---|---:|---|
| 1M context | B | 有 session search、memory、trajectory compression，但不是 V4 layout |
| DeepSeek cache hit/miss | C+ | tool schema caching强，但未发现 DeepSeek hit/miss 原生适配 |
| Flash/Pro/Think/Max | C+ | 多 provider / model switch 有，DeepSeek route 需自研 |
| V4 DSML encoding | D | 无证据显示支持 V4 DSML |
| Tool runtime | A | tool registry / dynamic schema / progressive disclosure 很强 |
| Memory / skills | A | 自进化 skill / memory 是核心卖点 |
| Gateway / multi-platform | A | Telegram/Discord/Slack/WhatsApp/Signal/CLI 单 gateway |
| Cron / automation | A | scheduled automations 是核心能力 |
| Trajectory | A | trajectory generation/compression 是核心资产 |
| Security risk | 高 | always-on gateway + memory + cron + shell 合并同一 authority boundary，需 provenance gates |

---

## 7. 对 DeepSeek Agent 的迁移判断

### 可直接借鉴

```text
tool registry 自注册
tool schema 缓存
dynamic schema rewriting
tool_search progressive disclosure
tool error sanitization
tool argument coercion
trajectory compression
memory / skill self-evolution
gateway architecture
cron / scheduled automation
multi-terminal backend abstraction
```

### 不应直接照搬

```text
always-on single authority boundary
跨消息平台 + memory + cron + shell 混合权限
无 DeepSeek-specific cache telemetry
无 V4-specific context layout
无 Flash/Pro route
```

### DeepSeek Agent 应增强

```text
Provenance gate
Owner attestation for scheduled jobs
Memory/skill provenance
Cron action digest
Tool permission isolation
DeepSeek cache hit/miss aware tool schema protocol
```

---

## 8. 初步结论

Hermes 的价值不是 Code Agent，而是 **个人通用 Agent 操作系统**：

```text
Memory
Skills
Gateway
Cron
Tool Registry
Trajectory Compression
Multi-platform continuity
```

它对 DeepSeek Agent 的 Agent Mode 很重要，但其安全边界复杂。DeepSeek Agent 若吸收 Hermes，必须把 memory、skill、cron、gateway 与 shell/tool 权限隔离，否则会出现持久化 prompt injection 和 sleeper-channel 风险。

下一轮继续读：

```text
agent/*
tools/registry.py
tools/tool_search.py
tools/cron*
gateway/*
cron/*
skills/*
providers/*
hermes_state.py
```
