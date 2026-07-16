# Quick Instruction Routing: DeepSeek V4's Built-In Task Dispatch Mechanism

> **Evidence note:** This paper presents design hypotheses based on the definition of Quick Instruction special tokens and message rendering logic in `encoding_dsv4.py`. The actual effectiveness of each Task requires validation in real API scenarios. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-16
> **LLM + Harness = Agent** · Part 16
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [I-15 DSML Tool-Call Format Optimization](15-dsml-tool-call-optimization.md)
> Next: [I-17 Reasoning Effort Control](17-reasoning-effort-control.md)

---

## Problem: How Can One Model Handle Chat, Search Routing, and Title Generation Simultaneously?

The traditional approach deploys a dedicated model or prompt for each task. Chat has a chat model, search-intent classification has a classifier, title generation has a summarization model. Each model is trained, deployed, and invoked independently — latency stacks, costs stack.

DeepSeek V4 takes a different approach: **one model handles all these tasks, using special tokens embedded in the text stream to trigger distinct behavioral modes.** This is the Quick Instruction system.

---

## Key Evidence: Six Task Token Definitions

`encoding_dsv4.py` explicitly defines six Quick Instruction special tokens (L28-35):

```python
# Task special tokens for internal classification tasks
DS_TASK_SP_TOKENS = {
    "action": "<｜action｜>",
    "query": "<｜query｜>",
    "authority": "<｜authority｜>",
    "domain": "<｜domain｜>",
    "title": "<｜title｜>",
    "read_url": "<｜read_url｜>",
}
VALID_TASKS = set(DS_TASK_SP_TOKENS.keys())
```

These tokens are not intended for users to see, nor for Agent developers to manually concatenate. They are injected into the encoded prompt through the `task` field of message objects.

---

## Mechanism: How Task Tokens Trigger Model Behavior

In `render_message()` (L369-383), when a message carries a `task` field, the encoding logic appends the corresponding special token at the end of the message according to the task type:

```python
task = messages[index].get("task")
if task is not None:
    assert task in VALID_TASKS, f"Invalid task: '{task}'..."
    task_sp_token = DS_TASK_SP_TOKENS[task]

    if task != "action":
        # Non-action tasks: append task sp token directly after the message
        prompt += task_sp_token
    else:
        # Action task: append Assistant + thinking token + action sp token
        prompt += ASSISTANT_SP_TOKEN
        prompt += thinking_end_token if thinking_mode != "thinking" else thinking_start_token
        prompt += task_sp_token
```

Key distinction:
- **Non-action tasks** (query, authority, domain, title, read_url): the Task Token is appended directly after the message, with no Assistant prefix. This means the model is asked to output the task result directly, without generating a full conversational response.
- **action task**: an additional `＜｜Assistant｜＞` and thinking marker are prepended before the token, simulating a standard assistant reply opening. The model generates from this starting point, outputting a routing decision (such as "Search" or "Answer").

---

## What the Six Tasks Each Do

| Task | Encoding Position | Purpose |
|------|---------|------|
| **action** | After user message + `＜｜Assistant｜＞` + thinking + `＜｜action｜＞` | Determines whether the user's question requires a web search or can be answered directly. Outputs a short routing decision. |
| **query** | Appended directly after user message | Generates a search-engine query string from the user prompt. Does not generate a full reply — only outputs the query string. |
| **authority** | Appended directly after user message | Classifies the degree of authoritative-source requirement in the user prompt (e.g. finance/medicine need high-authority sources). |
| **domain** | Appended directly after user message | Identifies the domain classification of the user prompt (e.g. programming, mathematics, literature). |
| **title** | Appended after Assistant reply | Generates a concise conversation title from the dialogue content. Used in multi-turn conversation list display. |
| **read_url** | Used alongside `＜｜extracted_url｜＞` | Determines whether each URL mentioned in the prompt should be fetched and read. |

---

## Why This Matters for Harness

### 1. Significant Reduction in Request Latency

Under the traditional architecture, a "user asks → search → answer" flow might require 3 model calls: routing (should we search?), query generation (what to search for), and final answer. The network latency for each call stacks independently.

Quick Instruction compresses routing and query generation into single-token or extremely short outputs. An `action` task output might be just the word "Search" — a few tokens completing what previously required a full round of inference.

### 2. Implementation Cost

Quick Instruction Tokens are appended to the end of the prompt and do not add length to the system prompt. However, each Quick Instruction call is still an independent API request, and the prompt must be resent. If your application needs a quick routing decision between "search" and "no-search", you can first use a short prompt + action task to decide, then determine whether to construct a full search prompt — rather than sending the full system prompt and tool definitions with every message.

### 3. Integration at the Harness Layer

The Harness can set the `task` field in message objects to trigger these behaviors:

```python
# Determine whether search is needed
messages = [
    {"role": "user", "content": "What's the weather today?", "task": "action"}
]
# → model outputs "Search"

# Generate a search query
messages = [
    {"role": "user", "content": "What's the weather today?", "task": "query"}
]
# → model outputs "Beijing weather forecast 2026-07-16"
```

No additional model or prompt engineering is required. The Harness only needs to know which scenario uses which task, then populate the `task` field in the message object.

---

## Limitations and Open Questions

1. **Uncontrolled task output.** Quick Instruction output has no strict schema. The model might return "Search", or "Search\n", or add extra explanation. The Harness needs to perform output cleaning.
2. **Unknown interactions with other features.** What happens when a message has both `task` and `tools`? The source code appends the task token at the end of the message, but if the message simultaneously has tool_calls, unexpected token sequences may result.
3. **Behavioral differences across thinking modes.** The `action` task has different encoding logic in chat mode and thinking mode (L381), but the minimal actual difference requires experimental verification.

---

## Validation Path

1. Set `task="action"` and `task=None` on the same prompt, comparing the length and content of the model output.
2. Measure end-to-end latency for the action task: one call with `task="action"` vs. the first inference turn of a full dialogue — verify the latency advantage.
3. Test behavior when task and tool_calls coexist: whether token sequence errors occur.

---

*This article is based on lines 28-35 of `encoding_dsv4.py` (DS_TASK_SP_TOKENS definition) and lines 369-383 (task token rendering logic), combined with Quick Instruction descriptions in the DeepSeek V4 encoding documentation.*
