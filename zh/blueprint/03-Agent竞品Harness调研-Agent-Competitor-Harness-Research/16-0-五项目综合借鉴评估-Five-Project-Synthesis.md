# 16-0 OpenCode / OMO / OMC / OpenSpec / Superpowers 综合借鉴评估

## 1. 目的与总评

这五个项目不是同一层面的直接竞品，而是恰好覆盖了现代 Agent 产品栈的五个关键层级：

```text
OpenCode        = 可 fork 的 Agent Runtime 与多端产品骨架
Oh My OpenAgent = Harness 增强、工具可靠性、并行与持续执行
Oh My ClaudeCode= Teams-first 编排状态机与可观测性
OpenSpec        = 可版本化的需求/设计/任务 artifact 协议
Superpowers     = 可组合、可强制、可验证的软件工程技能方法论
```

**综合结论：**DeepSeek Agent 不应选择其中一个“整体照搬”，而应以 OpenCode 类 runtime 为底座候选，将 OMO/OMC 的编排机制、OpenSpec 的 artifact 协议和 Superpowers 的工程纪律收敛为一套 DeepSeek V4-native、cache-first、checkpoint-gated 产品。

## 证据与状态说明

- 调研日期：2026-06-04。
- 证据优先级：官方源码仓库与官方文档为 A 级；基于目录、配置和公开行为的架构推断为 B 级，并明确标注为推断。
- 本报告状态：**源码审计 Pass 1**。已完成仓库结构扫描、关键机制定位、Model-Harness Fit 与迁移判断；尚未完成全仓逐文件/逐函数审计，因此不宣称“完整源码深读完成”。

## 2. 分层架构建议

```text
┌────────────────────────────────────────────────────┐
│ Desktop / CLI / IDE / Web Task Center              │  借鉴 OpenCode 多端 + OMC HUD
├────────────────────────────────────────────────────┤
│ Workflow & Artifact Protocol                       │  OpenSpec + Superpowers
│ proposal/spec/design/task/checkpoint/evidence      │
├────────────────────────────────────────────────────┤
│ Orchestrator                                       │  OMO + OMC
│ intent gate / single loop owner / team state       │
├────────────────────────────────────────────────────┤
│ DeepSeek V4-native Harness                         │
│ cache layout / Flash-Pro router / reasoning policy │
├────────────────────────────────────────────────────┤
│ Tool & Safety Runtime                              │  OpenCode permissions + OMO hash edit
│ permission / sandbox / worktree / LSP / MCP        │
├────────────────────────────────────────────────────┤
│ Session / Event / Evidence Store                   │
└────────────────────────────────────────────────────┘
```

## 3. 能力对比矩阵

| 能力 | OpenCode | OMO | OMC | OpenSpec | Superpowers | DeepSeek Agent 决策 |
|---|---:|---:|---:|---:|---:|---|
| 核心 Agent runtime | 强 | 依赖宿主 | 依赖 Claude/CLI | 无 | 无 | 优先评估 OpenCode fork |
| 多端产品 | 强 | 弱 | CLI/plugin | 无 | 多宿主安装 | runtime 与 UI 解耦 |
| 多 Agent 编排 | 中 | 强 | 强 | 无 | 中 | 单一 loop owner + 持久 team state |
| 需求/设计 artifact | 弱 | 中 | 中 | 强 | 中 | 兼容 OpenSpec，绑定 runtime evidence |
| 工程纪律 | 中 | 强 | 强 | 中 | 强 | Superpowers 默认技能包 |
| 权限/安全 | 强 | 依赖宿主 | 依赖宿主 | 无 | worktree | OpenCode 权限模型 + 风险策略 |
| 编辑可靠性 | 中 | hash edit 强 | 依赖宿主 | 无 | 流程约束 | hash/version-anchored edit 原生化 |
| 验证/完成证据 | 中 | continuation 强 | verify/fix 强 | verify 较轻 | 强 | evidence ledger + Pro reviewer |
| DeepSeek 缓存原生 | 无证据 | 无 | 无 | 间接有利 | 间接有利 | 必须自研核心差异化 |
| Flash/Pro 原生路由 | 无 | 模型匹配 | smart routing | 无 | 无 | 必须自研策略路由 |

## 4. DeepSeek Agent 应形成的核心闭环

### 4.1 从需求到完成

