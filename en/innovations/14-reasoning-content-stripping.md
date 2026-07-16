# Reasoning Content Stripping: The Agent Should Know What Not to Send Back

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source code, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-14
> **LLM + Harness = Agent** · Part 14
> Series: [LLM + Harness = Agent](../../README.md)
> Related: [I-13 Byte-Stable Prefix Architecture](13-byte-stable-prefix-architecture.md)

---

## Problem: Tokens You Paid For That Provide Zero Value

A seemingly simple question: after a reasoning model finishes thinking, should you send its chain of thought back to the API on the next turn?

The intuitive answer is "yes — the model needs prior reasoning to maintain coherence." Claude Code does this. Most Agents do this. The OpenAI API format even has a dedicated `reasoning_content` field on the assistant message, implying you should send it back.

But with DeepSeek, here is what actually happens:

```
Turn 1: User asks question
  → Model generates: reasoning_content (~800 tokens) + response (~200 tokens)
  → Billed: prompt (cached) + completion (1000 tokens)

Turn 2: User follows up
  → You send: system + turn-1 message (containing 800 tokens reasoning_content) + new question
  → DeepSeek treats those 800 tokens of reasoning_content as: ordinary PROMPT INPUT
  → Billed: prompt (800 more tokens, not cache-eligible) + completion
  → Wasted per turn: ~500 tokens of meaningless prompt input, every single turn
```

A 50-turn coding session wastes roughly 25,000 tokens purely. In absolute terms that's small (¥0.007), but the problem is: **100% waste.** You are paying the model to re-read its own thoughts with zero benefit.

---

## Industry Default: Send Everything Back

Look at how current Agents handle reasoning content:

| Agent | Behavior | Cost Impact |
|-------|------|---------|
| **Claude Code** | Sends thinking blocks back (required by Anthropic, tool-call continuity) | Zero — Anthropic cache covers signed thinking blocks |
| **Hermes** | Stored in `assistant_msg["reasoning"]`, included in message history | Provider-dependent; not specifically stripped |
| **CodeWhale** | Not specifically documented | Unknown |
| **Reasonix** | **Conditional strip** of reasoning_content in `buildRequest()`: stripped on non-tool-call turns; preserved on tool-call turns (API protocol requirement) | Source confirmed: reduced input on non-tool-call turns; preserved on tool-call turns per API requirement |

The industry default is full send-back. Most Agent frameworks treat message history as a complete log — what the model said, you send all of it back. That's the simplest implementation: `messages.append(response)`, done. No filtering logic. No special cases.

But "simplest implementation" does not equal "correct behavior." And the gap between the two widens as reasoning models become the default.

---

## Key Distinction: What the Model Needs vs. What the Model Already Has

The core insight is surprisingly simple:

> **Whether reasoning content needs to be sent back is a provider-protocol question, not a universal truth.** Models typically need user messages, tool calls, and tool results to maintain task continuity; whether reasoning content also needs to be sent back must be tested per endpoint, thinking mode, and tool-calling protocol.

Think about how reasoning works. The model generates a chain of thought to arrive at an answer. That chain is **the process of getting the answer**, not **context for future answers**. Once the answer is given, reasoning has served its purpose.

This is fundamentally different from tool results. Tool results tell the model things it didn't know before — file contents, command output, grep matches. That is new information shaping future decisions. Reasoning content is merely a record of how the model processed information it already had.

**Three categories of assistant output:**

| Category | Example | Should Send Back? | Reason |
|------|------|----------|------|
| **Tool calls** | `read_file("main.go")` | ✅ Yes | Model needs to know which tools were called and their results |
| **Final answer** | "the bug is on line 42" | ⚠️ It depends | Dialogue coherence needs it, but compressible |
| **Reasoning content** | "let me think... first check..." | ⚠️ Per-protocol | May be for display only, or may be a required field for tool-call continuity |

Provider-specific knowledge becomes critical here. Anthropic's thinking blocks carry cryptographic signatures and *must* be sent back when tool calls follow thinking — that's a protocol requirement and they're cached. Some DeepSeek-compatible implementations can omit `reasoning_content`; other thinking/tool-call paths may require it or actively replay it. Its billing and caching behavior should also be governed by actual usage data from the specific endpoint.

A smart Agent should know which provider it's talking to and adjust send-back behavior accordingly.

---

## Implementation Case: Sending Fewer Fields Can Save Input Tokens

Reasonix's approach is extremely simple — but with an important exception. In `buildRequest()` of `openai.go`:

```go
// reasoning_content is deliberately NOT sent back for non-tool-call turns:
// it's a response-only field. DeepSeek accepts it but counts it as ordinary
// prompt input (measured ~500 extra tokens per turn on a reasoner chain).
//
// ⚠️ Important exception: when an assistant turn contains tool_calls,
// reasoning_content must be preserved (DeepSeek API protocol requirement —
// losing reasoning_content on tool_calls turns causes 400 errors)
cm := chatMessage{
    Role:       string(m.Role),
    Content:    m.Content,       // ← main content
    ToolCallID: m.ToolCallID,
    Name:       m.Name,
    // ReasoningContent not sent on non-tool-call turns; must be kept on tool-call turns
}
```

That's it. The `Message` struct has a `ReasoningContent` field. It exists in the session. It's shown to the user. But when constructing the API request, it is simply not copied to the wire format.

This "send fewer fields" code can reduce input tokens in long sessions; actual savings and correctness must be reproduced per endpoint and task.

---

## DeepSeek V4 Native Implementation: `_drop_thinking_messages`

Reasonix's implementation is a sound Harness-level choice. But the more interesting question is: **how does DeepSeek itself handle this?**

V4's `encoding_dsv4.py` gives a clear answer. This is not post-hoc remediation; it is native logic baked into the tokenizer encoding layer since V4 was trained.

### Core Mechanism: Two-Layer Filtering Architecture

V4's reasoning content stripping is not a single strategy but a **two-layer defense: data layer + render layer**:

```
encode_messages() entry (L510: drop_thinking=True)
  │
  ├─ Layer 1: _drop_thinking_messages() — data layer (L575-599)
  │   └─ Modifies the message list itself before rendering:
  │        · Keeps role ∈ {user, system, tool, latest_reminder, direct_search_results}
  │        · Keeps all messages after last_user_idx
  │        · Assistant before last_user_idx: removes reasoning_content field
  │        · Developer before last_user_idx: dropped entirely
  │
  └─ Layer 2: drop_thinking in render_message() — render layer (L344-348)
      └─ Even if reasoning_content leaks through, thinking_part is skipped at render time
```

#### Layer 1: `_drop_thinking_messages` — Subtracting at the Data Structure (L575-599)

```python
# encoding_dsv4.py L575-599
def _drop_thinking_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Drop reasoning_content and non-essential messages before the last user message.

    Behavior:
    - Messages with role in ["user", "system", "tool", "latest_reminder"] are always kept.
    - Messages at or after the last user index are always kept.
    - Assistant messages before the last user get reasoning_content removed.
    - Developer messages before the last user are dropped entirely.
    """
    last_user_idx = find_last_user_index(messages)  # L209
    result = []
    keep_roles = {"user", "system", "tool", "latest_reminder", "direct_search_results"}

    for idx, msg in enumerate(messages):
        role = msg.get("role")
        if role in keep_roles or idx >= last_user_idx:
            result.append(msg)
        elif role == "assistant":
            msg = copy.copy(msg)
            msg.pop("reasoning_content", None)  # ← in-place field deletion
            result.append(msg)
        # developer and other roles before last_user_idx are dropped

    return result
```

Key point: `msg.pop("reasoning_content", None)` performs **in-place deletion** (L595), not message filtering. The assistant message remains in the list — `content` and `tool_calls` intact — only the `reasoning_content` field is gone. This ensures the subsequent `render_message()` receives a clean message structure.

#### Layer 2: Defense in `render_message` (L344-348)

```python
# encoding_dsv4.py L344-348
if thinking_mode == "thinking" and not prev_has_task:
    if not drop_thinking or index > last_user_idx:
        thinking_part = thinking_template.format(reasoning_content=rc) + thinking_end_token
    else:
        thinking_part = ""  # ← even with residual data, render layer skips
```

The render layer has an independent `drop_thinking` check: even if layer-1 data cleaning fails for some reason, the render layer will not encode old-turn reasoning content into the prompt.

### tools Auto-Disable Drop: Protocol Over Optimization

V4's most notable design choice is at L548-551:

```python
# encoding_dsv4.py L548-551
# Resolve drop_thinking: if any message has tools defined, don't drop thinking
effective_drop_thinking = drop_thinking
if any(m.get("tools") for m in full_messages):
    effective_drop_thinking = False
```

As long as **any one** message in the message history carries a `tools` field, `drop_thinking` for the entire session is forced to `False`. This confirms Reasonix's observation noted earlier — losing reasoning_content on tool-call turns causes API errors (400) — but V4's implementation strategy differs: **not "check if the current turn has tool_calls then conditionally preserve," but "all-or-nothing"** — with tools, keep everything; without tools, strip everything.

