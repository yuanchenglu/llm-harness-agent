# 18-0 五项目 Pass 2 与统一证据矩阵

> 结论日期：2026-06-05。状态：**Stage 2 P0 Pass 2 完成**。本报告只证明固定 commit 下的源码路径与代表性测试，不证明生产成熟度、DeepSeek V4 适配收益或真实任务优越性。可复算清单见 [`stage2-pass2-evidence-2026-06-05.json`](./stage2-pass2-evidence-2026-06-05.json)。

## 1. 方法、边界与完成定义

本轮按 `3-Y` 的八步规则完成：仓库扫描、关键模块、逐文件阅读、符号/调用链摘录、固定链接、Model-Harness Fit、迁移判断和报告。证据等级沿用：

```text
A0 = 固定 commit 的真实运行路径 + 本轮执行测试
A1 = 固定 commit 实现源码，未执行对应路径
A2 = 固定 commit 官方 docs/config
B  = 基于 A 级事实的工程推论
N  = 官方开源源码未发现
```

限制：

- 文件数只表示扫描边界，不表示逐文件穷尽阅读；
- 代表性测试通过只证明相应机制在该快照可运行；
- 五项目均未证明 DeepSeek V4 cache、reasoning、路由或成本收益；
- Claude Code 完整 engine 非官方公开，该边界永久保留；
- E4 真实任务比较属于 Stage 3/6，不在本报告伪装完成。

## 2. 固定快照与运行证据

