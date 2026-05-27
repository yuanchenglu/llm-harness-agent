# 8 Agent Products Deep Comparison

> Not a benchmark. Not a feature checklist. This is what a builder understands after pushing every product to its limits.

---

## One-Sentence Summary

| Product | In One Sentence |
|---------|-----------------|
| **Hermes** | The most systemically complete Agent — Memory + Skills + Cron + Gateway |
| **Claude Code** | King of long-running tasks — nobody beats its context compression, but the ecosystem is closed |
| **OpenCode** | Most flexible orchestration — the most open plugin ecosystem, but long-task stability is weak |
| **Codex** | OpenAI's first-party son — full native toolchain; bridge mode is the lifeline for domestic models |
| **OpenClaw** | Weak Memory is actually a feature — the best vehicle for blank-slate innovation |
| **Cursor** | The best AI editor — but it's an editor, not an Agent |
| **Coze** | The best Workflow platform — but it is not an Agent; there's no autonomous Planning |
| **pi agent** | Session Tree is revolutionary — but no Memory/Cron; it's not a complete product |
| **CodeWhale** | Open-source project (DeepSeek-TUI) — I validated DeepSeek KV Cache advantages in Agent scenarios on it |

---

## Deep Dive Per Product

### Hermes Agent

**How I use it**: CEO + CTO, managing 3 R&D squads + 1 marketing & operations squad. Participated in multiple rounds of Volcengine Hermes Agent internal beta testing.

**Core strengths**:

1. **Memory (three-layer system)**
   - SQLite persistence: remembers user preferences, project structure, and key decisions across sessions
   - Skills system: successful experiences auto-solidified into Skills, loaded automatically next time
   - Session context: short-term memory within the current conversation

   No other Agent has this. Claude Code and OpenCode start every conversation from zero.

2. **Self-evolving Skills**
   After completing a complex task, the Agent can propose "save what we just did as a Skill." Next time a similar scenario comes up, the Skill loads automatically — no need to burn inference tokens on repetition. This is the first layer of the token-saving pyramid.

3. **Cronjob**
   One of the few agents supporting scheduled tasks. My "daily conversation summary" and "group chat log summary" are two cronjobs that run automatically every day. OpenClaw also has scheduling, but Hermes' cron is deeply integrated with the agent reasoning pipeline.

4. **Gateway — multi-platform bridging**
   The same Agent can interact via Feishu, WeChat, Discord, and other platforms. This means my Agent matrix isn't just a "command-line tool" — it's a "portable R&D team" I can give instructions to from my phone on Feishu at any moment.

**Core weaknesses**:

1. **Plan is a flat structure**
   PlanStep only has `text` + `status`. No `parent_id`, no `dependency_ids`, no `association_strength`. Change the requirements on step 3, and steps 4–7 don't cascade-correct automatically.

2. **Cross-session memory continuity has a bottleneck**
   Despite SQLite-persisted Memory, in practice the quality of cross-session memory recovery is inconsistent. The longer the gap between sessions, the worse the memory recovery.

3. **Skills self-evolution is positive-only learning**
   Hermes Skills follow a "success → solidify" positive learning loop. But there's no "failure → self-diagnose → solidify" negative correction loop. The Agent learns "the right way to do it" but doesn't learn from doing things wrong.

**My counter-strategies**:
- Convergent tasks (R&D orchestration, bug fixes, code review) → Hermes, leveraging Memory persistence
- On every session restart, inject critical context (project structure, current branch, in-progress tasks)

---

### Claude Code

**How I use it**: Squad Two's core R&D engine, responsible for long tasks and complex refactors

**Core strengths**:

1. **Context compression — strongest in the industry, period**
   Claude Code's compaction system dominates long-conversation stability. Segmented summarization + split-turn processing + cumulative file tracking — this three-layer compression lets it stay accurate through 30+ turns of conversation.

   Compared to Hermes's simple compression, Claude Code is an order of magnitude better at preserving semantic integrity.

2. **Long-task stability**
   This is what I trust most about Claude Code. I can hand it a task that needs 2–3 hours of sustained execution (refactoring a feature across 10 files) without worrying about context rot derailing it halfway through.

**Core weaknesses**:

1. **No multi-model orchestration**
   Claude-series models only. With DeepSeek V4 now available, Claude Code's "only Claude" constraint has become a liability. The KV Cache cost advantage is completely off the table.

2. **Plugin system is closed**
   Superpowers (the community's "multi-agent orchestration plugin") is powerful, but architecturally closed. You can only operate within its defined framework — no custom extensions.

3. **No Memory**
   Every conversation starts from zero. The project conventions, file structures, and personal preferences you taught it last round — all gone.

4. **OAuth authorization requires manual patching**
   Claude Code's GitHub integration needs OAuth, but its authorization flow is incomplete. I had to patch it myself.

**My counter-strategies**:
- Tasks needing sustained context → Claude Code (it has the best compression)
- Tasks needing cross-session memory → Hermes (it has Memory)
- After coding, switch to Hermes for review (use Skills for final compliance checks)

---

### OpenCode

**How I use it**: Squad One's core R&D engine, heavy daily use

**Core strengths**:

1. **Most flexible tool orchestration**
   OpenCode's tool-call mechanism is the most flexible among all Agents. It supports custom tools, custom agent roles, and custom review rules. An order of magnitude more open than Claude Code's closed toolchain.

2. **OMO (Oh My OpenAgent) plugin**
   59K+ Stars, community-driven. The 7+1 intent classification (Refactor / New / Moderate / Collaboration / Architecture / Research / Simple + Spec-Driven) is the industry's most complete intent → strategy auto-switching system.

3. **OpenSPEC's document-driven approach beats Superpowers**
   OpenSPEC's `propose → apply → archive` workflow makes requirement documentation and execution tracking extremely clear.

**Core weaknesses**:

1. **No native DeepSeek KV Cache optimization**
   OpenCode's context management was designed for GPT/Claude (tokens are expensive → aggressive compression). DeepSeek's KV Cache cost advantage goes to waste.

2. **Review mechanism doesn't adapt to context state**
   OMO's Momus review Agent uses a fixed "approve at 80% clarity" strategy. Review quality tanks when context balloons, but it won't auto-switch modes.

3. **Multi-model orchestration still needs manual config**
   There's model routing, but switching models requires manual config changes — no automatic optimal-model selection by task type.

**My counter-strategies**:
- Squad One runs OpenCode + OMO, using OMO's intent classification for task dispatch
- Squad Two runs Claude Code for complex refactors needing ultra-long context
- Both squads back each other up — OpenCode goes down, switch to Claude Code, and vice versa

---

### Codex (OpenAI)

**How I use it**: Squad Three R&D, running domestic models via bridge

**Core strengths**:

1. **OpenAI-native toolchain**
   Deeply integrated with the GPT model family. If you're all-in on OpenAI, Codex offers the best native experience.

2. **Bridge mode supports domestic models**
   Via bridge, you can connect GLM, DeepSeek, and other domestic models. Not native support, but it runs.

**Core weaknesses**:

1. **Weak support for non-OpenAI models**
   Stability drops noticeably through bridge. Tool-call accuracy and context management quality aren't on par with native OpenAI.

2. **Toolchain ecosystem is still early-stage**
   Compared to OpenCode's OMO (59K Stars) and Claude Code's Superpowers (34K Stars), Codex's plugin ecosystem is very immature.

**My counter-strategies**:
- Squad Three is the "experiment group" — testing domestic model performance in Agent scenarios
- No mission-critical tasks through Squad Three — experimental and low-risk tasks only

---

### OpenClaw

**How I use it**: CMO, responsible for marketing operations and content creation

**Core strengths**:

**Weak Memory is actually an advantage.** This is a feature I deliberately exploit.

Hermes's Memory gets to know me better and better — but it also gets more and more "like me." Its creative suggestions get boxed in by my historical preferences. OpenClaw has no strong Memory; every conversation is close to a "clean slate" — which is precisely the ideal environment for creativity. Unshackled from historical preferences, it can explore genuinely new directions.

OpenClaw also excels as a pure orchestrator + messaging hub — it can distribute messages to different platforms and trigger different workflows.

**Core weaknesses**:

1. **Long tasks are basically unusable**
   Context management is OpenClaw's weakest link. Without Claude Code-level auto-compression, conversations beyond ~15 turns reliably go off the rails.

**My counter-strategies**:
- Divergent tasks (marketing ideas, content strategy) → OpenClaw, leveraging blank-slate innovation
- Convergent tasks (R&D orchestration) → Hermes, leveraging Memory persistence
- OpenClaw only does creative proposals, not execution — all execution goes through Hermes's Kanban Worker

---

### Cursor

**How I use it**: Early-stage AI coding entry point. Already migrated to the Agent workflow.

**Core strengths**:

**Highest Tab-completion precision.** In code editing scenarios, Cursor's inline completion experience is the best of all products. Its context awareness has the finest granularity (local context around the edit position, not the conversation window).

**Core weaknesses**:

**No Agent-level autonomous decision-making.** Cursor is an "AI-assisted editor," not an "Agent." It can write your next line of code, but it can't decompose a requirement, assign sub-tasks, or review execution results.

The leap from "AI assistance" to "Agent autonomy" — Cursor can't make it. This leap triggered my Harness thinking: when Tab completion is already good enough, the next problem to solve isn't "make completion more accurate" but "turn completion into planning."

**My counter-strategies**:
- Fully migrated from Cursor to the Hermes/OpenCode/ClaudeCode Agent matrix
- Cursor's philosophy is retained — the local-context-awareness design concept is adopted in our Agent approach

---

### Coze

**How I use it**: Heavy user since early 2024, built 100+ workflows

**Core strengths**:

1. **Workflow orchestration + plugin ecosystem**
   Visual flow orchestration is Coze's strongest suit. For deterministic, template-able tasks (web scraping → data processing → formatted output), Coze's Workflow is actually more suitable than an Agent.

2. **Low barrier to entry**
   No coding required — drag and drop to build workflows. This is a major direction for AI application democratization.

**Core weaknesses**:

**Coze is not an Agent.** This is the essential distinction.

A Workflow is a predefined pipeline — if A then B, if C then D. An Agent makes autonomous decisions — dynamically planning the next step based on current state.

Coze has no autonomous Planning: it won't say "this task is more complex than I anticipated, I need to break it into more steps." It has no Error Recovery: one step fails, the entire workflow halts. It has no Context Awareness: each step only knows its own inputs and outputs, not *why* the previous step made that decision.

**What I learned from Coze**: The essential difference between Workflow and Agent — not "a difference in capability magnitude" but "a difference in decision authority." Every step in a Workflow is pre-set; every step in an Agent is a decision.

---

### pi agent

**How I use it**: A learning target — I study its architectural design, not for production use

**Core strengths**:

1. **Session Tree (in-file branching) — revolutionary design**
   In a single JSONL file, uses `id` + `parentId` to build a tree structure. You can backtrack to any historical point and continue the conversation. This is a capability Hermes, ClaudeCode, OpenCode, and Codex all lack. Imagine applying Git's branch concept to conversations — at turn 5, you can "fork" into two different conversation paths that are mutually independent yet both retain full context.

2. **Compaction system — the most granular segmented summarization**
   Not one-shot compression of the entire context, but compression segmented by topic and time period, with cumulative file tracking. In preserving semantic integrity, pi's compaction is the most granular among all Agents.

3. **Extension API — the richest in the industry**
   2,596 lines of documentation, covering everything from tool registration to TUI component rendering to event interception to state persistence. This is the engineering realization of the "minimal kernel + plugins do everything" philosophy.

4. **Exceptionally high code quality**
   617 `.ts` files, zero `any` types. Armin Ronacher (creator of Flask + Jinja2) is behind it. Engineering-grade craftsmanship.

**Core weaknesses**:

1. **No Memory** — cross-session starts from zero
2. **No Cron** — cannot run scheduled tasks
3. **No sub-agents** — cannot `delegate_task`
4. **No multi-platform access** — terminal only

pi is a "proof-of-concept-level" product — it achieves the absolute maximum in conversation management and extensibility, but it's not a "complete product." You need to build your own Memory, write your own Cron, and do your own sub-agent orchestration.

**What it taught me**: Session Tree is the design Hermes should learn from most. If Hermes could support "topic branching" within a session, it would elevate long-conversation management by an order of magnitude.

---

### CodeWhale (Open-source, by DeepSeek Official)

**How I use it**: An experimental platform for studying how DeepSeek models actually perform in Agent scenarios

**Background**: CodeWhale is DeepSeek's official open-source Coding Agent (formerly DeepSeek-TUI). I didn't participate in its development, but I use it deeply to validate DeepSeek model performance under Agent architecture — because it runs directly on the DeepSeek API, unlike OpenCode/ClaudeCode which are shaped by overseas-model assumptions.

**Core findings**:

1. **DeepSeek KV Cache long-session stability confirmed**
   Running multi-agent orchestration on CodeWhale, I found: DeepSeek's stability in long contexts exceeds both Claude and GPT. This isn't because the model is "smarter" — it's because KV Cache is cheaper → no need for aggressive compression → better semantic preservation.

2. **KV Cache prefix injection feasibility confirmed**
   I ran hard-constraint prefix injection prototypes on CodeWhale. Result: with constraint injection prefix, constraint retention after 15 turns > 95% (vs. ~40% without injection). This validates the feasibility of innovation point I-06.

3. **Existing Harness tools share a systemic blind spot**
   OpenCode, ClaudeCode, Cursor — these Harness tools were all designed for overseas models. They assume tokens are expensive, so they compress aggressively. They don't leverage DeepSeek's KV Cache advantage. That's why we need a native, DeepSeek-optimized Harness.

---

## My Agent Matrix Division

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  CEO (Hermes) — Orchestration Hub                            │
│  ├── Task decomposition → Kanban                            │
│  ├── Sub-agent assignment → delegate_task                   │
│  ├── Scheduled automation → cronjob                         │
│  └── Persistent memory → Memory (SQLite)                    │
│                                                             │
│  Squad One (OpenCode + OMO) — Core R&D                      │
│  ├── Plugin development                                      │
│  ├── Code review (Momus)                                     │
│  └── Spec documentation (OpenSPEC)                          │
│                                                             │
│  Squad Two (Claude Code) — Complex Refactors                │
│  ├── Large cross-file refactors                             │
│  ├── Long-context tasks (30+ turns)                          │
│  └── Post-compression review                                 │
│                                                             │
│  Squad Three (CodeX + bridge) — Domestic Model Experiments  │
│  ├── GLM/DeepSeek bridge testing                            │
│  └── Low-risk task validation                                │
│                                                             │
│  CMO (OpenClaw) — Marketing Operations                      │
│  ├── Marketing creativity (blank-slate innovation)           │
│  └── Content strategy                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Two Agent Philosophies

The contrast between these two philosophies is more valuable than any single-product comparison:

```
pi philosophy (Linux kernel)        Hermes philosophy (macOS)
─────────────────────────           ─────────────────────────
Minimal kernel + plugins do all     Self-contained all-in-one
4 built-in tools                    20+ built-in tools
Extension API for extensibility     Skills for extensibility
No Memory / Cron / Gateway          Memory + Cron + Gateway
Session Tree branching              Linear sessions
For: those willing to build         For: those who need it
     their own toolchain                 working out of the box
```

**There is no right answer.** pi's Extension API depth is something Hermes should learn from; Hermes's Memory + Cron combo is a moat pi doesn't have. The best Agent platform probably sits somewhere between the two — a stable kernel with a programmable periphery.

---

## Selection Guide (If I Were Starting Over)

| Your Scenario | Pick | Why |
|---------------|------|-----|
| Need cross-session memory | Hermes | Only one with SQLite Memory |
| Need scheduled automation | Hermes | Only one with cronjob |
| Need multi-platform access | Hermes | Gateway supports Feishu/WeChat/Discord |
| Need ultra-long conversation stability | Claude Code | Strongest context compression |
| Need flexible tool orchestration | OpenCode | Most open toolchain |
| OpenAI-only stack | Codex | Best native integration |
| Creative / marketing work | OpenClaw | Weak Memory = blank-slate innovation |
| Studying Agent architecture | pi agent | Session Tree is worth learning |
| Fixed template tasks | Coze | Workflow suits you better than Agent |

---

*"Coze is not an Agent" — that's my core conclusion after 100+ workflows. The difference between Workflow and Agent isn't capability magnitude. It's about who holds the decision authority.*
