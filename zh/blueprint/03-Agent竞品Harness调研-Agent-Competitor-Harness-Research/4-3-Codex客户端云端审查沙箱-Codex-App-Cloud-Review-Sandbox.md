# 4-3 Codex App Cloud Review Sandbox 调研 Codex App Cloud Review Sandbox

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

## 1. 目标

回答：Codex App / Web / Cloud 相比 CLI 强在哪里？它的任务、review、sandbox、worktree 对 DeepSeek Agent 有什么启发？

---

## 2. Codex App：桌面 command center

Codex App 官方文档称其为 focused desktop experience / command center，支持 parallel threads、worktree support、automations、Git functionality。来源：[Codex App overview](https://developers.openai.com/codex/app)。

App 新建 thread 可选择：

```text
Local：直接在当前项目目录工作
Worktree：隔离到 Git worktree
Cloud：在配置好的 cloud environment 远程运行
```

来源：[Codex App modes](https://developers.openai.com/codex/app/features)。

### 对 DeepSeek Agent 的启发

我们的桌面端应参考：

```text
Thread / Task list
Local mode
Worktree isolation
Future Cloud mode
Task sidebar
Review pane
Integrated terminal
```

---

## 3. Worktree 支持

Codex App 支持 Worktree：Local 在当前项目中工作；Worktree 会创建新的 Git worktree，隔离更改，适合并行尝试新想法或独立任务。来源：[Worktree support](https://developers.openai.com/codex/app/features)。

### DeepSeek Agent 启发

MVP 可以先做：

```text
默认 local project
可选 git worktree task sandbox
多任务隔离
每个任务一个 checkpoint / diff / route trace
```

---

## 4. Integrated Terminal

Codex App 每个 thread 都有 scoped terminal，可用于验证更改、运行脚本、执行 Git 操作；Codex 能读取当前 terminal output，参考失败 build 或运行中的 dev server 状态。来源：[Integrated terminal](https://developers.openai.com/codex/app/features)。

### DeepSeek Agent 启发

DeepSeek Agent 的终端不应只是日志输出，而应是：

```text
per-task terminal
captured terminal output
tool-result context
failed build diagnosis input
permission-scoped execution
```

---

## 5. Review Pane

Codex App 的 review pane 反映 Git repo 状态，默认关注 uncommitted changes，也可切 all branch changes 或 last turn changes；支持 inline comments、stage/revert、PR feedback loop。来源：[Review pane](https://developers.openai.com/codex/app/review)。

### DeepSeek Agent 启发

这非常适合我们的 Code Mode：

```text
diff pane
last-turn changes
full branch changes
inline comments
stage/revert
Pro review comments
PR feedback ingestion
```

但 DeepSeek Agent 应增加：

```text
Flash-generated diff
Pro reviewer comments
cache/cost of review
checkpoint-linked review
```

---

## 6. Codex Web / Cloud

Codex Web 官方文档说明，Codex cloud 可以在自己的 cloud environment 中 background/parallel 工作，并可连接 GitHub、创建 PR。来源：[Codex Web](https://developers.openai.com/codex/cloud)。

### DeepSeek Agent 启发

纯客户端 MVP 不应一开始复制 cloud sandbox，但应预留：

```text
Remote runner interface
Task queue
Cloud execution backend
PR creation workflow
Evidence logs
```

---

## 7. Permissions / Sandbox

Codex permissions 支持 built-in profiles：

```text
:read-only
:workspace
:danger-full-access
```

来源：[Permission profiles](https://developers.openai.com/codex/permissions)。

网络权限支持 domain allow/deny、local/private network guard、Unix socket rules。来源：[Network permissions](https://developers.openai.com/codex/permissions)。

OS enforcement：

```text
macOS: Seatbelt
Linux/WSL: bubblewrap + seccomp + Landlock fallback
Windows: elevated sandboxing / native Windows sandbox
```

来源：[Sandbox enforcement](https://developers.openai.com/codex/permissions)。

### DeepSeek Agent 启发

我们应从一开始设计：

```text
PermissionProfile
FilesystemPolicy
NetworkPolicy
ApprovalPolicy
OS-specific sandbox adapter
```

即使 MVP 先只做基础 ask/allow/deny，也要保留配置模型。

---

## 8. Skills / Subagents / Automations

Codex Skills 使用 progressive disclosure：初始 context 只放 skill name、description、path；完整 `SKILL.md` 只在决定使用时加载。来源：[Codex Skills](https://developers.openai.com/codex/skills)。

Subagents 可并行 spawn specialized agents，收集结果后统一返回；可定义 custom agents，带不同 model configs、instructions、tools。来源：[Codex Subagents](https://developers.openai.com/codex/subagents)。

App 还支持 thread automations，周期性唤醒同一个 thread，保留上下文。来源：[Thread automations](https://developers.openai.com/codex/app/features)。

### DeepSeek Agent 启发

这正好对应：

```text
Skill index in prefix, body on demand
Flash worker subagents
Pro reviewer subagent
Thread-level automation
Checkpoint persistence
```
