# KV Cache-Driven Review Depth Switching

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, “validated” does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-07
> **LLM + Harness = Agent** · Part 7
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [06 OKR-Enhanced PlanStep + Cascading Correction Engine](06-okr-planstep-cascade.md)
> Next: [08 Scope Creep Detection and Adaptive Refusal](08-scope-creep.md)

---

> **Abstract**: Momus, Hermes's review agent, performs well in short conversations — "80% clear → approve" is a reasonable, high-efficiency heuristic. But as the conversation grows and KV Cache occupancy climbs, Momus's review judgment degrades in lockstep with attention dilution. A review conducted at the "80% clear" standard in a 128K context may have an effective review quality that has already fallen to 40% — and Momus has no awareness that it's getting dumber. This article identifies a hidden assumption shared by all agent frameworks — that review depth is a fixed threshold — and argues that this assumption constitutes systemic self-deception under long contexts. We propose a two-dimensional dynamic function for review depth, f(KV Cache occupancy, Plan complexity), defining a depth gradient across four review tiers (<8K / 8-32K / 32-128K / >128K), enabling review depth to switch automatically based on context state. This is a specialized deepening of the review dimension within the Attention Budget Management framework (article 03).

---

## 1. Problem Definition

### 1.1 Momus's Self-Deception Trap

Momus is Hermes's review agent, responsible for checking whether outputs meet requirements during task execution. Its core working pattern:

1. Read the current Plan Step's `key` (verifiable completion criteria)
2. Read the agent's output (code, documentation, configuration)
3. Judge whether it is "clear enough" → pass or reject

In short conversations (< 10 turns), this pattern works well. Momus's standard review depth — "check each Plan Step against requirements item by item" — is effective when attention is abundant.

The problem emerges in long conversations.

When the main agent has executed 30+ turns and the context has ballooned to 64K+ tokens, Momus also receives that inflated context as its review input. When Momus reads the output, its attention has already been diluted by tens of thousands of tokens of preceding history — like a fatigued reviewer examining their 47th document after 8 straight hours of work.

Yet Momus still uses the same review standard: "80% clear → approve."

The self-deception chain works as follows:

1. Momus **believes** it is reviewing at an 80% clarity standard
2. But in reality, due to attention dilution, its judgment of "clarity" itself is no longer accurate — it may miss critical inconsistencies
3. It still issues "approve" — because it has no awareness that its judgment has degraded
4. The user receives a "review passed" result — but the review quality has significantly degraded

This is "fixed-depth self-deception" — the review standard hasn't changed, but the capability of the agent executing the review has, and the review framework has no awareness of this change.

### 1.2 Root Cause: Review Depth Is a Hidden Static Parameter

In today's agent ecosystem, review depth is not an explicit, configurable parameter. It is implicitly embedded in the System Prompt:

```
"Carefully check whether the output meets requirements"
"Verify each Plan Step key item by item"
"Ensure code style consistency"
```

These instructions describe the goal of the review behavior, not the "depth budget" of the review. They assume that the review agent has equivalent judgment under any context — as if a reviewer with diminished attention can match the thoroughness of item-by-item checking performed when fully alert.

But the System Prompt doesn't know the KV Cache is full. The System Prompt doesn't know the Plan has 15 steps. The System Prompt doesn't know the current context contains 3 abandoned conversation branches and 2 execution logs of completed subtasks. The System Prompt only repeats the same sentence: "Check carefully."

This is not a Prompt Engineering issue — it is a **missing decision framework** for review depth. Review depth should not be a static instruction; it should be a function of context state.

### 1.3 Formalization

Let review agent M perform a review under context S(t), with review depth d. d determines the granularity of review: how many dimensions to check, how many constraints to verify, the strictness of boundary conditions.

Fixed review depth model:

```
d = d₀ (constant)
Review quality Q = g(M's capability, d₀, S(t))
```

As S(t) grows, M's effective attention α_M(t) ∝ 1/|S(t)|, and M's actual judgment degrades. But d₀ remains unchanged — M executes an unchanged workload with degraded judgment. Result:

