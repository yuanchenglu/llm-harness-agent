# OKR-Enhanced PlanStep + Cascade Correction Engine

> **Innovation Index**：I-01, I-03
> **LLM + Harness = Agent** · Part 6
> **Series**：[LLM + Harness = Agent](../README.md)
> **Previous**：[05 Document KV Cache Optimization](05-document-kv-cache.md)
> **Next**：[07 Review Switching Engine](07-review-switching.md)

---

> **Abstract**：Every existing Agent framework shares the same flaw in its Plan module — PlanStep is a flat `text + status` checklist with no dependency semantics between steps. Change the requirement on step 3, and steps 4-7 never learn that anything changed — producing contradictory outputs and redundant rework. This article proposes the OKR-Enhanced PlanStep: five new fields — `key` (verifiable result metric), `step_id` (unique identifier), `parent_id` (parent-child hierarchy), `dependency_ids` (cross-branch dependencies), and `association_strength` (coupling intensity) — upgrading Plan from a linear Checklist to a directed dependency graph. On top of this, we construct the Cascade Correction Engine: when any node is modified, traverse the subgraph and dependency nodes → mark `pending_review` → trigger per-node re-review → propagate upward to the root. This is not "re-execute the entire Plan" — it is re-auditing only the minimal affected dependency subgraph.

---

## 1. Problem Definition

### 1.1 The Phenomenon

You give an Agent a task: "Write a REST API for the user registration feature." The Agent generates a 7-step Plan:

```
Step 1: Design database schema        [completed]
Step 2: Implement POST /register      [completed]
Step 3: Implement email verification   [in_progress]
Step 4: Write unit tests               [pending]
Step 5: Write integration tests        [pending]
Step 6: Implement JWT authentication   [pending]
Step 7: Write API documentation        [pending]
```

By step 3, you realize the requirements were misunderstood — it should be "phone verification," not "email verification." The Agent changes the text of Step 3. But Step 4, 5, and 7 still say "unit test for email verification," "integration test for email verification," "email verification documentation."

The Agent has no idea these steps are related. It knows Step 3 changed — Steps 4-7 don't know, don't care, don't update.

You are left manually checking every subsequent step for impact — precisely the thing you adopted an Agent to avoid.

### 1.2 Root Cause

The root cause isn't the Agent's model capability. It's the PlanStep data structure.

Every mainstream Agent framework's PlanStep structure is a variation on the same pattern:

```typescript
// OMO (oh-my-claudecode) — PlanProgress
interface PlanProgress {
  total: number;
  completed: number;
  isComplete: boolean;
}

// ACP Protocol Standard — PlanEntry
type PlanEntry = {
  content: string;    // step description
  priority: string;   // priority (high/medium/low)
  status: string;     // status (pending/in_progress/completed)
}

// CodeWhale — PlanStep (Rust)
struct PlanStep {
  text: String,
  status: StepStatus,
  started_at: Option<Instant>,
  completed_at: Option<Instant>,
}
```

All three share the same assumption: PlanSteps are independent — no parent-child relations, no sequential dependencies, no association strength. Plan is essentially a flat Checklist, not a directed dependency graph (DAG).

**Where does this assumption come from?** From the product positioning that "Agent Plans are just execution-progress displays for humans." CodeWhale's `update_plan` tool description is blunt: *"Update optional high-level strategy metadata for complex initiatives. Use checklist_write for primary work progress."* — Plan is for *display*, not for *driving*.

Under the "display" positioning, a flat structure suffices. Under the "driver" positioning — where the Agent autonomously executes steps based on its Plan, reviews outputs, and decides the next move — a flat structure is entirely insufficient. But today's Agents are transitioning from the former to the latter. The data structure hasn't caught up.

### 1.3 Formalization

Let Plan contain n steps P = {p₁, p₂, ..., pₙ}. All current frameworks model P as an unrelated vector:

```
∀ i, j ∈ [1, n]: relation(pᵢ, pⱼ) = ∅ (from the framework's perspective)
```

