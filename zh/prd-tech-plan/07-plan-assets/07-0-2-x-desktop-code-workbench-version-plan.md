# 07. `0.2.x` Desktop Code Workbench 版本研发计划

## 0. AI 执行提示词

你是 `0.2.x Desktop Code Workbench` 版本负责人。你的目标是把首片闭环推进成可试用的桌面 Code 工作台，而不是扩成通用助理或移动连接。先核对 `03-desktop-code-workbench-first-slice-plan.md`、`start-desktop-code-workbench` OpenSpec、`apps/desktop` 当前状态和 PRD TechPlan。任何 UI 状态必须来自 bridge/runtime；任何写入必须经过 ChangeSet、approval、rollback。不要做 Assistant mode、phone connection、团队共享、插件市场或 hosted service。

## 1. 目标

在 `0.2.x` 中，把 Desktop 首片从“证明真实 diff/apply/rollback 闭环”推进到“开发者可以实际使用的桌面 Code 工作台 alpha”。

版本完成后，用户应能：

1. 安装或启动桌面 app。
2. 选择代码工作区。
3. 创建、查看、恢复 Code 任务。
4. 看见 runtime health、task status、evidence、route/cache/usage/cost。
5. 审查 diff、批准一次写入、拒绝写入、执行 rollback。
6. 在 bridge/runtime crash 时看到明确错误和恢复路径。

## 2. 事实依据

确定：

- `0.2.x` release line 的目标是 Desktop Code Workbench。
- 技术栈是 Electron first、React + TypeScript、FastAPI + SSE、Python runtime。
- runtime truth 在 Python；desktop 只是 runtime 前端。
- `deepseek-runtime` 需要通过 tag pin 使用。
- `start-desktop-code-workbench` 已定义首片范围：workspace inspect、task create、SSE、ChangeSet proposal、approval、rollback。

需要重新核验：

- `apps/desktop` 当前实现是否已提交。
- `start-desktop-code-workbench` 是否已 archive。
- `deepseek_runtime` 最新可用 tag 是否仍是桌面依赖期望版本。
- 当前 Node / Python / Playwright 环境是否能跑完整 gate。

验证命令：

```bash
git status --short --branch
openspec instructions apply --change start-desktop-code-workbench --json
cd apps/desktop && npm run test && npm run build && npm run e2e
python3 scripts/check_repo.py
```

## 3. 关键决策

- `0.2.x` 只做 Code Workbench，不做 General Workspace。
- `apps/desktop` 留在 DeepSeekAgent 主仓库。
- Bridge 继续使用 `127.0.0.1:8765`，Vite dev 使用 `127.0.0.1:5173`。
- UI 不直接写文件，不直接读任意文件，不保存 API key。
- Task event log 是 workspace-local JSONL；SQLite 仍是 optional，不作为版本前置。
- 审批语义固定为 `Deny`、`Allow once`、`Rollback`。
- 版本应优先补硬化、恢复、打包、可用性，而不是增加模式。

## 4. 非目标

- 不做 Assistant mode。
- 不做连接手机。
- 不做文档/表格通用工作台。
- 不做定时任务。
- 不做 MCP/tool marketplace。
- 不做团队共享或企业策略。
- 不把 runtime 改写成 TypeScript。
- 不支持 shell/network/git mutating/delete/rename/binary 写入工具，除非后续版本重新开 OpenSpec。

## 5. 实施步骤

### 5.1 版本基线审计

1. 检查 `apps/desktop` 是否存在并能跑完整 gate。
2. 检查 `runtime_bridge/requirements.txt` 是否 pin 到已验证 runtime tag。
3. 检查 bridge API 是否覆盖 `/health`、workspace inspect、tasks、events、approval、rollback。
4. 检查 UI 是否包含 workspace chooser、task form、event list、evidence panel、diff review。
5. 若 `start-desktop-code-workbench` 已 all_done，准备 archive；若未 all_done，先完成首片。

建议 OpenSpec：

```text
harden-desktop-code-workbench
```

### 5.2 Bridge hardening

1. 给 local bridge 增加 origin 限制和 CSRF/loopback 防护。
2. 给 approval route 增加明确状态机：
   - pending -> denied。
   - pending -> applied。
   - applied -> rolled_back。
   - rolled_back 不可再次 rollback。
3. 给 bridge 增加 crash / timeout / dependency missing 的结构化错误。
4. 给 event stream 增加 reconnect-friendly 行为：
   - 已有事件可重放。
   - 新事件按序追加。
   - task snapshot 可补全状态。
5. 给 workspace path 增加更强限制：
   - path escape。
   - symlink escape。
   - binary / large file。
   - hidden `.git` mutating 禁止。

验证：

```bash
cd apps/desktop
npm run test:bridge
```

### 5.3 Task Center / Task Detail

1. 增加任务列表：
   - task id。
   - workspace。
   - status。
   - updated time。
   - pending approvals。
   - cost/cache summary。
2. 增加任务详情页：
   - timeline。
   - evidence events。
   - pending/applied/denied changesets。
   - errors。
   - recovery actions。
3. 增加 task refresh：
   - 从 snapshot 恢复 UI。
   - SSE 断开后仍可手动刷新。
4. 增加空状态和错误状态：
   - no workspace。
   - bridge offline。
   - runtime dependency missing。
   - permission denied。
   - stale original hash。

验证：

```bash
cd apps/desktop
npm run test:frontend
```

### 5.4 Runtime manager

1. Electron main process 管理 bridge 启动/停止。
2. UI topbar 展示 bridge process、runtime version、health。
3. bridge 启动失败时提供可复制的诊断摘要。
4. 退出 app 时清理子进程。
5. dev 模式和 packaged 模式分开处理。

验证：

```bash
cd apps/desktop
npm run build
npm run e2e
```

### 5.5 Packaging alpha

1. 增加 desktop alpha build manifest。
2. 记录 Node、Electron、Python、runtime tag、platform。
3. 提供本地启动说明。
4. 提供 cleanup/uninstall 说明。
5. 提供 diagnostics bundle，必须 redaction。

验证：

```bash
cd apps/desktop
npm run build
python3 ../../scripts/check_repo.py
```

### 5.6 Version gate

`0.2.x` gate 必须证明：

1. UI 不伪造 runtime 状态。
2. diff/approval/rollback 与 runtime 语义一致。
3. bridge crash 不静默。
4. task detail 能展示 evidence、未验证项、人工接管和 cost。
5. 真实临时工作区 E2E 通过。

## 6. 验证命令

```bash
python3 scripts/check_repo.py
openspec validate harden-desktop-code-workbench --type change --strict
cd apps/desktop
npm run test
npm run build
npm run e2e
rg -n "deepseek-runtime @ git\\+https://github.com/7colorai/deepseek_runtime.git@v0\\.1\\.1-alpha\\.1|Allow once|Rollback|EventSource|127\\.0\\.0\\.1:8765" .
```

## 7. 完成定义

`0.2.x` 完成必须满足：

- `0.2.x` 对应 OpenSpec change strict validate 通过。
- Desktop 可从干净 clone 安装依赖并启动。
- UI 可选择工作区、创建任务、查看 task detail。
- UI 可见 evidence、route/cache/usage/cost。
- `Allow once` 真实写入，`Deny` 不写入，`Rollback` 恢复原内容。
- bridge/runtime 错误有结构化 UI。
- `npm run test`、`npm run build`、`npm run e2e` 通过。
- `python3 scripts/check_repo.py` 通过。
- 未完成项明确延期到 `0.3.x` 或后续 patch，不藏在文档里。

