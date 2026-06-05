# 11-0 OpenCode 源码审计 Pass 1

> Pass 2 已于 2026-06-05 完成，固定 commit、运行路径、实测结果与校准结论见 [`18-0-五项目Pass2与统一证据矩阵`](./18-0-五项目Pass2与统一证据矩阵-Five-Project-Pass2-Uniform-Evidence-Matrix.md)。本文件保留为 Pass 1 历史输入。

## 1. 目标与结论

OpenCode 不是“又一个终端聊天壳”，而是一套模型无关、前后端分层、可被插件扩展的开源 Coding Agent 平台。它同时覆盖 TUI、CLI、Web、桌面端、IDE、SDK、Server、插件与企业能力，是五个对象中最接近 DeepSeek Agent 可选产品底座的项目。

**核心判断：**优先把 OpenCode 当作“Adapter/Fork 候选 Agent Runtime + 多端产品骨架”，而不是仅当竞品功能清单；是否作为最终底座必须由 E4 对比决定。最值得借鉴的是 provider/model 抽象、primary/subagent 体系、细粒度权限、child session、隐藏系统 agent、server/SDK/plugin 边界；最需要补齐的是 DeepSeek V4 原生缓存布局、Flash/Pro/Thinking 路由、reasoning_content 生命周期和 checkpoint-gated review。

## 证据与状态说明

- 调研日期：2026-06-04。
- 证据优先级：官方源码仓库与官方文档为 A 级；基于目录、配置和公开行为的架构推断为 B 级，并明确标注为推断。
- 本报告状态：**源码审计 Pass 1**。已完成仓库结构扫描、关键机制定位、Model-Harness Fit 与迁移判断；尚未完成全仓逐文件/逐函数审计，因此不宣称“完整源码深读完成”。

## 2. 官方证据索引

