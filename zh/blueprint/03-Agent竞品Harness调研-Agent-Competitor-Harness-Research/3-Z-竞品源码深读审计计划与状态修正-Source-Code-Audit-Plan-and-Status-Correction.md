# 3-Z 竞品源码深读审计计划与状态修正 Source-Code Audit Plan and Status Correction

> 版本：v0.7  
> 修订原因：用户指出此前 Claude Code / Codex / Trae 调研速度过快，存在“Docs/README 调研”被误标为“深度源码调研”的问题。该批评成立。  
> 本文件用于纠偏：把此前竞品调研状态降级为第一轮预研，并建立真正的源码深读流程。

---

## 1. 状态修正

此前文件：

```text
3-1 ~ 3-4 Claude Code 调研
4-1 ~ 4-4 Codex 调研
5-1 ~ 5-4 Trae / SOLO / Trae Agent 调研
```

应统一标记为：

```text
第一轮预研版：
官方 Docs / 官方 README / 官方产品页 / 少量源码线索 / Model-Harness Fit 初步判断
```

不能标记为：

```text
完整源码深读完成
```

---

## 2. 到目前为止实际读了什么？

### Claude Code

已读：

```text
官方 Docs：overview / how it works / context-window / prompt-caching / memory / permissions / skills / subagents / hooks / MCP
官方 GitHub 仓库首页 / README / plugins 线索
非官方 sourcemap 仓库仅作为线索
```

未完成：

```text
完整 CLI engine 源码逐模块阅读
工具调用实现源码
permission runtime 源码
context compaction 源码
memory / skills / subagents 实现源码
```

备注：

```text
Claude Code 官方仓库公开内容未必包含完整 CLI engine 源码，因此源码深读需要先明确官方公开边界，再决定是否使用非官方 sourcemap 作为“线索级”材料。
```

### Codex

已读：

```text
官方 README
官方 AGENTS.md
官方 Developers Docs：CLI / App / Cloud / Permissions / Config / MCP / Skills / Subagents
少量源码定位：turn_context.rs 等
```

已确认的源码级事实示例：

```text
AGENTS.md 明确 model visible context 规则：
- No history rewrite
- Avoid frequent changes to context that cause cache misses
- No unbounded items
- No items larger than 10K tokens
- >1K tokens 新项需要 P0 review
- injected fragments 必须是 core/context structs 并实现 ContextualUserFragment
```

```text
turn_context.rs 中存在 model_info、effective_reasoning_effort、model_context_window、supported_reasoning_levels、truncation_policy 等逻辑。
```

未完成：

```text
codex-rs/core 全模块阅读
context injection 源码
model provider 源码
tool runtime 源码
permission/sandbox 源码
app-server 源码
TUI 源码
MCP 源码
skills/subagents 源码
```

### Trae / Trae Agent

已读：

```text
Trae / SOLO 官方产品页
Trae Agent README
tools.md
trajectory recording docs
roadmap / config 线索
Trae Agent 技术报告
```

未完成：

```text
Trae Agent 核心源码逐模块阅读
agent loop 源码
LLM provider 源码
tool runtime 源码
trajectory writer 源码
sequential_thinking 工具源码
generation / pruning / selection 若开源则对应代码
Docker execution 源码
```

---

## 3. 真正的源码深读必须怎么做？

每个竞品至少需要完成以下文件级审计。

---

## 4. Claude Code 源码深读计划

### 4.1 官方公开仓库边界确认

先确认 `anthropics/claude-code` 中公开的是：

```text
完整 CLI engine
还是插件 / commands / examples / docs / integrations
```

如果官方仓库不含完整 engine，则：

```text
官方 Docs = 主证据
官方仓库 = 插件/配置证据
非官方 sourcemap = 线索证据，必须标注 C 级
```

### 4.2 必读模块 / 主题

```text
CLI entry
Tool call runtime
Permission enforcement
File edit implementation
Shell execution implementation
Context construction
Compaction implementation
CLAUDE.md loading
Memory writing
Skills loader
Subagents context isolation
Hooks lifecycle
MCP integration
Session / checkpoint / resume
Prompt cache handling
```

### 4.3 必须产出

```text
3-C-Claude-Code源码深读报告-Claude-Code-Source-Audit.md
3-D-Claude-Code模型物理适配证据矩阵-Claude-Code-Model-Adaptation-Evidence-Matrix.md
```

---

## 5. Codex 源码深读计划

### 5.1 必读目录

```text
codex-rs/core/
codex-rs/core/src/session/
codex-rs/core/src/context/
codex-rs/core/src/config/
codex-rs/core/src/model*
codex-rs/core/src/tools*
codex-rs/core/src/exec*
codex-rs/tui/
codex-rs/app-server/
codex-rs/codex-mcp/
sdk/
```

### 5.2 必须回答

```text
1. ContextualUserFragment 在哪里定义？
2. context fragments 如何注入 model-visible context？
3. model_info 如何定义 context window、reasoning levels、tool mode？
4. custom provider 如何接入？
5. truncation / compaction policy 如何执行？
6. tool calls 如何被规划、执行、回传？
7. sandbox policy 如何执行？
8. App server 如何和 core 通信？
9. Codex 是否有 cache telemetry？
10. 哪些代码能迁移到 DeepSeek Agent？
```

### 5.3 必须产出

```text
4-C-Codex源码深读报告-Codex-Source-Audit.md
4-D-Codex模型物理适配证据矩阵-Codex-Model-Adaptation-Evidence-Matrix.md
```

---

## 6. Trae Agent 源码深读计划

### 6.1 必读目录 / 文件

```text
Agent loop
LLM provider abstraction
tool registry
bash tool
file edit tool
json edit tool
sequential_thinking tool
task_done tool
trajectory recorder
Docker execution
MCP integration
configuration loader
benchmark / SWE-bench runner
```

### 6.2 必须回答

```text
1. Trae Agent 的主 loop 如何组织？
2. 工具调用如何解析、执行、回传？
3. sequential_thinking 是否只是工具描述，还是有状态结构？
4. trajectory 是否完整记录 prompt、response、tool、state、error？
5. 多 provider 抽象能否表达 DeepSeek V4 Flash/Pro/Think/Max？
6. Docker mode 如何隔离执行？
7. generation / pruning / selection 是否在开源代码中实现，还是只在论文中？
8. 哪些代码可以 fork / 借鉴？
```

### 6.3 必须产出

```text
5-C-Trae-Agent源码深读报告-Trae-Agent-Source-Audit.md
5-D-Trae模型物理适配证据矩阵-Trae-Model-Adaptation-Evidence-Matrix.md
```

---

## 7. 新的执行节奏

从 v0.7 开始，不能再在几十秒内声称“深度源码调研完成”。

每个竞品源码深读至少要经过：

```text
1. 仓库结构扫描
2. 关键模块清单
3. 逐文件阅读
4. 函数/类/配置摘录
5. 证据链接整理
6. Model-Harness Fit Matrix
7. 对 DeepSeek Agent 的迁移判断
8. 产出源码审计报告
```

---

## 8. README 状态修正建议

在总 README 中应将：

```text
Claude Code 深度调研
OpenAI Codex 深度调研
Trae / Trae SOLO 深度调研
```

改为：

```text
Claude Code 第一轮预研完成；源码深读未完成
OpenAI Codex 第一轮预研完成；源码深读未完成
Trae / Trae SOLO 第一轮预研完成；源码深读未完成
```

---

## 9. 结论

用户指出的问题成立：

```text
没有完整源码阅读，就不能叫源码深度调研。
```

后续必须改为：

```text
先承认预研
再做源码审计
再更新结论
```
