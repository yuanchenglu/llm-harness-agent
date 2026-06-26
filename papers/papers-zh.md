# LLM + Harness = Agent：论文数据库（简体中文版）

> 核心命题：Agent = Model × Harness × Environment × Evidence
> Harness（装备层）= { 执行循环, 工具注册表, 上下文管理器, 状态存储, 生命周期钩子, 评估接口 }

本数据库收录与 **LLM + Harness = Agent** 命题直接相关的高质量学术论文，涵盖 SCI 期刊、CCF-A/B 类顶会以及同等影响力的预印本。每篇条目包含完整引用信息、摘要（据原文综合提炼）、核心贡献，以及与装备层理论的关联分析。

---

## A 类：装备层核心理论

直接论述"模型之外的系统"作为一等架构对象的论文。

---

### A1. Agent Harness for Large Language Model Agents: A Survey
**Agent 装备层综述：大语言模型智能体的执行基础设施**

| 字段 | 内容 |
|-------|-------|
| **作者** | Qianyu Meng, Yanan Wang, Liyi Chen 等 |
| **标题** | Agent Harness for Large Language Model Agents: A Survey |
| **日期** | 2026-04-07 (v1) |
| **出处** | Preprints.org, 2026 (v3，尚未同行评审) |
| **链接** | https://www.preprints.org/manuscript/202604.0428 |
| **状态** | 预印本 |

**摘要（原文综合提炼）。** 大语言模型智能体在生产环境中的可靠性取决于 agent 执行装备层（harness）而非模型本身。本综述将装备层形式化为六元组 H = (E, T, C, S, L, V)：执行循环、工具注册表、上下文管理器、状态存储、生命周期钩子、评估接口。它调研了 23 个系统并归入 6 个类别，指出现有生态存在"模块化鸿沟"，并记录了 9 个紧密耦合的技术挑战，包括安全与沙箱、评估、协议标准化和记忆治理。核心证据：仅修改装备层（不改变模型）即可在编程基准上获得高达 10 倍的提升，在 TerminalBench 上提升 26%，在数学推理上提升 4.7 个百分点。

**与 LLM + Harness = Agent 的关联。** 这是与当前命题最直接相关的论文。它将"装备层"形式化为一等概念，给出了具体的六组件定义，并汇集了"装备层改进主导模型改进"的实证证据。该综述明确将 Hermes Agent、OpenClaw、AIOS 和 OpenHands 列为全栈装备层实例。

---

### A2. AIOS: LLM Agent Operating System
**AIOS：大语言模型智能体操作系统**

| 字段 | 内容 |
|-------|-------|
| **作者** | Kai Mei, Xi Zhu, Wujiang Xu, Mingyu Jin 等（Rutgers University） |
| **标题** | AIOS: LLM Agent Operating System |
| **日期** | 2024-03-25 (arXiv v1) / 2025 (COLM) |
| **出处** | Conference on Language Modeling (COLM), 2025 |
| **arXiv** | https://arxiv.org/abs/2403.16971 |
| **状态** | ✅ COLM 2025 长文 |

**摘要。** 本文提出 AIOS，一个将大语言模型嵌入操作系统作为 OS "大脑"的智能体操作系统。AIOS 解决 LLM 智能体部署中的关键挑战：上下文调度、并发智能体管理、工具编排和资源分配。它提出了一种将 LLM 与智能体执行基础设施分离的模块化架构，使多个智能体可以共享同一 LLM 后端同时保持隔离和状态。系统将 Agent 调度器、上下文管理器、记忆管理器和工具管理器作为 OS 的一等模块引入。

**与 LLM + Harness = Agent 的关联。** AIOS 是"操作系统比喻"最明确的实现。它将 LLM 类比为 CPU，并围绕它构建操作系统——与 DeepSeek Agent 理论总纲中的 CPU/OS 类比完全一致。其模块化架构（调度器、上下文管理器、记忆管理器、工具管理器）直接映射到装备层理论的各组件。

---

### A3. A Survey on Large Language Model Based Autonomous Agents
**基于大语言模型的自主智能体综述**

