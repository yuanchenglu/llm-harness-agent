# Document KV Cache Optimization: Applying Agent Inference Optimization to Its Own Outputs

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation Index**: I-05
> **LLM + Harness = Agent** · Part 5
> **Series**: [LLM + Harness = Agent](../../README.md)
> **Previous**: [04 KV Cache Hard-Constraint Prefix Injection](04-kv-cache-prefix.md)

---

> **Abstract:** As Agent-produced documents grow through iteration, each new session loads the full document into context. Token consumption grows linearly, yet the core conclusions are only about 30% of the full text. This paper proposes applying the KV Cache prefix reuse principle to document structure: solidify "must-read" content in the prefix zone (YAML metadata, TL;DR, core arguments), and place "occasionally needed" discussion at the tail's changing zone. When new content is appended, the prefix zone's KV Cache hits fully, and only the tail tokens need recomputation. Theoretical token savings exceed 80%, with zero information loss. The only change is the ordering.

---

## 1. Problem Definition

### 1.1 The Phenomenon

You use an Agent to write a 15KB architecture analysis document. Three days later, you open a new session and ask the Agent to reference that document and continue working. The Agent loads all 15KB into context.

You add 10KB of discussion appendix. Now the document is 25KB. Next time the Agent reads it, another 25KB goes straight into context. Repeat.

Every read cycle, token consumption grows linearly with the document. But the information that matters for the current task (core conclusions, key decisions) is typically just 30% of the document. The other 70% is discussion process, edge-case exploration, and Q&A appendices. Valuable, but not directly relevant to the task at hand.

This is the most insidious cost funnel in Agent development: **document bloat leads to context waste, which leads to effective intelligence degradation.** The model did not get worse. The signal-to-noise ratio in what is fed to it collapsed.

### 1.2 Root Cause

The root cause is not in the Agent's reading strategy. It is in the document's writing convention.

Every document convention today is designed "for humans." Title, introduction, body, subsections, code blocks, conclusions. The structure serves human reading habits: first set the context, then unfold the argument, then summarize at the end. But the primary reader of these documents is no longer human. It is the Agent itself. When an Agent re-reads a document it produced, it does not care about typographic aesthetics. It cares about one thing: **can the first 500 tokens tell me the core conclusions of this document?**

Under the traditional "Introduction > Body > Conclusion" structure, the Agent must read 2KB before reaching the core conclusions. Sentences like "With the rapid advancement of AI technology, Agent architecture has become increasingly important..." are pure token waste for an Agent reader.

The deeper root cause: **KV Cache's granularity is "prefix-contiguous matching."** In traditional document structure, the most stable information (title, metadata) and the most volatile information (discussion records, Q&A) are interleaved. Every time discussion is appended, the prefix may be broken, and all cached KV pairs are invalidated. The Agent must re-encode the entire document.

### 1.3 Formalization

Let document size be S, with core conclusion zone U (typically U ≈ 0.3S) and discussion/appendix zone D = S - U. Token consumption Tᵢ for the i-th Agent read:

**Traditional structure**: Tᵢ = S (full encoding every time). Total consumption over N reads: C = N·S.

**Optimized structure** (stable prefix + changing tail): first read T₁ = S (cold start). Subsequent reads hit the prefix zone's KV Cache. Only tail zone D needs recomputation. Tᵢ ≈ D (i ≥ 2). Total consumption over N reads: C' = S + (N-1)·D.

