# DeepSeek Agent Blueprint 交接包

> 当前状态先读：[项目状态真源](../../STATUS.md)  
> 机器可读状态：[`stage-gates.json`](stage-gates.json)  
> 本目录性质：历史研究、证据、阶段审计、产品架构和 MVP 记录的交接索引。

## 1. 重要边界

本目录不是当前 DeepSeekAgent Runtime 的完整实现仓库，也不是 Production Release 的独立证明。

必须区分：

```text
研究结论
规格和 ADR
脱敏实验摘要
本地/外部工作区实现记录
固定 Commit 验证
远端 Release
```

当前可确认：

- Stage 0–5 的研究和规格资产已完成；
- Stage 6 research MVP 有 E3/E4、安全写入、回滚和恢复等摘要证据；
- Production Release 在本仓库中仍为 `unverified_in_this_repository`；
- 最早未完成项是 `6-release-evidence-reconciliation`。

任何历史文档中的“已完成”“Gate 已关闭”或“已发布”，若没有实际 Runtime 仓库、完整 Commit SHA、Tag、Artifact、Checksum、平台矩阵和发布决策，均视为历史记录或外部工作区声明，不作为当前产品发布事实。

## 2. 推荐阅读顺序

### 判断当前状态

1. [项目状态真源](../../STATUS.md)
2. [`stage-gates.json`](stage-gates.json)
3. [PRD TechPlan](../prd-tech-plan/README.md)
4. [版本路线与 Release Gates](../prd-tech-plan/04-roadmap-and-release-gates.md)

### 理解研究方法

5. [研究方法与事实校准](../theory/research-method.md)
6. [DeepSeek Agent 理论总纲](../theory/theory-guide.md)
7. [Stage 0–6 全阶段完成度审计](01-总体计划与阶段管理-Master-Plan-and-Stage-Tracking/1-2-Stage0至Stage6全阶段完成度审计-All-Stage-Completion-Audit.md)

### 追溯实验和架构

8. [协议与 Prefix Cache 实证报告](03-5-DeepSeek-Agent协议与Benchmark验证-DeepSeek-Agent-Protocol-and-Benchmark-Validation/18-0-协议与Prefix-Cache实证报告-Protocol-and-Prefix-Cache-Evidence.md)
9. [E4 真实任务与 Release Gate 结果](07-代码Fork整合与MVP实现-Code-Fork-Integration-and-MVP/7-3-E4真实任务与Release-Gate结果-2026-06-05.md)
10. [竞品架构对比](04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md)
11. [产品战略和技术架构目录](05-DeepSeek-Agent产品战略与技术架构-Product-Strategy-and-Technical-Architecture/)
12. [PRD / UX / 研发拆解目录](06-PRD-UX与研发拆解-PRD-UX-and-Engineering-Breakdown/)

## 3. 目录地图

```text
00-项目总纲与交接提示词
01-总体计划与阶段管理
02-DeepSeek-V4源码调研
03-Agent竞品Harness调研
03-5-DeepSeek-Agent协议与Benchmark验证
04-竞品架构对比与借鉴评估
05-DeepSeek-Agent产品战略与技术架构
06-PRD-UX与研发拆解
07-代码Fork整合与MVP实现
99-归档与原始压缩包
```

### `00` 项目总纲与交接提示词

保存历史执行提示词和接手规则。提示词中的“下一步”具有日期上下文，不自动代表当前优先级。

### `01` 总体计划与阶段管理

保存阶段定义、完成度审计和状态变化记录。当前状态以根目录 `STATUS.md` 和 `stage-gates.json` 为准。

### `02` DeepSeek V4 源码调研

保存固定来源、模型结构、Encoding、Kernel 和能力边界研究。必须区分：

```text
当前官方事实
旧版本外推
产品声明
工程推论
unknown
```

### `03` Agent 竞品 Harness 调研

保存 Claude Code、Codex、Trae、Reasonix、Hermes、CodeWhale、OpenCode、OMO、OpenSpec、Superpowers 等固定版本审计。

竞品结论只能在固定 Commit 和扫描范围内成立。

### `03-5` 协议与 Benchmark

保存 DeepSeek API 协议、Prefix Cache、Capability Matrix、Manifest 和脱敏实验摘要。

注意：