This "all-or-nothing" strategy has two advantages:
1. **Implementation simplicity**: no per-turn tool_calls existence check; one Boolean decides the entire session
2. **Error-proof safety**: no edge case where "should have kept reasoning but misjudged" — either all kept or all stripped

The cost is that reasoning is kept for every turn in tool-call sessions, even when some turns don't contain tool_calls and could theoretically be safely stripped.

### Reasonix Go Implementation vs. DeepSeek V4 Python Implementation

| Dimension | Reasonix `buildRequest()` (Go) | V4 `_drop_thinking_messages` (Python) |
|------|-------------------------------|--------------------------------------|
| Stripping method | **Does not copy** `ReasoningContent` field to wire format when constructing API request | **In-place pop** of `reasoning_content` field + render-layer defense before prompt encoding |
| tool-call handling | Strips non-tool-call turns; keeps tool-call turns (API protocol requirement) | **Globally disables** drop if tools present; strips all if no tools |
| Defense layers | 1 layer (wire format boundary) | 2 layers (data structure layer + render layer) |
| Strategy granularity | Per-turn judgment | All-or-nothing |
| Timing | API request construction | Tokenizer encoding (well before the API request) |
| Other message types handled | Focuses on reasoning content only | Also handles developer messages (dropped entirely), keeps keep_roles messages |
| Evidence level | A0 (source confirmed, running in production) | A1 (source confirmed, not reproduced in actual deployment) |

### Design Insight: Why V4 Puts Stripping at the Tokenizer Layer

Reasonix does stripping at the API boundary — specifically when constructing the HTTP request body, deciding what to send and what not to send. V4 does it at the tokenizer encoding layer, earlier and deeper.

This means:

1. **Token counting is also the correct accounting boundary**: because stripping happens before tokenization, removed reasoning participates in neither token counting nor prompt cache computation
2. **Integrated with other encoding logic**: `_drop_thinking_messages` executes right after `merge_tool_messages` and `sort_tool_results_by_call_order` (L538-554); tool message processing, sorting, and reasoning stripping all live in the same pipeline
3. **Does not depend on upper-layer callers**: even if the Harness forgets to handle reasoning content, V4's encoding layer cleans up as a safety net — as long as the Harness correctly calls `encode_messages()`

> **Evidence level: A1** (source confirmed, Flash and Pro implementations identical). The existence and complete logic of `_drop_thinking_messages` are verified by `encoding_dsv4.py` L575-599; the two-layer protection is confirmed by the collaboration between L344-348 and L595; global tool disable is verified by L548-551. Specific token-saving figures still require real measurement (evidence level B).

---

## General Principle: The Agent's "Do Not Send" Checklist

Zooming out from reasoning content. Every Agent should maintain an explicit checklist: what should not be included in API requests — even if stored locally.

**"Do Not Send" Checklist:**

1. **Reasoning content** — decide drop / replay / summarize per provider contract, and log usage
2. **Overly large tool schemas** — shrink tool surface via stable ordering and progressive disclosure; most APIs still require the full tools field per request and cannot be assumed to support deltas
3. **Stale system instructions** — if a constraint is superseded, delete the old version rather than just appending a new one
4. **Redundant error messages** — truncate to the actionable portion; models don't need full stack traces
5. **Redundant file contents** — if a file was read, modified, and read again, the old read result is noise

Each is a small optimization. Cumulatively, that is the difference between an Agent that "bleeds tokens" and one that is "surgically precise."

---

## What This Means for Hermes

Hermes currently stores reasoning content in `assistant_msg["reasoning"]` and includes it in the message history sent to the API. For Anthropic models this is correct (signed thinking blocks, cached). For DeepSeek-compatible endpoints, it needs verification whether this constitutes waste and whether it would break tool-call continuity.

The fix is not complex:

1. **Provider-aware message policy.** Before constructing the API request payload, select drop / replay / summarize based on provider, model, thinking mode, and tool-calling stage; only strip when protocol testing confirms it is deletable.

2. **Keep reasoning for display.** The Session DB and user chat view should still show reasoning. Stripping happens only at the API boundary — the last layer before the HTTP request.

3. **Make it a configurable strategy.** Some users want reasoning in context for debugging or research. Default strategy must come from protocol testing; allow per-provider, per-model, per-mode configuration, with safe fallback on error.

---

## Deeper Insight: Every Token Should Justify Its Existence

Reasoning content stripping is the most obvious case, but the underlying principle is broader:

