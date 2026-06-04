# Agent Immune System: Let the Harness Self-Audit and Self-Repair Prompt Decay

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, “validated” does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Point: I-13
> **LLM + Harness = Agent** · Part 1
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: none
> Next: [02 Brain Drives the Cerebellum](02-bidirectional-agent.md)

---

## Problem: Prompt Instructions Inevitably Decay

You write a System Prompt. Fifty rules: "Back up files before editing." "Don't touch config files." "Use Python 3.11, not 3.9." "Run tests after every change."

The Agent cheerfully says "Got it." Then you watch it forget, one rule at a time.

By round 15, out of 50 rules, maybe 20 are still being followed. The Agent isn't being malicious. Transformer soft attention physics guarantees that in long sequences, attention weights dilute across *all* tokens — including your System Prompt.

I verified this in OMO's source code. Its System Prompt lists 50+ scenario-handling instructions ("If it's a refactor task, read AGENTS.md first," "If it's a new project, confirm the tech stack first"…). But only 20 of these are actually implemented in code. The other 30 are held up entirely by the Prompt. And in large contexts, the Prompt can't hold.

---

## Industry Status: Two Dead Ends

Right now, everyone is walking one of two paths. Both are dead ends.

**Path 1: Write longer System Prompts.**

"Agent forgot rule A? I'll add a reminder not to forget rule A." This is Prompt inflation. More rules → lower attention weight per rule → faster forgetting. A downward spiral.

**Path 2: Wait for better models.**

"Next-gen models will have bigger context windows, stronger attention — they won't forget." This is pushing a Harness-layer problem onto the model team. But Transformer soft attention is bounded by O(n²) physics. Going from 128K to 1M tokens only delays the dilution. It doesn't eliminate it.

Neither path works. Because the fundamental problem isn't "the model isn't smart enough." It's that **you shouldn't be asking the model to follow rules through memory alone.**

---

## Solution: Immune System-Style Self-Repair

Biological immune systems don't work by "remembering every pathogen." They work by: recognize non-self → generate antibodies → auto-clear the same attack next time.

An Agent's constraint-compliance mechanism should work the same way. Not by having the model memorize 50 rules and self-check during every inference — but by having **an independent audit mechanism inspect whether the Prompt was followed after each execution.**

Three steps:

### Step 1: Self-Audit

After the Agent completes a task, an independent audit Agent is spawned. It doesn't read execution logs. It reads exactly two things:

1. The original Prompt instructions ("what you should do, what rules to follow")
2. The final output (code, documents, config changes, etc.)

The audit Agent compares line by line: what did the Prompt require? What actually appeared in the output?

### Step 2: Detect Omission → Generate Antibody (Skill Crystallization)

If the audit Agent finds a Prompt instruction was not followed — say the Prompt required "back up the original file before modifying code" but the Agent skipped it — the system automatically crystallizes that constraint into an executable Skill.

```markdown
# Skill: pre-edit-backup
# Crystallized from: Prompt instruction "back up before code changes" was forgotten

Before executing any write_file / patch / terminal that modifies code:
1. Check if target file exists
2. If it does, cp to .bak/ directory first
3. Confirm backup succeeded, then proceed with modification
```

### Step 3: Inject Skill into Execution Flow

The newly generated Skill is auto-registered into the system. Next time any Agent executes a similar task, this Skill loads before execution. The model doesn't need to "remember to do an extra backup." The system injects a non-skippable check step into the instruction flow.

---

## The Essence: Not "Stronger Memory" — "Less Need to Remember"

The core logic of this approach is not about making the Agent's "memory" stronger. It's about letting the system evolve from "pure Prompt-driven" to "Prompt + Skill co-driven."

- Prompt covers all scenarios (50+)
- Code only handles the 20 that are deterministically quantifiable
- The immune system gradually crystallizes the other 30 into Skills
- Every crystallization = lower token consumption + lower forgetting risk

This is self-evolution. The system accumulates "antibodies" through usage, rather than relying on an ever-longer, ever-harder-to-follow Prompt.

---

## Why Hermes Is Closest to This

Hermes already has the first half of this — **Skills self-evolution.**

When you complete a complex task on Hermes, it can propose "save what we just did as a Skill." Next time a similar scenario comes up, the Skill loads automatically. This is positive learning (success → crystallization).

But Hermes is missing the second half — **negative correction.**

Hermes Skills only trigger after "task success." They never trigger after "Prompt was forgotten." There's no self-audit loop — no independent post-execution review of whether the Prompt was actually followed.

This blind spot is exactly what the "Agent Immune System" fills. Positive learning + negative correction. Together, they form a complete self-evolution loop.

---

## Verification Path

- **Source audit**: OMO's System Prompt has 50+ rules. Code implements 20. Prompt instruction decay is real, quantifiable, and structural — not hypothetical.
- **Prototype design**: Self-audit logic and Skill crystallization format are designed.
- **Next step**: Run 100+ real-world tasks, measure Prompt forgetting rate + Skill auto-crystallization success rate.

---

## Link to Next Innovation

The Immune System answers: "When the Agent screws up, how does it fix itself?"

But there's a deeper question: **Can the Agent realize it needs help *before* it screws up?**

That leads to the next innovation — [Brain Drives the Cerebellum](02-bidirectional-agent.md): making the LLM not a passive executor inside the Harness, but an active participant that recognizes its own limitations and requests assistance from the Harness.
