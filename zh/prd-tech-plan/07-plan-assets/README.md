# 07. 计划资产

本目录保存跨阶段计划、历史执行记录和后续工作说明。计划资产不是实现事实、OpenSpec 真源或 Release Gate 证据。

当前状态先读：

1. [项目状态真源](../../../STATUS.md)
2. [`stage-gates.json`](../../blueprint/stage-gates.json)
3. [版本路线与 Release Gates](../04-roadmap-and-release-gates.md)

## 使用边界

必须区分：

```text
计划已写
OpenSpec 已归档
外部工作区曾实现
固定 Commit 已验证
Release Candidate 已验证
Production Release 已发布
```

这些状态不能互相替代。

本目录中的旧计划可能引用另一个仓库或未提交工作区里的：

- `src/`、`tests/`、`scripts/`；
- `apps/desktop/`；
- `openspec/`；
- build artifact；
- release tag。

如果当前知识库中不存在这些路径，执行者必须先登记实际仓库 URL 和完整 Commit SHA，不得把相对路径当作当前可执行资产。

## 当前状态快照

| 计划线 | 本仓库可确认状态 | 需要补齐的证据 |
| --- | --- | --- |
| Runtime Kernel | 存在版本与发布计划记录 | 实际仓库、版本 tag、artifact、checksum、测试报告 |
| `0.1.x` Public Alpha | research MVP 和部分安装/安全摘要存在 | 远端 Public Alpha release、兼容矩阵和完整 Gate |
| `0.2.x` Desktop Code Workbench | 存在首片、hardening 和 OpenSpec 归档记录 | 实现 Commit、Desktop 测试、安装包和运行证据 |
| `0.3.x` General Workspace Agent | 存在规格和归档记录 | 实际 OpenSpec/实现仓库映射、测试和发布状态 |
| `0.4.x` Integrations and Automation Preview | 存在 2026-06-17 外部工作区归档记录 | 固定 Commit、MCP/Automation 安全测试和发布证据 |
| `1.0` Stable Public Release | 计划称 2026-06-18 外部工作区已完成收口，同时明确尚需 Commit、Tag 和 Remote Release | Runtime Commit、tag、release notes、artifact、checksum、平台矩阵和生产发布决策 |
| 中文 B 端桌面 UI 重构 | 产品方向计划 | 需确认是否仍是当前产品方向，并映射到实际实现仓库 |

因此，当前统一状态是：

```text
research/specification assets: available
external implementation claims: require reconciliation
production release: unverified in this repository
```

## 阅读顺序

### 基础规则

1. [计划资产写作标准](00-plan-asset-writing-standard.md)

### 历史计划与执行记录

2. [Runtime Kernel 发布与补丁计划](01-runtime-kernel-release-and-patch-plan.md)
3. [DeepSeekAgent 产品化路线计划](02-deepseekagent-productization-roadmap-plan.md)
4. [Desktop Code Workbench 首片计划](03-desktop-code-workbench-first-slice-plan.md)
5. [`0.1.x` Public Alpha Release Gate 归档计划](04-0-1-x-public-alpha-release-gate-archive-plan.md)
6. [PRD TechPlan 分层归档计划](05-prd-tech-plan-layered-archive-plan.md)
7. [OpenSpec 工作流与 Artifact Gate 归档计划](06-openspec-workflow-bootstrap-plan.md)
8. [`0.2.x` Desktop Code Workbench 版本研发计划](07-0-2-x-desktop-code-workbench-version-plan.md)
9. [`0.3.x` General Workspace Agent 版本研发计划](08-0-3-x-general-workspace-agent-version-plan.md)
10. [`0.4.x` Integrations and Automation Preview 版本研发计划](09-0-4-x-integrations-and-automation-preview-plan.md)
11. [`1.0` Stable Public Release 版本研发计划](10-1-0-stable-public-release-plan.md)
12. [中文 B 端桌面 UI 重构计划](11-business-desktop-ui-redesign-plan.md)

这些文件应按其记录日期阅读。标题中的“发布”“归档”“已完成”不自动表示当前远端产品已经发布。

## 新计划写作要求

每份新计划必须包含：

```text
目标
当前事实与固定证据
实际仓库和 Commit
关键决策
非目标
实施步骤
验证命令
Artifact / Report 输出
完成定义
回滚
状态同步位置
```

并在前部明确：

- 这是计划、实现记录还是验证报告；
- 适用仓库；
- 基础 Commit；
- 当前状态；
- 哪些结论仍未验证。

## 状态晋级规则

### 从 Plan 到 Implemented

需要：

- 实际文件；
- 固定 Commit；
- 测试；
- 与 Spec 的映射。

### 从 Implemented 到 Verified

需要：

- 干净环境复现；
- 失败样本；
- 平台/版本边界；
- 安全和回滚测试。

### 从 Verified 到 Released

需要：

- Tag；
- Release Notes；
- Artifact Manifest；
- Checksum；
- 发布决策；
- 远端可复核记录。

## 维护规则

- 已完成事实和待做计划分开写；
- 外部工作区记录必须标记为外部或未提交；
- 相对路径只有在本仓库真实存在时才可作为执行入口；
- 不用 OpenSpec Archive 代替 Runtime Evidence；
- 不用一次本地 Smoke 代替平台兼容矩阵；
- 不用最终重试成功率代替首次成功率；
- 新证据进入后同步 `STATUS.md`、`stage-gates.json`、PRD 和 Blueprint；
- 具体实施仍应走实际实现仓库的 OpenSpec 或等价变更流程。
