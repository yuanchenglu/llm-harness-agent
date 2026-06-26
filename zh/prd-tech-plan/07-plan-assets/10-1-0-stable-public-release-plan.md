# 10. `1.0` Stable Public Release 版本研发计划

## 0. AI 执行提示词

你是 DeepSeekAgent `1.0 Stable Public Release` 的 product release lead。你的职责不是继续做研究，也不是扩成企业平台，而是把现有 runtime / desktop / workspace / automation 能力收敛成外部用户可以安装、理解、试用、诊断、回滚和反馈的正式 1.0 产品。执行前必须核对 `0.1.x` 到 `0.4.x` 的 gate、OpenSpec 状态、release artifact、当前 git 状态和公开文档。任何未通过 gate 必须写成 blocker 或延期豁免，不允许用自然语言包装成已完成。

当前状态（确定，2026-06-18）：

- `1.0` 的目标是正式发布给外部用户使用；当前工作区已完成产品页面闭环、安装/诊断/文档/验收证据和 OpenSpec 归档，剩余动作是按仓库 commit / tag / remote release 流程正式发布。
- `0.3.x` 已通过并归档。
- `0.4.x` 已在当前工作区执行 archive：`openspec/changes/archive/2026-06-17-start-integrations-automation-preview`；该 archive 还没有随 DeepSeekAgent 根仓库 commit 一起收口。
- `refresh-consumer-desktop-ui` 已完成并归档到 `openspec/changes/archive/2026-06-18-refresh-consumer-desktop-ui`，主规格为 `openspec/specs/consumer-desktop-ui/spec.md`。
- `prepare-stable-public-release` 已完成并归档到 `openspec/changes/archive/2026-06-18-prepare-stable-public-release`，主规格为 `openspec/specs/stable-public-release/spec.md`。
- 当前真正下一步是提交本次 1.0 产品发布收口，并在需要公开分发时创建 tag / release notes / remote artifact。
- 不能把当前未提交工作区误写成已交付。任何接手 AI 必须先核对 git 状态和测试结果，再继续。

## 1. 目标

`1.0` 的目标是形成真正面向公开用户的稳定产品，而不是企业平台或生态市场。

版本完成后，公开用户应能：

1. 安装 DeepSeekAgent。
2. 配置本地环境和 API key。
3. 运行 doctor。
4. 完成第一个安全任务。
5. 升级版本。
6. 回滚或卸载。
7. 生成 redacted diagnostics bundle。
8. 查阅 Quick Start、Troubleshooting、Security、Compatibility。
9. 提交 issue 或安全报告。

### 1.1 `1.0` 外部用户可用定义

`1.0` 不是“代码能跑”的版本，而是外部用户拿到 release artifact 后可以完成以下闭环的版本：

1. 下载并安装 Desktop 应用或 CLI 包。
2. 首次打开时看懂产品定位：本地个人 Agent 工作台，侧重真实任务、证据、审批和可回滚。
3. 配置 DeepSeek API key 或本地环境，不把 secret 写入日志、截图、diagnostics 或 issue 模板。
4. 选择一个 workspace，运行一个只读任务，看见任务进度、证据、route/cache/usage/cost。
5. 运行一个写入任务，在 diff review 中选择 `Allow once` 或 `Deny`。
6. 应用变更后可以 `Rollback`，并看到回滚结果。
7. 创建或查看一个本地 automation preview，理解它只在本机 app / bridge 存活时运行。
8. 在失败时打开 Diagnostics，生成 redacted bundle，并按 Troubleshooting 或 issue template 提交有效反馈。
9. 升级、回退或卸载时知道会保留和删除哪些数据。

如果以上任一闭环无法由非项目成员独立完成，不能发布 `1.0`。

### 1.2 `1.0` 产品范围

必须进入 `1.0` 的用户可见能力：

