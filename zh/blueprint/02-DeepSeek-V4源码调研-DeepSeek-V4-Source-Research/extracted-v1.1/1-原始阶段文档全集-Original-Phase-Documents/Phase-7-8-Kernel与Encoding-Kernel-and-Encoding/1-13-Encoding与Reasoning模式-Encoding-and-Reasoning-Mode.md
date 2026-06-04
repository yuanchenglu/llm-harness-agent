# 08-encoding-and-reasoning-mode.md — DeepSeek V4 Encoding / Reasoning Mode 深拆 v0.1

> 日期：2026-06-04  
> 阶段：Phase 8 — Encoding / Reasoning Mode 深拆  
> 目标：基于 `encoding/README.md`、`encoding_dsv4.py`、`generate.py`，拆清楚 V4 的消息协议、thinking mode、tool calling、reasoning_content 策略。

---

## 1. 总体结论

DeepSeek V4 没有使用传统 Jinja chat template，而是提供了一个专门的 Python encoding 实现：

```text
encoding/encoding_dsv4.py
```

它支持：

```text
multi-turn conversation
tool calling
extended thinking / reasoning
quick instruction tasks
OpenAI-compatible messages → V4 input string
V4 completion text → structured assistant message
```

这意味着 DeepSeek Agent 不能只做 OpenAI messages 透传，而应该有自己的 V4-aware message compiler。

---

## 2. Special Tokens

关键 special tokens：

| Token | 作用 |
|---|---|
| `<｜begin▁of▁sentence｜>` | BOS |
| `<｜end▁of▁sentence｜>` | EOS / assistant turn end |
| `<｜User｜>` | user turn prefix |
| `<｜Assistant｜>` | assistant turn prefix |
| `<｜latest_reminder｜>` | latest reminder |
| `` | thinking start |
| `` | thinking end |
| `｜DSML｜` | DSML markup token |

---

## 3. Chat Mode vs Thinking Mode

### 3.1 Chat Mode

在 `thinking_mode="chat"` 下：

```text
<｜Assistant｜>
```

后面会立即放 thinking_end_token，相当于“关闭 thinking block”，模型直接生成 content。

适合：

```text
普通问答
摘要
简单执行
低风险工具参数
格式化
```

### 3.2 Thinking Mode

在 `thinking_mode="thinking"` 下：

```text
<｜Assistant｜><thinking_start>
reasoning
<thinking_end>
content
<eos>
```

适合：

```text
复杂规划
代码修改
失败分析
多步骤推理
审查
```

### 3.3 Reasoning Effort Max

当：

```python
reasoning_effort="max"
```

且第一条消息处于 thinking mode 时，会在 prompt 最前面注入 `REASONING_EFFORT_MAX` 特殊前缀。

这是 Max thinking 的 prompt-level 控制，不是在 `model.py` 中看到单独模型结构路径。

---

## 4. drop_thinking 策略

`encode_messages` 默认：

```python
drop_thinking=True
```

行为：

- thinking mode 下，会丢弃 last user message 之前 assistant 的 reasoning_content；
- user/system/tool/latest_reminder 保留；
- 早期 assistant message 只保留 content，不保留 reasoning_content；
- developer message 在 last_user 之前会被 drop。

但如果任何 message 带 tools：

```python
if any(m.get("tools") for m in full_messages):
    effective_drop_thinking = False
```

也就是说：

- 无工具普通 thinking 对话：默认丢弃旧 reasoning；
- 有工具调用对话：保留全部 reasoning，因为模型需要追踪多步工具推理。

---

## 5. Tool Calling：DSML 格式

### 5.1 工具 schema 注入

工具定义放在 system 或 developer message 的 `tools` 字段中，encoding 会渲染成：

```text
## Tools
You have access to a set of tools...
...
### Available Tool Schemas
{tool_definitions_json}
```

### 5.2 工具调用输出格式

模型输出：

```xml
<｜DSML｜tool_calls>
<｜DSML｜invoke name="function_name">
<｜DSML｜parameter name="param" string="true">string_value
<｜DSML｜parameter name="count" string="false">5
<｜end▁of▁sentence｜>
```

