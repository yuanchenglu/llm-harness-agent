# 01. 产品定位与范围

## 1. 一句话定位

DeepSeekAgent 是面向财务、行政、产品经理、律师等知识工作者的中文 B 端本地任务客户端。它把 DeepSeek-native runtime 的本地安全、审批、回滚、证据和诊断能力收敛到一个普通业务人员能理解的桌面工作台：选择项目文件夹，描述任务，审查需要写入的变更，并在失败时恢复。

产品底层仍坚持 Runtime-first：CLI、desktop、automation 都只是本地 runtime 的前端。但桌面端的默认体验不再面向服务器运维人员或研究 demo 用户，也不要求用户理解 route、cache、bridge、SSE、ChangeSet 或 raw evidence。

公开表达可以压缩为：

```text
目标是让财务、行政、产品经理和律师能在本地安全地整理资料、生成任务成果、审查高风险写入，并在需要时回滚和诊断。
```

价值层级：

1. 可验证完成：完成不是模型自述，而是计划、工具调用、diff、测试、验收器和 evidence 支撑的结果。
2. 每成功任务成本：省 token 不能以降低正确性、安全或完成率为代价，核心指标是每个成功任务的 token / cost。
3. 懂项目：通过项目文件夹、Workspace Scan、Project Memory、Skill、PlanGraph 和稳定上下文布局复用项目约束。
4. 更可控：所有副作用都受 permission、sandbox、approval、ChangeSet、checkpoint 和 rollback 约束。

## 2. 项目当前阶段

确定：

- 研究、竞品、DeepSeek V4 物理特性、产品战略、生产 PRD 和研发拆解已经在 blueprint 中完成。
- 研究 MVP 已具备本地 runtime、安全、diff、rollback、session resume 等关键基础能力。
- production release gate 已关闭；下一步是把 runtime foundation 和已证明的桌面能力收敛为中文 B 端工作客户端，而不是继续研究型扩散。

## 3. 目标用户

### 财务人员

需要整理发票、报销、费用、付款节点、预算材料和审计证据，并能明确看到来源、缺失项和待确认事项。

### 行政人员

需要整理会议纪要、制度文档、采购记录、资产台账、通知材料和执行跟进清单。

### 产品经理

需要整理需求、PRD、竞品材料、评审意见、行动项和版本范围。

### 律师

需要整理合同摘要、条款风险清单、事实时间线、材料清单和待确认问题。产品只提供材料整理辅助，不替代法律意见。

### 高级开发者与开源试用者

仍需要可安装、可诊断、边界清楚、不会偷偷写文件或泄露密钥的本地 Agent。Code / diff / diagnostics 作为高级能力保留，但不再压过 B 端默认任务路径。

## 4. 核心产品承诺

DeepSeekAgent 必须做到：

- Completion-first：优先优化真实任务的可验证完成率，而不是单次请求的自然语言表现。
- Runtime-first：CLI、desktop、automation 都只是本地 runtime 的前端。
- DeepSeek-native：不是 generic OpenAI wrapper，必须显式利用 DeepSeek 的 cache、context、route 和 reasoning 特性。
- Local-first：用户代码、文件和密钥默认留在本机。
- Evidence-first：完成不是自然语言声明，而是输入、工具、diff、测试、审批、成本和结果证据。
- Policy-enforced：写文件、运行命令、调用高风险工具都必须被 policy 和 approval gate 约束。
- Recoverable：任何写入都要能预览、应用、回滚、恢复。

## 5. 产品范围

### 5.1 当前主线必须做

- CLI-first public alpha。
- DeepSeek provider / route / cache / usage 可观测。
- Permission、sandbox、diff preview、apply、rollback。
- Session、checkpoint、resume。
- Evidence ledger。
- 中文 B 端 Desktop Workbench。
- 业务角色任务模板。
- Task drawer with approval / rollback / diagnostics。
- Desktop Code Workbench 作为高级入口保留。
- General Workspace Agent。
- Project Memory、Skill index/body separation、PlanGraph。
- MCP/tool integration preview。
- Local automation with approval and audit。
- Stable release packaging、install、upgrade、uninstall、diagnostics。
- deepseek_runtime 通信内核与宿主（如 Kun）的桥接与适配。

### 5.2 当前明确不做

- 企业 SSO / SCIM。
- 云端多租户。
- 云端常驻任务执行。
- 公开插件市场。
- 商业计费。
- 实时多人协同编辑。
- 完整移动端客户端。
- 手机连接作为默认桌面入口。
- 插件市场。
- 未验证的 Excel 深度分析、PDF OCR、合同深度解析或自动法律意见。
- 因为语言偏好而重写 runtime。

### 5.3 可以后置评估

- 团队共享项目配置。
- Task handoff export / import。
- Audit export。
- Plugin SDK preview。
- 轻量移动审批入口。

这些能力只在不阻塞稳定发布、且有真实用户证据时进入 release scope。

## 6. 成功标准

### 产品成功

- 用户能安装、配置、运行第一个安全任务。
- 用户不需要理解 runtime / bridge / cache / route，也能知道下一步该点哪里。
- 用户知道 Agent 是否完成、依据是什么、读了什么、改了什么、为什么改、怎么撤回。
- 用户能在高级详情中看见 route、cache、usage、cost 和 evidence。
- 用户能按任务查看成功/失败、首次完成、人工接管、rollback 和每成功任务成本。
- 用户能在失败时诊断、回滚或提交有效 issue。

### 工程成功

- 生产 release gate 可由测试、文档和 artifact 证据关闭。
- UI 不绕过 runtime policy。
- 版本路线不再扩散成过多对外承诺。
- DeepSeek 物理特性进入 release-critical gates，而不是停留在产品口号。
