# Agent Immune System: From Prompt Violations to Auditable System Hardening

> **Evidence level: B (engineering design proposal)**  
> This article no longer treats “a model inevitably forgets the Prompt in long conversations” as a physical law of Transformers, nor does it claim that automatically generated Skills can raise compliance to 100%. The central question is: when an Agent produces a reproducible violation, how should the Harness turn one failure into an auditable, testable, and reversible system improvement? Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-01  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Next**: [02 Brain Actively Drives the Cerebellum](02-bidirectional-agent.md)

---

## Abstract

An Agent may violate a constraint because of instruction conflicts, missing context, retrieval errors, noisy tool results, stochastic model behavior, or absent Runtime enforcement.

The conventional repair pattern is usually:

```text
Observe one error
→ add another reminder to the System Prompt
→ the Prompt keeps growing
→ the same class of error can still recur
```

An “Agent Immune System” should instead be defined as a system-hardening loop:

```text
Violation event
→ preserve evidence
→ classify root cause
→ propose a repair
→ select the correct control layer
→ test and approve
→ enable within a limited scope
→ monitor recurrence and side effects
→ retain rollback
```

The key principle is:

> Not every failure should generate a Skill. Non-negotiable safety constraints should first become Runtime Policy, Schema, tests, or permission rules. A Skill is suitable only for reusable, explainable process knowledge that still requires model participation.

---

## 1. Public Corrections

### 1.1 A Prompt violation does not necessarily mean “the model forgot”

When a constraint is not followed, at least the following explanations are possible:

- the constraint never entered the current request;
- the constraint conflicted with a newer user instruction;
- compaction or retrieval omitted the constraint;
- the model saw the constraint but selected the wrong action;
- the Tool Schema induced an incorrect parameter choice;
- the Runtime did not block a prohibited side effect;
- the Verifier failed to detect the error;
- the constraint itself was ambiguous, non-executable, or internally inconsistent.

Without evidence, these cases cannot all be attributed to “attention dilution” or “Prompt forgetting.”

### 1.2 More turns do not necessarily produce monotonically lower compliance

Different models, tasks, Prompt layouts, and toolchains can produce different curves. Re-retrieving rules, rebuilding context, switching to an independent Session, or moving a constraint into Runtime Policy can restore quality.

### 1.3 Automatically generating a Skill is not inherently a repair

An incorrect Skill can become a persistent supply-chain risk:

```text
Malicious or incorrect context
→ generate Skill
→ automatically load it across tasks
→ expand permissions or institutionalize an incorrect process
```

A Skill therefore requires provenance, permission limits, tests, approval, versioning, expiration, and rollback.

### 1.4 “A unique innovation no one else has addressed” is not a defensible claim

The industry already contains Policies, Guardrails, Verifiers, Hooks, Skills, Memory, incident learning, and automatic rule proposals. The value of this design is not uniqueness; it is the integration of those mechanisms into a strict failure-hardening loop.

---

## 2. Violation Event Model

Every violation should be preserved as a structured event:

```yaml
incident_id: inc-20260727-001
task_id: task-123
constraint_id: workspace-boundary@3
expected: Only the approved Workspace may be modified
observed: Attempted to write ../shared/config.yaml
blocked: true
source_refs:
  - tool-call-882
  - policy-event-991
model: deepseek-v4-pro
runtime_version: 0.1.1
context_fingerprint: sha256:...
severity: critical
status: investigating
```

At minimum, record:

```text
incident_id
task_id
constraint_id / requirement_ref
expected behavior
observed behavior
model / provider / runtime version
context fingerprint
tool and artifact references
whether a side effect occurred
severity
```

Do not record complete private Prompts, API keys, or raw chain-of-thought.

---

## 3. Root-Cause Classification

### 3.1 Context Failure

- the constraint did not enter the request;
- Retrieval missed it;
- Compaction removed it;
- an old summary overrode newer facts;
- the wrong Session was restored.

Candidate repairs: Context Compiler, Constraint Registry, Checkpoint, Retrieval Test.

### 3.2 Model Compliance Failure

- the constraint was present and non-conflicting, but the model still proposed a violating action;
- the model selected the wrong tool or parameters;
- the model assessed risk incorrectly.

Candidate repairs: clearer instructions, structured output, an independent Reviewer, or model routing. High-risk actions should still be blocked by the Runtime.

### 3.3 Runtime Enforcement Gap

- a path that should have been rejected was allowed;
- Approval could be bypassed;
- a stale Diff could still be applied;
- an irreversible tool lacked a separate permission.

Candidate repairs: Policy, Sandbox, Schema, state machine, idempotency, and hash verification.

### 3.4 Requirement Defect

- the constraint was ambiguous;
- two rules conflicted;
- the user’s objective changed;
- the completion criterion was not verifiable.

Candidate repairs: clarification, versioned Specs, conflict resolution, and user approval.

### 3.5 Verifier Failure

- test coverage was insufficient;
- the Reviewer read only a summary without source evidence;
- a failed task was classified as successful;
- an acceptance heuristic overfit the development set.

Candidate repairs: held-out tests, evidence traces, Verifier diversity, and manual review of failure samples.

---

## 4. Selecting the Repair Layer

A repair must be placed in the correct layer:

| Problem | Preferred control layer | Not recommended |
| --- | --- | --- |
| Writing outside the Workspace is prohibited | Runtime Policy | Only adding a Prompt reminder |
| Output must conform to a JSON Schema | Schema Verifier | Relying on the model to claim correctness |
| Approval is required before modification | ChangeSet state machine | A Skill checklist |
| A framework upgrade follows a fixed procedure | Governed Skill | Hard-coding it into the core Runtime |
| The project requires Python 3.11 | Environment Check + Project Policy | Repeating a long reminder every turn |
| The user prefers a particular comment style | Project Memory / Style Rule | System-level security policy |

Decision rules:

```text
If deterministic code can verify it, do not rely only on a Prompt
If it creates a side effect, do not rely only on model judgment
Use a Skill only when knowledge should be reusable across tasks but remains context-dependent
```

---

## 5. The Hardening Loop

### 5.1 Detect

Signals include:

- Runtime Policy Block;
- Test Failure;
- Reviewer Verdict;
- user correction;
- Rollback;
- Incident Replay;
- task-failure clustering.

### 5.2 Preserve

Preserve:

```text
Diff Hash
Tool Call ID
Test Run ID
Policy Event
Artifact Hash
Runtime / Model Version
```

### 5.3 Diagnose

The same execution Agent must not determine the root cause solely through natural-language self-assessment. Prefer deterministic evidence. Model-based diagnosis must carry a confidence value and alternative explanations.

### 5.4 Propose

Repair types:

```text
policy_patch
test_patch
schema_patch
context_rule
skill_proposal
documentation_fix
model_route_change
```

### 5.5 Validate

Every repair should include at least:

- a failing test that reproduces the original incident;
- a passing test after the repair;
- regression tests for unrelated tasks;
- permission and side-effect checks;
- performance and cost changes;
- rollback instructions.

### 5.6 Approve

Approval strength depends on scope:

| Scope | Approval |
| --- | --- |
| Temporary rule for the current task | User or task owner |
| Project-level Skill / Policy | Project maintainer |
| Global Runtime Policy | Security owner + maintainer |
| Cross-user automatic Skill | Disabled by default; requires higher-level review |

### 5.7 Canary

Initially constrain:

```text
workspace
project
user
model
runtime version
time window
```

Observe false blocks, missed blocks, cost, and task success before widening the scope.

### 5.8 Monitor recurrence and side effects

Record:

```text
incident recurrence rate
false-positive block rate
false-negative rate
rollback rate
first-pass success
human override
cost per successful task
```

### 5.9 Rollback

Every automatically proposed hardening item must be versioned, disableable, and reversible, and must preserve the link between the original incident and the repair.

---

## 6. Governed Skill Specification

```yaml
skill_id: python-migrate-pyproject
version: 1.2.0
origin:
  incident_ids: []
  successful_task_ids:
    - task-456
scope:
  workspaces:
    - project-a
permissions:
  tools:
    - read_file
    - propose_patch
  network: false
  write_requires_approval: true
tests:
  - fixture-basic
  - fixture-custom-build
reviewed_by:
  - maintainer@example
expires_at: 2026-10-27
content_hash: sha256:...
rollback_to: 1.1.0
```

Requirements:

- minimum scope by default;
- least privilege by default;
- disabled by default after automatic generation;
- users can inspect content and provenance;
- cross-project enablement requires renewed approval;
- changing content invalidates the hash and approval;
- long-term non-use or repeated failures should trigger a disablement recommendation.

---

## 7. Validation Design

### 7.1 Dataset

Include:

- known historical violations;
- similar negative samples that should not trigger;
- held-out samples from new projects;
- malicious Prompt Injection;
- conflicting constraints;
- version-upgrade scenarios.

### 7.2 Metrics

```text
incident detection precision / recall
root-cause classification accuracy
policy false positive / false negative
skill trigger precision / recall
regression pass rate
recurrence rate
human override rate
rollback success rate
```

### 7.3 Control groups

Compare:

```text
Prompt-only reinforcement
vs.
Prompt + Runtime Policy / Test / Governed Skill
```

Side effects must be reported; it is insufficient to report only whether the original incident disappeared.

---

## 8. Boundaries and Risks

- the Reviewer can also make incorrect judgments;
- automatic root-cause analysis may mistake correlation for causation;
- excessive hardening can create many false blocks;
- Skill matching may be too broad or too narrow;
- security policy may conflict with the user’s objective;
- historical incidents may no longer apply to a new version;
- automatic learning can be poisoned by Prompt Injection.

The system must therefore retain human takeover, evidence replay, scope restrictions, expiration, and rollback.

---

## 9. Conclusion

An Agent Immune System is not “the model forgot once, so automatically generate a Skill.”

A more reliable loop is:

1. preserve a violation as a reproducible Incident;
2. distinguish Context, Model, Runtime, Requirement, and Verifier root causes;
3. place the repair in the correct control layer;
4. govern persistent Skills as supply-chain artifacts;
5. prove the improvement through tests, approval, canary rollout, monitoring, and rollback.

Real self-evolution does not mean that the system becomes increasingly complex. It means that recurrence of the same failure declines while false blocks, permission risk, and maintenance cost remain controlled.
