# Byte-Stable Prefix: A Cache Optimization Invariant Constrained by Correctness

> **Evidence level: A1 + B**  
> Fixed source code confirms that some Agents intentionally maintain stable prefixes across Sessions, Memory, Skills, Plan Mode, and model collaboration. This proves that the design exists. It does not prove that “stable prefix + transient suffix” is physically optimal for every Agent, nor that Prefix Cache hits necessarily improve task quality. This article treats Byte Stability as an observable and invalidatable optimization invariant subordinate to correctness. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-13  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Related**: [I-04 Stable Constraints and Compressible History](04-kv-cache-prefix.md) · [I-05 Agent-Readable Document Structure](05-document-kv-cache.md)

---

## Abstract

The basic Prefix Cache opportunity is that when multiple requests share a common prefix, a Provider may reuse part of the computation and reduce input cost or time to first token.

This can influence Agent architecture, but it must not become the highest priority. The correct order is:

```text
correctness and safety
> Provider protocol compatibility
> state consistency and recoverability
> task quality
> Cache / Token / Latency optimization
```

Byte-Stable Prefix means:

> For request segments marked stable, use deterministic serialization and explicit versions, and keep bytes unchanged only while semantics, permissions, and protocol remain unchanged. Every necessary update must be able to invalidate the prefix deliberately.

---

## 1. Public Corrections

### 1.1 Not a “physical optimality law”

Autoregressive Transformers and Prefix Cache explain why a common prefix may be reused. They do not imply that:

- all dynamic information must be placed in the suffix;
- mid-session model switching should never occur;
- a more stable prefix produces higher task quality;
- any prefix change is unacceptable;
- one open-source implementation is optimal for the entire industry.

Some tasks need timely updates to safety rules, tool permissions, project facts, or model capability more than they need cache stability.

### 1.2 Similar patterns across encoding and Harness layers do not prove causality

Removing old reasoning in model encoding source and stabilizing a System Prompt in an Agent Runtime may share the design intuition of separating stable and transient information.

They operate at different layers:

```text
model data/encoding preprocessing
Provider server-side cache
client request compilation
Agent Session state
```

Cross-layer similarity can generate a research hypothesis but does not prove a shared optimization objective or training intention.

### 1.3 Byte Stability is not Semantic Correctness

A byte-identical prefix may contain:

- stale Memory;
- a revoked tool;
- an incorrect safety rule;
- expired pricing;
- obsolete project state.

Semantic validity must be checked before byte stability is optimized.

### 1.4 A cache hit is not task success

Report together:

```text
cache hit/miss
latency
cost
task success
constraint violation
human intervention
```

Hit Rate alone cannot prove that an architecture is better.

---

## 2. Stable-Prefix Segments

Split the prefix into independently versioned segments:

```text
P0 Provider / Protocol Contract
P1 System Safety Policy
P2 Product / Runtime Rules
P3 Project Constraints
P4 Tool Catalog
P5 Memory / Skill Index
```

Each segment contains:

```yaml
segment_id: tool-catalog
semantic_version: 12
serializer_version: 3
content_hash: sha256:...
source_refs:
  - tool-registry@commit-abc
invalidation_reasons:
  - tool_added
  - permission_changed
  - schema_fixed
```

### 2.1 Why segmentation matters

It answers:

- which segment changed;
- why it changed;
- whether it was a safety update;
- where in the prefix the change occurred;
- which earlier common prefix may still be reusable.

This is easier to diagnose than one `system_prompt_hash`.

---

## 3. Canonical Serialization

### 3.1 Objects requiring deterministic representation

- Tool Schema order;
- JSON key order;
- Unicode normalization;
- newlines;
- whitespace;
- numeric and Boolean representation;
- default handling for optional fields;
- message-wrapper order.

### 3.2 Serializer Version

The serializer must be versioned:

```yaml
serializer:
  name: deepseek-openai-compatible
  version: 3
  unicode: NFC
  newline: LF
  sort_tools_by: name
  sort_json_keys: true
```

A serializer change should record Drift explicitly rather than misdiagnosing a lower hit rate as a Provider failure.

### 3.3 Prohibit fake stability

Do not preserve stability by:

- retaining revoked tools;
- sending Schemas the user is not allowed to use;
- hiding a security update;
- keeping an old dynamic date;
- freezing incorrect Memory;
- disabling a required Context Rebuild.

---

## 4. Dynamic Information Strategy

### 4.1 Turn Tail

Appropriate for:

- current task;
- temporary mode;
- latest tool results;
- mid-session Memory proposals;
- current date and location;
- Pending Approval.

