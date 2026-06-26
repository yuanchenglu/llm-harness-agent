# 基于LLM的多智能体系统综述：应用的最新进展与新前沿

陈帅航¹，刘远星¹，韩伟¹，张伟男¹†，刘挺¹  
¹哈尔滨工业大学社会计算与信息检索研究中心  
{shchen, yxliu, whan, wnzhang, tliu}@ir.hit.edu.cn

## 摘要

自大型语言模型（LLM）兴起以来，基于LLM的多智能体系统（LLM-MAS）已成为研究热点。然而，随着相关新工作的不断涌现，现有的综述难以全面覆盖。本文对这些研究进行了全面的综述。我们首先讨论了LLM-MAS的定义——一个涵盖了大量先前工作的框架。我们概述了LLM-MAS在以下三个方面的各种应用：（i）解决复杂任务，（ii）模拟特定场景，以及（iii）评估生成式智能体。在以往研究的基础上，我们还强调了若干挑战并提出了该领域未来的研究方向。

## 1 引言

多智能体系统（MAS）因其适应性和解决复杂分布式挑战的能力而得到了显著的发展（Balaji and Srinivasan, 2010）。与单智能体设置相比（Gronauer and Diepold, 2022），MAS能更准确地表示现实世界，因为许多实际应用天然涉及多个决策者同时交互。然而，受限于传统的强化学习（RL）智能体参数以及通用知识和能力的缺乏，智能体无法处理复杂的决策任务，例如与其他智能体协作进行软件开发（Qian et al., 2024b）。近年来，大型语言模型（LLM），如Llama 3（Dubey et al., 2024）和GPT-4（OpenAI et al., 2024），通过在庞大的网络语料库上进行训练，取得了显著的成功（Radford et al.）。与RL相比，以LLM为核心控制智能体的生成式智能体，即便无需训练，也能在推理、长轨迹决策等方面表现更优（Shinn et al., 2023）。此外，生成式智能体提供了与人类交互的自然语言接口，使这些交互更加灵活且更易于解释（Park et al., 2023）。基于这些优势，基于LLM的多智能体系统（LLM-MAS）应运而生。研究者们对这些新兴工作进行了综述，并提出了一个通用框架（Guo et al., 2024）。然而，随着相关研究数量的持续增长，一些超出原有框架范围的工作也逐渐出现。本文在先前关于LLM-MAS综述的基础上，提供了一个新的视角，重点关注最新进展并讨论潜在的研究方向。我们收集了2023年和2024年发表在顶级人工智能会议（如*ACL、NeurIPS、AAAI和ICLR）上的125篇论文，以及一些来自arXiv的未发表但有价值的论文。¹基于LLM-MAS的目的，我们将其应用总结为任务求解、针对特定问题的模拟以及生成式智能体的评估三个方面。图1展示了我们提出的LLM-MAS应用框架。（i）**解决复杂任务**。多智能体将自然地将任务拆分为子任务，从而提升任务性能。（ii）**模拟特定场景**。研究者将LLM-MAS视为一个沙盒，用于模拟特定领域中的问题。（iii）**评估生成式智能体**。与传统的任务评估相比，LLM-MAS具有动态评估的能力，更加灵活且更难发生数据泄露。对于每个类别，我们都将讨论代表性的LLM-MAS、相关资源及其评估方法。

与先前的综述（Guo et al., 2024; Li et al., 2024d; Han et al., 2024; Gronauer and Diepold, 2022）相比，本综述具有以下独特贡献：（i）**聚焦LLM-MAS应用的分类法**：我们基于LLM-MAS的应用目的，引入了一个更新的分类法（分类法及差异如图1所示）。（ii）**更多资源**：我们分析了开源框架以及带有基准测试或数据集的研究工作，以促进研究社区的发展。（iii）**挑战与未来方向**：我们讨论了LLM-MAS面临的挑战，并展望了未来的研究方向。

¹本综述收录的论文列表可见于 https://github.com/bianhua-12/Multi-generative_Agent_System_survey

---

**图1：** LLM-MAS、生成式智能体与LLM的应用框架及关系概览。带虚线边框的直角矩形表示与先前综述一致的内容，而圆角矩形则表示本研究引入的原创贡献。

---

## 2 LLM-MAS的核心组件

LLM-MAS是指一个系统，其中包含一组能够在共享环境设置中进行交互和协作的生成式智能体（Wang et al., 2024c）。下面我们将讨论生成式智能体和环境。

### 2.1 生成式智能体

生成式智能体是指LLM-MAS中具有角色定义、能够感知环境、做出决策并执行复杂行动以改变环境的组件（Wang et al., 2024a）。它们可以是游戏中的玩家或社交媒体上的用户，其作用是推动LLM-MAS的发展并影响其结果。

与传统智能体相比，生成式智能体需要能够执行更复杂的行为，例如基于历史信息生成完整的个性化博客文章（Park et al., 2022）。因此，除了以LLM为核心之外，生成式智能体还需要具备以下特征：（i）**角色设定（Profiling）**，用于通过自然语言描述角色来关联其行为（Gao et al., 2023b），或根据每个生成式智能体的任务为其定制提示词（Xu et al., 2023c）。（ii）**记忆（Memory）**，用于存储历史轨迹并检索相关记忆以指导后续智能体行动，使其具备执行长期行动的能力，同时解决LLM上下文窗口有限的问题。通常包括三个层次的记忆：长期记忆、短期记忆和感官记忆（Park et al., 2023）。（iii）**规划（Planning）**，用于制定未来较长时期内的总体行为（Yao et al., 2023）。（iv）**行动（Action）**，执行生成式智能体与环境之间的交互（Wang et al., 2024a）。生成式智能体可能需要从若干候选行为中选择一个来执行，例如投票给谁（Xu et al., 2024），或者在没有强制约束的情况下生成行为，例如生成一段文本（Li et al., 2023）。

生成式智能体可以相互通信以实现系统内的协作。生成式智能体的通信大致可分为两个目的：（i）第一个目的是实现**协作**，将自己获取的信息与其他智能体共享，并在一定程度上将多个智能体聚合成一个完整的系统，实现超越独立智能体的性能（Yuan et al., 2023）；（ii）第二个目的是达成**共识**，使某些智能体在行为或策略上具有更大的相似性，从而更快地收敛到纳什均衡（Oroojlooy and Hajinezhad, 2023）。

通信内容的类型大致可分为两种：自然语言和自定义内容。自然语言形式的通信具有较高的可解释性和灵活性，但难以优化，因此更适合追求共识，例如ChatDev（Qian et al., 2024b）和招聘会系统（Li et al., 2023）。自定义内容可以是向量或离散信号，除了系统中的生成式智能体外，其他人无法理解。但这种形式易于使用策略梯度进行优化，因此常用于实现协作目的，例如DIAL算法（Hausknecht and Stone, 2015）及其变体。

