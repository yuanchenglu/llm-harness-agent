# 07. 计划资产

本目录保存可执行计划资产，用于后续 AI 或工程执行者接手。它不是 PRD、OpenSpec 或 release gate 的替代品。

## 使用边界

确定：

- PRD TechPlan 说明产品方向、范围、架构和 release gate。
- OpenSpec 说明具体变更的 proposal、design、spec 和 tasks。
- 本目录保存跨阶段计划资产，重点是目标、事实依据、关键决策、非目标、执行步骤、验证命令和完成定义。

因此，执行具体变更前仍应按仓库规则创建或同步 OpenSpec；判断阶段状态仍应回到 `stage-gates.json` 和验证命令。

## 阅读顺序

1. [Runtime Kernel 发布与补丁计划](01-runtime-kernel-release-and-patch-plan.md)
2. [DeepSeekAgent 产品化路线计划](02-deepseekagent-productization-roadmap-plan.md)
3. [Desktop Code Workbench 首片计划](03-desktop-code-workbench-first-slice-plan.md)

## 维护规则

- 已完成事实和待做计划必须分开写。
- 只保留当前有效计划，不收录逐字对话。
- 不收录过时中间判断、不采用的视觉草稿或未验证口号。
- 每份计划必须能独立交给较弱 AI 执行，并包含明确验证命令。

