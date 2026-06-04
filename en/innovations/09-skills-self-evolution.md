# Skills Self-Evolution: Let the Agent Grow Its Own Skill Tree

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, “validated” does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-07
> **LLM + Harness = Agent** · Part 9
> **Series**: [LLM + Harness = Agent](../../README.md)
> **Previous**: [08 A Divide-and-Conquer Strategy for Two-Level Scope Creep](08-scope-creep.md)
> **Next**: [10 7+1 Intent → Strategy Auto-Switching](10-intent-routing.md)

---

> **Abstract**: Every time an Agent completes a complex task, it burns through a substantial amount of inference tokens — but the next time it encounters a similar task, none of those tokens are automatically reused. This article proposes the Skills Self-Evolution Loop: after the Agent successfully completes a task, the system automatically proposes crystallizing the reusable execution path into a Skill; the next time a similar scenario arises, the Skill auto-loads and the Agent reuses it directly without re-reasoning. This is Layer 1 of the Token Savings Pyramid (Skill Crystallization) — and Hermes is one of the earlier research subjects in this project to productize this mechanism; other platforms are rapidly adding skills and experience-crystallization capabilities. At its core, this is the "skill conversion" process in humans, mapped onto an Agent: things you do repeatedly should become muscle memory.

---

## 1. Problem Definition

### 1.1 The Phenomenon

You use an Agent to complete a complex task — say, migrating a Python project from `setup.py` to `pyproject.toml`. The Agent takes 12 rounds of conversation, consumes approximately 15K tokens of reasoning context, and ultimately succeeds.

A week later, you need to do the same thing on another project. You open a new session. The Agent starts from scratch — it does not remember how it did it last time, what pitfalls it hit, what verification steps it used. It walks through those same 12 rounds all over again. Another 15K tokens burned from scratch.

This is not a bug in any particular Agent. It is the default behavior of nearly every Agent product: **every conversation starts from zero, and successful experience never auto-accumulates.**

### 1.2 Root Cause

The root cause is not model capability — it is the product architecture's stance on "experience."

Current Agent products handle experience in three patterns:

| Pattern | Representative Products | Essence |
|---------|------------------------|---------|
| **No Memory** | pi agent, Claude Code (default state) | Every session starts from zero. Experience is valid only within the current session; wiped on session end |
| **Passive Memory** | CodeWhale, OpenClaw | The Agent can actively call `remember` to write memories. But *when* and *what* to write depends entirely on the Agent's own judgment — there is no system-level trigger mechanism |
| **Proactive Skill Crystallization** | **Hermes (this approach)** | After a successful task, the system **automatically proposes** crystallizing the execution path into a Skill. It is not "the Agent is allowed to write memories" — it is "the system triggers memory writing" |

The problem with passive Memory is: the Agent rarely calls `remember` on its own initiative during task execution. It is busy reasoning, invoking tools, handling errors — "record the experience" is not on its priority list. By the time the task ends and the session closes, the experience is lost.

### 1.3 Formalization

Let C(T) be the inference tokens the Agent expends on task T. If tasks T₁ and T₂ are of the same type (sharing the same execution pattern), then ideally C(T₂) = 0 — the second execution fully reuses the first execution's experience, with no need to re-reason.

The reality is C(T₂) ≈ C(T₁). Because there is no mechanism to extract T₁'s execution path and save it as a reusable execution unit.

The goal of Skills Self-Evolution: for any set of same-type tasks {T₁, T₂, ..., Tₙ}, make C(Tₙ) → 0, and make total token consumption ΣC(Tᵢ) → C(T₁) (i.e., you only pay for the first reasoning pass).

---

## 2. Existing Approaches and Their Limitations

| Approach | Core Idea | Why It Falls Short |
|----------|-----------|-------------------|
| **User Profile / Memory** | Record user preferences ("I prefer pnpm over npm") | Preferences ≠ execution paths. A preference tells you "what to use," not "how to do it." The full step chain for "migrate setup.py to pyproject.toml" cannot be described as a preference |
| **Prompt Template** | User manually creates a `prompts/` folder with reusable instructions | Depends on manual user maintenance. Every new scenario requires the user to proactively create a template. The vast majority of users will never do this — it's an engineer's mindset, not a product mindset |
| **Workflow (Coze-style)** | Predefined pipelines — if A then B, if C then D | Fixed templates. Breaks the moment the scenario varies. Complex Agent tasks often have unforeseeable variants; Workflow if-else cannot cover them |
| **Claude Code Custom Commands** | User defines custom commands like `/migrate` | Same problem as Prompt Templates — depends on manual user maintenance. The Agent itself discovers reusable patterns but has no path to write them down |
| **OpenSPEC propose→apply→archive** | Auto-archive after requirements are documented | What gets archived is the requirements document, not the execution path. The next time a similar requirement appears, the Agent reasons from scratch again |
| **CodeWhale remember tool** | Agent can call `remember` to write memories | The timing of the call is entirely up to the Agent's judgment. During task execution the Agent won't call it proactively — experience is lost after the task ends |

