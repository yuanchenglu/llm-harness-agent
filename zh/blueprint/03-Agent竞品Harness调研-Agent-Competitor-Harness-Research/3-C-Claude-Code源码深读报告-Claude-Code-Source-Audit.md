# 3-C Claude Code 源码深读报告 Claude Code Source Audit

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v0.8  
> 状态：源码边界确认完成；官方完整 engine 源码未公开。  
> 结论先行：Claude Code 官方 GitHub 仓库可作为“官方产品入口 + 插件生态源码”证据，但目前不能作为完整 CLI engine 源码审计材料。

---

## 1. 仓库结构扫描

官方仓库：https://github.com/anthropics/claude-code/blob/main/README.md

已读文件：

| 文件 | 证据 | 结论 |
|---|---|---|
| `README.md` | https://github.com/anthropics/claude-code/blob/main/README.md | 说明 Claude Code 是 terminal / IDE / GitHub 中使用的 agentic coding tool；安装方式指向外部 installer，而不是仓库内源码构建 |
| `plugins/README.md` | https://github.com/anthropics/claude-code/blob/main/plugins/README.md | 明确该仓库包含 official Claude Code plugins，扩展 custom commands、agents、hooks、MCP servers |
| plugins 子目录 | https://github.com/anthropics/claude-code/blob/main/plugins/README.md | 可审计插件结构、agents、skills、hooks，但不能等同 engine 内部实现 |

README 写到 Claude Code 是 terminal 里的 agentic coding tool，可理解代码库、执行 routine tasks、解释复杂代码、处理 git workflows。  
但 README 的安装方式是 curl / Homebrew / WinGet / npm，而不是从本仓库源码 build CLI。

---

## 2. 源码公开边界判断

官方仓库 README 明确说该 repository includes several Claude Code plugins。plugins README 进一步说明 plugins extend functionality through custom commands, specialized agents, hooks, MCP servers。

### 结论

当前官方 GitHub 仓库更像：

```text
Claude Code 产品入口
官方插件 / commands / agents / hooks / skills / MCP 示例集合
生态扩展仓库
```

而不是：

```text
完整 Claude Code CLI engine 源码仓库
```

因此，Claude Code 的 engine 级源码深读无法基于官方仓库完成；只能基于官方 Docs 做机制分析，并把非官方 sourcemap 当 C 级线索。

---

## 3. 关键模块清单

| 模块 | 官方源码是否可读 | 官方 Docs 是否确认 | 说明 |
|---|---|---|---|
| Agent Loop | engine 源码未公开 | 是 | Docs 确认 gather context → take action → verify results |
| Tool Runtime | engine 源码未公开 | 是 | Docs 确认 file/search/execution/web/code intelligence |
| Permission Runtime | engine 源码未公开 | 是 | Docs 确认权限由 Claude Code 执行，不是模型执行 |
| Context / Compaction | engine 源码未公开 | 是 | Docs 确认 CLAUDE.md、auto memory、compaction behavior |
| Prompt caching | engine 源码未公开 | 是 | Docs 确认 exact prefix matching |
| Plugins | 官方源码可读 | 是 | plugins 目录公开了 commands/agents/skills/hooks/MCP 结构 |
| Hooks | 插件示例可读 | 是 | plugins 目录包含 Hook 示例；Docs 有 hooks reference |
| Skills / Agents | 插件示例可读 | 是 | plugins 中有 agent/skill 示例 |
| MCP | 插件配置可读 | 是 | plugins 可包含 `.mcp.json` |

---

## 4. 函数 / 类 / 配置摘录

官方完整 engine 源码未公开，因此不能摘录 engine 内部函数 / 类。

可摘录的官方插件结构：

```text
plugin-name/
├── .claude-plugin/plugin.json
├── commands/
├── agents/
├── skills/
├── hooks/
├── .mcp.json
└── README.md
```

这说明 Claude Code 的扩展系统不是单纯 prompt 文档，而是有明确文件结构和 runtime lifecycle 的插件体系。

---

## 5. Model-Harness Fit Matrix

| DeepSeek V4 特性 | Claude Code 能否发挥 | 证据等级 | 判断 |
|---|---|---|---|
| 1M context | 部分能 | S1 Docs | Claude Code 有 context / memory / compaction，但不是 V4-specific layout |
| CSA/HCA / sliding_window=128 | 基本不能 | 推论 | 未发现公开资料中针对 DeepSeek sparse attention 的布局 |
| cache hit/miss pricing | 基本不能 | S1 Docs + 推论 | Claude 有 prompt caching，但不是 DeepSeek usage hit/miss telemetry |
| Flash/Pro/Thinking/Max | 不能 | 推论 | Claude Code 面向 Claude 模型路由，不面向 DeepSeek V4 |
| V4 DSML encoding | 不能 | 推论 | Claude Code 使用 Anthropic 协议 |
| reasoning_content policy | 部分能 | S1 Docs | Claude 有 compaction，但不是 DeepSeek reasoning 四态 |
| Permission runtime | 能借鉴 | S1 Docs | 权限由 runtime 强制 |
| Skills/Subagents/Hooks | 能借鉴 | S0 plugins + S1 Docs | 官方 plugins 公开结构 |

---

## 6. 对 DeepSeek Agent 的迁移判断

### 可直接借鉴

```text
插件结构思想
commands / agents / skills / hooks / MCP 的组织方式
权限必须由 runtime 强制
CLAUDE.md-like project memory
```

### 需要 V4-native 重写

```text
Context Layout Manager
CacheHitTelemetry
Flash/Pro Router
DeepSeekV4MessageCompiler
ReasoningContentPolicy
Checkpoint-driven Pro Review
```

### 不可直接复用

```text
Claude Code engine 内部实现：官方仓库未公开完整源码
Anthropic prompt/cache/model protocol
```

---

## 7. 审计结论

Claude Code 的官方源码审计结论不是“读完源码”，而是：

```text
官方 engine 源码不可完整审计；
官方 plugins 生态可审计；
核心 Harness 机制只能基于官方 Docs 作为 S1 证据；
非官方源码只能作线索。
```
