# 6-1 DeepSeek Agent 生产 PRD 与桌面双模式 UX

> 版本：2026-06-05 production candidate。本文定义生产产品范围与交互完成标准；底座、Router 和 Cache ROI 的最终参数仍以 Stage 3/4 ADR 为准。

## 1. 产品定义

DeepSeek Agent 是面向本地代码仓库的 evidence-first 编程 Agent。它把 DeepSeek V4 的协议、cache usage 和成本暴露为可审计事实，并在任何副作用前提供权限判断、变更预览、checkpoint 与可回滚执行。

### 目标用户

| 用户 | 核心任务 | 当前痛点 | 产品价值 |
|---|---|---|---|
| 个人开发者 | 修 bug、加测试、小重构 | Agent 行为不可见、失败难恢复 | 默认安全、成本可见、失败可继续 |
| 工程团队 | 委派中风险代码任务 | 缺统一权限、证据和验收 | 可审计任务、确定性验收、可复盘 |
| Harness 研究者 | 验证模型/协议/缓存 | 实验难复现、结论越级 | 固定 manifest、脱敏 trace、证据等级 |

### Jobs-to-be-Done

1. 当我委派一个代码任务时，我要先看到计划、风险与预计成本，再决定是否执行。
2. 当 Agent 请求写文件、shell、网络或 Git 操作时，我要明确知道影响面并能允许、拒绝或限定范围。
3. 当任务中断、失败或超预算时，我要从 checkpoint 继续，而不是重复副作用或重新开始。
4. 当 Agent 声称完成时，我要看到 diff、测试、验收器和证据，而不是只看到自然语言结论。
5. 当我比较 Flash/Pro、当前 runtime 与 OpenCode Adapter 时，我要使用同一任务、预算和验收器。

## 2. 产品边界

### P0 生产范围

- macOS / Windows 桌面任务中心；
- CLI 作为脚本化与恢复入口；
- Agent Mode 与 Code Mode；
- 本地单仓库 workspace；
- DeepSeek V4 Flash / Pro；
- 只读探索、受控 ChangeSet、受控 shell；
- permission policy、sandbox、diff preview、apply、rollback；
- session/checkpoint/resume；
- evidence ledger、usage/cache/cost 展示；
- 确定性验收器与发布 Gate。

### 非目标

- 默认无限自主循环；
- 默认网络访问、自动提交或自动 push；
- 把模型 CoT 作为产品日志；
- 无验收器的“自动完成”；
- 在无 E4 数据时承诺自动 Router、planner/reviewer 提升；
- 用 Cache 命中率覆盖正确性或安全要求；
- 多租户云执行与企业权限中心，后置到 P1/P2。

## 3. 双模式

### Agent Mode

适合目标明确但路径未知的任务。Agent 可探索、形成计划、提出 ChangeSet、请求审批、执行验收并恢复失败。

状态机：

```text
Draft → Inspecting → Planned → Awaiting Approval
→ Applying → Verifying → Completed
                    └→ Failed → Recovering → Planned/Applying/Verifying
                    └→ Rolled Back
```

硬约束：

- 未批准的副作用不能执行；
- 已成功副作用 resume 时不能重复；
- `Completed` 必须绑定至少一个验收结果；
- 超预算、协议不确定或高风险操作自动停在 checkpoint。

### Code Mode

适合用户主导的精确编辑。用户选择文件/范围，Agent 提议 patch；产品默认不自行扩展范围。

状态机：

```text
Selection → Proposal → Diff Review → Apply/Reject → Verify → Done/Rollback
```

硬约束：

- patch 必须带 original hash；
- stale hash 必须重新读取并重新提议；
- 默认只修改选中范围；
- apply 前始终展示 diff 和权限决策。

## 4. 信息架构

```text
Workspace
├── Task Center
│   ├── Active / Awaiting Approval / Failed / Completed
│   └── task risk, model, budget, progress, checkpoint
├── Task Detail
│   ├── Plan & Scope
│   ├── Conversation
│   ├── Changes
│   ├── Verification
│   └── Evidence
├── Code Mode
│   ├── File/selection context
│   ├── Proposed diff
│   └── Apply / Reject / Rollback
├── Policy Center
│   ├── workspace rules
│   ├── command/path rules
│   └── audit history
└── Benchmarks
    ├── E3 protocol/cache
    └── E4 task comparison
```

