# DeepSeek Agent Theory Guide: From Model Capability to a Verifiable Agent System

> This is the conceptual entry point of the project. It explains which claims are grounded in source code, which are design hypotheses, and how the research should guide a DeepSeek-native Agent without turning product observations into universal laws.

## Abstract

A usable Agent is not merely a model with tools. It is a system composed of a model, context compiler, tool runtime, permission layer, state store, verification loop, and user interface:

```text
Agent = Model × Harness × Environment × Evidence
```

The multiplication sign represents a weakest-link effect. A capable model with unsafe execution is unusable; rich tools with a noisy context are hard to select; an implementation without tests or review is difficult to trust.

The proposed DeepSeek Agent direction is:

```text
Cache-first        Keep reusable prefixes stable when correctness permits
Layout-driven      Compile model-visible context instead of replaying every log
Policy-enforced    The model proposes; the runtime authorizes and executes
Checkpoint-gated  Completion is determined by evidence and review state
Model-routed       Route Flash / Pro / Thinking by risk and task state
```

These are architectural hypotheses to validate, not universal laws already proven by benchmarks.

## 1. What a Harness Does

Models handle probabilistic work: interpreting intent, generating candidates, reasoning, and expression. Harnesses handle deterministic work: assembling context, exposing tools, enforcing permissions, persisting state, measuring cost, and verifying results.

The CPU/operating-system analogy is useful but incomplete. A model is not deterministic, and a Harness is more than an OS. More precisely, the Harness is the protocol, control, and evidence layer between a model and the real world.

The same model behaves differently across Agent products because it receives a different process: different instructions, file excerpts, tool schemas, permission decisions, retries, summaries, and completion gates. Harness quality matters greatly, but “Harness improvements are always exponential” is not an established law.

## 2. Five Layers of a DeepSeek Agent

### 2.1 Model Profile

A Harness must express the real provider contract: context window, thinking modes, tool-call protocol, `reasoning_content` behavior, cache usage fields, pricing, latency, and endpoint availability. Whether reasoning should be dropped or replayed must be tested against the concrete endpoint and mode.

### 2.2 Context Compiler

Context is a compiled product, not a complete log:

```text
stable prefix     system rules, approved constraints, stable tool contracts
append-only proof decisions, checkpoints, tests, review verdicts
active working set current task, relevant files, recent tool feedback
external index    full traces, archived sessions, historical artifacts
```

A byte-stable prefix is a useful target, not an absolute rule. Security updates, tool changes, or an incorrect prefix must be allowed to rebuild.

### 2.3 Tool and Safety Runtime

Reliable execution requires schema validation, progressive disclosure, error sanitization, ask/allow/deny permissions, workspace isolation, version-anchored edits, and deterministic feedback from tests and LSP. Prompts must not replace permission enforcement, and model claims must not replace evidence.

### 2.4 Orchestrator

Multi-agent systems should be state machines, not role-play. Every role needs explicit inputs, outputs, exit conditions, isolated workspaces where needed, one loop authority, and visible budget/blocking state.

### 2.5 Evidence Ledger

“Done” should mean that scope, diff, tests, review, cost, and remaining risks are recorded. A checkpoint is valuable when it connects planning, execution, verification, review, and recovery—not merely when it stores another summary.

## 3. Calibrated Lessons from Existing Projects

| Project | Source-grounded lesson | Boundary |
|---|---|---|
| Claude Code | Plugins, skills, hooks, product interaction patterns | Official repository does not expose the full engine |
| Codex | Typed context, turn loop, compaction, guardian, sandbox | Fast-moving; cite fixed commits |
| Trae Agent | Small Agent loop, trajectory, Docker, MCP, stateful sequential thinking | No open-source test-time-scaling orchestrator found |
| Reasonix | DeepSeek adapter, cache telemetry, plan gate, compaction | Quality/cost advantages still require benchmarks |
| Hermes Agent | Tool registry, progressive disclosure, Agent OS capabilities | Self-improvement quality requires longitudinal evaluation |
| CodeWhale | Prefix drift checks, cache/cost telemetry, router, side-git, LSP | Full three-zone request contract is not yet wired |
| OpenCode | Multi-client open runtime and extension boundaries | Requires deeper audit and an adapter spike |
| OpenSpec | Versioned change artifacts | Does not replace runtime checkpoints |
| Superpowers | Composable engineering workflows | Enforcement depends on the host runtime |

## 4. Theory-to-Product Loop

```text
clarify intent
  → versioned spec/design/task artifacts
  → risk and cost routing
  → isolated execution and tool evidence
  → checkpoint
  → independent verification / Pro review when needed
  → archive decisions and reusable experience
```

The differentiated value should come from connecting routing to evidence gates, cache layout to runtime state, and design artifacts to real diffs/tests/review—not from simply combining many plugins.

## 5. Validation Agenda

The next priority is empirical validation:

1. `reasoning_content` drop/replay contract and cost;
2. cache impact of system/tools drift, mode switching, and compaction;
3. single-model vs. router vs. planner/executor vs. Pro review;
4. full tool catalogs vs. progressive disclosure;
5. success rate, rework, intervention, latency, and cost on the same task set.

Until these experiments are complete, this project will use terms such as “candidate design,” “confirmed in source,” and “awaiting benchmark,” rather than “proven optimal.”

## Conclusion

The useful meaning of `LLM + Harness = Agent` is not that the Harness is always more important than the model. It is this:

> Model capability becomes dependable product capability only through controlled context, reliable tools, safe execution, persistent state, and verifiable evidence.
