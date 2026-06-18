# 07. 计划资产

本目录保存可执行计划资产，用于后续 AI 或工程执行者接手。它不是 PRD、OpenSpec 或 release gate 的替代品。

## 使用边界

确定：

- PRD TechPlan 说明产品方向、范围、架构和 release gate。
- OpenSpec 说明具体变更的 proposal、design、spec 和 tasks。
- 本目录保存跨阶段计划资产，重点是目标、事实依据、关键决策、非目标、执行步骤、验证命令和完成定义。

因此，执行具体变更前仍应按仓库规则创建或同步 OpenSpec；判断阶段状态仍应回到 `stage-gates.json` 和验证命令。

## 写作标准

所有新计划必须先读：

- [计划资产写作标准](00-plan-asset-writing-standard.md)

后续只要新增计划，都必须在文件前部加入 `AI 执行提示词`，用于锁定后续 AI 的角色、规则、技能、思维方式和前置背景。

## 阅读顺序

## 当前状态快照

确定：

| 计划线 | 当前状态 | 正确执行入口 |
| --- | --- | --- |
| Runtime kernel | `v0.1.1-alpha.0` 与 `v0.1.1-alpha.1` 已发布记录在本目录。 | 后续只做 runtime patch 计划，不重复抽取。 |
| `0.1.x` Public Alpha | release gate 已关闭，作为历史归档和补丁参考。 | 新 public CLI 行为改动必须另开 OpenSpec。 |
| `0.2.x` Desktop Code Workbench | 首片和 hardening 已完成并归档：`2026-06-08-start-desktop-code-workbench`、`2026-06-09-harden-desktop-code-workbench`。 | 后续只做明确 patch，不把新工作塞回旧 change。 |
| `0.3.x` General Workspace Agent | 已实现并归档：`2026-06-09-start-general-workspace-agent`；主规格在 `openspec/specs/general-workspace-agent/spec.md`。 | 后续只做 patch。 |
| `0.4.x` Integrations And Automation Preview | 已实现并归档：`2026-06-17-start-integrations-automation-preview`；主规格在 `openspec/specs/integrations-automation-preview/spec.md`。 | 后续只做 patch，不把新工作塞回旧 change。 |
| `1.0` Stable Public Release | 已实现并归档：`2026-06-18-refresh-consumer-desktop-ui`、`2026-06-18-prepare-stable-public-release`；主规格在 `openspec/specs/consumer-desktop-ui/spec.md` 与 `openspec/specs/stable-public-release/spec.md`。 | 剩余是 commit / tag / remote release notes；新功能必须另开 OpenSpec。 |

### 基础规则

1. [计划资产写作标准](00-plan-asset-writing-standard.md)

### 已完成或历史归档计划

2. [Runtime Kernel 发布与补丁计划](01-runtime-kernel-release-and-patch-plan.md)
3. [DeepSeekAgent 产品化路线计划](02-deepseekagent-productization-roadmap-plan.md)
4. [Desktop Code Workbench 首片计划](03-desktop-code-workbench-first-slice-plan.md)
5. [`0.1.x` Public Alpha Release Gate 归档计划](04-0-1-x-public-alpha-release-gate-archive-plan.md)
6. [PRD TechPlan 分层归档计划](05-prd-tech-plan-layered-archive-plan.md)
7. [OpenSpec 工作流与 Artifact Gate 归档计划](06-openspec-workflow-bootstrap-plan.md)
8. [`0.2.x` Desktop Code Workbench 版本研发计划](07-0-2-x-desktop-code-workbench-version-plan.md)
9. [`0.3.x` General Workspace Agent 版本研发计划](08-0-3-x-general-workspace-agent-version-plan.md)
10. [`0.4.x` Integrations And Automation Preview 版本研发计划](09-0-4-x-integrations-and-automation-preview-plan.md)

### 当前与后续版本研发计划

11. [`1.0` Stable Public Release 版本研发计划](10-1-0-stable-public-release-plan.md)

## 维护规则

- 已完成事实和待做计划必须分开写。
- 只保留当前有效计划，不收录逐字对话。
- 不收录过时中间判断、不采用的视觉草稿或未验证口号。
- 每份计划必须能独立交给较弱 AI 执行，并包含明确验证命令。
- 每份新计划必须包含：目标、事实依据、关键决策、非目标、实施步骤、验证命令、完成定义。
- 具体实施仍应走 OpenSpec；计划资产只负责跨阶段交接和可执行说明。
