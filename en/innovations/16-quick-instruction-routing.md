# Quick Instruction Routing: Separate Encoding-Layer Capability from Public API Availability

> **Evidence level: A1 + N/B**  
> - **A1**: fixed `encoding_dsv4.py` source confirms the existence and rendering logic of the `action / query / authority / domain / title / read_url` special tokens.  
> - **N/B**: current public evidence is insufficient to prove that a client can set a `task` field in a standard API request and trigger those behaviors reliably; product integration still requires an Endpoint Spike.  
> Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-16  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [15 DSML Encoding-Layer Research](15-dsml-tool-call-optimization.md)  
> **Next**: [17 Reasoning Effort Control](17-reasoning-effort-control.md)

---

## Abstract

DeepSeek V4 encoding source defines six task-specific tokens:

```text
action
query
authority
domain
title
read_url
```

They indicate that the model encoding or service stack may support specialized task modes for short-output classification, query generation, title generation, and URL decisions.

A critical boundary remains:

```text
encoding function accepts a task field
≠
standard public Chat API accepts a client task field
```

The correct Harness strategy is therefore:

1. treat Quick Instruction as a Provider Capability;
2. run an end-to-end raw HTTP probe first;
3. enable default routing only after the Wire Contract and behavior are stable;
4. always retain a standard Prompt / Tool-routing fallback;
5. never convert internal source-level task names directly into product promises.

---

## 1. What the Source Confirms

The fixed source contains a mapping similar to:

```python
DS_TASK_SP_TOKENS = {
    "action": "<｜action｜>",
    "query": "<｜query｜>",
    "authority": "<｜authority｜>",
    "domain": "<｜domain｜>",
    "title": "<｜title｜>",
    "read_url": "<｜read_url｜>",
}
```

Message rendering selects a special token according to `task`.

A1 conclusion:

> The DeepSeek V4 encoding implementation contains six specialized task tokens and corresponding Prompt-rendering paths.

The source alone does not confirm that:

- the public API request Schema exposes `task`;
- an SDK forwards `task`;
- the hosted service version matches the source;
- output values and formats are stable;
- the mode is faster, cheaper, or more accurate than an ordinary Prompt.

---

## 2. Three-Layer Boundary

### 2.1 Model encoding layer

Converts structured messages into the model token sequence.

### 2.2 Provider service layer

May:

- use the encoding logic above;
- whitelist or discard client fields;
- invoke these tasks internally;
- keep them private from external users;
- run a different implementation version.

### 2.3 Harness client

May rely only on:

- official API documentation;
- SDK behavior;
- raw HTTP Wire Evidence;
- repeatable Endpoint experiments.

A client must not add an undocumented field to a standard API and treat HTTP 200 as proof that its semantics took effect.

---

## 3. Reasonable Hypotheses for the Six Tasks

The following are engineering interpretations based on token names and rendering position, not confirmed public product semantics.

| Task | Candidate use | Must be validated |
| --- | --- | --- |
| `action` | Route between search, answer, or action | output enum, accuracy, interaction with thinking |
| `query` | Generate a search query | multilingual behavior, length, injection risk |
| `authority` | Decide whether authoritative sourcing is required | label set, calibration, domain transfer |
| `domain` | Domain classification | taxonomy, open-set handling, confusion matrix |
| `title` | Generate a conversation title | length, language, sensitive-information leakage |
| `read_url` | Decide whether a URL should be fetched | multiple URLs, malicious URLs, output format |

Candidate use does not replace protocol documentation or end-to-end evidence.

---

## 4. Capability Probe

### 4.1 Request paths

Compare at least:

```text
raw HTTP with documented fields
raw HTTP with task field
official SDK with task field
standard prompt emulation
```

### 4.2 Result classification

| Result | Meaning |
| --- | --- |
| 4xx unknown field | Public API does not support it |
| 200 but behavior unchanged | Field may have been ignored |
| 200 with short but unstable output | Experimental capability; do not productize yet |
| 200 and stable across models/time | May enter a Capability Snapshot |
| SDK drops the field | Raw HTTP only; maintenance cost must be assessed |

