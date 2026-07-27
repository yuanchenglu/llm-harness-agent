# Scope Governance: Distinguishing Product Expansion from Implementation-Dependency Discovery

> **Evidence level: B (engineering design proposal)**  
> This article corrects the earlier absolute framing that “scope creep is two diseases and all existing solutions confuse them.” A more precise engineering split is: one class of change adds to or alters the approved user-value scope; another class discovers work required to implement an already approved objective. Both must be recorded, assessed, and controlled, but they use different approval thresholds. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-08  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [07 Risk- and Evidence-Driven Review Switching](07-review-switching.md)  
> **Next**: [09 Skills Self-Evolution](09-skills-self-evolution.md)

---

## Abstract

When a user asks for “basic JWT login,” execution may reveal two different classes of change.

### A. Product Scope Expansion

New user capabilities:

```text
RBAC
OAuth
password recovery
2FA
multi-tenancy
```

Even when technically adjacent, these exceed the approved scope of basic login and require a Change Request and a user decision.

### B. Implementation Dependency Discovery

Work required to complete basic login:

```text
password hashing
token-signing configuration
authentication middleware
error handling
required tests
```

These usually do not change the user objective, but they may change effort, file scope, and risk. They require Impact Analysis and may still require approval when thresholds are exceeded.

Reliable scope governance is neither “forbid every new step” nor “automatically do anything technically reasonable.” It uses a versioned Scope Contract, Change Proposals, impact analysis, and approval policy.

---

## 1. Public Corrections

### 1.1 Do not use a “two pathologies” metaphor as the model

A scope change may combine product, technical, safety, compliance, and operational factors. This article uses executable change types rather than a medical metaphor:

```text
scope expansion
implementation dependency
requirement clarification
corrective work
risk mitigation
```

### 1.2 A missing list of non-goals does not authorize free expansion

The default rule should be:

> Perform only the minimum work necessary to achieve the confirmed objective and acceptance criteria. Adjacent features are out of scope by default.

Negative boundaries are useful, but the user should not bear the burden of enumerating every possible non-goal.

### 1.3 An implementation dependency is not automatically approved

Even when work is necessary, it must become a Change Request if it:

- changes the architecture;
- adds an external service;
- expands permissions;
- modifies production data;
- materially increases time or cost;
- reduces compatibility.

### 1.4 Remove unsupported percentages

Earlier examples that assigned specific proportions of scope creep to particular causes had no reproducible data source and are removed.

---

## 2. Scope Contract

```yaml
scope_id: auth-jwt-v1
version: 3
objective: Add basic username-and-password login to the existing Web application
in_scope:
  - login endpoint
  - JWT issuance and verification
  - secure password storage
  - authentication middleware
  - unit and integration tests
non_goals:
  - RBAC
  - OAuth
  - password recovery
  - 2FA
  - multi-tenancy
acceptance_criteria:
  - A valid user can log in and receive a Token
  - An incorrect password returns 401
  - A protected endpoint rejects an invalid Token
constraints:
  - use the existing database
  - do not add an external identity service
change_budget:
  max_files_without_approval: 8
  max_estimated_hours_without_approval: 4
  external_dependency_requires_approval: true
  permission_change_requires_approval: true
owner: user-or-product-owner
status: approved
```

### 2.1 Objective

Describe user value, not an implementation method.

### 2.2 In Scope

List capabilities explicitly included in the confirmed objective.

### 2.3 Non-goals

List likely adjacent features. Exhaustive enumeration is unnecessary; cover common expansion directions for the current task.

### 2.4 Acceptance Criteria

Scope completion is determined by acceptance criteria, not the number of Steps.

### 2.5 Constraints

Include technical, time, platform, compatibility, and permission boundaries.

### 2.6 Change Budget

Define which small changes the Runtime may process automatically and which must be escalated for approval.

---

## 3. Change Classification

### 3.1 Clarification

Removes ambiguity without changing the objective.

Example: should Token validity be 30 minutes or 24 hours?

### 3.2 Implementation Dependency

Necessary to satisfy an approved Acceptance Criterion.

Decision question:

```text
If this work is omitted, can the approved acceptance criteria still be satisfied honestly?
```

If the answer is no, it may be a necessary dependency.

### 3.3 Corrective Work

Repairs an error introduced or exposed by the current change.

Distinguish:

- a regression introduced by this change: repair it;
- a pre-existing unrelated defect: create an Issue and do not include it by default.

### 3.4 Risk Mitigation

Work required for the approved implementation to meet a minimum safety, data-integrity, or compliance baseline.

High-impact Risk Mitigation still requires approval.

### 3.5 Product Scope Expansion

Adds a user capability, platform, integration, or product behavior. Product-owner approval is required by default.

### 3.6 Refactor Opportunity

“Refactor while we are here” or “make the code cleaner” is not a necessary dependency. Unless an acceptance, safety, or maintainability Gate explicitly requires it, record it as future work.

---

## 4. Change Proposal

```yaml
change_id: change-auth-7
scope_version: 3
type: implementation_dependency
description: Add a password-hashing library and migrate existing plaintext passwords
reason: Basic username-and-password login cannot be considered secure without protected storage
trigger:
  node_id: step-password-storage
impact:
  files: 5
  data_migration: true
  external_dependency: argon2
  permissions_changed: false
  estimated_effort_hours: 6
  rollback_complexity: medium
alternatives:
  - name: Support new users only
    tradeoff: Existing users cannot log in
  - name: Migrate progressively on first login
    tradeoff: Higher implementation complexity
recommendation: Request user approval for the migration strategy
approval_required: true
status: proposed
```