- First Run：欢迎、定位说明、环境检查、API key 配置指引、workspace 选择。
- Home / Task Entry：轻量任务入口，支持新建只读任务、写入任务和继续最近任务。
- Workspace：显示当前 workspace、branch、health、权限状态和最近任务。
- Task Center：任务列表、状态、更新时间、pending approval、成本摘要。
- Task Detail：timeline、evidence、route/cache/usage/cost、错误、恢复动作。
- Approval / Change Review：diff、风险说明、`Allow once`、`Deny`、`Rollback`。
- Automation Preview：本地 schedule、notification、audit 的可见状态和安全边界。
- Diagnostics：health、版本、runtime、bridge、redacted bundle、copy issue summary。
- Settings：provider/API key 指引、runtime version、permission profile、data location、updates。
- Docs Entry：Quick Start、Troubleshooting、Security、Compatibility、Contributing。

明确不进入 `1.0` 的用户可见能力：

- 公开插件市场。
- 云端多租户或 hosted service。
- 企业 SSO / SCIM / policy center。
- 商业计费。
- 完整移动端客户端。
- 团队协同和实时多人编辑。
- 新的通用 assistant 大功能。
- Kun / DeepSeek GUI runtime adapter 的 UI switcher。

### 1.3 1.0 页面和交互规格

所有页面默认采用浅色消费级个人助理风格，参考 Codex 的清爽布局语言，但不复制其功能范围。产品不是深色 IDE，不是运维后台，也不是聊天壳。

#### A. 首次启动 / Onboarding

目标：让第一次使用者在 5 分钟内完成环境准备并启动第一个安全任务。

页面必须包含：

1. 产品一句话说明：本地个人 Agent 工作台，所有高风险写入都要审批，可回滚。
2. 环境检查卡片：Desktop version、bridge health、runtime version、Python、Node、DeepSeek provider。
3. API key 配置指引：只说明如何配置，不在 UI 中明文显示完整 key。
4. Workspace 选择：选择本地目录，显示该目录是否可读、是否 git repo、是否可安全写入。
5. “开始第一个只读任务”入口。

交互要求：

- API key 缺失时，允许进入只读 demo / disabled state，但不得假装任务可运行。
- doctor 失败时显示具体原因和恢复动作。
- workspace 选择失败时说明 path、permission 或 trust 问题。
- 不弹出营销式介绍页，不把核心入口藏在文档后面。

验收：

- 新用户从空环境打开应用，能看到下一步要做什么。
- 缺少 `DEEPSEEK_API_KEY`、bridge offline、runtime dependency missing 都有可见恢复路径。

#### B. Home / Task Entry

目标：让用户知道“我现在可以让 Agent 做什么”，并能从轻量入口创建任务。

页面必须包含：

1. 左侧 sidebar：快速对话 / 工作区 / 自动化 / 设置 / 文档入口。
2. 主任务输入区：目标、约束、验收标准、附件或参考路径。
3. 任务类型：只读分析、建议改动、执行改动。
4. 安全提示：写入任务会进入 diff review，不会直接改文件。
5. 最近任务列表：状态、workspace、更新时间、失败/审批提示。

交互要求：

- 默认任务类型是只读分析。
- 用户切到执行改动时，必须展示 approval / rollback 说明。
- 输入区不得出现硬编码 telemetry、假 cache hit rate 或假 routing graph。
- 任务创建失败必须保留用户输入，允许重试。

验收：

- 用户能创建只读任务和写入任务。
- 任务创建后进入 Task Detail，而不是停在空白 loading。

#### C. Workspace

目标：让用户理解当前 Agent 作用域和风险边界。

页面必须包含：

1. 当前 workspace path。
2. Git branch / dirty state / ignored state，如不可用则说明原因。
3. Runtime / bridge health。
4. Permission profile。
5. 最近 file changes、pending approvals、last diagnostics。

交互要求：

- 切换 workspace 时要重新检查权限和 git 状态。
- 不允许 UI 直接读写任意文件；所有写入仍走 runtime / bridge / ChangeSet。
- 对 `.git` hidden mutating、path escape、symlink escape 的拒绝要能被用户理解。

验收：

- 用户能确认 Agent 正在操作哪个目录。
- 用户能看见为什么某个路径或写入被拒绝。

#### D. Task Center

目标：让用户按任务管理 Agent 工作，而不是在聊天记录里找状态。

页面必须包含：

1. task id。
2. workspace。
3. status。
4. updated time。
5. pending approvals。
6. cost / cache summary。
7. failure / recovery badge。

交互要求：

