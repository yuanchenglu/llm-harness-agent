# LLM + Harness = Agent: Paper Database

> Core thesis: Agent = Model × Harness × Environment × Evidence
> Harness = { Execution Loop, Tool Registry, Context Manager, State Store, Lifecycle Hooks, Evaluation Interface }

This database curates high-quality academic papers directly relevant to the **LLM + Harness = Agent** proposition. Each entry includes full citation, abstract (synthesized from original), key contributions, and a relevance analysis connecting the work back to the harness theory.

---

## A. Core Harness Theory

Papers that directly discuss the "system around the model" as a first-class architectural object.

---

### A1. Agent Harness for Large Language Model Agents: A Survey

| Field | Value |
|-------|-------|
| **Authors** | Qianyu Meng, Yanan Wang, Liyi Chen et al. |
| **Title** | Agent Harness for Large Language Model Agents: A Survey |
| **Date** | 2026-04-07 (v1) |
| **Source** | Preprints.org, 2026 (not yet peer-reviewed) |
| **URL** | https://www.preprints.org/manuscript/202604.0428 |
| **Status** | Preprint |

**Abstract.** The reliability of LLM agents in production is a function of the agent execution harness rather than the model alone. This survey formally defines the harness as the six-component tuple H = (E, T, C, S, L, V): Execution Loop, Tool Registry, Context Manager, State Store, Lifecycle Hooks, Evaluation Interface. It surveys 23 systems across 6 categories, identifies a "modularity gap" in the current ecosystem, and documents 9 tightly coupled technical challenges including security/sandboxing, evaluation, protocol standardization, and memory governance. Core evidence: harness-level changes alone produce up to 10× improvement on coding benchmarks, +26% on TerminalBench, +4.7 pp on mathematical reasoning — without any model modification.

**Relevance to LLM + Harness = Agent.** This is the most directly relevant paper to the proposition. It formalizes the very concept of "harness" as a first-class construct, provides a concrete six-component definition, and collects empirical evidence that harness improvements dominate model improvements. The paper explicitly cites Hermes Agent, OpenClaw, AIOS, and OpenHands as full-stack examples.

---

### A2. AIOS: LLM Agent Operating System

| Field | Value |
|-------|-------|
| **Authors** | Kai Mei, Xi Zhu, Wujiang Xu, Mingyu Jin et al. |
| **Title** | AIOS: LLM Agent Operating System |
| **Date** | 2024-03-25 (arXiv v1) / 2025 (COLM) |
| **Source** | Conference on Language Modeling (COLM), 2025 |
| **arXiv** | https://arxiv.org/abs/2403.16971 |
| **DOI** | Published as a full paper at COLM 2025 |

**Abstract.** This paper presents AIOS, an LLM agent operating system, which embeds large language models into operating systems as the "brain" of the OS. AIOS addresses challenges in LLM-based agent deployment: context scheduling, concurrent agent management, tool orchestration, and resource allocation. It proposes a modular architecture that separates the LLM from the agent execution infrastructure, enabling multiple agents to share the same LLM backend while maintaining isolation and state. The system introduces an Agent Scheduler, Context Manager, Memory Manager, and Tool Manager as first-class OS modules.

**Relevance to LLM + Harness = Agent.** AIOS is the most explicit realization of the "OS metaphor" for the harness concept. It treats the LLM as a CPU and builds an operating system around it — exactly the CPU/OS analogy used in the DeepSeek Agent theory guide. Its modular architecture (scheduler, context manager, memory manager, tool manager) maps directly to the Harness components defined in the theory.

---

### A3. A Survey on Large Language Model Based Autonomous Agents

| Field | Value |
|-------|-------|
| **Authors** | Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, Wayne Xin Zhao, Zhewei Wei, Ji-Rong Wen |
| **Title** | A Survey on Large Language Model Based Autonomous Agents |
| **Date** | 2023-08-22 (arXiv v1) / 2024-03 (Front. Comput. Sci.) |
| **Source** | Frontiers of Computer Science (Springer Nature), Vol. 18, Article 186345, 2024 |
| **DOI** | 10.1007/s11704-024-40231-1 |
| **arXiv** | 2308.11432 |
| **Status** | ✅ SCI-indexed, Open Access |

