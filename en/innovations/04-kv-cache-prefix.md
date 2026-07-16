# KV Cache Hard-Constraint Prefix Injection: Constraints Survive Because They Never Enter the Compression Zone

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source code, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation Index**: I-04
> **LLM + Harness = Agent** · Part 4
> **Series**: [LLM + Harness = Agent](../../README.md)
> **Previous**: [03 Attention Budget Management](03-attention-budget.md)
> **Next**: [05 Document KV Cache Optimization Structure](05-document-kv-cache.md)

---

> **Abstract:** Long-task Agents must compress context to control window expansion, but compression algorithms evaluate all information with uniform weight — they don't know that "never touch config files" is 100x more important than "that warning from turn 7." This paper proposes KV Cache prefix-zone hard-constraint injection: separating non-losable constraints from the compressible zone and placing them in the prefix zone (KV Cache) for physical isolation. Constraints survive not because the compression algorithm is clever — but because they are never in the content being compressed. This approach raises constraint retention from ~40% to >95% after 15 dialogue turns, and its economic feasibility depends on DeepSeek's low KV Cache cost — the same approach is unaffordable for Claude and GPT.

---

## 1. Problem Definition

### 1.1 The "Fairness Violence" of Compression

Every long-task Agent must perform context compression. No compression = context window explosion = Agent cannot run. Compression itself is not the problem — the problem is: **you don't know what information gets lost after compression.**

Typical scenario: on turn 3 you repeatedly emphasize, "Never touch config files, the whole service will crash if you do." The Agent responds, "Understood."

After 20 turns, the context has been compressed. Is that constraint you hammered on turn 3 still there?

The compression algorithm doesn't know that "never touch config files" is 100x more important than "that warning on turn 7 doesn't matter." It evaluates all information with uniform weight. The important gets submerged, the unimportant gets preserved. This is the "fairness violence" of compression — mathematically fair, semantically stupid.

### 1.2 Root Cause: Constraints and Dialogue Share the Same Compression Domain

The root of the problem is not that compression algorithms aren't good enough — it is an **architectural error**: hard constraints (non-losable) and dialogue history (compressible) are placed in the same region and subjected to uniform processing by the same compression algorithm.

```
Traditional approach:
  [System Prompt including constraints A/B/C][dialogue1][dialogue2][dialogue3]...[dialogueN]
    ↑ All in the same compression domain → constraint A may be randomly dropped after compression
```

Constraints and dialogue differ in position, importance, and lifecycle within the sequence, yet are fed indiscriminately into the same compressor. This is not the compressor's fault — it is the premise of "mix everything together then compress" that is the problem.

### 1.3 Formalization

Let an Agent's long dialogue sequence S = C ∥ D, where C = {c₁, c₂, ..., cₖ} is the set of hard constraints (non-losable) and D = {d₁, d₂, ..., dₜ} is the dialogue history (compressible).

Let a compression function f reduce sequence length from L to L' (L' < L), with compression ratio r = L'/L. f is semantically unfaithful — for any information fragment x ∈ S, the probability P(preserved | x, f) that f retains x is independent of x's semantic importance.

As t → ∞, sequence length L(t) ∝ t and compression ratio r converges to a fixed upper bound (determined by window size), so for any cᵢ:

P(cᵢ ∈ f(S)) → r · (1/|S|) · |S| = r

That is, the expected retention rate for each constraint converges to the compression ratio r. When r = 0.4 (typical long-task Agent compression ratio), constraint retention is approximately 40%.

**Key insight**: if C and D are fed into the same f, C's retention rate is determined by r and uncontrollable. But if C is physically isolated — not passing through f — then P(cᵢ preserved) = 1.

---

## 2. Existing Approaches and Limitations