Real-world task execution contains explicit and implicit dependencies:

```
Actual dependency graph G = (V, E), V = P
E = {(pᵢ, pⱼ) | pⱼ's output directly depends on pᵢ's result}
```

When the user modifies pₖ, the affected set is Aₖ = {pₓ ∈ V | there exists a path from pₖ to pₓ (including descendants) + nodes with cross-branch semantic coupling}. In the flat model, Aₖ is **completely invisible to the Agent** — the Agent doesn't know which steps were impacted, and therefore cannot correct them. In the dependency graph model, Aₖ can be precisely computed via transitive closure, making cascade correction automatable.

---

## 2. Existing Approaches and Limitations

| Approach | Core Idea | Why It Falls Short |
|----------|-----------|-------------------|
| **OMO PlanProgress** | Markdown checklist parsing: regex match `- [x]` vs `- [ ]`, count total/completed/isComplete | Purely flat progress tracking. No step entity, let alone dependencies. Steps are a collection of plain text lines — line 3 and line 7 have zero relational constraint |
| **ACP PlanEntry** | content + priority + status, three fields, each entry independent | An industry protocol standard defines the lowest common denominator. Cross-product compatibility comes at the cost of semantic minimalism — you cannot require every product to implement dependency graphs |
| **CodeWhale PlanStep** | text + status + started_at/completed_at, atomic steps managed by a single PlanState | The most polished flat implementation — state machine validation, single in_progress constraint, duration tracking. But still lacks parent_id and dependency_ids. All steps sit in a single Vec ordered sequentially; modifying step 3's text means steps 4-7 are strings on other lines — zero inter-association |
| **Hermes Kanban task_links** | parent_id/child_id many-to-many association table, supports progress rollup | The closest design to a dependency graph among all tools. But task_links only has parent-child binary relations, lacking "association strength," "dependency type," and "read-only dependency vs. strong-coupling dependency" semantics. Furthermore, task_links serves task delegation ("subtask done → parent can advance"), not Plan cascade correction ("step 3 changed → steps 4-7 need re-review") |
| **Manual human management** | After changing one thing, manually check every subsequent step | Doesn't scale. Omission rate skyrockets when Plan exceeds 10 steps. And human inspection granularity is far below the Agent's — the Agent can diff outputs line by line; humans can only read titles |

**Common deficiency**: All approaches acknowledge that Plan steps "should have ordering" (implicitly via list numbering), but none *structuralize* that ordering. Sequence numbers are visual mnemonics for human readers, not data structures for machine reasoning.

---

## 3. Solution Design

### 3.1 OKR-Enhanced PlanStep Field Design

Core thesis: borrow from OKR (Objectives and Key Results) — not just defining "what to do" (Objective) but also "what done looks like" (Key Result) — introducing verifiable result metrics for each PlanStep. Then layer in dependency graph fields.

```typescript
// OKR-Enhanced PlanStep (this proposal)
interface OKRPlanStep {
  // ─── Base fields (inherited from existing flat models) ────
  text: string;              // step description (Objective)
  status: PlanStatus;        // pending | in_progress | completed | pending_review

  // ─── OKR layer: verifiable result metric ────
  key: string;               // This step's Key Result: verifiable completion criterion
                             // e.g. "POST /register returns 201 + database has one new user row"
                             // Format: natural language assertion, but must be decidable
                             // as true/false by an Agent or test code

  // ─── Dependency graph layer: structured inter-step relations ────
  step_id: string;           // unique identifier (UUID or semantic ID, e.g. "step-3")
  parent_id?: string;        // parent step's step_id. null = root step
                             // all children complete → parent auto-marked complete

  dependency_ids: string[];  // explicit dependency list: which other steps' outputs
                             // this step depends on
                             // distinct from parent_id: the former is "hierarchical containment,"
                             // the latter is "output dependency"
                             // e.g. step 6 may depend on step 2's result but is not step 2's child

  association_strength: AssociationStrength;
                             // "strong" | "moderate" | "weak"
                             // strong: modifying this step must re-review dependent nodes
                             // moderate: modifying this step should re-review dependent nodes
                             // weak: modifying this step only notifies dependent nodes, no forced re-review

  // ─── Children list (tree structure) ────
  children?: OKRPlanStep[];  // recursive nesting. leaf nodes = atomic tasks,
                             // non-leaf nodes = aggregate tasks
}
```

