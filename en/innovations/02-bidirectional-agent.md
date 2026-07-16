# Bidirectional Agent: Brain Actively Drives the Cerebellum

> **Evidence note:** This paper presents Harness design hypotheses and validation paths. Unless fixed-version source, runtime wiring, and reproducible experiments are provided, "validated" does not mean universally proven. Read [Research Method and Evidence Calibration](../theory/research-method.md) first.

> Innovation Point: I-02
> **LLM + Harness = Agent** · Part 2
> Series: [LLM + Harness = Agent](../../README.md)
> Previous: [01 Agent Immune System](01-agent-immune-system.md)
> Next: [03 Attention Budget Management](03-attention-budget.md)

---

> **Abstract:** Every current Agent architecture shares the same one-way assumption - the LLM can only passively respond to Harness calls, never proactively make requests based on its own cognitive state. This paper argues that the root cause is not model capability, but the design assumption baked into the tool-calling API protocol itself: the LLM is modeled as a stateless function, not an equal participant in a dialogue. The proposed Bidirectional Agent architecture introduces four new primitives - `need_more_context`, `request_specialized_model`, `trigger_self_review`, and `propose_skill` - that let the LLM actively declare its needs during inference, upgrading the Agent Loop from "Harness drives LLM" to "LLM ⇄ Harness joint decision-making."

---

## 1. Problem Definition

### 1.1 The Phenomenon

Open the source code of any Agent product. Whether it's LangChain Agent, OpenAI Assistants, AutoGPT, or Claude Code - you see the same architectural pattern:

```
User input → Harness receives → Decomposes task → Calls LLM → LLM returns tool_call
→ Harness executes tool → Feeds result back to LLM → Loop
```

The LLM is passive from start to finish. It only "thinks" when it gets called. It can perceive that "the previous tool call returned empty results," but it won't proactively say: "Wait. Before the next step, I need information X. But I don't have X. Go get it for me."

This architectural pattern is not an accidental choice of any single product. It is the default assumption of every Agent framework.

The consequence is systemic: the LLM has zero voice about its own capability boundaries. It knows it doesn't understand a particular domain, but it won't proactively say "This task exceeds my abilities - swap in a specialized model." It knows it hasn't seen a critical file, but it won't proactively say "Give me that file, otherwise my judgment is based on guesswork." It can only answer when the Harness asks. It cannot speak when it needs to.

Like someone sitting in the passenger seat. They can see the road. They can offer advice. But they don't have the steering wheel. Braking, turning - everything waits for the driver (Harness) to act first, and only then can they react.

### 1.2 Root Cause

The root cause is not model capability. It is the design assumption of the tool-calling API protocol.

Every mainstream LLM API today (OpenAI function calling, Anthropic tool use, Google Gemini function calling) shares the same protocol pattern: request-response. The client (Harness) sends a request containing messages and tools. The server (LLM) returns a response containing text and tool_calls. One request, one response. The LLM cannot proactively "do" anything outside of a single request's response.

The underlying assumption of this protocol: **the LLM is a stateless function** - given input, produce output. A function does not "proactively call" its caller. A function's control flow is always: caller → function → return.

When the LLM is embedded in an Agent Loop, this assumption is inherited unchanged. The Agent Loop treats the LLM as a reasoning engine to invoke, and the LLM returns reasoning results. The Harness is always the caller. The LLM is always the callee.

**Why "giving the LLM more tools" does not solve this problem**: Tools are a preset list of capabilities that the Harness allows the LLM to invoke. But the LLM's real needs often fall outside this list. What it needs is not a specific tool, but a meta-expressive ability to say "I need more context before I can make a judgment." Tools extend the range of Harness-preset capabilities. They do not grant the LLM initiative.

### 1.3 Formalization

Define the interaction pattern of a standard Agent Loop:

Let the conversation state be S(t), the Harness's reasoning function be H, and the LLM's reasoning function be L. The standard Agent Loop interaction at time t is:

```
L: S(t) → (response_t, tool_calls_t)
H: (response_t, tool_calls_t) → S(t+1)
```

The critical constraint: L's domain does not include the ability to "actively modify H's behavior." L can only produce responses and tool calls within its output space. It cannot produce an instruction that says "before the next step, force H to perform some operation." H's transformation function is closed - it has already determined all executable operation paths before calling L.

A Bidirectional Agent Loop needs to break this constraint by introducing a reverse channel:

```
L: S(t) → (response_t, tool_calls_t, meta_directives_t)
H: (response_t, tool_calls_t, meta_directives_t) → S(t+1)
```

