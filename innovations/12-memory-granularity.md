# Memory Granularity Control: Stronger Isn't Always Better

> **Innovation Point**: New (Extracted from Conversation)
> **LLM + Harness = Agent** · Part 12
> **Series**: [LLM + Harness = Agent](../README.md)
> **Previous**: [11 Checkpoint Multi-Round Review](11-checkpoint-review.md)
> **Next**: TBD

---

> **Abstract**: Memory is treated as an absolute good in the Agent field — the stronger the Memory, the smarter the Agent. This article argues that this assumption is wrong. Strong Memory locks the Agent into historical preferences and becomes poison for divergent tasks (creativity, exploration, breakthrough thinking). Weak Memory gives the Agent a blank slate each time and becomes a disaster for convergent tasks (engineering coordination, process execution). I ran an Agent matrix experiment across 5 machines for over a year and arrived at a counterintuitive conclusion: Memory strength should match task type — divergent tasks use weak Memory (OpenClaw), convergent tasks use strong Memory (Hermes), and hybrid tasks use medium Memory. Memory is not a binary switch; it is a continuously adjustable variable on a spectrum.

---

## 1. Problem Definition

### 1.1 The Phenomenon

This is the wall I kept running into over a year of Agent use:

**Scenario A**: I asked Hermes (strong Memory) to help me conceptualize an innovative article. Hermes opened Memory and saw my past preferences — "likes systematic frameworks," "skilled at analogies," "prefers first-principles reasoning." So every article it produced had the same flavor: framework → analogy → first principles. Well-structured, logically rigorous. But by the time you read the third one, you already know exactly how the fourth one will read.

**Scenario B**: Same task, switched to OpenClaw (weak Memory). No historical preferences to reference, no database of "what style does Mr. Yuan like." It faces the prompt as a blank slate. The output is completely unpredictable — sometimes it goes wildly off-track, sometimes it produces an angle I'd never considered. That "wild" angle later became one of my most important innovations.

**Scenario C**: Reverse the situation — ask OpenClaw (weak Memory) to coordinate a cross-3-machine Agent matrix task: "Remember who reviewed that PR last week?" "What was the root cause of that bug?" OpenClaw knows nothing. I have to explain everything from scratch every time. Strong-Memory Hermes utterly dominates OpenClaw in this scenario.

**Same model** (DeepSeek V4), same prompt, same context window. The only variable is Memory strength. The results diverge massively — but whether that's good or bad depends on the task type.

### 1.2 Root Cause

The root cause isn't in Memory implementation quality — it's in Memory's cognitive assumptions.

The entire Agent industry holds an unexamined premise about Memory: **More Memory is always better. Remember user preferences → reduce repetitive communication → Agent becomes more efficient.** This logic holds for convergent tasks (repetitive execution, process coordination, information retrieval). But for divergent tasks (creative generation, solution exploration, paradigm breakthrough), this logic is reversed.

The essence of strong Memory is **the accumulation of historical constraints**. Every time the Agent reads Memory, it pulls its behavior toward the gravitational center defined by past preferences. The more conversation rounds, the stronger the gravitational pull, the more the output resembles "the past self." This is the **Memory Lock-in Effect**: the Agent isn't getting smarter — it's being trapped by its own history.

The essence of weak Memory is **cognitive reset**. The Agent faces each task without historical baggage, forced to reconstruct understanding from the current prompt alone. This "start from zero" cost is waste on convergent tasks but an asset on divergent tasks — because without historical gravity, it can land in entirely different solution spaces.

This isn't a bug in the Memory module — it's an inherent property of Memory itself. Remembering the past and breaking free from the past are two sides of the same coin.

### 1.3 Formalization

Model the Agent's behavior B(t) at conversation round t as:

**B(t) = f( P(t), M(t), C(t) )**

Where P(t) is the current prompt, M(t) is injected memory, and C(t) is the context window.