- 历史 Pilot 不是确认性实验；
- HTTP 200 不等于参数语义生效；
- Cache Hit 不等于任务质量；
- 结果只适用于记录的 Endpoint、账户和时间窗口。

### `04` 架构对比

保存跨产品能力矩阵、可借鉴模式和反模式。借鉴结论不是代码实现完成证明。

### `05` 产品战略与技术架构

保存产品定位、Runtime 分层、Provider、Context、Policy、Evidence、路由和 ADR。

### `06` PRD / UX / 研发拆解

保存生产规格、Desktop UX、Runtime API/Data、威胁模型和验收拆解。

### `07` 代码整合与 MVP

保存研究 MVP、OpenCode Spike、E3/E4 和 Release Gate 历史结果。

其中 2026-06-05 的结论明确是：

```text
research MVP Gate passed
production release Gate not passed
```

后续计划若称外部工作区已完成更多版本，必须补实际实现仓库映射后才能晋级状态。

### `99` 归档

只用于历史追溯。归档内容不能作为当前事实或默认执行入口。

## 4. 阶段状态

| 阶段 | 当前状态 | 说明 |
| --- | --- | --- |
| Stage 0 | completed | 总纲、交接和机器状态框架 |
| Stage 1 | completed | DeepSeek V4 固定来源与事实边界研究 |
| Stage 2 | completed | 竞品固定版本审计与统一矩阵 |
| Stage 2.5 | completed | E3 协议和 Prefix Cache 限定范围实验 |
| Stage 3 | completed | 架构比较和借鉴评估 |
| Stage 4 | completed | 产品战略与技术架构规格 |
| Stage 5 | completed | PRD、UX、威胁模型和工程拆解 |
| Stage 6 Research MVP | completed | 研究型实现和受控任务证据 |
| Stage 6 Production Release | unverified | 需实际 Runtime 的不可变发布证据 |

## 5. 当前缺口

Production Release 对账至少需要：

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

如果实际能力分布在多个仓库，应建立映射表：

| 能力 | 仓库 | Commit | Tag | Evidence |
| --- | --- | --- | --- | --- |
| Runtime | 待登记 | 待登记 | 待登记 | 待登记 |
| Desktop | 待登记 | 待登记 | 待登记 | 待登记 |
| OpenSpec | 待登记 | 待登记 | - | 待登记 |
| Release Scripts | 待登记 | 待登记 | - | 待登记 |

## 6. 证据等级

```text
A0：固定 Commit 的真实运行路径与测试共同证明
A1：固定 Commit 的实现源码证明，运行效果未确认
A2：官方 README / Docs / Config 声明
B：基于事实的工程推论或设计方案
C：非官方逆向或社区线索
N：公开证据中未找到实现
```

每个关键结论应说明：

- 来源；
- 固定版本；
- 扫描范围；
- 是否进入真实运行路径；
- 是否有测试；
- 可外推范围；
- 未验证项。

## 7. Benchmark 纪律

报告必须区分：

```text
development set
prompt-tuning set
validation set
held-out test set
first-pass success
success after retry
human intervention
failure samples
```

任务专用 Acceptance Hint、Verifier Feedback 和多次 Retry 后的最终完成率，不能直接写成未见任务上的泛化成功率。

## 8. 交接执行规则

新的 AI 或工程执行者应：

1. 先读取 `STATUS.md` 和 `stage-gates.json`；
2. 确认任务属于本知识库还是实际 Runtime 仓库；
3. 使用固定 Commit，不依赖移动分支；
4. 将计划、实现、验证、发布状态分开；
5. 对强结论提供 Evidence；
6. 不提交 Secret、完整 CoT 或未授权文件正文；
7. 更新状态时同步所有当前入口；
8. 历史文档只增加“已被取代”说明，不篡改原始实验结果。

## 9. 当前正确下一步

```text
确认实际 Runtime / Desktop / OpenSpec 仓库
→ 固定 Commit 和版本
→ 对账历史计划与真实实现
→ 运行 Release Gate
→ 生成 Artifact / Checksum / Platform Matrix
→ 创建 Tag / Release Notes
→ 记录 Production Release Decision
→ 同步本知识库状态
```

在上述证据完成前，本目录继续作为研究和产品交接知识库，不宣称生产版本已完成发布。
