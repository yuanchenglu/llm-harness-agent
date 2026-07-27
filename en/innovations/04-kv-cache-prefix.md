# Stable Constraints and Compressible History: A Context Compiler, Not a “KV Cache Safe Zone”

> **Evidence level: B (engineering design proposal)**  
> This article corrects the earlier claim that placing constraints in a KV Cache prefix physically guarantees retention and compliance. Provider Prefix Cache, Harness context compaction, and model constraint compliance are three different problems and must be designed and measured separately. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-04  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [03 Attention Budget Management](03-attention-budget.md)  
> **Next**: [05 Stable-Prefix Document Structure](05-document-kv-cache.md)

---

## Abstract

Long-running tasks produce user constraints, project rules, tool traces, test results, historical discussion, and temporary information. These have different lifecycles and should not be processed by one compaction strategy.

The correct architectural principle is:

> Partition stable constraints that must persist, append-only evidence, the current active working set, and externally retrievable history; then define update, compaction, invalidation, and verification rules for each class.

This is a **Context Compiler** design, not a physical isolation property of KV Cache.

- the Harness decides which information is reintroduced into each request;
- the Provider Prefix Cache decides whether computation for a common prefix is reused;
- Runtime Policy decides whether an action is permitted;
- whether the model follows a natural-language constraint requires task-level tests.

These four mechanisms cannot substitute for one another.

---

## 1. Public Corrections

### 1.1 KV Cache is not a separate storage zone inside a message

From a client Harness perspective, a request remains a serialized message sequence. Prefix Cache is usually a Provider-side mechanism for reusing computation over an identical or common prefix.

It does not mean that a client can “place text into KV Cache” and remove that text from subsequent requests. Unless a specific Provider exposes an explicit persistent-cache protocol, each request must still send all messages required by the API contract.

### 1.2 Exclusion from compaction is a Harness rule, not a Cache property

If a Context Compiler specifies:

```text
System Rules do not enter the History Compactor
```

then those rules are retained because the request builder includes them again on every turn—not because Provider Cache automatically protects them.

Use precise terminology:

```text
Stable Constraints Zone
Compressible History Zone
Provider Prefix Cache
```

Do not merge all three into the phrase “KV Cache prefix zone.”

### 1.3 Presence in the request does not guarantee compliance

Distinguish:

```text
Retention: is the constraint text still present in the input?
Compliance: does model output or behavior satisfy the constraint?
Enforcement: does the Runtime block a violating side effect?
Cache: did the Provider reuse common-prefix computation?
```

Even if `Retention = 100%`, `Compliance` may be lower than 100%. Non-negotiable constraints should be guaranteed by Runtime Enforcement rather than natural-language Prompt alone.

### 1.4 One changed byte does not necessarily cause a total cache miss

Prefix Cache generally operates over a common prefix. A changed suffix may preserve hits for earlier common tokens; the earlier the first change occurs, the larger the potentially invalidated suffix.

Exact behavior depends on Provider, serialization, Tokenizer, cache policy, TTL, account, and time. It must be inferred from Usage telemetry and repeated experiments, not stated as the universal rule “one changed byte clears the entire Cache.”

### 1.5 Historical `40% → 95%` results are downgraded

Earlier constraint-retention figures lacked a reproducible Runner, task set, raw results, and statistical testing. They are no longer treated as confirmatory evidence. Future reports must separately show:

- input retention rate;
- model compliance rate;
- Runtime block rate;
- final task success rate;
- Prefix Cache hits and cost.

---

## 2. Problem Definition

### 2.1 Information has different lifecycles

| Information type | Example | Lifecycle | May be compacted? |
| --- | --- | --- | --- |
| Safety policy | Writing outside the Workspace is prohibited | Project or system | No; only versioned updates |
| User-approved constraint | Do not modify configuration files | Task | No by default; explicit user change required |
| Tool contract | Tool Schema, permission level | Session/version | No silent rewrite |
| Decisions and evidence | Approval, Diff Hash, Test Result | Entire task | May be indexed, but provenance cannot be lost |
| Active working set | Current objective, relevant file excerpt | Current step | Replaceable and re-retrievable |
| Raw tool output | Logs, search results, full file text | Temporary | May be truncated or stored externally |
| Conversation discussion | Alternatives, rejected ideas | Historical | May be summarized or archived |

The fundamental problem is not merely that “the compaction algorithm is not smart enough.” The system has failed to define:

```text
who may change it
when the change becomes effective
whether it may be compacted
how it is invalidated
how it is audited
how it is restored
```

### 2.2 Accurate meaning of a Hard Constraint

A genuine Hard Constraint should satisfy:

> Its violation causes a safety, permission, data-integrity, or explicit acceptance failure, and a deterministic execution-time check exists.

Examples:

| Constraint | Prompt reminder | Runtime Enforcement |
| --- | --- | --- |
| Do not write outside the Workspace | Useful | Path Boundary Check required |
| Do not modify `.git` | Useful | Protected paths must be rejected |
| Use Python 3.11 | Useful | Validate the execution and test environment |
| Approval is required before modification | Useful | ChangeSet state machine must block |
| Output must use Markdown | Usually sufficient | System-level blocking generally unnecessary |

Words such as “must,” “must not,” “never,” and “prohibited” are insufficient to automatically promote a sentence to a system Hard Constraint. Natural language may contain negation, quotations, examples, temporary preferences, or conflicting instructions. Structured confirmation is required.

---

## 3. Constraint Registry

Model stable constraints as versioned objects:

```yaml
constraint_id: workspace-boundary
version: 3
source:
  type: system_policy
  ref: policy/security.yaml
scope:
  type: workspace
  value: /approved/workspace
enforcement: runtime
severity: critical
priority: 100
message: Read and write only within the approved Workspace
validator: path_boundary_check
created_at: 2026-07-27T00:00:00Z
supersedes: workspace-boundary@2
```

