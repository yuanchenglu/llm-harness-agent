# 04. 版本路线与 Release Gates

## 1. 当前阶段真相

当前状态以仓库根目录 [`STATUS.md`](../../STATUS.md) 和 [`stage-gates.json`](../blueprint/stage-gates.json) 为准。

确定：

- Stage 0–5 已完成。
- Stage 6 research MVP 已完成。
- 当前知识库没有足够的不可变外部证据证明 Production Release Gate 已关闭。
- 产品发布状态是 `unverified_in_this_repository`。
- 最早未完成项是 `6-release-evidence-reconciliation`。

这不等于否认外部 Runtime 工作区可能已经实现部分或全部能力。它只表示：在实际 Runtime 仓库、固定 commit、tag、artifact、checksum、平台矩阵和发布报告被登记前，本仓库不能把生产发布写成已完成。

## 2. 状态语义

| 状态 | 含义 | 可否对外宣称已发布 |
| --- | --- | --- |
| `planned` | 只有需求、设计或任务计划 | 否 |
| `implemented_in_external_workspace` | 外部或本地工作区有实现记录，但本仓库缺少不可变映射 | 否 |
| `research_mvp_completed` | 研究型实现和受控任务验证已完成 | 否 |
| `release_candidate_verified` | 固定 commit、完整 Gate 和候选 artifact 已通过 | 只能宣称 RC |
| `verified_released` | 远端 tag、release notes、artifact、checksum 和发布决策可复核 | 是 |
| `blocked` | 关键 Gate 未通过 | 否 |
| `waived_with_reason` | 明确延期，并记录风险、负责人和后续处理 | 只能按豁免范围描述 |

“OpenSpec 已归档”“计划已完成”“本地 smoke 通过”都不是 `verified_released` 的同义词。

## 3. 路线原则

- 对外版本少，内部迭代快。
- 每条 release line 只承担一个用户价值闭环。
- 共享 Runtime 底座不在每个版本重复铺开。
- DeepSeek 特性只能在固定源码、公共协议或端到端实验支持后进入 Gate。
- 完成率优先于单次 Token 最低；成本按每个可验证成功任务计算。
- 正确性、安全、权限、Evidence 和恢复能力优先于 Prefix Cache 命中。
- 团队、生态和企业能力必须由真实用户证据牵引。
- 计划状态、实现状态、验证状态和发布状态必须分开记录。

## 4. Release Lines

### 4.1 `0.1.x` Public Alpha

**目标**：把 research MVP 收敛成可公开试用的 CLI-first 产品。

必须具备：

- CLI install / uninstall / doctor；
- DeepSeek provider adapter；
- permission / sandbox / changeset / rollback；
- checkpoint / resume；
- evidence / usage / cache / cost；
- README / release artifact / compatibility matrix。

Gate：

- 从干净环境完成 install、first task、uninstall；
- 只读任务有来源证据；
- 写入任务有 diff、approval、stale-hash protection 和 rollback；
- route、cache、usage、cost 可见；
- 确定性任务集报告首次成功率、重试后成功率、失败样本、人工介入和每成功任务成本；
- artifact、manifest 和 checksum 可复核。

**当前知识库状态**：研究证据存在，但远端 Public Alpha release 证据尚未在本仓库完成对账。

### 4.2 `0.2.x` Desktop Code Workbench

**目标**：把唯一 Runtime 接到桌面 UI，形成可信的本地 Code 工作台。

必须具备：

- desktop shell；
- workspace chooser；
- Task Center / Task Detail；
- Agent / Code 双模式入口；
- diff review / approval UI；
- checkpoint / evidence / cost 可视化；
- local runtime manager。

Gate：

- Desktop 通过 local runtime bridge 启动任务；
- UI 不拼 Prompt、不直接写文件、不伪造 Runtime 状态；
- approval / diff / rollback 与 CLI 语义一致；
- Task Detail 展示完成证据、未验证项、人工接管和 cost per successful task；
- Runtime crash、SSE disconnect 和 bridge restart 有可见恢复路径；
- Desktop build、test、E2E 和安装包证据映射到固定 commit。

**当前知识库状态**：历史计划记录过外部工作区实现与归档，仍需固定实现仓库和发布证据。

### 4.3 `0.3.x` General Workspace Agent

**目标**：从代码工作台扩展到通用本地工作台。

必须具备：

- 文件夹总结和多文档报告；
- artifact manager；
- Project Memory；
- Skill index / body separation；
- PlanGraph；
- Review Gate。

Gate：

- Artifact 有来源引用和内容 Hash；
- Memory 可确认、编辑、禁用、删除；
- Skill 有来源、版本、权限、测试、审批和回滚；
- PlanStep 可持久化、恢复并关联 Evidence；
- 长期任务报告完成率、恢复结果、人工接管和成本；
- Checkpoint 摘要可追溯到原始 diff、测试和工具证据。

