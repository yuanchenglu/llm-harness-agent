# 6-3 生产研发拆解与可执行验收

> 版本：2026-06-05。估算使用工程日（eng-day），用于依赖与风险排序，不是交付承诺。机器可读 E4 任务见 `e4-task-catalog-2026-06-05.json`；mock 验收器自检见 `e4-mock-baseline-2026-06-05.json`。

## 1. 完成定义

每个 Story 完成必须同时满足：

1. 实现进入真实调用路径；
2. 正常与失败路径测试通过；
3. 证据/接口/文档同步；
4. 不降低默认安全策略；
5. 不把 mock、E1 或 E2 写成 E3/E4/E5；
6. `check_repo.py`、全量测试、compileall、diff check 和 secret scan 通过。

## 2. Epic 与依赖

| Epic | 目标 | 依赖 | 估算 | 主要风险 |
|---|---|---|---:|---|
| E1 Provider/E3 | capability-driven Flash/Pro adapter 与 evidence bundle | 无 | 8–12 | 服务变化、静默忽略 |
| E2 Safety | permission/sandbox/ChangeSet/rollback | 无 | 10–15 | 越权、并发覆盖 |
| E3 Recovery | session/checkpoint/resume | E2 action schema | 7–10 | 重复副作用 |
| E4 Benchmark | 20–30 任务、runner、验收器 | E2/E3 | 8–12 | 任务偏置、自证 |
| E5 Runtime Adapter | current/OpenCode 同接口 | E1/E2/E3 | 10–15 | 外部 runtime 控制力 |
| E6 Desktop/CLI | 双模式任务中心与审批 UX | E2/E3 APIs | 15–25 | UI 绕过 policy |
| E7 Observability | evidence/usage/cache/cost/diagnostics | E1/E3 | 7–10 | 隐私、指标误读 |
| E8 Release | 包装、兼容、安装/卸载、canary | 全部 | 8–12 | 环境漂移 |

## 3. 可执行 Stories

### E1 Provider / E3

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E1-S1 | 精确 wire hash 与结构化 request/response evidence | trace 无正文/CoT/Key，hash 可复算 | recorder tests + secret scan | 2 |
| E1-S2 | SSE stream 结构与 TTFT | Flash/Pro 5 次有 event/delta/usage/first-event | stream unit + E3 | 2 |
| E1-S3 | capability matrix | high/max/tool/strict/invalid/drop/replay 均有结论边界 | E3 bundle | 3 |
| E1-S4 | Prefix Cache matrix | exact/common/tool/schema/position/history/mode/order/concurrency/cross-time | E3 bundle | 4 |
| E1-S5 | 请求预算与停止条件 | 超请求上限不发送 | dry-run/guard test | 1 |

### E2 Safety

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E2-S1 | PermissionPolicy | read allow；副作用默认 deny；last matching rule | policy tests | 2 |
| E2-S2 | WorkspaceSandbox | 阻止 traversal/absolute/symlink escape | sandbox tests | 2 |
| E2-S3 | Shell runner | argv、cwd、timeout、output cap、network/danger classify | shell tests | 3 |
| E2-S4 | ChangeSet preview/apply | original hash、diff、批准后 apply | changeset tests | 3 |
| E2-S5 | rollback/audit | 中途失败自动恢复；显式 rollback；日志脱敏 | rollback/audit tests | 3 |

### E3 Recovery

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E3-S1 | versioned SessionState | 保存/加载、未知版本拒绝 | session tests | 2 |
| E3-S2 | atomic checkpoint | 中断不产生半文件 | checkpoint failure test | 2 |
| E3-S3 | idempotent resume | succeeded 副作用 skip | resume tests + CLI plan | 3 |
| E3-S4 | corrupt diagnostics | corrupt 不执行，给出稳定错误 | corrupt tests | 1 |

### E4 Benchmark

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E4-S1 | TaskSpec 与 20 个任务 | 覆盖十类任务；包含预算/范围/禁止行为 | catalog validation | 3 |
| E4-S2 | fixture reset | 任意运行后恢复干净基线 | reset test | 1 |
| E4-S3 | deterministic verifier | 正确实现通过，no-op/错误实现失败 | mock/no-op tests | 2 |
| E4-S4 | result schema | success/tests/tools/approval/rollback/step/duration/token/cache/cost | schema test | 2 |
| E4-S5 | fair adapter runner | 同模型/任务/预算/验收器，多次报告失败样本 | E4 comparison | 4 |

