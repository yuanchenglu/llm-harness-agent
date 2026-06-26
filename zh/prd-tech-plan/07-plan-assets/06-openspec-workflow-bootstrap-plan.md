# 06. OpenSpec 工作流与 Artifact Gate 归档计划

## 0. AI 执行提示词

你是 DeepSeekAgent 的 OpenSpec 工作流维护代理。执行任何中高风险产品、release、跨文件行为或架构变更前，必须先创建或读取 OpenSpec change。你不能把 OpenSpec tasks 勾选当成代码正确；完成必须同时有 artifact 状态和可执行验证命令。先读 `AGENTS.md`、`openspec/config.yaml`、相关 change 的 `proposal.md/design.md/specs/tasks.md`，再实施。

## 1. 目标

归档 OpenSpec 工作流引入计划，让后续 AI 清楚：

- 什么时候必须先 propose。
- 什么时候可以直接做低风险小改。
- 如何从 plan asset 进入 OpenSpec change。
- 如何区分 artifact 完成和代码/产品完成。

## 2. 事实依据

确定：

- 根仓库有 `AGENTS.md`，要求研究优先、证据优先、最小改动、带置信度。
- 根仓库有 `openspec/config.yaml`，schema 是 `spec-driven`。
- `openspec/config.yaml` 要求 proposal 写问题、影响区域、事实源、假设、非目标、置信度。
- `openspec/config.yaml` 要求 tasks 小、排序、可独立验证，并包含明确验证步骤。
- 当前已有 OpenSpec change 示例：
  - `extract-deepseek-runtime-kernel`
  - `start-desktop-code-workbench`
  - `harden-desktop-code-workbench`
  - `start-general-workspace-agent`
  - `align-completion-first-positioning`
  - `improve-zh-doc-readability-and-glossary`

需要重新核验：

- `openspec` CLI 是否可用。
- 当前 change 是否已归档或仍 active。
- 目标文件是否已有未提交用户改动。

验证命令：

```bash
openspec list
openspec status --change <change-name>
openspec validate <change-name> --type change --strict
python3 scripts/check_repo.py
git status --short --branch
```

## 3. 关键决策

- 产品/release/架构/跨文件行为变更必须走 OpenSpec。
- 文档小修、链接修复、局部计划资产维护可以跳过 OpenSpec，但仍要声明假设和验证。
- OpenSpec 是变更入口，不是最终正确性证明。
- 计划资产负责跨阶段交接；OpenSpec 负责具体 change 的 proposal、design、spec 和 tasks。
- 同一个 change 的 tasks 更新要跟实际实现同步，不能提前勾选。

## 4. 非目标

- 不把 OpenSpec 当项目管理系统。
- 不为每个 typo 创建 change。
- 不在没有需求清晰度时直接实现。
- 不用 OpenSpec 替代测试、lint、build、E2E 或人工验收。
- 不把历史计划资产自动转成 OpenSpec，除非进入执行阶段。

## 5. 已完成计划归档

### 5.1 Repo 级规则固化

已完成事实：

1. `AGENTS.md` 写入研究优先工作流。
2. `AGENTS.md` 明确 OpenSpec Gate。
3. `openspec/config.yaml` 定义 spec-driven schema 和 artifact 规则。

复核命令：

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,220p' openspec/config.yaml
```

### 5.2 已验证的使用方式

已完成事实：

1. Runtime 抽取使用 `extract-deepseek-runtime-kernel` change。
2. Desktop 首片使用 `start-desktop-code-workbench` change，已归档。
3. Desktop hardening 使用 `harden-desktop-code-workbench` change，已归档。
4. General Workspace Agent 使用 `start-general-workspace-agent` change，已归档。
5. Integrations And Automation Preview 使用 `start-integrations-automation-preview` change，已归档。
6. 文档中文可读性和 completion-first 定位也通过 change 维护过。

复核命令：

```bash
find openspec/changes -maxdepth 2 -type f \( -name 'proposal.md' -o -name 'tasks.md' \) | sort
openspec validate desktop-code-workbench-first-slice --type spec --strict
openspec validate general-workspace-agent --type spec --strict
openspec validate integrations-automation-preview --type spec --strict
find openspec/changes/archive -maxdepth 2 -type d | rg "start-desktop-code-workbench|harden-desktop-code-workbench|start-general-workspace-agent|start-integrations-automation-preview"
```

## 6. 实施步骤：后续执行

当计划资产进入实现阶段时：

1. 定义 change 名：
   - 当前 UI 收口：`refresh-consumer-desktop-ui`。
   - 稳定发布准备：`prepare-stable-public-release`。
   - 已归档历史示例：`start-desktop-code-workbench`、`harden-desktop-code-workbench`、`start-general-workspace-agent`、`start-integrations-automation-preview`。
2. 创建 proposal：
   - Why。
   - What changes。
   - Non-goals。
   - Impact。
   - Evidence sources。
   - Assumptions and confidence。
3. 写 design：
   - Context。
   - Goals / Non-goals。
   - Decisions。
   - Alternatives rejected。
   - Risks。
   - Migration / rollback。
4. 写 specs：
   - Observable requirements。
   - Acceptance scenarios。
   - Error and security scenarios。
5. 写 tasks：
   - 小步骤。
   - 每步能独立验证。
   - 最后有 tests / build / e2e / check_repo。
6. validate：
   - strict validate 通过后再实现。
7. apply：
   - 实现一项，验证一项，勾选一项。

## 7. 验证命令

```bash
openspec list
openspec validate <change-name> --type change --strict
openspec instructions apply --change <change-name> --json
python3 scripts/check_repo.py
```

## 8. 完成定义

本归档计划完成的条件：

- 后续 AI 知道产品/release/架构变更必须先走 OpenSpec。
- 后续 AI 知道计划资产和 OpenSpec 的职责边界。
- 后续 AI 不会把 artifact 完成误判成代码正确。
- 计划资产 README 能链接到本文件。
