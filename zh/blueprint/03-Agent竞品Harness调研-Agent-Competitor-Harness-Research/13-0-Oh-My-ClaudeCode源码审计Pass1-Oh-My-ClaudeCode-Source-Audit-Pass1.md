# 13-0 Oh My ClaudeCode 源码审计 Pass 1

> Pass 2 已于 2026-06-05 完成，固定 commit、运行路径、实测结果与校准结论见 [`18-0-五项目Pass2与统一证据矩阵`](./18-0-五项目Pass2与统一证据矩阵-Five-Project-Pass2-Uniform-Evidence-Matrix.md)。本文件保留为 Pass 1 历史输入。

## 1. 目标与结论

Oh My ClaudeCode（OMC）是面向 Claude Code 的 teams-first 多 Agent 编排插件与 CLI runtime。它把团队执行定义为显式阶段流水线，并提供 native in-session teams 与 tmux CLI workers 两种并行运行时，同时包含深度访谈、自动执行、持续验证、质量循环和跨模型顾问。

**核心判断：**OMC 对 DeepSeek Agent 最大价值是“把编排状态产品化”：团队流水线、单一 loop authority、verify/fix 回路、HUD、持久目标/证据 artifact。最不应照搬的是围绕 Claude Code 实验性 team 能力和 tmux 的宿主耦合。

## 证据与状态说明

- 调研日期：2026-06-04。
- 证据优先级：官方源码仓库与官方文档为 A 级；基于目录、配置和公开行为的架构推断为 B 级，并明确标注为推断。
- 本报告状态：**源码审计 Pass 1**。已完成仓库结构扫描、关键机制定位、Model-Harness Fit 与迁移判断；尚未完成全仓逐文件/逐函数审计，因此不宣称“完整源码深读完成”。

## 2. 官方证据索引

| 证据 | 级别 | 支撑结论 |
|---|---|---|
| [官方仓库](https://github.com/Yeachan-Heo/oh-my-claudecode) | A | plugin + npm CLI/runtime；teams-first 定位 |
| [仓库根目录](https://github.com/Yeachan-Heo/oh-my-claudecode/tree/main) | A | agents、bridge、commands、hooks、skills、src、templates、tests 等结构 |
| [官方文档](https://yeachan-heo.github.io/oh-my-claudecode/) | A | CLI、workflow 与配置说明 |
| [README Team Mode](https://github.com/Yeachan-Heo/oh-my-claudecode#team-mode-recommended) | A | staged pipeline 与 native/tmux 两类团队 |

## 3. 架构与运行面

OMC 同时暴露：

1. **Claude Code 内技能面**：`/team`、`/autopilot`、`/ralph`、`/ultrawork`、`/deep-interview` 等；
2. **终端 CLI 面**：`omc setup`、`omc ask`、`omc team`；
3. **插件分发面**：Claude marketplace；
4. **npm runtime 面**：安装 CLI、状态与辅助运行时。

`omc team` 与 `/team` 不是同一实现：前者启动 tmux 中真实 Claude/Codex/Gemini/Grok CLI worker，后者运行 Claude Code session 内 native team。这个“双运行时同产品语义”的设计对 DeepSeek Agent 很有启发：本地进程、远端 Agent、应用内子 Agent 可以共享任务协议，但执行适配器不同。

仓库公开目录 `agents/bridge/commands/hooks/skills/src/templates/tests` 表明 OMC 同时包含声明式技能、生命周期注入和 TypeScript runtime，而非只有提示词。

## 4. 关键机制

### 4.1 Team 状态机

官方将 Team 定义为：

```text
team-plan → team-prd → team-exec → team-verify → team-fix (loop)
```

这里最重要的是 `verify → fix` 是明确回路，而不是“执行完就结束”。DeepSeek Agent 应将其扩展为带 checkpoint、证据、预算和 reviewer model 的状态机。

### 4.2 多种 loop authority

OMC 明确建议一个 session 只使用一个 primary loop authority：Team 负责并行阶段执行，Ralph 负责单 Agent 验证完成，UltraQA 负责质量门循环，artifact-only Ultragoal 只保存目标/证据而不启动循环。

这是成熟的控制原则。多个“坚持完成”插件同时运行会导致重复工具调用、冲突状态与无法停止；DeepSeek Agent 应在 runtime 层强制单一 loop owner，而不是靠文档提醒。

### 4.3 需求澄清与可观测性

- Deep Interview 用苏格拉底式提问暴露隐含假设，在编码前量化清晰度；
- HUD statusline 展示运行状态；
- Artifact-only goal/checkpoint/evidence 允许可靠交接；
- `/ask codex`、`/ask gemini` 与 `/ccg` 提供异构模型顾问/交叉审查。

这说明 OMC 不只优化执行速度，也把“何时不该开始写代码”和“用户如何看见编排”作为产品能力。

## 5. Model-Harness Fit

| 维度 | OMC 当前机制 | DeepSeek V4 适配判断 |
|---|---|---|
| 模型路由 | specialized agents + smart routing + 外部 CLI workers | 可映射 Flash/Pro/Thinking，但当前以 Claude/外部 CLI 为中心 |
| 计划与审查 | team-plan/prd/verify/fix、Deep Interview | 很适合 checkpoint-gated Pro review |
| 长任务 | Ralph、Team、UltraQA、持久 artifact | 适合长任务恢复；需 cache-aware message layout |
| 多 Agent | native teams + tmux workers | 协议思想可借鉴，tmux 不宜作为桌面产品核心 |
| 可观测性 | HUD、team status、artifact | 应吸收到 DeepSeek Agent task center |
| 成本 | 宣称 smart routing 节省 token | 需要独立验证；应加入 cache hit/miss 与真实成本账本 |

## 6. 对 DeepSeek Agent 的迁移建议

1. 将 Team pipeline 建模为持久状态机，每个阶段有输入、输出、退出条件、证据和 reviewer。
2. `team-plan/prd` 默认走 Flash + 必要时 Thinking；高风险设计、关键 diff、失败回路升级 Pro。
3. 在 runtime 强制单一 loop authority，禁止 Team/Ralph/QA loop 竞争控制权。
4. 用应用内 worker manager + 隔离 worktree/container 替代 tmux 作为主实现，但保留 CLI adapter。
5. 在任务中心展示 Agent、阶段、预算、工作区、证据、阻塞原因与审批请求。
6. 将 Deep Interview 变成可配置的“需求不确定性门”：只有低清晰度或高风险任务才触发，避免所有任务增加流程负担。

## 7. 风险与待验证问题

1. native team 与 tmux team 是否共享统一 task/state schema，还是仅共享命令名称？
2. Team 的并发写隔离、worktree 模式与合并冲突处理当前成熟度如何？
3. persistent execution 如何防止重复失败与成本失控？
4. “30-50% token 节省”等产品声明需要 benchmark 与源码级验证。
5. Claude Code hooks/skills 的宿主依赖有多少可以提取为独立 orchestrator core？