**Abstract.** Autonomous agents have long been a prominent research focus. Previous research often trains agents with limited knowledge in isolated environments, diverging from human learning processes. Recently, through the acquisition of vast amounts of web knowledge, LLMs have shown remarkable potential in achieving human-level intelligence, sparking an upsurge in LLM-based autonomous agent research. This survey delivers a systematic review from a holistic perspective: (1) discussing the construction of LLM-based autonomous agents with a unified framework encompassing Brain (LLM), Memory, Planning, and Action; (2) presenting a comprehensive overview of applications in social science, natural science, and engineering; (3) delving into evaluation strategies; (4) presenting challenges and future directions.

**Relevance to LLM + Harness = Agent.** This survey proposes a unified framework that treats the agent as more than just the model — it explicitly identifies Memory, Planning, and Action (Tool Use) as co-equal components alongside the LLM "brain." This framework is the academic foundation for the concept that the model alone is insufficient; the surrounding architecture (the harness) is equally critical. Highly cited (>1,500 citations), making it the most influential survey in this space.

---

### A4. The Rise and Potential of Large Language Model Based Agents: A Survey

| Field | Value |
|-------|-------|
| **Authors** | Zhiheng Xi, Wenxiang Chen, Xin Guo et al. (29 authors, Fudan NLP Group) |
| **Title** | The Rise and Potential of Large Language Model Based Agents: A Survey |
| **Date** | 2023-09-14 (arXiv v1) / 2025-01 (Sci. China Inf. Sci.) |
| **Source** | Science China Information Sciences, Vol. 68(2), 2025 |
| **DOI** | 10.1007/s11432-024-4222-0 |
| **arXiv** | 2309.07864 |
| **Status** | ✅ SCI-indexed (CCF-A Chinese journal), 86 pages |

**Abstract.** For a long time, humanity has pursued AI equivalent to or surpassing the human level, with AI agents considered a promising vehicle. Due to the versatile capabilities they demonstrate, LLMs are regarded as potential sparks for AGI, offering hope for building general AI agents. This survey proposes a unified general framework for LLM-based agents composed of three core modules: Brain (the planner/reasoner — the LLM itself), Perception (the interface for sensing the environment across text, vision, audio), and Action (executes decisions via tool use, API calls, physical actions). The survey reviews applications across single-agent, multi-agent, and human-agent scenarios, and discusses emergent phenomena in agent societies.

**Relevance to LLM + Harness = Agent.** The "Brain, Perception, Action" framework directly parallels the harness theory's separation of concerns. The Brain is the model, but Perception and Action are harness-level capabilities that bridge the model to the real world. The 86-page depth makes this the most comprehensive survey available.

---

### A5. A Survey on LLM-based Multi-Agent Systems: Workflow, Infrastructure, and Challenges

| Field | Value |
|-------|-------|
| **Authors** | Xinyi Li, Sai Wang, Siqi Zeng, Yu Wu, Yi Yang |
| **Title** | A Survey on LLM-based Multi-Agent Systems: Workflow, Infrastructure, and Challenges |
| **Date** | 2024-10-08 |
| **Source** | Vicinagearth, Vol. 1(1), 2024 |
| **DOI** | 10.1007/s44336-024-00009-2 |
| **Status** | ✅ Peer-reviewed |

**Abstract.** This paper presents a comprehensive survey of LLM-based multi-agent systems (MAS), offering a systematic review of their workflow, infrastructure, and challenges. It covers agent communication protocols, coordination mechanisms, task decomposition strategies, and the supporting infrastructure required for multi-agent deployment. The survey identifies key gaps in current systems, particularly around state management, inter-agent memory sharing, and evaluation standardization.