- 点击任务进入 Task Detail。
- 支持手动 refresh。
- SSE 断开后从 snapshot 恢复，不丢任务状态。
- 空状态提供“创建第一个任务”，不展示假数据。

验收：

- 任务列表能区分 running、awaiting approval、failed、completed、rolled back。
- bridge 重启后可重新看到已有 snapshot。

#### E. Task Detail

目标：让用户判断任务是否真实完成、依据是什么、是否需要人工介入。

页面必须包含：

1. timeline。
2. evidence events。
3. route/cache/usage/cost。
4. proposed changes。
5. applied / denied / rolled back changesets。
6. errors and recovery actions。
7. diagnostics shortcut。

交互要求：

- 任务运行中显示当前阶段，而不是泛泛“思考中”。
- 错误必须包含结构化 code、可读 message、建议恢复动作。
- raw prompt、raw response、reasoning_content 不直接暴露在普通 UI。
- 长任务、SSE disconnect、bridge offline 必须有恢复路径。

验收：

- 用户能说明 Agent 做了什么、读了什么证据、花了多少、下一步是什么。
- 用户能从失败任务直接进入 diagnostics 或重试。

#### F. Approval / Diff / Rollback

目标：让所有副作用可预览、可拒绝、可应用、可撤销。

页面必须包含：

1. 文件列表。
2. diff view。
3. 风险说明。
4. original hash / stale warning。
5. `Allow once`。
6. `Deny`。
7. `Rollback`。

状态机：

```text
pending -> denied
pending -> applied
applied -> rolled_back
```

禁止：

- 重复 rollback。
- stale original hash 继续 apply。
- UI 绕过 approval 直接写文件。
- 隐藏 `.git` mutating。
- binary / large file 静默写入。

验收：

- `Deny` 不写文件。
- `Allow once` 只应用一次。
- `Rollback` 恢复原内容。
- 重复 rollback 返回结构化错误。

#### G. Automation Preview

目标：让本地自动化可试用，但边界清楚。

页面必须包含：

1. schedule list。
2. enabled / paused / disabled 状态。
3. next local run。
4. last audit event。
5. notification preference。
6. pending approval count。

交互要求：

- schedule 只在 Electron + bridge 存活时触发。
- 触发前先写 audit event，再创建正常 task snapshot。
- notification payload 必须脱敏。
- 用户关闭某类通知后进入 opt-out 状态。

验收：

- create / edit / pause / resume / disable / delete schedule 可用。
- task complete / failed / approval required / drift detected 四类通知可投递或有明确 unavailable 状态。
- audit 能记录 trigger、permission、approval、result、cost、human intervention。

#### H. Diagnostics / Issue Handoff

目标：让外部用户遇到问题时能生成可安全分享的证据。

页面必须包含：

1. health summary。
2. app / bridge / runtime / platform version。
3. recent structured errors。
4. redacted diagnostics bundle 生成入口。
5. copy issue summary。
6. links to Troubleshooting / Security / Compatibility。

交互要求：

- bundle 生成前说明包含什么、不包含什么。
- redaction 必须覆盖 API key、Authorization、password、raw prompt、raw response、reasoning_content、未授权文件正文。
- 生成失败时给出本地路径、权限或 runtime 原因。

验收：

- diagnostics bundle 可以附到 issue。
- secret 扫描验证不包含敏感内容。

#### I. Settings / Updates / Data

目标：让用户控制 provider、权限、本地数据和版本。

页面必须包含：

1. provider 配置状态。
2. API key 配置指引。
3. runtime tag / bridge version / desktop version。
4. permission profile。
5. local data location。
6. update / migration status。
7. uninstall data retention 说明。

交互要求：

- 不展示完整 API key。
- 不在 Settings 做 Kun runtime adapter switcher。
- migration 必须 dry-run / backup / recoverable。

验收：

- 用户能知道升级会改什么、失败如何恢复、卸载保留什么。

### 1.4 1.0 核心用户旅程

发布前必须用真实应用跑通以下旅程，每条都要留下截图或命令证据：

