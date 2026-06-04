# 6-0 Claude Code / Codex / Trae 三者源码审计总评 Final Source Audit Summary

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v0.9  
> 目标：在完成 Claude Code、Codex、Trae 三者源码/文档审计后，给出可用于 DeepSeek Agent 架构设计的最终对比。

---

## 1. 审计状态

| 产品 | 官方源码完整度 | 当前审计状态 | 可信度 |
|---|---|---|---|
| Claude Code | 官方完整 engine 未公开；官方 plugins 公开 | 官方边界确认 + C级 reverse source Pass 1 | 官方 Docs=S1；reverse source=C |
| Codex | 官方开源核心较完整 | core context / turn / compact / config Pass 2 | S0/S1 |
| Trae Agent | 官方开源 agent 较完整 | BaseAgent / TraeAgent / Trajectory Pass 2 | S0/S1 |

---

## 2. 三者真正值得学什么

| 产品 | 最值得学 | 原因 |
|---|---|---|
| Claude Code | Mature Harness 范式、plugins/skills/hooks、permission callback、memory/compaction 思路 | 产品成熟、生态强，但源码不可全审 |
| Codex | typed context fragments、TurnContext、turn loop、auto compact、permission/sandbox、review/app workstation | 源码层最有价值 |
| Trae Agent | trajectory-first runtime、sequential_thinking、task_done、Docker/MCP | 开源源码适合作为小型 Agent loop 参考；未发现 multi-candidate/test-time scaling runtime |

---

## 3. DeepSeek V4 物理特性适配总矩阵

| V4 物理特性 | Claude Code | Codex | Trae Agent | DeepSeek Agent 应怎么做 |
|---|---:|---:|---:|---|
| 1M context | B | B+ | C | V4 Context Layout Manager |
| CSA/HCA sparse attention | C | C | D | Task Anchor / Active Working Set / Compressed History |
| sliding_window=128 | C | C | D | turn tail / active window 优先 |
| cache hit/miss pricing | C+ | B | B- | CostCacheTelemetry + PrefixDriftDetector |
| Flash/Pro/Think/Max | C | B | C+ | ModelRouter |
| MoE/hash routing | C | C+ | C | stable tags / fixed prompt protocol |
| mHC多信号 | C | C+ | B- | Goal/Constraint/Evidence/Execution/Review 分层 |
| V4 DSML encoding | D | D | D | DeepSeekV4MessageCompiler |
| reasoning_content policy | C | B- | B | 四态管理 + structured reasoning |
| checkpoint-driven review | B | B | B- | Flash execute + Pro review |
| tool runtime | A | A | B+ | 借鉴并统一 |
| permission/sandbox | A | A | B | Runtime enforce |
| trajectory/trace | B | B | A | Trajectory-first Runtime |

---

## 4. 最终架构启发

### 4.1 从 Claude Code 借

```text
plugins / skills / hooks / agents
permission callback
memory prompt
transcript/session persistence
cost tracker
file history snapshot
```

### 4.2 从 Codex 借

```text
ContextualUserFragment
InternalModelContextFragment
EnvironmentContext
TurnContext
run_turn loop
auto compact
pre/mid-turn compaction
approval reviewer
sandbox profile
app/review/worktree 思路
```

### 4.3 从 Trae 借

```text
TrajectoryRecorder
BaseAgent loop skeleton
task_done
sequential_thinking
Docker executor
multi-candidate / generation-pruning-selection（仅可作为待验证研究方向；当前官方开源源码未发现实现）
```

---

## 5. DeepSeek Agent 必须自研的核心层

三者都没有真正解决 DeepSeek V4 专属问题，因此必须自研：

```text
1. DeepSeekV4MessageCompiler
2. DSMLToolParser
3. V4 Context Layout Manager
4. Flash / Pro / Thinking / Max Router
5. DeepSeek Cache Telemetry
6. Prefix Drift Detector
7. ReasoningContentPolicy
8. Checkpoint-driven Pro Review
9. V4-aware Trajectory Schema
10. Cost-aware Test-time Scaling
```

---

## 6. 结论

Claude Code、Codex、Trae 的三者关系可以定为：

```text
Claude Code = Harness 成熟度标杆
Codex = 源码工程结构标杆
Trae Agent = trajectory-first 小型 Agent runtime 参考；不是已开源的 test-time scaling 标杆
```

DeepSeek Agent 的核心机会不是复制任何一个，而是：

```text
吸收三者 Harness 经验，
用 DeepSeek V4 的物理特性重写关键层。
```
