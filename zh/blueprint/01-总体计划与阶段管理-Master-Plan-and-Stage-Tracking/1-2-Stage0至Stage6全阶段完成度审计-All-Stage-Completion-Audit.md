# Stage 0–6 全阶段完成度审计

> 审计日期：2026-06-04
> 审计结论：此前不仅 Stage 6 被过度声明，**Stage 1、Stage 2、Stage 3、Stage 4、Stage 5 也均不能认定为完整完成**。Stage 0 在本次修正总控提示词、状态清单与 manifest 后可认定完成。

## 1. 审计方法

阶段“完成”必须同时满足：

1. **范围完整**：计划中必需项完成，延期项有明确决策而非被遗忘；
2. **证据充分**：强结论有固定源码、官方文档、可复现实验或真实任务数据；
3. **产物可用**：不是只有标题或短篇草案，而是能被后续阶段直接使用；
4. **状态一致**：README、master plan、manifest、stage-gates 不互相矛盾；
5. **验证通过**：代码、链接、JSON、测试与证据索引可检查；
6. **完成定义达标**：不得用“第一轮调研”“Pass 1”“v0.1 草案”“只读 Demo”替代最终 Gate。

本审计以仓库现有文件、明确 TODO、证据级别和可运行测试为依据；文件数量不等于完成度。

## 2. 总体结论

| 阶段 | 真实状态 | 为什么不能再提高状态 |
|---|---|---|
| Stage 0 项目总纲与交接 | **completed（本次修正后）** | 已有目标、阶段、机器 Gate、全阶段提示词和一致性检查；后续只需维护 |
| Stage 1 DeepSeek V4 模型事实 | **in_progress / calibration_required** | v1.1 调研包已完成，但仍含待验证物理事实；需要对当前 V4 官方来源固定版本、逐条校准并将模型事实与推论分离 |
| Stage 2 竞品/Harness 调研 | **in_progress** | 六项目校准完成、五项目仅 Pass 1；Claude Code 官方源码边界有限；五项目 Pass 2 和第二优先级竞品尚未完成 |
| Stage 2.5 协议与 Cache 实证 | **in_progress** | Harness 基础设施存在，但只有降级后的 E2 Pilot；缺 Flash/Pro E3 协议矩阵、跨时段 Cache 与可提交 evidence bundle |
| Stage 3 架构对比与借鉴 | **draft** | 只有部分项目矩阵和 Gap Analysis v0.1；缺全量对比矩阵、设计模式总结、不可照搬清单与 E4 数据 |
| Stage 4 产品战略与技术架构 | **draft** | 当前只有短篇假设性架构 v0.1；Cache ROI、路由、planner/reviewer、底座选择均未由 E3/E4 支撑 |
| Stage 5 PRD / UX / 研发拆解 | **research_mvp_spec** | 当前文档面向研究型 CLI；缺桌面端/Agent Mode/Code Mode 的完整 UX、生产 Runtime Spec、威胁模型、验收标准和可执行拆解 |
| Stage 6 Fork / 整合 / MVP | **in_progress** | 只读 MVP 和 OpenCode 源码 Spike 完成；生产安全、恢复、真实任务、Live Adapter 和最终底座 ADR 未完成 |

## 3. 分阶段证据与缺口

### Stage 0：项目总纲与交接机制

**已有证据**

- 总控 README、master plan、研究方法、机器可读 `stage-gates.json`；
- 全阶段总控提示词与 Stage 6 子提示词；
- `scripts/check_repo.py` 可检查链接、JSON 和密钥。

**本次修正前的问题**

- 旧提示词仍把下一步写成 Claude Code 调研；
- 新提示词直接跳到 Stage 6；
- `manifest.json` 保留旧的“Stage 1 完成、下一步直接战略”等错误状态。

**完成 Gate**

- 本次修正上述不一致后，Stage 0 可标记 completed；以后状态变化必须同步机器 Gate 与 README。

### Stage 1：DeepSeek V4 源码与物理特性调研

**已有证据**

- 完整 v1.1 文档包、证据规范、Phase 1–10 调研产物；
- 对模型结构、API、Kernel、Encoding 和 Harness 约束有大量初步结论。

**未完成项**