1. Fresh install：从 release artifact 安装，首次启动，doctor 通过或给出明确恢复路径。
2. First safe task：选择 workspace，运行只读任务，看到 evidence、route/cache/usage/cost。
3. First write task：生成 diff，`Deny` 不写入。
4. Approval path：重新生成 diff，`Allow once` 应用，文件变化可见。
5. Recovery path：对已应用 ChangeSet 执行 `Rollback`，文件恢复。
6. Failure path：模拟 bridge offline / dependency missing，UI 显示结构化错误和 recovery action。
7. Automation path：创建本地 schedule，pause / resume / disable / delete，触发时有 audit。
8. Notification path：task complete / failed / approval required / drift detected 通知或 unavailable 状态可见，payload 脱敏。
9. Diagnostics path：生成 redacted bundle，secret scan 通过。
10. Upgrade / uninstall path：旧配置 dry-run migration，backup，升级，卸载或保留用户数据。

### 1.5 1.0 产品完成定义

只有同时满足以下条件，才能说 `1.0` 正式发布准备完成：

- 外部用户不读源码也能完成安装、配置、第一个任务、审批、回滚、诊断。
- Desktop 页面覆盖 Onboarding、Home、Workspace、Task Center、Task Detail、Approval、Automation、Diagnostics、Settings。
- 公开文档覆盖 Quick Start、Troubleshooting、Security、Compatibility、Contributing、Issue Template。
- Release artifact 有 manifest、checksum、版本矩阵和可复现 build input。
- Diagnostics、audit、notification、logs 通过 secret / raw prompt / raw response / reasoning_content redaction 验收。
- 所有 prior specs strict validate 通过。
- 1.0 gate 不依赖人工口头解释，必须有命令、截图、artifact 或测试证据。

## 2. 事实依据

确定：

- `1.0` release line 是 Stable Public Release。
- PRD TechPlan 规定 `1.0` 必须做 Public README / Quick Start / Troubleshooting、artifact checksum、install / upgrade / uninstall smoke、config migration、diagnostics bundle、privacy / security / permission 文档、issue template、security policy、contributing guide。
- PRD TechPlan 明确 `1.0` 不做企业 SSO / SCIM、云端多租户、商业计费、公开插件市场、企业 policy center、实时多人协作。
- `1.0` gate 需要 prior gates 通过，或未通过 gate 有 blocker / 延期豁免。

前置 gate：

- `0.1.x` CLI-first public alpha gate 已关闭。
- `0.2.x` Desktop Code Workbench gate 已通过。
- `0.3.x` General Workspace Agent gate 已通过。
- `0.4.x` Integrations and Automation Preview gate 已通过并归档。
- 所有 active OpenSpec change 已清空；历史完成 change 也已归档到 `openspec/changes/archive/2026-06-18-*`。

当前工作区事实（确定，2026-06-18，只作为接手时的起点，执行前必须重跑命令确认）：

- `/Users/bluth/Code/deepseek_runtime`：`kun-runtime-adapter` 分支已存在，commit `e86c2db Add Kun runtime bridge adapter | 增加 Kun Runtime 桥接适配`；`develop` 无 tracked 修改，仍在 `v0.1.1-alpha.1` / `origin/develop`。若看到 `.agent/`、`.claude/`、`.codex/`、`.opencode/`、`.trae/`、`openspec/` 等 untracked 本地工具目录，不要提交或删除，除非用户明确要求。
- `/Users/bluth/Code/Kun`：已提交 `adee610 Add opt-in DeepSeek runtime adapter | 增加可选 DeepSeek Runtime 适配`；`vendor/deepseek_runtime` 指向 `kun-runtime-adapter` 的 `e86c2db`；仍有未提交测试修复 `kun/src/adapters/tool/output-accumulator.ts` 和 `kun/tests/loop.test.ts`，全量 `npm run test` 尚未确认通过。
- `/Users/bluth/Code/deepseekagent`：Desktop UI refresh、`1.0.0` 版本对齐、`0.4.x` archive、`refresh-consumer-desktop-ui` archive、`prepare-stable-public-release` archive、public docs 和 release evidence 已写入工作区；根仓库和 `docs/llm-harness-agent` 子模块仍需 commit。
- 原深色 UI 草稿已保护在 stash：`wip-dark-ui-experiment-before-consumer-refresh`。
- `.omo/` 和 Kun 的 `.agents/` 是未跟踪目录；继续忽略，不纳入本轮。

