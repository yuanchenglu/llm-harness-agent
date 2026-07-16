# Agent Immune System: Let the Harness Self-Audit and Self-Repair Prompt Decay

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation Index**: I-01
> **LLM + Harness = Agent** · Part 1
> **Series**: [LLM + Harness = Agent](../../README.md)
> **Next**: [02 Brain Actively Drives the Cerebellum](02-bidirectional-agent.md)

---

> **Abstract**: Large language models inevitably forget behavioral constraints in the System Prompt during long conversations. This is a physical boundary of the Transformer soft attention mechanism, not a model capability problem. This paper proposes an "immune system" style self-repair mechanism: after the Agent completes a task, an independent audit module checks whether the Prompt constraints were followed; when omissions are detected, the constraint is automatically crystallized into an executable Skill and injected into the execution flow. This approach realizes a self-evolution loop for Prompt + code co-driven systems. Hermes already handles positive learning (success → Skill), but the blind spot of negative correction (forgetting → self-audit → Skill) is currently unfilled by anyone.

---

## 1. Problem Definition

### 1.1 The Phenomenon

In long conversation scenarios, the Agent's compliance with behavioral constraints in the System Prompt decreases monotonically as the number of conversation rounds increases.

The typical pattern: a System Prompt with 50 behavioral rules may have fewer than 20 rules actually followed by the Agent after round 15. The omitted rules are not "chosen" to be ignored. The Agent genuinely believes it has followed every rule at each inference round, but a systematic gap exists between actual behavior and the rules.

### 1.2 Root Cause

The root cause is not model capability. It is the Transformer architecture's attention mechanism.

In the standard implementation, Transformer self-attention is O(n²) computation. Each token's attention weight must be distributed across all tokens. When sequence length grows from 2K to 128K, the attention weight allocated to any single rule in the System Prompt is diluted by roughly 64x.

> **Supplementary note (2026-07-04, source verified)**: DeepSeek V4 dramatically reduces effective complexity through CSA (Compressed Sparse Attention, 4-128x compression) + HCA (Heavily Compressed Attention) + MQA (1 KV head). Official data: 27% FLOPs + 10% KV cache of V3.2 at 1M context. But the mathematical nature of attention dilution remains unchanged. The softmax weight distribution is still diluted as sequence length grows.

**Why compression cannot solve this**: Context compression only reduces sequence length, but the compression algorithm cannot distinguish "this constraint must be preserved" from "this conversation can be discarded." After compression, constraint loss is random and unpredictable.

### 1.3 Formalization

Let the System Prompt contain n behavioral constraints C = {c₁, c₂, ..., cₙ}. After t rounds of conversation, the sequence length is L(t). The attention weight allocated to constraint cᵢ is αᵢ(t) ∝ 1/L(t). When L(t) → ∞, αᵢ(t) → 0. Constraint compliance rate is positively correlated with αᵢ(t).

Source verification: OMO v0.3's System Prompt defines 50+ scenario-handling instructions, but only 20 code paths are implemented in `plan-progress.ts` and `types.ts`. The other 30+ rely entirely on Prompt instructions with no corresponding runtime check mechanism.

> **Note**: This conclusion is based on a source audit of OMO v0.3. Specific file paths and version differences for v0.3 still need supplementary annotation.

---

## 2. Existing Approaches and Their Limitations

| Approach | Core Idea | Why It Fails |
|----------|-----------|--------------|
| **Prompt inflation** | Agent forgot rule A? Add "don't forget rule A" to the Prompt | More rules → lower αᵢ per rule → worse forgetting. A positive feedback loop that makes things worse |
| **More frequent repetition** | Repeat key constraints in the System Prompt every N rounds | Eats context window → accelerates L(t) growth → exhausts the window sooner |
| **Wait for next-gen models** | Bigger context windows + stronger attention | A 1M window only delays dilution from round 15 to round 50. The problem is unchanged, just delayed |
| **Context compression** | Compress conversation history to make room for constraints | The compression algorithm evaluates all information with uniform weight. Constraints and ordinary conversation are mixed together. What is lost after compression is unknowable |
| **Hermes Skill (positive learning)** | Save successful procedures as Skills after task success | Only triggers on task success. Forgetting-caused failures never trigger Skill generation |
| **CodeWhale Self-Improvement** | LLM detects code defects and fixes its own code | Does not change code. The root cause of constraint violation is not that the code is bad, but that the Prompt instructions were not executed |

**Common flaw**: Every approach tries to make the model "remember more." The correct direction is to make the system "reduce what the model needs to remember."

---

## 3. Solution Design

### 3.1 Core Mechanism: Self-Audit → Crystallize → Inject

The solution consists of three steps:

**Step One: Self-Audit**

After the Agent completes a task, the system spawns an independent audit Agent. The audit Agent receives exactly two inputs:
1. The list of behavioral constraints from the original Prompt
2. The final output (code changes, file modifications, command execution records)

The audit Agent does not read execution logs. Reading execution logs would re-introduce the context inflation problem. The audit granularity is a one-by-one match between "constraint" and "output," not a full-scale "constraint → execution trace" scan.

**Step Two: Crystallization**

When the audit Agent detects that a constraint was not followed, the system automatically generates a Skill. The Skill format is structured check steps. Not natural language hints, but executable check logic.

Example. If the audit finds the Agent skipped "back up before modifying code":

