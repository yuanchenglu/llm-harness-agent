# LLM + Harness = Agent

> From model capability to a verifiable Agent system — a theory grounded in practice, source audits, and testable hypotheses

[**简体中文**](README.md) · [**English**](README_en.md)

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
| [DeepSeek Agent Theory Guide](en/theory/theory-guide.md) | A five-layer theory of model, context, tools, orchestration, and evidence |
| [Research Method and Evidence Calibration](en/theory/research-method.md) | What is source-grounded and what remains a hypothesis |
| [DeepSeek API and Prefix Cache Benchmark Harness Plan (Chinese)](zh/blueprint/benchmark-harness-plan.md) | Experiment matrix, gates, and decision branches for the next and only execution task |
| [Product Comparison](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Product boundaries and use cases |

### Core Innovations (standalone deep-dives)

| # | Article | One-liner |
|---|---------|-----------|
| [01](en/innovations/01-agent-immune-system.md) | **Agent Immune System** | Prompt instructions inevitably decay — make the harness self-audit and self-repair |
| [02](en/innovations/02-bidirectional-agent.md) | **Brain Drives the Cerebellum** | From "Harness→LLM" one-way to "LLM⇄Harness" bidirectional flow |
| [03](en/innovations/03-attention-budget.md) | **Attention Budget Management** | Agent degradation may come from context and attention management, not only the model |
| [04](en/innovations/04-kv-cache-prefix.md) | **KV Cache Prefix Injection** | Separate stable constraints from compressible history to reduce loss during compaction |
| [05](en/innovations/05-document-kv-cache.md) | **Document KV Cache Optimization** | Apply the agent's internal optimization to its own document output |
| [06](en/innovations/06-okr-planstep-cascade.md) | **OKR PlanStep + Cascade Correction** | Upgrade flat checklists to directed dependency graphs with auto-cascade |
| [07](en/innovations/07-review-switching.md) | **KV Cache-Driven Review Switching** | Review depth as f(KV Cache, Plan complexity), not a fixed threshold |
| [08](en/innovations/08-scope-creep.md) | **Two-Level Scope Creep Strategy** | Demand creep and technical creep are different diseases — different treatments |
| [09](en/innovations/09-skills-self-evolution.md) | **Skills Self-Evolution** | Crystallize successful patterns into reusable skills to reduce repeated reasoning |
| [10](en/innovations/10-intent-routing.md) | **7+1 Intent→Strategy Routing** | Recognize task intent → auto-match interview depth, review standard, execution mode |
| [11](en/innovations/11-checkpoint-review.md) | **Checkpoint Multi-Round Review** | Use independent snapshots to bound review context instead of replaying full history |
| [12](en/innovations/12-memory-granularity.md) | **Memory Granularity Control** | Stronger memory isn't always better — convergent tasks need it, divergent tasks don't |
| [13](en/innovations/13-byte-stable-prefix-architecture.md) | **Byte-Stable Prefix Architecture** | Don't just cache the system prompt — make the whole agent cache-first |
| [14](en/innovations/14-reasoning-content-stripping.md) | **Reasoning Content Stripping** | Agent should know what NOT to send — every token must justify its existence |
| [15](en/innovations/15-dsml-tool-call-optimization.md) | **DSML Tool-Call Format Optimization** | DeepSeek V4's unique XML-style markup with string="true/false" typed parameters |
| [16](en/innovations/16-quick-instruction-routing.md) | **Quick Instruction Routing** | V4 built-in action/query/authority/domain/title/read_url 6 special-token routing |
| [17](en/innovations/17-reasoning-effort-control.md) | **Reasoning Effort Control** | reasoning_effort max/high/None three-tier, Max mode injects forced deep-reasoning instruction |
| [18](en/innovations/18-latest-reminder-injection.md) | **Latest Reminder Injection** | latest_reminder independent role, injecting time-sensitive info at highest-attention position |

### Product Analysis

| Article | Content |
|------|------|
| [9 Agent Products: Calibrated Comparison](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Calibrated comparison of Hermes / ClaudeCode / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent / CodeWhale + agent matrix division of labor |
| [DeepSeek-Reasonix Deep Analysis](zh/blueprint/03-Agent竞品Harness调研-Agent-Competitor-Harness-Research/7-a-Reasonix-PrefixCache架构深度分析.md) | Source-code level analysis + three-way comparison (Hermes vs CodeWhale) + 9 DeepSeek Prefix Cache optimizations |

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
