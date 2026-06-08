# DeepSeekAgent PRD TechPlan

本文档包是 `llm-harness-agent` 从 0 到 1 开发过程的准确产品与技术存档。它不是旧草案堆，也不是给公开用户浏览的营销 README。

中文表达原则见：[中文表达与术语表](00-中文表达与术语表.md)。后续中文文档默认先用清楚中文解释项目含义，再保留必要技术术语、命令、文件名和证据字段。

## 当前判断

确定：

- Blueprint 已完成 Stage 0-5。
- Stage 6 的 research MVP 已完成。
- 当前没有最早未完成项。
- `production_release_gate` 已关闭。

因此本目录的主任务是把已有研究、PRD、UX、架构和验收线用于后续 Runtime Kernel 化和产品化推进，而不是重新定义项目地基。

## 文档结构

如果第一次阅读，建议先读：

1. [中文表达与术语表](00-中文表达与术语表.md)
2. [产品定位与范围](01-product-and-scope.md)
3. [PRD](02-prd.md)

按角色阅读：

| 读者 | 建议入口 | 读完应能回答 |
| --- | --- | --- |
| 产品 / 项目推进 | [中文表达与术语表](00-中文表达与术语表.md)、[产品定位与范围](01-product-and-scope.md)、[版本路线与 Release Gates](04-roadmap-and-release-gates.md) | 现在处于什么阶段，下一刀为什么是 release artifact。 |
| 工程执行 | [PRD](02-prd.md)、[技术架构](03-technical-architecture.md)、[版本路线与 Release Gates](04-roadmap-and-release-gates.md) | 哪些能力要做，哪些 gate 必须验证。 |
| 设计 / 原型 | [产品定位与范围](01-product-and-scope.md)、[UI/UX 与原型说明](05-ui-ux-and-prototype-notes.md) | 核心工作流、页面边界和交互约束是什么。 |
| 后续 AI 接手 | [中文表达与术语表](00-中文表达与术语表.md)、[整理决策记录](06-decision-log.md) | 当前口径、非目标和不能重开的决策是什么。 |
| 执行计划接手 | [计划资产](07-plan-assets/README.md) | Runtime、产品化路线、历史归档和各版本研发计划该如何落地。 |

完整顺序：

1. [中文表达与术语表](00-中文表达与术语表.md)
2. [产品定位与范围](01-product-and-scope.md)
3. [PRD](02-prd.md)
4. [技术架构](03-technical-architecture.md)
5. [版本路线与 Release Gates](04-roadmap-and-release-gates.md)
6. [UI/UX 与原型说明](05-ui-ux-and-prototype-notes.md)
7. [整理决策记录](06-decision-log.md)
8. [计划资产](07-plan-assets/README.md)

## 目录原则

- 只保留当前准确文档。
- 旧草案的有效结论已融合进主题文档，不再保留原始全文。
- 不采用的视觉草稿不进入远程仓库。
- 每份文档承担一个清晰问题，避免把所有内容压进一个巨型 Markdown。
- 所有产品和技术判断必须能回到 blueprint、当前代码、测试或明确决策记录。
- 面向当前推进的中文文档优先解释业务含义；历史证据文档不为了通俗化而重写。

## 与主仓库的关系

主仓库只保留公开精简入口；完整 PRD TechPlan 留在本子仓库。这样可以同时满足：

- 公开仓库入口清晰。
- 内部 AI 和工程协作有完整上下文。
- 旧资料不会污染最终远程文档。

## 当前最高优先级

`0.1.x` production release gate 已关闭。当前优先级是维护已发布的 `deepseek_runtime` kernel，并推进 `0.2.x` Desktop Code Workbench；`0.3.x`、`0.4.x` 和 `1.0` 的后续研发计划见 [计划资产](07-plan-assets/README.md)。
