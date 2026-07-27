# 项目状态真源

> 最近核对：2026-07-27  
> 适用仓库：`yuanchenglu/llm-harness-agent`  
> 机器可读状态：[`zh/blueprint/stage-gates.json`](zh/blueprint/stage-gates.json)

## 1. 本仓库是什么

本仓库是 Agent Harness 的研究、产品规格、架构决策和实验摘要知识库，不是当前 DeepSeekAgent Runtime 的完整可执行代码仓库。

因此必须区分两类状态：

1. **研究与文档阶段状态**：由本仓库内的固定来源、审计文档、实验摘要和规格完整性决定。
2. **产品发布状态**：必须由实际 Runtime 仓库中的固定 commit、测试报告、平台兼容矩阵、远端 tag、release artifact 和 checksum 共同证明。

本仓库不能仅凭计划文档或某个未提交工作区的描述，宣布生产发布完成。

## 2. 当前确定状态

| 范围 | 状态 | 说明 |
| --- | --- | --- |
| Stage 0–5 | `completed` | 项目总纲、模型事实、竞品调研、协议实验、架构和 PRD 规格已经形成可用文档资产。 |
| Stage 6 研究 MVP | `completed` | 已有 E3/E4 摘要、安全写入、回滚和恢复等研究证据。 |
| Production Release Gate | `unverified_in_this_repository` | 本仓库缺少实际 Runtime 的固定仓库/commit、远端 release tag、可下载 artifact、checksum 和完整平台矩阵。 |
| 最早未完成项 | `6-release-evidence-reconciliation` | 先把外部实现证据映射回本仓库，再决定 Gate 是关闭、延期还是重新打开。 |

## 3. 关闭 Production Release Gate 的最低证据

必须同时提供：

- 实际 Runtime 仓库 URL 与不可变 commit SHA；
- 对应版本 tag 与 release notes；
- release artifact 下载记录与 SHA-256 或等价完整性校验；
- macOS、Windows、Linux 的支持/不支持矩阵和验证结果；
- install、upgrade、uninstall、rollback、diagnostics redaction 测试报告；
- E4-style 任务报告，至少区分首次成功率、重试后成功率、人工介入和失败样本；
- 明确的 production release decision。

缺少任一关键项时，状态只能写成 `unverified`、`blocked` 或 `waived_with_reason`，不能写成 `completed`。

## 4. 状态优先级

发生冲突时，按以下顺序裁决：

1. 实际 Runtime 固定 commit、测试结果、tag、artifact 和 checksum；
2. `zh/blueprint/stage-gates.json`；
3. 本文件；
4. 当前 PRD TechPlan；
5. 历史计划、交接 README 和归档文档。

历史文档中的“已完成”“已关闭”只代表当时记录，不自动升级为当前事实。

## 5. 下一步

1. 确认实际承载 Runtime、Desktop、OpenSpec 和 release scripts 的仓库。
2. 固定对应 commit/tag，补齐证据索引。
3. 运行发布 Gate 验证并提交机器可读结果。
4. 同步更新 `stage-gates.json`、本文件、PRD TechPlan 和 Blueprint README。

在上述工作完成前，本仓库继续作为研究与产品知识库维护，不对外宣称生产版本已经完成发布。
