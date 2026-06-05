# Stage 0–6 全阶段完成度审计

> 初始审计日期：2026-06-04
> 最近复核：2026-06-05
> 当前结论：Stage 0–5 已完成；Stage 6 研究 MVP Gate 已完成；最早未完成项是 `6-release`。不得声明生产发布完成，直到 Production Release Gate 有完整兼容、安装包、签名/卸载、rollback 与发布决策证据。

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
| Stage 1 DeepSeek V4 模型事实 | **completed** | 固定来源、当前事实、外推分离、高影响 Harness 结论复核与 unknowns register 已完成；E3/E4 未知项已转交后续阶段 |
| Stage 2 竞品/Harness 调研 | **completed** | 固定快照 Pass 2、P1 范围决策、统一证据矩阵与过度声明复核完成；Claude Code engine 不公开作为永久边界 |
| Stage 2.5 协议与 Cache 实证 | **completed** | E3 Flash/Pro 协议矩阵、Prefix Cache 跨时间验证与脱敏 evidence bundle 已完成 |
| Stage 3 架构对比与借鉴 | **completed** | 全量 Harness 矩阵、设计模式/反模式、证据化借鉴决策和 E4 输入已完成 |
| Stage 4 产品战略与技术架构 | **completed** | E3/E4 约束后的产品战略、Cache、Flash/Pro 路由、runtime foundation ADR 和生产架构规格已完成 |
| Stage 5 PRD / UX / 研发拆解 | **completed** | 生产 PRD、桌面双模式 UX、Runtime API/Data、威胁模型、验收标准与可执行拆解已完成 |
| Stage 6 Fork / 整合 / MVP | **research_mvp_completed_release_not_passed** | 研究 MVP、OpenCode fixed-source live probe、安全写入、恢复、E4 20/20 与 install/uninstall smoke 已完成；Production Release Gate 未通过 |

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

**2026-06-05 关闭证据**

- `stage1-source-snapshot-2026-06-05.json` 固定官方模型 revision、文件 blob、技术报告 SHA-256 与 API 文档页面哈希；
- `2-1-DeepSeek-V4当前事实校准与未知项-Current-Fact-Calibration.md` 分离事实、产品声明、推论、unknown 与 rejected 结论；
- E3 API 与 E4 真实任务问题已明确登记并转交 Stage 2.5 / Stage 3–4，不再伪装成 Stage 1 源码事实。

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

**2026-06-05 关闭证据**

- `stage2-pass2-evidence-2026-06-05.json` 固定五项目 commit、扫描边界、代表性测试命令/结果与 P1 范围决策；
- `18-0-五项目Pass2与统一证据矩阵` 完成五项目八步审计、十一项目统一矩阵和过度声明复核；
- 五项目代表性测试最终结果：OpenCode 147 pass/1 skip、OMO 94 pass、OMC 37 pass、OpenSpec 195 pass、Superpowers 56 pass，均 0 fail；
- Cursor/Windsurf/Devin 排除源码 Pass 2；Roo/OpenHands/Goose/Aider 纳入 E4 baseline；Cline 延期独立 Pass 2；
- Claude Code 完整 engine 非官方公开作为永久边界，不伪装完成源码深读。

**完成 Gate**

- 对 P0 项目完成固定 commit Pass 2 与运行路径/测试证据；
- 对 P1 项目明确完成、延期或排除及原因；
- 建立统一证据索引和可借鉴性矩阵；
- 所有不可获得源码边界明确记录。

### Stage 2.5：DeepSeek 协议与 Prefix Cache 实证

**已有证据**

- 可重复 runner、dry-run、manifest、脱敏 trace 结构、请求预算保护；
- 历史 E2 Pilot 和科研严谨性复核。
- E3 Flash/Pro protocol/cache/cross-time live bundle；
- 可提交的脱敏 evidence bundle 索引。

**完成 Gate**

- Flash/Pro E3 协议矩阵通过；
- Prefix Cache 跨时间验证完成；
- 结果以 manifest、summary 和脱敏 trace 提交。

### Stage 3：架构对比与借鉴评估

**已有证据**

- 五项目分层综合评估；
- 六项目校准后综合结论；
- Gap Analysis v1.0；
- 全量 Harness 矩阵、模式/反模式、借鉴/改造/拒绝矩阵；
- E3/E4 数据对架构判断的修订。

**完成 Gate**

- 全量项目统一维度矩阵完成；
- 可借鉴、需改造、不可照搬的证据化清单完成；
- E4 输入进入 Stage 6 验收闭环。

### Stage 4：产品战略与技术架构

**已有证据**

- 产品定位和分层架构 v0.1；
- 若干可逆 ADR。
- E3/E4 约束后的架构定稿；
- Flash/Pro 路由、Cache、runtime foundation ADR 与生产架构规格。

**完成 Gate**

- 产品战略、用户价值、桌面/CLI 边界与竞争策略完成；
- Cache、reasoning、Flash/Pro 路由和编排决策有 E3/E4 支撑；
- 数据模型、接口、部署、可观测性、安全、迁移与风险架构完成。

### Stage 5：PRD、UX 与研发拆解

**已有证据**

- 研究型只读 CLI MVP 范围和初步研发拆解。
- 生产 PRD、桌面双模式 UX、Runtime API/Data、威胁模型；
- Epic/Story/验收标准/依赖/估算的可执行拆解。

**完成 Gate**

- 桌面端、Agent Mode、Code Mode 的完整 PRD 与信息架构完成；
- 权限、diff、checkpoint、cost/cache telemetry、任务中心等 UX 完成；
- Runtime/API/data schema 生产规格、威胁模型、失败模式、发布和回滚计划完成。

### Stage 6：Fork、整合与 MVP

详见 `7-2-Stage6-完成定义与阻塞项.md`。现状是 `research_mvp_completed_release_not_passed`：研究 MVP Gate 已完成，Production Release Gate 未通过。

## 4. 正确执行顺序

下一位 AI 必须从**最早未完成项 `6-release`**继续，不能重新打开已关闭阶段，也不能把研究 MVP 结果写成生产发布：

```text
Stage 0–5 状态一致性维护
→ Stage 6 Production Release Gate
→ Windows / desktop installer / signing / uninstall compatibility drills
→ release rollback drill
→ production release decision
```

允许维护研究 MVP 代码和证据文档，但不得把缺少外部平台兼容证据的状态标记为生产发布完成。
