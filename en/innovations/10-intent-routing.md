# Intent-to-Strategy Switching: From Observed Routing to a 7+1 Design Proposal

> **Evidence level: A1 + B**  
> - **A1**: fixed-source audits confirm that OMO uses CLEAR/UNCLEAR routing and Trivial/Standard/Architecture tiers; Hermes also contains scenario-oriented routing mechanisms.  
> - **B**: the `refactor / new / medium / collaboration / architecture / research / simple + spec-driven` system in this article is an extended design proposal, not a complete feature already implemented by OMO or Hermes.  
> Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> **Innovation index**: I-10  
> **Series**: [LLM + Harness = Agent](../../README_en.md)  
> **Previous**: [09 Skills Self-Evolution](09-skills-self-evolution.md)  
> **Next**: [11 Checkpoint-Driven Multi-Round Review](11-checkpoint-review.md)

---

## Abstract

Different tasks require different execution strategies:

- a simple edit should not trigger ten rounds of requirement interviews;
- a high-risk refactor must not skip contracts and regression analysis;
- a research task cannot use “code was changed” as its only completion criterion;
- collaboration requires interfaces, isolation, and merge strategy;
- architecture decisions require tradeoffs, Evidence, and decision records.

Source observations show that some Agents already use coarse classification and conditional routing. The 7+1 system here is a further product design:

```text
Task Classification
→ Strategy Bundle
→ Runtime Observation
→ Upgrade / Downgrade
→ Evidence and Feedback
```

The goal is not elegant category names. It is selecting appropriate controls for the current task:

```text
clarification depth
Plan granularity
tool scope
Memory / Skill scope
review mode
model and budget
human approval
completion evidence
```

---

## 1. Boundary Between Source Facts and Design Proposal

### 1.1 Confirmed OMO mechanisms

A fixed-source audit confirms that OMO planning includes:

```text
CLEAR / UNCLEAR
+ Trivial / Standard / Architecture
```

These are mainly used to decide:

- whether further clarification is required;
- task complexity;
- planning depth.

This must not be described as a complete 7+1 intent system already implemented by OMO.

### 1.2 Confirmed Hermes mechanisms

Hermes is relevant for scenario routing, tool registration, Memory, Skills, and long-running operation. Specific categories, trigger conditions, and strategy bindings must be described from a fixed source version. Product concepts must not be expanded into unsupported implementation claims.

### 1.3 Proposal in this article

The 7+1 system explores whether explainable categories can bind useful default strategies quickly, with Spec-Driven mode covering unknown tasks.

It still requires validation of:

- classification accuracy;
- whether the strategy improves actual task outcomes;
- whether users consider clarification and review appropriately sized;
- the cost of misclassification;
- transfer across models and projects.

---

## 2. Why Strategy Routing Is Needed

A fixed workflow is commonly mismatched in two directions.

### 2.1 Too light

Task: refactor a legacy payment module.

Immediate execution may omit:

- backward compatibility;
- module contracts;
- shared state;
- data migration;
- rollback;
- regression tests.

### 2.2 Too heavy

Task: correct one invalid command in a README.

If the system forces:

- a deep interview;
- multi-Agent planning;
- architecture review;
- a complete release process;

coordination cost exceeds task value.

### 2.3 More accurate question

Not:

```text
Which label does this task belong to?
```

But:

```text
Which execution controls are required to complete this task safely, correctly, and economically?
```

---

## 3. Multi-Axis Task Representation

A fixed single label loses information. First produce a multi-axis profile:

```yaml
task_profile:
  kind: refactor
  ambiguity: medium
  change_scope: multi_module
  risk: R2
  reversibility: reversible_with_tests
  novelty: high
  collaboration: single_agent
  deliverable: code_and_report
  evidence_required:
    - diff
    - unit_tests
    - integration_tests
    - compatibility_review
```

### 3.1 Task kind

Candidates:

```text
simple
bugfix
refactor
new_feature
new_project
research
architecture
operations
collaboration
```

Categories are extensible. A task does not have to belong to exactly one class.

### 3.2 Ambiguity

```text
clear
partially_clear
unclear
conflicting
```

### 3.3 Risk and reversibility

Use the I-07 risk model:

```text
R0–R4
fully_reversible → irreversible
```

### 3.4 Change scope

```text
no_change
single_file
multi_file
multi_module
multi_service
external_system
```

### 3.5 Deliverable

```text
answer
document
code
diff
configuration
release artifact
external side effect
```

---

## 4. Seven Default Categories + One

These categories are strategy templates, not the only natural classification.

### C1: Simple

Applicable to low-risk, small-scope, clear tasks.

Default strategy:

- minimal clarification;
- one Step or no explicit Plan;
- M1 automated verification;
- low default budget;
- reversible result.

### C2: Medium Change

Applicable to functional changes across roughly 3–10 files in an existing project.

Default strategy:

- lightweight clarification of scope and acceptance;
- file/component-level Plan;
- Diff + Tests + Light Review;
- writes require a ChangeSet.

### C3: Refactor

Applicable when structure changes but external behavior should remain stable.

Default strategy:

- read existing architecture and call chains;
- state invariant contracts;
- fine-grained Plan;
- regression, compatibility, and performance evidence;
- independent Review for high-impact sections.

### C4: New

Applicable to a new project or module.

Default strategy:

- confirm core user value and non-goals;
- avoid injecting every best practice into the MVP;
- milestone Plan;
- prioritize the smallest runnable closed loop.

### C5: Architecture

Applicable to cross-module, long-lived, hard-to-reverse decisions.

Default strategy:

- explicit constraints and non-functional requirements;
- alternatives and tradeoffs;
- ADR;
- multi-dimensional Review;
- do not treat architecture discussion as implementation completion.