> **Every token in an API request should have a clear reason to exist. If it neither provides new information the model needs nor contributes to cache stability, it is waste.**

That sounds like a tautology. But most Agent codebases don't operate this way. They operate on "include everything in the session." Message history is treated as a complete log, and the complete log is sent to the API.

Cache-first agents invert this. They ask: "what is the **minimum** set of tokens the model needs to produce its next response?" Everything else — display content, debug logs, internal state, past reasoning — stays local.

Reasonix got this right in one specific case. The next step is to apply the same scrutiny to **every content category** the Agent sends.

---

## 5. Validation Path

### 5.1 Validated (Source Confirmed)

The following facts are directly confirmed by fixed-version `encoding_dsv4.py` source code, evidence level A1:

| # | Fact | Evidence | Level |
|---|------|------|------|
| 1 | `encode_messages()` defaults to `drop_thinking=True` | L510 | A1 |
| 2 | When any message contains a `tools` field, `effective_drop_thinking` is forced to `False` | L548-551 | A1 |
| 3 | `_drop_thinking_messages` keeps messages with role ∈ `{user, system, tool, latest_reminder, direct_search_results}` | L587 | A1 |
| 4 | `_drop_thinking_messages` uses `msg.pop("reasoning_content", None)` to delete the field in place (L595), rather than deleting the entire message | L594-595 | A1 |
| 5 | Developer messages before last_user_idx are dropped entirely | L597 (implicit: not in keep_roles and not assistant, so skipped) | A1 |
| 6 | `render_message` has an independent `drop_thinking` check as a render-layer defense (L344-348) | L344-348 | A1 |
| 7 | `_drop_thinking_messages` is called in `encode_messages()` after tool message merging and sorting, before rendering | L553-554 | A1 |
| 8 | Reasonix conditionally strips `reasoning_content` on non-tool-call turns in `buildRequest()` | Go source reviewed | A0 |

### 5.2 To Be Validated

The following inferences require real-measurement confirmation, current evidence level B (engineering inference):

#### Experiment 1: Token Savings Measured

```
Tools: DeepSeek V4 API, 100-turn coding session (no tool_calls)
Compare:
  A. Send back all reasoning_content (drop_thinking=False)
  B. Strip historical reasoning_content (drop_thinking=True, default)
Measure: prompt input token count per turn, total session cost
Expect: Group B saves ~500 tokens per turn (consistent with the magnitude described in Reasonix docs),
        50 turns cumulative savings ~25,000 tokens
```

#### Experiment 2: Necessity of Reasoning in Tool-Call Sessions

```
Tools: DeepSeek V4 API, 50-turn coding session with tool_calls
Question: V4 chose the "keep all when tools present" strategy (L548-551),
          but not every tool_calls turn needs prior reasoning
Compare:
  A. Keep all reasoning (default behavior)
  B. Only keep reasoning for turns containing tool_calls, strip pure-text turns' reasoning
Measure: whether the model correctly completes multi-step tool-call tasks, whether any 400 errors
Expect: Group B may work in specific scenarios, but V4 chose safety-first "all-or-nothing"
```

#### Experiment 3: Behavioral Differences Across Thinking Modes

```
Tools: DeepSeek V4, thinking_mode="chat" vs "thinking"
Compare:
  A. chat mode + drop_thinking=True
  B. chat mode + drop_thinking=False
  C. thinking mode + drop_thinking=True
  D. thinking mode + drop_thinking=False
Measure: token consumption per mode, reasoning quality (multi-turn consistency), tool-call accuracy
Note: in chat mode the model produces no thinking block, so the drop_thinking parameter may have no practical effect
```

#### Experiment 4: Harness Adaptation Verification

```
Task: Integrate V4's encoding_dsv4.py as the tokenization layer in Reasonix or Hermes
Measure:
  - Lines of code needed for adaptation (~50 lines Go/Python wrapper estimated)
  - Whether _drop_thinking_messages default behavior is correctly utilized
  - Whether _drop_thinking_messages's msg.pop() affects Harness-local message cache
Key issue: V4's stripping modifies the message object itself (L595: msg.pop),
           the Harness needs to deep copy to avoid accidental local state mutation
```

---

*This article is based on tracing Reasonix's `buildRequest()` source analysis (Go), plus source verification of DeepSeek V4's official `encoding/encoding_dsv4.py` lines 575-599 (`_drop_thinking_messages`) and lines 344-348 (the `drop_thinking` logic in `render_message`). V4 source version: Flash and Pro are identical (744 lines).*