| 证据 | 级别 | 支撑结论 |
|---|---|---|
| [官方仓库](https://github.com/anomalyco/opencode) | A | MIT 开源；同时提供终端与 Beta 桌面端；默认 build/plan agent |
| [packages 目录](https://github.com/anomalyco/opencode/tree/dev/packages) | A | app、cli、core、desktop、llm、opencode、plugin、sdk、server、web 等分层 |
| [Agents 文档](https://opencode.ai/docs/agents) | A | primary/subagent、隐藏 compaction/title/summary agent、模型与权限配置 |
| [Permissions 文档](https://opencode.ai/docs/permissions) | A | ask/allow/deny 与按命令/工具粒度匹配 |
| [Providers 文档](https://opencode.ai/docs/providers) | A | 多 provider 接入边界 |
| [Plugins 文档](https://opencode.ai/docs/plugins) | A | 插件扩展面 |

## 3. 仓库结构与架构地图

官方 `packages/` 直接显示产品采用 monorepo 分层：

```text
packages/app        通用应用 UI
packages/cli        CLI 入口
packages/core       通用核心能力
packages/desktop    桌面端
packages/llm        LLM 相关抽象
packages/opencode   Agent 主运行时（下一轮重点）
packages/plugin     插件 API
packages/sdk        外部集成 SDK
packages/server     服务端/API 边界
packages/web        Web 产品面
packages/enterprise 企业能力
```

**B 级推断：**`core/llm/opencode/server/sdk/plugin` 的拆分意味着 OpenCode 已把“Agent engine、模型协议、交互客户端和扩展生态”做了较清晰的解耦。这种边界比从单体 CLI 起步更适合 DeepSeek Agent 的桌面优先目标。

## 4. Agent 与运行机制

### 4.1 Agent 类型

- `build`：默认 primary agent，完整工具权限。
- `plan`：受限 primary agent，写文件与 bash 默认 ask，适合只读分析。
- `general`：通用 subagent，可处理多步任务并可并行。
- `explore`：快速、只读、本地代码探索。
- `scout`：只读外部依赖与文档研究。
- `compaction`、`title`、`summary`：隐藏系统 agent，分别负责压缩、标题和摘要。

这说明 OpenCode 没有把所有后台工作都塞给主 Agent，而是把系统维护任务也 agent 化。子 Agent 产生 child session，用户可以在父子会话之间导航，形成可观测的任务树。

### 4.2 配置与模型路由

Agent 可用 JSON 或项目/全局 Markdown 定义，并独立配置 prompt、model、temperature、steps 和 permission。`provider/model-id` 形式说明模型选择是显式配置项；subagent 默认继承调用它的 primary agent 模型，也可覆盖。

`steps` 是成本/失控控制器：达到上限后 Agent 被要求输出总结与剩余任务，而不是无限循环。该设计可迁移为 DeepSeek Agent 的预算门控，但应扩展为 token、cache miss、美元成本、wall time 与工具风险的联合预算。

### 4.3 权限模型

OpenCode 权限不是简单“全开/只读”：

- 动作：`ask | allow | deny`；
- 范围：read/edit/glob/grep/list/bash/task/external_directory/LSP/skill 等；
- 支持工具名与 shell 命令 pattern；
- 支持全局默认、per-agent 覆盖；
- `permission.task` 控制 orchestrator 能调用哪些 subagent，deny 后甚至从工具描述移除。

对 DeepSeek Agent 而言，最后一点尤其重要：权限不仅在执行时拦截，也在模型可见工具面上裁剪，可减少误调用与上下文噪声。

## 5. Model-Harness Fit

| 维度 | OpenCode 当前能力 | DeepSeek V4 适配判断 |
|---|---|---|
| 多模型/多 provider | 强，agent 可独立选模型 | 可映射 Flash/Pro，但需要内建策略路由而非静态配置 |
| 1M context | 有 compaction/summary 系统 agent | 能避免溢出，但未证明针对 CSA/HCA 布局优化 |
| active working set | explore/scout 子会话隔离 | 有利于保持主上下文精简 |
| 工具调用 | 丰富工具、MCP、LSP、插件 | 需要增加 DSML/DeepSeek tool encoding 原生适配 |
| 权限 | 细粒度 ask/allow/deny | 可直接借鉴为风险门控基础 |
| 成本控制 | steps 上限、模型覆盖 | 缺 cache hit/miss 与 Flash/Pro 成本遥测 |
| 审查 | plan/build 分工、子 agent | 尚缺强制 checkpoint→Pro review 产品语义 |
| 多端 | TUI/CLI/Web/Desktop/IDE/SDK/Server | 与 DeepSeek Agent 桌面优先 + CLI 附属高度匹配 |

## 6. 对 DeepSeek Agent 的迁移建议

### P0：优先验证可 fork 性

1. 对 `packages/opencode`、`packages/llm`、`packages/server`、`packages/sdk` 做 Pass 2 逐文件审计。
2. 实测接入 DeepSeek API：tool calling、thinking/reasoning_content、流式响应、错误恢复。
3. 在 agent 配置之上新增 `model_class: flash|pro|thinking|max`，由策略层动态解析，而不是暴露具体模型 ID。
4. 在会话事件中加入 `cache_hit_tokens/cache_miss_tokens/layout_hash/checkpoint_id/review_status`。

### P1：可直接借鉴的产品结构

- 复用 primary/subagent/hidden-system-agent 分类；
- 将 compaction 改造成“byte-stable prefix + append-only evidence + active set”布局器；
- 将 child session 升级为可视化任务树与审查树；
- 复用 permission pattern 思路，增加风险级别、数据边界与 endpoint policy；
- 以 Server + SDK 为桌面端、CLI、IDE 共用 runtime，而不是每端复制 agent loop。

## 7. 风险与待验证问题

1. `packages/opencode` 内部 Agent loop、消息持久化、compaction 与 provider 转换的真实耦合度如何？
2. Desktop Beta 是否真正复用同一 server/runtime，还是存在客户端特化？
3. 插件 API 是否足以实现 DeepSeek 专属上下文布局和协议适配，还是必须 fork core？
4. OpenCode 的 license 为 MIT，但依赖、品牌、云服务与 Zen 能力需单独审计。
5. 大规模并行 child session 的 token 成本、冲突处理和安全边界需要实测。