```
When |S(t)| ≫ initial |S₀|:
  g(M's capability, d₀, S(t)) ≪ g(M's capability, d₀, S₀)
  But d remains unchanged → review output still labeled "pass" → user unaware
```

Dynamic review depth model:

```
d = f(K, P), where:
  K = KV Cache occupancy rate = |S(t)| / Context Window
  P = Plan complexity = Number of Plan Steps + dependency density between steps
Review quality Q = g(M's capability, f(K, P), S(t))
```

When K rises, f(K, P) automatically increases review depth, using "stricter review standards" to compensate for "lower judgment baseline." This is not the model getting smarter — it is using higher review requirements to offset lower review capability, maintaining stable net review quality.

---

## 2. Existing Solutions and Limitations

### 2.1 The Universality of Fixed Review Depth

| Solution | Review Mechanism | How Review Depth Is Defined | Changes with Context? |
|------|---------|----------------|:---:|
| **Claude Code** | Executes `code_review` tool after generation | System Prompt instruction: "Review the code for correctness, bugs, and style" | No — fixed instruction, context-length unaware |
| **CodeWhale** | `plan_review` tool | Fixed checklist: logical correctness, boundary conditions, error handling | No — checklist unchanged whether context is 8K or 128K |
| **Devin** | Built-in review pipeline (closed source) | Undisclosed, but behavior suggests fixed standard | No — review behavior consistent across short and long tasks |
| **Hermes (current)** | Momus review agent | Item-by-item comparison against Plan keys | No — review depth statically defined by Momus's System Prompt |
| **LangGraph Supervisor** | Supervisor agent reviews worker agent output | Fixed review dimensions (format, content, constraint satisfaction) | No — review dimension list determined at initialization |

**Common defect**: All solutions treat review depth as a **static value**. It is either a piece of natural language in the System Prompt or a fixed checklist. There is no relationship between review depth and the context state at the time of review — a review in 128K context and a review in 8K context are, from the review framework's perspective, the same thing.

### 2.2 Why "Let the Model Judge Review Depth Itself" Doesn't Work

A natural counterargument: "Just let the LLM decide when it needs stricter review. Add one line to the Prompt: `if the context is very long, review more carefully.`"

This doesn't work. The reason is the same as the root cause of attention dilution:

The LLM's judgment of "whether the context is long" itself requires attention — and that attention has also been diluted by the long context. A model whose attention is already diluted, when told in the Prompt to "be more careful," typically responds by generating more text in the output (looking careful), but without any improvement in judgment accuracy.

In other words: **Asking an attention-diluted model to recognize that its attention is diluted is itself a paradox.** It's like asking a drunk person to judge whether they can still drive — their judgment has already been impaired by alcohol, and they cannot accurately assess their own sobriety.

The decision to switch review depth must happen at the Harness layer — not judged by the model, but calculated by the Harness based on hard metrics of the KV Cache (actual token occupancy, Plan step count, and dependency density).

### 2.3 Three Failure Modes of Fixed Depth

**Mode 1: Over-reviewing in short contexts.** Context is only 8K, Plan has only 2 steps. The agent's attention is abundant, judgment at its peak. Yet it still performs a full review of "item-by-item verification + boundary conditions + rollback strategy" — a waste of attention budget, using ten units of attention for a judgment that needs three.

**Mode 2: Under-reviewing in long contexts.** Context is 128K, Plan has 12 steps, dense dependency graph. The agent's attention has been diluted to baseline levels. Yet it executes the relaxed review of "80% clear → approve" — the actual review quality may not even be able to judge "40% clarity" — because it never saw the 40% that was unclear.

**Mode 3: Unauditable review quality.** Fixed review depth causes review quality to decay monotonically with context length, but the decay curve is completely invisible to the user. The user sees a binary result of "pass/fail," without knowing whether the review quality behind that pass was 90% or 40%. The review result loses auditability.

---

## 3. Solution Design

### 3.1 Core Function: Review Depth = f(KV Cache Occupancy, Plan Complexity)

