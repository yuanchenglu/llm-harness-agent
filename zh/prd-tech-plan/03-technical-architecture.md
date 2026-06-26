# 03. 技术架构

## 1. 架构目标

DeepSeekAgent 的架构目标不是追求新技术栈，而是把已经成立的 Python runtime foundation 产品化，并保持 DeepSeek-native、cache-disciplined、policy-enforced、evidence-first。

## 2. 总览

```text
CLI / Desktop / Automation
  -> Local Runtime API
  -> Orchestrator
  -> Policy / Sandbox / ChangeSet / Rollback
  -> Session / Checkpoint / Evidence
  -> Context Layout / DeepSeek Provider
  -> Local Event Log / Optional Index
```

桌面端、CLI、自动化入口都不能成为独立 agent loop。唯一真源在本地 runtime。

## 3. 推荐技术栈

| 层 | 推荐 | 置信度 | 说明 |
| --- | --- | --- | --- |
| CLI | Python CLI | 确定 | 贴合现有 runtime 与测试面 |
| Runtime core | Python | 大概率 85% | 当前阶段不要重写 |
| Provider / Router / Safety / Session | Python | 大概率 85% | 与 blueprint 证据链保持同面 |
| Runtime bridge | Local HTTP/SSE | 确定 | 让 CLI、desktop、未来桥接复用同一 runtime |
| Desktop UI | React + TypeScript | 确定 | 适合复杂状态、diff、审批、任务详情 |
| Desktop shell | Electron first | 大概率 80% | 优先交付稳定性；Tauri 后评估 |
| Evidence truth source | JSONL event log | 大概率 80% | 可审计、可导出、可回放 |
| Query index | SQLite optional | 大概率 80% | 用于产品查询和加速 |

## 4. 核心模块

### 4.1 CLI Layer

职责：

- 启动任务。
- 配置 API Key。
- 运行 doctor。
- 展示任务状态。
- 输出 evidence 和 diagnostics。

### 4.2 Runtime Core

职责：

- 维护任务状态机。
- 调度 planner / executor / reviewer。
- 管理 context layout。
- 执行 provider call。
- 记录 evidence events。

### 4.3 Safety Layer

职责：

- 管理 permission policy。
- 约束 filesystem / shell / tool access。
- 生成 changeset。
- 执行 approval gate。
- 创建 rollback point。

### 4.4 Provider Layer

职责：

- DeepSeek API 调用。
- route reason。
- Flash / Pro / thinking policy。
- cache hit/miss 记录。
- usage / cost 统计。

### 4.5 Desktop Bridge

职责：

- 暴露 local HTTP/SSE 或等价事件流。
- 传递任务事件、diff、approval request、usage、evidence。
- 接收用户审批和 UI actions。

禁止：

- UI 拼 prompt。
- UI 直接写文件。
- UI 绕过 policy。
- UI 自己维护任务真源状态。

## 5. DeepSeek 物理特性工程规则

### 5.1 1M context

大上下文不等于 history dump。必须使用 layout-driven context packing，并区分 stable prefix、constraints、working set、checkpoint summary、turn tail。

### 5.2 Prefix cache

`prompt_cache_hit_tokens` / `prompt_cache_miss_tokens` 必须进入 evidence、diagnostics 和 release gate。

要求：

- byte-stable prefix 是 runtime invariant。
- Memory / Skill / Tool catalog 不能随意破坏 prefix。
- prefix drift 必须可诊断。

### 5.3 Flash / Pro 路由

默认 Flash-first；在 checkpoint、风险审查、复杂计划判断时 Pro-on-checkpoint。

每次路由必须记录：

- selected model。
- route reason。
- risk level。
- fallback or retry。

### 5.4 Reasoning content

reasoning 内容默认用于 display/archive，不长期回灌 prompt。只有经明确摘要和布局规则处理后才能进入后续上下文。

## 6. Completion-per-token 闭环

架构优化目标不是单次请求 token 最低，而是每个可验证成功任务的 token / cost 更低，同时不降低正确性、安全和恢复能力。

闭环：

1. Context layout：稳定前缀承载项目规则、工具索引、Memory / Skill index 和安全约束；working set、checkpoint summary、turn tail 按任务变化。
2. Prefix cache：byte-stable prefix 保持 cache discipline，cache hit/miss、prefix drift 和主动失效原因进入 evidence。
3. Flash / Pro routing：Flash-first 执行低风险步骤，复杂计划、checkpoint、失败重试和高风险审查按 route reason 升级到 Pro。
4. Verifier feedback：任务不能靠模型自述完成；测试、确定性验收器、diff hash 和人工确认决定 retry、checkpoint 或 `Needs Review`。
5. Budget policy：请求预算、步骤预算和成本预算在发送前检查；超预算停在 checkpoint，而不是继续消耗 token。
6. Evidence ledger：每个任务结果记录 success、tests、tools、approval、rollback、step、duration、token、cache、cost 和限制。
7. Recovery：checkpoint / resume 避免重复副作用和重复上下文消耗，rollback 让失败任务可恢复。

不变量：如果 token 下降导致任务成功率、证据完整性、权限边界或 rollback 能力下降，该优化无效。

## 7. 数据对象

### Task

```text
id, workspace, objective, status, created_at, updated_at
```

### Session

```text
id, task_id, checkpoint_ids, event_log_ref, status
```

### ChangeSet

```text
id, task_id, files, diff, risk, approval_status, rollback_ref
```

### EvidenceEvent

```text
id, task_id, type, input_ref, tool_ref, output_ref, risk, usage, cache, created_at
```

### PlanStep

```text
id, parent_id, dependencies, objective, expected_result, status, risk, evidence_ids, checkpoint_id
```

### DiagnosticsBundle

```text
bundle_id, app_version, runtime_version, platform, config_summary, redacted_logs, event_refs, generated_at
```

## 8. Release-Critical Invariants

- Runtime 是唯一 agent loop。
- UI 不绕过 permission / sandbox / changeset / rollback。
- 所有写入先生成 diff preview。
- 高风险动作必须 approval。
- 每个任务必须有 evidence ledger。
- route / usage / cache / cost 必须可见。
- Context layout 不退回 history dump。
- 每成功任务 token / cost 只能在完成质量和安全边界不下降时作为优化指标。
- diagnostics bundle 不包含 API Key、secret token 或未授权文件正文。

## 9. 不推荐动作

- 现在把 runtime 重写成全 TypeScript。
- 现在为了轻量优先切 Tauri。
- 现在把手机连接、团队协作、企业治理压进主线。
- 在 release gate 未关闭时扩大产品面。
