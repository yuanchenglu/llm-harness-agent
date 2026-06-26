# A1. Agent Harness for Large Language Model Agents: A Survey

**Authors:** Qianyu Meng, Yanan Wang, Liyi Chen et al.
**Status:** Preprint (v1, April 3, 2026)
**Source:** Preprints.org

> ⚠️ This is a comprehensive summary of the original paper. Preprints.org has restricted direct PDF download. The following is based on the best available text.

---

## Core Thesis: Harness, Not the Model, Is the Binding Constraint

> "The harness, not the model, is the binding constraint on real-world agent system performance."

This paper's central claim: the reliability of agent task execution depends more on the **infrastructure layer ("Agent Execution Harness")** than on the underlying model's capabilities. The paper formalizes this layer, provides a taxonomy and systematic analysis, and argues it is an independent architectural object requiring dedicated study.

---

## I. Core Definition: Formal Framework H = (E, T, C, S, L, V)

The agent harness is formally defined as a **six-component runtime governance system**:

> **H = (E, T, C, S, L, V)**

| Component | Name | Description |
|-----------|------|-------------|
| **E** | Execution Loop | Manages the observe→think→act cycle, handling turn ordering, termination conditions, and error recovery. Formalized as a labeled transition system (LTS) with safety (no runaway) and liveness (reachable terminal state) properties. |
| **T** | Tool Registry | A typed, validated catalog of available tools. Routes, monitors, and manages tool calls. |
| **C** | Context Manager | Manages what information enters the model's context window. Manages compression, retrieval, and prioritization strategies. |
| **S** | State Store | Persists task-relevant state across turns and sessions; supports recovery from partial failures. |
| **L** | Lifecycle Hooks | Pre- and post-call interceptors: authentication, logging, policy enforcement, and instrumentation. |
| **V** | Evaluation Interface | Standardized instrumentation for capturing action traces, intermediate states, and success signals, supporting offline analysis and cross-harness comparison. Explicitly distinguished from operational logging (L). |

**Key boundary judgments:**
- **Minimal harness:** Implements E and T
- **Not a harness:** ReAct (no error recovery, no formal registry). LangGraph (framework, missing C/S/L/V)
- **Capability modules:** MemGPT (strong C and S, missing E/T)

---

## II. Evidence Matrix: Harness Changes > Model Changes

| Source | Intervention | Performance Change | Model Changed? |
|--------|-------------|-------------------|---------------|
| Practitioner (Pi Research) | Changed editing tool format | 6.7% → **68.3%** (10× improvement) | No |
| Practitioner (LangChain DeepAgents) | Middleware, lifecycle hooks, system prompts | 52.8% → **66.5%** (+26%) | No |
| Preprint (Meta-Harness, Stanford/MIT) | Automated agent search over harness space | **76.4%** on TerminalBench-2 (surpassing hand-designed) | No |
| Preprint (AgencyBench) | Models on native vs. external harness | Native ecosystem scores significantly higher (e.g., 48.4%) | No |
| Practitioner (Vercel) | Reduced tools from 15 to 2 | 80% → **100%** accuracy | No |

**Key industry reports:**
- **OpenAI Codex:** Coined the term "harness engineering." Team built ~1M lines of production code, zero hand-written code.
- **Stripe Minions:** ~1300 PRs/week. Curated tool registry is critical; exposing all tools degrades performance.
- **OpenClaw PRISM:** First publicly released open-source harness runtime security layer.

---

## III. Historical Evolution: The "Harness Turn"

The harness concept crystallizes from three lineages:

1. **Software testing harness (JUnit):** Governance wrapper pattern.
2. **RL environments (OpenAI Gym):** Interface standardization (`step()`/`observe()`).
3. **Early LLM agents (ReAct, AutoGPT, MemGPT):** Catalog of failure modes that define what governance is needed.

**"Harness Turn" (2024–2026)** marks the shift from model-centric research to infrastructure-centric engineering, catalyzed by protocol standardization (MCP, A2A), formalization (AIOS), and large-scale evaluation infrastructure (HAL, AgencyBench).

**Three engineering paradigms:**
- **Prompt Engineering (2022–2024):** "What text to give?"
- **Context Engineering (2025):** "What information to structure?"
- **Harness Engineering (2026):** "What governance to design?"

---

## IV. System Taxonomy (22 Systems Analyzed)

| Category | Example Systems | Component Coverage |
|----------|----------------|-------------------|
| **Full-stack harnesses** | DeepAgents, OpenClaw, OpenHands, AIOS, Claude Code | Full E, T, C, S, L, V |
| **Frameworks** | LangGraph, AutoGen, LlamaIndex | Partial E and T; C, S, L, V typically delegated |
| **Capability modules** | MemGPT (C/S), MCP Server (T), Voyager (S) | Strong in 1–2 components; no orchestration |
| **Evaluation infrastructure** | HAL, AgencyBench, SWE-bench, OSWorld | Extensive E, V; critical for domain reproducibility |

**Key finding:** **V (Evaluation Interface)** and **L (Lifecycle Hooks)** are the least developed components.

---

> *(Note: The original abstract was truncated due to context limitations at the time of extraction.)*
