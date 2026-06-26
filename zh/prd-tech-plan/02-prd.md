# 02. PRD

## 1. 问题定义

DeepSeekAgent 已经完成研究地基。当前产品问题是：

**如何把 DeepSeek-native runtime 变成一个财务、行政、产品经理、律师能直接使用的中文 B 端本地任务客户端，并保留可审计、可恢复、可审批的安全边界。**

这不是普通聊天壳，也不是服务器运维面板。它要把 DeepSeek 的物理特性和本地安全控制转化为业务用户能看见、能信任、能复用的任务工作流。route、cache、usage、evidence 等工程细节必须服务于完成、审批、回滚和诊断，不能压过业务首屏。

## 2. 产品目标

1. 用户可以安装和配置 DeepSeekAgent。
2. 用户可以用简体中文桌面端选择本地项目文件夹。
3. 用户可以从财务、行政、产品经理、律师模板开始任务。
4. 用户可以用底部输入框描述业务任务。
5. 用户可以在本地工作区执行只读理解任务。
6. 用户可以在审批后执行受控写入任务。
7. 用户可以查看任务结果、来源、失败原因和恢复路径。
8. 用户可以在高级详情中查看 diff、evidence、route、cache、usage、cost。
9. 用户可以回滚、恢复和继续长期任务。
10. 产品最终可以进入稳定公开发布。

## 3. 非目标

- 不做普通聊天应用。
- 不做云端托管 Agent。
- 不让 UI 直接拼 prompt 或直接写文件。
- 不承诺企业治理平台。
- 不把手机连接、插件市场、团队协作、云端自动化塞进本轮桌面重构。
- 不展示未验证的 Excel 深度分析、PDF OCR、合同深度解析或自动法律意见。
- 不在 release gate 关闭前重写 runtime 语言。
- 不用单次请求 token 更低来替代任务完成、正确性、安全和恢复证据。

## 4. 核心用户故事

### US-001 安装与配置

作为新用户，我希望安装 DeepSeekAgent，并配置 DeepSeek API Key。

验收：

- 安装命令或安装包可复现。
- API Key 不进入日志明文。
- 配置错误有明确原因和修复路径。
- `doctor` 或等价检查能说明环境是否可用。

### US-002 中文 B 端首屏

作为财务、行政、产品经理或律师，我希望打开桌面端后看到简体中文的项目、任务和输入框，而不是工程诊断面板。

验收：

- 首屏默认简体中文。
- 可选择项目文件夹。
- 可从角色模板开始。
- 不默认展示 raw JSON、route、cache、bridge、runtime 细节。

### US-003 业务模板任务

作为业务用户，我希望选择“发票核对”“会议纪要”“PRD 评审”“合同摘要”等模板，快速生成任务草稿。

验收：

- 模板按财务、行政、产品经理、律师分组。
- 点击模板只填充草稿，不自动提交。
- 没有工作区时不能运行任务。
- 模板不得承诺未实现的 Excel/PDF/OCR/法律意见能力。

### US-004 只读项目理解

作为业务用户，我希望让 Agent 阅读本地项目文件夹并给出结构化理解。

验收：

- 读取范围可见。
- 不写文件。
- 结论有来源引用或 evidence。
- usage / cache / cost 可见。

### US-005 受控写入

作为用户，我希望 Agent 生成变更或写入成果前，必须先让我审查。

验收：

- 变更以 diff preview 展示。
- 高风险动作需要 approval。
- 应用前创建回滚点。
- 应用后记录 evidence。

### US-006 回滚与恢复

作为用户，我希望任务失败或不满意时可以回滚和恢复。

验收：

- 可以回滚已应用 changeset。
- session 可以 resume。
- checkpoint 可查看。
- 回滚结果写入 evidence。

### US-007 DeepSeek 物理特性可见

作为高级用户或支持人员，我希望在高级详情中知道产品确实在利用 DeepSeek，而不是只换了模型名。

验收：

- route reason 可见。
- cache hit/miss 可见。
- usage / cost 可见。
- context layout 不退回 history dump。

### US-008 桌面 Code Workbench

作为高级用户，我希望不用留在终端，也能完成计划、diff、审批、证据和回滚闭环。

