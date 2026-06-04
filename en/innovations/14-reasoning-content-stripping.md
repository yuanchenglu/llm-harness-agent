# Reasoning Content Stripping: Agent Should Know What NOT to Send

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, “validated” does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-14
> **LLM + Harness = Agent** · Part 14
> Series: [LLM + Harness = Agent](../../README.md)
> Related: [I-13 Byte-Stable Prefix Architecture](13-byte-stable-prefix-architecture.md)

---

## The Problem: Tokens That Cost Money But Add Zero Value

Here's a deceptively simple question: after a reasoning model thinks through a problem, should you send its chain-of-thought back to the API on the next turn?

The intuitive answer is "yes — the model needs its previous reasoning to maintain coherence." Claude Code does it. Most agents do it. The OpenAI API format even has a dedicated `reasoning_content` field on the assistant message, implying you're supposed to round-trip it.

Here's what actually happens when you do this with DeepSeek:

```
Turn 1: User asks a question
  → Model generates: reasoning_content (~800 tokens) + response (~200 tokens)
  → You're billed: prompt (cached) + completion (1000 tokens)

Turn 2: User asks a follow-up
  → You send: system + turn-1-messages (including 800 tokens of reasoning_content) + new question
  → DeepSeek treats that 800-token reasoning_content as: ORDINARY PROMPT INPUT
  → You're billed: prompt (800 extra tokens, NOT cached) + completion
  → Cost per turn: +~500 tokens of wasted prompt input, every single turn
```

Over a 50-turn coding session, that's roughly 25,000 tokens of pure waste — roughly ¥0.007 at DeepSeek's current pricing. Small in absolute terms, but it's 100% waste. You're paying the model to re-read its own thoughts, and getting nothing in return.

---

## The Industry Default: Echo Everything Back

Let's look at what current agents do with reasoning content:

| Agent | Behavior | Cost Impact |
|-------|----------|-------------|
| **Claude Code** | Sends thinking blocks back (required by Anthropic for tool-call continuity) | Zero — Anthropic's cache covers signed thinking blocks |
| **Hermes** | Stores reasoning in `assistant_msg["reasoning"]`, included in message history | Provider-dependent; not specifically stripped |
| **CodeWhale** | Not specifically documented | Unknown |
| **Reasonix** | **Explicitly strips** reasoning_content in `buildRequest()` | Saves ~500 tokens/turn on DeepSeek |

The industry's default behavior is to echo everything back. Most agent frameworks treat message history as a complete log — whatever the model said, you send it back. This is the simplest implementation: `messages.append(response)`, done. No filtering logic. No special cases.

But "simplest implementation" is not the same as "correct behavior." And the gap between them is growing as reasoning models become the default.

---

## The Distinction: What the Model Needs vs. What the Model Already Has

The key insight is deceptively simple:

> **Whether reasoning must be replayed is a provider-contract question, not a universal truth.** User messages, tool calls, and tool results usually carry task continuity; reasoning content may be display-only or protocol-required depending on endpoint, thinking mode, and tool-call flow.

Think about how reasoning works. The model generates a chain-of-thought to arrive at its response. That chain-of-thought is *the process of getting to the answer*, not *context for future answers*. Once the answer is delivered, the reasoning has served its purpose.

This is fundamentally different from tool results. A tool result tells the model something it didn't know before — a file's contents, a command's output, a grep match. That's new information that shapes future decisions. Reasoning content is just a record of how the model thought about information it already had.

**Three categories of assistant output:**

| Category | Example | Should you send it back? | Why |
|----------|---------|------------------------|-----|
| **Tool calls** | `read_file("main.go")` | ✅ Yes | The model needs to know what tools it called and their results |
| **Final answers** | "The bug is on line 42" | ⚠️ Depends | Part of conversation coherence, but can be summarized |
| **Reasoning content** | "Let me think about this... first I'll check..." | ⚠️ By contract | It may be display-only or required for tool-call continuity |