In strong Memory mode: M(t) = {historical preferences, historical decisions, successful patterns, user style profile}, and |M(t)| grows monotonically with t.

As |M(t)| → ∞, the entropy of f's output distribution D(t), H(D(t)) → 0. The Agent's output becomes increasingly deterministic — always landing in the same solution space as before.

In weak Memory mode: M(t) ≈ ∅ or contains only minimal context. The entropy H(D(t)) stays at a high level — the Agent explores randomly across a larger solution space.

**Core contradiction**: Convergent tasks require H(D(t)) → 0 (deterministically execute known processes); divergent tasks require H(D(t)) to be sufficiently large (explore unknown solutions in the solution space). Memory strength directly controls this entropy — but when you only have one Memory mode, you can only optimize one end and must sacrifice the other.

---

## 2. Existing Approaches and Their Limitations

| Approach | Core Idea | Why It Fails |
|----------|-----------|--------------|
| **Full Memory (e.g., Hermes)** | Persist all preferences, decisions, and experience across sessions | Memory Lock-in Effect. On creative tasks, the Agent becomes increasingly "like itself," producing homogenized output |
| **Zero Memory (e.g., OpenClaw)** | Blank slate per session, no persistent state | Start from zero every time. On engineering coordination tasks, wastes massive tokens rebuilding context, and cannot accumulate experience |
| **Memory Toggle (manual switch)** | Give the user a Memory on/off button | Granularity is too coarse. The user has to remember "I should turn it off now" and "I should turn it on now" — the switch itself becomes a cognitive burden. And there's no intermediate state between on and off |
| **Auto-Summarization Memory** | Automatically compress conversation history into summarized Memory | The compression algorithm cannot distinguish "this preference should be retained" from "this preference should be discarded." After summarization, Memory strength is uncontrollable — is it strong or weak? |
| **RAG Retrieval Memory** | Retrieve relevant memories by query rather than injecting all | Solves the token efficiency problem, but not the Memory Lock-in Effect. Retrieved relevant memories still pull the Agent toward history |

**Common flaw**: All approaches treat Memory as a **binary variable** — either you have it or you don't. The right direction is to treat Memory as a **continuous spectrum** — strength can be adjusted between strong/medium/weak based on task type. It's not "whether to have Memory" — it's "how strong should Memory be."

---

## 3. Solution Design

### 3.1 Core Principle: Memory Strength = f(Task Type)

Memory isn't "the more the better" — it's "the better matched, the better." The key to matching is **the task's position on the convergence–divergence spectrum**.

```
Task Spectrum:

Convergent ←────────────────────────────────────→ Divergent
   │                                                    │
   Engineering process coordination    Hybrid tasks     Creative ideation
   Code review & verification       Solution design     Breakthrough thinking
   Bug tracking & traceback        Tech selection      Writing inspiration
   Scheduled task execution        Product strategy    Paradigm critique
   │                                                    │
   ↓                                                    ↓
Strong Memory              Medium Memory           Weak Memory
(Hermes)                  (Hermes+limits)         (OpenClaw)
```

Three Memory granularity zones:

**Strong Memory Zone**: Full historical preferences + decision records + successful patterns + user style profile, all injected. Applicable scenarios: engineering process coordination, code review, bug tracking, scheduled tasks, cross-session context maintenance. Goal: minimize repetitive communication, maximize execution determinism.

**Medium Memory Zone (Mixed)**: Only inject structured metadata (preference labels, tech stack constraints, core decision summaries), without injecting historical conversation transcripts or style preferences. Applicable scenarios: solution design review, technology selection analysis, product strategy discussion. Goal: maintain domain constraints without locking in thinking patterns.

**Weak Memory Zone**: Only inject minimal context (current task definition + global constraints), without injecting any historical preferences. Applicable scenarios: creative ideation, breakthrough thinking, writing inspiration, paradigm critique. Goal: maximize cognitive reset, encourage solution space exploration.

