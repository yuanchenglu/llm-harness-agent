# LLM + Harness = Agent: A First-Principles Framework for Agent Operating Systems

> **Part draft paper, part builder's field notes.**
> 5,000+ hours · 10+ Agent products · 5-machine agent matrix · Multiple rounds of Volcano Engine Hermes beta

---

> **Abstract**: The dominant approach to AI agents is "wait for the next model" — bigger context windows, stronger reasoning, better instruction following. This paper argues that approach is a dead end: Transformer soft-attention physics means the longer the context, the lower the attention weight on each instruction. This is a hard constraint, not a capability gap. The real breakthrough is in the harness — an operating system running outside the model that manages persistent memory, crystallized skills, long-running scheduling, and multi-platform orchestration. This paper proposes a four-layer agent OS architecture, groups 12 battle-tested design patterns under four first-principles-derived design rules, and provides empirical backing from a 5-machine agent matrix and 8-product comparison. Core thesis: model improvements are linear; harness improvements are exponential.

---

## 1. Introduction: Why Harness Matters More Than Model

### 1.1 A Counterintuitive Finding

In 2025, I ran an agent matrix across five machines — three R&D squads (OpenCode, ClaudeCode, CodeX) plus one marketing squad (OpenClaw), with Hermes as CEO orchestrating everything. All agents used the same underlying model: DeepSeek V4.

Same model. Radically different performance across harnesses.

- **Claude Code**: Unmatched long-task stability, but closed ecosystem, proprietary models only
- **OpenCode**: Most open plugin ecosystem, but starts "forgetting" around round 8
- **Codex**: OpenAI-native toolchain, but context management suffers when bridging to Chinese models
- **Hermes**: Memory (SQLite) + Skills (self-evolving) + Cron (scheduling) + Gateway (multi-platform) — evolved from "coding tool" to "agent operating system"

Same DeepSeek V4. ClaudeCode can run 30 rounds without losing logic. OpenCode starts reinventing the wheel by round 15. **The model didn't change. The harness's context scheduling strategy did.**

### 1.2 Root Cause: The Physics of Attention

Transformer self-attention is O(n²). When sequence length L grows from 2K to 128K, attention weight on any single system instruction is diluted by ~64×. A 1M context window only delays this dilution from round 15 to round 50 — the problem is the same, just arrives later.

Formally: given n behavioral constraints C = {c₁, c₂, ..., cₙ} and sequence length L(t) after t rounds, attention weight αᵢ(t) ∝ 1/L(t). As L(t) → ∞, αᵢ(t) → 0. **This is a monotonic decreasing function with no inflection point.**

What does this mean? "Make models stronger" has diminishing returns. GPT-5 follows instructions 20% better than GPT-4 — but if your agent runs 100 rounds, that 20% gets diluted away by round 30.

**The real problem isn't "the model isn't smart enough." It's "the model will inevitably forget in long conversations." This isn't a bug. It's the physics of Transformer attention.**

### 1.3 Defining Harness

A harness is system software running outside the LLM that manages:

1. **What enters the context window** (Memory selection, Skill injection, compaction strategy)
2. **What persists outside the context** (Memory SQLite, Skill files, Plan state)
3. **When to execute what** (Cron scheduling, Kanban decomposition, sub-agent orchestration)
4. **How to interact with the world** (Gateway multi-platform bridging, tool execution, browser control)

**One sentence: The model is the CPU. The harness is the process scheduler + filesystem + memory manager + network stack. A CPU without an OS is just silicon.**

---

## 2. The Four-Layer Harness Architecture

A complete agent OS requires four layers. Each solves a fundamental problem the model itself cannot.

```
┌─────────────────────────────────────────────────────────┐
│                     Gateway Layer                        │
│   Feishu / WeChat / Discord / X / Telegram / Browser    │
│   "The agent's interface to the world"                  │
├─────────────────────────────────────────────────────────┤
│                     Scheduling Layer                    │
│   Cron timing / Kanban decomposition / delegate sub-agents│
│   "Who does what and when"                              │
├─────────────────────────────────────────────────────────┤
│                     Skills Layer                         │
│   Success crystallization / failure pattern library     │
│   "Lessons learned — don't make the same mistake twice" │
├─────────────────────────────────────────────────────────┤
│                     Memory Layer                         │
│   User preferences / environment / decisions / conventions│
│   "Cross-session knowledge that shouldn't be rediscovered"│
└─────────────────────────────────────────────────────────┘
```

### 2.1 Memory Layer: Cross-Session Persistence

