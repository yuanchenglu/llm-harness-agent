# 08-agent-loop-message-protocol.md — DeepSeek Agent Message Protocol v0.1

> 基于 DeepSeek V4 encoding 源码设计的 Agent Loop 消息协议。

---

## 1. 设计目标

DeepSeek Agent 的消息协议必须同时满足：

```text
1. OpenAI-compatible 外部接口
2. DeepSeek V4 encoding 内部格式
3. Prefix cache 稳定性
4. Tool calling 可解析性
5. Reasoning content 可控回传
6. Long-context checkpoint 可压缩
```

---

## 2. 内部消息对象

建议 DeepSeek Agent 内部统一消息结构：

```yaml
id: msg-xxx
role: system | user | assistant | tool_result | latest_reminder
content: string
reasoning_content: string | null
tool_calls: []
tool_result_for: call-id | null
visibility:
  prompt: true/false
  display: true/false
  archive: true/false
cache_zone:
  stable_prefix | task_anchor | active_working_set | compressed_history | turn_tail
thinking_policy:
  keep | drop | summarize | archive_only
```

---

## 3. 编译到 V4 prompt 的流程

```text
Agent Internal Messages
  ↓
Context Layout Manager
  ↓
Reasoning Content Policy
  ↓
Tool Result Merger
  ↓
DeepSeekV4MessageCompiler
  ↓
encode_messages(...)
  ↓
tokenizer.encode
```

---

## 4. Stable Prefix 规则

进入 stable prefix 的内容：

```text
system identity
tool schema
hard constraints
memory index
skill index
```

禁止进入 stable prefix 的内容：

```text
当前时间
随机 ID
临时计划
工具结果
动态成本信息
长 reasoning_content
本轮用户请求
```

---

## 5. Tool Calling 规则

### 5.1 Tool schema

Tool schema 必须稳定排序：

```text
按 tool name 排序
参数字段稳定排序
description 不动态改写
不要每轮增删 tool
```

否则会破坏 prefix cache。

### 5.2 Tool result

OpenAI-style tool result 不直接作为 `tool` role 发送，而是：

```text
tool_result blocks → user message content_blocks
```

并按 tool call order 排序。

### 5.3 Parse recovery

由于官方 parser 只处理 well-formatted output，生产 Harness 必须增加：

```text
DSML parse error detector
malformed tool call repair
retry with lower temperature
fallback to JSON extraction
ask model to re-emit tool call
```

---

## 6. Reasoning Mode 路由

```yaml
flash_non_think:
  thinking_mode: chat
  reasoning_effort: null

flash_think:
  thinking_mode: thinking
  reasoning_effort: high

pro_non_think:
  thinking_mode: chat
  reasoning_effort: null

pro_think:
  thinking_mode: thinking
  reasoning_effort: high

pro_max:
  thinking_mode: thinking
  reasoning_effort: max
```

注意：

- `reasoning_effort=max` 会在 prompt 最前面注入特殊前缀；
- 这可能破坏 stable prefix；
- 所以 Max 应该是少数关键 checkpoint 的一次性模式。

---

## 7. Quick Task 子协议

V4 quick instruction token 可用于 Harness 内部分类：

```text
action: 是否搜索/调用工具
query: 生成搜索 query
authority: 判断是否需要权威来源
domain: 判断任务领域
title: 会话标题
read_url: 判断 URL 是否读取
```

DeepSeek Agent 可把这些当作便宜的 micro-agent：

```text
Flash Non-think + quick task token
```

用于低成本路由和分类。

---

## 8. 推荐 Agent Loop

```text
1. Receive user request
2. Intent classify using quick task / Flash
3. Build context layout
4. Select model + thinking mode
5. Compile V4 prompt
6. Generate assistant output
7. Parse content / reasoning / tool_calls
8. If tool_calls: execute tools
9. Merge tool results into user content_blocks
10. Continue loop
11. Generate checkpoint
12. Drop/summarize/archive reasoning according to policy
```

---

## 9. 与 OpenAI-compatible API 的关系

外部可以继续使用 OpenAI-style：

```json
{"role":"tool", "tool_call_id":"...", "content":"..."}
```

但内部必须转成 V4 format：

```text
user content_blocks: [{type: "tool_result", ...}]
```

否则无法完全利用 V4 的官方 encoding 约定。

---

## 10. 关键结论

DeepSeek Agent 需要一个独立协议层：

```text
OpenAI Adapter
  ≠
DeepSeek V4 Message Compiler
```

普通 OpenAI Adapter 只能“跑起来”，但不能做到：

```text
cache-stable
reasoning-aware
DSML-tool-aware
quick-task-aware
checkpoint-aware
```