HTTP 200 proves request acceptance, not parameter semantics.

### 4.3 Manifest

```yaml
probe_id: quick-instruction-action-20260727
provider: deepseek
endpoint: <redacted-endpoint-id>
model: deepseek-v4-pro
sdk_version: null
request_variant: raw-http-task-field
repeats: 20
observed_at: 2026-07-27
response_schema:
  fields: [choices, usage]
behavior:
  expected_labels: [Search, Answer]
  exact_match_rate: null
status: unverified
limitations:
  - endpoint/account/time scoped
```

---

## 5. Product Integration Architecture

### 5.1 Provider-Neutral Router

```typescript
interface RouteRequest {
  task: string;
  context?: unknown;
  allowedLabels?: string[];
}

interface RouteResult {
  label: string;
  confidence?: number;
  rawOutputRef: string;
  providerCapability: string;
  fallbackUsed: boolean;
}
```

The Router must not expose private tokens such as `action` to upper-layer product logic.

### 5.2 Adapter selection

```text
if provider capability verified:
    use quick-instruction adapter
else:
    use standard structured prompt or lightweight classifier
```

### 5.3 Output normalization

Even when a specialized mode is expected to return one word, handle:

- leading/trailing whitespace;
- capitalization;
- multiline explanation;
- unknown labels;
- empty output;
- truncation;
- Prompt Injection;
- streaming increments.

Use an Allowlist and an Unknown fallback. Never fuzzy-match a label and directly execute a high-risk action.

---

## 6. Risk Tiers

### 6.1 Low-risk uses

- conversation titles;
- candidate search queries;
- UI classification labels.

Errors are usually recoverable.

### 6.2 Medium-risk uses

- whether to search the web;
- whether to fetch a URL;
- tool-catalog selection.

Fallback and observability are required.

### 6.3 High-risk uses

- permission level;
- whether writes are allowed;
- whether an external side effect should execute;
- medical, legal, or financial authority judgments.

Quick Instruction alone is insufficient. Policy, deterministic rules, or human approval must remain authoritative.

---

## 7. Performance Hypotheses

Quick Instruction may produce short output, but end-to-end benefit depends on:

```text
additional network round trip
whether a long prefix is resent
Provider Cache hit
model queueing
output length
whether later calls are avoided
```

An extra classification call may be slower than allowing the main model to complete the task directly. Compare the full workflow:

```text
Router + Main Call
vs.
Single Main Call
```

Do not compare only Router output tokens.

---

## 8. Evaluation

### 8.1 Classification quality

```text
accuracy
macro F1
open-set rejection
confidence calibration
cost-weighted errors
```

### 8.2 Query quality

```text
search recall
result relevance
query injection rate
language quality
```

### 8.3 URL decisions

```text
necessary-fetch recall
unnecessary-fetch rate
malicious-url handling
multi-url accuracy
```

### 8.4 Performance

```text
router latency
workflow latency
total tokens
cache hit/miss
cost per successful task
```

### 8.5 Controls

Compare:

- Quick Instruction;
- a standard short Prompt;
- a rule classifier;
- a small-model classifier;
- no separate routing.

Use held-out data and repeat across time.

---

## 9. Boundaries and Failure Modes

- the API may silently ignore the field;
- output labels may be undocumented;
- model updates may change behavior;
- combinations with Tools / Thinking / Streaming may be incompatible;
- specialized tasks may be internal-only;
- an extra routing step increases latency;
- classification errors may select the wrong tool or source;
- concatenating private tokens directly may break the protocol.

A Feature Flag, Fallback, Capability Version, and disable switch are mandatory.

---

## 10. Conclusion

Quick Instruction source evidence is valuable, but the accurate current conclusion is:

1. six special tokens and encoding paths exist;
2. public API exposure of a `task` field still requires Wire Evidence;
3. a client must not implement an undocumented protocol directly from encoding source;
4. the product layer should use a Provider-Neutral Router and standard fallback;
5. high-risk decisions must not depend only on a short classification output;
6. value must be validated through full-workflow quality, latency, and cost.

Source confirms what capability may exist. Endpoint experiments determine whether a client can use it reliably today.