**Core problem**: Every new session, the agent starts from zero. It doesn't know your OS, language preference, or project structure — unless you re-tell it every time.

**Solution**: Memory is a structured SQLite database storing user preferences, environment facts, and project conventions. Auto-injected at session start — no repetition required.

**Key design decision**: Memory is not a log. It doesn't store task progress, "fixed bug X today," or temporary TODOs. Why? Because seven days later, that information is noise. Memory stores only **stable facts** — information that will still be true seven days from now.

This principle maps to [I-12: Memory Granularity Control](../innovations/12-memory-granularity.md) — convergent tasks (need stable context) demand strong memory; divergent tasks (exploratory) demand weak memory.

### 2.2 Skills Layer: Crystallization and Self-Evolution

**Core problem**: After completing a complex task, the agent starts from scratch on the next similar task. Same mistakes can happen again.

**Solution**: Skills are structured operational manuals — executable checklists, command templates, configuration examples — not natural language hints. After completing a task, the agent auto-proposes saving the successful approach as a Skill. Next trigger: Skill injected into context, zero inference tokens.

This is the core of [I-09: Skills Self-Evolution](../innovations/09-skills-self-evolution.md) — the agent doesn't reinvent the wheel; it crystallizes successful patterns.

Complementing this is [I-01: Agent Immune System](../innovations/01-agent-immune-system.md) — positive learning (success → Skill) already exists in Hermes; negative correction (forgetting → self-audit → Skill) is my proposed mechanism: when the system detects a prompt constraint violation, it auto-crystallizes the constraint into a Skill, injected into the execution flow for next time.

### 2.3 Scheduling Layer: From One-Shot to Autonomous

**Core problem**: LLMs are "question-answer" — you ask, it answers. A real agent needs to work when nobody's messaging: aggregate news every morning, check server health every 30 minutes, generate monthly reports on the 1st.

**Solution**: Cron scheduling + Kanban decomposition + delegate sub-agent orchestration.

- **Cron**: Time-triggered agent execution with complex schedules (cron expressions), chained tasks (Task A complete → auto-trigger Task B), and multi-platform delivery
- **Kanban**: Complex task → sub-tasks → dependency-sorted → execute sequentially → cascade correction ([I-06: OKR PlanStep + Cascade](../innovations/06-okr-planstep-cascade.md))
- **delegate_task**: Spawn independent sub-agents for subtasks; main agent receives only summaries — no context window pollution

This layer transforms the agent from "passive responder" to "active executor." An agent that can't schedule its own time is just a chatbot.

### 2.4 Gateway Layer: The World Interface

**Core problem**: The agent runs on a server, but users are on Feishu, WeChat, Discord, email — the agent needs to message, manage files, and control browsers across all platforms, like a real team member.

**Solution**: Gateway unifies multi-platform bridging — same agent receives requests from Feishu, delivers outputs via Discord, and opens GitHub Issues simultaneously. Platform differences are transparent to the agent.

This is the infrastructure for [I-10: 7+1 Intent→Strategy Routing](../innovations/10-intent-routing.md) — the agent recognizes task intent and auto-switches execution strategy. Without Gateway, the agent lives only in the terminal.

---

## 3. Twelve Design Patterns: From First Principles to Engineering

This section groups 12 battle-tested design patterns under four fundamental problems. Each pattern is not an independent idea — they are the same principle unfolding across different dimensions: **separate what cannot be lost from what can be compressed.**

### 3.1 Context Management (Solving Attention Dilution)

Transformer attention dilution is a hard physical constraint. You can't prevent it — you can only manage it. Keep the most critical information at highest attention weight during every inference step.

| # | Design Pattern | Core Method | Problem Solved |
|---|---------------|-------------|----------------|
| I-03 | [Attention Budget Management](../innovations/03-attention-budget.md) | Treat context as finite budget; dynamically allocate quotas by task type | Agent "getting dumb" isn't the model — it's the harness not managing attention |
| I-04 | [KV Cache Prefix Injection](../innovations/04-kv-cache-prefix.md) | Non-losable constraints in the non-compressible prefix zone, not in compressible body | Constraints survive because they were never in the compression zone |
| I-05 | [Document KV Cache Optimization](../innovations/05-document-kv-cache.md) | Apply agent-internal KV Cache optimization to document conventions — meta-level self-reference | Stable content (definitions, structure) before mutable content (progress, dates) |
| I-07 | [KV Cache-Driven Review Switching](../innovations/07-review-switching.md) | Review depth = f(KV Cache occupancy, Plan complexity), not a fixed threshold | When context is tight, deep review is itself interference |
| I-11 | [Checkpoint Multi-Round Review](../innovations/11-checkpoint-review.md) | Round 2 review context is smaller than Round 1 — not growing larger | Each review round only examines the previous round's decision summary |