### 4.2 Session Rebuild

Rebuild after changes to:

- safety policy;
- Tool permissions;
- Provider protocol;
- project root;
- model capabilities;
- an incorrect prefix;
- Compaction structure.

### 4.3 Independent Sessions

Separate Planner, Executor, and Reviewer Sessions may:

- keep each state clear;
- reduce cross-contamination;
- allow different models and tools;
- preserve a stable prefix for each role.

Costs include:

- duplicated input;
- state synchronization;
- Summary Error;
- higher total call cost.

Use task benchmarks to decide, not Cache alone.

---

## 5. Prefix Manifest

Record a redacted Manifest for each request:

```yaml
request_id: req-123
provider: deepseek
model: deepseek-v4-pro
endpoint_capability_version: 2026-07-16
segments:
  - id: provider-contract
    semantic_version: 4
    content_hash: sha256:...
  - id: safety-policy
    semantic_version: 9
    content_hash: sha256:...
  - id: tool-catalog
    semantic_version: 12
    content_hash: sha256:...
stable_prefix_hash: sha256:...
first_drift_segment: tool-catalog
drift_reason: permission_changed
cache:
  hit_tokens: 4096
  miss_tokens: 512
```

The Manifest must not store Secrets or a complete private Prompt.

---

## 6. Invalidation Policy

### 6.1 Explicit invalidation reasons

```text
security_policy_update
tool_permission_change
tool_schema_fix
provider_capability_change
project_switch
memory_correction
serializer_upgrade
context_compaction
manual_rebuild
```

### 6.2 Invalidation must not be silent

The Runtime should display:

- invalidation reason;
- affected segment;
- old and new versions;
- whether the change was expected;
- quality and cost impact.

### 6.3 Cache-priority Gate

If prefix stability requires sacrificing:

- the correct tool;
- the latest safety policy;
- correct project facts;
- a better-suited model;
- required review;

then Cache must be invalidated.

---

## 7. Provider Capability

Providers may differ in:

- automatic Prefix Cache;
- explicit Cache Control;
- minimum cache length;
- TTL;
- billing;
- Usage fields;
- tool protocol.

Recommended Capability Snapshot:

```yaml
provider: deepseek
model: deepseek-v4-pro
observed_at: 2026-07-16
prefix_cache:
  observable: true
  hit_field: prompt_cache_hit_tokens
  miss_field: prompt_cache_miss_tokens
  ttl: unknown
  deterministic: false
limitations:
  - endpoint/account/time scoped
```

An observation from one Endpoint must not be generalized to every model or future date.

---

## 8. Decision Metrics

### 8.1 Cache

```text
shared prefix ratio
cache hit tokens
cache miss tokens
hit stability across runs
TTL behavior
```

### 8.2 Performance

```text
TTFT
total latency
input cost
total cost
```

### 8.3 Quality and Safety

```text
first-pass success
constraint violations
incorrect tool calls
human intervention
stale context incidents
```

### 8.4 Complexity

```text
prefix segment count
invalidation frequency
serializer bugs
state synchronization defects
maintenance effort
```

---

## 9. Experimental Design

Compare:

```text
A. no stabilization: natural request assembly
B. Canonical Serializer
C. segmented stable prefix + Dynamic Tail
D. C + independent Planner/Reviewer Sessions
```

On the same held-out tasks measure:

- task success;
- cost;
- latency;
- Cache;
- invalidation count;
- maintenance defects.

Include safety-policy and tool-permission changes to verify that the system sacrifices Cache correctly.

---

## 10. When Byte Stability Should Become an Architectural Invariant

Only when all of the following hold should Byte Stability become a strong engineering constraint:

1. the Provider delivers stable and observable benefit;
2. stable segments are a meaningful share of the request;
3. Canonicalization introduces no protocol error;
4. quality and safety do not decline;
5. invalidation is explicit and reliable;
6. complexity has positive net value;
7. multi-round and cross-time experiments are reproducible.

Otherwise it should remain a local optimization rather than a root system principle.

---

## 11. Conclusion

Byte-Stable Prefix is a valuable Harness optimization direction, but it must be constrained accurately:

- it optimizes computation reuse for common prefixes;
- it does not guarantee constraint compliance;
- it does not prove higher model quality;
- it cannot block required safety and factual updates;
- it requires segmentation, versions, a Canonical Serializer, a Manifest, and Invalidation Policy;
- its value is determined jointly by cost per successful task, latency, quality, safety, and maintenance complexity.

Cache is a means. A correct, recoverable, and auditable Agent is the objective.
