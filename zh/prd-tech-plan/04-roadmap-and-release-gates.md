# 04. 版本路线与 Release Gates

## 1. 当前阶段真相

确定：

- Stage 0-5 completed。
- Stage 6 status 是 `completed`。
- Earliest incomplete stage 是 `null`。
- Open item 为空；`production_release_gate` 已关闭。

路线必须从这个事实出发：下一步是 Runtime Kernel 化和后续产品化推进，而不是再铺一轮从 0 到 1 的研究计划。

## 2. 路线原则

- 对外版本少，内部迭代快。
- 每条 release line 只承担一个用户价值闭环。
- 共享 runtime 底座不在每个版本重复铺开。
- DeepSeek 物理特性必须进入 gate。
- 完成率优先于单次 token 最低；成本指标按每成功任务计算。
- 团队、生态、企业能力必须由真实用户证据牵引。

## 3. Release Lines

### 3.1 `0.1.x` Public Alpha

目标：关闭当前 production release gate，把 research MVP 变成可公开试用的 CLI-first 产品。

必须做：

- CLI install / uninstall / doctor。
- DeepSeek provider adapter。
- permission / sandbox / changeset / rollback。
- checkpoint / resume。
- evidence / usage / cache / cost。
- README / release artifact / compatibility matrix。

明确不做：

- 完整桌面多工作台。
- 写作模式。
- 手机连接 / IM / 定时任务。
- 团队协作层。
- 企业治理。

Gate：

- install / first task / uninstall smoke 通过。
- read-only task 有来源证据。
- write task 有 diff、approval、rollback。
- route / cache / cost 可见。
- 小型确定性任务集能报告成功/失败、失败样本和每成功任务 token / cost。
- release artifact 可复核。

### 3.2 `0.2.x` Desktop Code Workbench

目标：把 runtime 接到桌面 UI，形成可信的桌面 Code 工作台。

必须做：

- desktop shell。
- workspace chooser。
- Task Center / Task Detail。
- Agent / Code 双模式入口。
- diff review / approval UI。
- checkpoint / evidence / cost 可视化。
- local runtime manager。

明确不做：

- 独立 Write 工作台。
- 手机连接。
- 定时任务。
- 团队共享规则。

Gate：

- Desktop 通过 local runtime bridge 启动任务。
- UI 不伪造 runtime 状态。
- approval / diff / rollback 与 CLI 语义一致。
- Task Detail 展示完成证据、未验证项、人工接管和 cost per successful task。
- runtime crash 不导致 UI 静默错误。

### 3.3 `0.3.x` General Workspace Agent

目标：从代码工作台扩展到通用本地工作台。

必须做：

- 文件夹总结。
- 多文档报告。
- artifact manager。
- Project Memory。
- Skill index / body separation。
- PlanGraph。
- Review Gate。

明确不做：

- 深度浏览器控制。
- IM / 手机连接。
- 定时任务。
- 多 Agent 群体调度。
- 团队共享 Memory。
- 企业治理。

Gate：

- artifact 有来源引用。
- Memory 可确认、编辑、禁用、删除。
- Skill body 只按需加载。
- PlanStep 可持久化、恢复、关联 evidence。
- 长期任务能按 PlanStep 汇总完成率、恢复结果、人工接管和 token / cost。
- Review Gate 可触发并写入 evidence。

### 3.4 `0.4.x` Integrations And Automation Preview

状态（确定，2026-06-17）：已实现并归档，主规格为 `openspec/specs/integrations-automation-preview/spec.md`，归档 change 为 `openspec/changes/archive/2026-06-17-start-integrations-automation-preview`。

目标：在本地工作台、Memory / Skill、PlanGraph 成立后，安全接入外部工具、MCP、定时任务和轻量审批。

必须做：

- MCP client。
- local tool catalog。
- tool schema fingerprint。
- drift detection。
- tool permission profiles。
- tool health check。
- local scheduled tasks。
- notification bridge。
- remote approval for pre-generated actions。
- automation audit log。
- deepseek_runtime 与成熟宿主（如 Kun）的桥接与协议适配。

明确不做：

- 公开插件市场。
- 云端常驻执行。
- 无审批自动副作用。
- 个人微信深度控制。
- 企业级 policy center。
- 多租户管理。

Gate：

- MCP connection test。
- tool risk / drift tests。
- schedule trigger audit。
- remote approval token tests。
- tool context / evidence checks。
- 自动化任务报告 completion evidence、approval intervention 和每成功任务成本。
- Kun 宿主桥接集成测试通过，无静默回退。
- Python 桥接在当前本地目标平台完成集成验证；跨平台兼容矩阵进入 `1.0` 稳定发布准备。

### 3.5 `1.0` Stable Public Release

目标：形成真正面向公开用户的稳定产品。

必须做：

- Public README / Quick Start / Troubleshooting。
- release artifact checksum 或等价完整性校验。
- install / upgrade / uninstall smoke。
- config migration。
- local diagnostics bundle。
- privacy / security / permission 文档。
- issue template / security policy / contributing guide。

明确不做：

- 企业 SSO / SCIM。
- 云端多租户。
- 商业计费。
- 公开插件市场。
- 企业 policy center。
- 实时多人协作。

Gate：

- prior gates 已通过，或未通过 gate 有明确 blocker / 延期豁免。
- public install 通过。
- migration / rollback tests 通过。
- build manifest + checksum verification 通过。
- diagnostics redaction tests 通过。
- route / cache / evidence smoke 通过。
- E4-style 真实任务证据报告可验证成功率、首次完成率、失败样本、人工接管和每成功任务 token / cost。
- `production_release_gate` 已关闭。

## 4. 全局禁止的伪完成

- 只在开发机能运行，没有安装链路。
- 只输出自然语言总结，没有 evidence。
- 只列出工具但不能安全调用。
- token 或成本下降但任务成功率、正确性、安全或恢复能力下降。
- 自动化绕过 approval。
- 诊断包泄露 secret。
- UI 隐藏 route / cache / usage / permission。
- 文档只覆盖 happy path。

## 5. 当前执行顺序

1. 冻结 0.1.x 范围。
2. 完成 install / uninstall / doctor / release artifact。
3. 验证 permission、sandbox、diff、rollback、session resume。
4. 将 route、cache、usage、cost、可验证成功率和每成功任务成本纳入 smoke。
5. 补齐 public README、security、troubleshooting。
6. 关闭 production release gate 后再进入桌面主线。
