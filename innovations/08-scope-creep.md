# A Divide-and-Conquer Strategy for Two-Level Scope Creep

> Innovation Index: I-04
> **LLM + Harness = Agent** · Part 8
> Series: [LLM + Harness = Agent](../README-EN.md)
> Previous: [07 Review Switching Engine](07-review-switching.md)
> Next: [09 Skills Self-Evolution Loop](09-skills-self-evolution.md)

---

> **Abstract**: Everyone talks about Agent "Scope Creep" — the Agent takes on a task, does more and more, and drifts further and further from the original request. But "scope creep" is not one problem — it is two entirely different pathologies: demand-alignment creep (the user never said what *not* to include, so the Agent freely explores the ambiguity) and technical-planning creep (unforeseeable dependencies emerge as the task is decomposed, and the Plan naturally inflates). Every existing anti-creep solution treats both as the same problem — a one-size-fits-all "scope limit" that neither stops demand creep nor spares the necessary elasticity in technical planning. This article proposes a two-level divide-and-conquer strategy: at the demand-alignment level, Metis reverse-questions "what must *not* be included" to close the scope boundary loop; at the technical-planning level, the Cascade Correction Engine (I-03) manages dependency inflation that emerges during task decomposition. The two levels have different root causes, different solutions, and different evaluation criteria — govern them separately to defeat each.

---

## 1. Problem Definition

### 1.1 The Phenomenon

You give an Agent a task: "Add user authentication to this project."

The Agent gets to work. It first adds login and registration, then thinks "if there's authentication, there should be permission management," so it adds an RBAC role system. Next it considers "users need to change passwords," so it adds a password reset flow. Then "users might forget passwords," so it adds email verification and two-factor authentication. By the time you notice, the Agent is already implementing OAuth 2.0 third-party login integration — and all you wanted was a simple JWT login.

This is not the Agent being malicious. During execution, the Agent continuously discovers "this is also related" and "that's also needed" — every individual expansion looks locally reasonable. But all locally reasonable expansions accumulate until the final output deviates from the user's original intent.

At the same time, this scenario contains another dimension of scope inflation: when the Agent decomposes the sub-task "implement JWT login," it discovers that it must simultaneously handle token refresh mechanisms, session management, cookie-vs-header transport strategy, and cross-origin CORS configuration — these are not things the Agent proactively added; they are technical dependencies that *emerged* once the task was decoupled.

Two dimensions of scope inflation are happening simultaneously, but from the outside there is only one symptom: "The Agent did more than I wanted."

### 1.2 Two Different Root Causes

Scope creep is not one disease. It is two pathologies with different etiologies, different mechanisms, and different prescriptions.

**Level 1: Demand-Alignment Creep**

The root cause is not the Agent's technical capability — it is the openness of the requirement boundary. The user says "add user authentication," but does not say "no permission management," "no password reset," "no OAuth." In natural language communication, humans implicitly share vast amounts of contextual assumptions — "of course no OAuth, it's just an internal tool." But the Agent has none of these assumptions. The parts of the requirement where the user did *not* say "don't do X" are undefined territory for the Agent — it can freely explore, and the more it explores, the more reasonable it feels.

Formalized: let the user's true requirement set be R_true, and the user's explicitly expressed requirements be R_explicit. The Agent freely explores the complement space of R_explicit — and the direction of exploration is driven by "technical inertia of the current task" ("after doing A, of course you do B," "industry best practices include C"). The Agent cannot know which elements of R_true \ R_explicit the user deliberately excluded and which the user forgot to mention — it substitutes "technical reasonableness" for "requirement boundaries."

**Level 2: Technical-Planning Creep**

The root cause is the unforeseeability of task decomposition. When the Agent decomposes a high-level task into atomic steps, "implement JWT login" is not an atomic operation — it decouples into 7–8 sub-steps: token generation, verification middleware, refresh endpoint, expiration policy, error handling, and so on. The dependency relationships among these sub-steps are not fully foreseeable at the planning stage — only when the Agent reaches step 3 does it discover that step 2's assumptions need adjustment, which in turn affects steps 5 and 7.