| 项目 | 固定 commit | 扫描源码/测试文件 | 本轮代表性测试 | 结果 |
|---|---|---:|---|---:|
| OpenCode | [`cb65926`](https://github.com/anomalyco/opencode/commit/cb65926c822b2339c260d8b94002f9aafb9ac83a) | 2,378 / 490 | compaction、permission、task | 147 pass / 1 skip / 0 fail |
| OMO | [`e0541cc`](https://github.com/code-yeongyu/oh-my-openagent/commit/e0541ccfe668c1c6d1aa6b3bf0320e27d23ad282) | 2,845 / 1,033 | state、team、hash edit、HTTP security | 94 / 0 / 0 |
| OMC | [`3e94567`](https://github.com/Yeachan-Heo/oh-my-claudecode/commit/3e945671dcf3ed1c1bcc422862815f92c1999143) | 3,299 / 1,125 | pipeline、governance、worktree E2E | 37 / 0 / 0 |
| OpenSpec | [`1b06fdd`](https://github.com/Fission-AI/OpenSpec/commit/1b06fddd59d8e592d5b5794a1970b22867e85b1f) | 277 / 91 | artifact graph、workflow CLI | 195 / 0 / 0 |
| Superpowers | [`6fd4507`](https://github.com/obra/superpowers/commit/6fd4507659784c351abbd2bc264c7162cfd386dc) | 8 / 2 | brainstorm server、WebSocket | 56 / 0 / 0 |

## 3. 五项目 Pass 2

### 3.1 OpenCode：完整 runtime 候选，不是已证明的最终底座

**源码边界与模块。** 官方 monorepo 包含 runtime、provider、session、tool、permission、server、SDK、TUI/Web/Desktop。核心阅读范围：

| 路径 / 符号 | 固定源码证据 | 结论 |
|---|---|---|
| `session/prompt.ts::while (true)` | [`prompt.ts#L1254`](https://github.com/anomalyco/opencode/blob/cb65926c822b2339c260d8b94002f9aafb9ac83a/packages/opencode/src/session/prompt.ts#L1254) | 主 turn loop 接入真实 runtime（A1） |
| `session/llm.ts::streamText` | [`llm.ts#L282`](https://github.com/anomalyco/opencode/blob/cb65926c822b2339c260d8b94002f9aafb9ac83a/packages/opencode/src/session/llm.ts#L282) | provider streaming 调用路径（A1） |
| `session/processor.ts::permission.ask` | [`processor.ts#L532`](https://github.com/anomalyco/opencode/blob/cb65926c822b2339c260d8b94002f9aafb9ac83a/packages/opencode/src/session/processor.ts#L532) | 权限不是只存在于配置（A0） |
| `session/prompt.ts::compaction.isOverflow` | [`prompt.ts#L1329`](https://github.com/anomalyco/opencode/blob/cb65926c822b2339c260d8b94002f9aafb9ac83a/packages/opencode/src/session/prompt.ts#L1329) | 压缩接入 loop（A0） |

**实测。** 147 pass 覆盖权限规则与审批生命周期、child/background task 生命周期、压缩与 token accounting；1 个 skip 明确为关闭的 v2 projector。测试还保留了已知 compaction 边界 BUG 用例，说明“测试通过”不等于“无缺陷”。

**Model-Harness Fit。** 1M context/CSA/HCA/MoE/DSML/DeepSeek cache 路由均无专门证据（N）；通用 provider、compaction、权限、child session 为 A0/A1。  
**迁移判断。** `adapt`：把它作为 Adapter/Fork 候选与自研 runtime 做 E4 对比；`rewrite`：DeepSeek request compiler、reasoning policy、cache telemetry/router；`reject`：在 E4 前宣称“直接 fork 即可”。

### 3.2 Oh My OpenAgent：机制丰富且有实测，复杂度本身是主要风险

**源码边界与模块。** OMO 是 OpenCode/Codex 上的编排增强层，核心为 agents、hooks、team mode、boulder state、tools、MCP 与 adapters。

| 路径 / 符号 | 固定源码证据 | 结论 |
|---|---|---|
| `features/team-mode/integration.test.ts` | [`integration.test.ts`](https://github.com/code-yeongyu/oh-my-openagent/blob/e0541ccfe668c1c6d1aa6b3bf0320e27d23ad282/src/features/team-mode/integration.test.ts) | create/deliver/task/resume/orphan/cleanup/concurrency 有集成测试（A0） |
| `features/boulder-state/storage.ts` | [`storage.ts`](https://github.com/code-yeongyu/oh-my-openagent/blob/e0541ccfe668c1c6d1aa6b3bf0320e27d23ad282/src/features/boulder-state/storage.ts) | 计划/session 状态持久化（A0） |
| `tools/hashline-edit/validation.ts` | [`validation.ts`](https://github.com/code-yeongyu/oh-my-openagent/blob/e0541ccfe668c1c6d1aa6b3bf0320e27d23ad282/src/tools/hashline-edit/validation.ts) | 编辑前验证行引用与 hash（A0） |
| `hooks/claude-code-hooks/execute-http-hook.ts` | [`execute-http-hook.ts`](https://github.com/code-yeongyu/oh-my-openagent/blob/e0541ccfe668c1c6d1aa6b3bf0320e27d23ad282/src/hooks/claude-code-hooks/execute-http-hook.ts) | 拒绝远端明文 HTTP 与非法 scheme（A0） |

**实测。** 94 pass，覆盖持久状态、团队全生命周期、最大并发、hashline stale reference 和 HTTP hook 安全。  
**Model-Harness Fit。** 后台并行/上下文隔离与 cache-first 方向相容（B），但没有 DeepSeek cache 命中或成本实测（N）。  
**迁移判断。** `borrow`：hash/version edit、显式 team lifecycle、安全 hook；`adapt`：少量透明 hooks；`reject`：默认复制大规模隐式 hook/agent surface。

### 3.3 Oh My ClaudeCode：显式团队状态机与治理链路成立

**源码边界与模块。** OMC 同时包含技能层、Claude/native team、tmux/CLI workers、持久状态、worktree、治理和审计。

| 路径 / 符号 | 固定源码证据 | 结论 |
|---|---|---|
| `hooks/team-pipeline/transitions.ts` | [`transitions.ts`](https://github.com/Yeachan-Heo/oh-my-claudecode/blob/3e945671dcf3ed1c1bcc422862815f92c1999143/src/hooks/team-pipeline/transitions.ts) | plan→prd→exec→verify→fix/complete/failed，含 artifact/task guards（A0） |
| `team/task-file-ops.ts` | [`task-file-ops.ts`](https://github.com/Yeachan-Heo/oh-my-claudecode/blob/3e945671dcf3ed1c1bcc422862815f92c1999143/src/team/task-file-ops.ts) | 原子 claim、依赖与完成状态（A1/A0） |
| `team/team-ops.ts` | [`team-ops.ts`](https://github.com/Yeachan-Heo/oh-my-claudecode/blob/3e945671dcf3ed1c1bcc422862815f92c1999143/src/team/team-ops.ts) | approval gate 与原子写入（A0） |
| `team/__tests__/worktree-runtime-e2e.test.ts` | [`worktree-runtime-e2e.test.ts`](https://github.com/Yeachan-Heo/oh-my-claudecode/blob/3e945671dcf3ed1c1bcc422862815f92c1999143/src/team/__tests__/worktree-runtime-e2e.test.ts) | 多 worker commit/merge/通知 E2E（A0） |

**实测。** 37 pass，包含 pipeline guard、approval enforcement 和 3-worker worktree merge E2E。  
**Model-Harness Fit。** 单一 loop authority、显式 phase/evidence 对模型无关；tmux/native Claude 耦合不适合作为桌面产品核心。DeepSeek router/cache 无证据。  
**迁移判断。** `borrow`：phase controller、治理、审计、worktree merge 协议；`adapt`：worker adapter；`reject`：把 tmux 或 prompt 技能当唯一强制层。

### 3.4 OpenSpec：artifact graph 成立，但 verify 不等于执行测试

**源码边界与模块。** OpenSpec 是 artifact/schema/workflow CLI，不是 Agent runtime、权限系统或验证执行器。

| 路径 / 符号 | 固定源码证据 | 结论 |
|---|---|---|
| `core/artifact-graph/schema.ts` | [`schema.ts`](https://github.com/Fission-AI/OpenSpec/blob/1b06fddd59d8e592d5b5794a1970b22867e85b1f/src/core/artifact-graph/schema.ts) | 校验重复 ID、缺失引用和环（A0） |
| `core/artifact-graph/graph.ts` | [`graph.ts`](https://github.com/Fission-AI/OpenSpec/blob/1b06fddd59d8e592d5b5794a1970b22867e85b1f/src/core/artifact-graph/graph.ts) | ready/blocked/complete dependency graph（A0） |
| `core/artifact-graph/state.ts` | [`state.ts`](https://github.com/Fission-AI/OpenSpec/blob/1b06fddd59d8e592d5b5794a1970b22867e85b1f/src/core/artifact-graph/state.ts) | 完成状态主要由 artifact 文件存在检测（A0） |
| `commands/artifact-workflow.test.ts` | [`artifact-workflow.test.ts`](https://github.com/Fission-AI/OpenSpec/blob/1b06fddd59d8e592d5b5794a1970b22867e85b1f/test/commands/artifact-workflow.test.ts) | CLI workflow 集成路径（A0） |

**实测。** 固定 `pnpm@10.17.1` 构建后 195 pass。  
**关键限制。** “all tasks complete”来自任务标记/artifact 状态；verify 指令会建议 tests/review，但 OpenSpec 本身不运行项目测试。因此“完成 artifact”不能升级为“实现通过验收”。  
**迁移判断。** `borrow`：artifact graph/schema/change folder；`adapt`：绑定 evidence ledger、runtime event 和验收器；`reject`：把文档状态当执行真相。

### 3.5 Superpowers：优秀方法论层，强制力取决于宿主

**源码边界与模块。** 核心资产是 skills/提示协议，运行时代码和自动测试面较小。

| 路径 / 符号 | 固定源码证据 | 结论 |
|---|---|---|
| `skills/subagent-driven-development/SKILL.md` | [`SKILL.md`](https://github.com/obra/superpowers/blob/6fd4507659784c351abbd2bc264c7162cfd386dc/skills/subagent-driven-development/SKILL.md) | fresh subagent + spec review + quality review 流程（A2） |
| `skills/verification-before-completion/SKILL.md` | [`SKILL.md`](https://github.com/obra/superpowers/blob/6fd4507659784c351abbd2bc264c7162cfd386dc/skills/verification-before-completion/SKILL.md) | 完成前验证协议（A2） |
| `tests/brainstorm-server/*` | [`tests/brainstorm-server`](https://github.com/obra/superpowers/tree/6fd4507659784c351abbd2bc264c7162cfd386dc/tests/brainstorm-server) | brainstorm 辅助 server 有运行测试（A0） |

**实测。** 56 pass，证明 brainstorm server/WebSocket；不证明所有 skill 都由宿主强制执行。  
**Model-Harness Fit。** 小而清晰的工程流程对模型无关；“MUST”主要是行为协议，不是 runtime gate。  
**迁移判断。** `borrow`：TDD、两阶段 review、verification-before-complete；`adapt`：把高风险规则升级为状态机/权限/验收器；`reject`：仅凭 prompt 宣称强制合规。

## 4. 十一项目统一证据矩阵

| 项目 | 官方源码边界 | 真实 runtime 路径 | 本地执行证据 | 成熟度可安全声称到 | DeepSeek Agent 决策 |
|---|---|---|---|---|---|
| Claude Code | 插件/docs；完整 engine 不公开 | 不可官方审计 | 无 engine 本地证据 | 产品/插件范式 | 借鉴产品行为，不借 engine 事实 |
| Codex | 完整公开核心 | turn/context/tool/sandbox 等可定位 | 既有 A0/A1 校准；本轮未重跑 | 通用核心工程强参考 | 借边界与类型，不等于 V4-native |
| Trae Agent | 小型公开 runtime | loop/tool/trajectory/Docker/MCP | 既有 A1 校准 | 可读单 Agent runtime | 借 trajectory；拒绝虚构 test-time scaling |
| Reasonix | DeepSeek-oriented runtime | adapter/plan/compaction/cache usage | 既有 A1/A0 校准 | DeepSeek-specific 候选 | 协议分歧交给 E3 |
| Hermes Agent | 大型 Agent OS | registry/disclosure/compression | 既有 A1 校准 | 能力层强参考 | 借 registry；memoization 不等于 prefix cache |
| CodeWhale | DeepSeek-oriented Rust runtime | prefix check/telemetry/router/replay | 既有 A0/A1 校准 | 部分 DeepSeek runtime 已接线 | 借 drift check；three-zone 仍未完整接线 |
| OpenCode | 完整多端 runtime | loop/provider/permission/compaction/task | 147 pass / 1 skip | 底座候选 | 进入 E4 Adapter/Fork 比较 |
| OMO | 宿主增强层 | hook/team/state/hash edit | 94 pass | 编排机制丰富 | 选择性吸收，限制隐式复杂度 |
| OMC | skills + team runtime | phase/governance/worktree | 37 pass | 团队治理强参考 | 借显式状态机，不绑定 tmux |
| OpenSpec | artifact/workflow CLI | graph/schema/instructions | 195 pass | artifact 协议 | 扩展为 evidence-backed protocol |
| Superpowers | skills 方法论 | 主要由宿主解释执行 | 56 pass（server） | 工程流程参考 | 把关键规则升级为 runtime gate |

## 5. P1 范围决策

| 项目 | 决策 | 理由与后续用途 |
|---|---|---|
| Cursor / Windsurf / Devin | 排除源码 Pass 2 | 完整官方 engine 不开源；只保留产品/docs 对比，不制造源码事实 |
| Roo Code | 纳入 E4 runtime baseline | Cline/Roo 家族的开放代表；用于 extension/UI/runtime 对比 |
| Cline | 延期独立 Pass 2 | 当前由 Roo 代表共享问题；出现家族差异关键假设时再审 |
| OpenHands | 纳入 E4 runtime baseline | 用于 sandbox/autonomous runtime 对比 |
| Goose | 纳入 E4 runtime baseline | 用于 desktop/MCP/runtime 对比 |
| Aider | 纳入 E4 git/edit baseline | 用于确定性编辑与 git 工作流对比 |

固定 HEAD 观察值与理由已写入机器清单；它们只是 Stage 3/6 baseline 输入，不是已完成 Pass 2。

## 6. 过度声明复核

| 旧表达风险 | 校准后表达 |
|---|---|
| OpenCode 是“可直接 fork 的最终底座” | OpenCode 是具备完整 runtime 的 **Adapter/Fork 候选**，最终选择需 E4 |
| OMO/OMC 团队模式必然提高质量 | 团队机制和测试成立；净收益、成本与冲突率待 E4 |
| OpenSpec verify/complete 等于代码验收通过 | 只证明 artifact/task 状态；必须绑定可执行验收器 |
| Superpowers 的 MUST 会被所有宿主强制执行 | 是方法论协议；关键规则需 runtime gate |
| “终版/完整/生产级”由源码模块名证明 | 必须有固定调用路径、运行测试和对应生产证据；历史标题不作为状态声明 |
| 任何通用 harness 已适配 DeepSeek V4 物理特性 | 五项目均无该证据；V4-native 层需 E3/E4 |

## 7. 复现命令

```bash
cd /tmp/stage2-opencode/packages/opencode
bun test test/session/compaction.test.ts test/permission/next.test.ts test/tool/task.test.ts

cd /tmp/stage2-omo
bun test src/features/boulder-state/storage.test.ts src/features/team-mode/integration.test.ts src/tools/hashline-edit/validation.test.ts src/hooks/claude-code-hooks/execute-http-hook-security.test.ts

cd /tmp/stage2-omc
npm run test:run -- src/hooks/team-pipeline src/team/__tests__/phase-controller.test.ts src/team/__tests__/governance-enforcement.test.ts src/team/__tests__/worktree-runtime-e2e.test.ts

cd /tmp/stage2-openspec
npx --yes pnpm@10.17.1 exec vitest run test/core/artifact-graph/*.test.ts test/commands/artifact-workflow.test.ts

cd /tmp/stage2-superpowers
node --test tests/brainstorm-server/server.test.js tests/brainstorm-server/ws-protocol.test.js
```

## 8. Stage 2 Gate 结论

- `five_project_pass2`：通过；五项目均有固定 commit、核心调用路径、限制与迁移判断；
- `p1_competitor_scope_decision`：通过；逐项纳入/延期/排除并说明原因；
- `uniform_runtime_and_test_evidence_matrix`：通过；机器清单和十一项目矩阵可追溯；
- `remaining_overclaim_audit`：通过；关键高影响表述已校准，历史标题不再作为完成证据。

Stage 2 的完成只允许进入 Stage 2.5；不代表 E3 API、E4 真实任务、底座 ADR 或生产 MVP 已完成。