**当前知识库状态**：规格和历史归档记录存在，实际实现状态待与 Runtime 仓库对账。

### 4.4 `0.4.x` Integrations and Automation Preview

**目标**：在本地工作台、Memory / Skill 和 PlanGraph 成立后，安全接入 MCP、外部工具、定时任务和轻量审批。

必须具备：

- MCP client 和 local tool catalog；
- tool schema fingerprint 和 drift detection；
- tool permission profiles 和 health check；
- local scheduled tasks；
- notification bridge；
- remote approval for pre-generated actions；
- automation audit log；
- Runtime 与宿主桥接协议。

Gate：

- MCP connection test；
- tool risk / drift tests；
- schedule trigger audit；
- remote approval token tests；
- tool context / evidence checks；
- 自动化任务报告 completion evidence、approval intervention 和每成功任务成本；
- 无审批自动副作用必须被 Runtime 拒绝；
- 宿主桥接集成测试无静默回退。

**当前知识库状态**：历史文档记录 `2026-06-17` 外部工作区实现与 OpenSpec 归档，但本仓库未登记对应实现 commit，因此状态不是可验证发布。

### 4.5 `1.0` Stable Public Release

**目标**：形成真正面向公开用户、可以安装、理解、诊断、升级、回滚和卸载的稳定产品。

必须具备：

- Public README / Quick Start / Troubleshooting；
- release artifact manifest 和 checksum；
- install / upgrade / uninstall smoke；
- config migration；
- local diagnostics bundle；
- privacy / security / permission 文档；
- issue template / security policy / contributing guide；
- 明确的平台兼容矩阵；
- 远端 tag、release notes 和 production release decision。

Gate：

- prior gates 已通过，或未通过项有明确 blocker / 延期豁免；
- public install 通过；
- migration / rollback tests 通过；
- build manifest + checksum verification 通过；
- diagnostics redaction tests 通过；
- route / cache / evidence smoke 通过；
- E4-style 真实任务报告可验证首次成功率、重试后成功率、失败样本、人工接管和每成功任务 Token / Cost；
- 实际 Runtime 仓库、commit、tag 和 artifact 之间可双向追溯。

**当前知识库状态**：`unverified_in_this_repository`。历史计划称某个工作区已完成收口，但同时明确远端 commit、tag 和 release 仍需执行，因此不能据此关闭 Gate。

## 5. Production Release Evidence Contract

关闭 Gate 时，`stage-gates.json.product_release.evidence` 至少登记以下类型：

```text
runtime_repository_url
runtime_commit_sha
release_tag
release_notes
artifact_manifest
artifact_checksum
platform_compatibility_matrix
install_upgrade_uninstall_report
rollback_report
diagnostics_redaction_report
E4_style_release_report
production_release_decision
```

证据要求：

- URL 指向可访问的固定资源，而不是本地路径；
- commit 使用完整 SHA；
- artifact 使用版本化文件名；
- checksum 使用 SHA-256 或等价完整性算法；
- 报告包含生成时间、运行环境、命令、结果和限制；
- 不提交 API Key、Authorization、原始私有 Prompt、完整 CoT 或未授权文件正文。

## 6. 全局禁止的伪完成

- 只在开发机能运行，没有安装链路；
- 只有计划或 OpenSpec archive，没有实现 commit；
- 只输出自然语言总结，没有 Evidence；
- 只列出工具但不能安全调用；
- Token 或成本下降，但任务成功率、正确性、安全或恢复能力下降；
- 自动化绕过 approval；
- Approval 后工作区已变化，仍继续应用旧 Diff；
- 诊断包泄露 Secret；
- UI 隐藏 route / cache / usage / permission；
- 文档只覆盖 happy path；
- 使用开发集反复调参后的 20/20，宣称为未见任务的泛化成功率；
- 用本地未提交工作区描述代替远端 release。

## 7. 当前执行顺序

1. 确认实际 Runtime / Desktop / OpenSpec 仓库。
2. 固定实现 commit、版本和依赖锁。
3. 将历史 `0.1.x`–`1.0` 计划映射到真实文件、测试和 OpenSpec。
4. 跑 install、upgrade、uninstall、rollback、diagnostics redaction 和平台矩阵。
5. 生成 E4-style 发布报告，严格分离首次成功和重试后成功。
6. 构建候选 artifact、manifest 和 checksum。
7. 创建远端 tag、release notes，并记录 production release decision。
8. 同步 `STATUS.md`、`stage-gates.json`、PRD TechPlan 和 Blueprint 入口。
9. 只有机器校验通过后，才能把 `product_release.status` 改为 `verified_released`。