At minimum, include:

```text
constraint_id
version
source
scope
enforcement
severity
priority
validator
created_at
supersedes
```

### 3.1 Enforcement types

| Type | Behavior |
| --- | --- |
| `runtime` | Deterministic code blocks the violating action |
| `verifier` | Tests, Schema, or rules check the generated result |
| `model_guidance` | Prompt guidance only; no strong guarantee |
| `human_approval` | Explicit user approval is required to continue |

The UI and Evidence must display the enforcement type so Prompt Guidance is not misrepresented as a hard security boundary.

### 3.2 Conflicts and updates

The constraint system must handle:

- system policy conflicting with a user request;
- old and new constraints conflicting;
- overlapping constraints at different Scopes;
- temporary exemptions;
- security updates requiring immediate effect.

Recommended precedence:

```text
system safety policy
> organization/project policy
> explicit task approval
> user preference
> inferred preference
```

A security update must rebuild the prefix immediately even if it breaks Prefix Cache. Correctness and safety take priority over cache hits.

---

## 4. Four-Zone Context Compiler Model

```text
┌──────────────────────────────────────────────┐
│ 1. Stable Rules                             │
│    versioned policy, approved constraints,   │
│    stable tool contracts                    │
├──────────────────────────────────────────────┤
│ 2. Append-Only Evidence                     │
│    decisions, Approval, Diff, Test,          │
│    Checkpoint                               │
├──────────────────────────────────────────────┤
│ 3. Active Working Set                       │
│    current objective, relevant files,        │
│    recent tool results, open risks           │
├──────────────────────────────────────────────┤
│ 4. External Index                           │
│    full trace, historical Session, Artifact, │
│    Skill Body                               │
└──────────────────────────────────────────────┘
```

### 4.1 Stable Rules

Requirements:

- stable serialization;
- explicit version;
- a reason for each update;
- explicit invalidation;
- independence from the History Compactor;
- contain only genuinely stable information that the model needs.

### 4.2 Append-Only Evidence

Evidence may be summarized inside a request, but the summary must retain references:

```text
evidence_id
artifact_hash
tool_call_id
test_run_id
approval_id
```

Original Evidence must not be overwritten or deleted by a summary.

### 4.3 Active Working Set

Recompile it for each step and include the smallest relevant set required for the current task. It must support re-retrieval and explicit scope expansion so aggressive pruning does not create missed recall.

### 4.4 External Index

Store complete history outside the model request and retrieve it through Tools or Retrieval when needed. An external index extends capacity but does not guarantee correct retrieval. Record queries, candidates, selections, and misses.

---

## 5. Prefix Cache Optimization

Optimize cache only after correctness is established.

### 5.1 Content that should remain stable

- canonicalized System Rules;
- deterministically ordered Tool Schemas;
- stable Memory / Skill indexes;
- fixed Provider and model configuration;
- explicit serialization version.

### 5.2 Changes allowed to invalidate the prefix

- safety-policy updates;
- reduced tool permissions;
- Tool Schema corrections;
- removal of an incorrect constraint;
- Provider protocol changes;
- Compaction or Session rebuild.

### 5.3 Telemetry

```text
prefix_fingerprint
serializer_version
first_changed_offset
drift_reason
prompt_cache_hit_tokens
prompt_cache_miss_tokens
TTFT
total_latency
cost
```

`prefix_fingerprint` is diagnostic only and must not contain Secrets or a complete private Prompt.

---

## 6. Validation Matrix

### 6.1 Context-retention tests

- are constraint objects identical before and after Compaction?
- are Constraint ID, Version, and Scope preserved?
- are conflicting constraints explicitly rejected?
- does a security update trigger a context rebuild?

### 6.2 Runtime Enforcement tests

- Workspace escape;
- symlink escape;
- `.git` modification;
- stale Approval;
- unapproved write;
- irreversible tool call;
- budget overrun.

### 6.3 Model compliance tests

For behavior not directly blocked by the Runtime, measure:

```text
instruction compliance rate
format compliance rate
citation correctness
incorrect-tool selection
```

### 6.4 Prefix Cache tests

Control and repeatedly run these variants:

- identical prefix;
- only the user suffix changes;
- only the end of the System content changes;
- Tool order changes;
- JSON key order changes;
- safety-rule version changes;
- different times and concurrency conditions.

Report the number of common-prefix hit tokens, not only a binary hit/miss label.

---

## 7. Boundaries and Failure Modes

- an oversized stable prefix increases fixed input and maintenance cost;
- stable reuse of an incorrect rule amplifies the error;
- automatic constraint extraction may misclassify natural language;
- unresolved constraint priority creates unpredictable behavior;
- Provider Cache is best-effort and cannot enter a safety promise;
- cache optimization may conflict with Progressive Tool Disclosure;
- an external index may miss critical history;
- the model may still violate rules enforced only through Prompt guidance.

The system must support:

```text
invalidate prefix
rebuild context
disable inferred constraints
escalate conflict to user
fall back to full evidence
```

---

## 8. Conclusion

The most important design is not “put constraints in KV Cache.” It is:

1. define persistent constraints as versioned objects;
2. enforce non-negotiable safety boundaries with Runtime Policy;
3. use a Context Compiler to separate Stable Rules, Append-Only Evidence, the Active Working Set, and external history;
4. independently measure Retention, Compliance, Enforcement, and Cache;
5. allow safety updates and correctness fixes to deliberately sacrifice cache hits.

Prefix Cache is a cost and latency optimization tool. It is not a constraint-retention mechanism and not a guarantee of model compliance.
