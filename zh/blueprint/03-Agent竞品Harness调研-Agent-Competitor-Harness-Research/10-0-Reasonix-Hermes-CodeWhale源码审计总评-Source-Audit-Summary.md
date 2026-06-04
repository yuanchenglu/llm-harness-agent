# 10-0 Reasonix / Hermes / CodeWhale 三者源码审计总评 Pass 1

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md`](./17-2-Reasonix-Hermes-CodeWhale源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v1.0  
> 状态：三者源码审计 Pass 1 完成。  
> 注意：这不是“每个文件都已读完”的最终版，而是足以确定三者架构价值和下一步深读路径的第一轮源码级审计。

---

## 1. 三者定位

| 项目 | 定位 | 最核心价值 |
|---|---|---|
| Reasonix | DeepSeek-native terminal coding agent | Prefix-cache stable sessions + Flash executor / Pro planner |
| Hermes Agent | 通用个人 Agent OS | Memory / skills / gateway / cron / trajectory / multi-platform |
| CodeWhale | DeepSeek V4 terminal coding harness | Constitution + auto Flash/Pro/thinking route + side-git + subagents + LSP |

---

## 2. DeepSeek V4 适配深度排序

```text
CodeWhale > Reasonix > Hermes
```

原因：

```text
CodeWhale 直接围绕 DeepSeek V4、prefix cache、model/thinking auto route、cache hit/miss tracking。
Reasonix 直接围绕 DeepSeek prefix cache、Flash/Pro planner/executor、cache-stable sessions。
Hermes 是强通用 Agent OS，但不是 DeepSeek-native，需要大量 V4-specific 重写。
```

---

## 3. 我们应从三者各借什么

### Reasonix

```text
cache-stable sessions
executor + planner 双模型
auto_plan_classifier = cheap Flash
config-driven providers/tools/plugins
MCP prompt/resource/tool protocol
permissions policy + sandbox enforcement 分离
branch / rewind / session tree
```

### Hermes

```text
tool registry self-registration
dynamic tool schema rewriting
tool_search progressive disclosure
tool error sanitization
tool arg coercion
memory / skill self-evolution
gateway / cron
trajectory compression
multi-platform continuity
```

### CodeWhale

```text
Constitution authority hierarchy
DeepSeek prefix cache as first-class product primitive
Flash routing call with thinking off
auto model + thinking route
side-git checkpoint / restore
concurrent subagents with transcript handles
LSP diagnostics injection
live cost/cache tracking
RLM sessions
```

---

## 4. 三者都没有完全解决的问题

即使 CodeWhale 已经很接近，也仍需要我们重新定义：

```text
DeepSeekV4MessageCompiler
DSMLToolParser
V4 CSA/HCA-aware Context Layout
ReasoningContentPolicy 四态管理
Checkpoint-driven Pro Review
Product-grade CostCacheTelemetry
Agent Mode + Code Mode 统一桌面产品
```

---

## 5. 下一步建议

继续源码深读顺序：

```text
1. CodeWhale Rust core：turn_loop / client / pricing / compaction / subagent / rlm
2. Reasonix Go core：agent.go / compact.go / provider/openai / billing / checkpoint / permission
3. Hermes：tool registry / memory / skills / cron / gateway / trajectory compressor
```

然后进入：

```text
竞品架构对比矩阵
DeepSeek Agent Harness 设计原则
DeepSeek Agent 产品战略与技术架构 v0.1
```
