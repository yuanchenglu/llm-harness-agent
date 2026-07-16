# Byte-Stable Prefix as an Architectural Constraint: It's Not Just About Caching the System Prompt — Make the Entire Agent Cache-First

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source code, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-13
> **LLM + Harness = Agent** · Part 13
> Series: [LLM + Harness = Agent](../../README.md)
> Related: [I-04 KV Cache Prefix Hard-Constraint Injection](04-kv-cache-prefix.md) · [I-05 Document KV Cache Optimization](05-document-kv-cache.md)

---

## Problem: Cache Awareness Should Be Architecture, Not a Patch

I-04 established a principle: "Constraints survive not because the compression algorithm is clever, but because they never enter the compression zone." That is physical isolation — putting critical instructions into the KV Cache prefix zone where compression cannot touch them.

But a deeper question lurks: **should "cache awareness" be a feature you bolt on later, or a constraint that dictates the entire Agent architecture?**

Look at the industry today. Every mainstream Agent platform has some form of cache optimization:

- **Hermes** persists `_cached_system_prompt` to Session DB and restores it the next turn
- **Claude Code** uses Anthropic's 1-hour prompt cache with system prompt segmentation
- **CodeWhale** places `<user_memory>` "above the volatile-content boundary" in prompt assembly

These are all **features**. A function call, a conditional. The system prompt is cached when convenient, rebuilt when needed. Cache awareness is a leaf on the architecture tree.

But there is another way.

What if cache stability is not a feature but a **root constraint** that every architectural decision must obey?

What if every component — Memory, Skills, Plan Mode, Model Switching, Context Compaction — must answer one question before doing anything:

> **"Does this decision preserve byte-stability of the system prompt prefix?"**

This is the architecture I discovered in **DeepSeek-Reasonix** (esengine/DeepSeek-Reasonix). This is not marketing copy. It is present at every layer of the source.

---

## Architecture: Cache-First as a Root Constraint

What a "cache-first architecture" actually looks like in code. Every item below was verified against the Go source under `internal/`.

### Boot Sequence: Assembled Once, Frozen Forever

```go
// boot.go L100-124 — system prompt assembled once at boot
sysPrompt = outputstyle.Apply(sysPrompt, st)     // 1. Output style
sysPrompt += "\n\n" + config.LanguagePolicy       // 2. Static language policy
sysPrompt = memory.Compose(sysPrompt, mem)         // 3. Memory (base first)
sysPrompt = skill.ApplyIndex(sysPrompt, skills)    // 4. Skills index (names only, no body)
```

After this, `sysPrompt` is a frozen byte sequence. It never changes for the entire session. User switches Plan Mode? Unchanged. Memory is written? Unchanged. Background job completes? Unchanged.

Any change the model must perceive goes through the **turn tail** — injected into the user message, never into the system prefix:

```go
// input.go L18-52 — Compose() injects transient context into the user message head
func (c *Controller) Compose(text string) string {
    if plan { text = PlanModeMarker + "\n\n" + text }       // Plan mode → user message
    if len(notes) > 0 { text = "<memory-update>..." + text }  // Mid-session memory → user message
    if c.jobs != nil { text = "<background-jobs>..." + text }  // BG completion → user message
    return text
}
```

This is architectural inversion. In most Agents, you modify the system prompt directly. In a cache-first agent, you treat it as a controlled change, not an arbitrary mutation. The system prompt is frozen by default; security updates, tool changes, or bug fixes still allow explicit rebuild.

---

### How This Constraint Shapes Six Subsystems

#### 1. Memory: Base-First Protocol + Mid-Session Injection

```go
// memory.go L148-152
// Base stays first (it is the most stable text, so
// it remains a valid cache prefix even when memory changes between sessions)
```

Two design decisions:

- **Base always stays first.** Even when Memory changes between sessions, the base prompt is unchanged → DeepSeek's prefix cache still hits the base portion
- **Mid-session Memory writes never touch the prefix.** When the `remember` tool saves a fact, it is written to disk immediately, but the model perceives it via **a `<memory-update>` block in the next user message**, not by a system prompt mutation. It naturally absorbs into the prefix at the next session boot.