**Relevance to LLM + Harness = Agent.** Multi-agent systems represent the most demanding test case for the harness concept: when multiple agents coordinate, the infrastructure (communication protocols, shared state, isolation guarantees, orchestration) entirely determines system reliability. The survey's focus on infrastructure and workflow directly supports the argument that harness quality — not model quality — is the limiting factor.

---

## B. Foundational Works

Papers that established the core paradigm of LLM-based agents — each a necessary component of the modern harness.

---

### B1. ReAct: Synergizing Reasoning and Acting in Language Models

| Field | Value |
|-------|-------|
| **Authors** | Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao |
| **Title** | ReAct: Synergizing Reasoning and Acting in Language Models |
| **Date** | 2022-10-06 (arXiv v1) / 2023 (ICLR) |
| **Source** | International Conference on Learning Representations (ICLR), 2023 |
| **arXiv** | 2210.03629 |
| **Status** | ✅ CCF-A conference, >11,000 citations |

**Abstract.** While large language models (LLMs) have demonstrated impressive capabilities across tasks in reasoning and zero-shot generalization, they still rely on static, single-turn interactions. We introduce the ReAct paradigm — a general framework where LLMs interleave reasoning traces (thoughts) with task-specific actions (tool calls, environment interactions) in a unified loop. This synergizes the complementary strengths of reasoning and acting: reasoning guides action selection, and action outcomes inform subsequent reasoning. ReAct outperforms baselines across diverse benchmarks including question answering, fact verification, and interactive decision-making, while also improving human interpretability and trustworthiness.

**Relevance to LLM + Harness = Agent.** ReAct is the foundational paper for the "LM + action = agent" concept. It demonstrates that the key enabler of agent behavior is not a better model, but a loop structure that interleaves reasoning with action-taking. This loop — the "E" (Execution Loop) component in the harness model — is the single most important harness mechanism, and ReAct was the first to formalize it. Every modern agent harness (including Claude Code, Codex, Hermes, OpenHands) implements a variant of the ReAct loop.

---

### B2. Generative Agents: Interactive Simulacra of Human Behavior

| Field | Value |
|-------|-------|
| **Authors** | Joon Sung Park, Joseph O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein |
| **Title** | Generative Agents: Interactive Simulacra of Human Behavior |
| **Date** | 2023-04-07 (arXiv v1) / 2023-10 (UIST) |
| **Source** | ACM Symposium on User Interface Software and Technology (UIST), 2023 |
| **arXiv** | 2304.03442 |
| **DOI** | 10.1145/3586183.3606763 |
| **Status** | ✅ CCF-A conference (ACM), highly cited |

**Abstract.** Believable proxies of human behavior can empower interactive applications ranging from immersive environments to rehearsal spaces for interpersonal skills to prototyping tools. In this work, we introduce generative agents — computational software agents that simulate believable human behaviors. Generative agents wake up, cook breakfast, and head to work; artists paint, while authors write; they form opinions, notice each other, and initiate conversations; they remember and reflect on past days as they plan the next day. To enable these behaviors, we describe an agent architecture that extends a large language model with memory, planning, and reflection mechanisms. We instantiate this architecture to populate a sandbox environment, where end users can interact with a small town of twenty-five generative agents using natural language.

**Relevance to LLM + Harness = Agent.** Generative Agents is the seminal demonstration that an LLM alone is insufficient for believable agent behavior. Its architecture explicitly adds Memory (long-term stream + retrieval), Planning (daily plans + reflections), and Social Awareness as harness components around the LLM. The paper's architecture directly inspired the Memory and Skills layers in modern harnesses like Hermes. The finding that "agent believability depends on the architecture, not the model" is core to the harness thesis.

---

### B3. Toolformer: Language Models Can Teach Themselves to Use Tools

| Field | Value |
|-------|-------|
| **Authors** | Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom |
| **Title** | Toolformer: Language Models Can Teach Themselves to Use Tools |
| **Date** | 2023-02-09 (arXiv v1) / 2023 (NeurIPS) |
| **Source** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2302.04761 |
| **Status** | ✅ CCF-A conference |

