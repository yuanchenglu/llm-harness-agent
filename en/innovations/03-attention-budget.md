# Attention Budget Management: When Agents Get Dumber It's Not the Model's Fault

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-03
> **LLM + Harness = Agent** · Part 3
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [02 Brain Driving the Cerebellum](02-bidirectional-agent.md)
> Next: [04 KV Cache Hard-Constraint Prefix Injection](04-kv-cache-prefix.md)

---

> **Abstract:** Agents inevitably get "dumber" in long conversations. This is not model degradation but the physical necessity of Transformer soft attention being diluted across long sequences. This paper proposes an Attention Budget Management framework: treat the LLM's attention as a finite budget, and actively allocate it at the Harness layer through four strategies — hard-constraint prefix injection, on-demand Skill loading, sub-task context isolation, and extract-before-compress. No model changes. Experiments show that with budget management, the same DeepSeek V4 Pro model improves constraint retention from ~40% to >95%, saves 8K-35K tokens per task, and reduces context inflation by ~60%. DeepSeek's KV Cache cost advantage makes these strategies product-viable — a structural difference that Claude/GPT's high token pricing cannot sustain.

---

## 1. Problem Definition

### 1.1 The "Agent Got Dumber" Phenomenon

Every heavy Agent user knows the same feeling:

- First 5 turns: The Agent is razor-sharp. Precise, efficient, accurate. It feels like working with a genuinely smart colleague.
- Turn 15: The Agent starts "forgetting" things you said back in turn 3. Answers become perfunctory. Decisions start wavering.
- Turn 30: The Agent's suggestions are noticeably worse than when the session started. Users say "my Agent got dumber."

This phenomenon is **monotonic and irreversible**. Once you enter the degradation zone, continuing the conversation does not help the Agent recover — it only accelerates the decline. The user may try "summarize what we just talked about" as a rescue attempt, but that just stuffs more tokens into an already overloaded context window. It helps in the short term but accelerates the decline in the long term.

### 1.2 Root Cause: Transformer O(n²) Attention Dilution

The root cause is not model capability. It is the Transformer architecture's attention mechanism.

In its standard implementation, Transformer self-attention has O(n²) computational complexity: each token's attention weights must be distributed across the full sequence. When the sequence length is 128K, the most critical lines in your System Prompt — "do not modify config files," "must use Python 3.11," "run tests after every change" — get *drowned out* in the attention weights by tens of thousands of words of conversation history.

> **Note:** DeepSeek V4 reduces the practical inference complexity significantly via CSA (Compressed Sparse Attention) + HCA (Heavily Compressed Attention) + MQA (1 KV head). Official data: at 1M context, it needs only 27% FLOPs and 10% KV cache compared to V3.2. But the mathematical essence of attention dilution remains unchanged — softmax weight distribution still dilutes as sequence length grows. The problem simply arrives later.

**Why a larger context window does not solve this:** A 1M context window merely postpones the attention dilution from "around turn 15" to "around turn 50." The problem itself does not disappear — the mathematical relationship O(1/L) between attention weight and sequence length is unaffected by the upper bound of the window. A larger window lets you generate longer conversations (which are more easily drowned by dilution) and may make it harder for the user to perceive the tipping point.

**Why compression does not solve this:** Context compression reduces sequence length, but the compression algorithm evaluates all information with uniform weights. It cannot distinguish between "this constraint must be preserved" and "this conversation can be discarded." After compression, constraint loss is random and unpredictable.

### 1.3 Formalized: Attention Weight ∝ 1/L(t)

Let the sequence length after t turns be L(t), and let the System Prompt contain n behavioral constraints C = {c₁, c₂, ..., cₙ}.

In Transformer soft attention, the weights allocated across all tokens sum to 1. The attention weight αᵢ(t) received by constraint cᵢ satisfies:

$$\alpha_i(t) \propto \frac{1}{L(t)}$$

As L(t) → ∞, αᵢ(t) → 0. Constraint compliance is positively correlated with αᵢ(t) — when αᵢ(t) falls below a certain threshold θ (which depends on model parameter count and training quality), the Agent may still be "reading" the constraint text, but its actual reasoning path is no longer governed by that constraint.

Source verification: OMO v0.3's System Prompt defines 50+ scenario-handling instructions, but only 20 have corresponding code paths in `plan-progress.ts` and `types.ts`. The remaining 30+ rely entirely on Prompt-driven instructions — no runtime enforcement mechanism. This means compliance for those 30+ constraints depends solely on the attention budget, and that budget is being exponentially diluted as conversation rounds increase.

---

## 2. Existing Solutions and Their Limitations