This is where provider-specific knowledge becomes critical. Anthropic's thinking blocks carry cryptographic signatures and *must* be echoed back when a tool call follows thinking — it's a protocol requirement, and cached. DeepSeek's reasoning_content has no such requirement — it's accepted but **billed as ordinary input with no cache benefit**.

A smart agent should know which provider it's talking to and adjust its re-upload behavior accordingly.

---

## Implementation Case: Sending Fewer Fields May Reduce Input Tokens

Reasonix's approach is dead simple. In `openai.go`, inside `buildRequest()`:

```go
// reasoning_content is deliberately NOT sent back: it's a response-only
// field. DeepSeek accepts it but counts it as ordinary prompt input
// (measured ~500 extra tokens per turn on a reasoner chain), and the
// OpenAI-compatible convention is not to echo it. The session still keeps
// it (for display/archive); we just don't pay to re-upload it every turn.
cm := chatMessage{
    Role:       string(m.Role),
    Content:    m.Content,       // ← main content
    ToolCallID: m.ToolCallID,
    Name:       m.Name,
    // ReasoningContent is NOT included here
}
```

That's it. The `Message` struct has a `ReasoningContent` field. It's stored in the session. It's displayed to the user. But when building the API request, it's simply not copied into the wire format.

Three lines of *not doing something* that save thousands of tokens over a session.

---

## The General Principle: The Agent's "Do Not Send" List

Zoom out from reasoning content. Every agent should maintain an explicit list of what it should NOT include in API requests, even if it stores that information locally.

**The "Do Not Send" Checklist:**

1. **Reasoning content** — choose drop / replay / summarize by provider contract and measure usage
2. **Oversized tool schemas** — use stable ordering and progressive disclosure; most APIs still require the complete tools field on every request and do not accept arbitrary deltas
3. **Stale system instructions** — if a constraint was superseded, remove the old version, don't just append the new one
4. **Verbose error messages** — truncate to the actionable part; the model doesn't need the full stack trace
5. **Redundant file contents** — if a file was read, changed, and read again, the old read is noise

Each of these is a small optimization. Cumulatively, they're the difference between an agent that bleeds tokens and one that's surgical.

---

## What This Means for Hermes

Hermes currently stores reasoning content in `assistant_msg["reasoning"]` and includes it in the message history sent to the API. For Anthropic models, this is correct (signed thinking blocks, cached). For DeepSeek, this is wasteful.

The fix isn't complex:

1. **Provider-aware message filtering.** Before building the API request payload, check the provider. If DeepSeek (or any OpenAI-compatible provider that doesn't cache reasoning), strip `reasoning_content` from assistant messages.

2. **Keep reasoning for display.** The session DB and the user's chat view should still show the reasoning. The strip happens at the API boundary only — the last layer before the HTTP request.

3. **Make it a configurable policy.** Some users want reasoning in context for debugging or research. Default to stripped for cost efficiency, allow opt-in.

---

## The Deeper Insight: Every Token Should Justify Its Existence

Reasoning content stripping is the most visible case, but the underlying principle is broader:

> **Every token in an API request should have a clear justification for being there. If it doesn't provide new information the model needs, or contribute to cache stability, it's waste.**

This sounds obvious. But most agent codebases don't operate this way. They operate on "include everything the session contains." The message history is treated as a complete log, and the complete log is sent to the API.

A cache-first agent inverts this. It asks: "what is the *minimum* set of tokens the model needs to produce the next response?" Everything else — display content, debugging logs, internal state, past reasoning — stays local.

Reasonix got this right for one specific case. The next step is to apply the same scrutiny to *every* category of content the agent sends.

---

*Written after tracing how `buildRequest()` constructs the API payload in Reasonix's OpenAI provider, and comparing against Hermes's message assembly in `run_conversation()` and Anthropic's signed-thinking protocol.*
