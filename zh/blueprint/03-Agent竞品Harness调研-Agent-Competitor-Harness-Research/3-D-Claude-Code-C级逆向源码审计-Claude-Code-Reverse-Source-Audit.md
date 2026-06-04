# 3-D Claude Code C级逆向源码审计 Claude Code Reverse Source Audit

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v0.9  
> 状态：Claude Code 官方源码边界 + 非官方逆向源码 C 级审计完成。  
> 证据等级：`oboard/claude-code-rev` 是非官方 source-map 还原仓库，只能作为 C 级线索，不能作为 Anthropic 官方事实。

---

## 1. 仓库性质判定

非官方仓库：https://github.com/oboard/claude-code-rev

该仓库 README 自述：

```text
Restored Claude Code Source
reconstructed primarily from source maps and missing-module backfilling
not the original upstream repository state
some files were unrecoverable from source maps and replaced with compatibility shims or degraded implementations
```

因此本仓库不能当作官方 Claude Code 源码，只能用于：

```text
理解可能的 engine 模块边界
寻找 Agent Loop / Tool / Context / Query / Cost / Provider 的源码线索
与官方 Docs 交叉验证
```

不能用于：

```text
证明 Anthropic 官方实现细节
直接 fork 到商业产品
作为法律/版权安全的代码来源
```

---

## 2. 仓库结构扫描

`oboard/claude-code-rev/src` 目录暴露出比官方仓库更接近 engine 的模块：

```text
assistant/
bootstrap/
bridge/
cli/
commands/
context/
coordinator/
hooks/
jobs/
memdir/
plugins/
query/
remote/
services/
skills/
state/
tasks/
tools/
types/
utils/
QueryEngine.ts
Task.ts
Tool.ts
context.ts
cost-tracker.ts
history.ts
query.ts
tools.ts
```

目录来源：https://github.com/oboard/claude-code-rev/tree/main/src

### 关键判断

这个结构与官方 Docs 里的 Claude Code 机制高度吻合：

```text
QueryEngine / query：Agent 主循环线索
Tool / tools：工具抽象线索
context / memdir：上下文与 memory 线索
hooks：生命周期 hook 线索
skills / plugins：技能与插件线索
cost-tracker：成本追踪线索
state / history：session 与历史线索
```

但因为它是逆向恢复仓库，所有源码判断必须标注 C 级。

---

## 3. QueryEngine 线索

`QueryEngine.ts` raw 文件显示它 import 了：

```text
loadMemoryPrompt
query
fetchSystemPromptParts
getSlashCommandToolSkills
loadAllPluginsCacheOnly
recordTranscript / flushSessionStorage
getTotalCost / getModelUsage
getMainLoopModel / parseUserSpecifiedModel
shouldEnableThinkingByDefault
fileHistoryMakeSnapshot
processUserInput
```

来源：https://raw.githubusercontent.com/oboard/claude-code-rev/main/src/QueryEngine.ts

并定义了 `QueryEngineConfig`，包含：

```text
cwd
tools
commands
mcpClients
agents
canUseTool
getAppState / setAppState
initialMessages
readFileCache
customSystemPrompt / appendSystemPrompt
userSpecifiedModel / fallbackModel
thinkingConfig
maxTurns
maxBudgetUsd
taskBudget
jsonSchema
orphanedPermission
snipReplay
```

### 推论

如果该恢复源码结构可信，Claude Code engine 内部确实围绕以下对象组织：

```text
conversation-scoped QueryEngine
messages / transcript persistence
system prompt parts
memory prompt
skills / plugins cache
tool permission callback
model selection
thinking config
cost tracking
file history snapshot
query loop
```

这与官方 Docs 的 agentic harness 描述一致，但不能替代官方源码证据。

---

## 4. Provider 支持线索

`oboard/claude-code-rev` README 说明恢复版 CLI 补了初步 multi-provider path：

```text
github-models
github-copilot
/provider
/model
```

并称 Copilot-hosted Claude models 可以走现有 Claude Code agent/runtime path；GPT/Grok style models 尚未完整接入，因为它们主要需要 Copilot `/responses` API，而当前适配层主要是 chat/messages shim。

来源：https://github.com/oboard/claude-code-rev

### 对 DeepSeek V4 的启发

这条线索非常关键：即使是恢复版，也显示 Claude Code runtime 对“非 Claude 协议模型”的适配难点不在“能不能换 provider”，而在：

```text
模型 API 协议
tool loop protocol
responses vs messages
thinking / reasoning 语义
model picker / model capability
```

这正好对应 DeepSeek Agent 需要自研：

```text
DeepSeekV4MessageCompiler
DSMLToolParser
ReasoningContentPolicy
Flash/Pro capability profile
```

---

## 5. Model-Harness Fit Matrix 更新

| DeepSeek V4 特性 | Claude Code / reverse source 线索 | 评分 | 说明 |
|---|---|---:|---|
| 1M context | 有 context、memory、history、snip/compact 线索 | B | 但不是 V4 sparse layout |
| cache hit/miss | 有 cost-tracker、usage、prompt cache Docs | C+ | 无 DeepSeek hit/miss telemetry |
| Flash/Pro router | 有 model picker / getMainLoopModel / provider picker 线索 | C+ | 不是 V4 五档路由 |
| thinking mode | 有 `thinkingConfig`、`shouldEnableThinkingByDefault` 线索 | B- | 不是 DeepSeek reasoning_effort / DSML |
| V4 DSML encoding | 无 | D | Claude/Chat messages 路线 |
| tool permission | 有 `canUseTool` callback 线索 | A- | 需官方 Docs 交叉验证 |
| skills/plugins | 有源码目录与官方 plugins | A- | 可借鉴结构 |
| transcript/session | 有 `recordTranscript`、history 线索 | B+ | 可借鉴 |
| file snapshot | 有 `fileHistoryMakeSnapshot` 线索 | B | 可借鉴 checkpoint 思路 |
| provider genericity | 恢复版初步支持 GitHub providers | C+ | 可作为多 provider 接入难点线索 |

---

## 6. 对 DeepSeek Agent 的迁移判断

### 可借鉴设计

```text
QueryEngine conversation-scoped runtime
canUseTool permission callback
system prompt parts builder
memory prompt loader
skills / plugins cache-only loading
cost tracker
transcript persistence
file history snapshot
provider picker / model picker
```

### 必须 DeepSeek-native 重写

```text
V4 Context Layout Manager
DeepSeekV4MessageCompiler
DeepSeek cache hit/miss telemetry
Flash/Pro/Think/Max router
DSML tool call parser
reasoning_content 四态管理
checkpoint-driven Pro review
```

### 不可直接复用

```text
非官方 reverse source 代码本身
Claude / Anthropic 协议层
source-map 恢复中的 shim / fallback
```

---

## 7. 结论

Claude Code 的真正价值现在更清楚了：

```text
官方 Docs 证明了成熟 Harness 范式；
官方 repo 证明 plugins/skills/hooks/MCP 生态结构；
C级 reverse source 证明 engine 可能围绕 QueryEngine、query、tools、context、cost、history、provider 组织。
```

但它仍不是 DeepSeek V4-native Harness。  
DeepSeek Agent 应学习它的 engine 分层，而不是复用它的协议实现。
