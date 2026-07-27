# Reasoning Effort Control: Parameter Acceptance, Actual Semantics, and Task Benefit Must Be Validated Separately

> **Evidence level: A1 + N/B**  
> - **A1**: fixed `encoding_dsv4.py` source confirms that `reasoning_effort` accepts `None / high / max`, and that `max` injects an enhanced reasoning instruction under specific conditions.  
> - **N/B**: whether `high` is consumed by a server-side backend, whether the public API exposes the same semantics, and the quality/latency/token effects of each value all require end-to-end experiments.  
> Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-17  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [16 Quick Instruction Routing](16-quick-instruction-routing.md)  
> **Next**: [18 Latest Reminder Injection](18-latest-reminder-injection.md)

---

## Abstract

“Make the model think harder” is not one capability. It may involve:

- a request parameter;
- model selection;
- Thinking Mode;
- Prompt instructions;
- maximum output tokens;
- a Planner / Reviewer;
- retry and verification budgets.

Encoding source can prove that certain fields and Prompt-rendering paths exist. It cannot independently prove hosted API behavior or benefit.

A reliable Harness should model reasoning intensity as Provider Capability plus Budget Policy:

```text
Task Risk / Uncertainty / Evidence Gap
→ Candidate Reasoning Policy
→ Provider Capability Check
→ Execute with Budget
→ Verify Result
→ Escalate or Stop
```

---

## 1. What the Source Confirms

The fixed encoding source contains validation similar to:

```python
assert reasoning_effort in ["max", None, "high"]
```

Under a specific `thinking_mode` and message position, `max` injects enhanced reasoning text.

A1 conclusions:

- the encoding implementation accepts three values;
- `max` has a visible Prompt-rendering path;
- `None` does not inject that text;
- in this encoding section, `high` does not use the same text-injection branch as `max`.

This does not confirm that:

- `high` is consumed by the backend inference engine;
- `high` is deeper than the default;
- the public API forwards the field;
- `max` improves answer quality;
- extra latency and tokens follow a fixed multiplier.

---

## 2. Public Corrections

### 2.1 Remove unverified fixed cost numbers

Earlier versions claimed:

```text
high: completion roughly 1.5–2x, latency +20–50%
max: completion roughly 2–5x, latency +50–200%
```

Those figures were not bound to a fixed Endpoint, task set, repeat count, or result artifact and are removed. Future claims must use distributions from reproducible experiments.

### 2.2 An accepted value does not mean the parameter took effect

An API or SDK may:

- accept and execute it;
- accept and ignore it;
- convert it into another parameter;
- support it only for some models;
- return 200 while behavior remains unchanged.

Output, Usage, latency, and task quality must be examined together.

### 2.3 Prompt position does not prove “maximum attention weight”

Placing an instruction first, in System, or near the latest user message may change behavior, but internal attention weight cannot be inferred from position alone. Use an A/B test.

### 2.4 More reasoning does not mean more correctness

Longer reasoning may:

- discover additional edge cases;
- create additional incorrect assumptions;
- increase latency and cost;
- delay recognition that tool evidence is missing;
- over-analyze a simple task.

Final quality must be determined by Verifiers and task outcomes.

---

## 3. Provider Capability

```yaml
provider: deepseek
endpoint: <redacted-endpoint-id>
model: deepseek-v4-pro
observed_at: 2026-07-27
thinking_mode:
  supported: unknown
reasoning_effort:
  accepted_values:
    - null
    - high
    - max
  high_semantics: unverified
  max_prompt_injection_in_source: true
  public_api_effect: unverified
limitations:
  - encoding source does not prove hosted endpoint behavior
```

Capability records require time, Endpoint, model, and evidence source. They must not become permanent global constants.

---

## 4. Internal Harness Policy

Provider-neutral representation:

```typescript
type ReasoningPolicy = {
  mode: "minimal" | "standard" | "deep";
  maxInputTokens: number;
  maxOutputTokens: number;
  maxLatencyMs: number;
  maxCost: number;
  requirePlanner: boolean;
  requireIndependentReview: boolean;
  providerParams: Record<string, unknown>;
};
```

The upper product layer should not depend directly on the strings `high` or `max`.

### 4.1 Minimal

Appropriate for:

- deterministic format conversion;
- simple queries;
- low-risk tasks with a strong Verifier;
- quickly retryable work.

### 4.2 Standard

Appropriate for:

- ordinary code changes;
- multi-step analysis;
- medium-risk decisions;
- tasks requiring tool evidence.

### 4.3 Deep

Candidate conditions:

- high risk and difficult rollback;
- multiple conflicting constraints;
- complex architecture tradeoffs;
- repeated Verifier failure;
- conflicting critical Evidence;
- security review.

Deep does not authorize automatic execution. High-risk actions still require Policy and Approval.

---

## 5. Routing Signals

Do not route only by keyword:

```python
if "code review" in prompt:
    effort = "high"
```

More reliable signals:

```text
risk
reversibility
blast radius
uncertainty
evidence completeness
novelty
verifier failures
remaining budget
```

Example:

```yaml
reasoning_route:
  policy: deep
  reasons:
    - risk:R3
    - irreversible:false
    - verifier_failures:2
    - evidence_conflict:true
  budget:
    max_latency_ms: 60000
    max_cost: <configured-budget>
  exit_conditions:
    - verifier_pass
    - user_intervention
    - budget_exhausted
```

---

## 6. Escalation Instead of a One-Time Guess

Recommended flow:

```text
Standard Attempt
→ Deterministic Verification
→ if pass: finish
→ if failure is repairable: retry with failure evidence
→ if high risk or repeated failure: Deep + Independent Review
→ if budget is exhausted or evidence is insufficient: stop and ask the user
```

This avoids using the most expensive mode at the beginning of every task.

### 6.1 Escalation record

```text
from policy
to policy
trigger
previous failure evidence
additional budget
outcome
```

### 6.2 Prevent infinite “deep thinking”

Set:

- maximum retries;
- maximum tokens;
- maximum latency;
- maximum cost;
- stop conditions;
- human takeover.

---

## 7. Reasoning Content and Subsequent Turns

A deeper mode may generate more reasoning content, but replay depends on Provider protocol:

- some Tool Call chains require retention;
- some ordinary multi-turn paths permit removal;
- some servers handle it automatically;
- billing and Cache behavior may differ.

Use the Capability Matrix from [I-14 Reasoning Content Replay Policy](14-reasoning-content-stripping.md). Never remove reasoning unconditionally merely to save tokens.

---

## 8. Experimental Matrix

### 8.1 Protocol

```text
None / high / max
thinking / non-thinking
stream / non-stream
tools / no tools
raw HTTP / SDK
```

Confirm:

- whether the field is accepted;
- response structure;
- whether it is silently ignored;
- whether a Tool Loop can continue.

### 8.2 Quality

Task classes:

- simple deterministic task;
- ordinary code change;
- concurrency Bug;
- architecture decision;
- security review;
- adversarial question with a false premise.

Metrics:

```text
first-pass success
verifier pass
constraint violation
factual/source accuracy
human preference
```

### 8.3 Resources

```text
reasoning tokens
output tokens
input tokens
cache hit/miss
TTFT
total latency
cost
```

### 8.4 Experimental discipline

- randomize execution order;
- repeat multiple times;
- record service status;
- separate development and held-out sets;
- report distributions and failure samples;
- do not compare output length only.

---

## 9. Decision Rule

A deeper policy should enter default routing only when:

```text
quality improvement is reproducible
AND
cost per successful task remains within budget
AND
latency meets product requirements
AND
safety violations do not increase
```

If it only increases reasoning length without improving Verifier Pass or reducing human intervention, reject the policy.

---

## 10. Boundaries and Risks

- Provider parameters may change;
- `high` may be ignored;
- `max` may be only Prompt injection;
- longer reasoning may expose more sensitive content;
- Tool Call protocol may require reasoning replay;
- Deep mode may amplify a false premise;
- the Router may over-escalate simple tasks;
- cost estimates may expire after price changes.

Capability Versions, budgets, Fallback, and a disable switch are required.

---

## 11. Conclusion

Three legal values in source code cannot be directly converted into three stable product tiers.

A reliable implementation must:

1. distinguish parameter acceptance, semantic effect, and task benefit;
2. encapsulate Provider-specific fields inside the Adapter;
3. escalate from risk, reversibility, Evidence, and Verifier failures;
4. set token, latency, cost, and retry ceilings;
5. measure quality and cost per successful task on held-out work;
6. stop when evidence is insufficient instead of “thinking harder” indefinitely.

Longer reasoning is not the goal. More reliable outcomes at controlled cost are the goal.
