# 12-0 Oh My OpenAgent 源码审计 Pass 1

## 1. 目标与结论

Oh My OpenAgent（OMO，历史名称 Oh My OpenCode）是建立在 Agent Harness 之上的“编排与工程纪律增强层”。它不是 OpenCode 的替代品，而是通过 agents、hooks、MCP、skills、规则注入、持续循环与编辑工具，把基础 Agent 变成可长期执行的多 Agent 工程团队。

**核心判断：**OMO 最值得 DeepSeek Agent 吸收的不是 11 个角色名称，而是四个机制：意图闸门、后台并行且保持主上下文精简、hash-anchored edit、完成证据/待办强制器。其最大风险是功能与 hook 数量过多，可能制造隐式状态、上下文污染和不可解释的自动行为。

## 证据与状态说明

- 调研日期：2026-06-04。
- 证据优先级：官方源码仓库与官方文档为 A 级；基于目录、配置和公开行为的架构推断为 B 级，并明确标注为推断。
- 本报告状态：**源码审计 Pass 1**。已完成仓库结构扫描、关键机制定位、Model-Harness Fit 与迁移判断；尚未完成全仓逐文件/逐函数审计，因此不宣称“完整源码深读完成”。

## 2. 官方证据索引

| 证据 | 级别 | 支撑结论 |
|---|---|---|
| [官方仓库与 README](https://github.com/code-yeongyu/oh-my-openagent) | A | Ultimate/Light 两种产品面；11 agents、54+ hooks、5 MCP、Team Mode |
| [`src/` 目录](https://github.com/code-yeongyu/oh-my-openagent/tree/dev/src) | A | agents/config/features/hooks/mcp/plugin-handlers/tools 等模块 |
| [安装指南](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/docs/guide/installation.md) | A | provider 访谈、agent-model matching、运行模式 |
| [ROADMAP](https://github.com/code-yeongyu/oh-my-openagent/blob/dev/ROADMAP.md) | A | 正在拆分纯 TS core、MCP、skills 与 harness adapters |

## 3. 产品边界与源码地图

OMO 当前分两种 edition：

- **Ultimate / OpenCode**：完整编排，含 agents、hooks、MCP、Team、ultrawork、hashline edits。
- **Light / Codex CLI**：只移植 Codex 插件面能承载的 rules、comment-checker、LSP、ultrawork、ulw-loop、续作与 telemetry，不宣称拥有完整编排。

这个差异揭示一个关键事实：插件能力上限受宿主 Harness 的 extension surface 决定。OMO ROADMAP 正在把纯 TypeScript core、MCP servers、skills 与 adapter shim 分层，说明“跨 Harness 可移植编排内核”本身是明确方向。

`src/` 结构进一步显示其实现不是纯 prompt 包：

```text
agents/             专业 Agent 定义与路由
features/           可组合功能
hooks/              生命周期控制与行为注入
mcp/                内置 MCP 服务
plugin-handlers/    宿主事件适配
plugin/             插件主体
shared/             共用逻辑
tools/              自定义工具
create-managers.ts  manager 装配
create-tools.ts     工具装配
index.compacting*   compaction 相关测试
```

## 4. 关键机制

### 4.1 意图、编排与持续完成

- `IntentGate` 在分类和执行前解析真实意图，避免逐字执行错误目标。
- Sisyphus 作为 lead 协调 Hephaestus、Oracle、Librarian、Explore 等专业角色。
- `ultrawork` 激活并行 Agent；`Ralph/ulw-loop` 与 Todo Enforcer 避免过早停止。
- Team Mode 支持 lead + 最多 8 个成员，并提供专用 `team_*` 工具与 tmux 可视化。

**迁移原则：**DeepSeek Agent 应借鉴“持续到有证据的完成”，但不能借鉴“默认无限坚持”。循环必须受成本、风险、重复失败、用户中断与 checkpoint 策略共同约束。

### 4.2 上下文与规则

- 后台 Agent 将搜索/研究隔离出去，只把结果带回主上下文。
- `AGENTS.md` 与 `.omo/rules/**` 在 prompt 时自动注入。
- `/init-deep` 生成分层 AGENTS.md，以局部规则减少无关上下文。
- skill-embedded MCP 让技能只在使用时携带专属工具，降低常驻工具描述膨胀。

这些机制与 DeepSeek V4 的 active working set 高度一致：主上下文保留目标、决策与证据索引，重搜索放在子会话。

### 4.3 工具可靠性

Hash-Anchored Edit 使用 `LINE#ID` 内容 hash 校验变更目标，避免基于旧行号或旧内容修改。这应被视作 DeepSeek Agent P0 借鉴项：长任务中 workspace 持续变化，编辑前的乐观并发校验比盲目 patch 更可靠。

LSP 与 AST-Grep 提供结构化定位、诊断与重写；Comment Checker 则是低成本输出质量门。共同点是把可确定的工程验证交给工具，而不是让模型“凭感觉确认”。

## 5. Model-Harness Fit

| 维度 | OMO 当前机制 | DeepSeek V4 适配判断 |
|---|---|---|
| Flash/Pro 路由 | agent-model matching matrix、多 provider | 思路可用，但需要 V4 原生质量/成本/风险路由器 |
| 长上下文 | 后台 Agent、规则分层、compaction 测试 | 有利于 active set；需 byte-stable prefix 策略 |
| 工具可靠性 | hash edit、LSP、AST-Grep | 非常适合提升 DeepSeek 工具执行确定性 |
| 持续执行 | Ralph、ulw-loop、Todo Enforcer | 能减少半成品；需预算与停机保护 |
| 证据审查 | comment checker、完成循环、团队批评 | 应升级为 checkpoint + Pro reviewer + evidence ledger |
| 插件可移植性 | Ultimate/Light + adapter 重构 | 可作为 DeepSeek 插件 API 设计样板 |

## 6. 对 DeepSeek Agent 的迁移建议

### 应吸收

1. `IntentGate`：在计划前输出结构化 intent/constraints/success criteria。
2. Hash-Anchored Edit：每次编辑携带文件版本/hash，冲突时重读而非硬写。
3. Background Agent：研究与扫描在隔离会话完成，只回传结构化证据。
4. Evidence-aware continuation：未满足测试、diff review、用户验收条件时不宣称完成。
5. Skill-embedded tools：按需暴露工具，缩小工具 schema 与权限面。
6. 分层规则生成：根规则 + 目录局部规则，配合稳定前缀缓存。

### 不应直接照搬

- 不应默认安装几十个 hook 并让行为难以解释；
- 不应把“永不停止”作为产品承诺；
- 不应静态绑定具体外部模型角色；
- 不应默认开启遥测，DeepSeek Agent 应在首次运行显式选择并公开事件 schema。

## 7. 风险与待验证问题

1. 54+ hooks 的触发顺序、冲突解决、失败隔离和可观测性如何？
2. compaction 相关测试证明了哪些不变量，是否能保持缓存稳定？
3. Team Mode 的 workspace 隔离与合并策略是否足以避免并发写冲突？
4. Hashline edit 的 hash 粒度、重定位策略与大文件性能如何？
5. ROADMAP 分层完成前，跨 Harness core 是否仍与 OpenCode API 高耦合？
