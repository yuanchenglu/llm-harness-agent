# Reasoning Effort Control: How to Make the Model "Think Harder" — And What It Costs

> **Evidence note:** Based on the definition of `REASONING_EFFORT_MAX` in `encoding_dsv4.py` and the rendering logic of the `reasoning_effort` parameter, this article presents design hypotheses. The actual effectiveness of the three reasoning tiers (max/high/None) requires end-to-end experimental validation. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-17
> **LLM + Harness = Agent** · Part 17
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [I-16 Quick Instruction Routing](16-quick-instruction-routing.md)
> Next: [I-18 Latest Reminder Injection](18-latest-reminder-injection.md)

---

## Problem: When Does the Model Need to "Think Harder"?

Making the model think harder can produce better answers, but it also makes them slower and more expensive. Not every question deserves deep reasoning. "1+1=?" requires no thought, but "debug this 200-line concurrency bug" does.

The ideal state: the Harness dynamically adjusts reasoning depth based on task complexity. DeepSeek V4's `reasoning_effort` parameter provides this capability, but only defines three tiers. How to choose between them, when to switch, and at what cost — these require systematic analysis.

---

## Key Evidence: Three-Tier Reasoning Intensity Design

The `reasoning_effort` parameter in `encoding_dsv4.py` accepts three values: `"max"`, `"high"`, and `None` (L261):

```python
assert reasoning_effort in ['max', None, 'high'], f"Invalid reasoning effort: {reasoning_effort}"
```

Only the `"max"` tier has a tangible effect — it injects a set of strong reasoning instructions at the very beginning of the prompt (before the system message) in thinking mode (L262-263):

```python
if index == 0 and thinking_mode == "thinking" and reasoning_effort == 'max':
    prompt += REASONING_EFFORT_MAX
```

And the content of `REASONING_EFFORT_MAX` (L64-68):

```python
REASONING_EFFORT_MAX = (
    "Reasoning Effort: Absolute maximum with no shortcuts permitted.\n"
    "You MUST be very thorough in your thinking and comprehensively decompose "
    "the problem to resolve the root cause, rigorously stress-testing your logic "
    "against all potential paths, edge cases, and adversarial scenarios.\n"
    "Explicitly write out your entire deliberation process, documenting every "
    "intermediate step, considered alternative, and rejected hypothesis to ensure "
    "absolutely no assumption is left unchecked.\n\n"
)
```

This instruction takes approximately 350 characters, roughly 90 tokens. Syntactically, it reads like an enhanced system prompt — but its position is entirely different.

---

## Three Tiers: When to Use Which

### 1. `reasoning_effort=None` (Default)

No reasoning intensity instruction is injected. The model uses its default reasoning depth.

**Applicable scenarios:** Daily Q&A, simple code completion, knowledge lookup, literal translation, format conversion.

**Cost:** Zero additional token overhead. Reasoning depth is determined autonomously by the model.

### 2. `reasoning_effort="high"`

In the source code, `"high"` is validated as a legal value (L261), but has no special logic in `render_message()`.

**Probable (>90%)** that `"high"` is a backend parameter that influences the model's internal reasoning behavior rather than the prompt structure. Similar to OpenAI's `reasoning_effort` parameter, consumed by the inference engine rather than the encoding layer.

**Applicable scenarios:** Medium-complexity tasks — code review, single-file refactoring, data interpretation, solution design.

**Cost:** Does not increase prompt length, but the model's deeper internal reasoning increases latency and completion token consumption.

### 3. `reasoning_effort="max"`

Injects the `REASONING_EFFORT_MAX` instruction at the very beginning of the prompt. The placement of this instruction is deliberate:

- ✅ After the `BOS` token, before the `system prompt` — it is the first content the model sees
- ✅ Only active when `thinking_mode="thinking"` — this parameter is ignored in chat mode
- ✅ Only injected when `index == 0` — injected once, never repeated in subsequent turns

**Applicable scenarios:** High-difficulty tasks — complex bug debugging, architecture decisions, security audits, mathematical proofs.

**Cost:** ~90 additional prompt tokens + significantly more reasoning output tokens + longer thinking latency.

---

## Why Prompt Position Matters

`REASONING_EFFORT_MAX` is injected at the **absolute earliest position** in the prompt — even before the system prompt. This is deliberately designed:

```
<bos>REASONING_EFFORT_MAX{system_prompt}<User>{question}...
```

In a KV Cache architecture, tokens positioned earlier are revisited by the attention mechanism during every decoding step (they form the prefix), exerting the greatest influence. Placing the reasoning intensity instruction here means: **every single token generation by the model is affected by it** — not a local option, but a global constraint.

By contrast, if you place the same instruction somewhere inside the system prompt, its attention share gets diluted by subsequent system prompt content. Placing it first makes it the underlying tone of the model's generative behavior.

---

## Implications for Harness

### 1. Dynamic Reasoning Intensity Routing

The most basic integration is to make `reasoning_effort` a dynamic parameter:

```python
def classify_reasoning_effort(user_prompt: str) -> str:
    if contains_complex_bug_pattern(user_prompt):  return "max"
    if contains_code_review_pattern(user_prompt):   return "high"
    return None  # default
```

Set the `reasoning_effort` value before each call to `encode_messages()`.

### 2. Cost Budget Management

The three tiers correspond to three distinct cost budgets:

| Dimension | None | high | max |
|-----------|------|------|-----|
| Prompt token overhead | 0 | 0 | ~90 |
| Completion token overhead | Baseline | Moderate (≈1.5-2x) | Significant (≈2-5x) |
| End-to-end latency | Baseline | +20-50% | +50-200% |
| Suitable budget | Daily | Important tasks | Critical tasks |

### 3. Synergy with Other Optimizations

Under `reasoning_effort="max"`, the reasoning output volume increases significantly. This makes [I-14 Reasoning Content Stripping](14-reasoning-content-stripping.md) especially important in long conversations — you don't want to cram the excessively long reasoning content produced by `max` mode back into the next turn's prompt.

---

## Limitations and Open Questions

1. **The actual behavior of `"high"` is unknown.** The source code only validates it as a legal value but has no front-end logic (independent of prompt structure). It may be passed as an API parameter to the backend inference engine. The difference in effect requires end-to-end comparative experiments.
2. **Different models interpret `reasoning_effort` differently.** DeepSeek V4's three-tier semantics do not apply to Anthropic's or OpenAI's reasoning parameters. The Harness needs provider-specific adaptation.
3. **Is `REASONING_EFFORT_MAX` purely a prompt effect or a model fine-tuning feature?** If the model has never seen this instruction during training, its effect may be limited. But if the model has been fine-tuned to recognize this instruction, the effect would be more reliable. Currently uncertain.

---

## Validation Path

1. For the same high-difficulty problem, call with `None`, `"high"`, and `"max"` respectively, and compare reasoning output length and final answer quality.
2. Measure the end-to-end latency differences across the three tiers (average of 5 random questions).
3. Compare output quality when `REASONING_EFFORT_MAX` is placed at the beginning of the prompt vs. inside the system prompt — to validate the hypothesis that "position matters."

---

*This article is based on lines 64-68 of encoding_dsv4.py (REASONING_EFFORT_MAX definition) and lines 261-263 (reasoning_effort parameter rendering logic).*