**Unifying logic**: All five patterns follow one rule — **information has two tiers: non-losable (hard constraints, core decisions) and compressible (execution details, conversation noise). Hard constraints live in the non-compressible zone. Reviews only examine summaries.**

### 3.2 Stability and Correction (Solving Long-Run Drift)

The longer an agent runs, the more it drifts from initial goals. Not because the agent "changed its mind" — because historical baggage makes every decision based on increasingly blurred context.

| # | Design Pattern | Core Method | Problem Solved |
|---|---------------|-------------|----------------|
| I-01 | [Agent Immune System](../innovations/01-agent-immune-system.md) | Independent audit agent checks constraint compliance → violated constraints auto-crystallize as Skills | Prompt forgetting is inevitable — let the system self-detect and repair |
| I-06 | [OKR PlanStep + Cascade](../innovations/06-okr-planstep-cascade.md) | Upgrade flat checklists to directed dependency graphs; change one step, cascade-update downstream | Step 7 reveals Step 2 was wrong — no need to redo Steps 3-6 |
| I-08 | [Two-Level Scope Creep](../innovations/08-scope-creep.md) | Demand creep and technical creep are different diseases — different treatments | Agent inflates scope over time — distinguish "user asked for it" from "it self-inflated" |

**Unifying logic**: Long-running agents need a **correction loop** — not relying on the model "having a good memory," but on the harness performing runtime checks + targeted intervention.

### 3.3 Knowledge Evolution (Solving the "Agent Doesn't Get Better" Problem)

Traditional agents treat each task independently. Yesterday's success doesn't auto-apply to today. Users must remember every pitfall and manually tell the agent.

| # | Design Pattern | Core Method | Problem Solved |
|---|---------------|-------------|----------------|
| I-09 | [Skills Self-Evolution](../innovations/09-skills-self-evolution.md) | Complex task complete → auto-propose saving as Skill → next time: zero inference tokens | Agent doesn't reinvent the wheel every time |
| I-12 | [Memory Granularity Control](../innovations/12-memory-granularity.md) | Stronger memory isn't always better — convergent tasks need it, divergent tasks don't | Remember the wrong things = noise pollution; forget the right things = repeat mistakes |

**Unifying logic**: Agent knowledge management has two dimensions — **what to persist** (Memory layer granularity decisions) and **what to crystallize** (Skills layer pattern extraction). Both share one judgment criterion: will this information still be true seven days from now?

### 3.4 Human-Agent Symbiosis (Solving the Agent-User Relationship)

Traditional agents are "user issues command → agent executes" one-way flow. Real team members don't work like that — teams are bidirectional: you push me, I push you.

| # | Design Pattern | Core Method | Problem Solved |
|---|---------------|-------------|----------------|
| I-02 | [Brain Drives Cerebellum](../innovations/02-bidirectional-agent.md) | From "Harness→LLM" one-way to "LLM⇄Harness" bidirectional flow | LLM isn't just executor — it can actively invoke harness capabilities, initiate Skill saves, adjust Cron strategies |
| I-10 | [7+1 Intent→Strategy Routing](../innovations/10-intent-routing.md) | Recognize message intent → auto-match interview depth, review standard, execution mode | "Take a look at this code" vs "Why is this code so slow" — should use completely different strategies |

**Unifying logic**: Agents shouldn't just be "reactive" — they should be "symbiotic." They perceive task type, proactively drive process, and pull the user in when needed — not wait for commands.

---

## 4. Empirical Basis

### 4.1 5-Machine Agent Matrix: Real-World Validation

My agent matrix isn't a paper architecture — it's running:

| Machine | Role | Agent(s) Running | Model |
|---------|------|-----------------|-------|
| Machine 1 | CEO + CTO | Hermes (central orchestrator) | DeepSeek V4 Pro |
| Machine 2 | R&D Squad 1 | OpenCode + OpenSpec + OMO | DeepSeek V4 Pro |
| Machine 3 | R&D Squad 2 | ClaudeCode + SuperPowers + OMC | Claude Sonnet 4 |
| Machine 4 | R&D Squad 3 | CodeX + OMX (via bridge) | GLM 5.1 |
| Machine 5 | Marketing & Ops | OpenClaw | DeepSeek V4 Flash |