需要重新核验：

- 当前 packaging 方式。
- 支持平台矩阵。
- runtime tag / app version / CLI version 对齐。
- release artifact checksum 机制。
- public docs 链接和安装命令。
- diagnostics redaction 是否覆盖最新日志和 event schema。

验证命令：

```bash
python3 scripts/check_repo.py
openspec list
git status --short --branch
rg -n "Stable Public Release|install|upgrade|uninstall|diagnostics|checksum|Security Policy|Troubleshooting" \
  docs/prd-tech-plan README.md SECURITY.md docs/TROUBLESHOOTING.md docs/llm-harness-agent/zh/prd-tech-plan
```

## 3. 关键决策

- `1.0` 是稳定化和公开发布，不是功能扩张。
- 未完成能力必须显式延期；当前不再以 `0.4.x` 作为 blocker，但 1.0 只做稳定发布准备，不允许临时塞入新 assistant 大功能。
- Public docs 必须覆盖 happy path 和失败恢复。
- Diagnostics bundle 必须 redaction，不能包含 API key、secret、未授权文件正文或 raw reasoning_content。
- Release artifact 必须有 manifest 和 checksum 或等价完整性校验。
- Migration / rollback 是 gate，不是 release note。
- E4-style 真实任务报告必须可验证成功率、首次完成率、失败样本、人工接管和每成功任务 token / cost。

## 4. 非目标

- 不做企业 SSO / SCIM。
- 不做云端多租户。
- 不做商业计费。
- 不做公开插件市场。
- 不做企业 policy center。
- 不做实时多人协作。
- 不在 1.0 前临时引入大功能。
- 不发布没有 rollback / uninstall / diagnostics 的“看起来可用”版本。

## 5. 实施步骤

### 5.0 当前前置收口恢复计划

本节是 2026-06-18 之后接手 AI 的第一执行顺序。先完成本节，再进入 `prepare-stable-public-release` 的 1.0 稳定发布准备任务。

#### 5.0.1 接手前只读核对

在三个仓库分别执行：

```bash
git -C /Users/bluth/Code/deepseekagent status --short --branch
git -C /Users/bluth/Code/deepseekagent/docs/llm-harness-agent status --short --branch
git -C /Users/bluth/Code/deepseek_runtime status --short --branch
git -C /Users/bluth/Code/deepseek_runtime branch --list kun-runtime-adapter
git -C /Users/bluth/Code/Kun status --short --branch
git -C /Users/bluth/Code/Kun submodule status vendor/deepseek_runtime
```

预期：

1. `deepseek_runtime` 的 `develop` 没有 tracked 修改，`kun-runtime-adapter` 存在。
2. Kun 至少 ahead 1，且可能还有 `output-accumulator.ts`、`loop.test.ts` 未提交。
3. DeepSeekAgent 根仓库包含 Desktop UI refresh、OpenSpec archive、1.0 prep change 和 docs 子模块改动。
4. 不处理 `.omo/`、Kun `.agents/`、runtime 本地 agent 配置目录。

如果预期不成立：

- 不要回滚用户改动。
- 先用 `git diff --stat` 和 `git diff -- <file>` 看差异来源。
- 只在明确属于本计划时继续；不相关改动保持未触碰。

#### 5.0.2 完成 Kun 测试收口

已知状态：

- `kun/src/adapters/tool/output-accumulator.ts` 已增加短 ASCII 流式输出解码，用于修复 `echo ready; sleep 5` 运行中 snapshot 为空的问题。
- `kun/tests/loop.test.ts` 已开始修复 active goal 测试挂起：active goal 下模型 `stop` 会继续 loop，测试必须让模型调用 `update_goal` 完成目标，不能依赖旧的 silent stop 行为。
- `tests/loop.test.ts` 全文件和 `npm run test` 还没有最终确认通过。

继续步骤：

1. 先跑已经定位过的用例：

   ```bash
   cd /Users/bluth/Code/Kun/kun
   npx vitest run tests/builtin-tools.test.ts -t "returns a pollable bash session" --reporter=verbose --testTimeout=10000
   npx vitest run tests/loop.test.ts -t "records elapsed seconds" --reporter=verbose --testTimeout=10000
   ```