| 字段 | 内容 |
|-------|-------|
| **作者** | Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang 等（中国人民大学） |
| **标题** | A Survey on Large Language Model Based Autonomous Agents |
| **日期** | 2023-08-22 (arXiv v1) / 2024-03 (Front. Comput. Sci.) |
| **出处** | Frontiers of Computer Science (Springer Nature), Vol. 18, Article 186345, 2024 |
| **DOI** | 10.1007/s11704-024-40231-1 |
| **arXiv** | 2308.11432 |
| **状态** | ✅ SCI 期刊，开放获取 |

**摘要。** 自主智能体一直是学术界和工业界的重要研究焦点。此前的研究往往在孤立环境中训练知识有限的智能体，这与人类学习过程存在显著差异，致使智能体难以做出类人决策。近期，通过获取海量网络知识，大语言模型在实现人类水平智能方面展现出显著潜力，这激发了针对 LLM 自主智能体的研究热潮。本综述从整体视角进行了系统性梳理：（1）讨论 LLM 自主智能体的构建，提出了涵盖大脑（LLM）、记忆、规划和行动的统一框架；（2）全面概述其在社会科学、自然科学和工程领域的多样化应用；（3）深入探讨评估策略；（4）提出挑战和未来方向。

**与 LLM + Harness = Agent 的关联。** 该综述提出的统一框架明确将智能体视为超越模型本身的存在——它明确将记忆、规划和工具使用与 LLM "大脑"并列。这一框架是"模型单独不足，周围架构（装备层）同样关键"这一概念的学术基础。引用量超过 1,500 次，是该领域最有影响力的综述。

---

### A4. The Rise and Potential of Large Language Model Based Agents: A Survey
**基于大语言模型的智能体的崛起与潜力：综述**

| 字段 | 内容 |
|-------|-------|
| **作者** | Zhiheng Xi, Wenxiang Chen, Xin Guo 等（29 位作者，复旦大学 NLP 组） |
| **标题** | The Rise and Potential of Large Language Model Based Agents: A Survey |
| **日期** | 2023-09-14 (arXiv v1) / 2025-01 (Sci. China Inf. Sci.) |
| **出处** | Science China Information Sciences, Vol. 68(2), 2025 |
| **DOI** | 10.1007/s11432-024-4222-0 |
| **arXiv** | 2309.07864 |
| **状态** | ✅ SCI 期刊（CCF-A 中文顶刊），86 页 |

**摘要。** 长期以来，人类一直在追求与人类水平相当或超越人类的通用人工智能，而 AI 智能体被视为实现这一目标的有希望的载体。大语言模型凭借其展现的多样化能力，被视为 AGI 的火花，为构建通用 AI 智能体带来了希望。本综述提出了一个基于 Brain（大脑，即 LLM 本身，负责推理和规划）、Perception（感知，通过文本、视觉、听觉多模态感知环境）、Action（行动，通过工具调用、API、物理动作执行决策）三模块的统一框架，并回顾了单智能体、多智能体和人与智能体协作三类场景中的应用。

**与 LLM + Harness = Agent 的关联。** "大脑、感知、行动"框架与装备层理论的关注点分离原则直接对应。大脑是模型，但感知和行动是连接模型与真实世界的装备层能力。86 页的篇幅使其成为目前最全面的综述。

---

### A5. A Survey on LLM-based Multi-Agent Systems: Workflow, Infrastructure, and Challenges
**基于 LLM 的多智能体系统综述：工作流、基础设施与挑战**

| 字段 | 内容 |
|-------|-------|
| **作者** | Xinyi Li, Sai Wang, Siqi Zeng, Yu Wu, Yi Yang |
| **标题** | A Survey on LLM-based Multi-Agent Systems: Workflow, Infrastructure, and Challenges |
| **日期** | 2024-10-08 |
| **出处** | Vicinagearth, Vol. 1(1), 2024 |
| **DOI** | 10.1007/s44336-024-00009-2 |
| **状态** | ✅ 同行评议期刊 |

**摘要。** 本文对基于 LLM 的多智能体系统进行了全面综述，系统梳理了其工作流、基础设施和挑战。涵盖智能体通信协议、协作机制、任务分解策略以及多智能体部署所需的基础设施支持。综述指出了当前系统的关键不足，特别是状态管理、智能体间记忆共享和评估标准化方面。