### 5.3 工具结果格式

DeepSeek V4 没有独立 standalone `tool` role。源码说明：

```text
tool messages are merged into user messages using content_blocks format
```

也就是说 OpenAI 风格：

```text
assistant tool_calls
tool result
```

会被转换为：

```text
assistant DSML tool_calls
user content_blocks: tool_result
```

### 5.4 工具结果排序

`sort_tool_results_by_call_order` 会按照前一个 assistant message 中的 tool_calls 顺序排序 tool_result blocks。

---

## 6. Quick Instruction Tasks

V4 encoding 支持特殊短任务 token：

| Task | Token | 用途 |
|---|---|---|
| action | `<｜action｜>` | 判断是否需要搜索 / 直接回答 |
| query | `<｜query｜>` | 生成搜索 query |
| authority | `<｜authority｜>` | 判断权威性需求 |
| domain | `<｜domain｜>` | 判断问题领域 |
| title | `<｜title｜>` | 生成会话标题 |
| read_url | `<｜read_url｜>` | 判断 URL 是否需要读取 |

这说明 V4 官方 encoding 已经把部分 Harness 任务模型化为 quick instruction token。

---

## 7. generate.py 与 encoding 的关系

`generate.py` 中：

```python
from encoding_dsv4 import encode_messages, parse_message_from_completion_text
...
prompt_tokens = tokenizer.encode(encode_messages(messages, thinking_mode="chat"))
completion = tokenizer.decode(completion_tokens[0])
messages.append(parse_message_from_completion_text(completion, thinking_mode="chat"))
```

这说明官方 demo 并不是直接把 messages 传给模型，而是：

```text
OpenAI-style messages
  ↓
encode_messages
  ↓
string prompt
  ↓
tokenizer.encode
  ↓
Transformer.forward
  ↓
completion string
  ↓
parse_message_from_completion_text
  ↓
structured assistant message
```

---

## 8. 对 DeepSeek Agent 的影响

DeepSeek Agent 应有一个独立模块：

```text
DeepSeekV4MessageCompiler
```

职责：

```text
OpenAI-compatible messages
+ tools
+ reasoning mode
+ response_format
+ latest_reminder
+ quick tasks
+ drop_thinking policy
+ cache-stable prefix policy
→ V4 prompt string
```

不能简单依赖 generic OpenAI adapter。

---

## 9. 新增物理特性编号

### P-033：V4 不使用 Jinja chat template，而是专门 encoding 实现

证据：模型卡和 `encoding/README.md`。

Harness 影响：DeepSeek Agent 应内置 V4-aware message compiler。

### P-034：chat mode 通过立即关闭 thinking block 实现 non-thinking

证据：encoding README / `render_message`。

Harness 影响：Non-think / Think 是 message protocol 层的重要开关。

### P-035：Max reasoning 是 prompt-level special prefix

证据：`REASONING_EFFORT_MAX` 只在 index 0 / thinking mode / max effort 注入。

Harness 影响：Max mode 会改变 prompt 前缀，可能破坏 cache；应只在关键节点使用。

### P-036：默认 drop old reasoning_content

证据：`drop_thinking=True` 与 `_drop_thinking_messages`。

Harness 影响：旧 reasoning 不应长期回传，减少上下文污染；但工具循环需特殊处理。

### P-037：有 tools 时 drop_thinking 自动 disabled

证据：`if any(m.get("tools") for m in full_messages): effective_drop_thinking = False`。

Harness 影响：长工具循环可能累积大量 reasoning，需要 Harness 外部压缩/归档策略。

### P-038：DeepSeek V4 tool calling 使用 DSML 格式

证据：`TOOLS_TEMPLATE`、`tool_calls_template`、`parse_tool_calls`。

Harness 影响：Tool schema 要稳定，DSML parse 失败需做 recovery。

### P-039：V4 没有 standalone tool role，tool results merge into user message

证据：`merge_tool_messages` 注释与实现。

Harness 影响：Agent Loop 设计不能机械照搬 OpenAI tool role；需要 V4-specific tool-result compiler。