Matrix operation: Hermes receives tasks as central hub → decomposes into subtasks → delegates to squads via delegate_task → each squad executes with optimal harness + model combo → results return to Hermes for aggregation.

Key findings:
- **Same model across different harnesses shows larger performance variance than different models on the same harness.** DeepSeek V4 on Hermes remembers decisions from 3 days ago and applies them to new tasks (Memory layer). On OpenCode, every new session requires full re-alignment.
- **Harness capabilities determine the agent's ceiling for autonomy.** No Cron = no autonomous execution — it sleeps when you sleep. No Skills = no accumulated experience — yesterday's pitfalls are today's pitfalls.
- **Gateway + Scheduling combined transforms agent from "developer tool" to "team member."** Drop a request in Feishu → Hermes decomposes, assigns, executes, pushes results — no terminal needed.

### 4.2 8-Product Comparison

See [8 Agent Products Deep Comparison](../../zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md). Core findings:

| Capability | Hermes-Unique | Partial Competition | Missing in Major Products |
|------------|--------------|---------------------|--------------------------|
| Memory (cross-session) | ✅ SQLite | — | ClaudeCode/OpenCode/Codex/Cursor: none |
| Skills Self-Evolution | ✅ Auto-propose save | — | No other platform |
| Cron Scheduling | ✅ Deep agent reasoning integration | OpenClaw has scheduling | Others: none |
| Gateway Multi-platform | ✅ Native kernel integration | OpenClaw is itself a Gateway | Cursor/Codex: no multi-platform |

**Note**: OpenClaw is fundamentally a Gateway product — its scheduling and multi-platform capabilities are strengths. Hermes' differentiator: Gateway is not an add-on module; it's deeply integrated with the agent reasoning pipeline — Feishu thread context directly enters Memory and intent routing.

### 4.3 Volcano Engine Hermes Beta Insights

Multiple rounds of Volcano Engine Hermes Agent internal beta testing. The most important finding wasn't "where Hermes excels" — it was that **harness iteration speed far exceeds model iteration speed.**

- Model upgrade cycle: 3-6 months (training + alignment + testing)
- Harness iteration cycle: daily — today discover Memory granularity causes noise pollution, tonight adjust config, tomorrow effective
- **Model marginal improvement is decreasing** (Transformer physics ceiling). **Harness improvement space is nearly unbounded** (every interaction detail is an optimization target).

---

## 5. Design Principles

Four universal design principles distilled from the 12 patterns. These apply to any agent system, not just Hermes.

### Principle 1: Separate the Non-Compressible from the Compressible

**Sources**: I-03, I-04, I-05, I-07, I-11

The first principle of context management: don't try to make the model remember more — reduce what the model needs to remember. Split information into two tiers:
- **Hard constraint tier**: Behavioral rules, safety checks, project conventions → lives in KV Cache prefix zone, never compressed
- **Soft context tier**: Execution logs, conversation details, temporary decisions → compressible, but compression strategy adapts to task type

In practice: my Hermes config injects Memory (user preferences, environment) and Skills (verified workflows) into the non-compressible prefix zone. Execution logs and past conversations go to the compressible zone. When compression fires, hard constraints survive untouched.

### Principle 2: The Agent Must Be Active, Not Passive

**Sources**: I-02, I-06, I-10

Traditional HCI is "user-pull" — user issues command, system executes. Agent needs "bidirectional push":
- **System pushes user**: Scheduled reports, anomaly alerts, progress updates (Cron)
- **Agent pushes system**: Auto-save experience (Skills), auto-adjust strategy (intent routing), proactively spawn subtasks (delegate)
- **User pushes agent**: Requirements, feedback, priority adjustments — unchanged

This is "the brain drives the cerebellum." The LLM is not just an executor — it's a decision-maker that can actively invoke any harness capability. This shift transforms the agent from "tool" to "team member."

### Principle 3: Memory Granularity Must Match Task Type

**Sources**: I-09, I-12

Stronger memory isn't always better. Wrong-granularity memory is worse than no memory:

- **Convergent tasks** (fix known bugs, standard ops) → strong memory — depends on stable preferences and conventions
- **Divergent tasks** (explore new architecture, brainstorm) → weak memory — too much historical decisions constrains exploration space
- **Skills vs Memory**: Skills store "how to do it" (workflows — convergent), Memory stores "what is" (facts and preferences — overridable)

In practice: when my Hermes fixes a bug, Memory loads full project structure, user preferences, and coding standards. When architecting a new product, Memory loads only core principles and preferences — no historical decisions from similar projects, avoiding path dependence.