**与 LLM + Harness = Agent 的关联。** 多智能体系统是对装备层概念最严苛的测试场景：当多个智能体协作时，基础设施（通信协议、共享状态、隔离保障、编排机制）完全决定了系统的可靠性。该综述对基础设施和工作流的关注直接支持了"装备层质量而非模型质量是限制因素"的论点。

---

## B 类：奠基性工作

奠定了现代 LLM 智能体核心范式的里程碑论文——每篇都是现代装备层的必要组成部分。

---

### B1. ReAct: Synergizing Reasoning and Acting in Language Models
**ReAct：在语言模型中协同推理与行动**

| 字段 | 内容 |
|-------|-------|
| **作者** | Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao |
| **标题** | ReAct: Synergizing Reasoning and Acting in Language Models |
| **日期** | 2022-10-06 (arXiv v1) / 2023 (ICLR) |
| **出处** | International Conference on Learning Representations (ICLR), 2023 |
| **arXiv** | 2210.03629 |
| **状态** | ✅ CCF-A 会议，引用量 11,000+ |

**摘要。** 虽然大语言模型在推理和零样本泛化任务中展现了令人印象深刻的能力，但它们仍然依赖静态的单轮交互。我们提出 ReAct 范式——一种通用框架，让 LLM 在统一循环中将推理轨迹（思考）与任务特定动作（工具调用、环境交互）交织在一起。这将推理和行动的互补优势协同起来：推理指导行动选择，行动结果反过来指导后续推理。在问答、事实验证和交互式决策等多样化基准上，ReAct 均优于基线方法，同时提高了人类的可解释性和可信度。

**与 LLM + Harness = Agent 的关联。** ReAct 是"LM + 行动 = Agent"概念的奠基性论文。它证明驱动智能体行为的关键不是更好的模型，而是一种将推理与行动交织在一起的循环结构。这个循环——装备层模型中的 E（执行循环）组件——是装备层中最重要的机制，而 ReAct 是第一个将其形式化的论文。每个现代智能体装备层（包括 Claude Code、Codex、Hermes、OpenHands）都实现了 ReAct 循环的变体。

---

### B2. Generative Agents: Interactive Simulacra of Human Behavior
**生成式智能体：人类行为的交互式仿真**

| 字段 | 内容 |
|-------|-------|
| **作者** | Joon Sung Park, Joseph O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, Michael S. Bernstein（Stanford） |
| **标题** | Generative Agents: Interactive Simulacra of Human Behavior |
| **日期** | 2023-04-07 (arXiv v1) / 2023-10 (UIST) |
| **出处** | ACM Symposium on User Interface Software and Technology (UIST), 2023 |
| **arXiv** | 2304.03442 |
| **DOI** | 10.1145/3586183.3606763 |
| **状态** | ✅ CCF-A 会议（ACM），极高引用量 |

**摘要。** 可信的人类行为代理可以赋能从沉浸式环境到人际技能排练空间再到原型设计工具的交互式应用。在本文中，我们引入生成式智能体——能够模拟可信人类行为的计算软件智能体。生成式智能体会起床、做早餐、去上班；艺术家画画，作家写作；它们形成观点、彼此注意、发起对话；它们记住并反思过去的日子，同时规划第二天。为了实现这些行为，我们描述了一种在 LLM 之外扩展了记忆、规划和反思机制的智能体架构。我们实例化此架构以填充沙箱环境，终端用户可以用自然语言与一个 25 个生成式智能体的小镇交互。

**与 LLM + Harness = Agent 的关联。** 生成式智能体是开创性的证明：仅有 LLM 不足以实现可信的智能体行为。它的架构在 LLM 周围明确添加了记忆（长期流+检索）、规划（每日计划+反思）和社交意识作为装备层组件。该论文的架构直接启发了 Hermes 等现代装备层中的记忆和技能层。"智能体可信度取决于架构而非模型"这一发现是装备层理论的核心。

---

### B3. Toolformer: Language Models Can Teach Themselves to Use Tools
**Toolformer：语言模型可以自学使用工具**