Review depth is not a constant — it is a two-dimensional function:

$$\text{ReviewDepth} = f(K, P)$$

Where:

- **K = KV Cache occupancy rate**: actual token count in current context / model Context Window upper limit. Directly reflects attention dilution. K ∈ [0, 1]; higher K → lower attention → stricter review standards needed to compensate.
- **P = Plan complexity**: the number of steps n in the current Plan and the density ρ of inter-step dependencies. P = n · (1 + ρ), where ρ = |E| / |V| (edges/nodes in the dependency graph). Higher P → higher error probability → stricter review standards needed.

**Why these two dimensions?**

- K reflects **reviewer capability decay** — after attention is diluted, the same review instruction yields lower effective quality.
- P reflects **review target difficulty** — more complex Plans with more inter-step interactions are more error-prone.

The two dimensions are independent but synergistic: when the Plan is simple (low P) and context is short (low K), review can be relaxed — because the reviewer is in good condition and error probability is low. When the Plan is complex (high P) and context is long (high K), review must be strictest — because the reviewer is in poor condition and error probability is high.

**Why not more dimensions?**

A more complex function (adding task type, user reputation, historical review pass rate, etc.) could theoretically be more precise, but at higher cost — every review decision would require computation and lookup. The two-dimensional f(K, P) is the sweet spot of "good enough" and "simple enough": both K and P are metrics the Harness already holds and updates in real time, requiring no additional computation.

### 3.2 Review Depth Gradient Table

Based on K and P, define four review tiers, each corresponding to a different review depth and specific review behavior:

| K (KV Cache Occupancy) | P (Plan Complexity) | Review Tier | Review Depth | Specific Behavior |
|:---|:---|------|------|------|
| < 8K tokens<br>(K < 0.06, 128K window) | Any | **Relaxed Review** | Shallow | Verify whether output Key is satisfied. No inter-Step consistency check. No boundary condition check. "80% clarity → approve" |
| 8K - 32K<br>(K ∈ [0.06, 0.25]) | P ≤ 3 | **Standard Review** | Medium | Item-by-item Key verification + check output consistency between current Step and previous Step + critical boundary conditions (empty input, insufficient permissions, timeout) |
| 8K - 32K<br>(K ∈ [0.06, 0.25]) | P > 3 | **Strict Review** | Deep | Item-by-item Key verification + check output consistency between current Step and all dependency Steps + full boundary conditions + error recovery paths |
| 32K - 128K<br>(K ∈ [0.25, 1.0]) | P ≤ 3 | **Strict Review** | Deep | Same as Strict Review + flag "context inflated, compression recommended" |
| 32K - 128K<br>(K ∈ [0.25, 1.0]) | P > 3 | **Strictest Review** | Deepest | Same as Strict Review + every Step must have requirement mapping + full boundary enumeration + rollback strategy + mandatory output of "review confidence" score (0-1) |
| > 128K<br>(near window limit) | Any | **Reject Review** | — | No review. Force-trigger context compression, review after compression. Because when K approaches 1, review quality is unreliable — the review itself has lost meaning |

**Four Principles of Gradient Design**:

**Principle 1: K drives review depth upward, not downward.** Intuitively, "long context → simplify review → fast pass" seems reasonable — because a full review consumes too many tokens. But this is the wrong direction. A long context means the agent has already produced substantial output in preceding steps — if those earlier outputs contain errors, subsequent steps will build upon errors. At this point, review is not something that "can be relaxed" — it's something that "must be stricter." Tokens should be spent where they matter most, and review under long context is exactly where they matter most.

**Principle 2: P amplifies K's effect.** Under the same K, Plan complexity P determines further stratification of review depth. A simple 3-step Plan at 64K context has manageable review risk; a 15-step Plan with dense dependencies at the same 64K context — any missed step can propagate across the entire dependency graph.

**Principle 3: Reject review beyond 128K.** This is not a tunable parameter — it is a hard boundary. When the context approaches the window limit, the review agent's effective attention has fallen to an unacceptable baseline. At this point, the review result — whether "pass" or "reject" — is unreliable. The correct behavior is not "lower review depth and make do," but "first compress context, free up attention budget, then review."

