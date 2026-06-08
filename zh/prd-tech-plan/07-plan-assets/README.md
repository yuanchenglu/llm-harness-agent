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

### 基础规则

1. [计划资产写作标准](00-plan-asset-writing-standard.md)

### 已完成或历史归档计划

2. [Runtime Kernel 发布与补丁计划](01-runtime-kernel-release-and-patch-plan.md)
3. [DeepSeekAgent 产品化路线计划](02-deepseekagent-productization-roadmap-plan.md)
4. [`0.1.x` Public Alpha Release Gate 归档计划](04-0-1-x-public-alpha-release-gate-archive-plan.md)
5. [PRD TechPlan 分层归档计划](05-prd-tech-plan-layered-archive-plan.md)
6. [OpenSpec 工作流与 Artifact Gate 归档计划](06-openspec-workflow-bootstrap-plan.md)

### 当前与后续版本研发计划

7. [Desktop Code Workbench 首片计划](03-desktop-code-workbench-first-slice-plan.md)
8. [`0.2.x` Desktop Code Workbench 版本研发计划](07-0-2-x-desktop-code-workbench-version-plan.md)
9. [`0.3.x` General Workspace Agent 版本研发计划](08-0-3-x-general-workspace-agent-version-plan.md)
10. [`0.4.x` Integrations And Automation Preview 版本研发计划](09-0-4-x-integrations-and-automation-preview-plan.md)
11. [`1.0` Stable Public Release 版本研发计划](10-1-0-stable-public-release-plan.md)

## 维护规则

- 已完成事实和待做计划必须分开写。
- 只保留当前有效计划，不收录逐字对话。
- 不收录过时中间判断、不采用的视觉草稿或未验证口号。
- 每份计划必须能独立交给较弱 AI 执行，并包含明确验证命令。
- 每份新计划必须包含：目标、事实依据、关键决策、非目标、实施步骤、验证命令、完成定义。
- 具体实施仍应走 OpenSpec；计划资产只负责跨阶段交接和可执行说明。