### 2.2 环境

环境设置包括规则、工具和干预接口：（i）**工具**负责将智能体的行动指令转化为具体结果。生成式智能体向环境发送行动指令，环境将该指令转换为行动已执行的记录。不同场景中有不同的行动空间。在社交媒体场景中，行动空间包括"点赞"、"评论"、"关注"等（Wang et al., 2024b）。在开发场景中，行动空间包含聊天链（Qian et al., 2024b），比社交网络更大。（ii）**规则**定义了生成式智能体之间的通信模式或与环境的交互方式，直接定义了整个系统的行为结构。基于场景的不同，系统有一些特殊规则，例如游戏规则（Xu et al., 2024; Chen et al., 2024c）和社会行为规范（Park et al., 2023; Wang et al., 2024b）。通常情况下，大规模系统中的生成式智能体具有较小的行动空间，更容易被基于规则的模型替代（Mou et al., 2024）。（iii）**干预**为外部干预系统提供了接口。这种干预可以来自任何外部来源，如人类（Wang et al., 2024b）、监督模型（Chen et al., 2024c），甚至是生成式智能体（Qian et al., 2024b）。干预的目的可能是主动从系统中读取信息（Wang et al., 2024b），或者被动地中断系统以防止出现失控行为（Qian et al., 2024b）。

## 3 用于解决复杂任务的LLM-MAS

完成复杂任务通常需要多个角色、多个步骤等。这对单个智能体来说是困难的，但多个智能体协同工作将非常适合此类任务（Islam et al., 2024）。此外，每个智能体都可以独立训练（Shen et al., 2024; Yu et al., 2024）。与单个智能体相比，LLM-MAS可以取得更好的结果。也就是说，多智能体协作将提升整体性能（Du et al., 2023）。

### 3.1 用于解决复杂任务的代表性LLM-MAS

该领域目前是一个研究热点。近期，研究者主要关注多智能体推理框架和多智能体通信优化，下面将对此进行讨论。

**LLM-MAS推理框架。** 我们根据推理流程总结为三个方面，包括：（i）多阶段框架，（ii）集体决策框架，以及（iii）自我精炼框架。多阶段框架指的是智能体在不同阶段充当串行问题求解器的流程（Qian et al., 2024b），而集体决策（Zhao et al., 2024c）则指不同智能体为了一个目标进行投票或辩论。自我精炼指的是LLM-MAS中的自我反思机制。研究者提出了将多智能体应用于自然科学的框架（Chen et al., 2024a），以增强数据分析、模型模拟和决策过程（Yin et al., 2024）。Zhang et al. (2023a) 提出了一个实现自我适应和自适应协作的框架。智能体协作中的规模定律也被探索（Qian et al., 2024c），研究发现没有明显的规律模式。

**LLM-MAS通信优化。** LLM-MAS中的全连接通信可能导致组合爆炸和隐私泄露等问题。基于此，我们在通信优化中总结两个方面，包括：（i）速度优化和（ii）分布式讨论。速度优化指研究者试图加快智能体的通信，例如通过非语言通信（Liu et al., 2024b）或更短的生成内容（Chen et al., 2024g）。而分布式讨论则指智能体在缺乏足够信息的情况下尝试解决问题（Liu et al., 2024a）。智能体需要相互通信以实现其目标（Zhang et al., 2023a），即使单个智能体没有完整信息（Liu et al., 2024a）。

### 3.2 用于解决复杂任务的LLM-MAS资源

我们在表1中总结了用于模拟的常见开源LLM-MAS，包括代码、数据集和基准测试。

**数据集。** 所有传统NLP任务的数据集均可使用。此外，继ECL（Qian et al., 2024a）之后，Qian et al. (2024b) 在SRDD数据集上评估了生成软件的质量，并系统性地评估了软件开发领域中智能体的能力。

**开源社区。** 开源社区和工业界也为LLM-MAS的发展做出了重要贡献。MetaGPT（Hong et al., 2023）为生成式智能体分配不同的角色，以形成用于复杂任务的协作实体。Gao et al. (2024) 提出了AgentScope，以消息交换为核心通信机制。同时，该工作开发了一个分布式框架，支持在本地和分布式部署之间无缝切换，并以最小的代价实现自动并行优化。Open AI提出了Swarm（Ope, 2024），这是一个实验性的多智能体编排框架，符合人体工程学且轻量级。与之前发布的Assistants API不同，Swarm赋予开发者对上下文、步骤和工具调用的细粒度控制，而不是由平台托管。

### 3.3 用于解决复杂任务的LLM-MAS评估

**特定任务的性能。** 如表1所示，LLM-MAS的性能可以通过特定任务进行评估，这种方法直观且方便。例如，在APP系统（Zhang et al., 2023b）中，智能体完成特定任务所使用的平均步骤数和工具数被视为指标；在BOLAA（Liu et al., 2023c）中，智能体检索引擎的召回率和QA准确率也被视为评估指标；在狼人杀游戏（Xu et al., 2023c）中，虚拟玩家的胜率自然也是一个评估指标；在招聘会系统（Li et al., 2023）中，招聘方正确招募到目标求职者的比例也是一个评估指标；在拍卖系统（Chen et al., 2024c）中，商品预测价格与实际价格之间的斯皮尔曼相关系数以及竞拍者的技能也通过TrueSkill分数（Graepel et al., 2007）来衡量；在斯坦福小镇（Park et al., 2023）中，虚拟智能体和人类智能体生成行为的质量通过人工排序并使用TrueSkill进行评估；在城市模拟系统（Xu et al., 2023a）中，完成导航等特定任务的成功率也是一个评估指标。

**通信成本分析。** 最首要的问题在于系统的运行成本。鉴于当代系统中很大一部分将LLM作为关键模块，系统运行过程中产生的额外支出已成为一个关键的关注领域。作为一个示例，Mou et al. (2024) 利用系统的实际运行时间作为关键指标，突显了管理这种运行开销的重要性。

---

**表1：** 用于任务求解研究的LLM-MAS中的代码与基准测试。"No Code"或"No Benchmark"表示代码或基准测试不可用。