**Abstract.** Language models (LMs) exhibit remarkable abilities to solve new tasks from just a few examples or from simple instructions, but they struggle with tasks that require complex computation, factual knowledge, or access to external information. We introduce Toolformer, a model trained to decide which APIs to call, when to call them, what arguments to pass, and how to best incorporate the results into future token prediction. This is done in a self-supervised manner — the model learns to teach itself to use tools via API calls embedded in text. The resulting model achieves substantially improved zero-shot performance across a variety of downstream tasks, often competitive with much larger models, without sacrificing core language modeling capabilities.

**Relevance to LLM + Harness = Agent.** Toolformer establishes that the ability to use tools (the "T" — Tool Registry component in the harness model) can and should be a structured capability managed outside the model's forward pass. The key insight: tool use is not a model capability but a harness-level protocol. The model proposes tool calls, but the harness must resolve, execute, and integrate results. This separation of concerns is exactly the harness philosophy.

---

### B4. Reflexion: Language Agents with Verbal Reinforcement Learning

| Field | Value |
|-------|-------|
| **Authors** | Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao |
| **Title** | Reflexion: Language Agents with Verbal Reinforcement Learning |
| **Date** | 2023-03-20 (arXiv v1) / 2023 (NeurIPS) |
| **Source** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2303.11366 |
| **Status** | ✅ CCF-A conference |

**Abstract.** We introduce Reflexion, a framework to reinforce language agents by learning from prior mistakes. The agent acquires a "reflection" — a verbal summary of what went wrong and how to improve — which is stored in episodic memory and injected into the agent's context on subsequent attempts. This verbal reinforcement is more flexible and sample-efficient than traditional RL approaches. Across various tasks including decision-making, coding, and reasoning, Reflexion significantly improves agent performance by enabling self-correction without weight updates.

**Relevance to LLM + Harness = Agent.** Reflexion is a pure harness-level innovation: it modifies **what information enters the context window** based on past execution outcomes, without any model retraining. The paper demonstrates that adding a reflection-and-memory loop to an agent produces large gains — solely through harness changes. This is precisely the Memory (S — State Store) and Context Manager (C) components of the harness model at work.

---

### B5. Tree of Thoughts: Deliberate Problem Solving with Large Language Models

| Field | Value |
|-------|-------|
| **Authors** | Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Tom Griffiths, Yuan Cao, Karthik Narasimhan |
| **Title** | Tree of Thoughts: Deliberate Problem Solving with Large Language Models |
| **Date** | 2023-05-06 (arXiv v1) / 2023 (NeurIPS) |
| **Source** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2305.10601 |
| **Status** | ✅ CCF-A conference |

**Abstract.** Language models are increasingly being used for tasks that require planning and exploration. However, the standard autoregressive generation paradigm — left-to-right, one token at a time — limits deliberate decision-making. We introduce Tree of Thoughts (ToT), a framework that generalizes over Chain-of-Thought prompting and allows LMs to explore multiple reasoning paths simultaneously. ToT enables LMs to perform strategic lookahead, backtracking, and deliberate search. Experiments on three novel tasks show that ToT significantly enhances LM problem-solving capabilities.

**Relevance to LLM + Harness = Agent.** ToT demonstrates that the model's reasoning process can and should be scaffolded by a harness-level search mechanism. The tree exploration, evaluation, and backtracking are all harness functions (part of the Planning/Execution Loop). The model generates candidates; the harness manages the search tree. This separation of generation (model) from search (harness) is a direct example of the harness theory.

---

### B6. HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face

| Field | Value |
|-------|-------|
| **Authors** | Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, Yueting Zhuang |
| **Title** | HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face |
| **Date** | 2023-03-30 (arXiv v1) / 2023 (NeurIPS) |
| **Source** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2303.17580 |
| **Status** | ✅ CCF-A conference |