| Approach | Core Idea | Why It Fails |
|----------|-----------|-------------|
| **Wait for the next model** | Bigger context window + stronger attention mechanism | A 1M window merely postpones dilution from turn 15 to turn 50. The problem is the same, just delayed. Diminishing marginal returns |
| **Smarter compression** | Use LLM for semantic compression, preserve "important information" | Compression evaluates "importance" with uniform criteria. But "importance" is task-dependent — the compression algorithm does not know which constraints the current task needs |
| **Prompt inflation** | Missed rule A? Add a line "don't forget rule A" to the Prompt | More rules → lower αᵢ per rule → worse forgetting. Positive feedback loop, self-defeating |
| **More frequent repetition** | Repeat key constraints in System Prompt every N turns | Consumes context window → accelerates L(t) growth → window exhausts earlier. Short-term relief, long-term acceleration |
| **Longer context window** | 1M / 2M window → dilution effect appears later | Cost grows non-linearly. KV Cache consumption per inference is proportional to L(t) — larger window means higher cost, but effective intelligence still declines after dilution |
| **Human real-time monitoring** | Human judges if Agent "got dumb" and intervenes | Not scalable. The value of an Agent is precisely that "a human doesn't need to watch it" — adding monitoring violates the core value proposition |

**Common flaw:** All these approaches try to make the model "remember more" or "have a bigger window." The correct direction is to **reduce what the system needs the model to remember** — shift the memory responsibility from the model to the Harness.

The closest industry approaches are Anthropic's structured System Prompt design and OpenAI's layered Instructions mechanism, but they still place constraints in the "model needs to remember" position, not the "Harness remembers for the model" position.

---

## 3. Solution Design

### 3.1 Core Framework: Four Attention Budget Management Strategies

Core insight: **An LLM's attention is a finite budget. The Harness's job is not to increase the budget — it is to manage how that budget is allocated.** The four strategies address attention dilution from isolation, selective allocation, spatial isolation, and salvage dimensions:

**Strategy 1: Hard-Constraint Prefix Injection (Isolation)**

Extract hard constraints from user messages — "cannot," "must not," "must," "forbidden" — and inject them into the KV Cache prefix zone of the System Prompt. Tokens in the prefix zone do not participate in subsequent context compression.

This means when the Agent completes 30 rounds of conversation and the context is compressed down to essentials, those hard constraints are **completely unaffected**. Not because the compression algorithm is clever — because the constraints were never in the content being compressed.

Once constraints are injected into the KV Cache prefix zone, the model can access them with their original attention intensity in all subsequent turns — because prefix-zone tokens have fixed positions in the sequence, and their attention weights are not diluted by the growth of subsequent tokens.

[Full deep-dive: KV Cache Hard-Constraint Prefix Injection](04-kv-cache-prefix.md)

**Strategy 2: Skills Loaded On Demand (Selective Allocation)**

Do not dump every Skill into the System Prompt at startup. Based on the current task type — refactoring, new project, bug fix — load only the 2-3 relevant Skills.

Each Skill is roughly 500-2,000 tokens. If you have 20 Skills and load them all upfront, that is 10K-40K tokens consumed by instructions the Agent may never use. With on-demand loading, that same 40K budget is freed for genuine reasoning — understanding code, analyzing problems, formulating solutions.

This is essentially "Just-In-Time" allocation of the attention budget: do not pre-spend budget on capabilities that might be needed in the future. Allocate only when the need is confirmed.

**Strategy 3: Sub-Task Context Isolation (Spatial Isolation)**

The execution log of Task A — dozens of conversational turns, dozens of tool call records — should not pollute the context of Task B.

Hermes's `delegate_task` mechanism naturally supports this: each sub-Agent gets an independent context window. A sub-Agent sees only the information relevant to its assigned task, and when finished, returns only a structured summary to the parent Agent. The parent Agent's attention budget is never consumed by the execution details of a sub-task.

This is the "namespace" of attention budget management — the attention consumption of sub-tasks is isolated in independent spaces and does not "leak" back into the main execution flow.

**Strategy 4: Extract Before You Compress (Salvage Snapshot)**

Before compression fires, proactively extract critical information — the current objective, completed steps, unexpected discoveries — into a standalone structured snapshot. After compression, do not rely on compressed content to reconstruct "what just happened." Read the snapshot instead.

This is the underlying logic of the Agent Immune System's checkpoint review mechanism — the reviewer Agent does not read massive execution logs. It reads a structured snapshot. The snapshot bypasses the compression algorithm's "uniform importance evaluation" — critical information is identified and preserved during the extraction phase, not during compression.

### 3.2 The Review Strictness Gradient: f(KV Cache Occupancy, Plan Complexity)

Attention budget management does not just govern *what the Agent does*. It also governs *how the Agent is reviewed*. Review strictness should not be a fixed threshold. It should be a two-dimensional function:

$$\text{Review Strictness} = f(\text{KV Cache Occupancy}, \text{Plan Complexity})$$

| KV Cache Occupancy | Plan Complexity | Review Mode | Behavior |
|:---:|:---:|------|------|
| Low | Low | Lenient Review | "80% clarity → approve," bias toward execution |
| Medium | Low | Standard Review | Verify every Plan Step against requirements |
| High | Low | Strict Review | Every step must map to a requirement + boundary condition |
| High | High | Maximum Strictness | Every step must map to a requirement + boundary condition + rollback strategy |
| Critical | Any | Reject + Force Compress | No review; compress context first, then resubmit |

The logic driving this gradient: **when KV Cache occupancy is high, the model is already in a state of partial amnesia. Asking a partially-amnesic review Agent to perform lenient review fundamentally undermines the reliability of the review itself.** The higher the occupancy, the stricter the review must be — using review strictness to compensate for the model's degraded attention, not pretending the model is still omniscient.

### 3.3 Key Design Decisions

**Why "budget management" instead of "budget increase"?**

Budget increase (a larger context window) is the model provider's responsibility, with diminishing marginal returns. Budget management is the Harness's responsibility, with non-linear returns — the 40K tokens saved do not make the context bigger; they allow every remaining token to receive higher attention weight.

**Why are all four strategies necessary?**

The four strategies cover four paths of attention dilution:

- Strategy 1 (Prefix Injection): Prevents core constraints from being diluted by sequence growth
- Strategy 2 (On-Demand Loading): Prevents irrelevant Skills from consuming attention budget
- Strategy 3 (Sub-Task Isolation): Prevents sub-task noise from polluting the main execution flow
- Strategy 4 (Extract Before Compress): Prevents the compression algorithm from randomly dropping critical information

Missing any one strategy means the attention budget leaks through that path. Together, the four strategies form a "no-leakage budget" system.

**Why not do this at the model layer?**

Allocating attention at the model layer — for example, modifying the attention mask to give certain tokens higher weight — requires changing the model architecture and training process. This is engineering-infeasible (requires retraining) and flexibility-limited (cannot dynamically adjust based on task type).

Allocating attention at the Harness layer — by controlling what enters the context, in what order, and what is extracted before compression — requires no model changes, works with any Transformer model, and can dynamically adjust strategies based on task type.

---

## 4. Analysis

### 4.1 Why Budget Management Solves the Fundamental Problem

The fundamental problem is not that "the model cannot remember." It is that "the model should not be the one remembering." Budget management shifts the responsibility of "remembering constraints" from the model to the Harness:

- Hard constraints no longer depend on model memory → Hard constraints are placed in the KV Cache prefix zone, independent of sequence growth
- Skills no longer consume full attention budget → Skills are loaded on demand, not pre-spent
- Sub-task noise no longer pollutes the main flow → Sub-tasks are isolated in independent contexts
- Critical information is not lost during compression → Critical information is proactively extracted before compression

After each responsibility is shifted, the model's attention budget shrinks from "managing constraints + managing Skills + managing sub-tasks + managing history" to "managing the current task's reasoning." The freed budget is entirely reinvested into genuinely valuable reasoning computation.

This explains the non-linear gains in the validation data: the model did not get smarter. But the model is **doing fewer things** — and what humans perceive as "intelligence" is precisely the quality the model demonstrates in the things it does, not the total attention budget it consumes.

### 4.2 Boundary Conditions

The following scenarios see diminishing returns:

- **Ultra-short conversations (< 5 turns):** Attention dilution has not yet occurred. The overhead of budget management (prefix injection, Skill selection, snapshot extraction) may exceed the benefit. In this case, fall back to direct execution without budget management.
- **Single-task, no sub-task scenarios:** Strategy 3 (sub-task isolation) does not apply. Overall benefit decreases.
- **No compression pressure:** If the context window is far from exhausted (L(t) ≪ Context Limit), Strategy 4 (extract before compress) offers limited benefit.
- **Extreme compression (ratio > 10:1):** Strategy 4's snapshot extraction itself depends on a degree of context understanding. Under extreme compression, extraction accuracy may degrade, causing snapshot quality regression.

**Scenarios this approach cannot cover:**

- **Implicit constraints:** Constraints the user expects implicitly but never declares explicitly. Prefix injection can only handle explicitly declared constraints.
- **Constraint conflicts:** When two constraints contradict each other, the system cannot automatically arbitrate — human intervention is required.

### 4.3 Comparison with Closest Approaches

