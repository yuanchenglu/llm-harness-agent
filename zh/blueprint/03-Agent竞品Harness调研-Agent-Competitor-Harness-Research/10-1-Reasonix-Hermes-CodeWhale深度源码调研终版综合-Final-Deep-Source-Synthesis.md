# 10-1 Reasonix / Hermes / CodeWhale 深度源码调研终版综合 Final Deep Source Synthesis

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.1  
> 状态：历史综合；三者已完成核心源码定位，但必须结合 17-2 校准与运行 benchmark 后才能进入最终架构决策。
> 说明：这不是声称每个仓库每一行都读完，而是核心 Harness 路径已读到足够形成架构判断，下一步可进入产品战略与技术架构设计。

---

## 1. 三者最终定位

| 项目 | 最终定位 | 对 DeepSeek Agent 的价值 |
|---|---|---|
| CodeWhale | DeepSeek V4-native coding harness | Code Mode 的最直接参考 |
| Reasonix | Cache-first DeepSeek terminal agent core | 底层 cache discipline / permission / compaction 的最直接参考 |
| Hermes | General-purpose personal Agent OS | Agent Mode、memory、skills、cron、gateway、trajectory 的参考 |

---

## 2. 三者对 DeepSeek V4 物理特性的利用程度

| DeepSeek V4 物理特性 | CodeWhale | Reasonix | Hermes |
|---|---:|---:|---:|
| 1M context | A | B+ | B |
| prefix cache | A | A | C+ |
| cache hit/miss telemetry | A | A- | C |
| Flash/Pro route | A- | A- | C+ |
| thinking/max route | A- | B+ | C+ |
| reasoning_content policy | A- | A- | C+ |
| tool runtime | A | A | A |
| permission/sandbox | A- | A | B |
| compaction | A- | A | B |
| trajectory | B | B | A |
| skills/memory | B | B+ | A |
| gateway/cron | C | C | A |
| V4 DSML | 未确认 | 未确认 | 无 |
| CSA/HCA-aware layout | 未完全解决 | 未完全解决 | 无 |

---

## 3. 最关键的源码级发现

### 3.1 CodeWhale

CodeWhale 已经把 DeepSeek V4 的核心物理特性写进代码：

```text
1M context window
384K max output
reasoning_effort
prompt_cache_hit_tokens / miss_tokens
reasoning_tokens
reasoning_replay_tokens
cache hit/miss pricing
cache savings
prefix fingerprint
prefix drift detector
prefix drift check（完整 three-zone request contract 尚未接入）
auto model/thinking route
LSP diagnostics injection
```

### 3.2 Reasonix

Reasonix 的核心工程哲学是：

```text
prompt append-only until compaction threshold
compaction is a rare cache-reset point
plan mode must not mutate system prompt/tool list
reasoning_content display/archive but not replay
session aggregate cache hit-rate
permission gate at runtime
tool pairing sanitizer
```

### 3.3 Hermes

Hermes 的核心工程哲学是：

```text
Agent is an OS, not a prompt
tools self-register
schema dynamically assembled
tool search delays non-core tools
trajectory is training data
memory/skills/cron/gateway make the agent long-lived
```

---

## 4. DeepSeek Agent 应该形成的最终 Harness 架构

结合三者，DeepSeek Agent 的 Harness 应该是：

```text
Desktop Shell
  ├─ Agent Mode Workspace
  ├─ Code Mode Project
  ├─ Thread / Task / Review / Terminal / Artifacts
  └─ Cost / Cache / Route / Checkpoint UI

Agent Runtime
  ├─ TurnLoop
  ├─ DeepSeekV4MessageCompiler
  ├─ ContextLayoutManager
  ├─ PrefixStabilityManager
  ├─ ModelRouter
  ├─ ToolRuntime
  ├─ PermissionRuntime
  ├─ CheckpointRuntime
  ├─ TrajectoryRuntime
  └─ SkillMemoryRuntime

DeepSeek V4 Native Layer
  ├─ Flash Executor
  ├─ Pro Planner / Reviewer
  ├─ Thinking Effort Policy
  ├─ DSMLToolParser
  ├─ ReasoningContentPolicy
  ├─ CostCacheTelemetry
  └─ PrefixDriftDetector
```

---

## 5. 直接借鉴清单

### 从 CodeWhale 借

```text
DeepSeekV4 model profile
prefix_cache.rs design
pricing.rs design
reasoning_effort in MessageRequest
client usage normalization
turn_loop prefix check before request
LSP diagnostics injection
side-git checkpoint
subagent handle idea
```

### 从 Reasonix 借

```text
cache-first compaction discipline
soft notice / compact / force ratios
fixed recent tail token budget
PlanMode runtime gate
Gate interface
ToolHooks
PostLLMCall
PreCompact
reasoning_content no replay
tool pairing sanitizer
session aggregate cache metrics
```

### 从 Hermes 借

```text
ToolRegistry
toolset
dynamic_schema_overrides
tool_search / tool_describe / tool_call
trajectory_compressor
memory/skills self-evolution
gateway
cron
credential pool
callbacks
```

---

## 6. DeepSeek Agent 必须自研的核心创新

三者都没完全解决的部分，正是我们的产品创新空间：

```text
1. DeepSeekV4MessageCompiler：原生 V4 encoding / DSML / reasoning policy
2. CSA/HCA-aware Context Layout：不是简单 1M 堆上下文
3. Flash / Pro / Thinking / Max Router：按任务风险、失败、checkpoint、cache 状态路由
4. Checkpoint-driven Pro Review：Flash 执行，Pro 审查
5. Prefix-stable Skill/Tool Protocol：tool schema / skill index cache-first
6. ReasoningContentPolicy 四态：display / archive / summarize / no replay
7. CostCacheTelemetry 产品 UI：cache hit/miss、savings、drift、route reason
8. Provenance-first Memory/Skill/Cron：防持久化 prompt injection
9. Agent Mode 多格式 Workspace：借鉴 Hermes/SOLO，但底层 V4-native
10. Desktop-first Runtime：Mac/Windows 安装即用
```

---

## 7. 后续计划建议

现在已经可以进入下一阶段：

```text
DeepSeek Agent 产品战略与技术架构 v0.1
```

该文档应以本次源码调研为基础，结构建议：

```text
1. 产品背景
2. DeepSeek V4 物理特性
3. 竞品源码调研结论
4. 产品定位：Agent Mode + Code Mode
5. 技术架构：Desktop Shell + V4-native Harness
6. 核心创新点
7. MVP 功能边界
8. 技术路线
9. 风险与取舍
10. 研发计划
```

---

## 8. 最终结论

如果只看 “DeepSeek V4-native Harness”：

```text
CodeWhale 是最直接参考；
Reasonix 是最正确的 cache-first 工程参考；
Hermes 是 Agent Mode 和长期自进化能力参考。
```

DeepSeek Agent 的最佳路径不是 fork 一个项目，而是：

```text
以 CodeWhale/Reasonix 的 V4-native cache-first core 为底座思想；
吸收 Hermes 的 Agent OS 能力；
结合 Codex/Claude Code 的成熟工作台和工具范式；
重写 DeepSeek 专属 Harness。
```