A Change Proposal must state:

```text
change type
why it is needed
relationship to an Acceptance Criterion
impact scope
risk
cost
alternatives
consequence of not doing it
approval requirement
```

---

## 5. Decision Matrix

| Condition | Default action |
| --- | --- |
| No user capability change, low risk, within budget, reversible | Include automatically and record |
| Necessary dependency exceeds file/time budget | Pause and request approval |
| Adds an external dependency | Request approval |
| Changes permissions, safety, or data | Higher-level Review + approval |
| Adds user capability | Product Scope Change |
| Pre-existing unrelated defect | Create an Issue; do not repair by default |
| Necessity cannot be determined | Mark Unknown and request a decision |

---

## 6. Reverse Clarification

Clarification should target high-impact boundaries rather than list every possible feature.

A useful question:

```text
Should basic login include only username/password + JWT, excluding RBAC, OAuth, password recovery, and 2FA?
```

A better default system behavior is:

```text
I will implement username/password login, JWT, authentication middleware, and required tests. RBAC, OAuth, password recovery, and 2FA are excluded by default.
```

The user corrects a concrete default rather than defining everything from a blank form.

### 6.1 When asking is mandatory

- the option changes the data model;
- the option is hard to roll back;
- cost differs materially;
- compliance or safety is involved;
- different answers create different product value.

### 6.2 When not to ask

- an existing project convention can be selected safely;
- deterministic configuration or documentation provides the answer;
- the change is low-risk, reversible, and within budget;
- the question concerns an implementation detail that does not affect user value.

---

## 7. PlanGraph Integration

I-06 PlanGraph maps changes to:

```text
new node
new edge
changed acceptance criterion
changed constraint
invalidated evidence
```

Flow:

```text
Discovery
→ Change Proposal
→ Classify
→ Impact Analysis
→ Approve / Reject / Defer
→ New Scope and Plan Version
→ Invalidate affected Evidence
```

An unapproved Scope Expansion must not enter the official Plan.

---

## 8. Controlling User Interruptions

Frequent approval popups destroy Agent value. Use three levels.

### Auto-accept

Low-risk, necessary, within budget, reversible changes are recorded in the Timeline.

### Batch Review

Accumulate medium-impact changes until a Checkpoint and present them together:

```text
Added 3 necessary implementation steps
Estimated increase: 2 files and 40 minutes
No product-scope change
```

### Immediate Approval

Pause immediately for high risk, scope expansion, irreversibility, external side effects, or budget overruns.

---

## 9. Scope Drift Detection

At Runtime compare:

```text
approved scope
current plan
actual changed files
actual tools/dependencies
current artifacts
```

Signals include:

- a modified file is unrelated to any In-scope Criterion;
- a new dependency has no Change Proposal;
- the Plan contains a Non-goal node;
- tool permissions expanded;
- file count, cost, or time exceeded the budget;
- the output added an unapproved user capability.

A signal triggers Review; it does not automatically prove a violation.

---

## 10. Scope Verdict

```yaml
verdict_id: scope-review-11
scope_version: 3
plan_version: 8
status: changes_required
findings:
  - type: product_scope_expansion
    node: step-rbac
    reason: RBAC is explicitly listed under non_goals
    required_action: remove_or_request_approval
  - type: implementation_dependency
    node: step-password-hash
    reason: Required for basic secure login
    approval: required_due_to_data_migration
```

A Verdict must reference Scope, Plan, and Evidence versions.

---

## 11. Evaluation

### 11.1 Scope accuracy

```text
unauthorized feature additions
missed necessary dependencies
incorrect change classification
scope drift detection precision / recall
```

### 11.2 Task outcomes

```text
first-pass acceptance
rework
user corrections
completion time
cost per successful task
```

### 11.3 Interaction cost

```text
clarification turns
approval interruptions
batched decisions
unnecessary questions
```

### 11.4 Controls

Compare:

```text
no scope contract
prompt-only scope statement
scope contract + change control
```

Use held-out tasks containing newly discovered dependencies, pre-existing defects, tempting adjacent features, and high-risk changes.

---

## 12. Boundaries and Risks

- the Scope Contract may be incomplete;
- the Agent may misjudge what is “necessary”;
- the Change Budget may be too strict or too permissive;
- the user may approve an incorrect expansion;
- a safety issue discovered during implementation may require immediate action;
- too many Change Proposals increase process cost;
- too little approval creates silent drift;
- project conventions may themselves be obsolete.

The design needs an Unknown state, human override, audit, and post-task review.

---

## 13. Conclusion

Scope governance is not a simple limit on Step count and does not require the user to enumerate every non-goal in advance.

A reliable mechanism:

1. fixes objective, In-scope, Non-goals, acceptance, constraints, and Change Budget in a Scope Contract;
2. distinguishes product expansion, implementation dependency, corrective work, risk mitigation, and refactor opportunity;
3. generates Impact and alternatives for every change;
4. records low-risk within-budget changes automatically, batches medium changes, and immediately escalates high-risk changes;
5. updates Scope/Plan Version and invalidates stale Evidence;
6. evaluates scope accuracy, task outcomes, and interaction cost together.

The goal is not an immutable Plan. It is a system in which every change has a type, reason, impact, authorization, and traceable decision.