**Principle 4: Review confidence is a requirement.** In the Strictest Review tier, Momus must output a 0-1 confidence score indicating its level of confidence in this review judgment. This is not for the user to read — it is a feedback signal: if Momus repeatedly outputs high confidence (>0.9) in extremely high-K scenarios, it means Momus is unaware of its own attention deficit — a review system failure signal that requires investigation.

### 3.3 Implementation Path

Review depth switching is implemented at the Harness layer through three components:

**Component 1: Context State Monitor**

```typescript
interface ContextState {
  kvCacheTokens: number;       // Current actual KV Cache token count
  contextWindow: number;       // Model context window upper limit (e.g., 128K)
  planComplexity: number;      // Plan step count × (1 + dependency density)
  reviewDepth: ReviewDepth;    // Currently recommended review depth
}

// Called before each review
function getReviewDepth(state: ContextState): ReviewDepth {
  const K = state.kvCacheTokens / state.contextWindow;
  const P = state.planComplexity;
  
  if (state.kvCacheTokens > CONTEXT_WINDOW_HARD_LIMIT) return "reject";
  if (K < 0.06) return "shallow";
  if (K < 0.25 && P <= 3) return "medium";
  if (K < 0.25 && P > 3) return "deep";
  if (K >= 0.25 && P <= 3) return "deep";
  return "deepest";
}
```

**Component 2: Review Depth → System Prompt Compilation (Prompt Compiler)**

Different review depths map to different review System Prompts. Not simply "add a line about being stricter to the Prompt" — it's a complete Prompt replacement:

- `shallow` → Momus's lightest Prompt (Key verification only, ~200 tokens)
- `medium` → Momus's standard Prompt (Key + single-step consistency + critical boundaries, ~600 tokens)
- `deep` → Momus's strict Prompt (Key + full dependency consistency + full boundaries, ~1200 tokens)
- `deepest` → Momus's strictest Prompt (strict Prompt + requirement mapping + rollback strategy + confidence, ~2000 tokens)
- `reject` → Do not invoke Momus, trigger context compression flow

Key design decision: **The higher the review depth, the longer Momus's System Prompt.** This seems contradictory — increasing System Prompt length in a context where attention is already diluted? But the review Prompt is not "more content" — it is "more specific check items." A 2000-token review Prompt contains a structured checklist that Momus can execute item by item — this yields better performance from an attention-impaired model than a vague "check carefully" instruction (200 tokens). Structured checklists are the optimal review format under attention dilution.

**Component 3: Review Depth Audit Trail**

Each review records the following data:

```typescript
interface ReviewAuditEntry {
  timestamp: number;
  reviewDepth: ReviewDepth;     // Review depth used
  K: number;                     // KV Cache occupancy rate at review time
  P: number;                     // Plan complexity at review time
  result: "pass" | "reject";     // Review result
  confidence?: number;           // Confidence score (deepest mode only)
  tokensUsed: number;            // Tokens consumed by this review
}
```

The role of the audit log: make the decay curve of review quality **visible**. As K grows from 0.05 to 0.8, the trend of review pass rates and confidence scores can be tracked in the audit log — the user no longer faces a "pass/fail" black box.

---

## 4. Analysis

### 4.1 Why Dynamic Switching Solves the Three Failure Modes of Fixed Depth

**Corresponding to Mode 1 (over-reviewing in short contexts)**: When K < 8K, enter Relaxed Review. No inter-Step consistency or boundary condition checks — because in a short context with abundant attention, the probability of the agent making such errors on its own is naturally low. Tokens saved by Relaxed Review (~300-800 tokens per review saved) are invested into actual task execution.

**Corresponding to Mode 2 (under-reviewing in long contexts)**: When K ≥ 32K, enter Strict/Strictest Review. Use structured multi-dimensional checklists to offset attention dilution. The review itself consumes more tokens (from ~600 to ~2000 tokens), but this is necessary — because the context has inflated to the point where "not reviewing strictly risks missing errors."