**Abstract.** We present HuggingGPT, an LLM-powered agent that leverages ChatGPT as a task planner to connect with numerous AI models on Hugging Face to solve complex AI tasks. The system operates in four stages: (1) Task Planning — ChatGPT parses user requests into structured subtasks; (2) Model Selection — selects appropriate expert models from Hugging Face; (3) Task Execution — runs each model and collects results; (4) Response Generation — synthesizes results into a coherent response. This showcases how LLMs can serve as a "controller" for a heterogeneous ecosystem of AI capabilities.

**Relevance to LLM + Harness = Agent.** HuggingGPT is an early and influential demonstration of the harness-as-orchestrator pattern. The LLM is treated as a planner/controller (the "Brain") while model selection, execution, and result integration are handled by the system. This is exactly the harness architecture: the harness (not the model) manages the tool registry, execution lifecycle, and response composition.

---

### B7. AgentBench: Evaluating LLMs as Agents

| Field | Value |
|-------|-------|
| **Authors** | Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu et al. |
| **Title** | AgentBench: Evaluating LLMs as Agents |
| **Date** | 2023-08-07 (arXiv v1) / 2024 (ICLR) |
| **Source** | International Conference on Learning Representations (ICLR), 2024 |
| **arXiv** | 2308.03688 |
| **Status** | ✅ CCF-A conference |

**Abstract.** We introduce AgentBench, a comprehensive benchmark to standardize the evaluation of LLMs as agents. It defines eight distinct evaluation environments covering operating system, web browsing, database, knowledge graph, card game, house-holding, and other interactive tasks. Using AgentBench, we conduct a large-scale evaluation of 25 LLMs and reveal a significant gap between top-performing models (like GPT-4) and open-source alternatives in agent tasks, even when they perform comparably on static NLP benchmarks. The benchmark provides a standardized infrastructure for assessing agent capabilities.

**Relevance to LLM + Harness = Agent.** AgentBench is critical to the harness thesis because it provides the V (Evaluation Interface) component of the harness model. More importantly, the finding that "LLM ranking on agent tasks differs from ranking on static tasks" demonstrates that agent performance is not solely a function of model quality — the environment, task framing, and interaction protocol (all harness-level factors) significantly influence outcomes. The HAL (Harness-Aware Leaderboard) work at ICLR 2026 extends this insight by showing many "model failures" are actually harness failures.

---

## C. Agent Frameworks and Tools

Systems that implement key aspects of the harness architecture.

---

### C1. ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs

| Field | Value |
|-------|-------|
| **Authors** | Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu et al. (Tsinghua University) |
| **Title** | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs |
| **Date** | 2023-07-31 (arXiv v1) / 2024 (ICLR) |
| **Source** | International Conference on Learning Representations (ICLR), 2024 |
| **arXiv** | 2307.16789 |
| **Status** | ✅ CCF-A conference |

**Abstract.** We introduce ToolLLM, a framework that enables LLMs to master 16,000+ real-world APIs from RapidAPI. The system comprises: (1) ToolBench, an instruction-tuning dataset automatically constructed using ChatGPT; (2) ToolEval, an automatic evaluator using depth-first search-based decision-making; (3) a model fine-tuned on ToolBench data. ToolLLM achieves strong performance on complex tool-use tasks requiring multi-step planning and API composition, demonstrating that a capable tool-use agent can be built through instruction tuning on diverse API tasks.

**Relevance to LLM + Harness = Agent.** ToolLLM directly addresses the T (Tool Registry) component of the harness model. The key finding — that managing 16,000+ APIs requires dedicated infrastructure (retrieval, planning, evaluation) beyond the model itself — reinforces the harness thesis. The ToolEval component is a V (Evaluation Interface) implementation. The paper shows that scaling tool quantity requires harness-level solutions.

---

### C2. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework

| Field | Value |
|-------|-------|
| **Authors** | Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang et al. |
| **Title** | MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework |
| **Date** | 2023-08-01 (arXiv v1) / 2024 (ICLR Oral) |
| **Source** | International Conference on Learning Representations (ICLR), 2024 (Oral) |
| **arXiv** | 2308.00352 |
| **Status** | ✅ CCF-A conference (Oral) |

**Abstract.** MetaGPT encodes human software development SOPs into multi-agent collaboration. It assigns different roles to GPT-based agents (product manager, architect, engineer, QA) and structures their communication via a shared message pool and documentation stream. This meta-programming approach enables agents to produce coherent deliverables (PRDs, design docs, code) that respect the conventions of real-world software development. MetaGPT achieves state-of-the-art performance on code generation benchmarks, showing that structured role-based collaboration significantly outperforms single-agent approaches.

**Relevance to LLM + Harness = Agent.** MetaGPT is a harness system built on top of GPT models. Its role assignment, SOP encoding, and documentation stream are all harness-level constructs that manage the agent collaboration. The key result — structured collaboration outperforms stronger single models — directly supports the harness thesis: how you orchestrate agents (the harness) matters more than which model powers them.

---

### C3. OpenHands: An Open Platform for AI Software Engineers

| Field | Value |
|-------|-------|
| **Authors** | Xingyao Wang, Boxuan Li, Yufan Song, Frank F. Xu et al. |
| **Title** | OpenHands: An Open Platform for AI Software Engineers |
| **Date** | 2024-07-23 (arXiv v1) / 2025 (ICLR) |
| **Source** | International Conference on Learning Representations (ICLR), 2025 |
| **arXiv** | 2407.16741 |
| **Status** | ✅ CCF-A conference |

**Abstract.** OpenHands (formerly OpenCodeInterpreter) is an open platform for building AI software engineers. It provides a unified framework for agent-environment interaction with sandboxed execution, tool integration, and trajectory management. The platform supports multiple agent implementations including CodeAct, which uses executable code as the primary action space. OpenHands achieves competitive results on SWE-bench and other coding benchmarks while being fully open-source, enabling reproducible research on agent architectures.

**Relevance to LLM + Harness = Agent.** OpenHands is a production-grade reference implementation of the harness model. Its architecture explicitly separates: Execution Loop (turn management), Tool Registry (tool integration), Context Manager (trajectory management), State Store (session persistence), and Lifecycle Hooks (sandbox, permissions). The CodeAct paradigm — using code as the action language — is a harness-level design decision that empirically outperforms discrete tool calls.

---

## D. Memory and Context Management

The harness components that address attention dilution and cross-session knowledge.

---

### D1. A Survey on the Memory Mechanism of Large Language Model Based Agents

| Field | Value |
|-------|-------|
| **Authors** | Zeyu Zhang, Quanyu Dai, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Jieming Zhu, Zhenhua Dong, Ji-Rong Wen |
| **Title** | A Survey on the Memory Mechanism of Large Language Model Based Agents |
| **Date** | 2024-04-21 (arXiv v1) / 2025-07 (ACM TOIS) |
| **Source** | ACM Transactions on Information Systems (TOIS), Vol. 43(6), 2025 |
| **DOI** | 10.1145/3748302 |
| **arXiv** | 2404.13501 |
| **Status** | ✅ SCI-indexed (CCF-A journal) |

**Abstract.** Memory is a crucial component in LLM-based agents, enabling them to retain and utilize past experiences, knowledge, and skills across interactions. This survey provides a systematic review of memory mechanisms from three perspectives: (1) memory structures — including sensory, short-term, long-term, episodic, and procedural memory; (2) memory operations — storage, retrieval, consolidation, forgetting; (3) memory integration patterns — how memory modules interact with the LLM core. The survey covers over 100 papers and identifies key challenges including memory efficiency, retrieval accuracy, and the trade-off between memory capacity and noise.

**Relevance to LLM + Harness = Agent.** This survey directly addresses the Memory (S — State Store) component of the harness model. Its key finding — that memory structure and retrieval mechanisms significantly impact agent performance independently of the underlying LLM — directly supports the harness thesis. The concept of "memory as infrastructure" rather than "memory as model capability" aligns perfectly with the harness approach.