Where meta_directives are meta-instructions proactively issued by the LLM that have binding force on Harness behavior. This is the formal condition for upgrading the LLM from "callee" to "equal participant."

---

## 2. Existing Approaches and Their Limitations

| Approach | Core Idea | Why It Does Not Solve Bidirectionality |
|----------|-----------|--------------------------------------|
| **Standard Tool Calling** | LLM declares tool_call in its response, Harness executes and returns results | LLM can only call Harness-pre-registered tools. Cannot express "I need this tool, but it's not in the list" - this meta-level need has no corresponding tool_call protocol |
| **ReAct Pattern** | LLM alternates between Thought and Action outputs | Thought is debug info for developers - Harness does not parse or respond to it. The LLM's "thinking" does not change Harness behavior |
| **Planning Agent** | Harness pre-decomposes tasks into a step list before calling LLM | Planning is Harness's one-sided decision. If the plan is wrong, the LLM cannot correct it - because the LLM's input no longer contains "the plan itself" |
| **Reflection Agent** | After LLM produces output, Harness calls LLM again to review the output | Reflection is still a second invocation initiated by Harness. The LLM cannot proactively say "I need to reflect" during its first inference pass - the timing is preset by Harness |
| **Multi-Agent Orchestration** | Multiple Agents collaborate in parallel or sequence | The orchestrator (main Agent) is still Harness-layer logic. Sub-agents lack equal proactive communication - communication paths are preset by Harness |
| **Hermes delegate_task** | Main Agent dispatches subtasks to specialized sub-agents | The dispatch decision is triggered by Harness (based on task type matching), not proactively requested by the LLM. When the LLM perceives "I'm not good at this subtask," it has no channel to express that |

**Common flaw**: Every approach adds features around the periphery of the Agent Loop - more tools, more reflection rounds, more Agent roles. But none of them modify the core protocol of the Agent Loop: the LLM can only be the responder, never the initiator. The problem is not the Agent's peripheral capabilities. It is the Agent's communication topology.

---

## 3. Solution Design

### 3.1 Core Mechanism: LLM ⇄ Harness Bidirectional Flow

This solution introduces four new primitives into the standard Agent Loop. These are not "more tools." They are meta-instructions through which the LLM proactively declares its cognitive state and needs to the Harness.

**Primitive One: need_more_context**

When the LLM detects that critical information is missing during inference, it proactively declares the need to the Harness.

```
LLM → Harness: need_more_context(
  target: "config/deploy.yaml",
  reason: "I need the deployment environment to select the correct build command.
          The current context only has code files, no deployment configuration"
)
```

The essential difference from a tool_call: tool_call invokes a specific tool that Harness has pre-registered (such as `read_file`). need_more_context declares a cognitive need - the LLM does not presuppose "which tool can satisfy this need." The Harness interprets and executes accordingly. If `config/deploy.yaml` does not exist, the Harness can try searching, ask the user, or inform the LLM that the file is missing - instead of directly returning an error.

**Primitive Two: request_specialized_model**

When the LLM recognizes that the current task exceeds its own capability boundary, it proactively requests a model switch.

```
LLM → Harness: request_specialized_model(
  task: "Review the Python code in this PR for security vulnerabilities",
  reason: "I am a general-purpose reasoning model and lack domain knowledge
           of security vulnerabilities. Recommend switching to a
           security-review specialized model"
)
```

Currently, every Agent's model routing is determined by Harness-preset rules ("code tasks use model A, text tasks use model B"). But the optimal route often depends on the specific content of the task. Only the LLM can perceive during inference that "this task contains a security review subtask." Harness preset rules cannot capture this fine-grained judgment.

**Primitive Three: trigger_self_review**

Before outputting a critical decision, the LLM proactively requests an independent review of its own reasoning.

```
LLM → Harness: trigger_self_review(
  target: "Database migration plan about to be executed",
  reason: "This migration involves production databases and has broad impact.
           Recommend an independent Agent review the migration plan
           before execution"
)
```

The difference from Reflection Agent: Reflection is a second call initiated by Harness after the LLM finishes its output. Harness presets a rule like "important decisions require reflection." trigger_self_review is the LLM proactively judging during output that "this decision needs review" - the judgment is based on the risk level of the task content, not on a Harness-preset rule table.

**Primitive Four: propose_skill**

After completing a task, when the LLM discovers a reusable pattern, it proactively proposes crystallizing it into a Skill.

