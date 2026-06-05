# 14-0 OpenSpec 源码审计 Pass 1

> Pass 2 已于 2026-06-05 完成，固定 commit、运行路径、实测结果与校准结论见 [`18-0-五项目Pass2与统一证据矩阵`](./18-0-五项目Pass2与统一证据矩阵-Five-Project-Pass2-Uniform-Evidence-Matrix.md)。本文件保留为 Pass 1 历史输入；特别注意 OpenSpec 的 verify/complete 不等于项目测试已执行。

## 1. 目标与结论

OpenSpec 是跨 AI Coding Assistant 的轻量 Spec-Driven Development（SDD）框架。它不替代 Agent Runtime，而是在聊天历史与代码之间增加可版本化的 change artifact 层，使“为什么做、做什么、如何做、做到哪”不再只存在于易失的上下文中。

**核心判断：**OpenSpec 应成为 DeepSeek Agent 文档驱动与 checkpoint 体系的重要输入，但不能单独承担 runtime 状态、执行证据、权限和成本控制。最值得吸收的是 change folder、artifact graph、可迭代而非瀑布式流程、跨 25+ 工具适配器；最需要扩展的是机器可验证 evidence ledger 与 Agent 执行状态。

## 证据与状态说明

- 调研日期：2026-06-04。
- 证据优先级：官方源码仓库与官方文档为 A 级；基于目录、配置和公开行为的架构推断为 B 级，并明确标注为推断。
- 本报告状态：**源码审计 Pass 1**。已完成仓库结构扫描、关键机制定位、Model-Harness Fit 与迁移判断；尚未完成全仓逐文件/逐函数审计，因此不宣称“完整源码深读完成”。

## 2. 官方证据索引

| 证据 | 级别 | 支撑结论 |
|---|---|---|
| [官方仓库](https://github.com/Fission-AI/OpenSpec) | A | MIT、TypeScript、SDD、CLI 与 schema |
| [README](https://github.com/Fission-AI/OpenSpec#readme) | A | propose/apply/archive 主流程与 expanded workflow |
| [Concepts](https://openspec.dev/docs/concepts) | A | artifact-guided workflow 概念 |
| [Supported Tools](https://openspec.dev/docs/supported-tools) | A | 25+ Agent/工具适配 |
| [仓库 `src/`](https://github.com/Fission-AI/OpenSpec/tree/main/src) | A | CLI/runtime 实现入口 |
| [仓库 `schemas/`](https://github.com/Fission-AI/OpenSpec/tree/main/schemas) | A | schema 驱动扩展边界 |

## 3. Artifact 工作流

核心流程：

```text
/opsx:propose → proposal.md + specs/ + design.md + tasks.md
/opsx:apply   → 按 tasks 实现
/opsx:archive → 归档 change，并更新 specs
```

Expanded profile 还提供 `/opsx:new`、`continue`、`ff`、`verify`、`bulk-archive`、`onboard`。OpenSpec 的关键设计不是文件名本身，而是把一次变更变成独立目录和可持续更新的 artifact 集合。

```text
openspec/
  changes/<change-id>/
    proposal.md   为什么做、变化范围
    specs/        需求与场景
    design.md     技术方案
    tasks.md      实施清单
  changes/archive/<date>-<change-id>/
```

其理念明确强调 fluid not rigid、iterative not waterfall、brownfield first。换言之，artifact 是协作记忆，不是必须线性通过的官僚审批表。

## 4. Harness 价值

### 4.1 从聊天记忆转为项目记忆

OpenSpec 解决的是“需求只存在聊天历史里”的不可预测性。Artifact 可被 Git 版本化、review、diff、归档，并跨 session、跨模型、跨 Agent 保持稳定。这与 DeepSeek V4 1M context 并不冲突：大上下文不等于应把所有决策塞进上下文；可寻址 artifact 能显著降低重复输入与语义漂移。

### 4.2 工具无关适配层

OpenSpec 支持 25+ 工具，依赖各宿主的 slash command/skill 注入，而核心 change schema 保持一致。该模式可用于 DeepSeek Agent 的兼容策略：把稳定协议定义在 artifact/schema 层，客户端和第三方 Harness 只做 adapter。

### 4.3 上下文卫生

官方明确建议实施前清理上下文并维持 context hygiene。这说明 OpenSpec 的 artifact 并不自动解决上下文构建；它只提供可重新加载的外部记忆。DeepSeek Agent 仍需要决定何时加载 proposal/spec/design/task 的哪些片段。

## 5. Model-Harness Fit

| 维度 | OpenSpec 当前机制 | DeepSeek V4 适配判断 |
|---|---|---|
| 长上下文 | 外部化 proposal/spec/design/tasks | 降低主上下文常驻负担，利于 cache-first 布局 |
| 状态恢复 | change folder + archive | 强于纯聊天，但弱于 runtime checkpoint |
| 审查 | agree before build、verify 命令 | 可作为 Pro review 输入，需机器证据绑定 |
| 模型路由 | 工具无关，官方建议高推理模型 | 本身无动态 Flash/Pro 路由 |
| 工具协议 | 通过适配器生成命令/技能 | 不负责 DSML/tool runtime |
| 成本与缓存 | artifact 可复用 | 无 cache telemetry 与布局控制 |

## 6. 对 DeepSeek Agent 的迁移建议

### 建议采用“OpenSpec + Runtime Checkpoint”双层模型

```text
Design artifacts（人和 Agent 都可读）
  proposal / specs / design / tasks
          ↓ 绑定
Execution artifacts（机器可验证）
  checkpoint / diff / test result / tool trace / approval / cost / cache stats
```

1. 兼容 OpenSpec change folder，允许直接导入/导出。
2. 为每个 task 增加稳定 ID，并绑定 runtime checkpoint、commit、测试与 reviewer verdict。
3. 只将当前 task、相关 spec 片段和必要设计约束放入 active working set；其余通过检索按需加载。
4. proposal/spec/design 等稳定内容放入 byte-stable prefix，减少 cache miss。
5. archive 不只移动文档，还生成决策摘要、遗留风险和可检索经验。
6. 利用 schema bundle 思路开放 DeepSeek Agent workflow marketplace，但 schema 必须可验证、可版本化。

## 7. 风险与待验证问题

1. Artifact 之间的依赖图、完成状态和 schema 校验具体如何实现？
2. `/opsx:verify` 验证的是任务勾选、文档一致性，还是会运行测试并绑定证据？
3. 多 Agent 并行修改同一 change folder 时如何合并？
4. 轻量与灵活可能导致 artifact 漂移，如何自动检测 code/spec 不一致？
5. 适配器更新是否会覆写用户自定义命令或规则？