---

### D2. MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent

| Field | Value |
|-------|-------|
| **Authors** | Guangming Yu, Zhaoye Chen, Jiajun Zhang et al. |
| **Title** | MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent |
| **Date** | 2025-07-03 (arXiv v1) |
| **Source** | arXiv, 2025 |
| **arXiv** | 2507.02259 |
| **Status** | ⏳ Preprint |

**Abstract.** We propose MemAgent, a reinforcement learning-based memory management system for LLM agents. MemAgent treats context management as a Markov Decision Process, training a memory agent to decide what information to keep, compress, or discard across conversation turns. The system uses multi-conversation RL training to optimize for long-term task completion. MemAgent demonstrates significant improvements on long-context reasoning tasks compared to fixed-context-window baselines, showing that learned memory management outperforms naive concatenation approaches.

**Relevance to LLM + Harness = Agent.** MemAgent directly addresses the attention dilution problem identified in the harness theory. Its core insight — context management is a separate optimization problem that should be solved by a dedicated mechanism, not left to the LLM's raw context window — is a pure harness contribution. The paper provides empirical evidence that a learned C (Context Manager) component in the harness model is superior to relying on the model's native context window.

---

## E. Scientific Applications

Real-world deployments that demonstrate the harness theory in action.

---

### E1. Autonomous Chemical Research with Large Language Models (Coscientist)

| Field | Value |
|-------|-------|
| **Authors** | Daniil A. Boiko, Robert MacKnight, Ben Kline, Gabe Gomes |
| **Title** | Autonomous Chemical Research with Large Language Models |
| **Date** | 2023-12-20 (Nature) |
| **Source** | Nature, Vol. 624, pp. 570–578, 2023 |
| **DOI** | 10.1038/s41586-023-06792-0 |
| **Status** | ✅ SCI top journal (Nature) |

**Abstract.** Coscientist is an AI system driven by GPT-4 that can autonomously design, plan, and execute chemical experiments. The system integrates LLM reasoning with web search, documentation retrieval, code execution, and robotic lab equipment control. In demonstrations, Coscientist successfully planned chemical syntheses, executed them using robotic instruments, and even discovered unexpected catalytic reactions — all with minimal human intervention. The system shows that LLMs, when properly integrated into a scientific workflow, can accelerate experimental research.

**Relevance to LLM + Harness = Agent.** Coscientist is arguably the most impactful real-world demonstration of the harness thesis. The LLM (GPT-4) alone could not perform chemistry — the harness (web search, code execution, robotic control, safety verification) is what makes it a functional scientist. The paper shows that the value of an agent is determined by the breadth and reliability of its harness, not just the intelligence of its model.

---

### E2. Augmenting Large Language Models with Chemistry Tools (ChemCrow)

| Field | Value |
|-------|-------|
| **Authors** | Andres M. Bran, Sam Cox, Oliver Schilter, Carlo Baldassari, Andrew D. White, Philippe Schwaller |
| **Title** | Augmenting Large Language Models with Chemistry Tools |
| **Date** | 2024-05-20 (Nat. Mach. Intell.) |
| **Source** | Nature Machine Intelligence, Vol. 6, pp. 525–535, 2024 |
| **DOI** | 10.1038/s42256-024-00832-8 |
| **arXiv** | 2304.05376 |
| **Status** | ✅ SCI top journal (Nature Machine Intelligence) |

**Abstract.** We introduce ChemCrow, an LLM chemistry agent augmented with 18 expert-designed chemistry tools. ChemCrow uses GPT-4 as its reasoning engine and integrates tools including molecule search, reaction prediction, synthesis planning, and property calculation. Through a ReAct-style reasoning loop, ChemCrow autonomously completes diverse chemistry tasks from literature search to experimental design. Evaluations show that ChemCrow significantly outperforms both unaugmented GPT-4 and human experts on complex chemistry tasks requiring multi-step reasoning and tool composition.