```
LLM → Harness: propose_skill(
  name: "pre-commit-typecheck",
  trigger: "before git commit",
  steps: ["Run tsc --noEmit", "Check type error count", "Non-zero count blocks commit"],
  reason: "TypeScript type checking before every commit is a recurring need
           in this project. Crystallizing this as a Skill eliminates
           repetitive reasoning on every round"
)
```

The difference from Hermes's existing Skill mechanism: currently Skills are triggered by Harness after task success. propose_skill lets the LLM proactively identify reusable patterns during inference - without waiting for a "task success" signal from the Harness.

### 3.2 Key Design Decisions

**Why four primitives instead of one generic "request"?**

The four primitives cover four orthogonal dimensions of LLM initiative:

- need_more_context → "What I lack"
- request_specialized_model → "What I'm not good at"
- trigger_self_review → "What I'm uncertain about"
- propose_skill → "What I've learned"

These four dimensions exhaust the metacognitive needs an LLM can generate during inference. A single generic "request" primitive would mix all of these together, increasing the Harness's interpretation burden and the risk of misjudgment. Precise primitives let the Harness's response logic be deterministic - it does not need to "understand what the LLM is asking for." It only needs to "execute the corresponding handling flow based on the primitive type."

**Why not let the LLM directly control the Agent Loop?**

Giving full control to the LLM (letting it decide what to do next, what tools to call, and when to end) might seem like the ultimate form of bidirectional flow. But it introduces new risks: the LLM's reasoning cost is already high due to O(n²) attention. Adding control-flow decision-making on top would make the Agent Loop unstable. This solution's choice is: **the Harness retains control over the Agent Loop, but the LLM gains advisory power over Harness behavior.** The Harness must respond to need_more_context (because reasoning cannot continue without context), but can reject propose_skill (if the Skill registry is full or the format is invalid).

---

## 4. Analysis

### 4.1 Why This Solution Addresses the Fundamental Problem

The fundamental problem is not that "the LLM is not smart enough." It is that "the Agent's communication topology is one-way." A one-way topology means the LLM can only answer when asked. It cannot speak when it needs to.

Bidirectional flow upgrades the communication topology from `Harness → LLM` to `Harness ⇄ LLM`. This is not about giving the LLM more tools, more context, or stronger reasoning ability. It is about changing the LLM's role in the system: from callee to equal participant.

Specifically, the four primitives address four single points of failure:

- **Missing information**: In a one-way architecture, the LLM can only reason with existing context. Missing information leads to incorrect output. need_more_context lets the LLM proactively supplement context before reasoning is interrupted.
- **Capability boundaries**: In a one-way architecture, the LLM grits its teeth and handles every task because its tool list has no "reject task" option. request_specialized_model gives the LLM a "safe exit."
- **Risky decisions**: In a one-way architecture, the LLM cannot distinguish between "ordinary decisions" and "high-risk decisions." It has only one output mode. trigger_self_review lets the LLM flag risks and introduce an additional safety verification layer.
- **Experience accumulation**: In a one-way architecture, the LLM reasons from scratch every time. propose_skill lets the LLM crystallize reasoning results into reusable execution units.

### 4.2 Boundary Conditions

Bidirectional flow **should not** be triggered in the following scenarios:

- **Simple deterministic tasks**: The task steps are fully determined, no additional context is needed, and no risky decisions are involved (e.g., "change the version number in README from 1.0 to 1.1"). In these cases, bidirectional primitives only add meaningless round-trip communication.
- **Harness preset rules already cover it**: If the Harness already handles model routing through static rules (e.g., "code reviews always use the security model"), request_specialized_model is redundant.
- **Misuse risk of LLM initiative**: A malicious prompt could exploit need_more_context to trick the Harness into reading sensitive files. The Harness must perform permission checks on the LLM's meta-directives - not every need_more_context request should be satisfied.

**Design principle**: Bidirectionality grants the LLM "advisory power," not "control power." The Harness remains the final decision-maker. It can accept the LLM's suggestion (need_more_context), reject it (propose_skill with invalid format), or conditionally execute it (request_specialized_model degrades to the general model when no match is found in the model pool).

### 4.3 Comparison with the Closest Related Work

| Dimension | Hermes delegate_task | Anthropic Joint RL | This Solution |
|-----------|:---:|:---:|:---:|
| **Who decides dispatch/switch** | Harness (based on task type matching) | Joint optimization during training | LLM proactively declares needs |
| **Execution timing** | Static dispatch before task starts | Training phase, not runtime | Dynamic request during task execution |
| **Does LLM have initiative?** | No | Yes during training, no during inference | Yes, real-time during inference |
| **Requires training?** | No | Yes (Joint RL requires training) | No (protocol-level change) |
| **Compatibility with existing frameworks** | Already compatible | Requires custom training pipeline | Requires API protocol extension |

