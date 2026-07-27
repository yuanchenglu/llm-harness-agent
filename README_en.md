# LLM + Harness = Agent

> Making AI models work reliably in real-world scenarios — 18 in-depth analyses answering the same question from two angles: hands-on practice and source-code verification.
>
> Not a research paper. An engineer's field notes from the trenches.

**[简体中文](README.md)** · **[English](README_en.md)**

***

## What This Repository Is

You're probably here because you've run into one of these:

- The same model (DeepSeek V4 / GPT-4o...) behaves completely differently across Agent frameworks, and you don't know why
- You've tried several Agent products (Claude Code, OpenCode, Cursor...) and want to understand which architecture is worth deep-diving into
- You've heard about KV Cache, Prefix Cache, Reasoning Effort — and you want to know how to actually use them
- You want to build your own Agent but don't know where to start — too much theory, too many papers, not enough actionable code

**This repository is the answer to those questions.** It's not a standard README but a living knowledge base — the theoretical frameworks, source-audit conclusions, and unverified experimental hypotheses accumulated over a year of building agents in production.

**Core thesis**: Model capability determines the floor of an Agent; Harness design determines the ceiling. The same DeepSeek API, routed through different context management, tool orchestration, and permission controls, can produce 10× throughput difference. This isn't speculation — it's visible at the code level.

---

## Who Should Read This