| 领域 | 子领域 | 论文 | 代码 | 数据集与基准测试 |
|---|---|---|---|---|
| 推理框架 | 多阶段 | (Qian et al., 2024b) | 代码链接 | SRDD |
| | | (Du et al., 2024) | 代码链接 | SRDD |
| | | (Yue et al., 2024) | 代码链接 | SMART (自建) |
| | | (Liu et al., 2023c) | 代码链接 | WebShop |
| | | (Lin et al., 2024) | 代码链接 | FG-C, CG-O |
| | | (Islam et al., 2024) | 代码链接 | HumanEval, EvalPlus, MBPP, APPS, xCodeEval, CodeContest |
| | | (Shen et al., 2024) | 代码链接 | ToolBench, ToolAlpaca |
| | 集体决策 | (Zhao et al., 2024c) | 代码链接 | MCQA |
| | | (Cheng et al., 2024) | 代码链接 | ESConv dataset, P4G dataset |
| | | (Liang et al., 2024) | 代码链接 | MT-Bench |
| | | (Lei et al., 2024) | 代码链接 | MATH |
| | | (Zhang et al., 2024a) | 代码链接 | MMLU, MATH, Chess Move Validity |
| | | (Wang et al., 2024d) | 代码链接 | TriviaQA |
| | 自我精炼 | (Wang et al., 2024c) | 代码链接 | FOLIO-wiki |
| | | (Chen et al., 2024e) | 代码链接 | StrategyQA, CSQA, GSM8K, AQuA, MATH, Date Understanding, ANLI |
| | | (Chen et al., 2024a) | 代码链接 | TriviaQA |
| | | (Tang et al., 2024) | 代码链接 | Trans-Review, AutoTransform, T5-Review |
| | | (Zhang et al., 2023a) | 代码链接 | Overcooked-AI |
| 通信优化 | 速度优化 | (Liu et al., 2024b) | 无代码 | HotpotQA, NarrativeQA, MultifieldQA |
| | 分布式 | (Chen et al., 2024f) | 代码链接 | TriviaQA, Natural Questions, HotpotQA, 2WikiMultiHopQA |
| | | (Liu et al., 2024a) | 代码链接 | InformativeBench |

---

## 4 用于模拟特定场景的LLM-MAS

本节将阐述LLM-MAS在模拟中的应用。研究者应用智能体模拟某种场景，以研究其对特定主题（如社会科学）的影响。一方面，与基于规则的方法（Chuang and Rogers, 2023）相比，具有自然语言通信能力的生成式智能体对人类来说更直观。另一方面，环境决定了模拟的性质，这是整个模拟的核心。

### 4.1 用于模拟特定场景的代表性LLM-MAS

LLM-MAS模拟的典型场景描述如下。我们将根据学科领域介绍以下工作。

**社会领域。** 现实世界中的大规模社会实验成本高昂，且大规模社会参与有时会升级为暴力和破坏，带来潜在后果（Mou et al., 2024）。因此，有必要在虚拟环境中进行模拟；模拟可以解决真实环境中开销过大的问题，并且能够以更快的速度长时间模拟现实世界中的过程（Li et al., 2024a）。同时，整个过程易于重复，有利于进一步研究。研究者已经做了大量工作来模拟社交媒体场景。基于社交媒体模拟原型（Park et al., 2022），Park et al. (2023) 提出了斯坦福小镇（Stanford Town），实现了对美国小镇中25个不同职业的智能体为期一天的生活模拟。同时，还有关于情感传播影响（Gao et al., 2023b）、基于推荐场景研究的信息茧房（Wang et al., 2024b）以及社会运动研究（Mou et al., 2024）的工作。研究者提出了城市生成智能（UGI）（Xu et al., 2023a），以解决特定城市问题并模拟复杂的城市系统，提供了一种多学科方法来理解和管理城市复杂性。Li et al. (2024a) 通过医院模拟研究了医生智能体的进化方法。由于医生智能体的训练既廉价又高效，这项工作可以在几天内快速将智能体扩展到处理数万个病例，而这项任务需要人类医生花费数年的时间。Pan et al. (2024) 提出了大规模智能体模拟，将智能体数量增加到10⁶个。在社交游戏方面，如狼人杀（Xu et al., 2024）、阿瓦隆（Lan et al., 2024）和我的世界（Gong et al., 2024）等用于LLM-MAS模拟的尝试已经展开。此外，一些游戏公司如网易也在其游戏中积极探索LLM-MAS的应用。

**物理领域。** 在物理领域，生成式智能体模拟的应用包括移动行为、交通（Gao et al., 2023a）、无线网络等。然而，关于多生成式智能体的研究仍然有限。Zou et al. (2023) 探索了多个智能体在无线领域的应用，提出了一个框架，其中多个设备端智能体可以与环境交互并交换知识，共同解决复杂任务。

### 4.2 用于模拟的LLM-MAS资源

我们在表2中总结了用于模拟的常见开源LLM-MAS，包括代码和基准测试。

为了证明模拟的有效性，即与现实拟合，研究者通常通过模拟真实数据来评估模拟系统。因此，具有密集用户和记录的真实数据集对于评估模拟非常重要（Mou et al., 2024）。理想的数据集将是密集的：即在相同规模下，具有较少用户数量的数据能更好地评估LLM-MAS的模拟能力。

在基准测试方面，Du and Zhang (2024) 提出了基于狼人杀场景的WWQA，用于评估智能体在狼人杀场景中的能力。SoMoSiMu-Bench（Mou et al., 2024）提供了专注于个体用户行为和社交模拟系统结果的评估基准。

### 4.3 LLM-MAS模拟的评估

我们将根据用于评估LLM-MAS整体的指标（而非单个智能体的能力）进行讨论。

**一致性。** LLM-MAS需要与现实世界高度一致，以确保获得有意义和有洞察力的实验结果。在模拟系统的背景下，以UGI（Xu et al., 2023a）为例，其主要目标在于忠实地复现特定的现实世界场景。当用于训练智能体时（如SMART（Yue et al., 2024）），只有在密切模拟真实环境的虚拟环境中经过严格训练的智能体，才能被认为适合在现实环境中部署。类似地，当用于评估目的时（如AgentSims（Lin et al., 2023）），获得真实可靠的评估结果取决于虚拟环境与其现实对应物保持高度一致。最后，在用于收集数据的系统中（如BOLAA（Liu et al., 2023c）），一致性也确保了数据的有效性。因此，LLM-MAS的一个重要性能指标就是其与现实情况的一致性。

**信息传播。** 使用时间序列分析方法比较系统中信息传播行为与现实之间的差异。信息传播在一定程度上可以反映媒体的性质；因此，一个现实的多智能体系统应该具有与现实世界相似的信息传播趋势。Abdelzaher et al. (2020) 比较了在线社交媒体模拟环境中每天发生事件数量的变化；S³（Gao et al., 2023b）比较了每天知晓某一事件的用户数量，以及对该事件的情感密度和支持率的变化；斯坦福小镇（Park et al., 2023）中也采用了类似的方法。

