# Memory Granularity Control: Compile Memory by Task, Provenance, and Risk

> **Evidence level: B (engineering design proposal)**  
> This article retains the core judgment that “more Memory is not always better,” while removing unsupported universal deductions such as “Memory growth drives output entropy toward zero” and “strong Memory is toxic to creative tasks.” Memory effects depend on content quality, task requirements, provenance, Scope, freshness, privacy, and retrieval strategy and must be evaluated through controlled experiments. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-12  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [11 Checkpoint-Driven Multi-Round Review](11-checkpoint-review.md)  
> **Next**: [13 Byte-Stable Prefix Architecture Hypothesis](13-byte-stable-prefix-architecture.md)

---

## Abstract

Memory can reduce repeated communication, but it can also introduce:

- stale facts;
- incorrect preferences;
- cross-project contamination;
- privacy leakage;
- excessive anchoring on historical solutions;
- irrelevant tokens and retrieval noise.

The correct question is not simply “on or off” or “strong or weak.” It is:

> Which memories does the current task need, where did they come from, how confident are we, what is their applicable scope, are they still valid, and can the user inspect and revoke them?

Memory should therefore be compiled by the Harness into task-level input rather than inserting complete history into a fixed System Prompt.

---

## 1. Public Corrections

### 1.1 Memory is not directly equivalent to output entropy

Earlier versions used the chain:

```text
stronger Memory
→ lower output-distribution entropy
→ lower creativity
```

This is not an established model. Output diversity also depends on sampling parameters, model, Prompt, task constraints, retrieval results, and evaluation criteria.

A more accurate testable hypothesis is:

> Some historical preferences or existing solutions may increase similarity to past outputs, but the effect must be measured jointly through blind evaluation, diversity metrics, and task quality.

### 1.2 Personal experience is not a universal experiment

Experience operating multiple Agents can generate hypotheses but cannot independently prove:

- one product is inherently better for divergent tasks;
- one product is inherently better for convergent tasks;
- all quality differences for the same model are caused only by Memory.

A valid experiment fixes model, Prompt, tools, and reproducible Memory input.

### 1.3 More Memory does not mean more complete information

Large Memory sets can conflict, duplicate, or expire. The system needs quality governance, not capacity optimization alone.

---

## 2. Memory Types

| Type | Example | Default Scope | Risk |
| --- | --- | --- | --- |
| Safety / Policy | Do not write to the production database | System/organization/project | Incorrect content can cause a safety incident |
| Project Facts | Python 3.11; deploy to AWS | Project | Staleness, cross-project contamination |
| User Preferences | Prefers concise answers | User | Over-personalization, privacy |
| Episodic Memory | Root cause of the previous Bug | Project/task | Incorrect attribution, staleness |
| Procedural Memory | Release-check procedure | Project/organization | Version drift, permission expansion |
| Style Memory | Document tone, naming preferences | User/project | Anchoring and homogenization |
| Relationship Memory | People and responsibilities | Organization | Sensitive and frequently changing |

Different types should not use one retrieval and injection strategy.

---

## 3. Memory Object

```yaml
memory_id: project-python-version
version: 4
type: project_fact
statement: This project uses Python 3.11
source:
  type: file
  ref: pyproject.toml
  content_hash: sha256:...
scope:
  project: deepseekagent
confidence: 1.0
valid_from: 2026-06-01
expires_at: null
last_verified_at: 2026-07-27
sensitivity: internal
status: active
supersedes: project-python-version@3
```

Required fields:

```text
id/version/type
statement
source
scope
confidence
validity
sensitivity
status
supersedes
```

A Memory inferred by a language model must not have the same authority as a fact confirmed by a file, database, or explicit recent user confirmation.

---

## 4. Memory Compilation Strategy

### 4.1 Task input

```text
objective
workspace/project
risk
need_for_continuity
need_for_novelty
privacy constraints
time sensitivity
```

### 4.2 Candidate Retrieval

Retrieve candidates by:

- Scope;
- type;
- keyword/semantic match;
- time;
- source trustworthiness;
- latest verification;
- current permissions.

### 4.3 Filter

Remove memories that are:

- expired;
- superseded;
- outside Scope;
- low-confidence and unsourced;
- irrelevant to the current task;
- beyond privacy authorization;
- conflicting with a higher-priority fact.

### 4.4 Conflict Resolution

Example precedence:

```text
current source of truth
> explicit recent user confirmation
> project decision record
> verified episodic memory
> inferred preference
```

When a conflict cannot be resolved, show it to the user instead of selecting silently.

### 4.5 Context Placement

