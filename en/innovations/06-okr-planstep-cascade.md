# PlanGraph: Acceptance Criteria, Dependency Edges, and Cascading Invalidation

> **Evidence level: B (engineering design proposal)**  
> This article retains the core judgment that a flat Checklist is insufficient for complex tasks, while correcting the earlier data model: association strength belongs to dependency edges; `parent_id` and recursive `children` must not become dual sources of truth; and one natural-language `key` is not enough to prove completion. The core of PlanGraph is explicit representation of objectives, acceptance, dependencies, evidence, and invalidation—not automatic inference of every semantic relationship. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-06  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [05 Agent-Readable Document Structure](05-document-kv-cache.md)  
> **Next**: [07 Risk- and Evidence-Driven Review Switching](07-review-switching.md)

---

## Abstract

Steps in a complex task commonly contain:

- hierarchical decomposition;
- execution-order dependencies;
- data or interface dependencies;
- shared Artifacts;
- acceptance conditions;
- risk and approval;
- Evidence;
- invalidation relationships after changes.

A `text + status` list can display progress but cannot reliably drive execution and recovery.

PlanGraph models:

```text
Nodes: Objective / Step / Milestone
Edges: hierarchy / requires / produces-consumes / validates / conflicts
Acceptance Criteria: structured assertions and verifiers
Evidence: tests, artifacts, approvals, tool results
Invalidation: changed inputs make downstream evidence and verdicts stale
```

The first action of a cascade engine is not automatic re-execution. It computes impact, marks stale state, requires revalidation, and lets the Runtime decide whether execution should be repeated.

---

## 1. Public Corrections

### 1.1 Not every Agent has only a flat Plan

Different products may expose task trees, DAGs, Issue Links, Workflow Graphs, or implicit dependencies. The accurate conclusion is that many lightweight Plan APIs expose only content, status, and priority, which makes complex execution semantics difficult to represent.

### 1.2 `association_strength` belongs to the Edge

The same Step can affect different downstream nodes differently:

```text
A is a strong dependency of B
A is only a weak reference for C
```

Dependency type, strength, provenance, and confidence must therefore be Edge properties.

### 1.3 Avoid dual truth in `parent_id` and `children[]`

Persist only one direction, such as `parent_id` or a separate Hierarchy Edge. Compute `children` during queries. Otherwise, updating one representation while forgetting the other corrupts graph consistency.

### 1.4 One `key` does not prove verifiable completion

A natural-language Key Result may be ambiguous, compound, or impossible to check automatically. Each Step should contain multiple Acceptance Criteria and declare a verification method:

```text
test
schema
artifact existence
human approval
model review
manual observation
```

### 1.5 Cascade propagation cannot prove semantic impact

A graph can propagate only declared relationships. Missing, incorrect, or implicit semantic dependencies still require type checking, tests, search, or Reviewer findings.

---

## 2. Core Model

### 2.1 Plan

```yaml
plan_id: plan-123
version: 8
task_id: task-88
objective: Implement basic JWT login without RBAC, OAuth, or 2FA
status: active
root_node_id: objective-auth
created_at: 2026-07-27T00:00:00Z
updated_at: 2026-07-27T01:00:00Z
base_checkpoint_id: cp-7
```

A Plan must be versioned. Any structural, Scope, or acceptance change creates a new Version.

### 2.2 Node

```yaml
node_id: step-token-endpoint
kind: step
objective: Implement a login endpoint that returns an access token
status: in_progress
risk: R2
owner: executor-main
acceptance_criteria:
  - criterion_id: ac-http-200
    assertion: A valid account returns 200
    verifier:
      type: test
      ref: test_login_success
  - criterion_id: ac-invalid-401
    assertion: An incorrect password returns 401
    verifier:
      type: test
      ref: test_login_invalid_password
expected_outputs:
  - artifact: src/auth/login.py
constraints:
  - no-rbac
  - no-oauth
evidence_refs: []
```

### 2.3 Edge

```yaml
edge_id: edge-schema-to-login
from: step-user-schema
to: step-token-endpoint
type: requires
strength: strong
source:
  type: planner
  ref: plan-generation-8
confidence: 0.91
condition: null
status: active
```

Recommended Edge types:

| Type | Meaning |
| --- | --- |
| `contains` | Hierarchical decomposition |
| `requires` | Upstream completion is required before downstream execution |
| `consumes` | The downstream node uses an upstream Artifact |
| `validates` | One node validates another |
| `conflicts` | Two nodes cannot both hold |
| `related` | Weak association; Review notice only |

### 2.4 Evidence Link

```yaml
link_id: ev-step-token-1
node_id: step-token-endpoint
evidence_id: test-run-991
supports:
  - ac-http-200
  - ac-invalid-401
artifact_hash: sha256:...
plan_version: 8
status: valid
```

Evidence must bind to a Plan Version, Artifact Hash, and Criterion so input changes can deterministically invalidate it.

---

## 3. State Machine

Node states:

```text
pending
ready
in_progress
blocked
awaiting_approval
awaiting_verification
completed
stale
cancelled
```

### 3.1 `completed` Gate

A node becomes complete only when every required Acceptance Criterion has valid Evidence, dependencies are satisfied, and required approvals remain active:

```text
all required criteria satisfied
AND all strong prerequisites valid
AND required approvals active
AND no blocking issue
```

A model’s natural-language statement “completed” does not change state.

### 3.2 `stale`

A node or Evidence becomes stale when:

- an upstream Artifact Hash changes;
- an Acceptance Criterion changes;
- the Plan Version changes;
- a Tool Schema or Runtime version change affects the result;
- the Diff bound to an Approval changes;
- a dependency Edge is added or strengthened.