---

**表2：** 用于模拟研究的LLM-MAS中的代码与基准测试。"No Code"或"No Benchmark"表示代码或基准测试不可用。

| 领域 | 子领域 | 论文 | 代码 | 数据集与基准测试 |
|---|---|---|---|---|
| 社会 | 微型社会 | (Huang et al., 2024b) | 无代码 | AdaSociety |
| | | (Chen et al., 2024b) | 代码链接 | AgentCourt |
| | | (Park et al., 2023) | 代码链接 | 无基准测试或数据集 |
| | | (Piatti et al., 2024) | 代码链接 | 无基准测试 |
| | | (Chuang et al., 2024) | 代码链接 | 无基准测试或数据集 |
| | 经济学 | (Li et al., 2024b) | 代码链接 | 无基准测试或数据集 |
| | 社交媒体 | (Wang et al., 2024b) | 代码链接 | Movielens-1M |
| | | (Gao et al., 2023b) | 无代码 | Blog Authorship Corpus |
| | | (Mou et al., 2024) | 代码链接 | SoMoSiMu-Bench (自建) |
| | 游戏 | (Du and Zhang, 2024) | 代码链接 | WWQA |
| | | (Pan et al., 2024) | 代码链接 | 无基准测试或数据集 |
| 物理 | 无线 | (Zou et al., 2023) | 无代码 | 无基准测试或数据集 |

---

## 5 用于评估生成式智能体的LLM-MAS

随着LLM在社区中占据主导地位，如何评估LLM的能力仍是一个开放性问题。现有的评估方法存在以下不足：（i）评估能力受限，（ii）基准测试易受攻击，以及（iii）指标缺乏客观性。LLM-MAS的复杂性和多样性表明其可用于评估LLM。然而，如何设计具体的评估指标和评估方法一直困扰着研究者。类似地，LLM-MAS也可用于训练生成式智能体。我们总结了训练的三个方面：（i）监督微调（SFT），（ii）强化学习（RL），（iii）为训练合成数据。

### 5.1 用于评估生成式智能体的代表性LLM-MAS

LLM-MAS可以向智能体提供奖励，这些奖励可用于评估或训练生成式智能体，下面将对此进行讨论。

**生成式智能体的评估。** 研究者通过将生成式智能体置于LLM-MAS中来研究它们。在LLM-MAS中，研究者可以进一步研究LLM在不同场景中的策略能力，如长期策略能力（Chen et al., 2024c）、领导力策略（Xu et al., 2023c）和竞争策略（Zhao et al., 2024b）。在情感领域，MuMA-ToM（Shi et al., 2024）用于评估智能体通过视频和文本描述理解和推理真实家庭环境中人类交互的能力。

**生成式智能体的训练。** Li et al. (2024c) 通过LLM-MAS增强数据以进行监督微调（SFT）生成式智能体。Xu et al. (2023c) 创建了生成式智能体，通过提出一种新颖的框架，将生成式智能体与多智能体强化学习相结合，克服了LLM固有的偏差（Xu et al., 2023c）。对于LLM-MAS，Yue et al. (2024) 将知识密集型任务中的复杂轨迹拆分为子任务，提出了多智能体框架的共训练范式——长短期轨迹学习，在保持每个智能体细粒度性能的同时确保协同效应。RLHF因其高昂的成本而受到批评。Liu et al. (2023a) 提出了一种基于多智能体系统的对齐方案，有效解决了基于奖励的RL优化中与不稳定性和奖励博弈相关的问题。无论哪种方式，LLM-MAS本质上都被视为RL中的一种环境，通过不同的方式从环境中获取奖励。

### 5.2 用于评估的LLM-MAS资源

表3展示了我们总结的带有代码、数据集和基准测试的工作，为未来的研究者提供参考。

---

**表3：** 用于评估研究的LLM-MAS中的代码与基准测试。"No Code"或"No Benchmark"表示代码或基准测试不可用。

| 领域 | 子领域 | 论文 | 代码 | 数据集与基准测试 |
|---|---|---|---|---|
| 生成式智能体的评估 | 策略 | (Liu et al., 2023b) | 代码链接 | AGENTBENCH |
| | | (Bandi and Harrasse, 2024) | 无代码 | MT-Bench |
| | | (Chan et al., 2023) | 代码链接 | ChatEval |
| | | (Chen et al., 2024d) | 代码链接 | LLMARENA |
| | | (Xu et al., 2023b) | 代码链接 | MAgIC |
| | | (Huang et al., 2024a) | 代码链接 | MLAgentBench |
| | | (Chen et al., 2024c) | 代码链接 | AUCARENA |
| | 情感 | (Zhang et al., 2024b) | 代码链接 | PsySafe |
| | | (Shi et al., 2024) | 代码链接 | MuMA-ToM |
| 生成式智能体的训练 | LLM-MAS上的SFT | (Li et al., 2024c) | 代码链接 | MT-Bench, AlpacaEval |
| | LLM-MAS上的MARL | (Xu et al., 2023c) | 无代码 | 无数据集或基准测试 |
| | 合成数据 | (Liu et al., 2023a) | 代码链接 | HH, Moral Stories, MIC, ETHICS-Deontology, TruthfulQA |

---

## 6 挑战与未来方向

尽管先前关于LLM-MAS的工作取得了诸多显著成功，但该领域仍处于初始阶段，其发展过程中有若干重大挑战需要解决。下面，我们概述了几个关键挑战以及潜在的未来方向。

### 6.1 生成式智能体带来的挑战

生成式智能体是LLM-MAS不可或缺的组成部分。然而，由于基座模型LLM的固有特性，生成式智能体存在一些不足之处，下面将详细讨论。

**挑战。** （i）**模拟的广义对齐**（Liu et al., 2023a）。当智能体被用于现实世界模拟时，一个完美的生成式智能体应能诚实地描绘多样的特征（Wang et al., 2024a）。然而，由于基础模型的训练方法（OpenAI et al., 2024），生成式智能体通常无法与模拟对象对齐。（ii）**幻觉**。生成式智能体与其他智能体交互时存在一定概率产生幻觉（Du et al., 2023）。各种增强方法可以缓解但无法解决这个问题。（iii）**缺乏足够的长文本能力**。在处理复杂信息时，由于缺乏长文本能力，生成式智能体会遗忘输入信息（Zhao et al., 2024a）。

**未来方向。** 提升单一智能体的能力或基座模型的能力一直是一个热点话题。研究者持续关注增强对齐、减少幻觉以及提升长文本能力。新一代Open AI模型o1的提出（Int, 2024），为研究者提供了新思路，即利用更复杂的推理来增强模型能力。

### 6.2 交互带来的挑战

