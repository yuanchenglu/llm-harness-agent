# Reasoning Content Replay Policy: Protocol Correctness Before Token Optimization

> **Evidence level: A1 + A0/E3 + B**  
> - **A1**: fixed implementation source confirms that some Harnesses and encoding paths conditionally retain or remove reasoning content.  
> - **A0/E3, scoped to an Endpoint, account, and time window**: project protocol experiments show that ordinary multi-turn behavior can differ from Tool Loops, and HTTP 200 does not prove that field semantics took effect.  
> - **B**: the net quality, cost, and Cache benefit of removing reasoning must be reproduced by Provider, model, mode, and task.  
> Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-14  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Related**: [I-13 Byte-Stable Prefix](13-byte-stable-prefix-architecture.md)

---

## Abstract

A reasoning-model response may contain:

```text
visible content
tool calls
reasoning / thinking content
provider metadata
signatures or encrypted blocks
```

There is no Provider-independent answer to whether reasoning must be replayed on the next turn. Possible behaviors include:

- ordinary multi-turn conversation permits removal;
- Tool Call continuity requires exact replay;
- the Provider handles it automatically;
- an SDK rewrites fields;
- a field is display-only;
- a field is signed and cannot be modified;
- different Endpoints from the same Provider behave differently.

A Harness should therefore avoid a global `strip_reasoning=true`. It should use a versioned **Replay Policy**:

```text
Provider Capability
+ Response Shape
+ Tool State
+ Thinking Mode
+ Endpoint Evidence
→ Replay / Drop / Summarize / Reject Unknown
```

---

## 1. Public Corrections

### 1.1 Reasoning is not “100% worthless tokens”

Earlier versions described replayed reasoning as pure waste and used fixed token and monetary examples. That claim was too strong.

Reasoning may:

- be part of Tool Call protocol continuity;
- contain a Provider-required signature or state;
- be cached server-side;
- affect later inference;
- be removed or reconstructed by the Provider in some modes.

It is an optimization only after protocol deletion is confirmed safe, task quality remains stable, and Usage shows real benefit.

### 1.2 Field names cannot be generalized across Providers

`reasoning_content`, thinking blocks, encrypted content, and reasoning items are different protocols. The internal Runtime may expose a unified abstraction, but the Wire Adapter must preserve Provider-specific rules.

### 1.3 Encoding source is not a hosted API Wire Contract

`_drop_thinking_messages` in `encoding_dsv4.py` proves that the encoding implementation contains corresponding preprocessing logic. It does not independently prove that:

- public API clients should copy the same logic;
- the hosted service runs exactly that version;
- every turn in a Tool scenario must retain reasoning;
- removal saves a fixed number of tokens.

### 1.4 HTTP 200 does not prove semantic correctness

A successful response after removing a field proves only that the server accepted the request. Also verify:

- continuity on the next turn;
- correct association of Tool Results;
- output quality;
- Usage changes;
- delayed failures in later turns.

---

## 2. Message-Content Classification

```typescript
type AssistantTurn = {
  visibleContent?: string;
  toolCalls?: ToolCall[];
  reasoning?: ReasoningPayload;
  providerMetadata?: Record<string, unknown>;
};
```

### 2.1 Visible Content

Used for conversational continuity. It may be retained, summarized, or rewritten during Compaction, subject to product semantics.

### 2.2 Tool Calls

Usually must remain consistent with Tool Results in ID, order, and state. Critical call records must not be removed merely to save tokens.

### 2.3 Reasoning Payload

Provider-specific:

```typescript
type ReasoningPayload = {
  format: "plain_text" | "signed_block" | "encrypted" | "provider_item";
  rawRef: string;
  replayRequirement: "required" | "optional" | "forbidden" | "unknown";
  sensitivity: "restricted";
};
```

### 2.4 Provider Metadata

May contain IDs, signatures, state, and sequence numbers. An Adapter must not discard unknown fields and continue a high-risk process silently.

---

## 3. Replay Policy

```yaml
policy_id: deepseek-thinking-tools-v3
provider: deepseek
endpoint_capability_version: 2026-07-27
conditions:
  thinking: true
  has_tools: true
action: replay_required_fields
fields:
  - role
  - content
  - reasoning_content
  - tool_calls
fallback_on_unknown: stop_and_probe
```

### 3.1 Actions

| Action | Meaning |
| --- | --- |
| `replay_exact` | Replay the structure exactly as required by the Provider |
| `replay_required_fields` | Retain only fields confirmed necessary by the Capability Matrix |
| `drop_reasoning` | Remove reasoning while retaining visible content and tool state |
| `summarize_visible_content` | Compact only visible conversation, leaving protocol state untouched |
| `stop_and_probe` | Stop or run a safe probe when the protocol is unknown |

### 3.2 Safe default

```text
unknown protocol + Tool side effect
→ do not attempt aggressive deletion
→ retain the original server structure or stop
```

Token optimization cannot outrank Tool Loop correctness.

---

## 4. Capability Matrix