**Design rationale for the five new fields**:

**① `key`**: The biggest problem with flat Plans is that "completed" has no verification criterion. The Agent marks Step 3 as completed — but how do you know it's *actually* done? `key` is an "acceptance test" embedded in the Plan structure — every step carries a verifiable assertion. This allows a review Agent to automatically judge whether a step is truly complete, without human item-by-item inspection.

Why "OKR"? The essence of OKR is "every Objective has measurable Key Results." Apply this to PlanStep: each step's `text` is the Objective (what to do), `key` is the Key Result (what done looks like). Plan upgrades from a "wishlist" to a "set of verifiable commitments."

**② `parent_id`**: Step hierarchy. A 50-step Plan is cognitive load for both humans and Agents — flattened into a single list, you can't see that "these 7 steps all belong to the same sub-goal." `parent_id` introduces a tree structure, letting the Agent "focus on the current branch" instead of losing context in a 50-step linear list.

**③ `dependency_ids`**: Cross-branch output dependency. `parent_id` expresses "logical grouping" (steps 4-7 are children of step 3), while `dependency_ids` expresses "data/output dependency" (step 6 "implement JWT auth" depends on step 2 "POST /register"'s interface definition — but they aren't in the same parent-child branch). Without dependency_ids, cross-branch impact analysis is completely untraceable.

**④ `association_strength`**: Not all dependencies are equal.

- Strong: step A's output is directly referenced/invoked in step B. Changing A must re-review B.
- Moderate: step A's output defines the context for step B (e.g., interface contract). Changing A likely impacts B, but not inevitably.
- Weak: steps A and B share the same module/file but have no direct call relationship. Changing A only notifies B, no forced re-review.

This three-tier intensity design comes from actual engineering experience — not every "dependency" means "change one, everything breaks." Without intensity grading, every dependency is treated as strong, causing excessive re-review and Token waste.

**⑤ `children`**: Recursive nesting. Atomic tasks are leaf nodes (no children); aggregate tasks are intermediate nodes (children = sub-step list). Tree structure lets Plan complexity be "collapsed" — the Agent sees only 5 aggregate steps at the top level; only upon entering an aggregate step does it see the 10 atomic steps within. This solves the "50-step Plan cognitive load" problem.

### 3.2 Cascade Correction Engine

The Cascade Correction Engine is the automated propagation mechanism built on top of the OKR PlanStep dependency graph.

**Core algorithm**:

```
function cascade_correct(modified_node: OKRPlanStep, plan_graph: Graph):
    affected = transitive_closure(modified_node, plan_graph, direction="downstream")

    for node in affected:
        match node.association_strength:
            "strong"   → node.status = "pending_review"
                          schedule_review(node)
            "moderate" → node.status = "pending_review"
                          # moderate nodes are also flagged, but review depth is shallower
            "weak"     → notify(node)  # only notify, no forced re-review

    # Upward propagation: if the modification causes the parent's key
    # to no longer hold, flag the parent
    current = modified_node.parent
    while current != null:
        if not verify_keys(current):
            current.status = "pending_review"
            schedule_review(current)
        current = current.parent
```

**Three phases of the engine**:

**Phase 1: Traverse dependency graph → mark affected set**

Starting from the modified node, perform BFS/DFS along `dependency_ids` and `parent_id → children`. `transitive_closure` computes all "downstream affected" nodes — all nodes indirectly connected via explicit dependencies or parent-child relations. Not the entire graph — only the **downstream subgraph** from the modification point.

**Phase 2: Tiered processing by association_strength**