```markdown
# Skill: pre-edit-backup
# Crystallized from: Prompt constraint "back up original file before editing" was forgotten at round N
# Trigger condition: write_file / patch / terminal(cp/mv/rm)
# Check logic: Does the target file exist → Is there already a .bak → If not, intercept and require backup first
```

**Step Three: Injection**

The newly generated Skill is registered into the Skill system. When any subsequent Agent executes a similar task, this Skill is loaded before execution and injected into the execution flow as a non-skippable check step.

### 3.2 Key Design Decisions

**Why not directly modify core code?**

Core code (e.g., `plan-progress.ts`) can only cover known, quantifiable scenarios. About 20 of them. But in real usage, 50+ variant scenarios can emerge. The strength of the Prompt is coverage breadth (descriptive power). Its weakness is execution reliability (depends on model memory). Skill crystallization combines the "coverage breadth" of the Prompt with the "execution reliability" of code. Core code stays untouched, and the system's behavioral coverage expands progressively through injected Skills.

**Why call it an "immune system"?**

A biological immune system does not work by "remembering all pathogens." It works by "recognize non-self → generate antibodies → auto-clear on next encounter." This solution replicates that logic exactly:

| | Biological Immune System | This Solution |
|---|---|---|
| Recognition | Recognize foreign antigens | Audit Agent detects constraint violation |
| Generate antibodies | B cells produce specific antibodies | Automatically generate a targeted Skill |
| Memory | Memory B cells survive long-term | Skill persists, auto-loads next time |
| Self-tolerance | Does not attack self-cells | Does not modify core code |

### 3.3 Positive Learning vs. Negative Correction

Hermes's Skill mechanism is positive learning. It only learns from successful tasks. This solution is negative correction. It learns from failure/forgetting. The relationship is not substitution, but complement:

```
Positive learning (Hermes):  task success → extract procedure → crystallize as Skill
Negative correction (this):  constraint forgotten → audit detects → crystallize as Skill

Both share the same Skill storage and execution engine
The only difference is "what event triggers Skill generation"
```

---

## 4. Analysis

### 4.1 Why This Solution Addresses the Root Problem

The root problem is not "the model cannot remember." It is "the model should not be the one doing the remembering." This solution shifts the responsibility of "remembering constraints" from the model to the Harness. The model only handles reasoning and judgment. Constraint compliance is guaranteed by the Harness through the Skill injection mechanism.

Each audit + crystallization cycle migrates one constraint from "depends on the Prompt" to "depends on a Skill." A Skill does not consume attention weight. It is injected as a deterministic check step before execution, bypassing the model's soft attention allocation entirely. After migration, the compliance rate for that constraint shifts from probabilistic (~40% @ round 15) to deterministic (~100%).

### 4.2 Boundary Conditions

The following scenarios **cannot** be covered by this solution:

- **Implicit constraints**: Constraints that are not explicitly written in the Prompt but are implicitly expected by the user (e.g., "code style should be consistent"). The audit Agent can only check explicitly declared constraints.
- **Context-dependent constraints**: Constraints whose validity depends on situational judgment (e.g., "if it's an emergency fix, skip code review"). A crystallized Skill is a deterministic check and cannot make situational judgments.
- **First-time forgetting**: Crystallization can only be triggered after a constraint has been forgotten at least once. The loss caused by that first forgotten instance cannot be recovered by this solution.

### 4.3 Comparison with the Closest Approach

| Dimension | Hermes Skill | This Solution |
|-----------|:---:|:---:|
| Trigger event | Task success | Constraint forgotten |
| Learning direction | Positive | Negative |
| Generated content | Steps of a successful procedure | Check logic for a forgotten constraint |
| Execution method | Load Skill instructions before task | Inject check step before execution |
| Modifies core code | No | No |

---

## 5. Verification Path

### 5.1 Verified

- **Problem existence**: OMO source audit confirms Prompt instructions cover 50+ scenarios, code implements only 20. Prompt decay is a structural defect, not an occasional bug.

### 5.2 To Be Verified

- **Audit accuracy**: Constraint compliance check accuracy (precision and recall) of the audit Agent across 100+ tasks
- **Crystallization efficiency**: Average latency from detecting forgetting to Skill generation
- **Token savings**: Token consumption comparison before and after Skill crystallization. After a constraint migrates from "depends on Prompt" to "depends on Skill," the attention budget saved per round
- **Combined positive + negative effect**: Constraint compliance rate under joint operation of positive learning (success → Skill) + negative correction (forgetting → Skill), versus positive learning alone

---

## 6. Relationship with Hermes

Hermes already has the first half of this solution. **Positive learning through Skill self-evolution.** After an Agent completes a complex task, it can propose saving the procedure as a Skill.

What is missing is the second half. **The trigger mechanism for negative correction.** Currently, Hermes Skills only trigger on task success. They never trigger when a constraint is forgotten. Filling this blind spot requires an independent "audit → crystallize" loop. This can be implemented as a Skill plugin for Hermes without modifying the core architecture.

---

## Conclusion

The reliability of Agent constraint compliance does not depend on how well the Prompt is written. It depends on whether the Harness layer has a "detect forgetting → self-repair" loop. Positive learning plus negative correction. Together, they form a complete self-evolving system.

---

*Next: [02 Brain Actively Drives the Cerebellum](02-bidirectional-agent.md) — The LLM should not be just a passive executor inside the Harness*
