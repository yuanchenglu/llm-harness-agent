# Checkpoint-Driven Multi-Round Review: State Snapshots Must Connect to Original Evidence

> **Evidence level: B (engineering design proposal)**  
> This article no longer assumes that “all Agents review only at the end of a task,” and it no longer uses an unverified formula in which review quality is inversely proportional to context length. The core value of a Checkpoint is preserving execution state, recovery conditions, and Evidence so a Reviewer can work within a controlled context and retrieve original Artifacts when needed. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-11  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [10 Intent-to-Strategy Routing](10-intent-routing.md)  
> **Next**: [12 Memory Granularity Control](12-memory-granularity.md)

---

## Abstract

Complex tasks require repeated confirmation during execution:

- is the current objective still aligned?
- do completed Steps have evidence?
- has the Workspace changed unexpectedly?
- can the system recover safely after failure?
- does the remaining Plan still hold?
- should review or human intervention be escalated?

Reading a complete conversation only at the end is not the only review method. But reading only a model-generated summary is equally dangerous: a summary can omit failure, misattribute causes, or turn an unverified judgment into fact.

A Checkpoint should therefore be:

> A versioned, verifiable, recoverable snapshot of task state in which natural-language summaries act only as an index, while completion decisions connect to Diff, Test, Tool, Approval, and Artifact Evidence.

---

## 1. Public Corrections

### 1.1 A Checkpoint is not merely a summary

Insufficient design:

```text
objective + completed summary + remaining plan
```

This is useful for orientation but insufficient for recovery or audit. At minimum include:

```text
state version
workspace hash
plan version
changeset ids
artifact hashes
test run ids
approval ids
open errors
resume preconditions
```

### 1.2 A Reviewer should not read only the summary

A Reviewer may begin with a compact Snapshot, but must be able to retrieve original evidence:

```text
Snapshot
→ Evidence Index
→ Original Diff / Test / Tool Result / Source File
```

Otherwise Summary Laundering occurs: the execution Agent’s incorrect summary is accepted by the Reviewer as verified fact.

### 1.3 “Smaller context” is not an automatic quality guarantee

A smaller Review Context may reduce noise or remove critical evidence. Measure:

- critical-source coverage;
- defect detection rate;
- incorrect citation rate;
- review cost;
- recovery success.

Fewer tokens alone do not prove a more reliable review.

### 1.4 Asynchronous review must handle state drift

After a Reviewer loads a Checkpoint, the main Agent may continue changing the Workspace. A Verdict must bind to:

```text
checkpoint_id
workspace_hash
plan_version
changeset_hash
```

After state changes, the old Verdict is historical evidence only and cannot authorize new actions.

---

## 2. Checkpoint Data Model

```yaml
checkpoint_id: cp-0007
task_id: task-123
sequence: 7
created_at: 2026-07-27T00:00:00Z
runtime_version: 0.1.1
state_version: 42
workspace:
  root_id: workspace-a
  git_commit: abcdef123456
  dirty_tree_hash: sha256:...
objective:
  spec_ref: spec-12
  text: Fix permission boundaries and add regression tests
plan:
  version: 8
  current_step_id: step-4
  completed_step_ids:
    - step-1
    - step-2
  pending_step_ids:
    - step-4
    - step-5
changesets:
  proposed:
    - cs-19
  applied:
    - cs-18
evidence:
  test_run_ids:
    - test-88
  tool_event_ids:
    - tool-991
  artifact_refs:
    - diff:cs-18
    - report:security-scan-7
approvals:
  - approval-55
open_issues:
  - id: issue-local-3
    severity: medium
    text: Windows symlink test has not been run
resume:
  idempotency_key: resume-task-123-cp-7
  preconditions:
    - workspace_hash_unchanged
    - approval_still_valid
summary:
  completed: Workspace boundary check has been added
  next: Add Windows and symlink regression tests
integrity:
  previous_checkpoint_hash: sha256:...
  checkpoint_hash: sha256:...
```

### 2.1 Required fields

```text
checkpoint_id
task_id
sequence
state_version
workspace identity/hash
objective/spec ref
plan version/current step
changeset refs
evidence refs
approval refs
open issues
resume preconditions
integrity hash
```

### 2.2 Summary fields

The summary is for navigation only:

- it is not the only completion evidence;
- it does not overwrite original errors;
- it does not mutate historical Artifacts;
- every material claim must trace to an Evidence Ref.

---

## 3. Trigger Policy

A Checkpoint is not required for every Step. Triggering depends on risk and state changes.

### 3.1 Mandatory triggers

- before applying a ChangeSet;
- after applying a ChangeSet;
- before a high-risk tool call;
- after user Approval;
- before Compaction;
- before switching Runtime / Provider / Tool Schema;
- before a long task pauses or exits;
- when the retry budget is exhausted;
- before human takeover.

### 3.2 Conditional triggers

- completion of a Plan subgraph;
- discovery of a new dependency;
- a changed Spec or objective;
- a Test changes from passing to failing;
- degraded context health;
- cost or time reaches a threshold.

### 3.3 Do not trigger for

- every Chunk of streamed text;
- stateless, replayable read-only operations;
- internal reasoning that creates no new state or Evidence.

---

## 4. Reviewer Workflow