### 3.2 Key Design: Memory Spectrum, Not Memory Switch

The problem with binary Memory is: you only have two gears — full throttle and neutral. What you actually need is a continuously variable transmission.

This solution introduces a continuous **Memory strength parameter λ ∈ [0, 1]**:

- λ = 1.0: Full strong Memory (Hermes default mode)
- λ = 0.5: Medium Memory (structured metadata, excluding style preferences and historical transcripts)
- λ = 0.0: Weak Memory (task definition + global constraints only)

The actual injected memory M_injected = filter(M_full, λ), where the filter strategy is:

| λ Range | Injected Memory Layers | Filtered-Out Content |
|---------|----------------------|---------------------|
| 0.8–1.0 | Full: preferences + decisions + style + conversation summaries | None |
| 0.4–0.7 | Medium: preference labels + tech constraints + core decisions | Style preferences, historical conversation transcripts, successful pattern templates |
| 0.0–0.3 | Minimal: task definition + global constraints | All historical preferences, decision records, user style |

λ is not a parameter the user manually adjusts — the user doesn't need to know what λ is. λ is automatically determined by a **task classifier**: when the Agent receives a task, it first classifies the task on the convergence–divergence axis, then automatically matches the corresponding λ range.

This is what "granularity control" means: Memory strength is not a fixed system parameter — it is a variable that dynamically adjusts with the task.

### 3.3 My Production Configuration: Dual-Agent Division of Labor

This is the optimal division of labor I arrived at after over a year of running experiments:

```
                    ┌─────────────────────┐
                    │     Hermes (CEO)     │
                    │     λ ∈ [0.5, 1.0]  │
                    │                     │
                    │  • Task reception    │
                    │    & dispatch        │
                    │  • Cross-Agent       │
                    │    coordination      │
                    │  • Engineering       │
                    │    process mgmt      │
                    │  • Solution design   │
                    │    review            │
                    │  • Memory hub        │
                    └─────────┬───────────┘
                              │ Delegate divergent tasks
                              ↓
                    ┌─────────────────────┐
                    │   OpenClaw (CMO)     │
                    │     λ ∈ [0.0, 0.3]  │
                    │                     │
                    │  • Creative ideation │
                    │  • Marketing copy    │
                    │  • Breakthrough      │
                    │    thinking          │
                    │  • Writing           │
                    │    inspiration       │
                    │  • Unencumbered      │
                    │    exploration       │
                    └─────────────────────┘
```

It's not "Hermes is better than OpenClaw" or the reverse — it's that **they handle tasks of different Memory strengths**. Hermes does what requires historical constraints; OpenClaw does what requires cognitive reset. When the two Agents collaborate, Hermes is responsible for remembering context and history, and OpenClaw is responsible for generating new things on a clean canvas.

---

## 4. Analysis

### 4.1 Divergent Tasks vs. Convergent Tasks: Memory as a Creativity Valve

The theoretical root of this distinction lies in cognitive science's **Exploration-Exploitation tradeoff**:

- **Exploitation**: Leverage known optimal solutions. Corresponds to convergent tasks. Requires strong Memory — remember what worked in the past and reuse it directly.
- **Exploration**: Try unknown solution spaces. Corresponds to divergent tasks. Requires weak Memory — don't be boxed in by what worked before; try new directions.

Agent Memory, in this framework, is the weight on exploitation. The higher λ is, the more the Agent tends to reuse historical successful patterns; the lower λ is, the more the Agent tends to re-explore from the current prompt.

A concrete example: ask an Agent to design an API naming scheme.

- λ = 1.0 (strong Memory): The Agent sees your past preference for RESTful style + verb-prefix naming. It produces a standard `createUser` / `getUserById` / `updateUser`. The solution is predictable, maintainable, error-free — but also "just fine."
- λ = 0.0 (weak Memory): The Agent doesn't know your naming preferences. It might produce an OOP-style `user.create()` / `user.find()`, or an action-based `POST /users` scheme, or capability-based naming that completely escapes CRUD. Might go off-track — but might also stumble onto a better approach.