验收：

- 桌面 UI 连接同一 runtime。
- UI 不伪造任务状态。
- approval、diff、checkpoint、evidence 与 CLI 语义一致。

### US-009 通用工作区任务

作为知识工作者，我希望 Agent 可以整理本地文件夹、资料和文档。

验收：

- 文件读取范围可见。
- 生成 artifact 带来源。
- 不自动学习敏感信息。
- 写入仍走 approval。

### US-010 Memory / Skill / PlanGraph

作为长期项目用户，我希望项目规则、常用能力和长任务计划可以复用。

验收：

- Memory 候选进入 Inbox，由用户确认。
- Skill index 可进入稳定上下文，body 按需加载。
- PlanStep 可持久化、恢复、关联 evidence。
- 高风险 checkpoint 可触发 Pro Review。

### US-011 工具与自动化预览

作为高级用户，我希望安全接入 MCP 或本地工具，并创建低风险本地自动化。

验收：

- 工具有 risk profile。
- schema drift 可检测。
- 自动化任务可暂停、禁用、删除。
- 远程审批只能批准或拒绝预生成动作。

### US-012 稳定公开发布

作为公开用户，我希望产品可稳定安装、升级、卸载、诊断和反馈。

验收：

- release artifact 可校验。
- upgrade migration 有备份和回滚。
- diagnostics bundle 脱敏。
- 文档覆盖 quick start、security、troubleshooting、architecture。

## 5. 功能需求

### 5.1 CLI / Runtime

- install / uninstall / doctor。
- workspace scan。
- read-only task。
- write task with diff approval。
- session resume。
- rollback。
- evidence export。

### 5.2 Safety

- permission policy。
- sandbox boundary。
- changeset preview。
- approval gate。
- secret redaction。
- diagnostics redaction。

### 5.3 DeepSeek Observability

- model route。
- route reason。
- cache hit/miss。
- usage tokens。
- cost estimate。
- prefix drift evidence。

### 5.4 中文 B 端 Desktop Workbench

- 项目选择。
- 左侧项目/任务/技能/自动化/设置。
- 财务、行政、产品经理、律师任务模板。
- 底部主输入框。
- 任务列表。
- 任务详情抽屉。
- 审批 / 拒绝 / 回滚。
- 高级 evidence / route / cache / cost / diagnostics。
- Code mode 作为高级入口。

### 5.5 General Workspace

- local folder tasks。
- multi-document reports。
- artifact manager。
- Project Memory。
- Skill Registry。
- PlanGraph。
- Review Gate。

### 5.6 Integrations

- MCP client。
- tool catalog。
- tool schema fingerprint。
- tool health check。
- permission profiles。
- scheduled local tasks。
- notification and approval bridge。

### 5.7 Release Readiness

- release manifest。
- checksum or equivalent integrity check。
- migration manager。
- diagnostics bundle。
- issue template seed。
- release smoke harness。

## 6. 完成质量与成本指标

这些指标是 release gate 和产品决策输入，不是当前已达成的公开承诺：

- 可验证任务成功率：任务必须由确定性验收器、测试、diff、evidence 或人工确认给出成功/失败。
- 首次完成率：首轮执行完成且不需要人工接管或额外修复的比例。
- 每成功任务 token / cost：按成功任务聚合 input、output、cache hit/miss 和价格快照。
- Cache 贡献：cache hit tokens、miss tokens、prefix drift 和主动失效原因。
- 人工干预：approval、deny、allow scoped、接管、retry 和 rollback 次数。
- 恢复质量：checkpoint resume 成功率、重复副作用次数、rollback 成功率。
- 协议质量：DeepSeek Flash / Pro protocol error、fallback、retry 和 unknown 边界。

## 7. 发布完成定义

产品不能按“能跑一次”算完成。必须同时满足：

- 安装、首启、配置、首个任务、卸载链路通过。
- 写入任务可审查、可审批、可回滚。
- route / cache / usage / evidence 可见。
- E4-style 任务证据能报告成功率、首次完成率、每成功任务 token / cost 和失败样本。
- 失败可诊断。
- release gate 有机器可读或可复核证据。