**The shared defect**: all existing approaches fall into "let the user manually manage experience" or "let the Agent decide for itself when to record." The correct direction is **"the system automatically triggers experience extraction after task completion"** — independent of user action, independent of the Agent's initiative during the task.

---

## 3. Solution Design

### 3.1 Core Mechanism: Complete → Propose → Crystallize → Reuse

The Skills Self-Evolution Loop consists of four phases:

**Phase 1: Completion**

The Agent completes a task. The completion signal can be user confirmation ("well done"), system judgment (all Step statuses are `done`), or an explicit completion marker.

**Phase 2: Proposal**

The system automatically triggers experience extraction: is there a reusable execution pattern in the just-completed task?

This trigger is not decided by the Agent — it is initiated by the Harness proactively after task completion. The Agent only needs to answer one question: "Is what we just did worth saving as a Skill?"

Specifically, the Agent checks three conditions:

1. **Repeatability**: is this task type's execution pattern likely to be reusable in future projects/scenarios?
2. **Complexity**: does the execution involve more than 3 steps? Tasks with fewer than 3 steps don't need crystallization — the reasoning cost is lower than the Skill management cost.
3. **Determinism**: are the execution steps deterministic (input → output predictable), rather than requiring heavy situational judgment?

If all three conditions are satisfied, the Agent outputs a Skill draft:

```markdown
# Skill: python-migrate-setup-to-pyproject

## Trigger Conditions
- User asks to migrate a Python project from setup.py to pyproject.toml
- Or the system detects setup.py is present but pyproject.toml is absent

## Execution Steps
1. Read setup.py, extract project metadata (name, version, dependencies, entry points)
2. Read requirements.txt (if present), merge dependency lists
3. Generate pyproject.toml (using setuptools as build-backend)
4. Validate: run `python -c "import tomllib; ..."` to confirm TOML format is correct
5. Validate: run `pip install -e .` to confirm the project is installable
6. Ask the user whether to delete the old setup.py / requirements.txt

## Notes
- If setup.py contains custom build logic (non-standard setuptools), evaluate before migrating
- If the project uses C extensions, additional build configuration handling is required
```

**Phase 3: Crystallization**

The Skill draft proposed by the Agent requires user confirmation. This is not a trust issue — it is because Skills have persistent impact. An erroneous Skill would auto-load in all future matching scenarios, causing systemic damage.

Once the user confirms, the Skill is written to the filesystem under the `skills/` directory. The Skill format is structured Markdown — readable and executable by the Agent, and readable and editable by humans.

**Phase 4: Reuse**

The crystallized Skill enters the Skill registry. From then on, whenever any Agent executes a task, the system matches relevant Skills before the task begins:

```
Task: "Migrate this project's setup.py to pyproject.toml"
  → Match found: Skill python-migrate-setup-to-pyproject
  → Load Skill execution steps into context
  → Agent skips "figure out how to do it" and goes straight to "execute by the list"
  → Inference token savings: 15K → ~3K (approximately 80% reduction)
```

### 3.2 Key Design Decisions

**Why require user confirmation instead of auto-crystallizing?**

Skills have system-level impact — a crystallized Skill auto-loads in all matching scenarios. A misconfigured Skill (e.g., wrong verification steps) causes systemic damage. User confirmation is the safety valve.

But this does not mean "the user needs to manually manage Skills." The user only needs to confirm or reject — they do not need to write, modify, or maintain Skill content. The Agent handles generation and maintenance; the user handles approval.

**Why Markdown instead of code for Skill format?**

Code (Python/TypeScript) would offer better determinism, but has two fatal problems:

1. **Agent-generated code is untrustworthy** — LLM-generated code has bugs as a norm. Registering buggy code as a system-level Skill makes the risk uncontrollable.
2. **Users cannot read or modify it** — most users are not programmers. Markdown format lets users understand what a Skill does and manually adjust it when needed.