```text
Load Checkpoint
→ Validate Integrity
→ Verify State Is Current
→ Read Spec and Open Risks
→ Inspect Evidence Index
→ Fetch Required Original Artifacts
→ Run/Read Deterministic Verifiers
→ Produce Structured Verdict
→ Bind Verdict to Checkpoint Hash
```

### 4.1 Minimum Reviewer input

Load by default:

- Objective / Spec;
- current Checkpoint;
- relevant constraints;
- Open Issues;
- Evidence Index.

Do not load by default:

- the full execution conversation;
- all tool logs;
- raw chain-of-thought;
- unrelated historical Sessions.

### 4.2 On-demand Reviewer reads

- relevant Diff;
- modified files;
- Test Logs;
- Static Analysis;
- Tool Results;
- previous Checkpoint;
- failure samples;
- Approval content.

### 4.3 Structured Verdict

```yaml
review_id: review-cp-7
checkpoint_id: cp-0007
checkpoint_hash: sha256:...
verdict: changes_required
risk: R2
findings:
  - severity: high
    claim: Windows compatibility has not been verified
    source_refs:
      - checkpoint:cp-0007:open_issues:issue-local-3
missing_evidence:
  - windows_symlink_test
required_actions:
  - run_windows_compatibility_suite
confidence: high
reviewer:
  type: independent_model
  model: deepseek-v4-pro
created_at: 2026-07-27T00:00:00Z
```

A Verdict does not directly mutate main state. The Orchestrator uses Policy to block, warn, retry, or request a user decision.

---

## 5. Multi-Round Review

### 5.1 Review target for each round

Review the increment relative to the last accepted Checkpoint:

```text
previous accepted checkpoint
+ current changesets
+ new evidence
+ changed plan/constraints
```

The Reviewer may still traverse older evidence and must not be restricted to an incremental summary only.

### 5.2 Verdict inheritance

An earlier Verdict may be inherited only when all of the following remain unchanged:

```text
spec version
constraint versions
workspace base hash
relevant file hashes
tool schema fingerprint
runtime version
```

Otherwise revalidate the affected portion.

### 5.3 Cascading invalidation

When a Step or Artifact changes:

- related Verdicts become `stale`;
- downstream PlanSteps become `pending_review`;
- Approval bound to an old Hash expires;
- Resume begins from a new Checkpoint.

---

## 6. Recovery Semantics

### 6.1 Pre-resume checks

```text
workspace exists
workspace hash matches or divergence is explained
runtime/provider versions are compatible
pending approvals are still valid
already-applied side effects are not repeated
required secrets are available but not serialized
```

### 6.2 Idempotency

Every retryable action requires an `idempotency_key`. Before resuming, inspect Evidence:

```text
if the action was committed successfully
→ do not execute again
if action state is unknown
→ require human confirmation or a safe probe
```

### 6.3 Irreversible actions

External email, payments, and production deletion cannot be rolled back by a Checkpoint alone. Use:

- pre-generation + approval;
- Dry Run;
- external-system idempotency keys;
- compensating transactions;
- human change-management processes.

---

## 7. Evidence Integrity

### 7.1 Hash chain

Checkpoints may form a hash chain:

```text
checkpoint_hash = hash(
  canonical_checkpoint_without_hash
  + previous_checkpoint_hash
)
```

Uses:

- detect historical modification;
- fix Review input;
- support exportable audit bundles.

It cannot prevent an actor with write permission from rewriting the entire chain. Git commits, signatures, or external attestation provide stronger boundaries.

### 7.2 Redaction

Do not write into a Checkpoint:

- API keys;
- Authorization headers;
- passwords;
- complete private file contents;
- raw chain-of-thought.

Use redacted summaries, Artifact IDs, and hashes.

---

## 8. Validation Metrics

### 8.1 Review Quality

```text
defect detection rate
false approval rate
false rejection rate
source citation accuracy
missing evidence detection
```

### 8.2 Recovery

```text
resume success rate
duplicate side-effect rate
stale approval rejection rate
rollback success rate
mean time to recover
```

### 8.3 Cost

```text
checkpoint storage
review prompt tokens
artifact fetch tokens
review latency
cost per prevented defect
```

### 8.4 Controlled experiment

Compare:

```text
full-history final review
summary-only checkpoint review
traceable checkpoint + on-demand evidence review
```

Use the same defect set and held-out tasks and report quality, cost, latency, and recovery outcomes.

---

## 9. Boundaries and Risks

- the Snapshot generator may omit fields;
- the Evidence Index may point to the wrong version;
- a correct Hash does not prove truthful content;
- the Reviewer may fail to fetch a critical Artifact;
- asynchronous Review may lag behind main state;
- too many Checkpoints increase storage and complexity;
- too few Checkpoints increase recovery loss;
- a summary may hide uncertainty.

Schema Validation, Integrity Check, Stale Detection, Evidence Fetch, and human takeover are required.

---

## 10. Conclusion

The value of a Checkpoint is not merely compressing long history into a short summary. It establishes:

1. versioned state;
2. recoverable preconditions;
3. traceable Evidence;
4. Review Verdicts bound to concrete hashes;
5. cascading invalidation after state changes;
6. idempotent semantics that prevent duplicate side effects.

A Reviewer may use a smaller default context, but every conclusion must trace to original Diff, Test, Tool, and Approval Evidence. Small context is a means; auditable completion is the objective.