### C6: Research

Applicable when uncertainty is high and the deliverable is knowledge or recommendation.

Default strategy:

- define the research question;
- define source priority;
- separate facts from inference;
- record missing evidence;
- allow iterative planning;
- use evidence coverage, not code volume, as the completion standard.

### C7: Collaboration

Applicable to multi-Agent or human-Agent collaboration.

Default strategy:

- define roles, inputs, outputs, and Loop Authority;
- isolate Workspaces;
- establish interface contracts;
- define merge and conflict strategy;
- return Evidence from subtasks.

### +1: Spec-Driven

Applicable when:

- classification confidence is low;
- categories are mixed;
- risk is high;
- the user already has a structured Spec;
- default templates cannot express the task adequately.

Generate the Strategy Bundle directly from Spec constraints instead of forcing one category.

---

## 5. Strategy Bundle

```yaml
strategy:
  clarification:
    mode: targeted
    max_questions: 3
  planning:
    granularity: component
    dependency_graph: true
  memory:
    mode: scoped_project
  skills:
    disclosure: index_then_on_demand
  tools:
    profile: code_safe_write
  model:
    default: flash
    escalation:
      - on_high_risk_checkpoint
      - on_repeated_verifier_failure
  review:
    mode: M2
  approval:
    required_for:
      - file_write
      - external_side_effect
  evidence:
    required:
      - diff
      - tests
      - rollback_point
```

Strategy fields must be executable by the Runtime rather than existing only as natural-language advice.

---

## 6. Routing Flow

```text
Parse Task
→ Extract Task Profile
→ Generate Candidate Categories
→ Estimate Confidence and Risk
→ Select Strategy Bundle
→ Show Material Assumptions
→ Execute
→ Observe Runtime Signals
→ Upgrade / Downgrade Strategy
→ Record Outcome
```

### 6.1 Routing output

```yaml
route_id: route-123
category: refactor
alternatives:
  - medium_change
confidence: 0.72
risk: R2
reasons:
  - touches 4 modules
  - user requires the external API to remain unchanged
assumptions:
  - current test coverage is a valid behavioral baseline
strategy_ref: strategy-refactor-v2
```

### 6.2 Material Assumptions

High-impact assumptions should be shown to the user or entered into Evidence, such as:

- “do not change the external API”;
- “macOS only”;
- “do not migrate historical data”;
- “do not add OAuth.”

---

## 7. Runtime Strategy Upgrades

Initial classification may be wrong. The Runtime should upgrade from observed facts:

```text
Simple
→ discovers cross-module dependencies
→ Medium

Medium
→ discovers data migration and permission changes
→ Architecture / R3 Review

Research
→ user approves implementation
→ New or Medium Change
```

Downgrades are also valid:

```text
Architecture
→ constraints are clear and a mature template exists
→ Medium Change
```

Every switch records its reason, cost, and Evidence requiring revalidation.

---

## 8. Asymmetric Error Cost

| Error | Main consequence | Default handling |
| --- | --- | --- |
| Simple → Refactor | Too many questions and reviews | Acceptable but control UX cost |
| Refactor → Simple | Contracts and regression omitted | High risk; use conservative threshold |
| Research → New | Implementation begins before research | Block writes and require a Spec |
| Medium → Architecture | Over-design | Allow user downgrade |
| External Side Effect → Simple | Executes without approval | Runtime risk classification must catch it |

Risk classification and permission systems cannot depend entirely on intent routing.

---

## 9. Unknown Tasks and Open-Set Handling

The classifier must support:

```text
unknown
mixed
needs_spec
needs_user_decision
```

It must not force a known label merely to increase coverage.

Spec-Driven mode provides:

- executable constraints for unknown tasks;
- collection of frequent new patterns;
- evidence for deciding later whether a new category is needed.

---

## 10. Evaluation

### 10.1 Classification

```text
confusion matrix
open-set rejection accuracy
confidence calibration
asymmetric cost-weighted error
```

### 10.2 Strategy effect

Compare:

```text
fixed generic strategy
user-selected mode
automatic router
spec-driven strategy
```

Metrics:

```text
first-pass success
clarification turns
human correction
escaped defect
review cost
latency
cost per successful task
```

### 10.3 User experience

- too many or too few questions;
- execution too slow or too fast;
- whether routing reasons are understandable;
- whether users can override;
- whether overrides improve outcomes.

### 10.4 Dataset discipline

Include:

- multiple projects;
- multiple task types;
- ambiguous and mixed tasks;
- high-risk negative samples;
- held-out projects;
- different models.

Do not generate the entire test set directly from the category definitions; otherwise the classifier merely repeats its own templates.

---

## 11. Boundaries and Risks

- too many categories increase maintenance cost;
- the router may be confidently wrong;
- the user objective may change during execution;
- project-specific strategy may override global defaults;
- routing and model selection may reduce Prefix Cache reuse;
- strategy escalation increases cost;
- automatic classification cannot replace Runtime safety boundaries;
- a Spec can also be incomplete or incorrect.

The system needs user override, Runtime fallback, versioned strategies, and failure replay.

---

## 12. Conclusion

The 7+1 framework is not a “complete disclosure” of an existing OMO implementation. It is an extended design based on observed routing mechanisms.

Reliable intent routing should:

1. first extract a multi-axis Task Profile;
2. bind categories to executable Strategy Bundles;
3. output confidence, reasons, and material assumptions;
4. support Unknown and Spec-Driven modes;
5. upgrade or downgrade dynamically from Runtime facts;
6. evaluate asymmetric error cost;
7. keep permissions, Policy, and high-risk approval as independent safeguards.

Classification is only a means. The actual objective is to use enough—but not excessive—clarification, planning, execution, and review for the task at hand.
