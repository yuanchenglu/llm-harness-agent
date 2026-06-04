# 4-D Codex 源码深读报告 Pass 2 Codex Source Audit Pass 2

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v0.9  
> 状态：核心 Model-Harness 模块审计完成到可用于架构判断。  
> 已读主题：context fragments、internal model context、environment/permission context、turn context、turn loop、auto compaction、config schema。  
> 仍未完成：每个工具实现和 app-server 全量审计；但核心模型-Harness 配合机制已足够形成架构结论。

---

## 1. 仓库结构扫描更新

Codex `codex-rs/core/src/context/mod.rs` 明确说：

```text
Context fragments injected into model input.
```

它导出/注册了：

```text
UserInstructions
EnvironmentContext
AdditionalContextUserFragment
SkillInstructions
UserShellCommand
TurnAborted
SubagentNotification
InternalModelContextFragment
PermissionsInstructions
PluginInstructions
ModelSwitchInstructions
NetworkRuleSaved
```

源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/context/mod.rs

这说明 Codex 不是随意拼接 prompt，而是把 model-visible context 拆成 typed fragments。

---

## 2. ContextualUserFragment 机制

`contextual_user_message.rs` 中存在 `CONTEXTUAL_USER_FRAGMENTS` 列表，集中登记：

```text
USER_INSTRUCTIONS
ENVIRONMENT_CONTEXT
ADDITIONAL_CONTEXT
SKILL_INSTRUCTIONS
USER_SHELL_COMMAND
TURN_ABORTED
SUBAGENT_NOTIFICATION
INTERNAL_MODEL_CONTEXT
LEGACY warnings
```

并通过 `is_contextual_user_fragment` 判断 content item 是否是标准上下文片段。源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/context/contextual_user_message.rs

### 架构意义

Codex 的 context 工程是：

```text
typed fragment registration
fragment matching
hook prompt fragment parsing
standard context fragment filtering
```

DeepSeek Agent 应直接借鉴这个思想，但增加：

```text
CacheZone
ContextLayoutZone
TokenBudget
StablePrefixFlag
V4AttentionPriority
```

---

## 3. InternalModelContextFragment

`internal_model_context.rs` 定义了：

```text
<codex_internal_context source="...">
...
</codex_internal_context>
```

并通过 `InternalContextSource` 约束 source label 必须符合 `[a-z][a-z0-9_]*`，目的是让 source 可以嵌入 wrapper 且便于审计 stored history。源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/context/internal_model_context.rs

### 架构意义

这是一个非常重要的设计：Codex 明确区分“用户自然语言消息”和“runtime-owned hidden model context”。

DeepSeek Agent 应设计类似：

```text
<deepseek_agent_context zone="task_anchor" source="planner">
...
</deepseek_agent_context>
```

但要进一步绑定：

```text
stable_prefix
task_anchor
active_working_set
compressed_history
turn_tail
```

---

## 4. EnvironmentContext / Permission Context

`environment_context.rs` 把 workspace roots、filesystem permissions、network allow/deny、shell、current date/timezone 等渲染成结构化 context。它支持：

```text
<filesystem>
  <workspace_roots>
  <permission_profile>
  <file_system type="restricted/unrestricted">
<network enabled="true">
```

并且从 `PermissionProfile` 生成 filesystem/network context。源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/context/environment_context.rs

### 架构意义

Codex 把 runtime 权限状态显式注入模型，让模型知道：

```text
工作目录是什么
workspace roots 是什么
filesystem 是否 restricted
network 允许/禁止哪些域
permission profile 是什么
```

DeepSeek Agent 必须借鉴，但要注意：

```text
权限注入只是让模型知道边界；
真正 enforcement 必须仍在 runtime 执行。
```

---

## 5. TurnContext：模型能力、权限、环境的单 turn 容器

`turn_context.rs` 定义 `TurnContext`，包含：

```text
model_info
tool_mode
provider
reasoning_effort
reasoning_summary
environments
developer_instructions
compact_prompt
approval_policy
permission_profile
network
available_models
truncation_policy
dynamic_tools
turn_skills
```

它还实现：

```text
effective_reasoning_effort()
model_context_window()
with_model()
file_system_sandbox_context()
to_turn_context_item()
compact_prompt()
```

源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/session/turn_context.rs

### 架构意义

Codex 的关键不是“调用模型”，而是在每个 turn 里显式组合：

```text
模型能力
reasoning 设置
上下文窗口
工具模式
权限
网络
sandbox
skills
动态工具
compaction prompt
```

