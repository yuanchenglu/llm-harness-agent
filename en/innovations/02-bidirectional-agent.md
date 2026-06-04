# The Brain Driving the Cerebellum: Letting the LLM Stop Being Harness's Passive Executor

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, “validated” does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Index: I-09
> **LLM + Harness = Agent** · Part 2
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [01 Agent Immune System](01-agent-immune-system.md)
> Next: [03 Attention Budget Management](03-attention-budget.md)

---

## The Problem: Every Agent Is One-Way

Open the source code of any agent product. You will see the same architecture, every single time:

```
User input → Harness receives → Decomposes task → Calls LLM → LLM returns tool_call → Harness executes tool → Feeds result back to LLM → Loop
```

The LLM is passive from start to finish. It only "thinks" when it gets called. It can perceive that "the previous tool call failed," but it won't proactively say: "Wait. Before the next step, I need information X. But I don't have X. Go get it for me."

Picture someone sitting in the passenger seat. They can see the road. They can offer advice. But they don't have the steering wheel. Braking, turning—everything waits for the driver (Harness) to act first, and only then can they react.

The consequence of this one-way architecture: **The LLM has zero voice about its own capability boundaries.** It knows it doesn't understand a particular domain, but it won't proactively say "This task exceeds my abilities—swap in a specialized model." It knows it hasn't seen a specific file, but it won't proactively say "Give me that file, otherwise my judgment is based on guesswork."

---

## Industry Reality: Nobody Is Doing This

It's not that nobody has noticed the problem. It's that nobody is working on it.

The reason is simple: every current agent evaluation metric measures "task completion rate," "code generation accuracy," "token consumption." Not a single metric measures "the frequency and quality of LLM-initiated assistance requests."

No metric → no optimization direction. No optimization direction → Harness design forever assumes the LLM is a passive execution engine.

But Anthropic is likely already exploring this frontier. The "Joint RL" they're running on Opus + Claude Code—not optimizing the model and Harness separately, but using a single feedback signal to improve both simultaneously—fundamentally requires bidirectional information flow between LLM and Harness. If the LLM is always one-way passive, Joint RL can't work.

---

## The Solution: Knowledge Is the Beginning of Action, Action Is the Completion of Knowledge

Wang Yangming's phrase describes exactly what agent architecture should look like.

**Knowledge is the beginning of action**: During inference, the LLM shouldn't only output "what to do next." It should first output "what is my cognitive state right now"—what do I understand? What am I uncertain about? What information am I missing?

**Action is the completion of knowledge**: When Harness receives the LLM's cognitive declaration, it doesn't "decide the next step for the LLM." It "helps the LLM get what it needs." LLM says "I need to read config.yaml before I can make this judgment"—Harness goes and reads it. LLM says "This task needs a code-review-specialized model, swap one in for me"—Harness performs the swap.

Concretely, bidirectional flow requires adding several new primitives to the Agent Loop:

```
Traditional Agent Loop:
  Harness → LLM: "Here's the task, here's the context, now execute"

Bidirectional Agent Loop:
  Harness → LLM: "Here's the task, here's the context"
  LLM → Harness: "I need additional information: [specific request]"
  Harness → LLM: "Here's what you asked for"
  LLM → Harness: "This subtask exceeds my capability, recommend using [specialized model]"
  Harness → LLM: "Model switched, continue"
```

The critical difference: Harness doesn't predefine "when the LLM should get what." **The LLM proactively declares its needs based on its own cognitive state.**

---

## Why This Matters

This changes three fundamental things.

### 1. Planning Becomes Dynamic, Not Predefined

Traditional agent Planning is done by Harness before calling the LLM—decompose the task into steps, LLM executes step by step. If the Planning is wrong, the LLM has no ability to correct it—because the LLM's input is already the pre-decomposed steps.

Bidirectional flow makes Planning dynamic. When the LLM reaches step 3, it can say: "The assumption behind step 4 is wrong, because I discovered an unexpected outcome in step 2's output. Re-plan steps 4 through 7."

### 2. The Training Feedback Loop Goes from Slow to Fast

- Slow loop: User feedback → Product team analysis → Researcher adjusts training data → Retrain → Deploy (weeks to months)
- Fast loop: LLM real-time perception → Proactive need declaration → Harness instant response → LLM continues reasoning (milliseconds)

This gap isn't a matter of degree. It's a paradigm gap.

### 3. True Model + Harness Co-evolution

If the LLM is always one-way passive, then the "+" in "Model + Harness = Agent" is just concatenation, not fusion. Bidirectional flow turns "+" into "⇄"—the model tells Harness what it needs, Harness tells the model what it can do. The two co-evolve through interaction.

---

## Relationship to Hermes

Hermes's `delegate_task` mechanism is already moving in this direction—the main Agent can dispatch subtasks to specialized sub-agents. But `delegate_task` is still triggered by the main Agent (the Harness layer), not requested by the LLM.

An ideal bidirectional flow implementation would let the LLM actively call `delegate_task` during reasoning—not "Harness thinks this should be delegated," but "the LLM thinks this subtask should go to a more specialized Agent."

---

## The Anthropic Frontier

If Anthropic's Joint RL on Opus + Claude Code is real, then bidirectional flow is very likely already implemented inside Anthropic. Joint RL requires the model and the harness to optimize against the same signal—which means the model must be able to express what it needs from the harness, and the harness must be able to respond. That is bidirectional flow by definition.

When this becomes public, it will force every agent platform to reconsider their architecture. The ones still running one-way loops will look like they're missing half the equation.

---

## Verification Path

- **Concept validation**: Bidirectional Agent Loop prototype design is complete.
- **Obstacle**: No current agent platform supports LLM-initiated Harness calls. Existing APIs only support the Harness → LLM → tool_call → Harness one-way chain. Implementation requires modifying the Agent Loop's foundational design.
- **Anthropic frontier**: If Joint RL on Opus + Claude Code is real, bidirectional flow has likely already been implemented internally at Anthropic.

---

## Relationship to the Previous Innovation

The [Immune System](01-agent-immune-system.md) solves "when the Agent screws up, how does it fix itself"—this is **post-error correction**.

The Brain Driving the Cerebellum solves "how does the Agent realize it needs help before it screws up"—this is **pre-error prevention**.

Together, they cover the two core dimensions of Agent reliability: when it makes a mistake, it can repair. When it can't see clearly, it can ask.
