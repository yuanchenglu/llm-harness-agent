# 3-0 Claude Code 证据索引 Claude Code Evidence Index

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

> 阶段：Stage 2A  
> 版本：v0.2  
> 重要修正：已确认 `anthropics/claude-code` 为 Anthropic 官方公开 GitHub 仓库。本阶段调研优先级改为：**官方 GitHub 仓库 + 官方 Docs 双主证据**。此前的 source-map / 泄露仓库只作为补充线索。

---

## 1. 证据等级

| 等级 | 含义 | 本阶段适用 |
|---|---|---|
| S0 | 官方 GitHub 仓库 / 官方源码 / 官方仓库文件 | `anthropics/claude-code` |
| S1 | 官方 Docs / 官方产品说明 | `code.claude.com/docs` |
| A | 论文 / 学术分析 | arXiv 论文，仅辅助 |
| B | 可信媒体 / 第三方报告 | 辅助 |
| C | 非官方源码镜像 / 泄露 / source-map | 只能作为线索，不作为最终事实 |

---

## 2. 官方 GitHub 仓库

### 2.1 仓库定位

官方仓库：[anthropics/claude-code](https://github.com/anthropics/claude-code)

GitHub 页面显示该仓库属于 `anthropics` 组织，仓库名为 `claude-code`，状态为 Public；README 将 Claude Code 定义为一个 agentic coding tool，可在 terminal、IDE 或 GitHub 中使用自然语言命令完成 routine tasks、解释复杂代码、处理 git workflows。来源：[官方 GitHub README](https://github.com/anthropics/claude-code)。

### 2.2 仓库内容边界

当前官方仓库公开展示的内容包括：

```text
.claude-plugin/
.claude/ commands
.devcontainer/
.github/
.vscode/
Script/
examples/
plugins/
scripts/
CHANGELOG.md
LICENSE.md
README.md
SECURITY.md
```

其中 `plugins/` 目录包含官方 Claude Code plugins，插件可扩展 custom commands、agents、hooks、MCP servers 等能力。来源：[官方 plugins 目录](https://github.com/anthropics/claude-code/tree/main/plugins)。

重要边界：

```text
该官方仓库可以作为官方公开源码/插件/示例/配置证据。
但它不必然等同于完整 CLI engine 内部源码全部公开。
若需要分析 CLI 内部实现，仍需结合官方 Docs、官方仓库文件、以及明确标注为非官方线索的 source-map 仓库。
```

---

## 3. 官方 Docs 主证据

| 主题 | 关键事实 | 来源 |
|---|---|---|
| 产品定义 | Claude Code 是 agentic coding tool，可读代码库、编辑文件、运行命令，集成 terminal、IDE、desktop、browser | [Overview](https://code.claude.com/docs/en/overview) |
| 多端形态 | Terminal、VS Code、Desktop app、Web、JetBrains；各 surface 连接同一个 underlying Claude Code engine | [Overview / Use Claude Code everywhere](https://code.claude.com/docs/en/overview) |
| Agent Loop | gather context → take action → verify results，可随时 interrupt/steer | [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) |
| Harness 定义 | Claude Code 是 Claude 的 agentic harness，提供 tools、context management、execution environment | [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) |
| 工具类别 | File operations、Search、Execution、Web、Code intelligence | [Tools section](https://code.claude.com/docs/en/how-claude-code-works) |
| 访问范围 | project files、terminal、git state、CLAUDE.md、auto memory、extensions | [What Claude can access](https://code.claude.com/docs/en/how-claude-code-works) |
| 执行环境 | Local、Cloud、Remote Control | [Execution environments](https://code.claude.com/docs/en/how-claude-code-works) |
| Session | JSONL session、resume、fork、rewind、snapshot | [Work with sessions](https://code.claude.com/docs/en/how-claude-code-works) |
| Context | CLAUDE.md、auto memory、MCP tool names、skill descriptions 会进入 context | [Context window](https://code.claude.com/docs/en/context-window) |
| Compaction | `/compact` 后 project-root CLAUDE.md、auto memory 重新注入；path-scoped rules/nested CLAUDE.md 可能丢失直到再次触发 | [What survives compaction](https://code.claude.com/docs/en/context-window) |
| Prompt cache | 按请求 prefix 精确匹配；无 per-file/per-segment caching | [Prompt caching](https://code.claude.com/docs/en/prompt-caching) |
| Memory | CLAUDE.md 用户写，auto memory Claude 写；两者每次会话开始加载 | [Memory](https://code.claude.com/docs/en/memory) |
| Permissions | allow / ask / deny，deny → ask → allow；权限由 Claude Code 执行，不由模型执行 | [Permissions](https://code.claude.com/docs/en/permissions) |
| Permission modes | default、acceptEdits、plan、auto、dontAsk、bypassPermissions | [Permission modes](https://code.claude.com/docs/en/permissions) |
| Subagents | 独立 context window、独立 system prompt、tool access、permissions，返回 summary | [Subagents](https://code.claude.com/docs/en/sub-agents) |
| Skills | `SKILL.md`；skill body 只在使用时加载，适合从 CLAUDE.md 抽离流程 | [Skills](https://code.claude.com/docs/en/skills) |
| Hooks | SessionStart、PreToolUse、PostToolUse、SubagentStart/Stop、PreCompact/PostCompact、SessionEnd 等事件 | [Hooks reference](https://code.claude.com/docs/en/hooks) |
| MCP | 外部工具/数据源连接机制 | [MCP](https://code.claude.com/docs/en/mcp) |

---

## 4. 非官方源码线索

`Hyper66666/claude-code-sourcemap` 来源性质：非官方 source-map 还原 / 镜像仓库。来源：[claude-code-sourcemap](https://github.com/Hyper66666/claude-code-sourcemap)。

可作为：

```text
模块命名线索
目录结构线索
内部实现探索入口
```

不可作为：

```text
Anthropic 官方事实
最终架构唯一依据
可直接复用代码来源
```

---

## 5. 学术辅助资料

论文《Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems》声称基于公开 TypeScript source code 分析 Claude Code，并总结 permission、compaction、extensibility、subagent 等设计空间。来源：[arXiv 2604.14228](https://arxiv.org/abs/2604.14228)。

用途：辅助建立问题框架，不替代官方 Docs / 官方 GitHub。