| Approach | Core Idea | Why It Fails |
|------|---------|-----------|
| **Smarter compression algorithms** | Optimize compression strategy, use importance scoring instead of uniform weights | Still post-hoc remediation. Importance assessment itself depends on model judgment — the model forgets just the same in long context, and importance-assessment accuracy degrades with dialogue turns |
| **Importance-aware compression** | Mark critical information as "incompressible" | The marking act itself depends on model judgment in long context. The deeper the turn count, the more likely the model misses marks. Essentially outsourcing the same model's attention problem to the same model |
| **Longer compression intervals** | Accumulate more turns before compressing, lower compression frequency | Defers the problem. Window exhaustion just arrives later — pushed from turn 15 to turn 30, but the problem's nature doesn't change |
| **Segmented summaries + cumulative tracking** (Claude Code) | Segment-summarize history dialogue, maintain cumulative tracking of file modifications | Industry's strongest, but summaries are still compression — after constraint expression in a summary is rephrased, fidelity drops. "Absolutely never touch config files" becomes "watch config files" |
| **Constraint re-injection** | Re-inject key constraints into dialogue every N turns | Occupies context window → accelerates L(t) growth → triggers compression earlier → accelerates constraint dilution. Positive-feedback degradation |

**Common defect**: all approaches optimize on the proposition "preserve the most important information after compression." The correct proposition should be: **what information fundamentally should not be compressed?**

---

## 3. Solution Design

### 3.1 Prefix-Zone Isolation Principle

The physical structure of KV Cache provides a natural isolation zone: **the prefix zone**.

Prefix-zone tokens are computed (participate in self-attention) for every new token generated, but they sit at the very front of the sequence and **do not participate in subsequent dialogue accumulation and compression flows**. The prefix zone = a physical "compression get-out-of-jail-free card."