### E5 Runtime Adapter

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E5-S1 | RuntimeAdapter lifecycle | prepare/run/resume/evidence/cleanup | mock contract | 2 |
| E5-S2 | current runtime adapter | 使用 session/evidence/safety | contract + E4 | 3 |
| E5-S3 | OpenCode wrapper | 固定 commit/config，结构化 live evidence | mock + live probe | 4 |
| E5-S4 | Foundation ADR | 基于 E3/E4 与维护成本，可逆选择 | ADR review | 2 |

### E6 Desktop / CLI

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E6-S1 | Task Center | 状态/风险/预算/checkpoint 可见 | UI flow tests | 4 |
| E6-S2 | Agent Mode | 计划→审批→apply→verify→恢复 | E2E | 5 |
| E6-S3 | Code Mode | selection→proposal→diff→apply/rollback | E2E | 4 |
| E6-S4 | Policy Center | scoped allow/ask/deny 与 audit | UI/security E2E | 3 |
| E6-S5 | Benchmark viewer | E3/E4 evidence 与限制可读 | UI tests | 3 |

### E7/E8 Observability 与发布

| Story | 实现 | 验收 | 测试 | 估算 |
|---|---|---|---|---:|
| E7-S1 | Evidence Ledger | 结构化、脱敏、可索引 | evidence tests | 3 |
| E7-S2 | usage/cache/cost | 价格快照与 token 分项 | metric tests | 2 |
| E7-S3 | diagnostics/export | 可导出不含敏感字段的诊断包 | secret scan | 2 |
| E8-S1 | package/install/uninstall | 干净机可安装、卸载不删用户 checkpoint | smoke | 3 |
| E8-S2 | compatibility matrix | macOS/Windows/Python/adapter 固定版本 | CI/manual evidence | 3 |
| E8-S3 | canary/rollback | 版本回退与 adapter 禁用 | release drill | 3 |

## 4. E4 任务集

当前机器任务集包含 20 个任务：

| 类别 | 数量 |
|---|---:|
| single-file-bug | 4 |
| parameter-validation | 3 |
| add-test | 2 |
| cross-file-feature | 3 |
| call-chain-bug | 2 |
| small-refactor | 2 |
| checkpoint-resume | 1 |
| permission-recovery | 1 |
| stale-patch | 1 |
| test-failure-fix | 1 |

每个任务包含：ID、类别、难度、初始 fixture、用户需求、允许工具、风险预算、确定性验收、最大步骤、超时、预期修改范围和禁止行为。

Mock 自检规则：

- deterministic mock 必须 20/20；
- no-op baseline 必须 0/20；
- 该结果只证明 fixture 与 verifier 可判错，不是模型 E4 成绩；
- 模型/adapter E4 必须保留失败样本并多次运行。

## 5. 发布验收矩阵

| Gate | 必须证据 | 失败时 |
|---|---|---|
| 底座 | current/OpenCode 同任务 E4 + 维护成本 ADR | 保持可逆，不定稿 |
| 协议 | Flash/Pro E3 protocol + cache + cross-time bundle | 保留 unknown，不发布自动策略 |
| 安全 | permission/sandbox/diff/apply/rollback 全失败路径测试 | 禁止副作用 |
| 恢复 | checkpoint/resume 不重复副作用 | 禁止长任务生产使用 |
| 质量 | 20–30 E4 多次真实运行 | 只允许研究预览 |
| 发布 | threat model、secret scan、兼容、安装/卸载、rollback drill | 不发布 |

## 6. 当前可直接执行命令

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m deepseek_agent.e4 list
PYTHONPATH=src python -m deepseek_agent.e4 run-mock
PYTHONPATH=src python benchmarks/protocol/e3_matrix.py all --repeats 5 --dry-run
python scripts/check_repo.py
python -m compileall -q src tests benchmarks scripts
git diff --check
```