Markdown Skills are parsed and executed by the Agent (the Agent reads the step list from the Markdown and executes in order). It is not "a prompt for the Agent" — it is "the Agent's execution checklist."

**What is the difference between Skill and Memory?**

|  | Memory | Skill |
|--|--------|-------|
| **Granularity** | Preferences/facts ("prefers pnpm", "project deployed on Vercel") | Execution paths ("complete step chain for migrating setup.py") |
| **Trigger** | Auto-loaded into system prompt every conversation | Loaded only when a same-type task is matched |
| **Token Cost** | Fixed (loaded every conversation) | On-demand (loaded only on match) |
| **Use Case** | Cross-task preferences and constraints | Execution patterns for specific task types |

Memory answers "who you are / what you like"; Skill answers "how to do this thing." The two are complementary, not substitutes.

### 3.3 Relationship with the "Agent Immune System"

Skills Self-Evolution is **positive learning** — extracting experience from successful tasks. The Agent Immune System (I-13) is **negative correction** — generating check Skills from constraint violations. Both share the same Skill storage and execution engine; the difference lies only in the trigger event:

```
Positive Learning (this article): Task succeeds → extract approach → crystallize as Skill
Negative Correction (I-13):        Constraint forgotten → review discovers → crystallize as Skill

Both share the same Skill registry and execution engine
Together → a complete self-evolution system:
  - What was done right, remember how (this article)
  - What was done wrong, remember how to check (I-13)
```

This is why the WRITING-PLAN says I-07 and I-13 are "complementary." A gap in either direction is a systemic blind spot — positive learning alone means repeating the same mistakes after failures; negative correction alone means wasting the experience accumulated from every successful task.

---

## 4. Analysis

### 4.1 The Token Savings Pyramid

Skill Crystallization is Layer 1 of the Token Savings Pyramid — and the most foundational layer:

```
Layer 3: KV Cache Prefix Injection (I-06)
  │  Hard constraints are placed in the non-compressible zone; every hit has token cost ≈ 0
  │
Layer 2: Document KV Cache Optimized Structure (I-05)
  │  Stable content first, variable content last; KV Cache hit rate > 95%
  │
Layer 1: Skills Self-Evolution Crystallization (I-07) ★ This Article
  │  Successful experience auto-crystallizes into Skills; direct reuse next time
  │
Foundation: Attention Budget Management (I-10)
    Manages what the model "can pay attention to," maximizing the effect of the three layers above
```

Each layer addresses a different source of token consumption:
- **Foundation** (Attention Budget): reduces attention consumed by "things that shouldn't be noticed"
- **Layer 1** (Skills): reduces tokens spent re-reasoning about "things already learned"
- **Layer 2** (Document Structure): reduces tokens wasted "re-reading documents"
- **Layer 3** (Prefix Injection): reduces tokens spent "repeatedly loading constraints"

The four layers work in concert, converging the Agent's token consumption from "re-reasoning from scratch every time" to "pay only for the first learning pass + execution overhead."

### 4.2 Why Hermes Is a Useful Early Implementation to Study

Skills Self-Evolution requires two prerequisites:

1. **Skill system infrastructure**: Skill registry, matching engine, loading mechanism, execution engine. These cannot be solved by "adding a feature" — they require system-level architectural support.
2. **Post-task trigger mechanism**: The Harness must proactively initiate experience extraction after the Agent completes a task. This is not something the Agent can do on its own — during task execution the Agent is not thinking "should I save this experience."

Other Agent products are missing one or both prerequisites:

| Product | Skill Infrastructure | Post-Task Trigger |
|---------|:---:|:---:|
| **Hermes** | ✅ Complete Skills system | ✅ Auto-proposes saving |
| **CodeWhale** | ⚠️ Skills directory exists, but Agent has READ-only permission (no write/save) | ❌ |
| **Claude Code** | ❌ No Skill system | ❌ |
| **OpenCode** | ❌ No built-in Skill system | ❌ |
| **Cursor** | ❌ No Skill system | ❌ |

CodeWhale's case is especially telling: it has a `skills/` directory, a `skill_view` tool, and even a Skill loading mechanism. But the Agent can only *read* Skills — there is no tool to *write or create* Skills. This means Skills depend entirely on manual user creation. The Skill infrastructure exists, but the final step of self-evolution was never taken.

