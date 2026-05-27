# 7+1 Intent→Strategy Automatic Switching

> **Innovation Index**：I-08
> **LLM + Harness = Agent** · Part 10
> **Series**：[LLM + Harness = Agent](../README-EN.md)
> **Previous**：[09 Skills Self-Evolution Loop](09-skills-self-evolution.md)
> **Next**：[11 Checkpoint Snapshot-Driven Multi-Round Review](11-checkpoint-review.md)

---

> **Abstract**: Every Agent, upon receiving a task, generates a plan using the same pattern — ask for requirements, decompose into steps, assign priorities. But "refactor a legacy module" and "build a new project from scratch" do not need the same interview strategy, nor the same review standard. OMO has already implemented a 7+1 intent taxonomy at the code level (refactor / new / medium / collaboration / architecture / research / simple + Spec-Driven), with each intent bound to a different interview strategy, review standard, and execution mode — but the documentation only advertises 4. This article fully discloses the 7+1 taxonomy and its strategy binding table, and argues the core value of this mechanism: achieving strategy induction (lower floor — new intents automatically receive reasonable default strategies) and ceiling extension (raise ceiling — Spec-Driven, as the latest evolution, proves the taxonomy's sustainability). This is not about "making the Agent smarter" — it's about "making the system use the right strategy at the right moment."

---

## 1. Problem Definition

### 1.1 The Phenomenon

You use the same Agent to do two things:

**Task A**: "Help me refactor this 2000-line `payment.py`, split it into a few modules." The Agent spends 3 rounds of conversation understanding the existing code structure, then starts refactoring directly — without asking whether backward compatibility needs to be maintained, without confirming the granularity of the split, without discussing testing strategy. Halfway through the refactor, it splits out 5 modules, but `PaymentProcessor` and `RefundHandler` share an internal state they shouldn't share — because it never asked about the contract boundaries between modules.

**Task B**: "Help me build a blog system from scratch." The Agent spends 12 rounds of conversation aligning requirements with you — which framework, database choice, article format, comment system, RSS, SEO, deployment method. Midway through, you're already impatient: "I just want a simple Markdown blog, no comment system or SEO needed."

Both tasks failed, but the failure causes are diametrically opposite — Task A failed because the **strategy was too light** (a refactor needs deep interviews, the Agent skipped them), Task B failed because the **strategy was too heavy** (a simple new project doesn't need 12 rounds of requirements alignment). The same Agent applied the same default strategy to two tasks of fundamentally different natures — a strategy-to-task mismatch.

### 1.2 Root Cause

The root cause lies not in the Agent's capabilities, but in the Agent framework's cognitive absence regarding "task type."

The default behavior of all current Agent products is: user issues a task → Agent begins execution. A critical step is missing in between: **What type is this task? What strategy should be used?**

This omission is not accidental — it's an implicit assumption in Agent design: "A general-purpose Agent should use the same general-purpose process for all tasks." But this assumption ignores a fundamental fact: different task types require completely different interview depth, review rigor, plan granularity, and execution mode. The cost of generality is — inadequate fit for every specific task.

Formalized: Let the Agent's execution strategy space be Σ = {interview strategy, review standard, plan granularity, execution mode}. Under a fixed-strategy model, Σ is constant for all task types T:

$$\Sigma(T) = \Sigma_0 \quad \forall T$$

But the optimal strategy differs across task types:

$$\Sigma^*(T_{\text{refactor}}) \neq \Sigma^*(T_{\text{new}}) \neq \Sigma^*(T_{\text{simple}})$$

The fixed-strategy model outputs Σ₀ for all T, resulting in suboptimal outcomes for all T — only the degree of suboptimality varies.

### 1.3 Formalization

Let the task space T be partitionable into k intent categories {C₁, C₂, ..., C_k}, each category Cᵢ corresponding to its optimal strategy Σᵢ. The Agent's execution quality Q(T, Σ) on task T ∈ Cᵢ is a function of strategy Σ:

$$Q(T, \Sigma) = Q_{\text{base}}(T) - \text{mismatch}(\Sigma^*(C_i), \Sigma)$$

where mismatch(Σ*, Σ) is the strategy mismatch cost. Under a fixed strategy, mismatch > 0 holds for almost all T (unless T happens to fall into the category for which Σ₀ is optimal).

The goal of intent classification: before execution begins, map T to its category Cᵢ and automatically bind strategy Σᵢ, such that:

$$Q(T, \Sigma_i) \approx Q_{\text{base}}(T) \quad \text{(strategy mismatch cost → 0)}$$

Key challenges: (1) Classification must complete before task execution — you can't discover mid-execution that the strategy is wrong; (2) The taxonomy must be extensible — when new task types emerge, the entire classifier shouldn't need a rewrite; (3) New categories must have reasonable default strategies — the system must not degenerate to the generic strategy just because "it's never seen this kind of task before."

---

## 2. Existing Solutions and Their Limitations

| Solution | Core Approach | Why It Fails |
|------|---------|-----------|
| **Fixed Generic Strategy (all Agent defaults)** | All tasks use the same interview→plan→execute→review flow | Strategy-to-task mismatch. Refactors need deep interviews but get skipped, simple tasks get over-interviewed. Users complain about simple tasks: "the Agent asks too much"; about complex tasks: "the Agent didn't ask enough" |
| **User Manual Mode Selection** | Provide a dropdown: Code Review / New Feature / Bug Fix / Refactor | Relies on user judgment. Users don't necessarily know the strategic differences between "refactoring legacy code" and "fixing a bug" — that's precisely the cognitive burden they're using an Agent to avoid. And classification granularity is fixed — users can't define new task types |
| **Strategy Declaration in Prompt ("please review carefully", "just do it quick")** | Users attach strategy expectations in the task description | Natural language is unreliable. "Review carefully" means different things in different tasks — in a refactor, "careful" means checking module contracts; in a new project, "careful" means checking project structure. The Agent cannot extract precise strategy parameters from vague natural language |
| **Task Templates** | Pre-define Prompt templates for each task type | Templates are static — they don't adjust to project context. The same "new project" template is used for a blog system and a microservice architecture, but the latter needs heavier interviews and stricter review |
| **LangGraph Conditional Routing** | Define conditional branches in the Graph: if task_type == "refactor" → route to node A | Routing logic is hardcoded. Adding a new task type requires modifying the Graph structure. And the condition judgment relies on the user providing a task_type field — back to "user manual mode selection" problem |
| **Devin's Task Understanding Module (closed-source, inferred)** | Infer task type from task description | Closed-source implementation, mechanism unverifiable. But behaviorally, Devin's task-type differentiation granularity appears coarse (new vs. modify), with no observable strategy switching for fine-grained types like refactoring, research, or collaboration |

**Common flaw**: Either shift classification responsibility to the user (manual mode selection, prompt declaration), or cram all tasks into a single generic process. The correct direction is **system-automated classification + automatic strategy binding** — the user only needs to describe the task; the system judges the task type and matches the corresponding execution strategy. The user does not and should not need to know that "refactors need deep interviews while simple tasks don't" — that's the system's job.

---

## 3. Solution Design

### 3.1 The 7+1 Intent Taxonomy

OMO defines 7 base intent categories + 1 extension mechanism (Spec-Driven), for a total of 7+1. Each intent is defined along three dimensions: task essence, typical characteristics, and strategic needs.

#### The Seven Base Categories

**C₁ — Refactor**

- **Task essence**: Change structure without changing external behavior on an existing codebase
- **Typical characteristics**: Existing codebase present, involves redrawing module boundaries, requires backward compatibility
- **Strategic needs**: Deep interview (understand existing architecture + confirm split boundaries + clarify immutable constraints) → Fine-grained Plan (module-level) → Strict review (contract consistency matters more than functional correctness)

**C₂ — New**

- **Task essence**: Build a new project or feature module from scratch
- **Typical characteristics**: No existing code dependencies (or very weak ones), open technology choices, large architecture design space
- **Strategic needs**: Medium interview (tech stack confirmation + project structure conventions) → Coarse-grained Plan (milestone-level) → Standard review (structural soundness and basic functional correctness)

**C₃ — Medium**

- **Task essence**: Add or modify medium-scale functionality in an existing project
- **Typical characteristics**: Involves 3–10 file modifications, clear existing code context, controllable scope
- **Strategic needs**: Lightweight interview (confirm scope and constraints) → Medium-grained Plan (file-level) → Standard review (local correctness of changes + consistency with existing code)

**C₄ — Collaboration**

- **Task essence**: Tasks completed through multi-Agent or human-Agent collaboration
- **Typical characteristics**: Task dispatched to multiple executors, parallel and dependency relationships exist, coordination and merging required
- **Strategic needs**: Heavy interview (role assignment + interface contracts + merge strategy) → Layered Plan (per-executor sub-plans + global coordination plan) → Interface-level review (contract compatibility of each executor's output takes priority over internal implementation quality)

**C₅ — Architecture**

- **Task essence**: System-level architecture design and decisions
- **Typical characteristics**: Cross-module/cross-service decisions, involves non-functional requirements (performance, scalability, security), high-impact and irreversible decisions
- **Strategic needs**: Deepest interview (make all constraints explicit + trade-off analysis + decision records) → Abstract Plan (architecture decision layer, no specific file details) → Multi-dimensional review (independent review for each NFR dimension)

**C₆ — Research**

- **Task essence**: Exploratory task, final output is knowledge and recommendations rather than code
- **Typical characteristics**: High uncertainty, requires multiple iteration rounds, output forms vary (document/report/recommendation proposal)
- **Strategic needs**: Iterative interview (align direction after each research round) → Elastic Plan (adjustable as research findings evolve) → Relaxed review (completeness > precision)

**C₇ — Simple**

- **Task essence**: Explicit modification of a single file or very few files
- **Typical characteristics**: Scope ≤ 2 files, requirements clear and unambiguous, no architecture decisions involved
- **Strategic needs**: Zero interview (execute directly) → Minimal Plan (1–2 steps) → Shallow review (verify diff correctness only)

#### Extension Mechanism: Spec-Driven

**Spec-Driven** is not an eighth intent type — it is a meta-mechanism: when a task does not fit into any of the seven categories above, the system enters Spec-Driven mode. This mode does not attempt to guess the user's intent; instead, it requires the user to provide a structured Spec, and the system derives interview depth, plan granularity, and review standards automatically from the constraints in the Spec.

Spec-Driven's existence solves the inherent ceiling problem of a 7-category fixed taxonomy — there may emerge new task types that the current seven cannot cover. Rather than forcibly classify into an existing category (causing strategy mismatch), it's better to fall back to a "Spec as anchor, reverse-derive strategy" mode.

### 3.2 Intent→Strategy Binding Table

Each intent binds four strategy dimensions: interview depth, plan granularity, review standard, and execution mode.

| Intent | Interview Depth | Plan Granularity | Review Standard | Execution Mode |
|------|:---:|:---:|------|------|
| **Refactor** | Deep interview | Fine-grained (module-level) | Strict review (contract consistency + behavior preservation + test coverage) | Single Agent, sequential execution |
| **New** | Medium interview | Coarse-grained (milestone-level) | Standard review (structural soundness + basic functionality) | Single Agent, parallelizable sub-tasks |
| **Medium** | Lightweight interview | Medium-grained (file-level) | Standard review (local correctness + consistency) | Single Agent, sequential execution |
| **Collaboration** | Heavy interview | Layered Plan (sub-plans + coordination plan) | Interface-level review (contract compatibility first) | Multi-Agent parallel + merge |
| **Architecture** | Deepest interview | Abstract Plan (architecture decision layer) | Multi-dimensional review (each NFR dimension independent) | Single Agent + human decision points |
| **Research** | Iterative interview | Elastic Plan (adjustable) | Relaxed review (completeness > precision) | Single Agent, multi-round iteration |
| **Simple** | Zero interview | Minimal Plan (1–2 steps) | Shallow review (diff correctness) | Single Agent, direct execution |
| **Spec-Driven** | Spec→derived | Spec→derived | Review per Spec constraints | Execute per Spec constraints |

**Bindings are not hardcoded**

The strategies in the binding table are each intent's **default strategy** — not an unmodifiable iron rule. When project context or user preferences suggest a different strategy is needed, the system can adjust. For example, Refactor defaults to deep interview, but if the project's refactoring history shows the user prefers rapid iteration (many small refactors rather than one big refactor), the system can lower interview depth to medium. Default strategies provide "the most reasonable starting point for that intent" — not the endpoint.

**Strategy Induction**

The core value of the binding table lies not in "providing strategies for known intents" — it lies in "providing reasonable default strategies for new intents." When a new intent is added to the taxonomy (e.g., a future "Migration" intent — database/framework migration), it doesn't need to define all strategy dimensions from scratch. The system can derive a default strategy from task essence ("Migration" is similar to "Refactor" — has an existing system, needs functional equivalence, involves multi-file changes), yielding "deep interview + fine-grained Plan + strict review," sharing the strategy template with Refactor, then adding extra review dimensions based on migration-specific traits (the irreversibility of data migration).

This is what "lower floor" means: new intents don't collapse — they won't degenerate to generic strategy just because "this task type has never been seen before."

### 3.3 Spec-Driven: The Ceiling Extension Mechanism

Spec-Driven was the last addition to the 7+1 system — its very existence proves the incompleteness of a 7-category fixed taxonomy.

**Trigger Conditions**

Spec-Driven is triggered under two circumstances:

1. **Low classification confidence**: When the system classifies a task into the 7 categories and the highest confidence is below a threshold (e.g., < 0.6) — i.e., the task does not belong to any known type
2. **User explicitly requests it**: When the user issues a task in Spec format (e.g., using OpenSPEC's propose flow)

**Workflow**

```
User provides structured Spec
  │
  ▼
Spec parser extracts constraint dimensions:
  ├── Scope (number of files/modules)
  ├── Immutable constraints (modules/interfaces that must not change)
  ├── Quality requirements (performance/security/compatibility)
  └── Delivery format (code/documentation/configuration/mixed)
  │
  ▼
Constraint→Strategy derivation engine:
  ├── Scope → Plan granularity
  ├── Immutable constraints → Interview depth (more constraints → heavier interview)
  ├── Quality requirements → Review standard (each quality dimension → independent review item)
  └── Delivery format → Execution mode
  │
  ▼
Generate bound strategy → Enter execution
```

**Why Spec-Driven is "raise ceiling"**

The ceiling of a fixed taxonomy is the number of categories — if an 8th, 9th type of task emerges in reality that can't fit into the existing 7, the fixed taxonomy must be modified (add category + define strategy + update classifier). This is a fragile extension method — every extension requires code changes.

Spec-Driven breaks this ceiling: no new category is needed, only a user-provided Spec. The constraints in the Spec directly drive strategy derivation — the system doesn't need to "recognize" this task type. This means the effective coverage of the taxonomy expands from "7 categories" to "all tasks describable by a Spec" — the ceiling is significantly raised.

At the same time, Spec-Driven also serves as an incubator for future new categories — if a certain Spec pattern appears frequently (e.g., many users provide structurally similar "database migration Specs"), the system can abstract a new intent category (Migration) from the Spec pattern and refine a default strategy for it. Spec-Driven is both a fallback strategy and a mine for new intents.

---

## 4. Analysis

### 4.1 The Dual Mechanism: Lower Floor and Raise Ceiling

The core design principle of the 7+1 system is not "make strategies for known intents more precise" — though it certainly achieves that — but to simultaneously address two natural vulnerabilities of any taxonomy: bottom collapse (new intents have no strategy available) and top lock-in (category count is frozen).

**Lower Floor: Strategy Induction**

When a new intent category is introduced (whether manually designed or emergent from Spec patterns), it faces a "cold start" problem — no historical data, no knowledge of the optimal strategy. The 7+1 system's solution is strategy induction: the new intent inherits a default strategy from the existing intent closest in task essence, then gradually tunes through usage.

Specific mechanism:
1. When new intent C_new is defined, declare its similarity vector to existing intents: `sim(C_new, C_i) for i ∈ {1..7}`
2. Initial strategy Σ(C_new) is a weighted average of existing strategies: `Σ(C_new) = Σ w_i · Σ(C_i)`, where `w_i = sim(C_new, C_i) / Σ sim`
3. As instances of C_new accumulate, tune Σ(C_new) from execution feedback

This guarantees new intents won't "collapse" — i.e., they won't degenerate to generic strategy due to lack of a dedicated strategy, causing significant execution quality degradation.

**Raise Ceiling: Spec-Driven Extension**

The ceiling of a 7-category fixed taxonomy is removed under Spec-Driven mode — because Spec-Driven doesn't depend on classification, it depends on constraint derivation. Any task, as long as it can be described by a structured Spec, can receive a reasonable strategy binding.

This means:
- Short-term: No need to urgently extend the classifier for every newly emerging task type — Spec-Driven serves as fallback
- Medium-term: Identify high-frequency patterns from Spec patterns, refine them into new intent categories
- Long-term: The taxonomy grows organically on top of the 7 categories, rather than being a closed set designed once and frozen

**Synergy of the Dual Mechanism**

Lower floor and raise ceiling are not independent — they work in synergy:

```
New task emerges
  │
  ├── Covered by 7 categories → Use existing strategy (lower floor ensures default strategy is reasonable)
  │
  └── Not covered by 7 categories → Enter Spec-Driven
        │
        ├── Short-term: Spec constraints derive strategy (raise ceiling mechanism)
        │
        └── Medium-term: This Spec pattern appears frequently → Refine into new intent C_8
              │
              └── C_8 induces default strategy from existing 7 categories (lower floor mechanism activates again)
```

### 4.2 Boundary Condition: Intent Misclassification

The most critical boundary condition of this solution is that the classifier may misclassify task T into the wrong intent category C_wrong, causing strategy mismatch.

**Asymmetric Consequences of Misclassification**

The severity of misclassification consequences varies by direction:

| Misclassification Direction | Consequence | Severity |
|-----------|------|:---:|
| Simple → Refactor (simple task treated as refactor) | Over-interviewing (user bombarded with unnecessary questions) + over-reviewing (time wasted checking contracts that don't exist) | Low — wastes time but produces no errors |
| Refactor → Simple (refactor treated as simple task) | Skip interview (don't confirm split boundaries) → Plan too coarse → Review too shallow (don't check contract consistency) → Refactor may introduce hidden bugs | **High — may produce functional defects** |
| New → Architecture (new project treated as architecture decision) | Over-interviewing + Plan too abstract (no specific file details) → Execution never lands concretely | Medium — user feels Agent is "all talk, no action" |
| Research → New (research treated as new project) | Interview focuses on tech stack choice instead of research direction → Plan too specific (attempts coding instead of exploration) → Review too strict (demands precision instead of completeness) | Medium — output format may deviate from user expectations |
| Medium → Collaboration (ordinary task treated as collaboration task) | Over-designed interface contracts + unnecessary parallelization → Added coordination overhead with no benefit | Low — adds valueless complexity |

**Mitigation Strategies for Misclassification**

1. **Classification confidence threshold**: The classifier outputs a confidence score for each intent category. If the highest confidence < θ_low (e.g., 0.6), don't force classification — fall back to Spec-Driven or request user confirmation
2. **Asymmetric rejection**: Some misclassification directions are too costly and should have stricter thresholds. Refactor → Simple misclassification cost is high → require higher confidence threshold for Simple classification (θ_simple > θ_others)
3. **Runtime strategy upgrade**: If the Agent discovers during execution that actual task complexity far exceeds the current classification's assumptions (e.g., classified as Simple but execution reveals 5 files involved), trigger strategy upgrade — escalate from Simple's lightweight strategy to Medium's standard strategy
4. **Classification feedback loop**: When the user's subsequent behavior indicates misclassification (e.g., Agent interviews with Refactor strategy but user says "don't ask so much, just change it"), that feedback is used to tune the classifier — not just model weights, but also user/project-specific classification preferences

**Classification is not the goal itself**

It's worth emphasizing: the purpose of intent classification is to bind the appropriate strategy, not to pursue 100% classification accuracy. If the classifier's highest confidence for a task is only 55%, but the second-highest confidence is 95% — directly choosing the second-highest category may be more practical than forcing "accurate classification." Classification is the means; strategy binding is the goal.

---

## 5. Validation Path

### 5.1 Verified

- **OMO codebase has implemented 7+1**: Source code audit of OMO confirms that intent classification logic covers all 7+1 types. Each type's corresponding interview strategy, review standard, and execution mode has independent logic branches in the code — not textual descriptions in Prompts, but traceable code paths.
- **Documentation-code gap**: OMO's public documentation advertises only 4 intent types (refactor / new / medium / simple), but the code actually supports 7+1. The implementations of Collaboration, Architecture, Research, and Spec-Driven exist but are not disclosed in documentation — a gap discovered by the author through source code audit.
- **Classifier input signals**: OMO's classifier uses the following input signals for intent judgment: (a) natural language analysis of the user's task description; (b) codebase characteristics of the current project (file count, dependency graph complexity, whether existing code is present); (c) user historical behavior (preferred interview depth, preferred review strictness). Multi-signal fusion improves classification accuracy.

### 5.2 To Be Validated

- **7-category classification accuracy**: On 200+ real task scenarios, the classifier's accuracy in correctly categorizing tasks into the 7 categories (excluding Spec-Driven). Key metric is the confusion matrix — which categories are easily confused with each other (e.g., Medium and Simple, Architecture and New).
- **Strategy binding user satisfaction**: User satisfaction with "the strategy the classifier automatically selected" — whether they feel there was too much/too little interviewing, too strict/too loose reviewing. Controlled experiments against "user manually selecting strategy" and "generic strategy."
- **Strategy induction quality**: When introducing a new intent category (e.g., Migration), the performance of the strategy-induction-generated default strategy on actual tasks — the gap from a manually designed dedicated strategy.
- **Spec-Driven coverage and derivation quality**: In a test set, how many tasks trigger Spec-Driven mode; the overlap between strategies derived from Spec constraints and the optimal strategy as judged by humans.
- **Runtime strategy upgrade trigger accuracy**: When the Agent discovers its classification is too low during execution (Simple → actually Medium complexity) and triggers a strategy upgrade — whether the upgrade is timely, necessary, and improves execution outcomes.
- **Classifier transferability across different LLMs**: The classifier depends on the LLM's task understanding capability. When the underlying model switches from DeepSeek V4 Pro to Qwen or Claude, how classification accuracy changes.

---

## 6. Relationship to Hermes

### 6.1 How Hermes Implements Intent Classification

Hermes's Metis module is the natural carrier for intent classification. Metis analyzes the user's task description at the task reception stage and currently already has strategy routing capability (dispatching tasks to different execution modes). The 7+1 classification can serve as an upgrade to Metis's strategy routing:

**Current state**: Metis uses heuristic rules for task dispatch (e.g., "files involved > 10 → complex task mode")

**After upgrade**: Metis feeds the task description into the classifier → outputs intent category + confidence → queries the binding table for default strategy → injects into Plan generation and execution flow

Implementation path:
1. Add an intent classification node in Metis's task analysis pipeline
2. Write classification results into task context (`TaskContext.intent`); subsequent Plan generation, review, and execution modules read this field to adjust their behavior
3. Store the binding table as a configuration file (`intent_strategy_bindings.yaml`), allowing users and projects to customize strategy overrides

### 6.2 Relationship to OMO's 7+1

The 7+1 system described in this article originates from OMO's code implementation, but this article's contribution is not "restating OMO's documentation" — OMO's documentation only describes 4 types. Through source code audit, this article discovered the complete 7+1 system and systematized it into:

- The strategy binding table for each intent (§3.2) — these bindings exist in OMO's code but are scattered across multiple files; this article is the first to consolidate them in a single view
- The formalized description of strategy induction (§4.1) — OMO's code contains strategy inheritance logic, but its design rationale is not articulated in the documentation
- The argument for Spec-Driven as a "raise ceiling" mechanism (§3.3) — OMO's code implementation of Spec-Driven is relatively primitive; this article provides a systematic analysis of its positioning within the entire taxonomy

In other words, what this article does: **reverse-extract design principles from OMO's code implementation**, and articulate them as a general Agent architecture pattern that can be used independently of OMO.

### 6.3 Why Hermes Needs This Solution

Hermes currently faces the same "strategy-to-task mismatch" problem as all Agents — all tasks enter the same execution flow. Introducing 7+1 classification allows Hermes to achieve "use the right strategy at the right moment":

- User says "help me refactor this module" → Hermes automatically identifies as Refactor → initiates deep interview (proactively asks about module boundaries, immutable constraints) → fine-grained Plan → strict review (contract consistency check)
- User says "update the installation steps in the README" → Hermes automatically identifies as Simple → skips interview → 1-step Plan → shallow review (diff correctness check)
- User says "research microservice framework options" → Hermes automatically identifies as Research → iterative interview → elastic Plan → relaxed review

The user doesn't need to write in the Prompt "this is a refactor task, please do a deep interview" or "this is a simple task, just do it directly" — the system automatically judges from the task description. This is a key step in the Agent's journey from "tool" to "partner": a true partner knows when to ask and when not to ask.

---

## Conclusion

An Agent's strategy should not be a one-size-fits-all generic template. Refactoring and new projects, research and simple modifications — these tasks have completely different reasonable expectations for the Agent's interview depth, plan granularity, and review standards.

OMO's 7+1 intent taxonomy solves this problem through three designs:

1. **Automated classification**: The system automatically judges intent type from the task description — no need for the user to manually select a mode
2. **Strategy binding table**: Each intent binds interview depth, plan granularity, review standard, and execution mode — strategy matches task type
3. **Bidirectional extension mechanism**: Strategy induction guarantees new intents don't collapse (lower floor), Spec-Driven guarantees the taxonomy isn't ceiling-locked (raise ceiling)

This is not about making the Agent smarter — it's about making the Agent's execution framework more discerning. The Agent's capabilities haven't changed, but it now knows what method to use when.

7+1 is not the endpoint. The very existence of Spec-Driven admits the limitations of 7 categories — new task types will keep emerging. But the design of 7+1 ensures that when new types appear, the system won't degenerate to "don't recognize → use generic strategy" — instead, through strategy induction and Spec derivation, it provides a reasonable strategic starting point for the new type.

---

*Previous: [09 Skills Self-Evolution Loop](09-skills-self-evolution.md) — Things done repeatedly should become muscle memory*
*Next: [11 Checkpoint Snapshot-Driven Multi-Round Review](11-checkpoint-review.md) — Review quality should not decay as context expands*