## 5. 核心交互

### 5.1 新建任务

输入：目标、workspace、模式、预算、允许工具。  
系统预检：仓库状态、风险、模型 capability、预计请求/成本、可用验收器。  
成功标准：用户在执行前能看到范围、非目标、最大步骤、权限边界与停止条件。

### 5.2 权限请求

权限卡必须显示：

| 字段 | 要求 |
|---|---|
| action | read/write/delete/shell-safe/shell-dangerous/network/git-mutating |
| target | 规范化路径或参数数组命令 |
| reason | 与当前 task/plan step 的关系 |
| impact | 修改/删除/网络/Git 影响 |
| decision | Allow once / Allow scoped / Ask / Deny |
| audit | 决策时间、规则来源、调用 ID |

默认策略：read allow；所有副作用 deny，除非显式规则或批准。

### 5.3 Diff 与 ChangeSet

- 展示文件级和行级 diff；
- 显示 original hash、当前 hash 与 stale 状态；
- 可按文件批准/拒绝；
- apply 后立即生成 rollback token；
- 多文件 apply 任一步失败时回滚已应用项；
- 用户可从任务详情执行显式 rollback。

### 5.4 Checkpoint 与恢复

- 顶部持续显示最近 checkpoint；
- 中断后打开任务，先展示恢复计划；
- 已成功副作用显示 `skip`；
- pending/running/failed 显示 `execute/retry/review`；
- corrupt 或未知 schema 不自动修复，进入诊断页；
- 恢复前可回滚到任一安全 checkpoint。

### 5.5 验证与完成

完成页必须显示：

- 需求/任务验收器；
- 测试命令、退出码和结构化结果；
- changed paths 与 diff hash；
- 权限、rollback、错误工具调用；
- token/cache/cost（可用时）；
- 未验证项、限制与人工确认。

没有确定性验收器时只能标为 `Needs Review`，不能标 `Completed`。

### 5.6 Cache / Cost 可见性

- 每个请求显示 hit/miss/output token 与价格快照；
- UI 明确写“best-effort cache”；
- cache miss 不作为错误；
- policy/context 必要变化时展示“正确性优先，主动失效”；
- 不展示或保存完整 CoT。

## 6. 失败恢复 UX

| 失败 | 用户看到 | 系统动作 | 用户选项 |
|---|---|---|---|
| API 4xx capability | 字段/模式不兼容 | 停在请求前后 checkpoint | 修改模式、重试、终止 |
| API 429/5xx/timeout | 外部服务失败 | 不重复副作用；记录 error class | 延迟重试、切模型、终止 |
| stale patch | 文件已变化 | 阻止 apply | 重读重提、放弃 |
| test failure | 验收未通过 | 保持未完成 | 修复、rollback、人工接管 |
| permission denied | 操作被阻止 | 保持 task 状态 | 改计划、局部授权、终止 |
| corrupt checkpoint | 无法安全恢复 | 拒绝自动执行 | 导出诊断、从早期 checkpoint 恢复 |
| budget exceeded | 达到硬上限 | 停止新请求 | 增加预算、降级模式、终止 |

## 7. 指标与 SLO

### 产品指标

- 确定性任务成功率；
- 首次完成率；
- 测试通过率；
- 人工批准/拒绝/接管次数；
- rollback 与错误工具调用数；
- session 恢复成功率；
- 协议错误率；
- 每成功任务成本、延迟和 cache hit tokens。

### 安全与可靠性 SLO

- 未批准副作用执行数：0；
- workspace escape：0；
- 已成功副作用重复执行：0；
- API key / CoT 入 evidence：0；
- rollback 验证成功率：100%（支持范围内）；
- corrupt/未知 checkpoint 自动执行数：0。

## 8. PRD 验收

生产候选只有在以下全部成立时可发布：

1. 安全、恢复、协议、质量、底座与发布 Gate 全部通过；
2. 20–30 个 E4 任务可重置，验收器能区分正确/错误；
3. 当前 runtime 与 OpenCode Adapter 使用同一接口和任务；
4. Flash/Pro E3 bundle 可复算，unknown 明确保留；
5. 威胁模型、安装/卸载、兼容性和 rollback 文档完成；
6. README、manifest 与 `stage-gates.json` 一致。