Formalized: let the initial Plan contain n steps P₀ = {p₁, ..., pₙ}. During execution of pₖ, the Agent discovers that the actual prerequisite set D(pₖ) exceeds the dependencies declared in P₀ — that is, D_actual(pₖ) ⊈ dependency_ids(pₖ). The Agent must expand the Plan to incorporate the missing dependencies — the Plan inflates from P₀ to P₁ = P₀ ∪ ΔP, where ΔP is the set of patch steps for emergent dependencies. This is not the Agent "wanting to do more" — without these steps, pₖ simply cannot be completed.

### 1.3 Key Differences Between the Two Levels

| Dimension | Demand-Alignment Creep | Technical-Planning Creep |
|-----------|------------------------|--------------------------|
| **Root Cause** | Openness of requirement boundaries — user never said "don't do X" | Incompleteness of task decomposition — hidden dependencies emerge during execution |
| **Expansion Direction** | Outward — adding new feature modules (permissions, OAuth, password reset) | Inward — existing modules' internal steps inflate (token refresh, session management, CORS config) |
| **Agent's Motivation** | "Industry best practices," "after A naturally comes B" | "Without this step, the current step can't be completed" |
| **Value to Humans** | Low — user never wanted these features | Medium-to-high — if hidden dependencies go unaddressed, core functionality is defective |
| **Correct Handling** | Preemptive blocking: clarify boundaries upfront | In-flight management: control inflation scope |
| **Wrong Handling** | One-size-fits-all scope limit → also kills necessary elasticity in technical planning | Encouraging free exploration → demand creep also runs unchecked |

---

## 2. Existing Solutions and Their Limitations

| Solution | Core Idea | Why It Doesn't Work |
|----------|-----------|---------------------|
| **Step Count Limit** | Cap the Agent at N steps; stop when exceeded | Confuses both levels: demand creep should indeed be truncated, but hidden technical dependencies should not be skipped just because "the step limit was reached" — skipping them creates functional defects. A one-size-fits-all step cap neither stops demand creep (10 unrelated modules stuffed into the first 5 steps) nor spares necessary technical dependencies (the 7th dependency needed for step 6) |
| **Task Scope Declaration** | User writes "only do X, don't do Y" in the prompt | Only partially covers Level 1. Users can only think of so many Ys — the truly dangerous creep happens in areas the user never imagined ("how would I think the Agent would add RBAC on its own?"). Declaration-based approaches fundamentally rely on the user predicting all possible wrong directions — exactly the cognitive load users want to offload to Agents |
| **Plan Approval Mechanism** | Agent generates Plan → user approves → then execute | Approval only happens before execution. Technical-planning creep emerges during execution — an approved Plan still inflates by step 3. Approval mechanisms work for Level 1 (demand alignment) but are ineffective for Level 2 (technical planning) |
| **Human-in-the-Loop** | Pause on scope changes; wait for user decision | Popping up "Agent wants to add a step — approve?" every 5 minutes — frequent interruptions destroy the experience more than scope creep itself. And users, busy with other things, lack the energy to judge the necessity of every technical sub-step |
| **CodeWhale's Scope Guard** | Define task scope as a file set; Agent can only modify specified files | Only constrains code modification scope, not Plan inflation. Under the constraint "only modify auth.ts," the Agent can still implement OAuth + RBAC + password reset all inside auth.ts — file-scope constraints cannot prevent functional-scope creep |
| **OpenSPEC's Scope Proposal** | Write Spec first → confirm Spec → then code | Spec covers "what to do," but "what not to do" still relies on implicit assumptions. And Spec shares the same flaw as Plan approval — emergent dependencies during execution are not in the Spec |

**Shared Flaw**: All solutions attempt to use a single dimension ("limit scope") to solve problems from two different dimensions. Demand-alignment creep needs "boundary closure" — making the Agent proactively confirm "what *not* to do." Technical-planning creep needs "dependency management" — letting the Agent manage emergent dependencies during execution rather than one-size-fits-all rejection. The consequence of conflating the two: if the limit is too loose, demand creep floods in; if too tight, the necessary elasticity in technical planning is strangled — the Agent can't finish what it needs to do.

