# Byte-Stable Prefix as Architecture Constraint: Don't Just Cache the System Prompt — Make the Whole Agent Cache-First

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, “validated” does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-13
> **LLM + Harness = Agent** · Part 13
> Series: [LLM + Harness = Agent](../../README.md)
> Related: [I-04 KV Cache Prefix Injection](04-kv-cache-prefix.md) · [I-05 Document KV Cache](05-document-kv-cache.md)

---

## The Problem: Cache Awareness Should Be Architecture, Not Afterthought

I-04 established a principle: "constraints survive not because compression is smart, but because they were never in the compression zone." That was about physical separation — put critical instructions in the KV Cache prefix zone where compression can't reach them.

But a deeper question lurks: **should "cache awareness" be a feature you bolt on, or a constraint that shapes the entire agent architecture?**

Look at the state of the industry. Every major agent platform has *some* form of cache optimization:

- **Hermes** persists `_cached_system_prompt` to the session DB and restores it on the next turn
- **Claude Code** uses Anthropic's 1-hour prompt cache with system prompt segmentation
- **CodeWhale** places `<user_memory>` "above the volatile-content boundary" in prompt assembly

These are all **features**. A function call here, a conditional there. The system prompt is cached when convenient, rebuilt when necessary. Cache awareness is a leaf node in the architecture tree.

But there's another way.

What if cache stability were *not* a feature, but the **root constraint** from which every other architectural decision flows?

What if every component — Memory, Skills, Plan Mode, Model Switching, Context Compaction — had to answer one question before anything else:

> **"Does this decision preserve byte-stability of the system prompt prefix?"**

This is the architecture I found in **DeepSeek-Reasonix** (esengine/DeepSeek-Reasonix). And it's not marketing. It's in every layer of the source code.

---

## The Architecture: Cache-First as Root Constraint

Here's what "cache-first architecture" actually means in code. I've verified every claim below against the Go source at `internal/`.

### The Boot Sequence: Assemble Once, Freeze Forever

```go
// boot.go L100-124 — the system prompt is assembled ONCE at boot
sysPrompt = outputstyle.Apply(sysPrompt, st)     // 1. Output style
sysPrompt += "\n\n" + config.LanguagePolicy       // 2. Static language policy
sysPrompt = memory.Compose(sysPrompt, mem)         // 3. Memory (base stays first)
sysPrompt = skill.ApplyIndex(sysPrompt, skills)    // 4. Skills index (names only, no bodies)
```

After this point, `sysPrompt` is a frozen byte sequence. It never changes for the rest of the session. Not when the user toggles plan mode. Not when memory is saved. Not when a background job completes.

Every change that must reach the model in-session rides **the turn tail** — injected into the user message, not the system prefix:

```go
// input.go L18-52 — Compose() prepends transient context to the USER message
func (c *Controller) Compose(text string) string {
    if plan { text = PlanModeMarker + "\n\n" + text }       // Plan mode → user message
    if len(notes) > 0 { text = "<memory-update>..." + text }  // Mid-session memory → user message
    if c.jobs != nil { text = "<background-jobs>..." + text }  // BG completion → user message
    return text
}
```

This is the architectural inversion. In most agents, you'd modify the system prompt. In a cache-first agent, you treat it as a controlled change rather than a casual mutation. The system prompt is frozen by default; security updates, tool changes, or corrections may explicitly rebuild it.

---

### Six Places Where This Constraint Shapes Design

Let me trace how this single constraint propagates through six distinct subsystems.

#### 1. Memory: Base-First Protocol, Mid-Session Injection

```go
// memory.go L148-152
// Base stays first (it is the most stable text, so
// it remains a valid cache prefix even when memory changes between sessions)
func Compose(base string, s *Set) string {
    block := s.Block()
    if block == "" { return base }  // No memory → base unchanged → maximal cache prefix
    return strings.TrimRight(base, "\n") + "\n\n" + block
}
```

Two design decisions here:

- **Base stays first.** Even if memory changes between sessions, the base prompt is unchanged → DeepSeek's prefix cache still hits the base portion.
- **Mid-session memory writes never touch the prefix.** When the `remember` tool saves a fact, it's stored to disk immediately, but the model learns about it through a `<memory-update>` block in the *next turn's user message*, not a system prompt mutation. It joins the prefix naturally on the *next session's boot*.

This is the opposite of "just append to the system prompt." It's a temporal protocol: session-N-1 writes → session-N's boot absorbs it into the immutable prefix.

#### 2. Skills: Index in Prefix, Body on Demand

```go
// index.go L9 — the package's declared contract
// cache-stable system-prompt prefix; bodies never enter the prefix.
```

Only skill **names and one-line descriptions** enter the system prefix. Each skill body is loaded on demand via `run_skill` tool or `/name` slash command. Why? Because skill bodies change — you install new skills, you edit existing ones. If bodies were in the prefix, every skill change would bust the cache. Index-only means the prefix grows by a fixed, small amount regardless of how many skills you have.

#### 3. Plan Mode: Toggle Without Trace

```go
// agent.go L127-130
// planMode, when true, refuses any tool call whose ReadOnly() is false.
// The system prompt and tool list never change with the toggle so the
// prompt-cache prefix stays valid; the gating happens at execute time
```

Plan mode toggles a boolean in the agent. It changes behavior — writers are refused, the model gets a "blocked" result. But the system prompt and tool schema are byte-identical. The toggle costs **zero cache hits**.

The marker `[Plan mode — read-only...]` is a Go `const` string. It gets prepended to the user message by `Compose()`. It never touches the system prefix. It never touches the tools.

#### 4. Two-Model Collaboration: Separate Sessions or Nothing

```go
// coordinator.go L25-27
// Coordinator runs two models in separate sessions to keep each one's
// prompt prefix cache-stable. The sessions never mix, so
// neither model's prefix is disturbed by the other's turns.
```

The obvious way to add a "planner model" is to let the executor call the planner mid-conversation — switch the model for one turn, get a plan, switch back. This is what most implementations would do.

Reasonix does the opposite. Planner and executor get **independent sessions with independent system prompts**. The planner's session grows prepend-only. The executor's session grows prepend-only. They never share a message. The SPEC explicitly states:

> *"switching models inside one shared conversation would break the prefix and tank cache hits, so we don't."*

When "cache stability" is the root constraint, you don't fix the model-switching problem — you make model-switching architecturally impossible.

#### 5. Reasoning Content: Don't Pay Twice for Thinking

```go
// openai.go L171-184
// reasoning_content is deliberately NOT sent back: it's a response-only
// field. DeepSeek accepts it but counts it as ordinary prompt input
// (measured ~500 extra tokens per turn on a reasoner chain)
```

`reasoning_content` replay is endpoint- and mode-specific. Some implementations drop it to reduce input; other tool/thinking paths replay it. Protocol and usage experiments must decide the policy.

Reasonix strips it in `buildRequest()`. The session keeps it locally for display and archive, but it never reaches the API again.

This isn't a "cache optimization." It's a cost optimization enabled by the cache-first architecture — knowing exactly what the model needs vs. what it already has.

#### 6. Context Compaction: The ONLY Cache Reset Point

```
SPEC.md L177-197
- When prompt_tokens reach compactRatio (0.8) of context_window, compact ONCE
- Session becomes: system + summary + recentKeep (default 8) verbatim messages
- This is the ONLY point where the prompt prefix changes
- Between compactions the session grows prepend-only
```

Compaction is not a continuous background process. It fires exactly once when the token count crosses 80% of the context window. After compaction, the prefix is reset — a deliberate cache-reset point. Between compactions, every turn is a pure append. The prefix is byte-stable.

Default settings: 1M token window × 0.8 = 800K prompt tokens before first compaction. In a typical coding session, that's dozens of turns of cache-stable operation.

---

## The Principle: Separate "What Changes" from "What Stays"

If you zoom out, all six of these design decisions are instances of one principle:

```
┌─────────────────────────────────────────────┐
│  STABLE ZONE (system prefix, frozen at boot) │
│  • Base prompt                               │
│  • Output style / language policy            │
│  • Memory (hierarchical docs + auto-index)   │
│  • Skills index (names + descriptions only)  │
│  • Tool schemas                              │
│  ═══════════════════════════════════════════ │
│  → NEVER changed mid-session                 │
│  → DeepSeek prefix cache hits 100% of this   │
├─────────────────────────────────────────────┤
│  VOLATILE ZONE (turn messages, appended)     │
│  • Plan mode marker                          │
│  • Mid-session memory updates                │
│  • Background job completions                │
│  • Skill bodies (loaded on demand)           │
│  • User input + tool results                 │
│  ═══════════════════════════════════════════ │
│  → Rides the turn tail                       │
│  → Folds into prefix on next session boot    │
└─────────────────────────────────────────────┘
```

This is not a feature. It's a contract. Every component must honor it.

---

## What Hermes Can Learn

Hermes already has cache awareness — `_cached_system_prompt` persistence, skill slash commands that inject as user messages, Anthropic prompt cache support. These are good. But they're **features**, not architecture.

Here's where the gap shows:

| Scenario | Hermes (current) | Reasonix (cache-first) |
|----------|-----------------|----------------------|
| **Mid-session memory write** | May modify system prompt (depending on provider/impl) | Always rides turn tail via `<memory-update>` |
| **Plan mode toggle** | May modify system prompt or tools | Byte-identical system prompt + tools; marker in user message |
| **Model switch mid-session** | Rebuilds system prompt (busts cache) | Architecturally impossible — separate sessions |
| **Skill install mid-session** | Changes available skills list | Index-only in prefix; new skills ride turn tail |
| **Reasoning re-upload** | Not specifically optimized | Explicitly stripped in buildRequest |

The upgrade path for Hermes isn't "add more cache features." It's:

1. **Freeze the system prompt at turn-0.** After boot, never mutate it.
2. **Move all mid-session state changes to turn tail injection.** Memory writes, plan mode, model hints — all ride `Compose()`.
3. **Adopt base-first memory protocol.** Even when memory changes, the base stays byte-identical.

---

## Why This Matters Beyond DeepSeek

DeepSeek's pricing makes this architecture economically rational today:

- Cache Hit: ¥0.14 / 1M tokens
- Cache Miss (Input): ¥0.28 / 1M tokens
- That's a **50% discount** on cached tokens

But the principle is model-agnostic. Anthropic has prompt caching (1-hour TTL). OpenAI has automatic caching. Google has context caching. Every major provider has some form of prefix-cache discount — and the discount only applies when the prefix is byte-stable.

A cache-first agent architecture doesn't just save money on DeepSeek. It saves money on **every provider that offers prefix caching**. And as context windows grow and tokens get cheaper in absolute terms but more plentiful in volume, the proportion of tokens that *can* be cached grows faster than the cost per token drops.

The economic argument for cache-first architecture gets stronger over time, not weaker.

---

## The Bigger Picture: Architecture as Frugality

I-04 taught us to protect constraints from compression by physical separation. I-05 taught us to structure documents so KV Cache stays warm across reads. I-13 completes the trilogy: **make the entire agent architecture cache-stable, and every component must justify any departure from that constraint.**

The unifying thread across these three is a philosophy: **tokens are not free, and the best way to save them is not to send them in the first place.** Compression reduces tokens. Cache-first architecture prevents them from ever needing to be sent.

Reasonix is currently the purest expression of this philosophy in open-source agent code. Not because it's "better" than Hermes — Hermes has Gateway, Cron, multi-provider Memory, and an ecosystem Reasonix can't touch. But because Reasonix asked a harder question: "what if cache stability were not a feature, but the law?"

And that's the innovation worth bringing back.

---

*Written after reading every relevant line of Reasonix's Go source. Analysis backed by: `boot.go`, `input.go`, `memory.go`, `agent.go`, `coordinator.go`, `openai.go`, `provider.go`, `index.go`, `controller.go`, `store.go`, `SPEC.md`, `cachehit_e2e_test.go`.*