Key insight: **Creativity is not a function of model capability — it is a function of Memory strength.** The same model, with different λ, produces radically different levels of creativity. Not because the model got smarter — but because historical gravity was released.

### 4.2 Boundary Conditions: When Weak Memory Becomes Harmful

Weak Memory is not a panacea. The following scenarios produce negative effects with weak Memory:

- **Repetitive collaborative tasks**: Cross-session collaborative development, continuous integration debugging, long-term project maintenance. Weak Memory means re-explaining every time — "what's this project's tech stack," "what was the conclusion of the last discussion" — pure waste of tokens and time.
- **Safety/compliance constraints cannot be lost**: Certain global constraints (e.g., "never commit code containing API keys," "all SQL queries must be parameterized") must not be forgotten regardless of task type. These constraints should not be affected by λ — they should be anchored in the System Prompt's hard constraint prefix, decoupled from the Memory system.
- **Personal preferences that are hard requirements**: If a user's preference is not a "style inclination" but a "functional requirement" (e.g., "I am colorblind, all charts must use textures instead of color to differentiate"), this is not a preference but a constraint. It should enter the global constraint layer and not be filtered by λ.
- **Weak Memory's randomness is uncontrollable**: At λ = 0, the Agent's behavioral variance is very high — it might produce a brilliant solution, or a completely useless result. In scenarios requiring stable output (such as production environment deployment scripts), this variance is unacceptable.

**Core principle**: λ only controls the "preference and style" layer, not the "safety and constraint" layer. The constraint layer's Memory is always at λ = 1.0.

### 4.3 Comparison with Hermes-Only and OpenClaw-Only Approaches

| Dimension | Hermes-only | OpenClaw-only | This Solution (Granularity Control) |
|-----------|:---:|:---:|:---:|
| Memory Model | λ ≡ 1.0 (full persistence) | λ ≡ 0.0 (zero persistence) | λ ∈ [0,1] (dynamic adjustment) |
| Convergent Task Performance | ★★★★★ | ★★☆☆☆ | ★★★★★ |
| Divergent Task Performance | ★★☆☆☆ | ★★★★☆ | ★★★★★ |
| Hybrid Task Performance | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| Memory Lock-in Effect | Severe | None | Avoided on demand |
| Repetitive Communication Cost | Low | High | Controlled on demand |
| User Cognitive Burden | Low (fully automatic) | Medium (must remember zero context) | Low (automatic task classification) |
| Creativity Ceiling | Low (locked by history) | High (random exploration) | Highest (λ matches task) |

The key point: Hermes-only is strongest on convergent tasks and weakest on divergent tasks. OpenClaw-only is the reverse. **Granularity control is not about taking an average — it's about giving each task the most appropriate Memory strength.** The composite score exceeds any single approach.

---

## 5. Validation

### 5.1 My 1-Year+ Production Validation

This is not theoretical deduction — it's the result of running an Agent matrix across 5 machines in production.

**Experimental Design**:

- **Time span**: Early 2025 to present, approximately 18 months
- **Agent configuration**: Hermes (strong Memory, λ ≈ 1.0) × 3 machines + OpenClaw (weak Memory, λ ≈ 0.0) × 1 machine + other Agents × 1 machine
- **Task distribution**: Convergent tasks ~60% (code development, process coordination, bug tracking, scheduled inspections), Divergent tasks ~40% (article writing, solution ideation, technology critique, creative exploration)
- **Unified model**: All based on DeepSeek V3/V4

**Core findings**:

1. **On divergent tasks, OpenClaw (weak Memory) produced 2–3× more innovative angles than Hermes (strong Memory).** Quantitative metric: "Novel perspective count" per task (i.e., the number of non-templated arguments/solutions in the output that exceeded my expectations). Hermes averaged 1–2, OpenClaw averaged 3–6. However, OpenClaw's "off-track rate" (probability of producing completely useless output) was approximately 30%.