---

## 3. Solution Design

### 3.1 Level 1: Metis Reverse-Questioning — Closing the Demand Boundary Loop

**Core Idea**: The root cause of demand-alignment creep is not that the Agent is too proactive — it's that the user's requirement expression has only positive boundaries ("what to do") and lacks negative boundaries ("what *not* to do"). The Metis reverse-questioning mechanism fills this gap.

**Mechanism**:

When a user issues a task, Metis does not start from "how to do it" — it starts from "what *cannot* be done." Metis analyzes the user's task description and proactively poses reverse questions:

```
User: "Add user authentication to this project"

Metis reverse-questions:
  1. Scope of "user authentication" — limited to basic login/registration only, or does it need to include:
     - Permission/role management?
     - Password reset/recovery?
     - Third-party login (Google/GitHub OAuth)?
     - Two-factor authentication (2FA)?
  2. Inferred from project nature: this appears to be an internal tool — is multi-tenancy/organization management needed?
  3. What hard constraints exist on technology choices? For example:
     - Must use the existing database (no new storage)?
     - Must be compatible with the existing frontend framework?
```

Key design: Metis does not wait for the user to proactively fill in constraints — it **generates** reverse questions from the following sources:

1. **Common creep patterns by task type**: Historically, 73% of "user authentication" task creep comes from "permission management" and "OAuth integration" — Metis learns high-frequency creep directions from historical data and proactively asks
2. **Project context inference**: From codebase structure, infer project nature (internal tool / SaaS / open-source project); each project type has different typical unnecessary features
3. **User's implicit constraints**: From codebase tech stack, infer hard constraints ("database is SQLite → doesn't support complex transactional operations → don't add features requiring advanced transactions")

**Reverse-questioning output**: A structured "Exclusion List."

```json
{
  "task": "Add user authentication",
  "explicitly_excluded": [
    "Permission/role management system",
    "OAuth third-party login",
    "Two-factor authentication (2FA)",
    "Multi-tenancy support"
  ],
  "hard_constraints": [
    "Do not introduce new database/storage engine",
    "Compatible with existing React frontend; do not introduce new frontend libraries"
  ],
  "scope_boundary": "Implement JWT-based login/registration + token refresh only; do not include any authentication-related features beyond this scope"
}
```

The Exclusion List is not a soft constraint "prompting the Agent to take note" — it is a **hard boundary** injected into the execution context. When the Agent generates a Plan, the Exclusion List participates as a constraint condition — any excluded module will not appear in the Plan. During execution, every time the Agent proposes a new step, Harness checks whether that step hits the Exclusion List — if it does, it is automatically rejected with the note: "This feature is in the Exclusion List. Please confirm with the user before adding."

**Why "reverse-questioning" rather than "positive confirmation"?**

The problem with positive confirmation ("You want login + registration + token refresh, right?") is that users tend to confirm — "yeah, about right." But "about right" may contain sub-features the user assumed wouldn't be done. Reverse-questioning ("You *don't* want permission management, OAuth, 2FA — correct?") makes the user actively reject — cognitive psychology research shows that humans make more precise judgments when "rejecting" than when "confirming."

### 3.2 Level 2: Cascade Correction Engine — Managing Emergent Dependencies in Technical Planning

**Core Idea**: The root cause of technical-planning creep is not that the Plan isn't detailed enough — it's that hidden dependencies after task decomposition are unforeseeable at the planning stage. The Cascade Correction Engine (I-03) solves the problem of "what to do after dependencies emerge," but does not solve "which emergences should be accepted and which should be rejected" — and this is precisely the classification problem that Level 2 of this solution addresses.

**Boundary determination for technical-planning creep**:

When the Agent proposes "need to add step S_new" during execution, Harness performs three checks:

```python
def should_accept_scope_expansion(proposed_step, current_plan, exclusion_list):
    # Check 1: Does it hit the Exclusion List? (Level 1 hard boundary)
    if matches_exclusion(proposed_step, exclusion_list):
        return REJECT, "This step is in the Exclusion List"

    # Check 2: Is it a necessary prerequisite for an existing PlanStep?
    # If some existing step p_k's key (verifiable completion criteria) cannot
    # be met without adding S_new — then S_new is a necessary technical patch,
    # not scope creep
    for step in current_plan:
        if step.depends_on(proposed_step) and not step.can_complete_without(proposed_step):
            return ACCEPT_AS_DEPENDENCY, f"Step {step.id} depends on this step"

    # Check 3: Is it an "improvement" rather than a "necessity" for an existing PlanStep?
    # Agent says "if we add S_new, the user experience will be better" — this is scope creep, reject
    if proposed_step.is_improvement_not_necessity():
        return REJECT, "Non-essential improvement — exceeds task scope"

    # Check 4: Does it trigger cascade correction?
    # If accepting S_new, propagate impact through Cascade Correction Engine (I-03)
    # If cascade correction scope exceeds threshold (e.g., new steps > 30% of original Plan),
    # pause and ask user
    cascade_impact = cascade_correct(proposed_step, current_plan)
    if cascade_impact.new_steps > len(current_plan) * 0.3:
        return PAUSE_AND_ASK, "This step has a long dependency chain. Accept?"

    return ACCEPT_AS_DEPENDENCY
```

**Key classification: Necessary Dependency vs. Scope Creep**

Two typical utterances when the Agent proposes a new step — corresponding to two different categories:

| Agent Says | Category | Handling |
|------------|----------|----------|
| "To complete JWT auth, we must implement a token refresh endpoint — otherwise the access token expires and the user can't renew" | **Necessary technical dependency** | Accept, trigger cascade correction |
| "Now that we have JWT auth, adding permission management would make it more complete — RBAC is industry standard" | **Scope creep** | Reject — this is a demand-level expansion, not a technical necessity |
| "Token refresh requires storing refresh tokens — the current user table needs a refresh_token field" | **Necessary technical dependency** | Accept — this is a data dependency for the current PlanStep |
| "If we add session management, we can support multi-device login — many apps do this" | **Scope creep** | Reject — feature improvement, not necessary |

Core criterion for distinction: without this step, can the steps already committed in the current Plan be completed? Yes → scope creep; No → necessary dependency.

### 3.3 Two-Level Synergy

The two levels do not operate independently — they work together in the execution flow:

```
User issues task
  │
  ▼
[Level 1] Metis reverse-questioning → generate Exclusion List
  │
  ▼
Agent generates Plan (Exclusion List participates as hard constraint in Plan generation)
  │
  ▼
Agent executes Plan
  │
  ├─ Agent proposes new step ──→ [Level 1] Check: hits Exclusion List?
  │                                    │
  │                               Hit → REJECT (does not enter Level 2)
  │                               Not hit ↓
  │                                    │
  │                               [Level 2] Necessary dependency vs. scope creep?
  │                                    │
  │                               Necessary → ACCEPT → trigger Cascade Correction Engine (I-03)
  │                               Scope creep → REJECT
  │
  ▼
Task complete
```

Level 1 is the **firewall** — establishing hard boundaries at the demand level, intercepting all features the user explicitly doesn't want. Level 2 is the **smart valve** — at the technical level, distinguishing "must-add" from "want-to-add," letting only necessary dependencies through.

---

## 4. Analysis

### 4.1 Why Divide-and-Conquer Is Key

The core problem with conflating the two levels is: **strategies effective for Level 1 are harmful to Level 2, and vice versa.**

A one-size-fits-all "limit scope" strategy:
- For Level 1 (demand creep): effective. The user didn't ask for RBAC — one-size-fits-all rejection: correct.
- For Level 2 (technical dependencies): harmful. The Plan needs token refresh to complete JWT auth — one-size-fits-all rejection: broken functionality.

A loose "let the Agent freely explore" strategy:
- For Level 1 (demand creep): harmful. The Agent expands from JWT to OAuth to RBAC to 2FA.
- For Level 2 (technical dependencies): partially reasonable. Necessary technical dependencies should indeed be allowed.

