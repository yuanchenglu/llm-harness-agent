# 03. Desktop Code Workbench 首片计划

## 0. AI 执行提示词

你是 `0.2.x Desktop Code Workbench` 首片实现代理。你的任务是证明桌面 UI 是本地 runtime 的前端，而不是新的 agent loop。执行前必须核对 `start-desktop-code-workbench` OpenSpec、`deepseek_runtime` tag、当前 `apps/desktop` 状态和验证命令。严禁 UI 直接写文件、拼装独立 agent prompt、伪造 runtime 状态或绕过 permission / ChangeSet / rollback。实现时优先完成真实 diff -> `Allow once` -> apply -> rollback 闭环，再做视觉细节。

## 1. 目标

在 `deepseekagent` 主仓库启动 `0.2.x Desktop Code Workbench` 首片，实现一条真实、可验证、可回滚的桌面工作流：

```text
选择代码工作区
-> 提交任务
-> Agent 读取/搜索工作区
-> Agent 提出 diff
-> 用户审批 apply
-> 用户 rollback
-> UI 展示 evidence、route/cache/usage/cost
```

首片必须证明桌面 UI 是 runtime 的前端，而不是新的 agent loop。

## 2. 事实依据

确定：

- `0.2.x` 的目标是把 runtime 接到桌面 UI，形成可信的桌面 Code 工作台。
- UI/UX 当前只保留信息架构、导航模型、关键页面线框和交互原则。
- Code 是 `0.2.x` 主线；助理模式是 `0.3.x` 主线；连接手机不是当前主线。
- 技术栈已收敛为 React + TypeScript、Electron first、Local HTTP/SSE bridge。
- 首片需要真实 diff/apply/rollback，因此依赖 runtime 后续公开 ChangeSet API。

验证命令：

```bash
python3 scripts/check_repo.py
rg -n "Desktop Code Workbench|Local HTTP/SSE|React \\+ TypeScript|Electron|diff review|rollback" \
  docs/llm-harness-agent/zh/prd-tech-plan
```

## 3. 关键决策

- 工程位置：`apps/desktop`。
- Desktop shell：Electron first。
- UI：React + TypeScript + Vite。
- Bridge：FastAPI + SSE。
- Runtime 依赖：Git tag pin 到 `7colorai/deepseek_runtime` 的 `v0.1.1-alpha.1`。
- diff 来源：Agent 调用 bridge 提供的 `propose_change` 工具，bridge 生成 ChangeSet 和 diff。
- 写入边界：只有用户点击 `Allow once` 后，bridge 才调用 `ChangeManager.apply`。
- 回滚边界：只有已应用且 rollback token 未消费的 ChangeSet 可以 rollback。
- UI evidence：只能展示 safe evidence，不展示 API key、raw reasoning_content 或公开 raw prompt/response。

## 4. 非目标

- 不做助理模式。
- 不做连接手机。
- 不做定时任务。
- 不做团队共享规则。
- 不做插件市场。
- 不做 hosted service。
- 不做高保真视觉稿。
- 不支持 delete、rename、binary diff、shell、network、git mutating。
- 不让 UI 直接写文件。

## 5. 实施步骤

### 5.1 OpenSpec

1. 创建 change：`start-desktop-code-workbench`。
2. 写清 proposal、design、tasks、spec delta。
3. OpenSpec 必须说明：
   - UI 通过 local runtime bridge 启动任务。
   - UI 不伪造 runtime 状态。
   - diff/apply/rollback 由 bridge 调 runtime safety API。
   - 首片只覆盖 Code 工作台。

验证：

```bash
openspec status --change start-desktop-code-workbench
openspec validate start-desktop-code-workbench --type change --strict
```

### 5.2 Desktop 工程骨架

1. 创建 `apps/desktop`。
2. 使用 `npm`，不引入 root 级 Node workspace。
3. 建立 Vite React TypeScript 工程。
4. 建立 Electron main/preload。
5. scripts 固定为：
   - `npm run setup:bridge`
   - `npm run dev:bridge`
   - `npm run dev:vite`
   - `npm run dev:electron`
   - `npm run dev`
   - `npm run build`
   - `npm run test`
   - `npm run e2e`

### 5.3 FastAPI + SSE bridge

创建 `apps/desktop/runtime_bridge`。

Python 依赖：

