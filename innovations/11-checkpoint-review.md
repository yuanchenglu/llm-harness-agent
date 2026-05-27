# Checkpoint Multi-Round Review: Snapshot-Driven Asynchronous Auditing

> **Innovation Point**: I-12
> **LLM + Harness = Agent** · Part 11
> **Series**: [LLM + Harness = Agent](../README.md)
> **Previous**: [10 Intent Routing: 7+1 Intent → Strategy Auto-Switching](10-intent-routing.md)
> **Next**: [12 Memory Granularity Control](12-memory-granularity.md)

---

> **Abstract**: Every Agent auditing mechanism rests on the same assumption — review happens after the task completes, and the reviewer reads the full execution log. This assumption fails on complex multi-step tasks: by the time the task finishes, the context has ballooned to the point where the reviewer itself can't see clearly. This article proposes Checkpoint snapshot-driven multi-round review: at every critical node during task execution, a structured snapshot is generated (goal + completed step summary + unexpected discoveries + remaining plan), and an independent review sub-Agent is spawned asynchronously. The review Agent reads only the snapshot, not the full execution log. Core counterintuitive property: the second round of review has a *smaller* context than the first — because the remaining plan shrinks with each round. This is not "reviewing repeatedly inside the same context" — it's "re-reviewing from an ever-smaller snapshot each time."

---

## 1. Problem Definition

### 1.1 The Phenomenon

Consider a typical complex Agent task: unifying log formats across 3 microservices, involving modifications to 12 files, 2 cross-service API alignments, and 1 CI configuration update. The Agent takes 45 rounds of conversation to complete. Now, the system needs to audit the final output.

The review Agent faces a 45-round execution log, with the context window near its limit. Between the "goal definition" the Agent sees in the first 20% of context and the "final deliverable" it sees in the last 20%, there lies 60% of intermediate reasoning, tool calls, error retries, and dead-end backtracking. The review Agent's attention has been diluted to the point where it can barely establish a complete causal chain from "goal → deliverable."

The result: review either degenerates into shallow formal checks ("Was the file modified? Yes." — without judging whether the modification was correct), or gets misled by noise from the intermediate process into making incorrect judgments.

A more insidious problem: **review itself consumes context budget**. If execution has already consumed 90% of the context window, review can only operate within the remaining 10%. This means review quality on complex tasks is *squeezed* by context budget — and the very thing squeezing it is the execution process it's supposed to audit.

### 1.2 Root Cause

The root cause lies not in review algorithm quality, but in *when* review happens and *what* the reviewer reads.

Every Agent auditing mechanism rests on two implicit assumptions:

**Assumption 1: Review happens after task completion.** Complete execution → one review. This holds for simple tasks — 3 steps, review sees everything at a glance. But on a 45-step complex task, only at the final moment do you discover step 3 was wrong, and the preceding 42 steps' work all needs to be redone.

**Assumption 2: The reviewer must read the full execution log.** To judge "was it done right," one must know "what was done." But this assumption puts reviewer and executor into the same context dilemma — the executor errs due to context inflation, and the reviewer misses errors due to the very same context inflation.

Together, these two assumptions produce a counterintuitive result: **the more complex the task, the less reliable the review.** Yet complex tasks are precisely the ones that need review the most.

### 1.3 Formalization

Let task T consist of n sub-steps {s₁, s₂, ..., sₙ}, with the context sequence length of the execution process being L(t), where L(t) increases monotonically with t.

Single-round review occurs at t = n (task completion), at which point the review Agent faces a context of length L(n). Let the review Agent's effective attention ratio be α(L), with α(L) ∝ 1/L (determined by Transformer soft attention mechanics). Then review quality Q_review ∝ α(L(n)) ∝ 1/L(n).

That is: **the more complex the task (larger n, larger L(n)), the worse the single-round review quality.** Review quality is inversely proportional to task complexity.

Multi-step tasks also exhibit error accumulation effects: let the probability of step s_i introducing an error be p, and the probability of single-round review detecting it be d. If d < 1 (imperfect review), then the cumulative undetected error count at task completion is E(n) = n·p·(1-d)ⁿ⁻¹ (ignoring error propagation and cascading). The larger n is, the larger the base of E(n).