```text
IntentGate
  → Spec/Design artifacts
  → executable plan
  → checkpointed execution
  → deterministic verification
  → Pro review when risk/uncertainty requires
  → archive decision + reusable memory
```

### 4.2 V4-native 路由

- **Flash**：代码探索、普通工具调用、小任务执行、并行 worker；
- **Thinking**：需求澄清、复杂调试、失败根因分析；
- **Pro**：架构决策、高风险 patch、关键 checkpoint、最终 review；
- **Max/长上下文模式**：跨仓库综合、超大 evidence synthesis，按需启用；
- 路由依据必须包含任务风险、失败次数、不确定度、上下文规模、cache miss 成本与用户 SLA。

### 4.3 Cache-first 上下文布局

```text
稳定前缀：系统规则 / 项目规则 / 当前 change 的批准 spec / 工具契约
追加证据：决策、checkpoint、测试结果、review verdict
活跃工作集：当前 task、相关文件片段、最近工具反馈
外部索引：历史会话、归档 change、子 Agent 全量轨迹
```

OpenSpec 和分层 AGENTS.md 提供稳定可寻址内容；后台 Agent/fresh subagent 隔离噪声；compaction 只应压缩非稳定、非证据内容；每次布局变化需记录 cache telemetry。

## 5. 建议优先级

### P0：MVP 必须具备

1. OpenCode 底座可 fork/可适配性 Spike；
2. DeepSeek provider + DSML/tool calling + reasoning_content policy；
3. Flash/Pro/Thinking 策略路由器；
4. OpenSpec-compatible change artifacts；
5. checkpoint/evidence ledger；
6. ask/allow/deny 权限与 isolated worktree；
7. hash/version-anchored edit；
8. verify-before-complete 与 Pro review gate；
9. 单一 loop authority；
10. cache hit/miss、成本、路由与阶段可视化。

### P1：增强能力

- background research agents 与 child session task tree；
- Team pipeline 与并行 worker；
- Deep Interview/IntentGate；
- LSP/AST-Grep/skill-embedded MCP；
- skills marketplace 与 schema bundles；
- archive→经验提取与检索。

### P2：谨慎后置

- 默认无限 continuation/Ralph loop；
- 大量隐式 hooks；
- tmux 作为桌面产品核心；
- 未验证的自动模型路由与“节省 token”承诺；
- 默认开启遥测。

## 6. 关键 ADR 候选

| ADR | 建议决策 |
|---|---|
| Runtime 底座 | 先用 OpenCode 做 fork Spike，再与自研成本比较，不立即承诺正式 fork |
| Workflow 协议 | 兼容 OpenSpec，但扩展 checkpoint/evidence schema |
| 编排控制 | runtime 强制单一 loop owner，team/qa/persistence 都是可替换策略 |
| Skills | 借鉴 Superpowers，流程强制尽量由状态机/权限实现而非只靠 prompt |
| 编辑 | 所有写操作使用文件版本/hash 保护；冲突自动重读与重新规划 |
| 审查 | spec compliance 与 code quality 分离；高风险 checkpoint 使用 Pro |
| 上下文 | 稳定前缀 + active set + 外部 evidence index；禁止无界轨迹常驻 |
| 遥测 | 默认本地可见；任何上传需显式 opt-in 与事件 schema |

## 7. 下一轮源码审计计划

1. **OpenCode Pass 2**：`packages/opencode` Agent loop、session/message、provider、tool、compaction、server、desktop。
2. **OMO Pass 2**：hook registry/顺序、hash edit、background agent、compaction、ulw-loop、team tools。
3. **OMC Pass 2**：team state machine、CLI/native bridge、worker/worktree、evidence artifact、HUD。
4. **OpenSpec Pass 2**：artifact graph/schema、adapter generation、verify/archive、并发 change。
5. **Superpowers Pass 2**：skill trigger/installation、workflow tests、两阶段 review、completion verification。
6. 建立统一 prototype benchmark：同一真实仓库任务分别测试基础 Harness 与吸收机制后的成功率、成本、cache hit、返工次数和人工干预。

## 8. 待验证问题

- OpenCode 是否能在不大规模 fork 的前提下实现 V4-native context layout？
- 插件层能否可靠控制消息构建、reasoning_content 与缓存前缀？
- artifact 与 runtime event 如何保持双向一致且不制造文档负担？
- 多 Agent 并行的收益是否高于额外 token、冲突与审查成本？
- “强制流程”如何按任务风险自适应，而不是成为固定仪式？