---

## 4. Graph Constraints

### 4.1 Hierarchy graph

`contains` should form a tree or forest:

- each node has at most one hierarchy parent;
- hierarchy cycles are prohibited;
- the root objective is explicit.

### 4.2 Execution dependency graph

`requires / consumes / validates` should form a DAG by default. Run topological checks whenever an Edge is created or updated.

A cycle may indicate:

- planning error;
- two Steps that should be merged;
- a Fixed Point Workflow is required;
- incorrect dependency typing.

Do not ignore cycles silently.

### 4.3 Integrity rules

- Node IDs are unique;
- every Edge references existing nodes;
- Criterion IDs are unique;
- a Completed Node cannot lack required Evidence;
- a Cancelled Node cannot remain a valid strong prerequisite;
- Evidence Hash and Plan Version are verifiable.

---

## 5. Cascading Invalidation Algorithm

### 5.1 Inputs

```text
changed nodes
changed artifacts
changed acceptance criteria
changed edges
changed constraints
```

### 5.2 Propagation

```python
def invalidate(graph, changes):
    queue = direct_impacted_nodes(changes)
    visited = set()

    while queue:
        node = queue.pop()
        if node in visited:
            continue
        visited.add(node)

        mark_relevant_evidence_stale(node, changes)
        if node.status == "completed":
            node.status = "stale"

        for edge in graph.outgoing(node):
            if edge.status != "active":
                continue
            if edge.type in {"requires", "consumes", "validates"}:
                queue.push(edge.to)
            elif edge.type == "related":
                create_review_notice(edge.to, reason=changes)

    return impact_report(visited)
```

### 5.3 Invalidation is not automatic re-execution

The result is an Impact Report:

```yaml
changed:
  - step-user-schema
invalidated:
  - node: step-token-endpoint
    evidence:
      - test-run-991
    reason: consumes changed schema artifact
review_recommended:
  - step-api-docs
blocked:
  - step-integration-tests
```

The Orchestrator chooses according to risk, budget, and approval:

- rerun deterministic tests automatically;
- re-execute a Step;
- request independent Review;
- request a user decision;
- defer and record the risk.

---

## 6. Discovering Implicit Dependencies

A declared graph will always be incomplete. The Runtime can propose new Edges from:

- Import / Call Graph;
- LSP References;
- Type Errors;
- Test Failures;
- shared Database Schema;
- Artifact read/write traces;
- Reviewer findings.

New relationships retain provenance and confidence:

```yaml
source:
  type: lsp_reference
confidence: 1.0
status: proposed
```

High-confidence deterministic relationships may be inserted automatically. Model-inferred relationships require Review by default.

---

## 7. Scope and Change Requests

PlanGraph must not silently expand product scope when it discovers a dependency.

Distinguish:

```text
Implementation Dependency: required to complete an approved objective
Product Scope Expansion: adds a new user capability or non-goal
```

The latter creates a Change Request and enters the scope-governance process defined in I-08.

---

## 8. Concurrency and Multi-Agent Execution

### 8.1 Single Loop Authority

Only the Orchestrator may modify official Plan state. A sub-Agent submits:

```text
proposed node update
proposed edge
artifact
evidence
blocker
```

### 8.2 Optimistic concurrency

An update request includes:

```text
plan_id
expected_plan_version
patch
```

If the Version does not match, reject the update and reread state so two Agents cannot overwrite one another.

### 8.3 Workspace isolation

Parallel writes require separate Worktrees/Workspaces and an explicit merge strategy. PlanGraph itself does not solve file conflicts.

---

## 9. API Examples

```text
POST /plans/{id}/nodes
POST /plans/{id}/edges
POST /plans/{id}/changes
POST /plans/{id}/evidence
POST /plans/{id}/impact-analysis
POST /plans/{id}/verify
```

Every write requires `expected_plan_version` and an Idempotency Key.

---

## 10. Evaluation

### 10.1 Graph quality

```text
dependency precision / recall
cycle detection
orphan node rate
implicit dependency discovery
```

### 10.2 Execution quality

```text
stale evidence escape rate
incorrect completed status
rework steps
first-pass success
resume success
```

### 10.3 Cost

```text
impact analysis latency
revalidation tokens
unnecessary re-execution
human review time
```

### 10.4 Controls

Compare:

```text
flat checklist
hierarchical tree
PlanGraph + evidence invalidation
```

Use held-out tasks containing mid-task requirement changes, interface changes, and implicit dependencies.

---

## 11. Boundaries and Risks

- a Planner may omit or misclassify dependencies;
- graph-maintenance cost may exceed the benefit for small tasks;
- a dense graph can invalidate too much work;
- automatic relationship discovery can create false positives;
- Acceptance Criteria may be unverifiable;
- Evidence may come from the wrong version;
- concurrent Agents can create state conflicts;
- a DAG is inappropriate for some iterative processes.

Simple tasks should be allowed to degrade to a lightweight Checklist rather than being forced into a graph.

---

## 12. Conclusion

The value of PlanGraph is not adding five fields. It establishes a computable contract:

1. Nodes represent objectives and Steps;
2. Edges represent concrete relationships, strength, provenance, and confidence;
3. Acceptance Criteria connect to Verifiers;
4. Evidence binds to Plan Version and Artifact Hash;
5. upstream changes trigger cascading invalidation and an Impact Report;
6. the Runtime decides whether to revalidate, redo, approve, or defer;
7. graph integrity, concurrency, and recovery become verifiable.

Complex tasks need a graph, but a graph does not replace tests, type systems, Policy, or human product judgment.