| 字段 | 内容 |
|-------|-------|
| **作者** | Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom（Meta AI） |
| **标题** | Toolformer: Language Models Can Teach Themselves to Use Tools |
| **日期** | 2023-02-09 (arXiv v1) / 2023 (NeurIPS) |
| **出处** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2302.04761 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** 语言模型在仅凭少量示例或简单指令解决新任务方面表现出色，但在需要复杂计算、事实知识或外部信息的任务上力不从心。我们引入 Toolformer，一个经过训练以自主决定调用哪些 API、何时调用、传什么参数以及如何将结果融入后续 token 预测的模型。这是以自监督方式完成的——模型通过学习将 API 调用嵌入文本来自学使用工具。得到的模型在多种下游任务上取得了显著改进的零样本性能，通常与更大的模型竞争，且不牺牲核心语言建模能力。

**与 LLM + Harness = Agent 的关联。** Toolformer 建立了关键认知：工具使用能力（装备层模型中的 T——工具注册表组件）应该且可以被构建为模型前向传播之外的结构化能力。核心见解：工具调用不是模型能力，而是装备层协议。模型提议工具调用，但装备层必须解析、执行和整合结果。这种关注点分离正是装备层哲学。

---

### B4. Reflexion: Language Agents with Verbal Reinforcement Learning
**Reflexion：具备语言化强化学习的语言智能体**

| 字段 | 内容 |
|-------|-------|
| **作者** | Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao |
| **标题** | Reflexion: Language Agents with Verbal Reinforcement Learning |
| **日期** | 2023-03-20 (arXiv v1) / 2023 (NeurIPS) |
| **出处** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2303.11366 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** 我们引入 Reflexion，一种通过从先前错误中学习来强化语言智能体的框架。智能体获取"反思"——对哪里出错以及如何改进的文字总结——存储在情景记忆中，并在后续尝试中注入智能体的上下文。这种语言化强化比传统的强化学习方法更灵活、样本效率更高。在决策、编程和推理等多种任务中，Reflexion 通过使智能体在不更新权重的情况下进行自我修正，显著提升了性能。

**与 LLM + Harness = Agent 的关联。** Reflexion 是纯粹的装备层创新：它根据过往执行结果修改进入上下文窗口的信息，而不需要对模型进行任何重训练。该论文证明在智能体上添加反思+记忆循环即可产生巨大收益——这完全是通过装备层变化实现的。这正是装备层模型中的 S（状态存储）和 C（上下文管理器）组件在发挥作用。

---

### B5. Tree of Thoughts: Deliberate Problem Solving with Large Language Models
**思维树：利用大语言模型进行深思熟虑的问题求解**

| 字段 | 内容 |
|-------|-------|
| **作者** | Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Tom Griffiths, Yuan Cao, Karthik Narasimhan |
| **标题** | Tree of Thoughts: Deliberate Problem Solving with Large Language Models |
| **日期** | 2023-05-06 (arXiv v1) / 2023 (NeurIPS) |
| **出处** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2305.10601 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** 语言模型越来越多地被用于需要规划和探索的任务。然而，标准自回归生成范式——从左到右、一次一个 token——限制了深思熟虑的决策。我们引入思维树（ToT），一种泛化思维链提示的框架，允许 LM 同时探索多个推理路径。ToT 使 LM 能够进行战略性前瞻、回溯和深思熟虑的搜索。在三个新任务的实验表明，ToT 显著增强了 LM 的问题解决能力。

**与 LLM + Harness = Agent 的关联。** ToT 证明模型的推理过程可以由装备层搜索机制来构建。树探索、评估和回溯都是装备层功能（属于规划/执行循环）。模型生成候选方案；装备层管理搜索树。这种将生成（模型）与搜索（装备层）分离的做法是装备层理论的一个直接实例。

---

### B6. HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face
**HuggingGPT：用 ChatGPT 及其 Hugging Face 伙伴解决 AI 任务**

| 字段 | 内容 |
|-------|-------|
| **作者** | Yongliang Shen, Kaitao Song, Xu Tan, Dongsheng Li, Weiming Lu, Yueting Zhuang（Microsoft） |
| **标题** | HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face |
| **日期** | 2023-03-30 (arXiv v1) / 2023 (NeurIPS) |
| **出处** | Advances in Neural Information Processing Systems (NeurIPS), 2023 |
| **arXiv** | 2303.17580 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** 我们提出 HuggingGPT，一个由 LLM 驱动的智能体，它利用 ChatGPT 作为任务规划器，连接 Hugging Face 上的众多 AI 模型来解决复杂的 AI 任务。系统分四个阶段运行：(1) 任务规划——ChatGPT 将用户请求解析为结构化的子任务；(2) 模型选择——从 Hugging Face 选择合适的专家模型；(3) 任务执行——运行每个模型并收集结果；(4) 响应生成——将结果综合成连贯响应。这展示了 LLM 如何充当异构 AI 能力生态系统的"控制器"。