Core contradiction: complex tasks demand stronger review, but the linear growth of review mechanism context causes review to become *weaker* instead.

---

## 2. Existing Solutions and Limitations

| Solution | Core Idea | Why It Fails |
|----------|-----------|-------------|
| **Single-round final audit (all Agent defaults)** | One full-log review after task completion | Review quality ∝ 1/L(n). On complex tasks the reviewer itself can't see clearly. Errors found too late — a step-3 mistake only discovered at step 45 |
| **Human-in-the-loop** | Pause at critical steps, wait for human confirmation before continuing | Human attention also decays at O(n). And human review latency disrupts Agent execution flow. Cannot scale — no one will click confirm 45 times for a 45-step task |
| **In-execution self-check** | Agent checks its own previous step output after each step | The same Agent checks itself within the same context — using the same attention state that produced the error to discover the error. Self-check miss rate is far higher than independent review |
| **LangChain/LangGraph multi-round review** | Invoke review nodes multiple times within the same conversation flow | Context grows continuously within the conversation flow. The second round's context > the first round's context — review quality degrades with each round |
| **Claude Code's `/review` command** | User manually triggers review; reviewer reads current conversation | Depends on user judgment for trigger timing. And reviewer still reads the full inflated context — same problem as row 1 |
| **Multi-Agent voting (Ensemble)** | 3 Agents review independently, take majority opinion | All 3 review Agents face the same inflated context. Not "3 different perspectives" — it's "3 sets of identically diluted attention." What increases is compute cost, not review quality |

**Shared flaw**: every solution places review inside the **same context space after execution ends**. The correct direction is to **decouple** review from the execution context — the review Agent does not read the execution log; it reads only the structured snapshot extracted at each critical node.

---

## 3. Solution Design

### 3.1 Core Mechanism: Snapshot Extraction → Independent Review → Incremental Correction

This solution consists of three modules:

**Module 1: Checkpoint Snapshot Extraction**

At each critical node during task execution (see 3.2 trigger conditions), the system automatically extracts a structured Checkpoint snapshot. The snapshot format is fixed — it does not depend on Agent judgment; the Harness fills it:

```
Checkpoint #[N]
├── Current Goal: the objective the Agent is executing (extracted from PlanStep)
├── Completed Steps Summary:
│   ├── Step 1: [action description] → [result] (≤2 sentences)
│   ├── Step 2: ...
│   └── Step N: ...
├── Unexpected Discoveries: important, unplanned information found during execution
│   (e.g., "API response format doesn't match documentation," "found an undocumented dependency")
└── Remaining Plan: list of steps yet to execute (extracted from PlanStep)
```

Key design: the snapshot does **not** include full tool-call input/output, intermediate reasoning chains, or complete error stack traces. All of these are structurally compressed during extraction — the review Agent doesn't need to know "the curl command returned 327 lines of JSON," it only needs to know "API call succeeded, returned data structure matches expectations."

**Module 2: Asynchronous Spawn of Independent Review Sub-Agent**

After generating the Checkpoint snapshot, the system spawns an independent review sub-Agent. The review Agent's context **only** contains:

1. The original task goal (extracted from OKR or PlanStep)
2. The concatenation of all snapshots up to the current Checkpoint
3. The global constraint checklist (extracted from the System Prompt's hard constraint layer)

The review Agent does **not** read the executing main Agent's conversation log, tool-call history, or intermediate reasoning process. This ensures the review Agent's attention is not diluted by execution-process noise.

Review Agent's audit tasks:
- Are completed steps aligned with the original goal? (goal alignment check)
- Is there progress deviation? (did completed steps miss any critical planned steps)
- Do unexpected discoveries have security/compliance impact?
- Does the remaining plan need adjustment? (are any steps now unnecessary or needing reordering due to discoveries)

**Module 3: Incremental Injection of Review Results**

The review Agent's output is not a "pass/fail" boolean — it is an **incremental correction suggestion**:

```
Review Result [Checkpoint #N]
├── Goal Alignment Status: ✅ aligned / ⚠️ partial deviation / ❌ severe deviation
├── Deviation Details:
│   └── [specific description of which step deviates from which aspect of the goal]
├── Unexpected Discovery Assessment:
│   └── [impact judgment on security/compliance/architecture]
├── Correction Suggestions:
│   ├── [operations needing rollback]
│   ├── [steps needing supplementation]
│   └── [remaining plan adjustments]
└── Review Confidence: [High / Medium / Low] (reviewer's confidence in its own judgment)
```

Correction suggestions are injected **non-intrusively** into the main Agent's context — as "correction hints" before the next execution round, not forced interruptions. Corrections with "High" confidence are enforced; "Medium" confidence corrections remind but don't block; "Low" confidence corrections are only logged for subsequent review reference.

### 3.2 Trigger Conditions: When to Generate a Checkpoint

Checkpoint triggers cannot be too frequent (review overhead > review benefit) nor too sparse (degenerating into single-round review). There are three trigger categories:

**Condition 1: Step-count threshold trigger.** Trigger a Checkpoint every k completed PlanSteps. Default value of k is 3 — neither reviewing every step (review overhead too high) nor allowing too many steps to proceed unchecked into the next stage (error accumulation effect becomes significant).

**Condition 2: Anomaly event trigger.** Immediately trigger a Checkpoint when the Agent encounters the following during execution:
- Tool call returns unexpected result (e.g., API returns 500, file operation fails but is handled by fallback)
- Agent autonomously modifies PlanStep order or content
- Agent encounters a dead end requiring retreat (executed 2 steps then undid them)

Anomaly triggers are **unskippable** — even if only 1 step has passed since the last Checkpoint. Because anomalies are the moments of highest error risk.

**Condition 3: Phase boundary trigger.** When PlanStep contains explicit phase demarcations (e.g., "Phase 1: Data Migration," "Phase 2: Interface Adaptation"), a Checkpoint is forced after each Phase completes. Phase boundaries are natural review points — Phase 1's output is Phase 2's input; Phase 1's errors will be amplified in Phase 2.

### 3.3 The Fundamental Difference from "Repeated Reviewing in the Same Context"

A common misunderstanding: "How is this different from repeatedly calling review nodes within the conversation flow?"

The essential difference lies in the **review Agent's context starting point**.

In conversation-flow repeated reviewing, the review Agent's context = conversation history + review instructions. Conversation history grows continuously between reviews — the second review's context is larger than the first. Review quality degrades with each round.

In Checkpoint snapshot review, the review Agent's context = Checkpoint snapshot chain + review instructions. The snapshot chain length grows linearly with Checkpoint count, but the growth rate is far lower than conversation history — because snapshots are structurally compressed, each snapshot's token count is fixed (~200-500 tokens), whereas each step in conversation history may consume 500-2000 tokens.

More importantly, **the remaining plan is shrinking**. In Checkpoint #N's snapshot chain, the completed-steps summary is growing in length, but the remaining plan is shrinking. The review Agent's core task is to check "are completed steps aligned with the remaining plan" — and the remaining plan's context volume shrinks with each round. This produces a counterintuitive property: the second round of review has a **smaller** context than the first.

---

## 4. Analysis

### 4.1 The Context-Decreasing Property

This is the most fundamental distinction between this solution and all existing review solutions.

Let the main Agent's context growth over n execution steps be L(t). In traditional single-round review, the review Agent at t=n faces context L(n).

In this solution, let the i-th Checkpoint's snapshot size be S (S is constant, ~300 tokens), and the snapshot chain length for the first m Checkpoints be m·S. The remaining plan size is R(t), where R(t) monotonically decreases as t increases — because steps are being completed one by one.

The review Agent's context at the m-th review is C_review(m) = m·S + R(t_m).

Key property: C_review(m+1) is not necessarily larger than C_review(m). When R(t)'s decline rate exceeds S (the snapshot increment rate) — i.e., the tokens reduced from the remaining plan per completed step exceed the tokens added by a new snapshot — C_review actually *decreases*.

In typical scenarios, one PlanStep description occupies ~100-200 tokens. Every 3 steps completed (one Checkpoint), the remaining plan shrinks by ~300-600 tokens, while a new snapshot adds ~300 tokens. C_review remains roughly flat or slightly declines.

By contrast, in traditional schemes, the (m+1)-th review within the same conversation flow has context = full conversation history + review instructions, which strictly increases.

**Conclusion**: Checkpoint snapshot review achieves context budget "decoupling" — review quality does not linearly degrade with task complexity. This is accomplished by replacing the review Agent's input from "complete record of the execution process" with "structured summary of the execution process."

### 4.2 Edge Cases

**Snapshot quality degradation risk.** Snapshots are generated by the main Agent during execution — if the main Agent's attention is already diluted by context inflation, the snapshots it generates may also omit critical information. This is the most fatal failure mode of this solution: using snapshots generated by a degraded Agent to audit that same Agent's work.

Mitigations:
1. Snapshot extraction is not left to the main Agent's discretion — the Harness mechanically extracts from PlanStep and tool-call returns using a fixed template, reducing reliance on Agent judgment.
2. The "Unexpected Discoveries" field is filled by the Agent, but the Harness simultaneously auto-detects unexpected tool-call returns and forces annotations — anomalies the Agent doesn't record, the Harness can still capture.
3. The review Agent has an obligation to flag "snapshot quality suspect" — if logical contradictions or information gaps are found in the snapshot chain, lower review confidence and mark it.

**Review overhead on short tasks.** When n ≤ 3 (tasks with fewer than 3 steps), the Checkpoint mechanism's overhead (spawning review Agent + generating snapshots) may exceed the cost of a simple final audit. Degradation: when n ≤ k (default threshold), skip Checkpoint triggering and perform a single-round final audit directly.

**Review Agent's own errors.** The review Agent can also make mistakes — misses or false positives. But this solution mitigates review error impact through multi-round **cross-validation**: Checkpoint #N's review can correct #N-1 review misses (because during #N review, #N-1's review result is also in the snapshot chain). This forms a progressive error-correction mechanism.

**Checkpoint density vs. task rhythm conflict.** Some tasks require continuous execution (e.g., "sequentially modify 10 files"), and inserting a review every 3 steps disrupts execution flow. Solution: for homogeneous operation sequences (repeated execution of the same type of operation), Checkpoint's k value can be dynamically adjusted to 5 or higher — single-step error probability is low for homogeneous operations, so sparser review carries manageable risk.

---

## 5. Validation

### 5.1 Technical Feasibility

Checkpoint snapshot review's technical feasibility has been confirmed at three layers:

**Layer 1: Snapshot extraction.** Hermes's PlanStep system already maintains "goal → action → result" structured records for each step. The Harness extracting "completed step summary" and "remaining plan" from PlanStep records is a purely mechanical operation, requiring no Agent reasoning. A 30-line TypeScript function can accomplish the extraction and formatting.

**Layer 2: Independent review Agent spawn.** Hermes's `delegate_task` mechanism already supports spawning sub-Agents for independent tasks. The review Agent uses the same delegate infrastructure as the execution Agent but receives a different context injection — the snapshot chain instead of conversation history.

**Layer 3: Non-intrusive injection of correction suggestions.** Hermes's Memory system can inject review results as "checkpoint summary memory" into the next round's execution context. The injection format is structured Markdown, with controllable context budget consumption (~200-500 tokens/review).

Implementation at all three layers involves no core architecture changes — it is a "composition" of existing mechanisms, not a "restructuring."

### 5.2 CI/CD Analogy Validation

The design pattern of Checkpoint snapshot review has a mature analogy: CI/CD pipeline checkpoints.

CI/CD does not perform a comprehensive code review and test after code is merged into the main branch — it inserts independent checks at each stage (lint → unit test → integration test → deploy). Each stage's check only examines that stage's inputs and outputs, not the entire pipeline log.

Agent task execution is essentially also a pipeline — a linear sequence of steps. Existing single-round final audit is equivalent to "not inserting any checkpoints in the pipeline, only doing a full regression after final deployment." This is unreasonable — the CI/CD industry rejected this pattern 20 years ago.

Checkpoint snapshot review transplants this mature pipeline pattern onto Agent task execution. The difference is that Agent task pipelines are **dynamically generated** (PlanStep is planned before execution but may be adjusted during execution), while CI/CD pipelines are static — meaning Checkpoint triggering needs dynamic judgment rather than predefinition.

### 5.3 To Be Validated

- **Snapshot compression rate vs. review precision tradeoff.** The higher the snapshot compression rate (fewer tokens), the cleaner the review context; but too high a compression rate loses critical information needed for review. Experimental determination of the optimal compression rate — with "review miss rate" as the dependent variable and "snapshot token count" as the independent variable, find the inflection point.
- **Optimal k value (Checkpoint interval step count).** k=1 (review every step) gives the highest review quality but the highest overhead; k=n (no Checkpoint) has zero overhead but degenerates into single-round final audit. The optimal k depends on average task step complexity and error propagation rate. Parameter scanning on a large-scale task set is needed.
- **Review Agent's "over-trust" of compressed snapshots.** The review Agent reads only snapshots, meaning it trusts snapshot accuracy. If snapshots omit critical errors (as described in 4.2 above), will the review Agent systematically overestimate snapshot completeness? Testing is needed on "whether the review Agent proactively flags uncertainty when snapshot information is incomplete."

---

## 6. Relationship with Hermes

Hermes already possesses most of the infrastructure needed for Checkpoint snapshot review:

1. **PlanStep system**: Hermes's OKR → PlanStep cascade provides the structured data source for "completed step summary" and "remaining plan." Snapshot extraction doesn't need to build data from scratch — PlanStep *is* the data source.

2. **delegate_task sub-Agent mechanism**: Hermes already supports spawning sub-Agents for independent tasks. The review Agent reuses the same spawn infrastructure — the only difference is that the injected context is the snapshot chain rather than conversation history. One `delegate_task` call + snapshot injection template achieves it.

3. **Memory three-layer injection architecture**: Review results can be injected as "checkpoint review memory" into the Memory layer of the Base/Skills/Memory three layers. Injection timing is after Checkpoint review completes and before the next execution round begins.

4. **Kanban Worker's Checkpoint granularity alignment**: Hermes's Kanban Worker already maintains state transitions during task execution (TODO → IN_PROGRESS → DONE). Each state transition is a natural Checkpoint trigger point — when a Worker pulls a step from IN_PROGRESS to DONE, the Harness checks whether to trigger a Checkpoint snapshot.

Parts needing completion:

1. **Checkpoint trigger logic**: Add trigger judgment in the Kanban Worker's state transition path — step-count threshold counter, anomaly detection, phase boundary identification. Estimated ~100 lines of TypeScript.
2. **Snapshot format template**: Define the structured template for Checkpoint snapshots and filling rules. The Harness mechanically extracts most fields from PlanStep records; only the "Unexpected Discoveries" field relies on Agent filling.
3. **Review Agent System Prompt**: A dedicated System Prompt for snapshot review — defining review granularity, confidence annotation rules, and correction suggestion output format. This is the part most needing polish — review Prompt quality directly determines review quality.

All three completions involve no Hermes core architecture changes. Checkpoint snapshot review is a "vertical composition" of Hermes's existing capabilities — threading PlanStep, delegate_task, and Memory into a review pipeline.

---

## Conclusion

Agent review should not happen in the inflated context after task completion — it should happen at each critical node, independently, from clean structured snapshots. Checkpoint snapshot-driven multi-round review achieves decoupling of review quality from task complexity through the three modules of "snapshot extraction → independent review → incremental correction." The core counterintuitive property — review context decreasing — derives from a simple fact: snapshots are not compressed versions of execution logs; they are structured summaries of execution semantics. The summary is shorter than the original, and the remaining steps get fewer with each review.

This is not a new AI capability — it is the "pipeline checkpoint" pattern validated by the CI/CD industry 20 years ago, applied to Agent task execution. The Agent's PlanStep is a dynamic pipeline; the Checkpoint is the quality gate within that pipeline. Transplanting a mature engineering pattern onto a new execution paradigm is more reliable than inventing a review mechanism from scratch.

---

*Next: [12 Memory Granularity Control](12-memory-granularity.md)*