2. **On convergent tasks, Hermes's context transfer efficiency was over 5× that of OpenClaw.** Quantitative metric: Success rate of "correctly executing the next step without manual re-explanation." Hermes ~90%, OpenClaw ~40%. Because OpenClaw lost track every time of "where did we leave off" and "what was the root cause of that bug."

3. **The key turning point**: When I began deliberately using Hermes for convergence and OpenClaw for divergence — i.e., manually implementing Memory granularity control — the composite output quality (convergent task success rate × divergent task innovativeness) was clearly superior to using all Hermes or all OpenClaw.

4. **An unexpected finding**: Medium Memory (λ ≈ 0.5) performed best on "solution design review" type tasks. These tasks require both remembering tech stack constraints (strong Memory side) and breaking free from "this is how we did it last time" (weak Memory side). λ = 0.5 happened to balance both.

### 5.2 To Be Validated

- **Accuracy of the λ auto task classifier**: Can it accurately identify convergence–divergence attributes across 100 mixed tasks and match the appropriate λ? The cost of misclassification (convergent task assigned λ = 0) is wasted tokens and time; the cost of misclassification (divergent task assigned λ = 1) is lost innovation — the latter is harder to detect and more dangerous.
- **Optimal granularity of λ**: Are three tiers (0.0 / 0.5 / 1.0) sufficient? Or is finer continuous adjustment (e.g., 0.0–1.0 in 0.1 increments) needed? In theory, continuous is better, but in practice, three tiers already cover 90% of scenarios.
- **Cross-model generalization**: This experiment was entirely based on the DeepSeek series. Do GPT, Claude, Gemini, and other models exhibit consistent performance curves at the same λ? Different models may have different sensitivities to Memory strength.
- **Long-term trends**: As Agent usage extends from 1 year to 3 years, to 5 years, will the Memory Lock-in Effect of strong Memory worsen exponentially? The larger the Memory store, the stronger the historical gravity — is there a critical point beyond which strong Memory becomes harmful on any task?

---

## 6. Relationship to Hermes

Hermes already possesses the industry's strongest Memory system — SQLite persistence, cross-session preference memory, three-layer injection architecture (Base → Skills → Memory). This is the foundation of its dominance over all competitors on convergent tasks.

But what Hermes currently lacks is **dynamic Memory granularity control**. Hermes's Memory injection is full-strength — λ is fixed at 1.0. Across all tasks, all sessions, all contexts, Memory is injected with the same strength.

Filling this capability gap requires two changes, neither involving core architecture modifications:

1. **Memory layer tagging**: When storing Memory, tag each memory item with a layer label — "global constraint," "technical preference," "style preference," "historical decision," "successful pattern." Different layers correspond to different λ filtering strategies.

2. **Task classifier**: When the Agent receives a task, add a lightweight convergence–divergence classification step. The classifier doesn't need model inference — it can operate on keyword and task pattern matching (e.g., "fix," "deploy," "troubleshoot" → convergent; "ideate," "design," "write," "critique" → divergent). The classification result automatically determines the λ value for that session.

These two changes would allow Hermes to evolve from a "full-Memory platform" into a "granularity-controllable Memory platform" — simultaneously covering both convergent and divergent tasks, without needing an external Agent (like OpenClaw) to fill the weak-Memory gap.

---

## Conclusion

Memory isn't "the more the better" — it's "the better matched, the better." The Agent industry treating Memory as a binary variable (have/don't have) is a systemic cognitive blind spot. Memory strength should be a continuous spectrum, dynamically matched along the convergence–divergence task axis. Strong Memory is an accelerator for convergent tasks and a brake for divergent tasks — what you need isn't stronger Memory, but smarter Memory granularity control.

---

*Next: TBD*
