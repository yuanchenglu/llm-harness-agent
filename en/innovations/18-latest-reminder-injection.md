# Latest Reminder Injection: Why Some Information Shouldn't Live in the System Prompt

> **Evidence note:** This paper presents design hypotheses based on the definition of `LATEST_REMINDER_SP_TOKEN` in `encoding_dsv4.py` and the rendering logic of the `latest_reminder` role. The actual attention weight difference between `latest_reminder` and system prompt requires experimental validation. Please read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-18
> **LLM + Harness = Agent** · Part 18
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [I-17 Reasoning Effort Control](17-reasoning-effort-control.md)
> Next: (none)

---

## Problem: The System Prompt Says "Today is 2026-07-16", So Why Is the Model Still Using Yesterday's Date?

You have a well-crafted system prompt. It begins with the model's identity, lists tool descriptions in the middle, and ends with a line that says "Current date: 2026-07-16." Everything looks correct.

But the model occasionally gets the date wrong in its responses, or asks what time it is. Why?

The answer lies in the attention mechanism. The system prompt sits at the **beginning** of the prompt. After the model generates hundreds of tokens of reasoning, tool calls, and replies, attention has already drifted significantly away from that date line at the tail end of the system prompt. It's not intentional — it's attention decay caused by physical distance.

DeepSeek V4 offers an elegant solution: the `latest_reminder` role.

---

## Key Evidence: A Special Role + A Special Token

`encoding_dsv4.py` defines the `latest_reminder` role and its dedicated special token (L25, L44, L313-314):

```python
LATEST_REMINDER_SP_TOKEN = "<｜latest_reminder｜>"

latest_reminder_msg_template: str = "{content}"
```

In `render_message()`, the rendering logic for the `latest_reminder` role is extremely simple:

```python
elif role == "latest_reminder":
    prompt += LATEST_REMINDER_SP_TOKEN + latest_reminder_msg_template.format(content=content)
```

It's a straightforward concatenation: `<latest_reminder>` + content. No tool definitions, no format templates, no extra wrapping.

But simplicity does not mean insignificance. The key is its **insertion position**.

---

## Core Design: Insertion Position Determines Attention Weight

Look at the logic controlling the insertion position of `latest_reminder` in `render_message()` (L366):

```python
if index + 1 < len(messages) and messages[index + 1].get("role") not in ["assistant", "latest_reminder"]:
    return prompt
```

The meaning of this logic: **after a `latest_reminder` message, if the next message is not an assistant or another `latest_reminder`, return immediately — do not append any transition token.**

Combined with the main loop of `encode_messages()` (L563-570), the `latest_reminder` message appears in the message list during encoding — typically placed just before the last user message.

This means the position of `latest_reminder` in the complete prompt is:

```
<bos>{system_prompt}
<User>{history_msg1}<Assistant>{reply1}<end>
<User>{history_msg2}<Assistant>{reply2}<end>
<latest_reminder>Current date: 2026-07-16
<User>{latest_user_question}<Assistant>
```

Notice: `latest_reminder` is placed immediately before the **latest user message**. In the KV Cache architecture, this is the position with the highest attention concentration — closest to the latest user query, closest to the tokens the model is about to generate.

Compare this: if that date information is placed in the system prompt, its token position could be hundreds or even thousands of tokens away from where the model is about to generate. Attention naturally decays.

---

## Essential Difference from System Prompt

| Dimension | System Prompt | latest_reminder |
|-----------|-------------|------------------|
| Position | Beginning of prompt (farthest from tokens being generated) | Before the last user message (closest to tokens being generated) |
| Content nature | Stable: identity, norms, tool definitions | Volatile: date, timezone, user location, temporary instructions |
| Cache behavior | Ideal cache target (stable content, frequently reused) | Should not be cached — different each session |
| Attention weight | Low (decays with token distance) | High (recency effect) |
| Suitable information | "You are a Python expert, follow PEP 8" | "Today is 2026-07-16, you are in Beijing" |

This leads directly to a design principle: **put stable constraints in the system prompt (for caching), and time-sensitive information in latest_reminder (for attention).**

---

## Implications for Harness

### 1. Prompt Decomposition: Stable Layer vs. Volatile Layer

Traditional agents stuff everything into a single system prompt. DeepSeek V4 gives us a better way:

```python
# Stable layer (KV Cache reused across invocations)
system_prompt = "You are a Python expert..."  # identity, norms, tools

# Volatile layer (dynamically injected per turn)
latest_reminder = f"Current date: {today()}, user location: {location}"

messages = [
    {"role": "system", "content": system_prompt},
    # ...history messages...
    {"role": "latest_reminder", "content": latest_reminder},
    {"role": "user", "content": user_question},
]
```

### 2. Not Just Dates and Locations

`latest_reminder` can carry any dynamic information the model needs to see before responding:

- The user's current page or context
- A summary of the last reply (helping the model remember key points in long conversations)
- Temporary constraints ("Do not use the search tool in this session")
- User state ("The user has expressed dissatisfaction 3 times in a row — respond with caution")

### 3. Complementarity with [I-04 KV Cache Hard Constraint Prefix Injection](04-kv-cache-prefix.md)

I-04 discussed the strategy of injecting stable constraints into the KV Cache prefix. `latest_reminder` is the dual of this approach: **put volatile information that needs high attention at the opposite end from the prefix — the latest content zone.**

The two work together: stable constraints go into the prefix cache (saving latency), volatile information goes into latest_reminder (preserving attention).

---

## Limitations and Open Questions

1. **The degree of attention weight improvement needs quantification.** "Closer means higher attention" is a theoretical property of the Transformer architecture, but the actual effect difference between `latest_reminder` and "putting the same content at the end of the system prompt" requires controlled experiments.

2. **Interaction with `drop_thinking`.** The `_drop_thinking_messages()` function (L575-599) preserves messages with the `latest_reminder` role, but whether other preprocessing functions (such as `merge_tool_messages`) affect the semantics of `latest_reminder` needs investigation.

3. **Whether the model was trained to pay special attention to this token.** If `<latest_reminder>` exists only at the prompt engineering level and the model never saw it as a special token during training, the effect may be limited. However, the token's name (`SP_TOKEN`, i.e., special token) suggests it is very likely part of the training data.

4. **The difference from date instructions in the system message.** An A/B test on the same task is needed: date in the system prompt vs. date in latest_reminder — to see which one the model uses more accurately.

---

## Validation Path

1. Construct a date-sensitive task (e.g., "Find movies showing today"), comparing accuracy when the date is provided in the system prompt vs. in latest_reminder.
2. Repeat the test at different conversation lengths (5 turns, 20 turns, 50 turns) to verify whether attention decay worsens as the conversation grows longer (latest_reminder's advantage should increase accordingly).
3. Measure the actual impact of latest_reminder on KV Cache behavior — whether it prevents partial cache reuse.

---

*This article is based on line 25 of encoding_dsv4.py (LATEST_REMINDER_SP_TOKEN definition), lines 313-314 (latest_reminder role rendering logic), and line 366 (inter-message transition token control logic).*