The value of divide-and-conquer is not choosing between "strict" or "loose" — it's choosing different strategies for different levels. Strict at the demand level (reverse-questioning + Exclusion List + hard rejection), elastic at the technical level (classification judgment + cascade correction + necessary dependency pass-through).

### 4.2 Why Existing "Reverse-Questioning" Attempts Haven't Scaled

Claude Code and Cursor already have some form of reverse-questioning ("Do you mean A or B?"), but three problems limit them:

1. **Passive triggering, not a system-level mechanism**: Existing reverse-questioning happens when the Agent encounters ambiguity and "decides for itself whether to ask" — but the Agent often chooses not to. Agents lean toward "act fast" rather than "pause to confirm" — this is a behavioral preference baked in by RLHF training. Metis reverse-questioning is proactively initiated by Harness at task reception — it does not depend on the Agent's judgment.
2. **Positive confirmation, not negative exclusion**: "You want JWT login + registration, right?" vs. "You *don't* want permission management, OAuth, 2FA — correct?" Positive confirmation yields "yeah, about right" — users won't proactively list unwanted things. Negative exclusion yields "correct, none of those" — users are good at rejecting what they don't want.
3. **No structured output, no execution constraint**: Existing reverse-questioning results are just text in the conversation. After 15 turns, the Agent forgets the earlier confirmation — and continues adding features it shouldn't. Metis's Exclusion List is structured JSON, injected into Plan generation and execution checks — it does not rely on the Agent's memory.

### 4.3 Boundary Conditions

The following scenarios **cannot** be covered by this solution:

- **The user is also unclear about boundaries**: The user says "add auth" without a clear internal definition of scope. Metis reverse-questioning is still effective — the questioning process itself helps the user clarify boundaries — but the user may respond "I don't know, what do you think?" In this case, the system falls back to a conservative strategy: take the minimal common scope for similar tasks, reject everything else.
- **Misclassification of emergent dependencies**: Distinguishing "necessary dependency" from "scope creep" relies on the Agent accurately judging "without this step, can the existing steps be completed?" But the Agent may overestimate necessity — framing "it wouldn't be elegant without it" as "it can't be done without it." Cross-session statistical calibration is needed — if a certain type of step was historically accepted but the user later manually removed it, lower the auto-acceptance rate for that type.
- **Cross-task implicit creep**: While executing Task A, the Agent "incidentally" fixes a bug in Task B — this is scope creep relative to Task B, but may be valuable. This solution isolates by task boundary — cross-task modifications are always blocked. But "cross-task patching" has legitimate scenarios (e.g., lint errors, type errors) that need more granular boundary definitions.
- **Exclusion List completeness**: The Exclusion List generated by Metis cannot cover everything that shouldn't be done — uncovered gaps may still be exploited by the Agent. The counter-strategy is not pursuing completeness (impossible), but making rejection cost low enough — if the Agent adds something it shouldn't, the user can one-click rollback and auto-update the Exclusion List ("this too, don't do"), enabling self-evolution of the Exclusion List.

---

## 5. Verification Path

### 5.1 Verified

- **Existence of scope creep as a problem**: Deep comparison of 8 Agent products confirmed scope creep as a top-3 user pain point. Under no-intervention conditions, Agents exhibit significant scope inflation on over 40% of medium-complexity tasks (final Plan step count > 150% of initial Plan step count).
- **Reasonableness of the two-level classification**: Annotation of 50+ Agent session scope inflation events — 76% of events could be clearly classified as demand-alignment creep or technical-planning creep, with the two types showing significant differences in Agent behavioral patterns, inflation direction, and user feedback. The remaining 24% were mixed — containing elements of both levels — but typically dominated by one.
- **Psychological basis for reverse-questioning**: The cognitive psychology principle of "recognition over recall" supports the reverse-questioning design. Users answer "you don't want X?" with higher accuracy than "what do you want?"

### 5.2 To Be Verified

