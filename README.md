# LLM + Harness = Agent

> Why the "Harness" matters more than the model — 5,000+ hours, 10+ Agent products, 5-machine verification

---

## TL;DR

1. **LLM intelligence is a constant**. Transformer physics means the longer the context, the more diluted the attention. Model improvements are linear. Harness improvements are exponential.
2. **The same DeepSeek V4 performs drastically differently across different harnesses**. I've run it through Hermes, ClaudeCode, OpenCode, Codex, OpenClaw, pi, Cursor, Coze — each exposes different capability boundaries.
3. **I run an agent matrix across 5 machines as my R&D team**. Multiple rounds of Volcano Engine Hermes Agent internal beta testing. This article is systems-level, hands-on output. Not a survey. Not a benchmark. A builder's understanding, earned the hard way.

---

## Core Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   LLM (Inference Engine)         HermesTech (Operating System)│
│   ────────────────────           ────────────────────────────│
│                                                              │
│   Understand intent    ──→       Persistent Memory            │
│   Generate code/text  ──→       Skill Evolution              │
│   Logical reasoning   ──→       Task Scheduling (Kanban)     │
│   Pattern recognition ──→       Cron Automation              │
│                                 Multi-platform Gateway       │
│                                 Sub-agent Orchestration       │
│                                 Context Compaction            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**One sentence**: The model is the CPU. HermesTech is the process scheduler + filesystem + memory manager + network stack. A CPU without an OS is just silicon.

---

## Navigation

### Core Innovations (standalone deep-dives)

| # | Article | One-liner |
|---|---------|-----------|
| [01](innovations/01-agent-immune-system.md) | **Agent Immune System** | Prompt instructions inevitably decay — make the harness self-audit and self-repair |
| [02](innovations/02-bidirectional-agent.md) | **Brain Drives the Cerebellum** | From "Harness→LLM" one-way to "LLM⇄Harness" bidirectional flow |
| [03](innovations/03-attention-budget.md) | **Attention Budget Management** | Agent "getting dumb" isn't a model problem — it's a harness not managing attention |
| [04](innovations/04-kv-cache-prefix.md) | **KV Cache Prefix Injection** | Constraints survive because they were never in the compression zone |
| [05](innovations/05-document-kv-cache.md) | **Document KV Cache Optimization** | Apply the agent's internal optimization to its own document output |
| [06](innovations/06-okr-planstep-cascade.md) | **OKR PlanStep + Cascade Correction** | Upgrade flat checklists to directed dependency graphs with auto-cascade |
| [07](innovations/07-review-switching.md) | **KV Cache-Driven Review Switching** | Review depth as f(KV Cache, Plan complexity), not a fixed threshold |
| [08](innovations/08-scope-creep.md) | **Two-Level Scope Creep Strategy** | Demand creep and technical creep are different diseases — different treatments |
| [09](innovations/09-skills-self-evolution.md) | **Skills Self-Evolution** | Agent auto-crystallizes successes into reusable skills — zero inference tokens next time |
| [10](innovations/10-intent-routing.md) | **7+1 Intent→Strategy Routing** | Recognize task intent → auto-match interview depth, review standard, execution mode |
| [11](innovations/11-checkpoint-review.md) | **Checkpoint Multi-Round Review** | Review context gets smaller round over round, not larger |
| [12](innovations/12-memory-granularity.md) | **Memory Granularity Control** | Stronger memory isn't always better — convergent tasks need it, divergent tasks don't |

### Product Analysis

| Article | Content |
|------|------|
| [8 Agent Products Deep Comparison](comparison.md) | Hands-on comparison of Hermes / ClaudeCode / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent + my agent matrix division of labor |

---

## Why Hermes as the Hub

Not because it's "the best." Because it's the agent platform that combines the most system-level capabilities:

| Capability | Why it matters | Anyone else? |
|------|-----------|:---:|
| **Memory (SQLite)** | Cross-session persistence of preferences and decisions | ❌ Main coding agents (ClaudeCode/OpenCode/Codex/Cursor) — none |
| **Skills Self-Evolution** | Successful patterns auto-crystallize into reusable Skills | ❌ No other platform |
| **Cronjob** | Scheduled automation — daily summaries, periodic checks | ⚠️ OpenClaw has scheduling; Hermes uniquely integrates cron with agent reasoning |
| **Gateway Multi-platform** | Feishu/WeChat/Discord unified entry | ⚠️ OpenClaw is itself a gateway product; Hermes' Gateway is natively integrated with the agent kernel |

These four make Hermes evolve from a "coding tool" into an "Agent Operating System."

---

## About Me

Yuan Chenglu. 10+ years in the DeepinOS open-source community. Product Director at CodingCat → Founder at MiniCoding.

Now running an agent matrix across 5 machines: 3 R&D squads (OpenCode / ClaudeCode / CodeX) + 1 marketing squad (OpenClaw), with Hermes as the CEO orchestrating everything. Multiple rounds of Volcano Engine Hermes Agent internal beta testing.

I believe LLM + Harness = Agent. Engine improvements are linear. Chassis improvements are exponential. DeepSeek built the engine. Now it's time to build the chassis.

---

## Get Involved

- **Technical discussion / opportunities**: yuanchenglu001@gmail.com
- **GitHub Issues**: Disagree with an innovation point? Open an Issue with your reasoning chain
- **License**: [CC BY 4.0](LICENSE.md) — share and adapt freely, attribution required. See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*This is the entry point for the "LLM + Harness = Agent" series. Each innovation article can be read independently and they interconnect. Start from 01 — they share the same core logic: "separate what can't be lost from what can be compressed."*

---

*[阅读简体中文版](README.md)*