**与 LLM + Harness = Agent 的关联。** HuggingGPT 是装备层即编排器模式的早期且影响深远的示例。LLM 被当作规划器/控制器（"大脑"），而模型选择、执行和结果整合由系统处理。这正是装备层架构：装备层（而非模型）管理工作注册表、执行生命周期和响应组合。

---

### B7. AgentBench: Evaluating LLMs as Agents
**AgentBench：评估作为智能体的 LLM**

| 字段 | 内容 |
|-------|-------|
| **作者** | Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu 等（清华大学） |
| **标题** | AgentBench: Evaluating LLMs as Agents |
| **日期** | 2023-08-07 (arXiv v1) / 2024 (ICLR) |
| **出处** | International Conference on Learning Representations (ICLR), 2024 |
| **arXiv** | 2308.03688 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** 我们提出 AgentBench，一个将 LLM 作为智能体进行评估的综合性基准。它定义了八个不同的评估环境，涵盖操作系统、网页浏览、数据库、知识图谱、卡牌游戏、家居任务等交互式场景。利用 AgentBench，我们对 25 个 LLM 进行了大规模评估，揭示了领先模型（如 GPT-4）与开源替代品在智能体任务中的显著差距——即使它们在静态 NLP 基准上表现相当。该基准为评估智能体能力提供了标准化基础设施。

**与 LLM + Harness = Agent 的关联。** AgentBench 对装备层理论至关重要，因为它提供了装备层模型的 V（评估接口）组件。更重要的是，"LLM 在智能体任务上的排名与在静态任务上的排名不同"这一发现证明了智能体性能不仅仅是模型质量的函数——环境、任务框架和交互协议（均为装备层因素）显著影响结果。ICLR 2026 的 HAL（装备层感知排行榜）工作将此洞察进一步深化，显示许多"模型失败"实际上是装备层失败。

---

## C 类：Agent 框架与工具

实现了装备层架构关键方面的系统。

---

### C1. ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs
**ToolLLM：让大语言模型掌握 16,000+ 真实世界 API**

| 字段 | 内容 |
|-------|-------|
| **作者** | Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu 等（清华大学） |
| **标题** | ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs |
| **日期** | 2023-07-31 (arXiv v1) / 2024 (ICLR) |
| **出处** | International Conference on Learning Representations (ICLR), 2024 |
| **arXiv** | 2307.16789 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** 我们引入 ToolLLM，一个使 LLM 能够掌握 RapidAPI 上 16,000+ 真实世界 API 的框架。系统包括：(1) ToolBench，一个使用 ChatGPT 自动构建的指令微调数据集；(2) ToolEval，一个基于深度优先搜索决策的自动评估器；(3) 在 ToolBench 数据上微调的模型。ToolLLM 在需要多步规划和 API 组合的复杂工具使用任务上取得了强大性能，证明通过指令微调可以在多样化 API 任务上构建有能力的工具使用智能体。

**与 LLM + Harness = Agent 的关联。** ToolLLM 直接解决装备层模型的 T（工具注册表）组件。关键发现——管理 16,000+ API 需要模型之外的专用基础设施（检索、规划、评估）——强化了装备层论点。ToolEval 组件是一个 V（评估接口）实现。论文表明，工具数量扩展需要装备层解决方案。

---

### C2. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework
**MetaGPT：面向多智能体协作框架的元编程**

| 字段 | 内容 |
|-------|-------|
| **作者** | Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang 等 |
| **标题** | MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework |
| **日期** | 2023-08-01 (arXiv v1) / 2024 (ICLR Oral) |
| **出处** | International Conference on Learning Representations (ICLR), 2024 (Oral) |
| **arXiv** | 2308.00352 |
| **状态** | ✅ CCF-A 会议（Oral 亮点论文） |

**摘要。** MetaGPT 将人类软件工程标准操作程序（SOP）编码为多智能体协作。它为不同的 GPT 智能体分配不同角色（产品经理、架构师、工程师、QA），并通过共享消息池和文档流结构化其通信。这种元编程方法使智能体能够生成遵循真实软件开发规范的连贯交付物（PRD、设计文档、代码）。MetaGPT 在代码生成基准上取得了顶尖性能，表明结构化基于角色的协作显著优于单智能体方法。

