# 01. 产品定位与范围

## 1. 一句话定位

DeepSeekAgent 是面向开发者和高频 AI 工作者的 DeepSeek-native 本地 Agent runtime / 工作台：基于 DeepSeek V4 的协议、长上下文、Prefix Cache、Flash / Pro 路由和 reasoning 边界做 harness 层深度优化，以真实项目任务的可验证完成率为第一指标，先以 CLI/runtime 发布，再走向桌面 Code Workbench 和通用本地工作区。

公开表达可以压缩为：

```text
目标是让 DeepSeek 在真实项目里更高概率完成任务，并以更低每成功任务成本、更强项目理解和更可控执行交付结果。
```

价值层级：

1. 可验证完成：完成不是模型自述，而是计划、工具调用、diff、测试、验收器和 evidence 支撑的结果。
2. 每成功任务成本：省 token 不能以降低正确性、安全或完成率为代价，核心指标是每个成功任务的 token / cost。
3. 懂项目：通过 workspace scan、Project Memory、Skill、PlanGraph 和稳定上下文布局复用项目约束。
4. 更可控：所有副作用都受 permission、sandbox、approval、ChangeSet、checkpoint 和 rollback 约束。

## 2. 项目当前阶段

确定：

- 研究、竞品、DeepSeek V4 物理特性、产品战略、生产 PRD 和研发拆解已经在 blueprint 中完成。
- 研究 MVP 已具备本地 runtime、安全、diff、rollback、session resume 等关键基础能力。
- production release gate 已关闭；下一步是把 CLI-first runtime foundation 收敛为可复用、可安装、可验证的 runtime kernel，而不是“重新找产品方向”。

## 3. 目标用户

### 开发者

需要让 Agent 在本地代码库里完成需求分析、计划生成、代码修改、测试建议、审查、提交准备和回滚。

### 高频 AI 工作者

需要让 Agent 整理本地文件、阅读资料、写文档、做调研、分析表格，并把长期项目经验沉淀为 Memory 和 Skill。

### 早期开源试用者

需要一个可安装、可诊断、边界清楚、不会偷偷写文件或泄露密钥的本地 Agent。

### 后续团队试点用户

需要共享项目规则、任务证据、审计记录和安全策略。但这些能力只有在个人版和本地工作台稳定后才进入主线。

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
- Desktop Code Workbench。
- General Workspace Agent。
- Project Memory、Skill index/body separation、PlanGraph。
- MCP/tool integration preview。
- Local automation with approval and audit。
- Stable release packaging、install、upgrade、uninstall、diagnostics。

### 5.2 当前明确不做

- 企业 SSO / SCIM。
- 云端多租户。
- 云端常驻任务执行。
- 公开插件市场。
- 商业计费。
- 实时多人协同编辑。
- 完整移动端客户端。
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
- 用户知道 Agent 是否完成、依据是什么、读了什么、改了什么、为什么改、怎么撤回。
- 用户能看见 route、cache、usage、cost 和 evidence。
- 用户能按任务查看成功/失败、首次完成、人工接管、rollback 和每成功任务成本。
- 用户能在失败时诊断、回滚或提交有效 issue。

### 工程成功

- 生产 release gate 可由测试、文档和 artifact 证据关闭。
- UI 不绕过 runtime policy。
- 版本路线不再扩散成过多对外承诺。
- DeepSeek 物理特性进入 release-critical gates，而不是停留在产品口号。