由于LLM-MAS的复杂性、自回归等特性，系统在实际应用中存在许多问题。以下列出两个主要问题：效率爆炸和累积效应。

**效率爆炸。** 由于自回归架构，LLM通常推理速度较慢。然而，生成式智能体每次行动需要多次查询LLM，例如从记忆中提取信息、在采取行动前制定计划等。当LLM-MAS扩展规模时，这个问题会被放大，特别是对于具有较大行动空间的生成式智能体。SoMoSiMu-Bench（Mou et al., 2024）用基于规则的智能体替代边缘生成式智能体，缓解了这一问题。然而，对于具有复杂行动空间的LLM-MAS中的生成式智能体，这个问题仍未解决。

**累积效应。** 由于LLM-MAS的每一轮都基于前一轮的结果，并且LLM-MAS对后续结果有很大影响。研究者使用了基于规则的模型进行中间错误修正（Chen et al., 2024c），但仍有很大的改进空间。IOA（Chen et al., 2024f）提出了一种类似互联网的通信架构，使LLM-MAS更具可扩展性，并增强了对动态任务的适应性。

**未来方向。** 工业界和学术界一直在努力降低LLM-MAS的通信成本，例如基于对齐的方法OPTIMA（Chen et al., 2024g）和工业化并行消息方法AgentScope（Gao et al., 2024），但这些仍处于基础阶段，有广阔的研究空间。

### 6.3 LLM-MAS评估的挑战

**缺乏群体行为的客观指标。** 如第4.3节所示，由于多智能体环境的多样性、复杂性和不可预测性，当前工作在群体层面上很难获得足够详细、具体和直接的系统评估指标。目前，研究者主要通过比较系统与真实环境的分布来评估LLM-MAS，这缺乏对LLM-MAS运行过程的细节评估。

**自动化评估与基准测试。** 由于缺乏针对LLM-MAS的基准测试，同类不同LLM-MAS之间无法进行比较。此外，缺乏一个通用的基准测试框架，既能用于个体评估也能用于整体评估，可用于评估大多数LLM-MAS。

**未来方向。** 研究大规模LLM-MAS将成为一个新的研究热点，研究者将从中评估并发现新的规模效应。同时，通用的测试基准和评估方法也将在未来的研究中出现。

## 7 结论

在本综述中，我们系统地总结了基于LLM的多智能体系统（LLM-MAS）领域的现有研究。我们从三个应用方面对这些研究进行了展示和回顾：任务求解、模拟和评估。我们提供了一个详细的分类法来连接现有研究，总结了每个方面的主要技术及其发展历程。除了回顾先前的工作，我们还提出了该领域的若干挑战，预计将指导潜在的未来方向。

## 局限性

我们已尽最大努力，但仍可能存在一些局限性。由于篇幅限制，我们只能对每种方法进行简要总结，无法提供详尽的技术细节。另一方面，我们主要收集了来自*ACL、NeurIPS、ICLR、AAAI和arXiv的研究，可能遗漏了在其他会议或期刊上发表的重要工作。在应用方面，我们主要在表1、表2和表3中列出了具有开放代码的代表性LLM-MAS资源。更完整的论文列表可在 https://github.com/bianhua-12/Multi-generative_Agent_System_survey 中找到。我们认识到本工作的时效性，并将持续关注研究社区内的讨论，在未来更新观点并补充遗漏的工作。

## 致谢

本研究得到了国家重点研发计划（No. 2022YFF0902100）和黑龙江省自然科学基金（YQ2021F006）的支持。

## 参考文献

