# Risk- and Evidence-Driven Review Switching

> **Evidence level: B (engineering design proposal)**  
> This article corrects the earlier single-variable model “review depth = f(KV Cache occupancy, Plan complexity).” Context length or cache occupancy does not directly measure Reviewer capability, and a stricter Prompt does not guarantee compensation for degraded quality. Review strategy should be selected jointly from risk, reversibility, blast radius, evidence completeness, task novelty, and context health. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-07  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [06 PlanGraph](06-okr-planstep-cascade.md)  
> **Next**: [08 Two-Layer Scope Governance](08-scope-creep.md)

---

## Abstract

A fixed review flow fails at both ends:

- expensive final review wastes time and tokens on low-risk, small, reversible changes;
- lightweight review creates false assurance for high-risk, irreversible, or poorly evidenced changes.

The correct question is not “how long is the context?” It is:

> What happens if the current action fails, can the available evidence prove correctness, can failure be recovered, and is an independent model or human authorization required?

This article proposes an executable Review Router:

```text
Change / Decision
→ Risk Classification
→ Evidence Completeness
→ Reversibility and Blast Radius
→ Context Health
→ Review Mode
→ Verdict + Evidence
```

---

## 1. Public Corrections

### 1.1 Cache occupancy is not a measure of Reviewer capability

High token usage may correlate with task complexity, but it cannot justify:

```text
128K context
→ Reviewer quality has fallen to 40%
```

Actual quality depends on the model, task, location of relevant information, tool evidence, summary quality, Prompt, sampling parameters, and Reviewer independence.

### 1.2 A stricter Prompt does not necessarily repair context problems

When the context is incorrect, conflicting, or noisy, telling the model to “be more careful” may increase output length without improving defect detection. Effective actions may include:

- shrinking review input;
- rereading original Artifacts;
- using an independent Session;
- running deterministic tests;
- requiring human approval;
- blocking irreversible actions.

### 1.3 Review depth is not a single monotonic variable

“Deeper” may mean different interventions:

```text
more tests
independent Reviewer
more original evidence
additional security scans
broader human approval
Canary execution
delayed release
```

Review escalation cannot be represented only by a longer Review Prompt.

---

## 2. Review-Routing Inputs

### 2.1 Risk level

| Level | Example | Default requirement |
| --- | --- | --- |
| R0 | Copy, formatting, side-effect-free analysis | Automated validation or light review |
| R1 | Reversible single-file change | Tests + Diff Review |
| R2 | Multi-file, interface, or configuration change | Independent Reviewer + regression tests |
| R3 | Data migration, permission, security, deployment | Specialized validation + human approval |
| R4 | Irreversible production side effect | Reject by default or use a strict change process |

### 2.2 Blast Radius

Consider at least:

```text
files
modules
services
users
data
permissions
external systems
```

### 2.3 Reversibility

```text
fully_reversible
reversible_with_backup
partially_reversible
irreversible
unknown
```

Unknown must not be treated as low risk.

### 2.4 Evidence Completeness

Review input should not contain only a model summary. Check:

- Spec / Acceptance Criteria;
- Diff / Artifact Hash;
- Test Result;
- Static Analysis;
- Tool Evidence;
- Approval;
- Known Failure;
- Rollback Plan.

### 2.5 Novelty

- is this the first modification to the module?
- does it introduce a new Provider / Tool / Dependency?
- does it depart from project conventions or known training patterns?
- does it involve an unknown Schema or protocol?

### 2.6 Context Health

Context health is an input, not the review quality itself:

```text
source coverage
conflicting instructions
stale summaries
missing artifacts
retrieval confidence
context size
compaction count
```

When health is degraded, rebuild the Review Context before merely tightening the Prompt.

---

## 3. Review Modes

### M0: No Additional Review

Appropriate when:

- there is no side effect;
- the operation is a deterministic format conversion;
- automated tests completely cover the result;
- the result can be discarded immediately.

The system must still record why review was skipped.

### M1: Automated Verification

Use:

```text
schema validation
unit tests
lint / typecheck
hash / path checks
policy checks
```

