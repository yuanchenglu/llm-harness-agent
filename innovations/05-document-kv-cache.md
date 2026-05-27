# Document KV Cache Optimization: Applying the Agent's Own Optimization Principle to Its Output

> Innovation Index: I-05
> **LLM + Harness = Agent** · Part 5
> Series: [LLM + Harness = Agent](../README.md)
> Previous: [04 KV Cache Hard-Constraint Prefix Injection](04-kv-cache-prefix.md)
> Previous (English): [03 Attention Budget Management](03-attention-budget-en.md)

---

## The Problem: Your Documents Get Longer, Your Agent Reads Slower

You used an Agent to write a 15KB architecture analysis. The Agent did great. Three days later you open a new session and ask the Agent to reference that document and keep working. The Agent reads it — all 15KB, straight into context.

You add 10KB of discussion appendix. Now the document is 25KB. Next time the Agent reads it — all 25KB, straight into context. Rinse. Repeat.

Every re-read, token consumption grows linearly. But the information the current task actually needs — the core conclusions, the key decisions — is maybe 30% of the document. The other 70% is discussion process, edge-case exploration, Q&A appendices. Valuable, but irrelevant to the current task.

This is the most invisible cost in Agent development: **document bloat → context waste → effective intelligence degradation**. The model didn't get worse. The signal-to-noise ratio in what you're feeding it collapsed.

And here's the twist nobody's talking about: the primary reader of Agent-produced documents is no longer human. It's the Agent itself. But we're still writing documents structured for human eyes.

---

## Industry Reality: Nobody Is Optimizing This

Every document-writing convention for Agents today is "for humans." Title, introduction, body, subsections, code blocks, references. Structure optimized for the way humans scan.

But when an Agent re-reads a document it produced, it doesn't care whether the typography is pleasant. It cares about one thing: **do the first 500 tokens tell me the core conclusions of this document?**

The traditional "Introduction → Body → Conclusion" structure is actively hostile to Agent re-reading. The introduction burns 200 words on "With the rapid advancement of AI technology, Agent architecture has become increasingly important..." — zero signal, all ceremony. The Agent needs conclusions in the first line, not pleasantries.

Nobody in the industry is treating "Agent-to-Agent document structure" as an optimization surface. It's a blind spot the size of a continent.

---

## The Solution: Stable in Front, Changing in Back

Apply the KV Cache prefix optimization principle to document structure.

KV Cache has a defining characteristic: tokens in the prefix zone are reused on every generation step — cache hit, zero incremental compute. Tokens in the changing zone must be recomputed every time.

Document structure should follow the same physics:

```
Traditional Document Structure:
  [Introduction / Background]
  [Body / Analysis]
  [Discussion Process]
  [Appendix / Q&A]

KV Cache-Optimized Structure:
  [YAML Metadata]       ← Prefix zone (permanent, never changes → full hit)
  [TL;DR Conclusions]   ← Core zone (rarely changes → high hit rate)
  [Core Arguments]      ← Core zone
  ═══════════════
  [Detailed Analysis]   ← Body zone
  [Discussion Process]  ← Changing zone (appends go here → only tail tokens affected)
  [Q&A Appendix]        ← Changing zone
```

**The three-zone principle:**

- **Prefix zone** (YAML metadata + TL;DR + core arguments): Written once at document creation. Never modified. KV Cache hits at 100%.
- **Core zone** (detailed analysis): Occasionally updated, but far less frequently than discussion. KV Cache hits at high rate.
- **Changing zone** (discussion + Q&A): New content appended with every conversation. But because it's at the end of the file, appends only re-compute tail tokens — the prefix remains untouched.

Same file size. Same content completeness. The only difference: information ordering. "What you always need" goes first. "What you occasionally need" goes last.

---

## Real Results

A typical Agent-produced architecture analysis document:

| | Traditional Structure | Optimized Structure |
|---|---|---|
| File size | 40KB | 40KB (identical content) |
| Agent first read cost | 40KB | 40KB |
| Agent re-read cost | 40KB (full re-read) | ~5KB (core zone KV Cache hit) |
| Re-read after discussion append | 42KB (full re-read) | ~7KB (core hit + new discussion) |
| Token savings | — | **> 80%** |

Eighty percent token savings. Not from compressing anything. Not from deleting anything. From putting the stable information where the cache can find it and the changing information where appends are cheap.

---

## A Real Example: Plan Architecture Analysis

Here's the before-and-after of a real document refactoring.

**Before** (traditional structure):

```
# Plan Architecture Deep Analysis
> Background: With the rapid advancement of Agent technology...

## 1. Introduction
...500-word preamble...

## 2. Plan vs Reason
...core conclusions buried in section 2...
```

The Agent had to read 2KB before reaching the core conclusions. Every new session, 2KB × N re-reads wasted.

**After** (optimized structure):

```yaml
---
title: Plan Architecture Deep Analysis
created: 2026-05-25
innovation_points: [I-01, I-03, I-04]
kv_cache_stable: true
---
```

```
# Plan Architecture Deep Analysis

> **TL;DR** — Plan is a divergent problem. Reason is a convergent problem.
> First Principles decomposition is the bridge connecting them.

## Core Conclusions
1. OMO's Plan is a flat checklist — no dependency graph
2. Cascade correction engine must be built on a directed dependency graph
3. Review strictness should = f(KV Cache occupancy, Plan complexity)

---

## Detailed Analysis
[→ Traditional body content]

## Discussion Appendix
[→ Q&A discussion records, appended chronologically]
```

The Agent reads the first 500 tokens and already knows: what this document is about, what the core conclusions are, which innovation points are relevant. If the current task only needs the conclusions — skip straight to execution. No need to burn 40KB on a full read.

---

## Why This Is "Meta-Level Self-Reference Optimization"

KV Cache is the mechanism Agents use internally to accelerate inference. I took the optimization principle of that mechanism — "stable prefix → high cache hit rate" — and applied it to the format of the documents the Agent produces.

Agent uses KV Cache to optimize its own reasoning → Agent uses the same principle to optimize the documents it produces → Agent reads its own documents faster next time.

This is a self-reference loop. The Agent is optimizing its own ecosystem. Not by asking for a better model. Not by waiting for the next architecture. By recognizing that the same physics governing internal inference also governs external output — and designing for both simultaneously.

---

## The Hermes Connection

Hermes's Memory system is a natural fit for this approach.

Hermes injects its System Prompt in layers: Base System Prompt (stable) + Skills (loaded on demand) + Memory (dynamically injected). This is already the "stable in front, changing in back" design philosophy — applied to input.

Extend that philosophy from the System Prompt layer to the document output layer — every document Hermes produces follows the "front-loaded YAML + TL;DR + core conclusions" structure — and you close the loop. The same optimization governs both how the Agent reads and how the Agent writes. Full-stack KV Cache efficiency.

---

## The Series: One Core Logic, Five Layers

Five articles. Five optimization layers. One shared principle: **separate what can't be lost from what can be compressed.**

1. [Immune System](01-agent-immune-system-en.md) — Extract "must-comply constraints" from Prompt and crystallize them as Skills
2. [Brain Driving the Cerebellum](02-bidirectional-agent-en.md) — Let the LLM declare what it needs instead of the Harness guessing
3. [Attention Budget Management](03-attention-budget-en.md) — Allocate attention as a finite resource, don't waste it on noise
4. [KV Cache Prefix Injection](04-kv-cache-prefix.md) — Physically isolate hard constraints from the compressible zone
5. **Document KV Cache Optimization** (this article) — Move core conclusions from the changing zone to the stable zone

Same paradigm, five levels. From Prompt instructions to sub-task isolation. From System Prompt to document output. From runtime to storage format. **Separate management is the first principle of Agent Harness Engineering.**

Don't ask the model to be smarter. Ask the Harness to be better at deciding what the model sees.