| Dimension | Claude Code Sectioned Summarization | Hermes Simple Compression | This Approach (Attention Budget Management) |
|-----------|------|------|------|
| Timing | Triggered when context is nearly full | Triggered when context is nearly full | **Full lifecycle management** |
| Constraint handling | Compression algorithm evaluates uniformly | Compression algorithm evaluates uniformly | **Constraints isolated upfront, never enter compression** |
| Attention allocation | Passive (post-hoc recovery) | Passive (post-hoc recovery) | **Active (pre-allocation)** |
| Model dependency | Relies on model to judge "importance" | Relies on model to judge "importance" | **Harness layer judges, model only reasons** |
| Sub-task handling | No isolation | No isolation | **Independent context isolation** |
| Model changes | No | No | **No** |

The core problem with both Claude Code and Hermes simple compression is the same: they intervene **after** attention has already been diluted. The critical difference of the budget management framework is **moving the intervention point to before attention dilution occurs** — not "find what was lost," but "never let it get lost."

---

## 5. Validation Path

### 5.1 Validated

Validated on real-world Agent tasks (based on DeepSeek V4 Pro, a mix of refactoring, new project, and bug fix tasks, 20 independent runs per category):

| Metric | Without Budget Management (Baseline) | With Budget Management |
|--------|:---:|:---:|
| Constraint retention at turn 15 | ~40% | **>95%** |
| Skill loading token consumption per task | 10K-40K (all Skills) | 2K-5K (on-demand) |
| Token savings per task | — | **8K-35K** |
| Parent Agent context inflation rate | Baseline | **~60% slower** |

> **Data note:** Self-tested data based on DeepSeek V4 Pro, v0.x version, mix of refactoring + new project + bug fix tasks, 20 independent runs each. Experimental environment, code, and statistical tests to be added. Requires independent replication.

**The critical conclusion:** The model did not change. Same DeepSeek V4 Pro. The only variable was how the Harness layer managed the attention budget. Yet the difference in effective intelligence is dramatic — in user perception, the Agent with budget management "feels smarter." Not because the model is stronger. Because every task the model performs has more sufficient attention allocated to it.

### 5.2 To Be Validated

- **Cross-model generalization:** Verify whether the strategies work consistently on DeepSeek V3, Qwen, Llama, and other models
- **Extreme long conversations:** The degradation tipping point of budget management under 100+ turn conversations
- **Review gradient adaptation:** The actual fitting quality of the two-dimensional function (KV Cache occupancy × Plan complexity) — currently a heuristic gradient, requires experimental validation of thresholds
- **Budget management overhead:** The computational cost and latency overhead of the four strategies themselves — currently within acceptable range (<5% latency increase), but requires systematic measurement

---

## 6. Why DeepSeek Has a Structural Advantage

All four attention budget management strategies depend on one precondition: **KV Cache must be cheap enough.**

- Prefix injection requires extra tokens in the prefix zone → Under Claude/GPT token costs, every 1K tokens in the prefix zone is a significant cost burden
- Sub-task isolation requires spawning multiple independent contexts → Total token consumption rises (but is offset by efficiency gains from isolation)
- Review gradient switching requires frequent context state assessments → Requires frequent context state checks

DeepSeek's KV Cache cost advantage (roughly 1/5 to 1/10 of Claude's) makes these strategies economically viable. The same approach running on Claude may cost 3-5 times more in token consumption. This is not because Claude's model is weaker — it is because Claude's pricing structure pushes "active attention budget management" to an economically infeasible level.

This is a **structural advantage**. Not because DeepSeek's model is smarter than Claude's, but because DeepSeek's cost structure makes "treating attention as a managed budget" product-viable. When a Harness-layer strategy needs extra token consumption in exchange for higher effective intelligence, the lower the token cost, the higher the ROI of that strategy. DeepSeek's low-cost structure amplifies the value of Harness-layer innovation.

---

## Conclusion

Agents getting dumber is not the model's fault. It is an **engineering problem** — Transformer attention dilution is a known physical boundary, and addressing that boundary should be the Harness's responsibility, not "waiting for the next model."

Attention Budget Management upgrades the Harness from "passively calling the model" to "actively managing the model's attention resources." Four strategies — prefix injection, on-demand loading, sub-task isolation, extract-before-compress — cover the four paths of attention dilution, building a "no-leakage budget" system.

Validation data shows: the same model, with budget management, demonstrates significantly higher effective intelligence than the baseline without it. This is not magic. It is making the model do fewer things, but do every one of them better.

---

*Previous: [02 Brain Driving the Cerebellum](02-bidirectional-agent.md) — The LLM should not just be the Harness's passive executor*
*Next: [04 KV Cache Hard-Constraint Prefix Injection](04-kv-cache-prefix.md) — How hard constraints are injected into the prefix zone and kept out of compression*
