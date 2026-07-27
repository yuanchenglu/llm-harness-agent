# DeepSeekAgent PRD TechPlan

本文档包记录 `llm-harness-agent` 从研究、产品规划到工程规格形成过程中的当前有效结论。它不是运行时代码仓库，也不能替代实际 Runtime 仓库中的测试、tag、artifact 和发布决策。

中文表达原则见：[中文表达与术语表](00-中文表达与术语表.md)。项目当前状态先读仓库根目录的 [`STATUS.md`](../../STATUS.md)，机器可读状态见 [`stage-gates.json`](../blueprint/stage-gates.json)。

## 当前判断

确定：

- Blueprint Stage 0–5 已完成。
- Stage 6 的 research MVP 已完成。
- Production Release Gate 在本仓库中处于 `unverified_in_this_repository`。
- 最早未完成项是 `6-release-evidence-reconciliation`。
- 历史计划中“已实现”“已归档”或“工作区已完成”的描述，不等于已经存在可复核的远端 production release。

当前主任务不是重新定义项目地基，也不是继续无边界增加功能，而是：

1. 确认实际承载 Runtime、Desktop、OpenSpec 和 release scripts 的仓库；
2. 固定实现 commit/tag；
3. 补齐 artifact、checksum、平台矩阵和发布 Gate 报告；
4. 再决定 Production Release Gate 是关闭、延期还是重新打开。

## 文档结构

如果第一次阅读，建议先读：

1. [项目状态真源](../../STATUS.md)
2. [中文表达与术语表](00-中文表达与术语表.md)
3. [产品定位与范围](01-product-and-scope.md)
4. [PRD](02-prd.md)
5. [版本路线与 Release Gates](04-roadmap-and-release-gates.md)

按角色阅读：

| 读者 | 建议入口 | 读完应能回答 |
| --- | --- | --- |
| 产品 / 项目推进 | [项目状态真源](../../STATUS.md)、[产品定位与范围](01-product-and-scope.md)、[版本路线与 Release Gates](04-roadmap-and-release-gates.md) | 当前哪些研究和规格已经完成，产品发布还缺哪些不可变证据。 |
| 工程执行 | [PRD](02-prd.md)、[技术架构](03-technical-architecture.md)、[版本路线与 Release Gates](04-roadmap-and-release-gates.md) | 哪些能力属于规格，哪些必须回到实际 Runtime 仓库验证。 |
| 设计 / 原型 | [产品定位与范围](01-product-and-scope.md)、[UI/UX 与原型说明](05-ui-ux-and-prototype-notes.md) | 核心工作流、页面边界和交互约束是什么。 |
| 后续 AI 接手 | [项目状态真源](../../STATUS.md)、[中文表达与术语表](00-中文表达与术语表.md)、[整理决策记录](06-decision-log.md) | 当前事实、非目标、证据缺口和不能伪完成的 Gate 是什么。 |
| 执行计划接手 | [计划资产](07-plan-assets/README.md) | 哪些计划是历史归档，哪些仍需在实际实现仓库执行。 |

完整顺序：

1. [项目状态真源](../../STATUS.md)
2. [中文表达与术语表](00-中文表达与术语表.md)
3. [产品定位与范围](01-product-and-scope.md)
4. [PRD](02-prd.md)
5. [技术架构](03-technical-architecture.md)
6. [版本路线与 Release Gates](04-roadmap-and-release-gates.md)
7. [UI/UX 与原型说明](05-ui-ux-and-prototype-notes.md)
8. [整理决策记录](06-decision-log.md)
9. [计划资产](07-plan-assets/README.md)

## 目录原则

- 只保留当前准确文档；历史状态必须标记日期和证据边界。
- 旧草案的有效结论应融合进主题文档，不把过时状态继续当作当前事实。
- 不采用的视觉草稿不进入远程仓库。
- 每份文档承担一个清晰问题，避免把所有内容压进一个巨型 Markdown。
- 所有产品和技术判断必须能回到固定源码、官方文档、实验结果、实际代码、测试或明确决策记录。
- 本仓库缺少实际实现时，使用“规格”“计划”“外部工作区记录”或“未验证”，不得写成“生产已完成”。
- 面向当前推进的中文文档优先解释业务含义；历史证据文档不为了通俗化而改写原始结论。

## 与实际产品仓库的关系

本仓库保留：

- 公开研究入口；
- 产品和技术规格；
- 竞品审计；
- 脱敏实验摘要；
- 阶段决策与证据索引。

实际产品仓库必须保留：

- Runtime / Desktop / scripts / tests；
- OpenSpec 当前实现；
- build manifest；
- release artifact 和 checksum；
- 平台兼容矩阵；
- tag、release notes 和 production release decision。

两者之间必须通过固定仓库 URL、commit SHA、tag 和证据 Hash 建立映射，不能依赖本地路径或口头描述。

## 当前最高优先级

当前最高优先级是完成发布证据对账：

1. 登记实际 Runtime 仓库与固定 commit；
2. 核对 `0.1.x`–`1.0` 的真实实现和 OpenSpec 状态；
3. 补齐 public install、upgrade、uninstall、rollback、diagnostics redaction、artifact checksum 和平台矩阵；
4. 提交 E4-style 发布报告，区分首次成功、重试成功、人工介入和失败样本；
5. 同步更新 `STATUS.md`、`stage-gates.json`、本目录和 Blueprint 入口。

在证据完成前，不扩大团队、企业、插件市场或云端多租户范围。