| If you are… | Start here |
|------------|-----------|
| **Product Manager / CEO** — want to understand technical differences between Agent products | [PRD TechPlan](zh/prd-tech-plan/README.md) → [Product Comparison](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) |
| **Developer** — want to apply these ideas in your own project | [Core Innovations](README_en.md#core-innovations) starting from 01 → [Research Method](en/theory/research-method.md) |
| **Researcher** — interested in the academic lineage of Agent architecture | [Paper Database](https://github.com/yuanchenglu/llm-harness-agent/blob/master/references/papers.md) → [Theory Guide](en/theory/theory-guide.md) |
| **Just want to get things done** — use a product instead | → [deepseek_runtime](https://github.com/7colorai/deepseek_runtime) / [deepseekagent](https://github.com/yuanchenglu/deepseekagent) |

---

## Quick Navigation

### For Product Managers / Decision-Makers

| Document | One-Liner |
|----------|-----------|
| [PRD TechPlan](zh/prd-tech-plan/README.md) | Current product roadmap, release gates, and decision log |
| [9 Agent Products: Calibrated Comparison](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Hermes / Claude Code / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent / CodeWhale |
| [Blueprint Handover Pack](zh/blueprint/README.md) | Milestone artifacts, evidence chain, and research history |

### For Developers

Core innovations, best read in order starting from 01:

| # | Article | One-Liner Value |
|---|---------|----------------|
| 01 | [Agent Immune System](en/innovations/01-agent-immune-system.md) | Prompt instructions decay in long tasks — have the harness self-audit and self-repair |
| 02 | [Brain Drives the Cerebellum](en/innovations/02-bidirectional-agent.md) | From "Harness→LLM" one-way to "LLM⇄Harness" bidirectional flow |
| 03 | [Attention Budget Management](en/innovations/03-attention-budget.md) | Agent degradation may come from context and attention management, not just the model |
| 04 | [KV Cache Prefix Injection](en/innovations/04-kv-cache-prefix.md) | Separate stable constraints from compressible history |
| 05 | [Document KV Cache Optimization](en/innovations/05-document-kv-cache.md) | Apply the agent's internal optimization to its own document structure |
| 06 | [OKR PlanStep + Cascade Correction](en/innovations/06-okr-planstep-cascade.md) | Upgrade flat checklists to directed dependency graphs with auto-cascade |
| 07 | [KV Cache-Driven Review Switching](en/innovations/07-review-switching.md) | Review depth as f(KV Cache, Plan complexity), not a fixed threshold |
| 08 | [Two-Level Scope Creep Strategy](en/innovations/08-scope-creep.md) | Demand creep and technical creep are different diseases — different treatments |
| 09 | [Skills Self-Evolution](en/innovations/09-skills-self-evolution.md) | Crystallize successful patterns into reusable skills |
| 10 | [7+1 Intent→Strategy Routing](en/innovations/10-intent-routing.md) | Recognize task intent → auto-match strategy |
| 11 | [Checkpoint Multi-Round Review](en/innovations/11-checkpoint-review.md) | Use independent snapshots to bound review context |
| 12 | [Memory Granularity Control](en/innovations/12-memory-granularity.md) | Convergent tasks need strong memory; divergent tasks don't |
| 13 | [Byte-Stable Prefix Architecture](en/innovations/13-byte-stable-prefix-architecture.md) | Make the whole Agent cache-first, not just the system prompt |
| 14 | [Reasoning Content Stripping](en/innovations/14-reasoning-content-stripping.md) | Every token must justify its existence |
| 15 | [DSML Tool-Call Format Optimization](en/innovations/15-dsml-tool-call-optimization.md) | DeepSeek V4's unique XML-style markup |
| 16 | [Quick Instruction Routing](en/innovations/16-quick-instruction-routing.md) | V4's 6 built-in special-token routing |
| 17 | [Reasoning Effort Control](en/innovations/17-reasoning-effort-control.md) | Three-tier reasoning_effort control strategy |
| 18 | [Latest Reminder Injection](en/innovations/18-latest-reminder-injection.md) | Inject time-sensitive info at the highest-attention position |

### I Want to Get Hands-On — Ready-Made Products

| Product | One-Liner |
|---------|-----------|
| [deepseek_runtime](https://github.com/7colorai/deepseek_runtime) | Fork-ready Python runtime kernel for building agents on DeepSeek API |
| [deepseekagent](https://github.com/yuanchenglu/deepseekagent) | "One-person company" OS with 10-layer Harness optimization |
| [oh-my-deepseek-harness](https://github.com/yuanchenglu/oh-my-deepseek-harness) | Hermes Agent plugin — inject full DeepSeek capability in one command |
| [deepcode](https://github.com/yuanchenglu/deepcode) | DeepSeek V4-optimized AI coding assistant |

---

## Core Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   LLM (Probabilistic Engine)     Harness Runtime & Evidence   │
│   ────────────────────           ────────────────────────────│
│                                                              │
│   Understand intent    ──→       Persistent Memory            │
│   Generate code/text  ──→       Tools and Policy             │
│   Logical reasoning   ──→       State and Orchestration      │
│   Pattern recognition ──→       Checkpoints and Verification │
│                                 Routing and Cost Telemetry    │
│                                 Sandbox, Recovery, Review     │
│                                 Context Compilation           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**One sentence**: The model is a probabilistic inference engine; the Harness connects it to context, tools, permissions, state, and evidence.

---

## About Me

Yuan Chenglu. DeepinOS Linux operating system developer. Product Director at CodingCat → Founder at MiniCoding.

Now running an agent matrix across 5 machines: 3 R&D squads (OpenCode / Claude Code / CodeX) + 1 marketing squad (OpenClaw), with Hermes as the CEO orchestrating everything. Multiple rounds of Volcano Engine Hermes Agent internal beta testing.

I believe LLM + Harness = Agent. Models and Harnesses evolve together. DeepSeek introduces new model capabilities and cost structures; the next task is turning them into dependable products through verifiable systems engineering.

---

## Get Involved

- **Technical discussion / opportunities**: <yuanchenglu001@gmail.com>
- **GitHub Issues**: Disagree with an innovation point? Open an Issue with your reasoning chain
- **License**: [CC BY-NC-SA 4.0](LICENSE.md) — non-commercial sharing and adaptation with attribution and share-alike required. See [CONTRIBUTING.md](CONTRIBUTING.md)

---

> ⭐ If this repository saved you research time, give it a star so others can find it.
>
> *Each article in the "LLM + Harness = Agent" series can be read independently. Start from 01 — they share the same core logic: separate what can't be lost from what can be compressed.*