### 4.3 Boundary Conditions

The following scenarios are **not** covered by Skills Self-Evolution:

- **One-off tasks**: tasks executed only once, unlikely to recur. The management cost of extracting a Skill exceeds the benefit. However, the system cannot predict "will this task appear again" — that is the user's judgment, not the system's. Hence the proposal phase requires user confirmation.
- **High-context-dependency tasks**: tasks whose execution path strongly depends on the current context (e.g., "fix this specific bug report"). A generalized Skill may become too vague, actually reducing efficiency.
- **Rapidly evolving task types**: toolchains or frameworks in rapid flux (e.g., "migrate to Next.js 16" — three months later the migration path for Next.js 17 may be entirely different). Skills have limited validity windows and need expiration mechanisms.
- **Skill conflicts**: two Skills with overlapping trigger conditions (e.g., `python-migrate-setup-to-pyproject` and `python-migrate-setup-to-poetry` both matching). This requires a priority or user-choice mechanism — currently Hermes resolves this through precise matching of Skill descriptions, but edge cases can still arise.

---

## 5. Validation Path

### 5.1 Confirmed Mechanism and Personal Observation

- **Mechanism existence**: Hermes Agent's Skills system has implemented the full closed loop: task complete → propose saving → user confirms → Skill crystallized → loaded next time. This is the infrastructure for the positive learning path.
- **Token savings effect**: taking "write a WeChat public account article" as an example, the crystallized `article-workflow-v2` Skill reduced task-startup reasoning tokens from ~3K to ~200 (a single description entry in the Skill list). Step selection during task execution no longer requires reasoning from scratch — follow the Skill checklist.
- **Cross-session reuse**: Skills files are persisted in the `skills/` directory. When a new session starts, the Skill list is automatically injected into the system prompt — no manual import by the user is needed.

### 5.2 To Be Validated

- **Skill proposal precision**: the accuracy of the Agent's "worth saving" judgment when proposing Skills after task completion. False positives (proposing to save content not worth crystallizing) increase the user's confirmation burden; false negatives (failing to propose what should be saved) lose experience.
- **Skill matching recall**: the probability of matching the correct Skill when a same-type task reappears. Overly loose matching loads irrelevant Skill noise; overly strict matching misses relevant Skills.
- **Skill expiration detection**: how long a crystallized Skill remains valid. Toolchain and framework evolution will render some Skill steps outdated — a detection mechanism is needed.
- **Combined effect with negative correction (I-13)**: Skill coverage and token savings when positive learning + negative correction run together, vs. positive learning alone.

---

## 6. Relationship with Hermes

Hermes combines skill crystallization with Memory, Cronjob, and Gateway capabilities in one long-running Agent system. Whether automatically extracted skills consistently improve quality still requires longitudinal evaluation.

Current implementation status:

- ✅ Positive learning path is complete — task complete → propose → crystallize → reuse
- ✅ Skill on-demand loading — Skill content does not bloat the system prompt; loaded only on match
- ❌ Missing negative correction — constraint violations do not trigger Skill generation (this is the problem I-13 will solve)
- ❌ Missing Skill expiration/conflict detection

Next steps:

1. **Lightest weight**: add Skill usage statistics (which Skills were loaded how many times, which Skills were never triggered). Let users clean up stale Skills.
2. **Medium effort**: add Skill conflict detection — when two Skills have overlapping trigger conditions, alert the user to choose priority.
3. **Deep integration**: merge with I-13 (Agent Immune System) into a complete self-evolution engine — positive learning + negative correction sharing the same Skill registry and execution engine.

---

## Conclusion

Agent evolution should not be "user manual configuration" or "developer code extensions" — it should be like a human: do something enough times and you naturally learn it; do it wrong and you reflect. The Skills Self-Evolution Loop is the first piece of this native Agent evolution capability: **things you do repeatedly should become muscle memory.**

This is what "self-evolution" truly means: not model upgrades, not prompt optimization — it is the Agent automatically growing new skill nodes from every successful execution. Every leaf comes from real usage; every path has walked verified steps. The skill tree is not designed — it is grown.

---

*Previous: [08 A Divide-and-Conquer Strategy for Two-Level Scope Creep](08-scope-creep.md) — Why demand creep and technical creep must be governed separately. Next: [10 7+1 Intent → Strategy Auto-Switching](10-intent-routing.md) — Different task intents require the Agent to automatically switch between different planning strategies.*
