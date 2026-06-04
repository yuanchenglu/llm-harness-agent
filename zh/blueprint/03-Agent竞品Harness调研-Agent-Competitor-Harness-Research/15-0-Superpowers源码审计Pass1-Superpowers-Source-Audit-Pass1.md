# 15-0 Superpowers 源码审计 Pass 1

## 1. 目标与结论

Superpowers 是由可组合 skills 构成的软件工程方法论层，覆盖 brainstorming、worktree、计划、子 Agent 开发、TDD、代码审查与分支收尾。它通过“自动触发且属于强制流程”的技能，把 Agent 从自由发挥约束到可验证工程流程。

**核心判断：**Superpowers 是五个对象中最值得直接吸收为 DeepSeek Agent 默认工程技能包的项目。它证明高质量 Agent 不一定依赖更复杂的核心 loop，也可以依靠少量清晰、可组合、可测试的流程原语提升可靠性。风险是规则过强会降低小任务效率，且 skill 是否真正被执行仍受宿主遵循能力影响。

## 证据与状态说明

- 调研日期：2026-06-04。
- 证据优先级：官方源码仓库与官方文档为 A 级；基于目录、配置和公开行为的架构推断为 B 级，并明确标注为推断。
- 本报告状态：**源码审计 Pass 1**。已完成仓库结构扫描、关键机制定位、Model-Harness Fit 与迁移判断；尚未完成全仓逐文件/逐函数审计，因此不宣称“完整源码深读完成”。

## 2. 官方证据索引

| 证据 | 级别 | 支撑结论 |
|---|---|---|
| [官方仓库](https://github.com/obra/superpowers) | A | composable skills + development methodology；MIT |
| [`skills/`](https://github.com/obra/superpowers/tree/main/skills) | A | 技能库是产品核心 |
| [`tests/`](https://github.com/obra/superpowers/tree/main/tests) | A | 技能/安装行为有测试支撑 |
| [README Basic Workflow](https://github.com/obra/superpowers#the-basic-workflow) | A | brainstorming→worktree→plan→execution→TDD→review→finish |
| [多 Harness 安装](https://github.com/obra/superpowers#installation) | A | Claude、Codex、Gemini、OpenCode、Cursor、Copilot 等 |

## 3. 方法论状态机

Superpowers 的基本工作流可以视为一条轻量状态机：

```text
brainstorming
  → design approval
  → using-git-worktrees
  → writing-plans
  → subagent-driven-development | executing-plans
  → test-driven-development
  → requesting-code-review
  → finishing-a-development-branch
```

关键不在步骤数量，而在每一步有清晰不变量：

- brainstorming 在写代码前触发，通过问题澄清需求并分段确认设计；
- worktree 创建隔离工作区并验证干净基线；
- plan 将任务拆到 2–5 分钟粒度，写明文件、代码和验证；
- subagent-driven-development 每个任务使用新 Agent，并执行“规格符合性→代码质量”两阶段审查；
- TDD 强制 RED-GREEN-REFACTOR，甚至要求删除测试前写出的实现；
- verification-before-completion 要求完成声明必须有证据；
- finishing branch 在测试后让用户选择 merge/PR/keep/discard 并清理工作区。

## 4. 为什么它有效

### 4.1 把隐性工程经验变成可调用原语

“先理解问题”“测试后再说完成”常被写成宽泛系统提示，容易被模型忽略。Superpowers 把它们拆为具体 skill，包含触发条件、流程和验收标准，降低执行歧义。

### 4.2 新鲜上下文与两阶段审查

每个任务交给 fresh subagent 可减少前序任务噪声；规格审查与代码质量审查分离，避免 reviewer 同时处理“做对东西”和“东西做得好”两类目标。这可直接映射 DeepSeek Flash 执行 + Pro review。

### 4.3 Evidence over claims

Superpowers 的核心哲学包含“系统化而非临时猜测”“证据优于声明”。它与 DeepSeek Agent checkpoint-gated 定位高度一致：完成不应是模型输出文本，而应是 tests/diff/review/evidence 状态。

## 5. Model-Harness Fit

| 维度 | Superpowers 当前机制 | DeepSeek V4 适配判断 |
|---|---|---|
| 模型依赖 | 多 Harness 可用、主要是文本 skills | 高可移植性，但执行可靠性取决于宿主 |
| Flash/Pro 路由 | 未内建 | 任务执行用 Flash、设计/审查用 Pro 很自然 |
| 长上下文 | 计划与 fresh subagent 分割任务 | 有利于 active set 与上下文隔离 |
| 审查 | 规格/质量两阶段 review、completion verification | 非常适合 checkpoint-gated Pro review |
| 执行隔离 | git worktree | 可作为本地并行默认隔离方式 |
| 工具协议/缓存 | 不负责 | 需由 DeepSeek runtime 提供 |

## 6. 对 DeepSeek Agent 的迁移建议

### P0 默认技能包

- `clarify-before-build`：风险/不确定度超过阈值才触发；
- `isolated-workspace`：为并行任务创建 worktree/container；
- `write-executable-plan`：任务必须绑定路径、验收与验证命令；
- `red-green-refactor`：在可测试任务中强制 TDD；
- `systematic-debugging`：根因追踪优先于试错 patch；
- `verify-before-complete`：没有新鲜证据不得完成；
- `two-stage-review`：spec compliance 与 code quality 分开；
- `finish-task`：明确 merge/PR/keep/discard 与清理。

### Runtime 原生化，而不是仅复制提示词

1. Skill 触发由策略引擎记录，UI 展示为何触发、是否可跳过。
2. 强制步骤通过工具权限与状态机实现，例如未记录失败测试时禁止进入 GREEN。
3. 每个验证结果写入 evidence ledger，并带时间、命令、退出码、artifact hash。
4. 根据任务规模提供 `fast/standard/strict` 三档流程，避免小修复被完整流程拖慢。
5. 为 skills 建立版本、依赖、冲突、测试与安全声明，形成可治理 marketplace。

## 7. 风险与待验证问题

1. 各 Harness 如何保证“mandatory workflow”不被模型忽略？
2. skills 的测试主要验证文本结构、触发行为还是端到端结果？
3. TDD 对 UI、配置、探索型任务如何合理豁免？
4. fresh subagent 的上下文交接格式是否稳定、是否丢失关键约束？
5. 多 Harness 安装适配器是否共享同一技能源，如何避免版本漂移？
