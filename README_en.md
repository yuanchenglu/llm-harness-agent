# LLM + Harness = Agent

> From model capability to a verifiable Agent system — a framework grounded in long-term practice, source audits, and falsifiable experiments

[**简体中文**](README.md) · [**English**](README_en.md) · [**Current Status**](STATUS.md)

---

## TL;DR

1. **Model capability is not product capability.** Context, tools, permissions, state, and verification can materially change the reliability, cost, and user experience of the same model.
2. **A Harness is the protocol, control, execution, and evidence layer between a model and the real world.** It may amplify model capability or introduce new failure modes, so it must be evaluated with fixed source evidence, protocol tests, and task benchmarks.
3. **This repository is a knowledge base for research, product specifications, architecture decisions, and redacted experiment summaries.** It is not the complete current DeepSeekAgent Runtime repository and does not independently prove that a production release exists.
4. **The current release state is defined by [`STATUS.md`](STATUS.md) and [`stage-gates.json`](zh/blueprint/stage-gates.json).** Without an immutable Runtime commit, tag, artifact, checksum, platform matrix, and release decision, the Production Release Gate remains unverified.

> **Bilingual status:** the 18 English innovation articles were synchronized with the current Chinese methodology and architecture on 2026-07-27. The Chinese and English articles are maintained as paired current documents; when wording differs, evidence level, boundaries, data models, and validation requirements must remain equivalent.

## Product and Research Entry Points

| Document | Purpose |
|---|---|
| [Repository Status](STATUS.md) | What this repository can confirm and which external release evidence is still missing |
| [PRD TechPlan](zh/prd-tech-plan/README.md) | Product scope, PRD, architecture, release gates, and decision records |
| [Blueprint Handover Pack](zh/blueprint/README.md) | Historical stages, evidence chains, and research materials |
| [Research Method and Evidence Calibration](en/theory/research-method.md) | Distinguishes source facts, official claims, engineering inference, experiments, and missing evidence |

Read `STATUS.md` first, then the PRD TechPlan, and only then use the Blueprint to trace historical evidence.

---

## Core Architecture

```text
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

**One sentence:** the model performs probabilistic understanding and generation; the Harness controls context, tools, permissions, execution, state, recovery, and evidence. The CPU/OS analogy is useful for intuition, but it is not a substitute for protocol and runtime analysis.

---

## Start Here

| Article | Purpose |
|---|---|
| [DeepSeek Agent Theory Guide](en/theory/theory-guide.md) | A five-layer theory of model, context, tools, orchestration, and evidence |
| [Research Method and Evidence Calibration](en/theory/research-method.md) | Evidence levels and correction rules for strong claims |
| [Protocol and Prefix Cache Evidence Report (Chinese)](zh/blueprint/03-5-DeepSeek-Agent协议与Benchmark验证-DeepSeek-Agent-Protocol-and-Benchmark-Validation/18-0-协议与Prefix-Cache实证报告-Protocol-and-Prefix-Cache-Evidence.md) | Historical experiment boundaries, confirmed observations, and unresolved questions |
| [Benchmark Harness Plan (Chinese)](zh/blueprint/benchmark-harness-plan.md) | Historical experiment design and acceptance criteria; not the current sole execution task |
| [Product Comparison](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Implementation boundaries and suitable use cases across Agent products |

## Core Innovations

> The English and Chinese articles below are paired current documents. A mechanism name does not mean that a public benchmark or production implementation has already been completed.

| # | Article | Accurate Current Positioning |
|---|---------|------------------------------|
| [01](en/innovations/01-agent-immune-system.md) | **Agent Hardening Loop** | Convert incidents into governed Policy, Test, Schema, or Skill improvements |
| [02](en/innovations/02-bidirectional-agent.md) | **Model Meta-Requests** | The model may request context, review, or escalation while Runtime retains authority |
| [03](en/innovations/03-attention-budget.md) | **Context Allocation** | Replace the unsupported `1/L` dilution law with measurable context and evidence controls |
| [04](en/innovations/04-kv-cache-prefix.md) | **Stable Constraints vs. Compressible History** | Separate retention, compliance, enforcement, and Provider cache behavior |
| [05](en/innovations/05-document-kv-cache.md) | **Agent-Readable Documents** | Versioned summaries, stable section IDs, evidence indexes, and tiered reading |
| [06](en/innovations/06-okr-planstep-cascade.md) | **PlanGraph** | Nodes, typed edges, acceptance criteria, evidence, and cascading invalidation |
| [07](en/innovations/07-review-switching.md) | **Risk/Evidence Review Router** | Select review modes from risk, reversibility, blast radius, and evidence completeness |
| [08](en/innovations/08-scope-creep.md) | **Scope Change Control** | Separate product scope expansion from implementation dependency discovery |
| [09](en/innovations/09-skills-self-evolution.md) | **Governed Skill Supply Chain** | Provenance, permission, tests, approval, canary, monitoring, and rollback |
| [10](en/innovations/10-intent-routing.md) | **Intent→Strategy Routing** | A 7+1 design proposal built from observed OMO/Hermes routing ideas |
| [11](en/innovations/11-checkpoint-review.md) | **Traceable Checkpoints** | Versioned state, evidence references, stale verdicts, and idempotent resume |
| [12](en/innovations/12-memory-granularity.md) | **Scoped Memory Compilation** | Source, scope, confidence, validity, privacy, and user control |
| [13](en/innovations/13-byte-stable-prefix-architecture.md) | **Bounded Byte-Stability** | Canonical segments and explicit invalidation, subordinate to correctness and safety |
| [14](en/innovations/14-reasoning-content-stripping.md) | **Reasoning Replay Policy** | Provider/endpoint-specific replay, drop, or conservative fallback |
| [15](en/innovations/15-dsml-tool-call-optimization.md) | **DSML Encoding Research** | Encoding internals do not imply a client-side DSML protocol |
| [16](en/innovations/16-quick-instruction-routing.md) | **Quick Instruction Capability Probe** | Encoding evidence exists; public API availability remains to be verified |
| [17](en/innovations/17-reasoning-effort-control.md) | **Reasoning Policy and Budget** | Separate parameter acceptance, semantic effect, and task benefit |
| [18](en/innovations/18-latest-reminder-injection.md) | **Dynamic Context Placement** | Source, trust, scope, TTL, privacy, and A/B testing matter more than position slogans |

---

## About

Yuan Chenglu. More than ten years in the DeepinOS open-source community, former Product Director at CodingCat, and founder of MiniCoding.

This project studies how models, Harnesses, tools, memory, skills, context, and evidence systems jointly affect real task outcomes.

The core thesis is `LLM + Harness = Agent`, but every strong claim should be traceable to fixed source code, a public protocol, a reproducible experiment, or task-level evidence.

---

## Get Involved

- **Technical discussion / opportunities:** yuanchenglu001@gmail.com
- **GitHub Issues:** submit counterexamples, source evidence, or reproducible experiments
- **License:** [CC BY-NC-SA 4.0](LICENSE.md) for non-commercial sharing and adaptation with attribution and share-alike. See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Separating stable from changing information is an important design line, not an experiment-free universal law.*