2. 跑 `loop.test.ts` 全文件：

   ```bash
   npx vitest run tests/loop.test.ts --reporter=dot --testTimeout=10000
   ```

3. 如果 `loop.test.ts` 仍挂起，用逐条定位脚本找第一个 timeout 标题：

   ```bash
   node - <<'NODE'
   const fs = require('node:fs');
   const { spawnSync } = require('node:child_process');
   const cwd = '/Users/bluth/Code/Kun/kun';
   const text = fs.readFileSync(`${cwd}/tests/loop.test.ts`, 'utf8');
   const titles = [...text.matchAll(/\bit\('([^']+)'/g)].map((m) => m[1]);
   for (const title of titles) {
     const result = spawnSync('npx', ['vitest', 'run', 'tests/loop.test.ts', '-t', title, '--reporter=dot', '--testTimeout=10000'], {
       cwd,
       encoding: 'utf8',
       timeout: 20000,
       maxBuffer: 1024 * 1024 * 5
     });
     const status = result.error?.code === 'ETIMEDOUT' ? 'TIMEOUT' : result.status === 0 ? 'PASS' : 'FAIL';
     console.log(`${status} ${title}`);
     if (status !== 'PASS') {
       process.stdout.write(result.stdout || '');
       process.stderr.write(result.stderr || '');
       process.exit(1);
     }
   }
   NODE
   ```

4. 修复规则：

   - 如果挂起原因是 active goal：测试模型必须调用 `update_goal` 完成或阻塞 goal；不要改业务逻辑去允许 active goal 下 silent stop。
   - 如果挂起原因是输出流：优先修测试或 output accumulator 的可解释边界；不要改变 tool API。
   - 每次只修一个挂起原因，修完立刻跑对应单测。

5. Kun gate：

   ```bash
   npm run typecheck
   npm run test
   npm run build
   ```

完成后提交 Kun 测试收口，建议 commit：

```text
Stabilize Kun runtime adapter tests | 稳定 Kun Runtime 适配测试
```

commit body 必须包含 `English:` 和 `简体中文:` 两段。

#### 5.0.3 完成 DeepSeekAgent UI refresh 收口

已知状态：

- `refresh-consumer-desktop-ui` change 已完成并归档。
- `apps/desktop/DESIGN.md` 已新增消费级 UI 设计规范。
- `apps/desktop/src/App.tsx` 和 `styles.css` 已改为浅色 Codex-like 消费级壳。
- Desktop / bridge / Python package 可见版本已对齐到 `1.0.0`；runtime pin 仍是 `v0.1.1-alpha.1`。
- 截图已生成：
  - `apps/desktop/test-results/desktop-code-workbench-1280.png`
  - `apps/desktop/test-results/desktop-code-workbench-390.png`
- `openspec/changes/archive/2026-06-18-refresh-consumer-desktop-ui/tasks.md` 已全部勾选，主规格已同步到 `openspec/specs/consumer-desktop-ui/spec.md`。

继续步骤：

1. 跑 UI change 验证：

   ```bash
   cd /Users/bluth/Code/deepseekagent
   openspec validate refresh-consumer-desktop-ui --type change --strict
   cd apps/desktop && npm run test
   npm run build && npm run e2e
   ```

2. 人工打开截图或 dev server 核查：

   ```bash
   cd /Users/bluth/Code/deepseekagent/apps/desktop
   npm run dev
   ```

3. UI 验收点：

   - 浅色消费级个人助理风格，不是深色 IDE 或运营后台。
   - 左侧 sidebar、主工作区、任务入口可见。
   - desktop `1280x820` 和 mobile `390x860` 无水平溢出、无文字重叠。
   - Code / Workspace / Automation 现有入口仍可用。
   - `Allow once`、`Deny`、`Rollback` 不回归。
   - 不出现伪造 cache hit rate、routing graph、telemetry HUD。

4. 若后续修改 UI，必须重新开 patch change；不要改已归档任务作为新工作入口。

#### 5.0.4 完成 0.4 archive 与 1.0 prep artifact 收口

已知状态：

- `start-integrations-automation-preview` 已从 active change 移入 archive 工作区。
- `openspec/specs/integrations-automation-preview/spec.md` 已生成。
- `prepare-stable-public-release` 已完成并归档，当前 1.0 稳定发布主规格在 `openspec/specs/stable-public-release/spec.md`。