**Corresponding to Mode 3 (unauditable review quality)**: The audit log records K, P, depth, result, and confidence for each review. Users can post-hoc analyze which context states show anomalously high pass rates (→ potentially overly lenient review) and which show anomalously low confidence (→ may need to trigger compression).

### 4.2 Why "Dynamic Review Depth" Is Not "Just More Reviewing"

An easy point of confusion: dynamic review depth sounds like "doing a more comprehensive review in long contexts" — isn't that just consuming more tokens in long contexts?

Yes. But the key difference is **when those tokens are consumed**:

- Fixed review depth: consumes **the same review tokens** in short and long contexts (~600 tokens/review), but the **effective token output** in long contexts is lower (due to attention dilution)
- Dynamic review depth: consumes **fewer** review tokens in short contexts (~200 tokens/review), **more** review tokens in long contexts (~2000 tokens/review), but the **per-token effective output** in long contexts is guaranteed by the structured checklist

Total token consumption under dynamic review is not necessarily lower than fixed review — it may be higher. But its **effective review quality** is stable (or at least does not decay monotonically with K), whereas fixed-depth review quality decays monotonically with K. Token efficiency is not an "absolute value" — it is "token consumption per unit of review quality."

### 4.3 Boundary Conditions

The following scenarios are **not covered** by this solution:

- **KV Cache token count not precisely obtainable**: Some model APIs (e.g., GPT-4's Chat Completions API) do not directly expose KV Cache token count, only Prompt tokens + Completion tokens. In this case, `prompt_tokens` must be used as an approximate proxy for K — sufficiently accurate in most cases, but may underestimate actual K in scenarios with prefix caching.
- **Plan complexity P accuracy issues**: P calculation depends on Plan dependency graph quality. If the Plan's `dependency_ids` annotations are incomplete (as discussed in article 06), P will be underestimated → review depth insufficient. However, the consequence of underestimating P is "lenient review" rather than "overly strict review" — a risk worth noting in safety-sensitive scenarios.
- **Frequent switching when K hovers near a threshold**: If KV Cache token count fluctuates near 8K (±500 tokens), review depth may repeatedly switch between shallow and medium, causing inconsistent review behavior from Momus. Solution: introduce threshold hysteresis — the threshold for switching from shallow to medium is K > 0.0625 (8K tokens), but the threshold for switching back from medium to shallow is K < 0.05 (6.4K tokens), avoiding boundary oscillation.
- **Different models have different Context Windows**: K is a relative ratio. But is the actual attention dilution the same for K = 0.25 whether the window is 32K/128K or 32K/1M? For models with 1M windows, 32K may still be within the "abundant attention" zone. This requires calibrating K thresholds per model window size rather than using uniform absolute token thresholds.

---

## 5. Verification Path

### 5.1 Verified

- **Problem existence (indirect verification)**: Article 03's attention budget experiments have verified that the same DeepSeek V4 Pro model's constraint retention rate drops from ~100% to ~40% by turn 15. The review agent's attention decay follows the same physical laws — Momus's review judgment degradation in long contexts and the main agent's task execution capability degradation share the same root cause.
- **Review gradient feasibility (theoretical basis)**: The Attention Budget Management framework (article 03 §3.2) already proposed the two-dimensional f(K, P) function concept and an initial gradient table. This article builds on that by refining the review dimension gradient table into four tiers with specific review behavior definitions.
- **Harness-obtainable metrics**: Hermes's KV Cache monitoring already produces `kv_cache_tokens` and `context_window` metrics; OKR PlanStep (article 06) already produces `dependency_ids` and step counts — the data needed for P calculation is already available.

### 5.2 To Be Verified

- **Empirical calibration of K thresholds**: Current thresholds (<8K / 8-32K / 32-128K / >128K) are heuristically set based on a 128K Context Window. Empirical verification is needed for: (a) Momus's actual review accuracy variation curve at each threshold; (b) whether thresholds need adjustment for different task types (refactoring/new-build/debugging).
- **Impact of review depth switching on net review quality**: The core hypothesis is "deeper review Prompts can compensate for attention dilution." Controlled experiment needed: fixed review depth vs. dynamic review depth, measuring review recall (missed errors) and precision (false positives) across K from 0.05 to 0.8.
- **Economic analysis of review token consumption**: Dynamic review consumes more review tokens at high K. Measurement needed for: (a) total task token consumption under dynamic review vs. fixed review; (b) token consumption per unit of review quality comparison.
- **Confidence score calibration**: Does the confidence score (0-1) Momus outputs in Strictest Review tier correlate with its actual review accuracy? If confidence and accuracy are decoupled (high confidence + low accuracy), Momus exhibits an "overconfidence" bias — requiring further calibration or introduction of a second review agent.
- **Cross-model generalization**: Does DeepSeek V4 Pro's attention dilution curve apply to Qwen, Llama, Claude, and other models? Different Transformer architectures may have different attention distributions at the same K → thresholds require model-specific calibration.

---

## 6. Relationship to Hermes

### 6.1 Why Momus Needs This Solution

Momus's current implementation is an "honest but blind" reviewer — it diligently executes audits but has never asked itself: "Is my judgment still adequate right now?"

Dynamic review depth switching transforms Momus in two steps:

**Step 1: Embed Context Monitor.** Before Momus is invoked for review, the Harness first queries Context Monitor → obtains current (K, P) → computes review depth → compiles the corresponding review Prompt → passes it to Momus. Momus doesn't need to know that review depth switching exists — it just receives a more specific or more relaxed Prompt.

**Step 2: Audit feedback loop.** Momus's review results (pass/reject + confidence) are written to the audit log. The Harness periodically analyzes audit data, detecting anomalous patterns (e.g., abnormally high pass rate at high K) → triggering automatic tuning of review depth thresholds or notifying the user.

### 6.2 Division of Labor with Article 03

Article 03 (Attention Budget Management) defines four attention management strategies, of which the review dimension (§3.2) is one of the four. This article is a **specialized deepening** of the review dimension:

- What article 03 does: proposes the f(K, P) concept + initial 5-row gradient table
- What this article does: expands the gradient table into a 6-row complete review behavior definition + review depth → Prompt compilation mechanism + audit logging + failure mode analysis + boundary conditions (hysteresis, cross-model calibration)

Their relationship: article 03 is the framework; this article is the detailed design document for the review module within that framework.

### 6.3 Synergy with Article 06

Article 06 (OKR PlanStep + Cascading Correction Engine) defines the computational basis for P — `dependency_ids` and `association_strength` transform Plan complexity P from a simple step count n into n · (1 + ρ), where ρ accounts for dependency graph structure.

Their synergy:

- Article 06's dependency graph → Article 07's P dimension
- Article 07's review depth → Article 06's cascading correction review phase (when a node is marked `pending_review`, Momus's review depth should be determined by f(K, P))
- When the cascading correction engine marks 5 `pending_review` nodes, each node's review depth is not uniform — but independently computed based on the (K, P) at the time of each review

---

## Conclusion

Momus's "80% clear → approve" is an efficient heuristic in short conversations and systemic self-deception in long ones. Not because Momus isn't trying — but because review depth is static while the reviewer's judgment is dynamically decaying.

Review Depth = f(KV Cache Occupancy, Plan Complexity) upgrades review from a "fixed standard" to a "state-aware system." When context inflates and attention dilutes, review doesn't relax — it goes deeper. Structured multi-dimensional checklists offset attention decay; audit logs transform review quality from a black box into a visible curve.

This is not about making Momus smarter — it's about letting Momus know when it isn't smart enough, and compensating with a stronger review framework.

---

*Previous: [06 OKR-Enhanced PlanStep + Cascading Correction Engine](06-okr-planstep-cascade.md) — Plan upgraded from Checklist to Dependency Graph, one change triggers automatic cascading correction*
*Next: [08 Scope Creep Detection and Adaptive Refusal](08-scope-creep.md) — Agents won't refuse scope creep, but the Harness should learn to say "no"*
