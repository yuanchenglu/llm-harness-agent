# 02. DeepSeekAgent 产品化路线计划

## 1. 目标

在 `0.1.x` CLI-first public alpha gate 已关闭、`deepseek_runtime` 已发布的前提下，推进 DeepSeekAgent 产品化开发。

下一步不是重新研究、不是扩张功能面，而是沿着 runtime kernel 和 desktop code workbench 两条主线做产品化闭环。

## 2. 事实依据

确定：

- Blueprint Stage 0-5 已完成。
- Stage 6 status 是 `completed`。
- `earliest_incomplete_stage` 是 `null`。
- `production_release_gate` 已关闭。
- `deepseek_runtime` 已作为独立 runtime kernel 发布到 `v0.1.1-alpha.0`，并已发布 `v0.1.1-alpha.1` 公开 ChangeSet 相关 API。
- PRD TechPlan 已将 release lines 压缩为 `0.1.x`、`0.2.x`、`0.3.x`、`0.4.x`、`1.0`。
- 当前推荐技术栈是 Python runtime/CLI、React + TypeScript UI、Electron first、Local HTTP/SSE bridge、JSONL event log、SQLite optional index。

验证命令：

```bash
python3 scripts/check_repo.py
python3 -m json.tool docs/llm-harness-agent/zh/blueprint/stage-gates.json | sed -n '1,120p'
git -C /Users/bluth/Code/deepseek_runtime tag --list 'v0.1.1-alpha.*' --sort=version:refname
```

## 3. 关键决策

- Completion-first 是产品北极星：优先优化真实任务的可验证完成率。
- Runtime-first 是架构边界：CLI、desktop、automation 都只是 runtime 前端。
- DeepSeek-native 是产品差异：route、cache、usage、cost、reasoning boundary 必须可见。
- Local-first 是默认安全边界：用户代码、文件和密钥默认留在本机。
- Evidence-first 是完成定义：完成不是自然语言声明，而是计划、工具、diff、测试、审批、成本和结果证据。
- UI 不能绕过 permission、sandbox、changeset、rollback。
- 当前不再把 `0.1.x` 清单当下一步；`0.1.x` 是已关闭 release line，后续只做必要补丁和试用卫生。

## 4. 非目标

- 不重新做 DeepSeek V4 或竞品研究。
- 不重写 runtime 语言。
- 不扩展手机连接、定时任务、团队协作、企业治理。
- 不提前做公开插件市场。
- 不把桌面端做成独立 agent loop。
- 不用高保真视觉稿替代可执行产品闭环。

## 5. 路线执行顺序

### 5.1 Runtime Kernel 补丁线

目的：让 `deepseek_runtime` 成为桌面端可依赖的稳定 kernel。

步骤：

1. 已发布 `v0.1.1-alpha.1`，正式公开 ChangeSet 相关 API。
2. 已保持 runtime release drill、live smoke、release audit 作为补丁发布 gate。
3. 已更新主仓库计划资产，记录 runtime tag、API 边界和验证状态。

完成定义：

- 上层桌面 bridge 可以通过 pinned tag 使用 diff/apply/rollback。
- runtime 文档明确哪些是 public API。
- 下一步可以进入 `0.2.x` Desktop Code Workbench 首片。

### 5.2 `0.2.x` Desktop Code Workbench 首片

目的：把 runtime 接到桌面 UI，形成可信的 Code 工作台首个端到端闭环。

步骤：

1. 创建 OpenSpec change：`start-desktop-code-workbench`。
2. 在 `apps/desktop` 建立 Electron + React + TypeScript 工程。
3. 用 FastAPI + SSE 实现 local runtime bridge。
4. 固定依赖 `deepseek-runtime` 的 `v0.1.1-alpha.1` tag。
5. 完成 workspace chooser、task detail、evidence/cost/cache 展示。
6. 完成 Agent 提出 ChangeSet、用户审批 apply、用户 rollback 的真实闭环。

完成定义：

- Desktop 通过 local runtime bridge 启动任务。
- UI 不伪造 runtime 状态。
- diff、approval、rollback 与 CLI/runtime 语义一致。
- Task Detail 展示完成证据、未验证项、人工接管和 cost per successful task。
- runtime crash 或 bridge failure 不导致 UI 静默错误。

### 5.3 后续 release lines

只有在 `0.2.x` Code 工作台闭环成立后，再进入：

- `0.3.x` General Workspace Agent。
- `0.4.x` Integrations And Automation Preview。
- `1.0` Stable Public Release。

这些 release lines 不在当前实施计划内。

## 6. 验证命令

产品化路线同步后至少运行：

```bash
python3 scripts/check_repo.py
rg -n "production_release_gate|Desktop Code Workbench|deepseek_runtime|0\\.2\\.x|FastAPI|SSE" \
  docs/prd-tech-plan \
  docs/llm-harness-agent/zh/prd-tech-plan \
  openspec/changes
```

## 7. 完成定义

本路线计划本身完成的标准：

- README 能从 PRD TechPlan 入口找到计划资产。
- runtime、产品化、desktop 三条线边界清楚。
- 已完成事实和待做计划分开。
- 后续 AI 能从本计划直接判断下一刀是 `0.2.x` 桌面首片，而不是重新研究、扩范围或重复 runtime API 补丁。