```text
deepseek-runtime @ git+https://github.com/7colorai/deepseek_runtime.git@v0.1.1-alpha.1
fastapi
uvicorn[standard]
pydantic
```

固定端口：

- Vite：`127.0.0.1:5173`
- Bridge：`127.0.0.1:8765`

Bridge API：

- `GET /health`
- `POST /workspaces/inspect`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `GET /tasks/{task_id}/events`
- `POST /tasks/{task_id}/changesets/{change_set_id}/approve`
- `POST /tasks/{task_id}/changesets/{change_set_id}/rollback`

SSE event names：

- `task.created`
- `task.started`
- `runtime.completed`
- `changeset.proposed`
- `approval.required`
- `changeset.applied`
- `changeset.rolled_back`
- `task.failed`
- `task.completed`

### 5.4 Agent tools

可用工具：

- `read_file`
- `search`
- `propose_change`

`propose_change` 的 `input` 必须是 JSON 字符串：

```json
{
  "path": "relative/path",
  "new_content": "...",
  "summary": "..."
}
```

Bridge 负责：

1. 校验 path 在 workspace 内。
2. 计算 `original_sha256`。
3. 创建 `FileChange` 和 `ChangeSet`。
4. 调用 `ChangeManager.preview` 生成 unified diff。
5. 写入 pending changeset store。
6. 通过 SSE 发出 `changeset.proposed` 和 `approval.required`。

### 5.5 Persistence

写入工作区内：

```text
.deepseekagent/desktop/events/{task_id}.jsonl
.deepseekagent/desktop/changesets/{task_id}.json
.deepseekagent/desktop/rollbacks/{task_id}-{change_set_id}.json
```

要求：

- event log 不包含 API key。
- event log 不包含 raw reasoning_content。
- public evidence 使用 `RuntimeResult.to_safe_dict()`。
- rollback token 只能消费一次。

### 5.6 UI

只启用 Code 模式。

布局：

- 左侧 rail：Code、工作区、新建需求、任务、变更、成本与缓存。
- 顶栏：workspace path、git branch、dirty summary、bridge health。
- 主区：workspace empty、workspace selected、task running、needs approval、completed、failed。
- 右侧 panel：`Evidence`、`Cost/Cache`、`Approval`。

新建需求表单字段：

- 背景
- 目标
- 验收标准
- 约束
- 参考资料

Approval controls：

- `Deny`
- `Allow once`
- `Rollback`

按钮必须有 loading、success、failure、disabled 状态。

## 6. 测试计划

Runtime patch tests：

- top-level imports。
- preview/apply/rollback。
- path escape。
- permission deny。
- release audit。

Bridge tests：

- `GET /health`。
- workspace inspect。
- read-only task。
- propose-change task。
- SSE 收到 `changeset.proposed`。
- approve 后文件改变。
- rollback 后文件恢复。
- deny 不写文件。
- event log 不泄露 secret。

Frontend tests：

- workspace 状态渲染。
- 任务提交。
- SSE 更新任务状态。
- diff panel 展示 unified diff。
- approval buttons 状态切换。
- error banner 给出恢复路径。

E2E：

- 启动 bridge、Vite、Electron 或 Playwright Chromium。
- 选择临时 git 工作区。
- 提交会修改 fixture 文件的任务。
- 看到 diff。
- `Allow once` 后文件改变。
- `Rollback` 后文件恢复。
- console 无相关 error/warn。

## 7. 验证命令

```bash
python3 scripts/check_repo.py
cd apps/desktop
npm run test
npm run build
npm run e2e
```

Browser 验证：

- 优先使用 Codex Browser 插件打开本地 app。
- 检查 desktop viewport 和一个窄 viewport。
- 确认页面非空、无 Vite/Electron overlay、主流程可点击、文本不溢出、按钮不跳动。

## 8. 完成定义

首片只有在以下条件全部满足时才算完成：

- `start-desktop-code-workbench` OpenSpec strict validate 通过。
- Desktop 可以通过 bridge 创建任务。
- UI 状态来自 bridge/runtime，不是 hard-coded mock。
- Agent 可以提出 ChangeSet。
- 用户可以看到真实 diff。
- `Allow once` 会真实写入文件。
- `Rollback` 会真实恢复文件。
- Evidence、route/cache/usage/cost 在 UI 中可见。
- 错误和 bridge crash 有明确 UI 状态。
- 所有验证命令通过，未通过项必须有明确 blocker。