```yaml
provider: deepseek
model: deepseek-v4-pro
endpoint: <redacted-endpoint-id>
observed_at: 2026-07-27
modes:
  ordinary_thinking:
    replay_reasoning:
      accepted: true
      semantic_effect: unverified
    drop_reasoning:
      accepted: true
      continuity: observed_in_test_window
  tool_thinking:
    replay_reasoning:
      accepted: true
    drop_reasoning:
      accepted: inconsistent_or_unverified
limitations:
  - endpoint/account/time scoped
  - hosted API behavior may differ from encoding source
```

Every conclusion must bind to:

- Request Fixture;
- Response Shape;
- HTTP Status;
- subsequent multi-turn results;
- Usage;
- repetition count;
- time and Endpoint.

---

## 5. Adapter Architecture

```text
Session Store
→ Provider-neutral AssistantTurn
→ Replay Policy
→ Provider Wire Builder
→ Raw Request Fingerprint
→ Response Recorder
```

### 5.1 Session Store

It may retain restricted references but should not expose complete reasoning to the normal UI, logs, or Diagnostics by default.

### 5.2 Wire Builder

Apply Policy only while building the request so one Provider-specific optimization does not permanently destroy the original Session model.

### 5.3 Unknown Fields

When a Provider returns a new field:

- record the field set and capability version;
- do not print sensitive values;
- handle conservatively inside a Tool Loop;
- trigger Capability Review.

---

## 6. Safety and Privacy

### 6.1 Reasoning sensitivity

Reasoning may contain:

- private user information;
- accidental repetition of a Secret;
- internal policy;
- unverified inference;
- security-analysis details.

By default it should:

- not enter normal logs;
- not enter Diagnostics;
- not become long-term Memory;
- not become Skill source text;
- preserve only required structure and Hash/Ref.

### 6.2 Separate display from protocol

A Provider requirement to replay a field does not imply that the user must see it. User-facing explanations should be concise product-designed rationales, not raw hidden reasoning.

### 6.3 Tool Injection

Commands or Tool suggestions appearing in reasoning have no execution authority. Tool Calls still require Schema, Policy, Permission, and Approval.

---

## 7. Compaction

Compaction should process separately:

```text
visible conversation
protocol-required tool state
evidence refs
reasoning payload
```

### 7.1 Compressible

- historical visible responses;
- closed discussion;
- repeated explanation.

### 7.2 Must not be compacted arbitrarily

- an unfinished Tool Call chain;
- Tool Call ID / Result pairing;
- Approval and ChangeSet state;
- Provider-required signed blocks;
- current errors and recovery conditions.

### 7.3 Session Rebuild

When protocol requirements and historical structure are incompatible, create an explicit Compaction/Reset point and record:

```text
old session ref
summary artifact
retained evidence
provider reset reason
cache reset reason
```

---

## 8. Experimental Design

### 8.1 Protocol matrix

```text
ordinary / tools
thinking / non-thinking
replay / drop / modified
stream / non-stream
Flash / Pro
SDK / raw HTTP
```

### 8.2 Continuity tasks

- multi-turn code modification;
- sequential Tool Calls;
- parallel Tool Calls;
- retry after Tool Failure;
- continuation after Compaction;
- Provider/model switching.

### 8.3 Metrics

```text
HTTP success
next-turn continuity
tool-call completion
first-pass task success
incorrect tool association
input tokens
cache hit/miss
latency
cost per successful task
```

### 8.4 Result discipline

- do not conclude from a single request;
- distinguish accepted from semantically effective;
- report failure samples;
- randomize execution order;
- repeat across time;
- snapshot prices instead of hard-coding permanent monetary amounts.

---

## 9. Decision Rules

For `drop_reasoning` to become a default strategy, at least:

1. the Provider/Endpoint explicitly allows it or experiments support it consistently;
2. ordinary multi-turn and Tool Loop behavior are validated separately;
3. task quality does not decline;
4. Tool State is not lost;
5. token/cost benefit is reproducible;
6. a Feature Flag and rapid rollback exist;
7. Capability changes trigger revalidation.

---

## 10. Boundaries and Risks

- Provider protocols change quickly;
- SDK and Raw HTTP behavior may differ;
- the server may rewrite messages automatically;
- Tool scenarios may fail only in a later turn;
- removing reasoning may reduce quality on some tasks;
- retaining reasoning may increase cost and privacy risk;
- a hosted Endpoint may differ from public source;
- Usage fields may be incomplete.

Capability Versions, conservative defaults, Telemetry, and rollback are required.

---

## 11. Conclusion

Reasoning Content handling is not a binary choice between “replay everything” and “drop everything.”

A reliable Harness should:

1. distinguish visible content, Tool State, Reasoning, and Provider Metadata;
2. select Replay Policy from Provider/Endpoint Capability;
3. handle ordinary multi-turn and Tool Loops separately;
4. apply policy in the Wire Builder without corrupting the internal Session model;
5. stop conservatively or probe when the protocol is unknown;
6. jointly evaluate continuity, task success, tokens, Cache, cost, and privacy;
7. never use raw reasoning as user-facing explanation, Memory, or Skill material.

Every token should justify its value, but protocol correctness must be proven first.