2024. Introducing OpenAI o1. https://openai.com/o1/.
2024. Openai/swarm. OpenAI.
Tarek Abdelzaher, Jiawei Han, Yifan Hao, Andong Jing, Dongxin Liu, Shengzhong Liu, Hoang Hai Nguyen, David M Nicol, Huajie Shao, Tianshi Wang, et al. 2020. Multiscale online media simulation with socialcube. *Computational and Mathematical Organization Theory*, 26:145–174.
P. G. Balaji and D. Srinivasan. 2010. An Introduction to Multi-Agent Systems. In Dipti Srinivasan and Lakhmi C. Jain, editors, *Innovations in Multi-Agent Systems and Applications - 1*, pages 1–27. Springer, Berlin, Heidelberg.
Chaithanya Bandi and Abir Harrasse. 2024. Adversarial Multi-Agent Evaluation of Large Language Models through Iterative Debates. *Preprint*, arXiv:2410.04663.
Chi-Min Chan, Weize Chen, Yusheng Su, Jianxuan Yu, Wei Xue, Shanghang Zhang, Jie Fu, and Zhiyuan Liu. 2023. ChatEval: Towards Better LLM-based Evaluators through Multi-Agent Debate. *Preprint*, arXiv:2308.07201.
Guangyao Chen, Siwei Dong, Yu Shu, Ge Zhang, Jaward Sesay, Börje F. Karlsson, Jie Fu, and Yemin Shi. 2024a. AutoAgents: A Framework for Automatic Agent Generation. *Preprint*, arXiv:2309.17288.
Guhong Chen, Liyang Fan, Zihan Gong, Nan Xie, Zixuan Li, Ziqiang Liu, Chengming Li, Qiang Qu, Shiwen Ni, and Min Yang. 2024b. AgentCourt: Simulating Court with Adversarial Evolvable Lawyer Agents. *Preprint*, arXiv:2408.08089.
Jiangjie Chen, Siyu Yuan, Rong Ye, Bodhisattwa Prasad Majumder, and Kyle Richardson. 2024c. Put Your Money Where Your Mouth Is: Evaluating Strategic Planning and Execution of LLM Agents in an Auction Arena. *Preprint*, arXiv:2310.05746.
Junzhe Chen, Xuming Hu, Shuodi Liu, Shiyu Huang, Wei-Wei Tu, Zhaofeng He, and Lijie Wen. 2024d. LLMArena: Assessing Capabilities of Large Language Models in Dynamic Multi-Agent Environments. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 13055–13077.
Justin Chen, Swarnadeep Saha, and Mohit Bansal. 2024e. ReConcile: Round-Table Conference Improves Reasoning via Consensus among Diverse LLMs. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 7066–7085, Bangkok, Thailand. Association for Computational Linguistics.
Weize Chen, Ziming You, Ran Li, Yitong Guan, Chen Qian, Chenyang Zhao, Cheng Yang, Ruobing Xie, Zhiyuan Liu, and Maosong Sun. 2024f. Internet of Agents: Weaving a Web of Heterogeneous Agents for Collaborative Intelligence. *Preprint*, arXiv:2407.07061.
Weize Chen, Jiarui Yuan, Chen Qian, Cheng Yang, Zhiyuan Liu, and Maosong Sun. 2024g. Optima: Optimizing Effectiveness and Efficiency for LLM-Based Multi-Agent System. *Preprint*, arXiv:2410.08115.
Yi Cheng, Wenge Liu, Jian Wang, Chak Tou Leong, Yi Ouyang, Wenjie Li, Xian Wu, and Yefeng Zheng. 2024. Cooper: Coordinating Specialized Agents towards a Complex Dialogue Goal. *Proceedings of the AAAI Conference on Artificial Intelligence*, 38(16):17853–17861.
Yun-Shiuan Chuang, Agam Goyal, Nikunj Harlalka, Siddharth Suresh, Robert Hawkins, Sijia Yang, Dhavan Shah, Junjie Hu, and Timothy Rogers. 2024. Simulating Opinion Dynamics with Networks of LLM-based Agents. In *Findings of the Association for Computational Linguistics: NAACL 2024*, pages 3326–3346, Mexico City, Mexico. Association for Computational Linguistics.
Yun-Shiuan Chuang and Timothy T. Rogers. 2023. Computational Agent-based Models in Opinion Dynamics: A Survey on Social Simulations and Empirical Studies. *Preprint*, arXiv:2306.03446.
Silin Du and Xiaowei Zhang. 2024. Helmsman of the Masses? Evaluate the Opinion Leadership of Large Language Models in the Werewolf Game. In *First Conference on Language Modeling*.
Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, and Igor Mordatch. 2023. Improving Factuality and Reasoning in Language Models through Multiagent Debate. *Preprint*, arXiv:2305.14325.
Zhuoyun Du, Chen Qian, Wei Liu, Zihao Xie, Yifei Wang, Yufan Dang, Weize Chen, and Cheng Yang. 2024. Multi-Agent Software Development through Cross-Team Collaboration. *Preprint*, arXiv:2406.08979.
Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, et al. 2024. The Llama 3 Herd of Models. *Preprint*, arXiv:2407.21783.
Chen Gao, Xiaochong Lan, Nian Li, Yuan Yuan, Jingtao Ding, Zhilun Zhou, Fengli Xu, and Yong Li. 2023a. Large Language Models Empowered Agent-based Modeling and Simulation: A Survey and Perspectives. *Preprint*, arXiv:2312.11970.
Chen Gao, Xiaochong Lan, Zhihong Lu, Jinzhu Mao, Jinghua Piao, Huandong Wang, Depeng Jin, and Yong Li. 2023b. S3: Social-network Simulation System with Large Language Model-Empowered Agents. *Preprint*, arXiv:2307.14984.
Dawei Gao, Zitao Li, Xuchen Pan, Weirui Kuang, Zhijian Ma, Bingchen Qian, Fei Wei, Wenhao Zhang, Yuexiang Xie, Daoyuan Chen, Liuyi Yao, Hongyi Peng, Zeyu Zhang, Lin Zhu, Chen Cheng, Hongzhu Shi, Yaliang Li, Bolin Ding, and Jingren Zhou. 2024. AgentScope: A Flexible yet Robust Multi-Agent Platform. *Preprint*, arXiv:2402.14034.
Ran Gong, Qiuyuan Huang, Xiaojian Ma, Yusuke Noda, Zane Durante, Zilong Zheng, Demetri Terzopoulos, Li Fei-Fei, Jianfeng Gao, and Hoi V o. 2024. MindAgent: Emergent Gaming Interaction. In *Findings of the Association for Computational Linguistics: NAACL 2024*, pages 3154–3183, Mexico City, Mexico. Association for Computational Linguistics.
Thore Graepel, Tom Minka, and R TrueSkill Herbrich. 2007. A bayesian skill rating system. *Advances in Neural Information Processing Systems*, 19(569-576):7.
Sven Gronauer and Klaus Diepold. 2022. Multi-agent deep reinforcement learning: A survey. *Artificial Intelligence Review*, 55(2):895–943.
Taicheng Guo, Xiuying Chen, Yaqi Wang, Ruidi Chang, Shichao Pei, Nitesh V. Chawla, Olaf Wiest, and Xiangliang Zhang. 2024. Large Language Model Based Multi-agents: A Survey of Progress and Challenges. In *Thirty-Third International Joint Conference on Artificial Intelligence*, volume 9, pages 8048–8057.
Shanshan Han, Qifan Zhang, Yuhang Yao, Weizhao Jin, Zhaozhuo Xu, and Chaoyang He. 2024. LLM Multi-Agent Systems: Challenges and Open Problems. *Preprint*, arXiv:2402.03578.
Matthew Hausknecht and Peter Stone. 2015. Deep recurrent q-learning for partially observable mdps. *Computer Science*.
Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, and Jürgen Schmidhuber. 2023. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework. *Preprint*, arXiv:2308.00352.
Qian Huang, Jian V ora, Percy Liang, and Jure Leskovec. 2024a. MLAgentBench: Evaluating Language Agents on Machine Learning Experimentation. *Preprint*, arXiv:2310.03302.
Yizhe Huang, Xingbo Wang, Hao Liu, Fanqi Kong, Aoyang Qin, Min Tang, Xiaoxi Wang, Song-Chun Zhu, Mingjie Bi, Siyuan Qi, and Xue Feng. 2024b. AdaSociety: An Adaptive Environment with Social Structures for Multi-Agent Decision-Making. *Preprint*, arXiv:2411.03865.
Md. Ashraful Islam, Mohammed Eunus Ali, and Md Rizwan Parvez. 2024. MapCoder: Multi-Agent Code Generation for Competitive Problem Solving. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 4912–4944, Bangkok, Thailand. Association for Computational Linguistics.
Yihuai Lan, Zhiqiang Hu, Lei Wang, Yang Wang, Deheng Ye, Peilin Zhao, Ee-Peng Lim, Hui Xiong, and Hao Wang. 2024. LLM-Based Agent Society Investigation: Collaboration and Confrontation in Avalon Gameplay. *Preprint*, arXiv:2310.14985.
Bin Lei, Yi Zhang, Shan Zuo, Ali Payani, and Caiwen Ding. 2024. MACM: Utilizing a Multi-Agent System for Condition Mining in Solving Complex Mathematical Problems. *Preprint*, arXiv:2404.04735.
Junkai Li, Siyu Wang, Meng Zhang, Weitao Li, Yunghwei Lai, Xinhui Kang, Weizhi Ma, and Yang Liu. 2024a. Agent Hospital: A Simulacrum of Hospital with Evolvable Medical Agents. *Preprint*, arXiv:2405.02957.
Nian Li, Chen Gao, Mingyu Li, Yong Li, and Qingmin Liao. 2024b. EconAgent: Large Language Model-Empowered Agents for Simulating Macroeconomic Activities. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 15523–15536, Bangkok, Thailand. Association for Computational Linguistics.
Renhao Li, Minghuan Tan, Derek F. Wong, and Min Yang. 2024c. CoEvol: Constructing Better Responses for Instruction Finetuning through Multi-Agent Cooperation. *Preprint*, arXiv:2406.07054.
Xinyi Li, Sai Wang, Siqi Zeng, Yu Wu, and Yi Yang. 2024d. A survey on LLM-based multi-agent systems: Workflow, infrastructure, and challenges. *Vicinagearth*, 1(1):9.
Yuan Li, Yixuan Zhang, and Lichao Sun. 2023. MetaAgents: Simulating Interactions of Human Behaviors for LLM-based Task-oriented Coordination via Collaborative Generative Agents. *Preprint*, arXiv:2310.06500.
Tian Liang, Zhiwei He, Wenxiang Jiao, Xing Wang, Yan Wang, Rui Wang, Yujiu Yang, Shuming Shi, and Zhaopeng Tu. 2024. Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate. *Preprint*, arXiv:2305.19118.
Jiaju Lin, Haoran Zhao, Aochi Zhang, Yiting Wu, Huqiuyue Ping, and Qin Chen. 2023. AgentSims: An Open-Source Sandbox for Large Language Model Evaluation. *Preprint*, arXiv:2308.04026.
Leilei Lin, Yumeng Jin, Yingming Zhou, Wenlong Chen, and Chen Qian. 2024. MAO: A Framework for Process Model Generation with Multi-Agent Orchestration. *Preprint*, arXiv:2408.01916.
Ruibo Liu, Ruixin Yang, Chenyan Jia, Ge Zhang, Diyi Yang, and Soroush V osoughi. 2023a. Training Socially Aligned Language Models on Simulated Social Interactions. In *The Twelfth International Conference on Learning Representations*.
Wei Liu, Chenxi Wang, Yifei Wang, Zihao Xie, Rennai Qiu, Yufan Dang, Zhuoyun Du, Weize Chen, Cheng Yang, and Chen Qian. 2024a. Autonomous Agents for Collaborative Task under Information Asymmetry. *Preprint*, arXiv:2406.14928.
Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu, Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan Sun, Minlie Huang, Yuxiao Dong, and Jie Tang. 2023b. AgentBench: Evaluating LLMs as Agents. *Preprint*, arXiv:2308.03688.
Yuhan Liu, Esha Choukse, Shan Lu, Junchen Jiang, and Madan Musuvathi. 2024b. DroidSpeak: Enhancing Cross-LLM Communication. *Preprint*, arXiv:2411.02820.
Zhiwei Liu, Weiran Yao, Jianguo Zhang, Le Xue, Shelby Heinecke, Rithesh Murthy, Yihao Feng, Zeyuan Chen, Juan Carlos Niebles, Devansh Arpit, Ran Xu, Phil Mui, Huan Wang, Caiming Xiong, and Silvio Savarese. 2023c. BOLAA: Benchmarking and Orchestrating LLM-augmented Autonomous Agents. *Preprint*, arXiv:2308.05960.
Xinyi Mou, Zhongyu Wei, and Xuanjing Huang. 2024. Unveiling the Truth and Facilitating Change: Towards Agent-based Large-scale Social Movement Simulation. In *Findings of the Association for Computational Linguistics ACL 2024*, pages 4789–4809, Bangkok, Thailand and virtual meeting. Association for Computational Linguistics.
OpenAI, Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, et al. 2024. GPT-4 Technical Report. *Preprint*, arXiv:2303.08774.
Afshin Oroojlooy and Davood Hajinezhad. 2023. A review of cooperative multi-agent deep reinforcement learning. *Applied Intelligence*, 53(11):13677–13722.
Xuchen Pan, Dawei Gao, Yuexiang Xie, Yushuo Chen, Zhewei Wei, Yaliang Li, Bolin Ding, Ji-Rong Wen, and Jingren Zhou. 2024. Very Large-Scale Multi-Agent Simulation in AgentScope. *Preprint*, arXiv:2407.17789.
Joon Sung Park, Joseph C. O'Brien, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, and Michael S. Bernstein. 2023. Generative Agents: Interactive Simulacra of Human Behavior. *Preprint*, arXiv:2304.03442.
Joon Sung Park, Lindsay Popowski, Carrie J. Cai, Meredith Ringel Morris, Percy Liang, and Michael S. Bernstein. 2022. Social Simulacra: Creating Populated Prototypes for Social Computing Systems. *Preprint*, arXiv:2208.04024.
Giorgio Piatti, Zhijing Jin, Max Kleiman-Weiner, Bernhard Schölkopf, Mrinmaya Sachan, and Rada Mihalcea. 2024. Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents. *Preprint*, arXiv:2404.16698.
Chen Qian, Yufan Dang, Jiahao Li, Wei Liu, Zihao Xie, YiFei Wang, Weize Chen, Cheng Yang, Xin Cong, Xiaoyin Che, Zhiyuan Liu, and Maosong Sun. 2024a. Experiential Co-Learning of Software-Developing Agents. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 5628–5640, Bangkok, Thailand. Association for Computational Linguistics.
Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng Su, Xin Cong, Juyuan Xu, Dahai Li, Zhiyuan Liu, and Maosong Sun. 2024b. ChatDev: Communicative Agents for Software Development. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 15174–15186, Bangkok, Thailand. Association for Computational Linguistics.
Chen Qian, Zihao Xie, Yifei Wang, Wei Liu, Yufan Dang, Zhuoyun Du, Weize Chen, Cheng Yang, Zhiyuan Liu, and Maosong Sun. 2024c. Scaling Large-Language-Model-based Multi-Agent Collaboration. *Preprint*, arXiv:2406.07155.
Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. Language Models are Unsupervised Multitask Learners.
Weizhou Shen, Chenliang Li, Hongzhan Chen, Ming Yan, Xiaojun Quan, Hehong Chen, Ji Zhang, and Fei Huang. 2024. Small LLMs Are Weak Tool Learners: A Multi-LLM Agent. *Preprint*, arXiv:2401.07324.
Haojun Shi, Suyu Ye, Xinyu Fang, Chuanyang Jin, Leyla Isik, Yen-Ling Kuo, and Tianmin Shu. 2024. MuMA-ToM: Multi-modal Multi-Agent Theory of Mind. *Preprint*, arXiv:2408.12574.
Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. 2023. Reflexion: Language agents with verbal reinforcement learning. *Advances in Neural Information Processing Systems*, 36:8634–8652.
Xunzhu Tang, Kisub Kim, Yewei Song, Cedric Lothritz, Bei Li, Saad Ezzini, Haoye Tian, Jacques Klein, and Tegawende F. Bissyande. 2024. CodeAgent: Autonomous Communicative Agents for Code Review. *Preprint*, arXiv:2402.02172.
Lei Wang, Chen Ma, Xueyang Feng, Zeyu Zhang, Hao Yang, Jingsen Zhang, Zhiyuan Chen, Jiakai Tang, Xu Chen, Yankai Lin, Wayne Xin Zhao, Zhewei Wei, and Jirong Wen. 2024a. A survey on large language model based autonomous agents. *Frontiers of Computer Science*, 18(6):186345.
Lei Wang, Jingsen Zhang, Hao Yang, Zhiyuan Chen, Jiakai Tang, Zeyu Zhang, Xu Chen, Yankai Lin, Ruihua Song, Wayne Xin Zhao, Jun Xu, Zhicheng Dou, Jun Wang, and Ji-Rong Wen. 2024b. User Behavior Simulation with Large Language Model based Agents. *Preprint*, arXiv:2306.02552.
Qineng Wang, Zihao Wang, Ying Su, Hanghang Tong, and Yangqiu Song. 2024c. Rethinking the Bounds of LLM Reasoning: Are Multi-Agent Discussions the Key? In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 6106–6131, Bangkok, Thailand. Association for Computational Linguistics.
Zhenhailong Wang, Shaoguang Mao, Wenshan Wu, Tao Ge, Furu Wei, and Heng Ji. 2024d. Unleashing the Emergent Cognitive Synergy in Large Language Models: A Task-Solving Agent through Multi-Persona Self-Collaboration. In *Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)*, pages 257–279, Mexico City, Mexico. Association for Computational Linguistics.
Fengli Xu, Jun Zhang, Chen Gao, Jie Feng, and Yong Li. 2023a. Urban Generative Intelligence (UGI): A Foundational Platform for Agents in Embodied City Environment. *Preprint*, arXiv:2312.11813.
Lin Xu, Zhiyuan Hu, Daquan Zhou, Hongyu Ren, Zhen Dong, Kurt Keutzer, See Kiong Ng, and Jiashi Feng. 2023b. MAgIC: Investigation of Large Language Model Powered Multi-Agent in Cognition, Adaptability, Rationality and Collaboration. *Preprint*, arXiv:2311.08562.
Yuzhuang Xu, Shuo Wang, Peng Li, Fuwen Luo, Xiaolong Wang, Weidong Liu, and Yang Liu. 2024. Exploring Large Language Models for Communication Games: An Empirical Study on Werewolf. *Preprint*, arXiv:2309.04658.
Zelai Xu, Chao Yu, Fei Fang, Yu Wang, and Yi Wu. 2023c. Language Agents with Reinforcement Learning for Strategic Play in the Werewolf Game.
Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2023. ReAct: Synergizing Reasoning and Acting in Language Models. *Preprint*, arXiv:2210.03629.
Xiangyu Yin, Chuqiao Shi, Yimo Han, and Yi Jiang. 2024. PEAR: A Robust and Flexible Automation Framework for Ptychography Enabled by Multiple Large Language Model Agents. *Preprint*, arXiv:2410.09034.
Xiaoyan Yu, Tongxu Luo, Yifan Wei, Fangyu Lei, Yiming Huang, Hao Peng, and Liehuang Zhu. 2024. Neeko: Leveraging Dynamic LoRA for Efficient Multi-Character Role-Playing Agent. *Preprint*, arXiv:2402.13717.
Haoqi Yuan, Chi Zhang, Hongcheng Wang, Feiyang Xie, Penglin Cai, Hao Dong, and Zongqing Lu. 2023. Skill Reinforcement Learning and Planning for Open-World Long-Horizon Tasks. *Preprint*, arXiv:2303.16563.
Shengbin Yue, Siyuan Wang, Wei Chen, Xuanjing Huang, and Zhongyu Wei. 2024. Synergistic Multi-Agent Framework with Trajectory Learning for Knowledge-Intensive Tasks. *Preprint*, arXiv:2407.09893.
Ceyao Zhang, Kaijie Yang, Siyi Hu, Zihao Wang, Guanghe Li, Yihang Sun, Cheng Zhang, Zhaowei Zhang, Anji Liu, Song-Chun Zhu, Xiaojun Chang, Junge Zhang, Feng Yin, Yitao Liang, and Yaodong Yang. 2023a. ProAgent: Building Proactive Cooperative AI with Large Language Models. *CoRR*.
Chi Zhang, Zhao Yang, Jiaxuan Liu, Yucheng Han, Xin Chen, Zebiao Huang, Bin Fu, and Gang Yu. 2023b. AppAgent: Multimodal Agents as Smartphone Users. *Preprint*, arXiv:2312.13771.
Jintian Zhang, Xin Xu, Ningyu Zhang, Ruibo Liu, Bryan Hooi, and Shumin Deng. 2024a. Exploring Collaboration Mechanisms for LLM Agents: A Social Psychology View. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 14544–14607, Bangkok, Thailand. Association for Computational Linguistics.
Zaibin Zhang, Yongting Zhang, Lijun Li, Jing Shao, Hongzhi Gao, Yu Qiao, Lijun Wang, Huchuan Lu, and Feng Zhao. 2024b. PsySafe: A Comprehensive Framework for Psychological-based Attack, Defense, and Evaluation of Multi-agent System Safety. In *Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)*, pages 15202–15231, Bangkok, Thailand. Association for Computational Linguistics.
Jun Zhao, Can Zu, Hao Xu, Yi Lu, Wei He, Yiwen Ding, Tao Gui, Qi Zhang, and Xuanjing Huang. 2024a. LongAgent: Scaling Language Models to 128k Context through Multi-Agent Collaboration. *Preprint*, arXiv:2402.11550.
Qinlin Zhao, Jindong Wang, Yixuan Zhang, Yiqiao Jin, Kaijie Zhu, Hao Chen, and Xing Xie. 2024b. CompeteAI: Understanding the Competition Dynamics in Large Language Model-based Agents. *Preprint*, arXiv:2310.17512.
Xiutian Zhao, Ke Wang, and Wei Peng. 2024c. An Electoral Approach to Diversify LLM-based Multi-Agent Collective Decision-Making. *Preprint*, arXiv:2410.15168.
Hang Zou, Qiyang Zhao, Lina Bariah, Mehdi Bennis, and Merouane Debbah. 2023. Wireless Multi-Agent Generative AI: From Connected Intelligence to Collective Intelligence. *Preprint*, arXiv:2307.02757.