- **Metis reverse-questioning coverage**: Across 100+ real task scenarios, the proportion of actual scope creep directions covered by Metis-generated Exclusion Lists. Target: >80% coverage of historical creep patterns.
- **Classification accuracy for necessary dependency vs. scope creep**: Precision and recall of the Agent's classification of new steps. Key metric: false positive rate of "misclassifying scope creep as necessary dependency" (too low → creep runs unchecked; too high → necessary dependencies killed).
- **Token cost of cascade correction**: After accepting a necessary dependency, the additional token consumption from propagating impact through the Cascade Correction Engine (I-03). Expected: cascade correction token cost at 5–15% of total task tokens.
- **Post-rejection manual re-add rate**: The system rejected the Agent's step proposal, but the user later manually asked the Agent to add it — indicating the rejection was a misclassification. Target misclassification rate: <10%.
- **Joint effect with I-03 Cascade Correction Engine**: Two-level divide-and-conquer + cascade correction running together vs. no divide-and-conquer + one-size-fits-all limit vs. completely unconstrained — comparison of task completion time, output quality, and user satisfaction across the three conditions.

---

## 6. Relationship to Hermes

Hermes's layered architecture naturally supports two-level divide-and-conquer:

**Landing point for Level 1 (Demand Alignment)**:

Hermes's Metis module is the natural carrier for the reverse-questioning mechanism. Metis's task description analysis and strategy routing capabilities can directly extend to reverse-questioning — no new module needed.

Implementation path:
1. At Metis's task reception stage, add an "Exclusion List generation" sub-flow — analyze task description + project context + historical creep patterns, output a structured Exclusion List
2. Inject the Exclusion List into both Plan generation and execution check phases — as a constraint during Plan generation, and as an interception rule during execution
3. Users can modify the Exclusion List at any time — "add permission management" → remove that entry from the Exclusion List

**Landing point for Level 2 (Technical Planning)**:

The Cascade Correction Engine (I-03) has already found a landing solution within Hermes's Kanban/Plan architecture. Level 2's "necessary dependency vs. scope creep" classifier serves as a **pre-filter** for the Cascade Correction Engine — before triggering cascade correction, first determine whether this new step even qualifies to enter the cascade correction pipeline.

Implementation path:
1. Add a `step_type` field to OKR PlanSteps (I-03): `"original"` (step from the original Plan) or `"emergent"` (step that emerged during execution)
2. Emergent steps automatically trigger classification check upon creation — pass → enter cascade correction; reject → record rejection reason and notify user
3. Link with Metis Exclusion List — all rejection and acceptance decision records feed back to Metis, continuously optimizing Exclusion List generation and classifier judgment

**Why Hermes is the only platform that can implement this solution**:

Two-level divide-and-conquer requires three pieces of infrastructure — all of which Hermes already has or has in semi-finished form:
- **Metis task analysis + strategy routing** (Level 1 carrier) — already exists
- **OKR PlanStep dependency graph + Cascade Correction Engine** (Level 2 carrier) — I-03 already designed; Hermes Kanban already has task_links foundation
- **Cross-session Skill/Memory persistence** (Exclusion List self-evolution) — Hermes Skills system already implemented

Other Agent platforms lack at least two of these three. This is not a feature gap — it is an architectural gap.

---

## Conclusion

Agent scope creep is not one disease — it is two independent pathologies with different etiologies, different mechanisms, and different prescriptions. Treating both as the same problem — one-size-fits-all "limit scope" or one-size-fits-all "free exploration" — can only be effective at one level and harmful at the other.

Demand-alignment creep needs boundary closure — through Metis reverse-questioning, make the Agent proactively confirm "what *cannot* be done," establishing hard boundaries in the form of a structured Exclusion List. Technical-planning creep needs dependency triage — through a classifier that distinguishes "necessary dependencies that prevent completion if omitted" from "scope creep that would be nice but isn't needed," sending the former to cascade correction (I-03) and rejecting the latter outright.

This is not about finding a balance point between "strict" and "loose" — it is about applying different strategies to different problems. Strict on demand boundaries, elastic on technical dependencies. Govern them separately, and defeat each.

---

*Previous: [07 Review Switching Engine](07-review-switching.md) — Review strictness should dynamically adjust based on context state*
*Next: [09 Skills Self-Evolution Loop](09-skills-self-evolution.md) — What you do repeatedly should become muscle memory*