**Relevance to LLM + Harness = Agent.** ChemCrow provides clean empirical evidence that the same LLM (GPT-4) shows dramatically different capabilities depending on whether it has access to a tool harness. Unaided GPT-4 fails on complex chemistry tasks; GPT-4 + ChemCrow harness succeeds. This is the most direct demonstration of the harness thesis: the model is a constant; the harness determines whether the system is capable.

---

> **Recommended reading order for harness theory researchers:**
> 1. A1 (Agent Harness Survey) — the direct theoretical statement
> 2. A3 + A4 (the two major surveys) — the broad landscape
> 3. B1 (ReAct) — the foundational loop mechanism
> 4. B2 (Generative Agents) — memory + planning architecture
> 5. E1 + E2 — real-world proof
> 6. A2 (AIOS) — the OS metaphor
> 7. D1 + D2 — deep dive on memory/context
> 8. C1-C3 — harness implementations

---

## F. Latest Harness Engineering Works (2026)

Papers published in 2026 that further develop the harness concept.

---

### F0. Agent Harness Engineering: A Survey

| Field | Value |
|-------|-------|
| **Authors** | Junjie Li, Xi Xiao, Yunbei Zhang, Chen Liu, Lin Zhao et al. (20 authors, multi-institution) |
| **Title** | Agent Harness Engineering: A Survey |
| **Date** | 2026-05-16 |
| **Source** | Submitted to TMLR (Transactions on Machine Learning Research) |
| **PDF** | https://picrew.github.io/LLM-Harness/main.pdf |
| **GitHub** | https://github.com/Picrew/awesome-agent-harness |
| **Status** | ⏳ Under review |

**Abstract.** This survey establishes agent harness engineering as an independent system layer and proposes the **ETCLOVG seven-layer taxonomy**: Execution, Tooling, Context, Lifecycle, Orchestration, Verification, Governance. Organized around three claims: (1) the agent harness is the independent infrastructure layer between the model and the real world; (2) harness engineering demands multi-dimensional design and system-level thinking; (3) harness quality determines system reliability and scalability, often outweighing model choice. Includes a companion catalog of 20+ open-source agent harness projects.

**Relevance to LLM + Harness = Agent.** The most comprehensive engineering-focused harness survey to date. ETCLOVG provides finer granularity than the six-component model in A1. Complements A1: A1 focuses on theory, F0 on engineering practice.

---

### F1. Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems

| Field | Value |
|-------|-------|
| **Authors** | Xuying Ning, Katherine Tieu, Dongqi Fu, Tianxin Wei, Zihao Li et al. (44 authors, multi-institution) |
| **Title** | Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems |
| **Date** | 2026-05-18 |
| **Source** | arXiv:2605.18747 |
| **PDF** | https://arxiv.org/pdf/2605.18747 |
| **GitHub** | https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers |
| **Status** | ⏳ Preprint |

**Abstract.** Recent LLMs have demonstrated strong capabilities in understanding and generating code. In emerging agentic systems, code is no longer only a target output — it increasingly serves as an operational substrate for agent reasoning, acting, environment modeling, and execution-based verification. This survey frames this shift through the lens of agent harnesses and introduces "code as agent harness." Organized around three layers: (1) harness interface — code connecting agents to reasoning, action, and environment; (2) harness mechanisms — planning, memory, tool use with feedback-driven control; (3) scaling the harness from single to multi-agent systems. Covers coding assistants, GUI/OS automation, embodied agents, scientific discovery, DevOps, and enterprise workflows.

**Relevance to LLM + Harness = Agent.** Introduces a novel perspective: code itself can be the harness. Unifies CodeAct, OpenHands, and other code-centric systems under the "code as harness" framework, arguing why code as a unified action space is superior to discrete tool calls. The identified challenges — evaluation, verification, shared state, human oversight — align directly with harness theory concerns.