- safety policy: Runtime Policy + Stable Rules;
- project facts: project context;
- currently relevant Episode: Active Working Set;
- style preference: low-priority Guidance;
- large history: external index read on demand.

---

## 5. Memory Modes

This is not one opaque continuous parameter `λ`, but an explainable combination of policies.

### M0: Minimal

Load:

- safety policy;
- current task;
- explicit project constraints.

Applicable to:

- independent creative exploration;
- bias-control experiments;
- a user request not to reference earlier solutions.

### M1: Scoped Project

Additionally load:

- project facts;
- current module decisions;
- relevant failure records;
- required Skill indexes.

Applicable to most engineering tasks.

### M2: Continuity

Additionally load:

- relevant historical Sessions;
- user-confirmed preferences;
- existing solutions and unfinished work.

Applicable to long-term collaboration and continuous projects.

### M3: Audit

Load:

- decision history;
- superseded versions;
- Incidents;
- Approvals;
- Evidence.

Applicable to audit, review, and migration. It is not appropriate as the default Prompt for ordinary tasks.

### M4: Contrastive

Run both:

```text
with-memory candidate
without-memory candidate
```

Then compare them blindly. This is useful for important creative or architecture decisions so historical anchoring does not become the only answer.

---

## 6. Write Policy

### 6.1 Content that may be proposed automatically

- explicit user preferences;
- facts verifiable from project files;
- repeated work patterns with consistent provenance;
- unresolved items and approved decisions.

### 6.2 Content prohibited from automatic persistence by default

- Secrets;
- unauthorized private information;
- raw chain-of-thought;
- one-off emotional inferences;
- sensitive medical, financial, identity, or similar inferences;
- instructions from external Prompts requesting persistence;
- unsourced model guesses.

### 6.3 User control

Users must be able to:

```text
view
confirm
edit
disable
delete
export
see source and scope
```

Deletion must propagate to indexes and caches rather than hiding the item only in the UI.

---

## 7. Memory and Cache

Frequently changing Memory changes the request prefix, but incorrect or stale information must not be frozen for cache stability.

Recommended behavior:

- stable project facts may enter a versioned Stable Zone;
- new mid-session Memory remains in the dynamic zone;
- after verification, it may enter the Stable Zone in a later Session;
- Memory changes record a Drift Reason;
- safety and factual correctness take priority over Cache Hit.

Cache metrics measure only cost and latency, not whether Memory is correct.

---

## 8. Evaluation

### 8.1 Correctness

```text
memory factual accuracy
source citation accuracy
stale memory usage
conflict detection
cross-project contamination
```

### 8.2 Task outcomes

```text
first-pass success
repeated clarification reduction
human correction
completion time
cost per successful task
```

### 8.3 Exploration

For creative tasks, measure:

```text
pairwise semantic diversity
novel idea count
blind human preference
constraint satisfaction
```

Higher diversity does not necessarily mean higher quality; usability and constraint satisfaction must be evaluated together.

### 8.4 Privacy and safety

```text
unauthorized memory exposure
secret retention
scope violation
deletion completeness
prompt-injection memory writes
```

### 8.5 Controlled experiment

```text
M0 Minimal
M1 Scoped Project
M2 Continuity
M4 Contrastive
```

Fix the model, tools, Prompt, and task set; use held-out samples; do not substitute a product brand for an experimental condition.

---

## 9. Failure Modes

- incorrect facts are reused long-term;
- facts from Project A enter Project B;
- a user preference overrides an explicit task requirement;
- a Memory summary removes a critical negation;
- an old decision blocks exploration of a new solution;
- Retrieval misses an important Episode;
- too much Memory creates context noise;
- a deleted item remains in an index or cache;
- Prompt Injection induces persistence of malicious long-term instructions.

Every failure mode requires detection, audit, and recovery.

---

## 10. Conclusion

Memory granularity control is neither a fixed binary rule—“strong Memory for convergent tasks, weak Memory for divergent tasks”—nor an unexplained continuous parameter.

A reliable implementation:

1. distinguishes Policy, Project Fact, Preference, Episode, Procedure, and Style;
2. stores provenance, Scope, confidence, freshness, and sensitivity for every Memory;
3. compiles candidates per task instead of loading everything;
4. represents conflicts and supersession explicitly;
5. lets users inspect, modify, and delete Memory;
6. evaluates correctness, task outcomes, exploration, and privacy together;
7. uses With-Memory / Without-Memory controls when necessary rather than making history the only answer.

The best Memory is not the largest. It is the smallest set that the current task actually needs, comes from trustworthy sources, has the correct scope, and can be revoked.