**与 LLM + Harness = Agent 的关联。** MetaGPT 是构建在 GPT 模型之上的装备层系统。其角色分配、SOP 编码和文档流都是管理智能体协作的装备层构造。关键结果——结构化协作优于更强的单模型——直接支持装备层论点：如何编排智能体（装备层）比使用哪个模型更重要。

---

### C3. OpenHands: An Open Platform for AI Software Engineers
**OpenHands：AI 软件工程师的开放平台**

| 字段 | 内容 |
|-------|-------|
| **作者** | Xingyao Wang, Boxuan Li, Yufan Song, Frank F. Xu 等 |
| **标题** | OpenHands: An Open Platform for AI Software Engineers |
| **日期** | 2024-07-23 (arXiv v1) / 2025 (ICLR) |
| **出处** | International Conference on Learning Representations (ICLR), 2025 |
| **arXiv** | 2407.16741 |
| **状态** | ✅ CCF-A 会议 |

**摘要。** OpenHands（前身为 OpenCodeInterpreter）是一个用于构建 AI 软件工程师的开放平台。它提供了一个统一的智能体-环境交互框架，具备沙箱执行、工具集成和轨迹管理功能。该平台支持多种智能体实现，包括使用可执行代码作为主要动作空间的 CodeAct。OpenHands 在 SWE-bench 和其他编程基准上取得了有竞争力的结果，同时完全开源，使智能体架构的研究可复现。

**与 LLM + Harness = Agent 的关联。** OpenHands 是装备层模型的生产级参考实现。其架构明确分离了：执行循环（对话管理）、工具注册表（工具集成）、上下文管理器（轨迹管理）、状态存储（会话持久化）和生命周期钩子（沙箱、权限）。CodeAct 范式——使用代码作为动作语言——是一个装备层设计决策，经验证明其优于离散工具调用。

---

## D 类：记忆与上下文管理

解决注意力稀释和跨会话知识的装备层组件。

---

### D1. A Survey on the Memory Mechanism of Large Language Model Based Agents
**基于大语言模型的智能体记忆机制综述**

| 字段 | 内容 |
|-------|-------|
| **作者** | Zeyu Zhang, Quanyu Dai, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Jieming Zhu, Zhenhua Dong, Ji-Rong Wen |
| **标题** | A Survey on the Memory Mechanism of Large Language Model Based Agents |
| **日期** | 2024-04-21 (arXiv v1) / 2025-07 (ACM TOIS) |
| **出处** | ACM Transactions on Information Systems (TOIS), Vol. 43(6), 2025 |
| **DOI** | 10.1145/3748302 |
| **arXiv** | 2404.13501 |
| **状态** | ✅ SCI 期刊（CCF-A 顶刊） |

**摘要。** 记忆是 LLM 智能体的关键组件，使其能够跨交互保留和利用过往经验、知识和技能。本综述从三个视角系统梳理了记忆机制：(1) 记忆结构——包括感觉记忆、短时记忆、长时记忆、情景记忆和程序性记忆；(2) 记忆操作——存储、检索、巩固、遗忘；(3) 记忆整合模式——记忆模块如何与 LLM 核心交互。综述涵盖 100 多篇论文，指出了关键挑战，包括记忆效率、检索精度以及记忆容量与噪音之间的权衡。

**与 LLM + Harness = Agent 的关联。** 该综述直接对应装备层模型的 S（状态存储）和 C（上下文管理器）组件。其核心发现——记忆结构和检索机制独立于底层 LLM，对智能体性能产生显著影响——直接支持装备层论点。"记忆即基础设施"而非"记忆即模型能力"的概念与装备层方法完全一致。

---

### D2. MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent
**MemAgent：用多轮强化学习记忆智能体重塑长上下文 LLM**

| 字段 | 内容 |
|-------|-------|
| **作者** | Guangming Yu, Zhaoye Chen, Jiajun Zhang 等 |
| **标题** | MemAgent: Reshaping Long-Context LLM with Multi-Conv RL-based Memory Agent |
| **日期** | 2025-07-03 (arXiv v1) |
| **出处** | arXiv, 2025 |
| **arXiv** | 2507.02259 |
| **状态** | ⏳ 预印本 |