Deterministic verification takes priority over model self-report.

### M2: Light Independent Review

An independent Reviewer reads:

- the original objective;
- the Diff;
- critical files;
- test results;
- open risks.

It does not receive the execution Agent’s complete reasoning history.

### M3: Deep Multi-Dimensional Review

Split review by dimension:

```text
correctness
security
compatibility
data integrity
performance
operability
rollback
```

Different Verifiers or Reviewers can produce independent Verdicts.

### M4: Human Approval / Change Management

Appropriate for:

- production data;
- permission expansion;
- irreversible external actions;
- safety-policy changes;
- high-impact migrations.

Model review cannot replace authorization responsibility.

### M5: Reject or Defer

When evidence is insufficient, rollback is unavailable, or risk is unacceptable, the correct result may be to stop—not to generate more review prose.

---

## 4. Routing Rules

Example policy:

```python
def choose_review_mode(change):
    if change.irreversible and change.risk >= R3:
        return M4
    if change.evidence_missing or change.context_health == "degraded":
        return M5
    if change.security_sensitive or change.data_migration:
        return M3
    if change.blast_radius > 1 or change.novelty == "high":
        return M2
    if change.has_deterministic_verifier:
        return M1
    return M2
```

A real implementation requires versioned Policy rather than rules scattered through Prompts.

### 4.1 Asymmetric thresholds

Different mistakes have different costs:

- over-reviewing a low-risk change increases cost;
- under-reviewing a high-risk change can cause an incident.

High-risk classification should therefore use conservative thresholds. Uncertainty should escalate, not downgrade, review.

### 4.2 Review Context Rebuild

Trigger a rebuild when:

- a critical source is missing;
- post-Compaction content is no longer traceable;
- the Spec conflicts with the Diff;
- Reviewer input contains a stale Snapshot;
- the Workspace Hash changed;
- the Provider or Tool Schema changed.

After rebuilding, load only original evidence relevant to the review.

---

## 5. Verdict Schema

```yaml
review_id: review-123
mode: M3
risk: R3
scope:
  files: 8
  services: 2
evidence:
  spec: spec-8
  diff_hash: sha256:...
  test_runs:
    - test-991
findings:
  - severity: high
    type: rollback_gap
    source_ref: diff:src/migrate.py:88
verdict: changes_required
confidence: medium
missing_evidence:
  - windows_compatibility_test
reviewer:
  type: independent_model
  model: deepseek-v4-pro
created_at: 2026-07-27T00:00:00Z
```

A Verdict must cite concrete evidence and locations. “Looks fine” is not sufficient.

---

## 6. Validation Metrics

### 6.1 Quality

```text
escaped defect rate
review precision / recall
severity-weighted defect detection
false approval rate
false rejection rate
```

### 6.2 Cost and speed

```text
review tokens
review latency
human review minutes
cost per prevented defect
```

### 6.3 Recovery and safety

```text
rollback availability
rollback success
policy block rate
unreviewed high-risk action count
```

### 6.4 Experimental design

Compare:

```text
fixed review mode
vs.
risk/evidence review router
```

Use a held-out change set with blinded ground-truth defects and report a confusion matrix for every risk level.

---

## 7. Boundaries and Risks

- the risk classifier can be wrong;
- Reviewers may share the same blind spot;
- more Reviewers do not necessarily add independent information;
- automated tests have limited coverage;
- human approval can become ceremonial;
- excessive review reduces delivery speed;
- the Review Router itself needs versions, tests, and audit logs.

Retain manual escalation, explicit skip reasons, Policy versions, and post-incident review.

---

## 8. Conclusion

Reliable review is neither a fixed Prompt nor a four-level threshold selected from KV Cache occupancy.

Review switching should center on:

1. consequences of failure;
2. blast radius;
3. reversibility;
4. Evidence completeness;
5. task novelty;
6. Context health;
7. need for an independent model or human authorization.

The objective is not “always review as deeply as possible.” It is to make high-risk defects harder to escape at an acceptable cost, while ensuring every Verdict can be traced to original evidence.