- `strong` → mark `pending_review`, trigger full review (re-verify key, re-check output consistency)
- `moderate` → mark `pending_review`, trigger lightweight review (only check interface/type signature match, no deep implementation inspection)
- `weak` → don't change status, only send Agent notification: "Step X was modified, you may want to glance, but not required"

The core value of tiered processing: not every affected step needs re-execution. Tokens aren't free — every review round consumes context. Tiered processing allocates review resources to nodes that "genuinely might break," not nodes that "technically have a relation but are actually independent."

**Phase 3: Upward propagation to root**

A modification may cause a parent step's `key` to no longer hold. Example: the parent step's key is "interface documentation for all sub-steps is complete." Step 3's sub-step changed an interface signature — the parent's key is now unsatisfied. The engine backtracks up the `parent_id` chain, re-verifying keys at each level.

Critical constraint on upward propagation: **unidirectionality**. Only propagate upward (child → parent), not downward (parent → children). Downward propagation ("parent changed, re-review all children") causes cascade storms — one top-level modification triggers full Plan re-review, Token consumption explodes.

### 3.3 Why a Tree, Not a General Graph

From a data structure perspective, Plan dependencies form a **Directed Acyclic Graph (DAG)** — not a tree (a child node can have multiple parent dependencies). But in the Plan context, `parent_id` represents **logical hierarchy** (decomposition structure of tasks), while `dependency_ids` represents **output dependency** (data/interface flows).

Reasons for separating the two:

1. **Logical hierarchy is a tree; output dependency is a graph.** Tree hierarchy maps to "task decomposition" — "implement user registration" decomposes into 7 sub-tasks. This is a top-down containment relation, naturally a tree. Output dependency maps to "this step's output is that step's input" — a lateral data flow, naturally a graph. Separating the two models means the Cascade Correction Engine only needs to traverse the "output dependency graph," not the "entire complex hybrid structure."

2. **Tree hierarchy supports folding and context isolation.** When the Agent executes "Step 3.2: implement SMTP portion of email verification," it doesn't need to see Step 5's content — they aren't in the same subtree. Tree structure lets the Agent's attention focus on the current branch.

3. **Cascade correction propagation paths are on the dependency graph, not the hierarchy tree.** When Step 3.2 is modified, what's affected is "all nodes that depend on Step 3.2's output" — this propagation is computed from the `dependency_ids` graph, independent of hierarchy. The hierarchy tree is only used for re-verifying parent keys — this is "upward verification," not "cascade propagation."

---

## 4. Analysis

### 4.1 Why This Solution Addresses the Root Problem

The root problem isn't "PlanStep doesn't have enough fields" — it's that "relationships between Plan steps aren't encoded as a computable structure."

The five new fields of the OKR-Enhanced PlanStep fall into three functional layers:

- **OKR layer** (`key`): Makes "completion" go from subjective judgment to verifiable assertion. Solves: "The Agent says it's done, but how do I know it's *really* done?"
- **Dependency graph layer** (`step_id`, `parent_id`, `dependency_ids`): Makes inter-step relationships go from "implicit assumptions for human reading" to "traversable directed graph." Solves: "I changed step 3 — how do I know steps 4-7 are affected?"
- **Intensity layer** (`association_strength`): Makes impact analysis granularity go from "binary (affected/unaffected)" to "three-tier graduated." Solves: "Not every affected node needs re-review — over-review is Token waste."

All three together: Plan upgrades from "a Checklist for humans" to "an execution graph the Agent can reason over." The Cascade Correction Engine isn't a bolt-on fix — it's a native capability of the dependency graph.

### 4.2 Boundary Conditions

The following scenarios are **not** covered by this proposal:

- **Implicit semantic dependencies**: Two steps lack an explicit `dependency_ids` declaration, but their outputs contain semantic conflicts (e.g., Step 2 defines user_id as int32, Step 6 assumes user_id as string in another file). This cross-file type inconsistency requires LSP/type-checker discovery, not dependency graph traversal.
- **The dependency graph itself requires maintenance**: In the Agent's created Plan, the accuracy of `dependency_ids` and `association_strength` depends on the Agent's understanding during the planning phase. If the Agent misses a dependency ("I thought Step 4 didn't depend on Step 3" but it actually does), the Cascade Correction Engine won't fix this omission — it only propagates along declared dependencies.
- **Cyclic dependencies**: The dependency graph must be acyclic (DAG). If the Agent creates a cyclic dependency (A depends on B and B depends on A), cascade correction enters an infinite loop. DAG validation (topological sort cycle detection) is required at Plan creation time.
- **Cross-session dependencies**: Plan steps may execute across multiple Agent sessions. Inter-session dependency graph consistency requires persistence to shared storage (database or file). Under session-isolated architecture, an additional "Plan state sync" mechanism is needed.
- **Overly large dependency graphs**: If a Plan contains 100+ steps with a dense dependency graph, modifying one node's cascade propagation may involve dozens of nodes. While far better than the traditional "re-review everything," this is still non-trivial Token cost. For very large Plans, a "checkpoint isolation" mechanism is needed — limiting cascade propagation within the same checkpoint interval.

### 4.3 Comparison with Existing Approaches

| Dimension | OMO PlanProgress | ACP PlanEntry | CodeWhale PlanStep | Hermes task_links | This Proposal: OKR PlanStep |
|-----------|:---:|:---:|:---:|:---:|:---:|
| Step identity | None (text lines) | Implicit (array position) | text string | task id (UUID) | step_id (explicit) |
| Inter-step relations | None | None | None (ordering only) | parent_id/child_id | parent_id + dependency_ids (dual) |
| Association strength | None | None | None | None | strong/moderate/weak (three-tier) |
| Completion criteria | Subjective human judgment | Subjective human judgment | Subjective human judgment | Subjective human judgment | key (verifiable assertion) |
| Cascade correction | None | None | None | None (progress rollup only) | dependency-based cascade engine |
| Tree hierarchy | None | None | None | Yes (two-level) | Yes (multi-level recursive children) |

Hermes task_links' parent_id/child_id is the closest design to this proposal — indeed, Hermes Kanban already does "parent-child task" association at the task delegation layer. But task_links is designed for task delegation ("who should this sub-task be assigned to"), not cascade correction ("which steps does this modification affect"). The key differences:

1. **Hermes task_links is binary** (parent/child), lacking dependency_ids for cross-level output dependencies. In Hermes Kanban, if Task A and Task B share the same file but aren't on the same parent chain, no field records their association.
2. **Hermes task_links has no association strength**. The parent knows "how many sub-tasks are complete" but not "how much a sub-task modification affects the parent." This creates an all-or-nothing parent-child relationship — either completely unrelated (not on the same parent chain) or completely bound (on the chain). No intermediate state.
3. **Hermes Kanban tasks lack a key field**. A task marked "done" doesn't mean its output passed verification — "done" is just the subjective marker of the user or Agent.

---

## 5. Verification Path

### 5.1 Verified

- **Problem existence**: Interactively verified Plan data structures across three frameworks —
  - OMO: `PlanProgress` only has `total/completed/isComplete`, zero step-level semantics
  - ACP Protocol: `PlanEntry` only has `content/priority/status`
  - CodeWhale: `PlanStep` is the most refined but remains flat — `text/status/started_at/completed_at`, stored in `Vec<PlanStep>`, no inter-step association
  - Hermes Kanban: `task_links` table has parent_id/child_id, but only for task-delegation parent-child aggregation, not serving Plan cascade correction
- **Cascade correction need**: In practical Agent usage, "changing one step invalidates several subsequent steps" is a high-frequency scenario — especially when "users modify requirements mid-execution." In-depth comparison of 8 Agent products confirmed this is the Plan module's most critical unsolved problem

### 5.2 To Be Verified