**摘要。** 我们提出 MemAgent，一种基于强化学习的 LLM 智能体记忆管理系统。MemAgent 将上下文管理建模为马尔可夫决策过程，训练一个记忆智能体来决定跨对话轮次中保留、压缩或丢弃哪些信息。系统使用多对话 RL 训练来优化长期任务完成。与固定上下文窗口基线相比，MemAgent 在长上下文推理任务上表现出显著改进，证明学习型记忆管理优于朴素的拼接方法。

**与 LLM + Harness = Agent 的关联。** MemAgent 直接解决装备层理论中识别的注意力稀释问题。其核心洞察——上下文管理是一个独立的优化问题，应由专用机制解决，而非留给 LLM 的原始上下文窗口——是完全的装备层贡献。论文提供了经验证据表明装备层模型中学习型 C（上下文管理器）组件优于依赖模型原生上下文窗口。

---

## E 类：科学应用

证明装备层理论在实际场景中影响力的真实部署。

---

### E1. Autonomous Chemical Research with Large Language Models (Coscientist)
**基于大语言模型的自主化学研究（Coscientist）**

| 字段 | 内容 |
|-------|-------|
| **作者** | Daniil A. Boiko, Robert MacKnight, Ben Kline, Gabe Gomes（CMU） |
| **标题** | Autonomous Chemical Research with Large Language Models |
| **日期** | 2023-12-20 (Nature) |
| **出处** | Nature, Vol. 624, pp. 570–578, 2023 |
| **DOI** | 10.1038/s41586-023-06792-0 |
| **状态** | ✅ SCI 顶刊（Nature 正刊） |

**摘要。** Coscientist 是一个由 GPT-4 驱动的 AI 系统，能够自主设计、规划和执行化学实验。该系统将 LLM 推理与网络搜索、文档检索、代码执行和机器人实验设备控制集成在一起。在演示中，Coscientist 成功规划了化学合成路线，使用机器人仪器执行了实验，甚至发现了意外的催化反应——全程只需最少的人类干预。该系统表明，当 LLM 被恰当地集成到科学工作流中时，可以加速实验研究。

**与 LLM + Harness = Agent 的关联。** Coscientist 可以说是装备层论点最有影响力的现实世界证明。LLM（GPT-4）单独无法进行化学研究——装备层（网络搜索、代码执行、机器人控制、安全验证）才使其成为功能上的科学家。该论文表明，智能体的价值由其装备层的广度和可靠性决定，而非仅由其模型的智能程度决定。

---

### E2. Augmenting Large Language Models with Chemistry Tools (ChemCrow)
**用化学工具增强大语言模型（ChemCrow）**

| 字段 | 内容 |
|-------|-------|
| **作者** | Andres M. Bran, Sam Cox, Oliver Schilter, Carlo Baldassari, Andrew D. White, Philippe Schwaller（IBM） |
| **标题** | Augmenting Large Language Models with Chemistry Tools |
| **日期** | 2024-05-20 (Nat. Mach. Intell.) |
| **出处** | Nature Machine Intelligence, Vol. 6, pp. 525–535, 2024 |
| **DOI** | 10.1038/s42256-024-00832-8 |
| **arXiv** | 2304.05376 |
| **状态** | ✅ SCI 顶刊（Nature Machine Intelligence） |

**摘要。** 我们介绍 ChemCrow，一个用 18 个专家设计的化学工具增强的 LLM 化学智能体。ChemCrow 使用 GPT-4 作为其推理引擎，并集成了包括分子搜索、反应预测、合成规划和性质计算在内的工具。通过 ReAct 风格的推理循环，ChemCrow 自主完成从文献搜索到实验设计的多样化化学任务。评估表明，ChemCrow 在需要多步推理和工具组合的复杂化学任务上显著优于未增强的 GPT-4 和人类专家。

**与 LLM + Harness = Agent 的关联。** ChemCrow 提供了干净的经验证据：同一个 LLM（GPT-4）在是否拥有工具装备层的情况下展现出截然不同的能力。未辅助的 GPT-4 在复杂化学任务上失败；GPT-4 + ChemCrow 装备层则成功。这是对装备层论点最直接的证明：模型是常数；装备层决定系统是否具备能力。