This is not "append to system prompt" — it is a temporal protocol: session N-1 writes → session N's boot absorbs it into the immutable prefix.

#### 2. Skills: Index in Prefix, Body On-Demand

```go
// index.go L9 — package's declarative contract
// cache-stable system-prompt prefix; bodies never enter the prefix.
```

Only a skill's **name and one-line description** enter the system prefix. Each skill body is loaded on demand via the `run_skill` tool or `/name`. Once a body enters the prefix — you install a new skill, edit an existing one — the cache shatters.

#### 3. Plan Mode: Zero-Trace Toggle

```go
// agent.go L127-130
// planMode, when true, refuses any tool call whose ReadOnly() is false.
// The system prompt and tool list never change with the toggle
```

Plan mode toggles one boolean in the Agent. Behavior changes — writers are rejected, the model receives a "blocked" result. But the system prompt and tool schemas are byte-identical. Cache cost of the toggle: **zero**.

#### 4. Dual-Model Collaboration: Separate Sessions or No Collaboration

```go
// coordinator.go L25-27
// Coordinator runs two models in separate sessions to keep each one's
// prompt prefix cache-stable. The sessions never mix.
```

The obvious approach: have the executor call the planner mid-conversation — switch models for one turn, get a plan, switch back. Most implementations do this.

Reasonix does the opposite. Planner and executor each have **independent Sessions and independent system prompts**. They never share messages. The SPEC states explicitly:

> "switching models inside one shared conversation would break the prefix and tank cache hits, so we don't."

When "cache stability" is the root constraint, you don't fix the model-switching problem — you make model switching architecturally impossible.

#### 5. Reasoning Content: Don't Pay Twice for Thinking

```go
// openai.go L171-184
// reasoning_content is deliberately NOT sent back: DeepSeek accepts it but
// counts it as ordinary prompt input (~500 extra tokens per turn)
```

The send-back policy for `reasoning_content` depends on the specific endpoint and thinking/tool-call protocol. Some implementations choose not to send it back to reduce input; other paths replay it; this must be adjudicated by protocol and usage experiments.

Reasonix explicitly strips it in `buildRequest()`. Session-locally retained for display/archive, but never sent to the API again.

#### 6. Context Compaction: The Primary Explicit Cache Reset Point

```
SPEC.md L177-197
- Compact once when prompt_tokens reaches compactRatio (0.8) × context_window
- Session becomes: system + summary + recentKeep (default 8) complete messages
- This is the primary explicit history rewrite point in the design; config, security policy, and tool changes may still trigger rebuilds
- Between two compactions, the session grows by append-only
```

Compaction is not an ongoing background process. It triggers exactly once. After that the prefix is reset — a deliberate cache-reset point. Default: 1M token window × 0.8 = **800K prompt tokens** before the first compaction.

---

### 7. DeepSeek V4 Encoding Layer: Model-Native Prefix Stability

The six subsystems above establish the cache-first architecture from the **Agent framework layer** (Reasonix Go source). But there is a deeper question: **is this principle an invention of Agent engineering, or an inevitability of Transformer attention physics?**

The answer lies in DeepSeek V4's official model encoding layer. In `encoding/encoding_dsv4.py` (identical across Flash and Pro), there is a function that looks like a detail — `_drop_thinking_messages` (L575-599) — and what it does is logically isomorphic to Reasonix's cache-first architecture, except it operates at the **model encoding layer** rather than the Agent framework layer.

#### Core Mechanism: Role Filtering in `_drop_thinking_messages`

```python
# encoding_dsv4.py L510 — drop_thinking defaults to True
def encode_messages(
    messages: List[Dict[str, Any]],
    thinking_mode: str,
    context: Optional[List[Dict[str, Any]]] = None,
    drop_thinking: bool = True,  # Drop old turns' reasoning by default
    ...
)
```

`encode_messages`'s default behavior is: **drop `reasoning_content` from all assistant messages before `last_user_idx`**. But crucially, it does **not** simply delete everything wholesale — it has a precise role-filtering rule:

```python
# encoding_dsv4.py L587
keep_roles = {"user", "system", "tool", "latest_reminder", "direct_search_results"}
```

These roles are **always kept**. They form the skeleton of the conversation prefix — no matter how long the dialogue, no matter how large the thinking block, messages with these roles are never touched byte-wise. Looking at the concrete logic:

```python
# encoding_dsv4.py L591-597
if role in keep_roles or idx >= last_user_idx:
    result.append(msg)              # Stable roles + latest turns → fully kept
elif role == "assistant":
    msg = copy.copy(msg)
    msg.pop("reasoning_content", None)  # Old-turn assistant → strip thinking only
    result.append(msg)                  # content and tool_calls preserved
# developer and other roles → entire message dropped (they are transient debug content)
```

#### Isomorphic Correspondence with Reasonix Cache-First

This table reveals that both layers implement the same pattern:

| Dimension | Reasonix (Agent Framework Layer) | V4 encoding_dsv4.py (Model Encoding Layer) |
|------|--------------------------|-----------------------------------|
| **Stable layer (always kept)** | System prompt (frozen at boot); Base memory (fixed position); Skills index (name+description) | Messages with `system`, `user`, `tool`, `latest_reminder` roles |
| **Semi-stable layer (content kept, payload stripped)** | Mid-session memory written to disk but never touching prefix; Skill bodies not entering prefix | Old-turn `assistant` messages: `content` and `tool_calls` preserved, `reasoning_content` stripped |
| **Transient layer (dropped)** | Reasoning content not sent back to API (`openai.go` L171-184) | `developer` role messages dropped entirely; old-turn `reasoning_content` not encoded |
| **Functional correctness first** | SPEC dictates that switching models would break the prefix — prefer sacrificing flexibility over breaking the prefix | L548-551: when `tools` present, `effective_drop_thinking = False` — tool-call chains need full reasoning context |

The most critical correspondence is row four: **the ultimate purpose of prefix stability is to serve functional correctness**. Reasonix says "switching models breaks the prefix, so we don't"; V4 says "when there is a tool-call chain, full reasoning context is needed, so don't drop thinking". Neither caches for the sake of caching — cache is the means, correctness is the end.

#### Why This Matters: Cross-Layer Corroboration

I-13's thesis arose from practical observation in Agent engineering: keeping the system prompt byte-stable → KV Cache hits → lower costs and no inference-quality degradation. That looks like an "Agent framework design choice."

But the existence of V4's `_drop_thinking_messages` shows: **the model team does the same thing at the encoding layer, based on the same physical understanding.** The `system`, `user`, `tool` roles are hardcoded as "never dropped" — not because of a vague design intuition that these roles are "important," but because:

1. **Transformer prefix cache only works on byte prefixes.** Any byte change in the prefix (insertion, deletion, modification) invalidates all cache after that position.
2. **`system`/`user`/`tool` messages form the structural skeleton of a conversation.** They are the parts that "change least" — the user asks a new question, the previous turn's system instructions don't change, tool definitions don't change, earlier user messages don't change.
3. **`reasoning_content` is the largest and most volatile payload.** A thinking block can be 2000+ tokens, and its content is completely different every turn — it is the number-one killer of prefix cache.