- **Dependency graph creation accuracy**: During Plan creation, can the Agent accurately identify inter-step dependencies and assign reasonable `association_strength`? Requires testing dependency annotation precision and recall on a set of standard tasks (50+ multi-step tasks)
- **Cascade propagation Token cost**: After modifying one step, compare the additional review Tokens generated by the Cascade Correction Engine vs. traditional "re-review everything" Token consumption. Expected cascade correction Token cost is approximately 15-35% of full re-review (since only the affected subgraph is re-audited)
- **OKR key verification rate**: Accuracy of the Agent automatically verifying `key` (verifiable completion criteria). If key is overly abstract ("code quality is good"), the Agent cannot auto-verify — key's value drops to zero. Requires exploration of optimal key granularity and expression paradigms
- **Upward propagation false positive rate**: After a parent step is marked `pending_review`, what proportion "actually needs modification" vs. "key verification unchanged, false flag"? The precision of upward propagation determines the engine's practical utility
- **Integration path with Hermes Kanban task_links**: If injecting OKR PlanStep fields into Hermes Kanban's task model — requiring three new fields (`dependency_ids`, `association_strength`, `key`) and corresponding cascade logic — scope of changes to the existing kanban kernel and compatibility impact

---

## 6. Relationship to Hermes

Hermes has the foundation for transformation on both the Plan and Kanban sides:

**On the Kanban side**: Hermes Kanban's `task_links` table already implements a parent/child relationship table. This is the closest design to a dependency graph among all Agent products. Transformation path:

1. **Add fields to `tasks` table**: `key` (verifiable completion criteria, TEXT), `association_strength` (association strength override enum, TEXT, e.g. `strong/moderate/weak`). `step_id` can reuse the existing `id` (UUID).
2. **Extend `task_links` table**: add `link_type` field (`"hierarchy"` for parent_id relations, `"dependency"` for dependency_ids relations). Current parent_id/child_id is hierarchical; dependency_ids is lateral — the two relation types need distinction but can share the same table.
3. **Add cascade logic in Kanban kernel**: when a task's `body` or `result` is modified, query `task_links` for all dependency-type associations with this task as `parent_id` — mark those associated tasks as `pending_review`.
4. **Add review Agent Kanban trigger**: tasks with status `pending_review` are handled by a dedicated review Agent — review logic reuses Hermes' existing Skill/review mechanism.

**On the Plan side**: Hermes currently uses flat PlanStep (`text + status`), not reading dependency information from Kanban task_links. Transformation path:

1. Have the Agent use the OKR-Enhanced PlanStep schema when generating Plans — `key` is a required field
2. During Plan execution, step changes automatically propagate via the Cascade Correction Engine
3. Plan state persists to Kanban — Plan steps and Kanban tasks are the same concept projected at different layers

**Why Hermes is the best platform to implement this proposal**:

Every other Agent framework's Plan is completely flat — lacking any concept of dependency relations from the start. Hermes' Kanban is the only platform that "already has parent/child relations, just hasn't applied them to Plan cascade correction." The transformation from task_links to OKR PlanStep isn't building a dependency system from scratch — it's adding semantics and propagation logic on top of an existing relationship table.

---

## Conclusion

An Agent's Plan should not be a Checklist for human eyes. A Checklist is a tool for "humans to tick off items one by one." A Plan is the reasoning foundation for "the Agent to know that changing A means B also needs re-review."

The five new fields of the OKR-Enhanced PlanStep (key, step_id, parent_id, dependency_ids, association_strength) upgrade Plan from a flat text list to a computable directed dependency graph. The Cascade Correction Engine leverages this graph to achieve "change one thing, precisely locate the affected scope, tiered processing" automated propagation — no more human manual inspection of every downstream ripple effect.

This isn't "writing Plans in more detail" — it's making Plan semantics go from "textual convention" to "structured data." When dependencies are no longer buried in natural language step descriptions ("Note: this step depends on the output of step 3") but instead live in structured dependency_ids arrays, the Agent can genuinely *reason* about "what does this modification affect."

---

*Previous: [05 Document KV Cache Optimization](05-document-kv-cache.md) — Agent-produced documents also need KV Cache optimization*
*Next: [07 Review Switching Engine](07-review-switching.md) — Review strictness should dynamically adjust based on context state*
