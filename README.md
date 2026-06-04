# LLM + Harness = Agent

> From model capability to a verifiable Agent system — a theory grounded in practice, source audits, and testable hypotheses

[**阅读简体中文版**](README-zh.md) · [**⭐ Star this repo**](https://github.com/yuanchenglu/llm-harness-agent) to get notified when new articles drop

---

## TL;DR

1. **Model capability is not product capability.** Context, tools, permissions, state, and verification can change the reliability, cost, and experience of the same model.
2. **A Harness is the protocol, control, and evidence layer between a model and the real world.** It can amplify capability or introduce new failure modes, so it must be evaluated with source evidence and benchmarks.
3. **This repository is a theory and research guide, not a completed product benchmark.** Practice raises questions, source audits confirm implementations, and experiments decide what belongs in DeepSeek Agent.

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

**One sentence**: The model is a probabilistic inference engine; the Harness connects it to context, tools, permissions, state, and evidence. The CPU/OS analogy is useful for intuition, but it does not replace protocol and runtime analysis.

---

## Navigation

### Start Here

| Article | Purpose |
|---|---|
| [DeepSeek Agent Theory Guide](THEORY-GUIDE.md) | A five-layer theory of model, context, tools, orchestration, and evidence |
| [Research Method and Evidence Calibration](RESEARCH-METHOD.md) | What is source-grounded and what remains a hypothesis |
| [DeepSeek API and Prefix Cache Benchmark Harness Plan (Chinese)](BENCHMARK-HARNESS-PLAN-zh.md) | Experiment matrix, gates, and decision branches for the next and only execution task |
| [Product Comparison](comparison.md) | Product boundaries and use cases |

### Core Innovations (standalone deep-dives)

| # | Article | One-liner |
|---|---------|-----------|
| [01](innovations/01-agent-immune-system.md) | **Agent Immune System** | Prompt instructions inevitably decay — make the harness self-audit and self-repair |
| [02](innovations/02-bidirectional-agent.md) | **Brain Drives the Cerebellum** | From "Harness→LLM" one-way to "LLM⇄Harness" bidirectional flow |
| [03](innovations/03-attention-budget.md) | **Attention Budget Management** | Agent degradation may come from context and attention management, not only the model |
| [04](innovations/04-kv-cache-prefix.md) | **KV Cache Prefix Injection** | Separate stable constraints from compressible history to reduce loss during compaction |
| [05](innovations/05-document-kv-cache.md) | **Document KV Cache Optimization** | Apply the agent's internal optimization to its own document output |
| [06](innovations/06-okr-planstep-cascade.md) | **OKR PlanStep + Cascade Correction** | Upgrade flat checklists to directed dependency graphs with auto-cascade |
| [07](innovations/07-review-switching.md) | **KV Cache-Driven Review Switching** | Review depth as f(KV Cache, Plan complexity), not a fixed threshold |
| [08](innovations/08-scope-creep.md) | **Two-Level Scope Creep Strategy** | Demand creep and technical creep are different diseases — different treatments |
| [09](innovations/09-skills-self-evolution.md) | **Skills Self-Evolution** | Crystallize successful patterns into reusable skills to reduce repeated reasoning |
| [10](innovations/10-intent-routing.md) | **7+1 Intent→Strategy Routing** | Recognize task intent → auto-match interview depth, review standard, execution mode |
| [11](innovations/11-checkpoint-review.md) | **Checkpoint Multi-Round Review** | Use independent snapshots to bound review context instead of replaying full history |
| [12](innovations/12-memory-granularity.md) | **Memory Granularity Control** | Stronger memory isn't always better — convergent tasks need it, divergent tasks don't |
| [13](innovations/13-byte-stable-prefix-architecture.md) | **Byte-Stable Prefix Architecture** | Don't just cache the system prompt — make the whole agent cache-first |
| [14](innovations/14-reasoning-content-stripping.md) | **Reasoning Content Stripping** | Agent should know what NOT to send — every token must justify its existence |

### Product Analysis

| Article | Content |
|------|------|
| [9 Agent Products: Calibrated Comparison](comparison.md) | Calibrated comparison of Hermes / ClaudeCode / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent / CodeWhale + agent matrix division of labor |
| [DeepSeek-Reasonix Deep Analysis](analysis/deepseek-reasonix-deep-analysis.md) | Source-code level analysis + three-way comparison (Hermes vs CodeWhale) + 9 DeepSeek Prefix Cache optimizations |

---

## Why Hermes as the Hub

Not because it has been proven to be "the best," but because it combines many system-level capabilities in one long-running Agent architecture and is therefore a useful research subject:

| Capability | Why it matters | Anyone else? |
|------|-----------|:---:|
| **Memory and Session Search** | Persist and retrieve preferences and decisions | Other products provide different memory forms and governance |
| **Skills and Experience Crystallization** | Reuse recurring workflows | Several platforms support skills; automatic extraction quality needs evaluation |
| **Cronjob** | Scheduled automation — daily summaries, periodic checks | Several platforms schedule work; Hermes is useful for studying integration with a long-running Agent |
| **Gateway Multi-platform** | Feishu/WeChat/Discord unified entry | ⚠️ OpenClaw is itself a gateway product; Hermes' Gateway is natively integrated with the agent kernel |

These four make Hermes evolve from a "coding tool" into an "Agent Operating System."

---

## About Me

Yuan Chenglu. 10+ years in the DeepinOS open-source community. Product Director at CodingCat → Founder at MiniCoding.

Now running an agent matrix across 5 machines: 3 R&D squads (OpenCode / ClaudeCode / CodeX) + 1 marketing squad (OpenClaw), with Hermes as the CEO orchestrating everything. Multiple rounds of Volcano Engine Hermes Agent internal beta testing.

I believe LLM + Harness = Agent. Models and Harnesses evolve together. DeepSeek introduces new model capabilities and cost structures; the next task is turning them into dependable products through verifiable systems engineering.

---

## Get Involved

- **Technical discussion / opportunities**: yuanchenglu001@gmail.com
- **GitHub Issues**: Disagree with an innovation point? Open an Issue with your reasoning chain
- **License**: [CC BY-NC-SA 4.0](LICENSE.md) — non-commercial sharing and adaptation with attribution and share-alike required. See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*This is the entry point for the "LLM + Harness = Agent" series. Each innovation article can be read independently and they interconnect. Start from 01 — they share the same core logic: "separate what can't be lost from what can be compressed."*