### Principle 4: Self-Evolution Is the Endgame, Not a Bonus

**Sources**: I-01, I-09

An agent that can't get better on its own has no future. Agent self-evolution has two directions:
- **Positive**: Successfully complete complex task → auto-propose Skill save (I-09)
- **Negative**: Detect constraint violation → auto-crystallize as Skill, no longer dependent on model memory (I-01)

Together they form a complete evolution loop: **successful patterns are retained, failure patterns are immunized.** Every Skill born means zero inference tokens forever. The agent's improvement rate depends on its accumulated Skill count — and Skill accumulation auto-accelerates.

---

## 6. Future Directions

### 6.1 What's Next for Harness

**Self-Evolution 2.0**: Current Skills self-evolution is "human review → confirm save." Next step: "auto-trial → auto-evaluate → auto-save," making the Skill library evolve autonomously like an immune system — no human intervention, generating response patterns for novel scenarios.

**Multi-Agent Collaboration**: Currently, each agent in the matrix works independently — Hermes assigns, squads execute, results aggregate. The real breakthrough is **dynamic division of labor**: Agent A gets stuck → auto-spawn Agent B to solve → Agent B's solution auto-saved as Skill shared across all agents.

**Harness-as-a-Service**: Harness shouldn't be bound to any single agent product. The ideal future is standardized harness layer — Memory protocol, Skill format, Gateway interface unified — letting any LLM plug into any harness. Like TCP/IP letting any application run on any network.

### 6.2 Limitations

1. **12 design patterns haven't been validated at scale** — one builder validating in his own scenarios, not an academic experiment
2. **Harness metrics are immature** — no widely accepted metric for "this harness is X% better than that one." This paper uses qualitative judgment + usage experience, not quantitative benchmarks
3. **Gateway multi-platform capabilities validated only on Feishu + Discord + local terminal** — WeChat, Slack, Telegram are theoretical
4. **Self-Evolution 2.0 and dynamic agent division of labor remain at design stage** — no engineering implementation

---

## 7. Conclusion

LLM improvements are linear. Harness improvements are exponential.

Not because harness is "more important" than model — but because Transformer attention has a physics ceiling, and harness has none. Every model version upgrade costs millions in training and 3-6 months. Every harness upgrade could be a config change, effective tomorrow.

**The 12 design patterns are not an endpoint — they're a direction:** from "wait for the next better model" to "build a better operating system on the current model." DeepSeek built the engine. Now it's time to build the chassis.

---

## Innovation Index

| # | Article | Design Principle |
|---|---------|-----------------|
| [I-01](../innovations/01-agent-immune-system.md) | Agent Immune System | P4: Self-Evolution |
| [I-02](../innovations/02-bidirectional-agent.md) | Brain Drives Cerebellum | P2: Active Agent |
| [I-03](../innovations/03-attention-budget.md) | Attention Budget Management | P1: Separate Non-Compressible |
| [I-04](../innovations/04-kv-cache-prefix.md) | KV Cache Prefix Injection | P1: Separate Non-Compressible |
| [I-05](../innovations/05-document-kv-cache.md) | Document KV Cache Optimization | P1: Separate Non-Compressible |
| [I-06](../innovations/06-okr-planstep-cascade.md) | OKR PlanStep + Cascade | P2: Active Agent |
| [I-07](../innovations/07-review-switching.md) | KV Cache-Driven Review Switching | P1: Separate Non-Compressible |
| [I-08](../innovations/08-scope-creep.md) | Two-Level Scope Creep | P2: Active Agent |
| [I-09](../innovations/09-skills-self-evolution.md) | Skills Self-Evolution | P4: Self-Evolution |
| [I-10](../innovations/10-intent-routing.md) | 7+1 Intent→Strategy Routing | P2: Active Agent |
| [I-11](../innovations/11-checkpoint-review.md) | Checkpoint Multi-Round Review | P1: Separate Non-Compressible |
| [I-12](../innovations/12-memory-granularity.md) | Memory Granularity Control | P3: Granularity Match |

---

*This is the framework paper for the "LLM + Harness = Agent" series. Innovation articles are independent case studies; this paper is the unifying theory. License: [CC BY 4.0](../../LICENSE.md).*

*Next: Prototype validation of the 12 design patterns is underway — not proof-of-concept, but engineering implementation.*

---

*Contact: yuanchenglu001@gmail.com · [GitHub](https://github.com/yuanchenglu) · [X](https://x.com/yuanchenglu)*