Anthropic's Joint RL may be the closest existing work to the concept of bidirectional flow. Joint RL uses the same feedback signal to simultaneously optimize the model and the Harness - which fundamentally requires bidirectional information flow between the two. If the LLM is always one-way passive, Joint RL cannot work in principle: the Harness cannot obtain signals from the LLM's reasoning process to optimize itself.

However, Joint RL operates during the training phase. The bidirectional flow in this solution operates during the inference phase - no model retraining is needed. It only requires extending the tool-calling API protocol to let the LLM's output space include meta-directives.

---

## 5. Verification Path

### 5.1 Verified

- **Problem existence**: I verified the Agent Loop source code in Hermes OMO v0.3. The Harness-to-LLM call path in `plan-execute.ts` is entirely one-way. The LLM's response is parsed into tool_calls and fed directly into the Harness's execution queue. The LLM has no channel to insert meta-directives. This is not a design flaw in Hermes - every mainstream Agent framework (LangChain, AutoGPT, CrewAI) uses the same one-way pattern.
- **Protocol limitation**: I verified the tool-calling API specifications from OpenAI, Anthropic, and Google. All three use a request-response pattern and do not support the LLM proactively initiating requests to the client outside of its response. Bidirectional flow requires extension at the API protocol level.

### 5.2 To Be Verified

- **Primitive trigger accuracy**: Whether need_more_context triggers accurately on 100 tasks - whether the trigger timing is reasonable (not too early, not too late), and whether the stated reason is credible (not "let me just request a random file to see what happens").
- **Harness response latency**: The change in the average number of Agent Loop iterations after introducing bidirectional primitives. need_more_context adds one round-trip of communication - this overhead needs to be weighed against the cost of the errors it prevents.
- **Integration difficulty with Hermes's existing architecture**: Of the four primitives, propose_skill has the highest overlap with Hermes's existing Skill mechanism and the lowest integration difficulty. need_more_context and request_specialized_model require changing the core Agent Loop - the highest integration difficulty. trigger_self_review can be implemented by spawning an independent Agent without modifying the core Loop.
- **Anthropic frontier tracking**: If Anthropic publishes technical details of their Joint RL on Opus + Claude Code, the implementation path for bidirectional flow needs to be re-evaluated - a superior joint training approach may exist.

---

## 6. Relationship to Hermes

Hermes's `delegate_task` mechanism is half a step in the right direction. It acknowledges that "some tasks should not be executed by the current Agent." But `delegate_task`'s trigger authority lies with the Harness, not the LLM.

Completing the other half requires letting `delegate_task` accept proactive requests from the LLM. The concrete path:

1. **Lightest weight**: Add a `delegate_task` tool to the existing tool_call list. The LLM can call it like any other tool. But this is not true bidirectional flow - it only adds one more tool. The LLM can still only call tools when the Harness asks it to.
2. **Medium change**: Add a "meta-directive channel" to the Agent Loop. The LLM's response contains not only tool_calls but also `meta_directives`. The Harness must process meta_directives before processing tool_calls. This is the core proposal of this paper - it requires modifying the Agent Loop's parsing logic.
3. **Deep integration**: Adopt the four primitives as Harness protocol-layer extensions. Every Hermes Agent supports bidirectional flow by default. This requires modifying the Hermes Agent Loop core, but once implemented, all upper-layer features (Skills, Delegate, Planning) will automatically gain bidirectionality.

Recommended path: start with path 2 (medium change), validate the actual effect of bidirectional flow on an experimental branch of Hermes. If validation passes, proceed to path 3 for deep integration.

---

## Conclusion

The direction of Agent evolution is not "smarter models." It is "a more equal model-Harness relationship." The one-way architecture assumes the LLM is a stateless reasoning engine. This assumption is wrong in production Agents. The LLM accumulates a substantial amount of cognitive state during long conversations. It is capable of, and should have the right to, express its own needs and boundaries.

Knowledge is the beginning of action. Action is the completion of knowledge. The LLM first declares its cognitive state (knowledge). The Harness then acts accordingly (action). The two form a closed loop, not a one-way instruction chain.

---

*Previous: [01 Agent Immune System](01-agent-immune-system.md) - The immune system solves "how to self-repair after making a mistake" (post-error correction). The brain driving the cerebellum solves "how to realize you need help before making a mistake" (pre-error prevention). Together, they cover the two core dimensions of Agent reliability: when it makes a mistake, it can repair. When it can't see clearly, it can ask.*