验证：

```bash
cd /Users/bluth/Code/deepseekagent
openspec validate integrations-automation-preview --type spec --strict
openspec validate desktop-code-workbench-first-slice --type spec --strict
openspec validate general-workspace-agent --type spec --strict
openspec validate stable-public-release --type spec --strict
openspec list --json
```

预期：

- `start-integrations-automation-preview` 不再出现在 active list。
- `refresh-consumer-desktop-ui` 和 `prepare-stable-public-release` 不再出现在 active list。
- `openspec list --json` 返回空 changes 列表。

#### 5.0.5 根仓库 gate 与提交顺序

DeepSeekAgent gate：

```bash
cd /Users/bluth/Code/deepseekagent
python3 scripts/check_repo.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
git diff --check
cd apps/desktop && npm run test && npm run build && npm run e2e
```

提交顺序：

1. `/Users/bluth/Code/Kun`：提交 Kun 测试收口。不要提交 `.agents/`。
2. `/Users/bluth/Code/deepseekagent/docs/llm-harness-agent`：提交计划资产、Blueprint、PRD TechPlan 对齐。
3. `/Users/bluth/Code/deepseekagent`：提交 Desktop UI refresh、OpenSpec archive、`prepare-stable-public-release`、docs 子模块 gitlink。
4. `/Users/bluth/Code/deepseek_runtime`：不要在 `develop` 提交本地 agent 配置目录；`kun-runtime-adapter` 已有 adapter commit，除非后续测试发现必须补丁。

建议 DeepSeekAgent 根仓库 commit：

```text
Prepare 1.0 readiness and refresh desktop UI | 完成 1.0 前置收口并刷新桌面 UI
```

交付时必须告诉用户如何验收，至少包含：

