# Attention Budget Management: From a “Dilution Law” to Testable Context Allocation

> **Evidence level: B (engineering design proposal)**  
> This article examines how a Harness controls model-visible information, interference, and verification cost. It no longer presents “attention must decay as `1/L` when context grows” as a physical law of Transformers. Any quality gain must be confirmed with a fixed model, a fixed task set, and reproducible experiments. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-03  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [02 Model Meta Requests](02-bidirectional-agent.md)  
> **Next**: [04 Stable Constraints and Compressible History](04-kv-cache-prefix.md)

---

## Abstract

In long-running tasks, an Agent may omit constraints, drift from the objective, select the wrong tool, reread the same material, or produce weaker reviews. These symptoms cannot be reduced to “attention is averaged away.” A more accurate engineering question is:

> Under finite context, cost, and latency budgets, what information should the Harness expose to the model, in what structure, which rules must be deterministically enforced by the Runtime, and which results must be verified by external evidence?

This article defines “attention budget” as a product-engineering concept rather than a mathematical quantity derivable directly from sequence length. The core design is:

1. move safety and permission constraints into a deterministic Runtime;
2. separate stable rules, the active working set, historical evidence, and external indexes;
3. disclose Skills, Memory, and tool catalogs on demand;
4. isolate subtasks while preserving traceability from summaries to original evidence;
5. compare compaction, retrieval, and layout strategies through task-level benchmarks;
6. treat Prefix Cache only as cost and latency telemetry, not as a quality guarantee.

---

## 1. Public Corrections

### 1.1 `O(n²)` does not imply that each token receives only `1/n` attention

For standard full attention, `O(n²)` describes how the number of Query-Key pairings grows with sequence length. The actual attention weight assigned to a token depends on Queries, Keys, layers, heads, positional encoding, training distribution, and task content. Uniform allocation is not required.

The following derivation is therefore not a fact:

```text
Sequence length grows
→ every instruction’s weight must equal 1/L
→ constraint compliance must be proportional to 1/L
```

Long context may increase retrieval difficulty, interference, position sensitivity, and cost. Whether degradation occurs, when it occurs, and by how much must be measured for a specific model and task.

### 1.2 Long-conversation degradation is not necessarily monotonic or irreversible

Quality changes may be caused by:

- relevant information was not retrieved;
- newer instructions conflict with older instructions;
- tool results are too long or badly formatted;
- earlier errors propagate forward;
- a compacted summary omits a critical fact;
- the model or tool changes;
- the user’s objective changes during a multi-turn interaction;
- the Runtime does not deterministically enforce permissions, state, or completion criteria.

Re-retrieval, cleaning tool results, rebuilding the active working set, rolling back incorrect state, or switching to an isolated review context can restore quality. It is therefore inaccurate to claim that “continuing the conversation can only make it worse” as a universal rule.

### 1.3 The historical `40% → 95%` numbers are downgraded

Earlier drafts claimed:

- constraint retention increased from roughly `40%` to `>95%`;
- each task saved `8K–35K` tokens;
- context growth slowed by roughly `60%`.

Those numbers lack a complete task set, Runner, raw results, random seeds, baseline definitions, statistical testing, and independent reproduction. They remain only as historical self-test clues and must not enter the README, product promises, or Release Gates.

### 1.4 Prefix Cache is not model attention and not constraint compliance

The following must be measured separately:

| Concept | Question | Typical metrics |
| --- | --- | --- |
| Context retention | Is the information still present in the request? | field/message/summary completeness |
| Prefix Cache | Did the Provider reuse computation for a shared prefix? | hit/miss tokens, TTFT, cost |
| Information retrieval | Did the model locate relevant content? | retrieval accuracy, citation correctness |
| Constraint compliance | Did the final action satisfy the rule? | violation rate, policy blocks |
| Task quality | Was the task completed correctly? | first-pass success, tests, human intervention |

A high prefix hit rate does not prove that the model followed constraints. The presence of constraint text also does not prove that the model will execute it.

---

## 2. Problem Definition

### 2.1 What a Harness can actually control

A Harness cannot directly allocate attention weights inside every model layer. It can control model input and the execution environment:

```text
visible information set
information order and structure
tool Schemas and tool results
Memory / Skill disclosure scope
compaction and retrieval strategy
subtask boundaries
permissions and side effects
Verifiers and completion conditions
model, budget, and retry policy
```

A more accurate definition of “attention budget management” is therefore:

> Joint allocation of model-visible information, deterministic rules, inference cost, and verification resources by the Harness.

### 2.2 Quality model

Instead of expressing task quality as a `1/L` function, use an experimentally decomposable form:

```text
TaskQuality = f(
  model,
  task,
  relevant_context_recall,
  instruction_conflict,
  tool_result_quality,
  context_layout,
  state_correctness,
  policy_enforcement,
  verifier_quality,
  retry_budget
)
```

This expression does not claim a closed-form solution. Its value is decomposing possible causes into variables that can be independently controlled and measured.

---

## 3. Design

### 3.1 Move deterministic constraints into the Runtime

The following rules should not depend only on a Prompt:

- writing outside the Workspace is prohibited;
- `.git` and protected paths may not be modified;
- high-risk actions require approval;
- if the original file hash changes after approval, Apply is rejected;
- when the budget is exceeded, stop at a Checkpoint;
- a task cannot be marked complete while tests fail;
- irreversible tools require separate authorization.

The model may explain a rule, propose an action, and generate a candidate solution, but final execution authority belongs to Policy, Sandbox, ChangeSet, and Verifier components.

### 3.2 Four context zones

```text
Stable Rules Zone
  system role, approved project rules, stable tool contracts

Append-Only Evidence Zone
  decisions, tests, Checkpoints, review conclusions, failure reasons

Active Working Set
  current objective, relevant file excerpts, recent tool results, unresolved risks

External Index
  full traces, historical Sessions, archived documents, Skill Bodies loaded on demand
```

The purpose of zoning is not to claim that “earlier tokens always receive more attention.” It is to:

- make information lifecycles explicit;
- avoid sending the full history by default;
- limit compaction to zones explicitly allowed to be compacted;
- keep Evidence and original Artifacts traceable;
- provide stable-prefix candidates for Prefix Cache.

### 3.3 Disclose Skills, Memory, and tools on demand

Load only indexes and short descriptions by default. Read full Bodies, detailed Memory, and infrequently used tools only when they match the current task.

On-demand disclosure introduces two risks:

1. **missed retrieval**: a relevant Skill or tool is not loaded;
2. **incorrect retrieval**: unrelated or malicious content is loaded, increasing interference or permission risk.

Record:

```text
candidate set
selected items
selection reason
confidence
fallback behavior
missed dependency
```

### 3.4 Subtask isolation

A subtask can use an independent Session so the main thread does not absorb the complete tool trace. But a returned summary must not become an unsourced “new fact.” It should include at least:

```text
source files / tool calls
diff or artifact hash
tests executed
unverified assumptions
failure samples
```

The main Agent and Reviewer must be able to trace a summary back to original evidence rather than trusting another model’s natural-language conclusion.

### 3.5 Checkpoints and compaction

A Checkpoint stores task state and an evidence index, not merely a summary:

```text
objective
approved scope
completed steps
pending steps
changeset ids
test results
open risks
source refs
resume preconditions
```

A compactor may rewrite historical narration, but it must not overwrite:

- approved constraints;
- current Workspace and version;
- unresolved errors;
- Diff / Test / Approval / Rollback Evidence;
- idempotency keys and state versions required for resume.

### 3.6 Prefix Cache telemetry

Record:

```text
prefix fingerprint
prefix length
hit tokens
miss tokens
drift reason
TTFT
total latency
input/output tokens
estimated cost
```

Cache optimization is valid only when all of the following hold:

- task quality does not decline;
- permission scope does not expand;
- security updates can explicitly invalidate an old prefix;
- total cost or latency improves reproducibly.

---

## 4. Validation Design

### 4.1 Experimental factors

For the same held-out tasks, control the following variables:

| Factor | Control | Treatment |
| --- | --- | --- |
| Context layout | Append full history | Four-zone layout + active working set |
| Skill | Load all | Index + on-demand Body |
| Tool results | Raw full output | Cleaned, truncated, Artifact-referenced |
| Subtasks | Shared history | Independent Session + returned Evidence |
| Compaction | Free-form summary | Structured Checkpoint + source index |
| Safety rules | Prompt constraints | Runtime Policy |

### 4.2 Core metrics

Primary metrics:

```text
first-pass task success
success within retry budget
constraint violation rate
incorrect tool-call rate
human intervention rate
rollback rate
source citation accuracy
```

Resource metrics:

```text
prompt/output tokens
cache hit/miss tokens
TTFT
total latency
cost per successful task
```

A report must not show token reduction while omitting correctness and failure samples.

### 4.3 Dataset discipline

Separate:

```text
development set
prompt-tuning set
validation set
final held-out test set
```

Task-specific acceptance hints, Verifier feedback, and multi-round retries must be recorded. A tuned final completion rate must not be presented as first-pass generalization success.

---

## 5. Boundaries and Risks

- for short tasks, retrieval, classification, and snapshot overhead may exceed the benefit;
- excessive isolation can lose cross-task dependencies;
- a summary may invent facts or hide failures;
- on-demand tool disclosure may miss a critical tool;
- a fixed prefix may obstruct security-rule updates;
- stricter review increases cost and does not guarantee compensation for insufficient model capability;
- Provider Cache behavior may change by time, region, account, or Endpoint.

Every strategy must therefore support:

```text
disable
fallback
rebuild context
invalidate cache
escalate to user
reproduce from evidence
```

---

## 6. Conclusion

“Attention budget” is a useful engineering metaphor, not a physical law of `α = 1/L`.

A reliable Harness does not use slogans to make the model “remember more.” It:

1. removes irrelevant input;
2. converts non-negotiable rules into Runtime Policy;
3. keeps state and Evidence traceable;
4. loads necessary information per task;
5. validates real quality, cost, and latency changes on held-out tasks.

A context strategy should become a product default only when experiments show that correctness does not decline, risk does not increase, and cost per successful task or latency improves consistently.