Token savings ratio = (C - C') / C = (N-1)·(S-D) / (N·S) = (N-1)·U / (N·S) ≈ U/S ≈ 70% (approaching limit as N ≥ 5).

Key insight: **the savings come not from compression. Document integrity is unchanged. They come from ordering**: put the stable content first, the changing content last.

---

## 2. Existing Approaches and Limitations

| Approach | Core Idea | Why It Falls Short |
|----------|-----------|-------------------|
| **Human reading convention** | Introduction > Body > Conclusion, optimized for human reading | Agent is the primary reader now. Introductions are noise. Core conclusions are buried mid-document |
| **Full re-read** | Load entire document on each new session | Token consumption grows linearly with document bloat. No upper bound |
| **Document summary as System Prompt** | Ask Agent to summarize before reading; inject only the summary | Summary generation itself consumes tokens. Information loss between summary and original is uncontrolled |
| **RAG retrieval** | Retrieve fragments by query instead of loading full document | Adds retrieval system complexity. Misses key information when retrieval is inaccurate. The "Agent needs to know what the whole document says" scenario cannot be served by fragments |
| **Context compression** | Compress conversation history to free space | Compression algorithms apply uniform weights to all content. Core conclusions and discussion process are compressed together. What gets lost is unknowable |

**Common deficiency**: Every approach tries to "read less." The correct direction should be "make the content that is read less happen to be the content that is needed." Not compression, but reordering.

---

## 3. Solution Design

### 3.1 Core Principle: Stable in Front, Changing in Back

KV Cache works as follows: during Transformer inference, the Key-Value vectors of already-computed prefix tokens are cached. On subsequent generations, if the prefix is unchanged, the cache is used directly with zero recomputation. Only tokens in the changed zone need recalculation.

Translate this principle to document structure:

```
Traditional Document Structure:       KV Cache-Optimized Structure:
  [Title]                               [YAML Metadata]      ← Prefix zone (permanent, full hit)
  [Introduction/Background]             [TL;DR Conclusions]  ← Core zone (rare change, high hit)
  [Body/Analysis]                       [Core Arguments]     ← Core zone
  [Discussion Process]                  ═══════════════
  [Appendix/Q&A]                        [Detailed Reasoning] ← Body zone
                                        [Discussion Process] ← Changing zone (appends only affect tail)
                                        [Q&A Appendix]       ← Changing zone
```

**Prefix zone** (YAML metadata + TL;DR + core arguments): Written once at document creation. Never modified. Agent reads with full KV Cache hit. Zero recomputation.

**Body zone** (detailed reasoning): Occasionally modified, far less frequently than discussion. High KV Cache hit rate.

**Changing zone** (discussion + Q&A): New content appended with each conversation cycle. But because it sits at the end of the file, appends only recompute the tail tokens. The prefix is unaffected.

This is not compression. It is reordering. File size unchanged. Information integrity unchanged. The only difference: **put what you always need in front. Put what you occasionally need in the back.**

### 3.2 Layer Definitions

The document is divided into three logical layers, ordered by stability:

| Layer | Content | Change Frequency | KV Cache Hit Rate | Typical Size Ratio |
|-------|---------|:---:|:---:|:---:|
| **L1 Prefix Layer** | YAML metadata, TL;DR, core conclusions list | Near zero | ~100% | ~5% |
| **L2 Body Layer** | Detailed analysis, reasoning process, data support | Occasional (modify/supplement) | ~90% | ~45% |
| **L3 Changing Layer** | Discussion records, Q&A appendix, iteration notes | Frequent (append per conversation) | ~0% (each append adds new tail) | ~50% |

L1 prefix layer is the key to KV Cache optimization. It must satisfy two constraints:

1. **Immutability**: Once written, never modified. If a core conclusion truly changes, the right action is not to append, but to restructure the entire document.
2. **Self-descriptiveness**: After reading the prefix layer, the Agent should know "what this document is about, what the core conclusions are, and which innovation points are relevant." It should not need to continue reading.

YAML metadata example:

```yaml
---
title: Plan Architecture Deep Analysis
created: 2026-05-25
innovation_points: [I-01, I-03, I-04]
kv_cache_stable: true
---
```

`kv_cache_stable: true` is a signal to the Agent: "this document's prefix zone is stable. Feel free to cache it. The core conclusions can be obtained within the first 500 tokens."

### 3.3 Real Example

Using the "Plan Architecture Deep Analysis" document, here is the structural difference before and after refactoring.

**Before** (traditional structure, ~40KB):

```markdown
# Plan Architecture Deep Analysis

> Background: With the rapid advancement of Agent technology, the importance
> of Plan as a task planning module is growing...

## 1. Introduction
...500-word preamble, positioning Plan within the Agent system...

## 2. Plan vs Reason: Core Differences
...core conclusions buried in section 2, Agent reads ~2KB to reach them...

## 3. Dependency Graph Analysis
...

## 4. Discussion and Q&A
...discussion records appended over time...
```

**After** (optimized structure, same ~40KB):

```yaml
---
title: Plan Architecture Deep Analysis
created: 2026-05-25
innovation_points: [I-01, I-03, I-04]
kv_cache_stable: true
---
```

```markdown
# Plan Architecture Deep Analysis

> **TL;DR** — Plan is a divergent problem. Reason is a convergent problem.
> First-Principles decomposition is the bridge between them.

## Core Conclusions
1. OMO's Plan is a flat checklist with no dependency graph
2. The cascade correction engine must be built on a directed dependency graph
3. Review strictness should = f(KV Cache occupancy, Plan complexity)

---

## Detailed Analysis
[→ Traditional body content, fully preserved]

## Discussion Appendix
[→ Q&A discussion records, appended chronologically]
```

Comparison:

| | Traditional Structure | Optimized Structure |
|---|---|---|
| File size | 40KB | 40KB (identical) |
| Agent first read | 40KB | 40KB |
| Agent re-read | 40KB (full re-encode) | ~5KB (prefix layer hit) |
| Read after discussion append | 42KB (full re-encode) | ~7KB (prefix hit + new discussion) |
| Token savings | — | **> 80%** |
| Information integrity | 100% | 100% (no content deleted) |

The Agent reads the first 500 tokens and already knows: what this document is about, what the core conclusions are, and which innovation points are relevant. If the current task only needs the core conclusions, it can jump straight to execution without loading 40KB.

---

## 4. Analysis

### 4.1 Why This Solution Addresses the Root Problem

The root problem is not "the Agent reads too slowly." It is "the Agent pays Token costs repeatedly for unchanged content."

This solution transforms the document from an "undifferentiated text stream" into a "KV Cache-friendly structure stratified by stability." The core mechanism:

1. **Prefix layer solidification**: L1 (metadata, TL;DR, core conclusions) is written once and never modified. When the Agent system reads the document, the prefix tokens' KV vectors are cached. This is a native behavior of the Transformer inference engine. No additional code is needed.
2. **Tail append isolation**: All incremental content (discussion, Q&A) is appended to the end of the file. Appending does not change the prefix. Cached KV vectors remain valid.
3. **Signal front-loading**: The Agent obtains all core information within the first 500 tokens of reading. It does not need to "turn to section 2" to find the conclusions.

This is fundamentally an **information ordering optimization problem**, not a compression problem. Changing the order lets the KV Cache mechanism take effect naturally, without introducing any new system.

### 4.2 Boundary Conditions

The following scenarios are **not** covered by this proposal or require additional care:

- **Core conclusion changes**: If the document's core conclusions are overturned and must be rewritten, the prefix layer must be modified. This causes full KV Cache invalidation, and that read degrades to the traditional structure. However, the frequency of such changes is far lower than discussion appends. The average benefit remains significant.
- **Full document restructuring**: If the document changes from an "analysis report" to an "operations manual," this is not an append scenario but a full rewrite. The prefix layer naturally becomes invalid. This is outside the design target.
- **Single-read scenarios**: A document read only once by the Agent gains nothing from the optimized structure (first read cost is the same). The benefit manifests in "multiple cross-session reads."
- **Agent systems without KV Cache**: If the underlying inference engine does not cache KV vectors at all (e.g., certain stateless API deployments), the prefix optimization does not help at the cache level. However, the Agent still benefits from "signal front-loading" in terms of reading efficiency.
- **Multi-author documents**: When multiple people append discussion simultaneously, the tail may experience conflicts. A collaboration strategy (file locking or per-author independent append zones) is needed.

### 4.3 Comparison with the Closest Approaches

| Dimension | RAG Retrieval | Document Summary | Context Compression | This Proposal |
|-----------|:---:|:---:|:---:|:---:|
| Principle | Retrieve fragments by query | Generate short summary to replace original | Uniform compression | Reorder by stability |
| Information loss | Lost if retrieval misses | Summary inherently loses | Uncontrolled | Zero |
| Additional system | Vector DB + index | Extra LLM call | Compressor | None |
| Reading efficiency | Depends on retrieval quality | Low summary tokens | Low compressed tokens | Low prefix tokens |
| Best use case | "Find" specific information | "Understand" the gist | "Save" context space | "Re-read" long documents |

This proposal does not replace RAG or summaries. They serve different scenarios. The scenario this proposal targets is: **an Agent repeatedly re-reading its own long documents, needing core conclusions most of the time but occasionally requiring deep detail.** In this scenario, reordering is a better fit than compression.

---

## 5. Verification Path

### 5.1 Verified

- **KV Cache prefix reuse principle**: The prefix caching mechanism of Transformer inference engines has been widely validated by the industry (vLLM, SGLang, and other inference frameworks with Prefix Caching support).
- **Problem existence**: In actual Agent usage, documents ballooning from 15KB to 40KB+ over iterative conversations is the norm. The token waste per session is quantifiable.

### 5.2 To Be Verified

- **Measured token savings**: In a Prefix Caching-capable inference environment (e.g., vLLM), compare actual Token consumption between traditional structure and optimized structure across 10 cross-session reads. Expected savings > 80%.
- **Signal front-loading effectiveness**: Compare task completion quality between "Agent reading only the prefix layer (first 500 tokens)" vs. "Agent reading the full document" on "continue working based on the document" tasks. Expected difference is minimal, since the prefix layer already contains the core conclusions.
- **Developer adoption threshold**: Document authors must change their writing habits: write core conclusions first, then detailed reasoning. Whether this "inverted pyramid" writing style is acceptable to humans and whether it increases writing burden remain open questions.
- **Automated tooling**: Can a lint tool be developed to automatically check whether an Agent-produced document satisfies the KV Cache-optimized structure (prefix layer existence, core conclusions front-loading, changing zone at the tail)?
- **Cross-framework compatibility**: Different inference frameworks (vLLM, SGLang, TensorRT-LLM) have different prefix caching granularity. The actual benefit of this proposal under each framework needs verification.

---

## 6. Relationship to Hermes

Hermes's System Prompt already implements a "stable in front, changing in back" design: Base System Prompt (permanently stable) > Skills (loaded on demand) > Memory (dynamically injected). This is a three-layer KV Cache-friendly architecture. During each inference, the Base System Prompt's KV vectors are fully cached. Only the tail Memory section needs re-encoding.

This proposal extends the same philosophy from the System Prompt layer to the **document output layer**. Every long document produced by Hermes, whether an analysis report, design proposal, or discussion summary, follows the "prefix YAML + TL;DR + core conclusions" structure.

This creates a complete KV Cache optimization loop:

```
System Prompt layer:   Base (stable) → Skills (semi-stable) → Memory (dynamic)
         ↓ Same design philosophy
Document output layer: L1 Prefix (stable) → L2 Body (semi-stable) → L3 Changing (dynamic)
         ↓ Compounded
KV Cache benefit:      Full prefix hit × two layers = end-to-end optimization from "how to read" to "how to write"
```

Hermes requires no architectural changes to support this proposal. It only needs a constraint in the document generation instruction: "output in KV Cache-optimized structure." The benefit appears automatically in subsequent sessions' context consumption.

---

## Conclusion

The optimization direction for Agent-produced documents is not "write shorter." It is "put the unchanging information in front." The KV Cache prefix reuse principle is not only effective inside the inference engine. Apply it to the document output format, and the Agent's ecosystem optimizes itself. From System Prompt to document output, the same design philosophy runs through the entire chain: **stable in front, changing in back.**

---

*Next: [06 OKR PlanStep + Cascade Correction Engine](06-okr-planstep-cascade.md)*