Core solution: extract hard constraints from the compressible zone and place them in the stable prefix of the system prompt (assembled once at Agent boot then frozen, using the inference engine's Prefix Caching mechanism so they do not participate in subsequent dialogue compression).

```
Traditional approach:
  [System Prompt including constraints A/B/C][dialogue1][dialogue2][dialogue3]...
    ↑ All in the compressible zone → constraint A may be dropped after compression

Prefix injection approach:
  [constraintA][constraintB][constraintC]  ← prefix zone (KV Cache, never compressed)
  ═══════════════════════
  [Rest of System Prompt][dialogue1][dialogue2][dialogue3]... ← compressible zone
```

Core logic: no smarter compression algorithm needed. Just physically separate "what cannot be lost" from "what can be lost."

> **Constraints survive not because the compression algorithm is clever. It is because they are never in the content being compressed.**

### 3.2 Definition and Extraction of Hard Constraints

Not every instruction should be injected into the prefix zone. The prefix zone is a scarce resource — each additional token adds slightly to the fixed computation cost of KV Cache.

**Definition of a hard constraint**: violation leads to unacceptable task failure.

| Constraint Type | Example | Hard Constraint? | Reason |
|---------|------|:---:|------|
| Safety red line | "Never delete the production database" | ✅ | Violation = disaster |
| Environment limits | "Must use Python 3.11" | ✅ | Violation = code won't run |
| Operation boundaries | "Don't modify files under /etc/" | ✅ | Violation = system-level damage |
| Format requirements | "Output as Markdown tables" | ✅ | Violation = output unusable |
| Style preference | "Code comments in English" | ⚠️ Case-dependent | Non-compliance doesn't cause failure, but may graduate to hard constraint in specific scenarios (e.g. international teams) |
| Naming convention | "Use camelCase for variable names" | ❌ | Don't place when unnecessary — prefix-zone real estate is limited |

**Extraction mechanism**: hard-constraint extraction should be automated — extract keywords like "shall not / don't / must / forbidden / strictly prohibited" from the System Prompt or user messages via pattern matching, and auto-inject into the prefix zone. No manual annotation needed, no need for the model to judge in long context — keyword matching is deterministic and unaffected by dialogue turn count.

### 3.3 Implementation: System Prompt Preprocessing Skill

In the Hermes architecture, this approach is implemented as a **System Prompt Preprocessing Skill**, fully leveraging Hermes's three-layer injection structure (template injection + Skills injection + Memory injection):

1. When a user sends a task, the preprocessing Skill scans the System Prompt and user message
2. Extracts all hard constraints via keyword matching ("cannot / don't / must / prohibit / strictly prohibit")
3. Injects the extracted constraint list into the prefix zone (KV Cache layer)
4. Executes the task normally — the rest of the System Prompt and dialogue history stay in the compressible zone

This Skill requires no modification to Hermes core code. It is an elegant use case of the Skills mechanism — using Harness-layer extensibility to achieve physical isolation of constraints without touching core architecture.

---

## 4. Analysis

### 4.1 Why This Approach Solves the Root Problem

The root problem is not "compression algorithms aren't smart enough" — it is **constraints and dialogue sharing the same compression domain**.

All existing approaches attempt to improve f's fidelity (preserve more important information after compression). But f's fidelity has a hard upper bound — model attention dilution with sequence length is a physical law, not an engineering problem.

Prefix injection does not improve f. It **bypasses f**:

- Hard constraints C enter the prefix zone → do not pass through f → P(preserved) = 1 (physical guarantee)
- Dialogue history D stays in the compressible zone → passes through f → accepts compression (acceptable because D is inherently designed to be compressed)

This is fundamentally different from Claude Code's compaction: Claude Code's compaction optimizes **inside f** (better summarization strategy, cumulative tracking). Prefix injection does architecture **outside f** — making things that should never be processed by f never pass through f.

Analogy: Claude Code is building a better juicer (less pulp, purer juice). Prefix injection says — don't juice yet, take the important fruit out and set it aside.

### 4.2 Boundary Conditions

The following scenarios are **not** covered by prefix injection:

- **Implicit expectations**: constraints the user implies but does not explicitly state in the Prompt. Keyword extraction only catches explicit declarations — vague expectations like "code should be elegant" cannot be identified as hard constraints or injected into the prefix zone. They live in the compression zone and will be compressed.

- **Context-dependent constraints**: constraint validity depends on current-context judgment. For example, "if it's an emergency fix, code review may be skipped" — injecting this verbatim into the prefix zone means the model sees it every turn, but the "emergency fix" judgment lives in the dialogue zone. After the dialogue zone is compressed, the model may be unable to judge whether the current scenario is an emergency fix.

- **Constraint inflation problem**: if 80% of statements in the System Prompt contain "must / shall not" keywords, the prefix zone fills with hard constraints. Each additional 1K tokens in the prefix zone raises per-new-token generation cost proportionally. In extremis, an oversized prefix zone backfires on inference speed — this is an engineering decision requiring tradeoff between "constraint coverage" and "inference cost."

- **Prefix-zone attention dilution**: although constraints are outside the compression domain (P(preserved) = 1), if the prefix zone itself is very large (e.g. 5K tokens of injected constraints), the model may still under-weight constraints at the back of the prefix zone in extremely long dialogues. Prefix injection solves "constraints not being lost" but cannot fully solve "constraints being followed." The latter requires combination with [attention budget management](03-attention-budget.md).

### 4.3 Comparison with Claude Code Compaction

| Dimension | Claude Code Compaction | Prefix Injection Approach |
|------|----------------------|:---:|
| Optimization target | Internal quality of compression algorithm f | Physical distribution of compressed objects |
| Strategy nature | Reactive — recover after compression | Proactive — isolate before compression |
| Constraint preservation mechanism | Depends on semantic fidelity of summary | Physical isolation, not passing through compression |
| Model dependence | Requires model to maintain judgment in long context | Not needed — keyword matching is deterministic |
| Retention rate | Incremental improvement, hard upper bound | >95% (physical guarantee) |
| Extra cost | Consumes tokens for summarization per compression | Each 1K extra tokens in prefix zone → per-new-token generation cost rises microscopically |

Claude Code's compaction is the industry's most mature approach, but its essence is still optimizing on "preserve the most important information after compression." Prefix injection changes the proposition — **don't compress** the most important information.

### 4.4 V4 Compressor: Learned Gated Pooling Challenges Static Boundaries

> **Evidence note:** This section is based on fixed-source analysis of DeepSeek V4 Flash (`inference/model.py`, checked-out commit). All line-number references use that checked-out version. Effect comparison of V4 Compressor against I-04's prefix injection = **Level B evidence** (pending end-to-end experimental validation); source-structure analysis = **Level A1 evidence** (reproducible reads).

#### 4.4.1 Revisiting the Original Claim's Premise

I-04's core thesis rests on Harness-layer physical constraints:

> Hard constraints C enter the prefix zone → do not pass through compression function f → P(preserved) = 1 (physical guarantee)

This claim is **completely correct** at the Harness layer. The Harness runs outside the model — it cannot see the attention matrix, gating weights, or which tokens the model internally considers most important for current generation. Therefore at the Harness layer, the claim "a static boundary between compression and hard constraints cannot be precisely implemented" still holds — you cannot use an external system that cannot see the model's internal workings to decide "keep the first 100 tokens, compress token 101."

But at the model layer, DeepSeek V4's Compressor mechanism provides a new perspective: **the model can learn to approximate "precisely choosing what to keep."**

#### 4.4.2 Compressor Mechanism: Learned Gated Pooling

DeepSeek V4 Flash's `Compressor` class (`inference/model.py` L279-377) implements a fundamentally different approach from Harness-layer static isolation — **learned gated pooling**.

Its docstring explicitly states the design intent:

```python
# inference/model.py L279-281
class Compressor(nn.Module):
    """Compresses KV cache via learned gated pooling over `compress_ratio` consecutive tokens.
    When overlap=True (ratio==4), uses overlapping windows for smoother compression boundaries."""
```

Key components (`inference/model.py` L283-298):

```python
# L283: default 4:1 compression ratio
def __init__(self, args: ModelArgs, compress_ratio: int = 4, ...):
    # L294: learnable positional encoding — gives each position in the compression window a trainable weight bias
    self.ape = nn.Parameter(torch.empty(compress_ratio, coff * self.head_dim, ...))
    # L297: learnable KV projection layer
    self.wkv = Linear(self.dim, coff * self.head_dim, ...)
    # L298: learnable gating weight layer — this is key: not static averaging, but learning each token's contribution weight in the target compressed token
    self.wgate = Linear(self.dim, coff * self.head_dim, ...)
```

The core operation is at L342 — the **soul** of the Compressor:

```python
# inference/model.py L324, L338, L342
score = self.wgate(x)        # output gate score per token
score = score.unflatten(1, (-1, ratio)) + self.ape  # add learnable positional encoding
kv = (kv * score.softmax(dim=2)).sum(dim=2)  # aggregate ratio tokens into one by softmax weights
```

**This is not simple average pooling.** `score.softmax(dim=2)` assigns each token in the compression window a **continuous learned weight** (summing to 1); `wgate` and `ape` are jointly optimized in end-to-end training, enabling the model to learn: **among 4 (or 128) consecutive tokens, which is most important for future generation, and give it larger compression weight.**

Furthermore, V4 Flash uses different compression ratios at different Transformer layers (`inference/model.py` L65 defaults, `config.json` L66 actual config):

```python
# ModelArgs L65: default compression ratio config
compress_ratios: Tuple[int] = (0, 0, 4, 128, 4, 128, 4, 0)
# 0 = no compression, 4 = CSA 4:1 compression, 128 = HCA 128:1 compression
# Alternating: shallow CSA compresses gently, deep HCA compresses aggressively
```

```
config.json L66 (Flash: 43 hidden layers + 1 MTP layer = 44 ratio values):
[0, 0, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, ..., 4, 0]
  L0 L1 L2  L3  L4  L5  L6  L7 ...
```

This means: **different depth layers see historical information at different granularities** — shallow layers retain finer-grained context, deep layers compress with more aggressive ratios, forming a "pyramid" KV compression structure. Each layer's Compressor has its own independent `wgate` and `ape` parameters, learning what to retain for itself.

Additionally, V4's `Indexer` class (`inference/model.py` L380-433) handles top-k selection for sparse attention — it internally has an independent `Compressor` (L398) used to score compressed KV. This shows learned compression is used not only in KV cache storage but also in selecting "which historical positions to attend to."

#### 4.4.3 Comparing the Two Approaches

| Dimension | Harness-Layer Static Prefix (I-04 Original) | V4 Model-Layer Compressor |
|------|------|------|
| **Isolation mechanism** | Physical isolation — constraints in prefix zone, not through f | Learned pooling — each token has a softmax weight |
| **Determinism** | Deterministic — P(preserved) = 1 | Probabilistic — P(preserved) ∝ learned weight, varies with input |
| **Learning cost** | Zero — no training needed | End-to-end training optimizes wgate/ape |
| **Granularity** | Coarse — either fully preserved or not preserved | Fine — each token has a continuous weight in [0, 1] |
| **Interpretability** | High — can list every constraint in the prefix zone precisely | Low — gating weights are implicitly learned, hard to explain per-token |
| **Visibility to Harness** | Fully visible — Harness constructs prefix-zone content | Invisible — Harness cannot see model-internal attention weights |
| **Applicable scenario** | "Absolutely cannot lose" hard constraints | "Relatively important" dialogue context |

#### 4.4.4 Complementary, Not Mutually Exclusive

The discovery of V4 Compressor does not negate I-04's core thesis; it reveals two **complementary** optimization paths:

- **Harness-layer prefix injection**: guarantees "absolutely cannot lose" hard constraints (system prompt core rules, safety red lines, environment limits). These constraints must have deterministic physical guarantees and cannot depend on the model's implicit judgment in long context.
- **V4 model-layer Compressor**: in "relatively important" dialogue history, distinguishes important information from noise via learned gating — that warning from turn 7 may matter more than an edge config mentioned on turn 3; the model learns to aggregate by softmax weights rather than simple truncation or averaging.

The division of labor can be summarized as:

```
Harness Layer (I-04 prefix injection)        Model Layer (V4 Compressor)
───────────────────────────────              ─────────────────────────
Guarantees "physical existence"               Learns "what is important"
  of constraints                               in history
Deterministic guarantee                      Probabilistic optimization
Architectural constraint                     Learned in training
"Don't lose"                                 "Choose correctly"
```

> **Analogy**: Harness-layer prefix injection is like taking important documents out of the pile headed for the shredder and locking them in a safe — **physically cannot be lost**. V4's Compressor is like training a sorter — it learns to quickly pick out the valuable sheets from the pile, but doesn't guarantee never making a mistake. The two solve different problems: the former targets "absolutely cannot lose" hard constraints, the latter targets "relatively important" soft context.

#### 4.4.5 Correction to the Original Claim

Earlier versions of this paper had a sharper formulation: **"the static boundary between compression and hard constraints cannot be precisely implemented."** This claim **still holds** at the Harness layer — because the Harness runs outside the model and lacks visibility into the model's internal attention distribution, it cannot "precisely" tell the model "keep the first 100 tokens, compress token 101."

But V4 Compressor provides a **model-layer corrective lens**:

1. **Inside the model**, through `wgate` + `ape` + `softmax` learned gating, the model can learn to "choose precisely" — not setting hard boundaries at the token level (keep vs. drop), but assigning continuous weights by importance within compression windows.
2. **Compressor boundaries are soft**: `overlap=True` (when ratio=4) uses overlapping windows for smoother compression boundaries — further demonstrating V4's design choice: **no hard truncation; use learning to approximate the optimal retention strategy**.
3. **Different compression ratios at different layers** means the model learns different "retention strategies" at different abstraction levels — shallow CSA (4:1) retains more positional detail, deep HCA (128:1) retains only the most core semantic information.

Thus the complete picture is:

> **The Harness layer (I-04) provides "deterministic physical guarantees" — constraints are not lost. The model layer (V4 Compressor) provides "learned information filtering" — what in history is important. Each plays its role; used in combination they maximize Agent information reliability in long tasks.**

---

## 5. Validation Path

### 5.1 Validated

| Approach | Constraint Retention After 15 Turns | Notes |
|------|:---:|------|
| No prefix injection (constraints in compressible zone) | ~40% | Constraints compressed alongside dialogue content — retention converges to compression ratio |
| **Prefix injection (constraint isolation)** | **> 95%** | Constraints in physically isolated zone, compression cannot touch them |

> **Data note:** Self-test data, same experiment group as article 03's prefix-injection dimension, not an independent experiment. Independent reproduction needed.

The reason retention > 95% is not 100%: not because constraints are lost to compression — but in extremely long context, the model's attention weight on constraints at the far end of the prefix zone may dilute. Prefix injection ensures "physical existence," but "attention allocation" remains constrained by Transformer's O(n²) attention distribution.

### 5.2 To Be Validated

- **Cost-benefit curve**: for each additional 1K tokens in the prefix zone, what is the marginal drop in dialogue throughput? At what constraint volume does prefix injection's cost exceed its benefit?
- **Optimal prefix-zone size**: under different task types, where is the sweet spot for prefix-zone token count? Is there a critical point where "constraints crowd out reasoning space"?
- **Keyword-matching precision/recall**: false-positive rate (rules that don't need injecting get injected) and false-negative rate (truly hard constraints get missed) for automated hard-constraint extraction
- **Combined effect with attention budget management**: when prefix injection (physical guarantee) + attention budget management (attention allocation optimization) run jointly, constraint **compliance rate** (not just retention rate) after 15 turns

---

## 6. Why Only DeepSeek Can Play This Way

This is not a technical barrier — it is an **economic barrier**.

KV Cache is not free. The more constraints placed in the prefix zone, the more KV pairs must be computed per new token generated → token generation cost rises. Under standard self-attention, each additional 1K tokens in the prefix zone → per-subsequent-token inference FLOPs rise on the order of d_model × n_layers. But DeepSeek V4 uses CSA (Compressed Sparse Attention) + MQA (1 KV head) to drastically compress KV cache and inference overhead (official data: 10% KV cache vs V3.2), meaning the prefix zone can hold more constraints without significant cost increase.

- **Claude / GPT**: Tokens themselves are expensive (GPT-4 output $60/1M tokens). Each extra 1K tokens in the prefix zone → per-new-token cost rises → marginal cost significant. A long task may generate 50K tokens → extra cost enough to be commercially unviable.
- **DeepSeek**: KV Cache is cheap (output ~$2/1M tokens). Prefix zone can hold more constraints → marginal cost negligible. For the same 50K-token task, extra cost is within the price of a meal.

Engineering-wise Claude and GPT could implement the same approach, but commercially they can't afford it. It's not that "others can't do it" — it's that "others can't afford it."

This is why DeepSeek's KV Cache advantage is a **product moat**. The essence of Harness Engineering is leveraging this structural cost advantage to design product approaches competitors cannot economically catch up to. When your competitive advantage derives from opponents' cost structure rather than technical capability, their window to catch up is not "develop a new approach" — it's "wait for your own token prices to drop."

---

## Conclusion

The "fairness violence" of context compression is not a compression-algorithm problem — it is an architectural error: putting things that should not be compressed into the compression domain. Prefix injection does not optimize the compression algorithm; it physically isolates hard constraints out of the compression domain. Constraints survive not because the algorithm is clever — but because they are never in the content being compressed. And the economic feasibility of this approach depends on DeepSeek's low KV Cache cost — a textbook case of Harness Engineering exploiting structural cost advantages.

---

*Next: [05 Document KV Cache Optimization Structure](05-document-kv-cache.md) — applying the prefix principle of "stable up front, changing later" to all document formats the Agent produces*