V4's `_drop_thinking_messages` is written in Python; Reasonix's cache-first is written in Go. They face different callers (V4's encoding layer is invoked by the API server; Reasonix by the Agent client). But underneath is the same physical law: **under the Transformer autoregressive architecture, "stable prefix + transient tail" is the optimal information organization.**

This is not a "best practice" for Agent frameworks — it is a "physical law" of the attention mechanism.

---

## Core Principle: Separate "What Changes" from "What Doesn't"

Pull back, and all six design decisions are instances of one principle:

```
┌─────────────────────────────────────────────┐
│  Stable zone (system prefix, frozen at boot)   │
│  • Base prompt                                 │
│  • Output style / language policy              │
│  • Memory (tiered docs + auto-index)           │
│  • Skills index (names+descriptions only)      │
│  • Tool schemas                                │
│  ═══════════════════════════════════════════   │
│  → Never changes mid-session                   │
│  → DeepSeek prefix cache hits this zone 100%   │
├─────────────────────────────────────────────┤
│  Mutable zone (turn messages, appended)        │
│  • Plan mode marker                            │
│  • Mid-session memory updates                  │
│  • Background job completion notifications     │
│  • Skill bodies (loaded on demand)             │
│  • User input + tool results                   │
│  ═══════════════════════════════════════════   │
│  → Ride the turn tail                          │
│  → Absorbed into prefix at next session boot   │
└─────────────────────────────────────────────┘
```

This is not a feature. It is a contract. Every component must comply.

---

## What Hermes Can Learn From This

Hermes already has cache awareness — `_cached_system_prompt` persistence, skill slash-command injection as user messages, Anthropic prompt cache support. These are good. But they are **features**, not architecture.

The gap shows up here:

| Scenario | Hermes (current) | Reasonix (cache-first) |
|------|-------------|----------------------|
| **Mid-session memory write** | May modify system prompt (depends on provider) | Default goes via turn tail; critical security/constraint updates can explicitly rebuild |
| **Plan mode toggle** | May modify system prompt or tools | System prompt + tools byte-identical; marker in user message |
| **Mid-session model switch** | Rebuilds system prompt (shatters cache) | Architecturally impossible — independent sessions |
| **Mid-session skill install** | Changes available skills list | Index-only in prefix; new skills go via turn tail |
| **Reasoning send-back** | Not specifically optimized | Explicitly stripped in buildRequest |

The upgrade path for Hermes is not "add more caching features"; it is:

1. **Freeze the system prompt at turn-0.** After boot, never mutate.
2. **Move all mid-session state changes to turn-tail injection.** Memory writes, plan mode, model hints — all via `Compose()`.
3. **Adopt a base-first memory protocol.** Even as memory changes, the base stays byte-identical.

---

## Why This Transcends DeepSeek

DeepSeek's pricing makes this architecture economically reasonable today:

- Cache Hit: ¥0.14 / 1M tokens
- Cache Miss (Input): ¥0.28 / 1M tokens
- **Cached tokens at 50% off**

But the principle is model-agnostic. Anthropic has prompt caching (1-hour TTL). OpenAI has automatic caching. Google has context caching. Every mainstream provider has some form of prefix-cache discount — and that discount only applies when the prefix bytes are stable.

Cache-first Agent architecture doesn't just save money on DeepSeek. It saves money on **every provider that offers prefix caching**. And as context windows grow and absolute token prices fall but usage grows — the proportion of tokens that can be cached grows faster than per-token costs fall.

The economic case for cache-first architecture strengthens over time, not weakens.

---

## The Bigger Picture: Architecture as Frugality

I-04 taught us to protect constraints from compression through physical separation. I-05 taught us to structure documents so KV Cache stays warm across reads. I-13 completes the trilogy: **make the entire Agent architecture cache-stable, and every component must give a reason for any behavior that violates this constraint.**

Running through all three is a single philosophy: **tokens are not free, and the best way to save tokens is to never send them in the first place.** Compression reduces tokens. Cache-first architecture prevents them from needing to be sent.

Reasonix is currently the purest expression of this philosophy in open-source Agent code. Not because it is "better" — Hermes has Gateway, Cron, multi-provider Memory, and an ecosystem Reasonix cannot touch. But because Reasonix asked a harder question: "what if cache stability is not a feature, but the law?"

And that is the innovation worth bringing back. But the discovery of V4's `_drop_thinking_messages` adds a layer of meaning: cache-first is not Reasonix's "design choice" — it is the projection of Transformer physical law onto the Agent framework layer. V4's model encoding layer independently reached an isomorphic conclusion, which corroborates that "stable prefix first" is not a stylistic preference, it is a physical constraint.

---

## 5. Validation Path

### 5.1 Validated

| Evidence | Layer | Status | Validation Method |
|------|-----|------|----------|
| Reasonix cache-first architecture | Agent framework layer (Go) | **Source confirmed** | `boot.go` L100-124 (system prompt frozen); `input.go` L18-52 (transient context via turn tail); `memory.go` L148-152 (base-first protocol); `openai.go` L171-184 (reasoning stripped); `SPEC.md` L177-197 (compaction strategy) |
| V4 `_drop_thinking_messages` | Model encoding layer (Python) | **Source confirmed** | `encoding_dsv4.py` L575-599: `keep_roles = {"user", "system", "tool", "latest_reminder", "direct_search_results"}` unconditionally kept; old-turn `assistant` messages strip `reasoning_content`; `developer` role messages dropped entirely |
| V4 `tools` disables drop | Model encoding layer (Python) | **Source confirmed** | `encoding_dsv4.py` L548-551: `any(m.get("tools") for m in full_messages)` → `effective_drop_thinking = False` — functional correctness takes priority over cache optimization |
| I-04 Prefix-injection constraint retention | Agent framework layer | **Experiment** | Constraint retention > 95% after 15 turns (prefix zone physical isolation, compression cannot touch). See [I-04](04-kv-cache-prefix.md) §5.1 |

> **Core cross-layer corroboration finding**: Reasonix (Agent framework layer) and V4 `_drop_thinking_messages` (model encoding layer) arrived at isomorphic prefix-stability strategies in independent design spaces — stable roles kept forever, transient content stripped by turn. This is not coincidence; it is Transformer prefix-cache physics acting on both layers simultaneously.

### 5.2 To Be Validated

The following questions currently lack sufficient evidence and require independent experiments or additional source confirmation:

- **V4 drop_thinking attention dilution in extremely long dialogues** (priority: high). We have currently confirmed that `_drop_thinking_messages` **physically preserves** the byte sequences of `system`/`user`/`tool` roles. But physical preservation ≠ attention allocation. After 100+ turns, even with the system prompt bytes intact, the model's attention weight on prefix-distant content may be diluted by subsequent KV pairs. Test needed: continuously inject a key constraint (e.g. "never touch config files") across 100 turns, compare whether the model still obeys that constraint in the final turn under `drop_thinking=True` vs `drop_thinking=False`.

- **Combined effect of Harness-layer cache-first and V4 model-layer drop_thinking** (priority: high). When Reasonix's cache-first (Harness layer freezes sysPrompt + strips reasoning) and V4's `_drop_thinking_messages` (model encoding layer keeps stable roles + strips old-turn reasoning) are both enabled, do they synergize or conflict? For example: after the Harness layer strips reasoning, does the V4 encoding layer's `_drop_thinking_messages` still have reasoning to strip? Are the optimization effects additive or redundant?

- **Encoding-layer prefix protection mechanisms in other models** (priority: medium). Do the official encoding layers of mainstream models like Qwen, Llama, Claude have similar "role filtering" or "prefix protection" mechanisms? If so, what are their `keep_roles` sets? How do they compare to V4's set (`system`/`user`/`tool`/`latest_reminder`)? This could validate the hypothesis that "stable prefix is a universal Transformer law."

- **Prefix semantics of `latest_reminder` and `direct_search_results`** (priority: medium). V4 also lists `latest_reminder` and `direct_search_results` in `keep_roles`, but their lifecycle and stability across multi-turn dialogues differs from `system`/`user`/`tool`. Need to confirm: do these roles remain byte-stable across consecutive turns? If not, could listing them in keep_roles actually reduce prefix-cache hit rates?

- **Quantitative cost-benefit model for cache-first architecture** (priority: low). Qualitative conclusions exist (cache-hit tokens at 50% off), but a quantitative model is lacking. Need to measure: in a typical 50-turn Agent session, how much token cost does cache-first architecture save vs. a baseline where the system prompt is rebuilt every turn? What is the functional relationship between this savings and session length?

---

*This article is based on reading every relevant line of Reasonix Go source (`boot.go`, `input.go`, `memory.go`, `agent.go`, `coordinator.go`, `openai.go`, `provider.go`, `index.go`, `controller.go`, `store.go`, `SPEC.md`, `cachehit_e2e_test.go`) and DeepSeek V4's official encoding-layer source (`encoding/encoding_dsv4.py` L500-600, identical across Flash and Pro).*