---

---

## F 类：2026 年最新 Harness 工程综述

---

### F0. Agent Harness Engineering: A Survey
**Agent 装备层工程：综述**

| 字段 | 内容 |
|-------|-------|
| **作者** | Junjie Li, Xi Xiao, Yunbei Zhang, Chen Liu, Lin Zhao 等（20 位作者，多机构合作） |
| **标题** | Agent Harness Engineering: A Survey |
| **日期** | 2026-05-16 |
| **出处** | 投稿至 TMLR（Transactions on Machine Learning Research） |
| **PDF** | https://picrew.github.io/LLM-Harness/main.pdf |
| **GitHub** | https://github.com/Picrew/awesome-agent-harness |
| **状态** | ⏳ 投稿评审中 |

**摘要。** 本综述将 Agent 装备层工程确立为一个独立的系统层，提出了 **ETCLOVG 七层分类法**：执行（Execution）、工具（Tooling）、上下文（Context）、生命周期（Lifecycle）、编排（Orchestration）、验证（Verification）、治理（Governance）。文章围绕三个核心主张展开：(1) Agent 装备层是模型与真实世界之间的独立基础设施层；(2) 装备层工程需要多维度的设计和系统视角，而非零散的点状优化；(3) 装备层的质量直接决定 Agent 系统的可靠性和可扩展性，其影响往往超过模型本身的选择。综述还配套提供了一个开源 Agent 装备层项目目录，涵盖 20+ 个代表性系统。

**与 LLM + Harness = Agent 的关联。** 这是目前分类最全面的装备层工程综述。ETCLOVG 七层模型比 A1 论文的六组件更细粒地刻画了装备层的全貌。论文明确将"装备层质量决定系统可靠性"作为核心论点，提供了大最工程实践层面的证据。它与 A1（Agent Harness Survey）互为补充：A1 重理论研究，F0 重工程实践。

---

### F1. Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems
**代码即 Agent 装备层：迈向可执行、可验证、有状态的 Agent 系统**

| 字段 | 内容 |
|-------|-------|
| **作者** | Xuying Ning, Katherine Tieu, Dongqi Fu, Tianxin Wei, Zihao Li 等（44 位作者，多机构） |
| **标题** | Code as Agent Harness: Toward Executable, Verifiable, and Stateful Agent Systems |
| **日期** | 2026-05-18 |
| **出处** | arXiv:2605.18747 |
| **PDF** | https://arxiv.org/pdf/2605.18747 |
| **GitHub** | https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers |
| **状态** | ⏳ 预印本 |

**摘要。** 近年来，LLM 在理解和生成代码方面展现出强大能力，从竞赛编程到仓库级软件工程。在新的 Agent 系统中，代码不再仅仅是目标输出——它日益成为 Agent 推理、行动、环境建模和基于执行的验证的运行基座。本综述通过 Agent 装备层的视角审视这一转变，提出"代码即 Agent 装备层"的统一观点。综述围绕三个层次展开：(1) 装备层接口——代码连接 Agent 与推理、行动和环境建模；(2) 装备层机制——规划、记忆和工具使用，配合反馈驱动的控制和优化；(3) 装备层规模化——从单 Agent 到多 Agent 场景。涵盖编程助手、GUI/OS 自动化、具身智能体、科学发现等领域的应用。

**与 LLM + Harness = Agent 的关联。** 这篇综述提出了一个新颖视角：代码本身就可以是装备层。它将 CodeAct、OpenHands 等以代码为核心动作空间的系统统一在"代码即装备层"框架下，论证了为什么代码作为装备层的统一动作语言比离散工具调用更优。论文指出的核心挑战——评估、验证、共享状态、人类监督——与装备层理论的关注点完全一致。

---

> **装备层理论研究推荐阅读顺序：**
> 1. A1（Agent Harness 综述）——直接的理论陈述
> 2. A3 + A4（两篇主要综述）——广阔的全景
> 3. B1（ReAct）——基础循环机制
> 4. B2（Generative Agents）——记忆+规划架构
> 5. E1 + E2——现实世界证明
> 6. A2（AIOS）——操作系统比喻
> 7. D1 + D2——记忆/上下文深度专题
> 8. C1-C3——装备层实现案例