DeepSeek Agent 应设计：

```text
DeepSeekTurnContext:
  model_profile: Flash/Pro
  thinking_mode: non-think/think/max
  context_layout
  cache_policy
  permission_profile
  tool_runtime
  checkpoint_state
  review_policy
```

---

## 6. Turn Loop：采样、工具、hooks、compaction 的主循环

`turn.rs` 的 `run_turn` 注释明确：每次 sampling request，模型可能返回 function calls 或 assistant message；如果返回 function call，就执行并把 output 放回下一次 sampling request；如果只返回 assistant message，就记录到 history 并结束 turn。源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/session/turn.rs

同一文件还显示：

```text
run_pre_sampling_compact
record_context_updates_and_set_reference_context_item
build_skills_and_plugins
run_pending_session_start_hooks
run_hooks_and_record_inputs
clone_history().for_prompt(...)
run_sampling_request(...)
auto_compact_token_status
run_auto_compact(...)
run_turn_stop_hooks
```

源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/session/turn.rs

### 架构意义

Codex 的 Agent Loop 是成熟的：

```text
pre-compact
record context diff
build skills/plugins
run hooks
sample model
execute tools
update history
measure token status
auto compact if needed
run stop hooks
```

DeepSeek Agent 应直接借鉴这个 loop 框架，但模型层要换成：

```text
Flash/Pro router
V4MessageCompiler
DSMLToolParser
CacheTelemetry
CheckpointReview
```

---

## 7. Auto Compaction

`compact.rs` 定义了：

```text
InitialContextInjection::BeforeLastUserMessage
InitialContextInjection::DoNotInject
run_inline_auto_compact_task
run_compact_task
run_compact_task_inner
run_compact_task_inner_impl
CompactionAnalyticsAttempt
```

源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/compact.rs

源码注释写明：pre-turn/manual compaction 不注入 initial context，mid-turn compaction 要把 initial context 插入到最后真实 user message 之前，因为模型被训练为在 mid-turn compaction 后看到 summary 作为 history 的最后 item。源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/compact.rs

当 context window exceeded 时，代码选择 trim oldest history item，注释写明这是为了 preserve cache prefix 并保留 recent messages intact。源码：https://github.com/openai/codex/blob/main/codex-rs/core/src/compact.rs

### 架构意义

这是 Codex 对模型物理特性的强适配：

```text
它知道模型对 compaction summary 的位置有预期；
它知道 prefix cache 需要保留；
它知道 recent messages 要保留。
```

DeepSeek Agent 应更进一步：

```text
不要只 compact；
要 checkpoint；
不要只保留 recent；
要保留 V4 active working set；
不要只 preserve prefix；
要显示 cache hit/miss。
```

---

## 8. Codex Model-Harness Fit 终版矩阵

| DeepSeek V4 特性 | Codex 适配程度 | 证据 | 迁移判断 |
|---|---:|---|---|
| 1M context | B+ | typed context、auto compact、model_context_window | 可借鉴，但需 V4 layout |
| CSA/HCA / sliding_window=128 | C | 无 V4 attention-aware zone | 必须重写 |
| cache hit/miss | B | avoid cache misses、preserve prefix | 加 DeepSeek hit/miss telemetry |
| Flash/Pro/Think/Max | B | TurnContext 有 model_info / reasoning_effort / with_model | 改造为 V4 router |
| DSML encoding | D | 未发现 | 必须重写 |
| reasoning policy | B- | reasoning_effort / summary / compaction | 改为 DeepSeek 四态 |
| checkpoint/review | B | review/approval/compaction/tool loop | 增加 Pro reviewer |
| permissions/sandbox | A | EnvironmentContext + PermissionProfile | 强借鉴 |
| skills/plugins/hooks | A- | build_skills_and_plugins / hooks | 借鉴 |
| typed context fragments | A | ContextualUserFragment | 强借鉴 |

---

## 9. Codex 结论

Codex 是目前三个里 **源码层最值得借鉴** 的产品。

它已经把很多模型物理适配写成工程结构：

```text
typed context fragments
runtime-owned internal context
environment/permission context
model_context_window
reasoning_effort
tool_mode
turn loop
pre/mid-turn compaction
cache-preserving history trimming
approval reviewer
sandbox context
```

但它不是 DeepSeek V4-native。DeepSeek Agent 应把 Codex 的 context/turn/compact/permission 结构作为蓝本，然后重写：

```text
V4 Context Layout
Flash/Pro Router
DSML compiler
DeepSeek cache telemetry
Checkpoint-driven Pro Review
```