```bash
cd /Users/bluth/Code/deepseekagent
python3 scripts/check_repo.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
openspec validate integrations-automation-preview --type spec --strict
openspec validate consumer-desktop-ui --type spec --strict
openspec validate stable-public-release --type spec --strict
cd apps/desktop && npm run test && npm run build && npm run e2e

cd /Users/bluth/Code/Kun/kun
npm run typecheck
npm run test
npm run build

cd /Users/bluth/Code/deepseek_runtime
git switch develop
git status --short --branch
git branch --list kun-runtime-adapter
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

### 5.1 Release freeze

已创建 change：

```text
prepare-stable-public-release
```

步骤：

1. 列出所有 active OpenSpec changes。
2. 每个 change 标记：
   - in 1.0。
   - deferred。
   - archived。
   - blocker。
3. 冻结功能范围。
4. 冻结 public API 和 config schema。
5. 建立 release checklist。

验证：

```bash
openspec list
openspec status --change prepare-stable-public-release
openspec validate prepare-stable-public-release --type change --strict
```

### 5.2 Version and compatibility matrix

1. 定义版本：
   - DeepSeekAgent app version。
   - CLI version。
   - runtime version。
   - desktop version。
2. 定义平台矩阵：
   - macOS。
   - Linux。
   - Windows，如未支持必须明确。
3. 定义 Python / Node / Electron 支持范围。
4. 定义 DeepSeek provider capability snapshot。
5. 文档中写清兼容限制。

验证：

```bash
rg -n "Compatibility|Limits|Python|Node|Electron|macOS|Linux|Windows" README.md docs
```

### 5.3 Install / upgrade / uninstall smoke

1. 从干净目录安装。
2. 配置 API key，不记录 secret。
3. 运行 doctor。
4. 执行 read-only task。
5. 执行 write task + approval + rollback。
6. 从旧 config 升级。
7. 卸载并确认清理范围。
8. 记录 smoke 输出和 artifact hash。

验证：

```bash
python3 scripts/check_repo.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
# 具体 install/upgrade/uninstall 命令在 1.0 OpenSpec 中固定
```

### 5.4 Config migration

1. 列出现有 config schema。
2. 为每个历史 schema 写 migration。
3. migration 必须：
   - 幂等。
   - 可 dry-run。
   - 可 backup。
   - 失败可恢复。
4. migration 不打印 secret。
5. migration 结果进入 diagnostics。

验证：

```bash
rg -n "migration|config schema|dry-run|backup" src apps tests docs
```

### 5.5 Diagnostics bundle

1. bundle 内容：
   - app version。
   - runtime version。
   - platform。
   - config summary。
   - redacted logs。
   - event refs。
   - recent errors。
2. redaction：
   - API key。
   - secret token。
   - Authorization。
   - password。
   - raw reasoning_content。
   - 未授权文件正文。
3. bundle 生成命令或 UI action。
4. bundle schema 文档。

验证：

```bash
rg -n "DiagnosticsBundle|diagnostics bundle|redacted_logs|reasoning_content" src apps tests docs
python3 scripts/check_repo.py
```

### 5.6 Release artifact and checksum

1. 生成 release manifest。
2. 生成 checksum。
3. 验证 checksum。
4. 记录 build input：
   - commit。
   - version。
   - dependency lock。
   - platform。
5. artifact 不包含 `.env`、key、local logs。
6. 文档写清用户如何验证 artifact。

验证：

```bash
python3 scripts/build_release_artifact.py --help
python3 scripts/release_gate_audit.py --help
rg -n "checksum|manifest|artifact" README.md docs scripts
```

### 5.7 Public documentation

1. Public README：
   - 产品定位。
   - Quick Start。
   - install。
   - first task。
   - safety model。
   - troubleshooting link。
2. Troubleshooting：
   - doctor fails。
   - install fails。
   - provider fails。
   - permission denied。
   - stale diff。
   - rollback fails。
   - diagnostics redaction。
3. Security：
   - secret handling。
   - permission model。
   - local-first。
   - report security issue。
4. Contributing：
   - dev setup。
   - tests。
   - OpenSpec workflow。
5. Issue templates：
   - bug report。
   - security route。
   - diagnostics attachment rules。

验证：

```bash
python3 scripts/check_repo.py
rg -n "Quick Start|Troubleshooting|Security Policy|Contributing|issue template|diagnostics" README.md SECURITY.md docs .github
```

### 5.8 E4-style release evidence report

1. 固定真实任务集。
2. 对每个任务记录：
   - success/failure。
   - first-pass completion。
   - failure sample。
   - human intervention。
   - rollback。
   - token。
   - cache hit/miss。
   - cost。
3. 报告不包含 secret、raw prompt、raw response、raw reasoning_content。
4. 报告能复核每成功任务 cost。

验证：

```bash
rg -n "success|first-pass|failure sample|human intervention|cost per successful task|cache" benchmarks docs scripts
```

### 5.9 Release candidate and final release

1. 创建 release candidate branch 或 tag。
2. 跑完整 gate。
3. 修复 blocker。
4. 复跑完整 gate。
5. 确认 worktree clean。
6. 创建双语 commit 和 tag。
7. 推送 remote。
8. 发布 release notes。

验证：

```bash
git status --short --branch
python3 scripts/check_repo.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
cd apps/desktop && npm run test && npm run build && npm run e2e
```

## 6. 验证命令

```bash
python3 scripts/check_repo.py
openspec validate prepare-stable-public-release --type change --strict
PYTHONPATH=src python3 -m unittest discover -s tests -v
cd apps/desktop && npm run test && npm run build && npm run e2e
rg -n "Stable Public Release|Quick Start|upgrade|uninstall|diagnostics bundle|checksum|manifest|Security Policy|Contributing" \
  README.md SECURITY.md docs scripts apps
```

## 7. 完成定义

`1.0` 完成必须满足：

- Prior gates 已通过，或未通过项有明确 blocker / 延期豁免。
- Public install 通过。
- Upgrade / migration / uninstall tests 通过。
- Build manifest + checksum verification 通过。
- Diagnostics redaction tests 通过。
- Route / cache / evidence smoke 通过。
- E4-style 真实任务证据报告可验证成功率、首次完成率、失败样本、人工接管和每成功任务 token / cost。
- Public README、Quick Start、Troubleshooting、Security、Contributing、Issue Template 完整。
- `production_release_gate` 状态与 Blueprint / manifest 一致。
- 远端 tag、release notes、artifact 和 checksum 可复核。