- 原始研究日志明确保留 V4 DSA、Ascend、工具稳定性等待验证项；
- 缺一份类似竞品 `17-0` 的 Stage 1 固定版本事实校准清单；
- 需要逐条区分：V4 官方当前事实、来自 V3/V3.2 的外推、API 产品声明、工程推论；
- 需要复核 README 中“通过源码确认”的总括性表述是否过强；
- Stage 1 结论尚未与 E3 API 实验闭环。

**完成 Gate**

- 建立固定来源/版本/访问日期的模型事实清单；
- 校准所有高影响 Harness 结论；
- 未证实项明确保持 unknown；
- 通过链接、来源和结论分类检查。

### Stage 2：Agent 产品与 Harness 竞品调研

**已有证据**

- Claude Code、Codex、Trae、Reasonix、Hermes、CodeWhale 固定 commit 事实校准；
- Codex、Trae、Reasonix、Hermes、CodeWhale 的部分 Pass 2；
- OpenCode、OMO、OMC、OpenSpec、Superpowers Pass 1 和综合评估。

**未完成项**

- OpenCode、OMO、OMC、OpenSpec、Superpowers Pass 2 未完成；
- Cursor、Windsurf、Cline/Roo、Devin、OpenHands、Goose、Aider 是否纳入/延期尚未形成决策；
- Claude Code 完整 engine 非官方公开，必须把该边界作为永久限制，不能伪装完成源码深读；
- 现有报告中的“终版/完整/可直接迁移”仍需统一审计；
- 缺统一测试/运行证据矩阵。

**完成 Gate**

- 对 P0 项目完成固定 commit Pass 2 与运行路径/测试证据；
- 对 P1 项目明确完成、延期或排除及原因；
- 建立统一证据索引和可借鉴性矩阵；
- 所有不可获得源码边界明确记录。

### Stage 2.5：DeepSeek 协议与 Prefix Cache 实证

**已有证据**

- 可重复 runner、dry-run、manifest、脱敏 trace 结构、请求预算保护；
- 历史 E2 Pilot 和科研严谨性复核。

**未完成项与 Gate**

- 详见 `18-1-科研严谨性复核与阶段重评`；必须完成 Flash/Pro E3、Cache 跨时段实验和可复算 evidence bundle。

### Stage 3：架构对比与借鉴评估

**已有证据**

- 五项目分层综合评估；
- 六项目校准后综合结论；
- Gap Analysis v0.1。

**未完成项**

- 全量项目统一维度矩阵；
- Agent Harness 设计模式和反模式；
- 可借鉴、需改造、不可照搬的证据化清单；
- E3/E4 数据对架构判断的修订；
- OpenCode Adapter / 自研 / Fork 的定量比较。

### Stage 4：产品战略与技术架构

**已有证据**

- 产品定位和分层架构 v0.1；
- 若干可逆 ADR。

**未完成项**

- 完整产品战略、用户价值、桌面/CLI 边界、竞争策略；
- 由 E3/E4 支撑的 Cache、reasoning、Flash/Pro 路由和编排决策；
- 数据模型、接口、部署、可观测性、安全、迁移与风险架构；
- 最终底座 ADR 和可执行技术路线图。

### Stage 5：PRD、UX 与研发拆解

**已有证据**

- 研究型只读 CLI MVP 范围和初步研发拆解。

**未完成项**

- 桌面端、Agent Mode、Code Mode 的完整 PRD 与信息架构；
- 权限、diff、checkpoint、cost/cache telemetry、任务中心等 UX；
- Runtime/API/data schema 生产规格；
- 威胁模型、失败模式、兼容性、发布和回滚计划；
- Epic/Story/验收标准/依赖/估算的可执行拆解。

### Stage 6：Fork、整合与 MVP

详见 `7-2-Stage6-完成定义与阻塞项.md`。现状仍是 `in_progress`，不能因 Stage 6 子提示词存在而假定前置阶段完成。

## 4. 正确执行顺序

下一位 AI 必须从**最早未完成阶段 Stage 1**开始校准，而不是直接从 Stage 6 开始：

```text
Stage 0 一致性维护
→ Stage 1 当前模型事实校准
→ Stage 2 P0 竞品 Pass 2 / 范围决策
→ Stage 2.5 E3 协议与 Cache
→ Stage 3 全量综合与 E4 输入
→ Stage 4 架构定稿
→ Stage 5 生产 PRD / UX / 拆解
→ Stage 6 Fork / 整合 / MVP Gate
```

允许并行推进不依赖前置结论的安全基础设施，但不得提前定稿后续阶段，也不得把并行实现写成阶段完成。
