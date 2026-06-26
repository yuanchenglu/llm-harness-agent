# AGENTBENCH: 评估作为智能体的大语言模型

**发表于 ICLR 2024 会议论文**

肖 刘1,*, 浩 于1,*,†, 汉臣 张1,*, 逸凡 徐1, 玄宇 雷1, 瀚宇 赖1, 宇 顾2,†,
航亮 丁1, 凯文 门1, 可娟 杨1, 书丹 张1, 翔 邓2, 傲寒 曾1,
正晓 杜1, 晨辉 张1, 晟 沈3, 天俊 张3, 宇 苏2, 欢 孙2,
敏列 黄1, 宇晓 董1,‡, 杰 唐1,‡

1清华大学, 2俄亥俄州立大学, 3加州大学伯克利分校

## 摘要

大型语言模型（LLM）作为智能体的潜力最近得到了广泛认可。因此，迫切需要量化评估LLM在交互环境中处理具有挑战性任务时的智能体能力。我们提出了AGENTBENCH，一个多维度的基准测试，包含8个不同的环境，用于评估LLM作为智能体的推理和决策能力。我们对29个基于API和开源（OSS）的LLM进行的广泛测试表明，虽然顶级商业LLM在复杂环境中展现出作为智能体的强大能力，但它们与许多不超过70B参数的OSS竞争对手之间存在显著的性能差距。我们识别了环境和LLM中失败的典型原因，表明长期推理、决策和指令遵循能力的不足是开发可用LLM智能体的主要障碍。改进指令遵循能力以及在高质量多轮对齐数据上进行训练可以提升智能体性能。与现有假设不同，代码训练对不同智能体任务的影响是矛盾的。AGENTBENCH的数据集、环境和集成评估包已发布在 https://github.com/THUDM/AgentBench。

| 操作系统 | 数据库 | 知识图谱 | 数字卡牌游戏 | 横向思维谜题 | 家务处理 | 网页购物 | 网页浏览 |
|---------|-------|---------|------------|-----------|--------|--------|--------|

**gpt-4 (0613)** | **claude-3 (opus)** | **glm-4** | **codellama-34b-instruct** | **vicuna-13b-v1.5** | **llama-2-70b**

**(a) 典型LLM在AgentBench各环境中相对于最佳模型的性能（相对值）**

**(b) AgentBench在8个环境中的总体得分。虚线表示两类LLM的平均值。**

**图1: LLM在AGENTBENCH上的概览。虽然LLM开始展现出作为智能体的能力，但模型之间的差距以及与实际可用性的距离仍然显著。**

## 1 引言

历史上，能够在特定环境中进行决策和行动执行的智能体和自主实体（Searle, 1970; Maes, 1994; Wooldridge & Jennings, 1995）一直是人工智能的核心概念。尽管深度学习算法在计算机视觉和自然语言处理方面取得了重大进展，但其在开发高效实用的辅助智能体方面的潜力在很大程度上仍未得到探索。

*XL、HY和HZ为共同第一作者。
‡通讯作者：YD和JT。
†HY和YG在访问清华大学期间完成此项工作。

大型语言模型（LLM）（Brown et al., 2020; Chowdhery et al., 2022; Touvron et al., 2023）的出现，如GPT-4（OpenAI, 2023），为这一领域带来了许多新的机遇。通过广泛的对齐训练（Ouyang et al., 2022; Wei et al., 2022a; Sanh et al., 2022），LLM不仅掌握了传统的NLP任务，还展现出理解人类意图和执行指令的令人印象深刻的能力。这推动了各种基于LLM的自主目标完成应用（如AutoGPT（Richards, 2023）、BabyAGI（Nakajima, 2023）、AgentGPT（age, 2023））以及置于社交和游戏环境中的LLM智能体（Park et al., 2023; Wang et al., 2023b; Zhu et al., 2023）的发展，引发了公众的广泛兴趣和讨论。

尽管取得了这些进展，但缺乏系统化、标准化的基准来评估LLM作为智能体的能力，这构成了一个关键挑战。历史上，基于文本的游戏环境（Osborne et al., 2022; Côté et al., 2019; Hausknecht et al., 2020; Urbanek et al., 2019）已被用于语言智能体评估。但它们常常受限于封闭、离散的动作空间，以及主要关注模型的常识基础能力。最近，具身智能体的尝试（Reed et al., 2022; Huang et al., 2022; Ahn et al., 2022; Li et al., 2022a）采用了基于游戏（Küttler et al., 2020; Fan et al., 2022）、GUI（Shi et al., 2017; Toyama et al., 2021）和室内场景（Shen et al., 2021; Srivastava et al., 2022）的复杂多模态模拟器。然而，这些模拟器尽管复杂，并不能准确反映LLM的实际使用场景，而且它们的多模态性质为急需评估现有纯文本LLM设置了障碍。最后，目前大多数智能体基准关注单一环境，因此未能提供跨不同应用场景的LLM全面概览。

为解决这些挑战，我们引入了AGENTBENCH，一个旨在跨一系列不同环境评估LLM作为智能体的多维度基准。AGENTBENCH包含八个不同的环境（参见图4，其中八个中有五个是首次创建的），可分为三种类型的场景：

- **代码类**：操作系统、数据库、知识图谱（Anonymous, 2023）
- **游戏类**：数字卡牌游戏、横向思维谜题、家务处理（Shridhar et al., 2020b）
- **网络类**：网页购物（Yao et al., 2022）、网页浏览（Deng et al., 2023）

所有数据集，无论是新创建的还是从现有数据集改编的，都经过精心设计和重构，以模拟纯文本LLM可以作为自主智能体运行的交互环境。因此，AGENTBENCH系统性地评估了LLM的核心能力，包括指令遵循（Ouyang et al., 2022）、编码（Chen et al., 2021）、知识获取（Joshi et al., 2017; Talmor et al., 2019）、逻辑推理（Srivastava et al., 2023）和常识基础（Shridhar et al., 2020a）。它既是LLM评估也是智能体评估的理想测试平台。

此外，我们开发了一个统一的评估工具包，使LLM能够在各种定制的智能体任务上运行，从而实现了对29种不同LLM在AGENTBENCH上的LLM-as-Agent能力的全面基准测试，包括基于API的和开源模型。我们的结果表明，像GPT-4这样的顶级模型能够处理广泛的现实世界任务，这表明确实存在开发强大、持续学习型智能体的潜力。然而，我们也注意到这些顶级模型与其开源竞争者之间存在显著的性能差距。尽管开源LLM最近取得了成功，并在一些基准测试中获得了有竞争力的分数（Li et al., 2023; Chen et al., 2021; Cobbe et al., 2021），但它们在具有挑战性的AGENTBENCH任务上的表现远远落后。这凸显了需要更多的努力来提高开源LLM的学习能力。

我们识别了不同环境和LLM中智能体任务失败的部分，揭示了现有LLM在长期推理、决策和指令遵循能力方面的不足。不同LLM之间的比较表明，引入代码训练的适当策略可以帮助改进LLM作为智能体的能力。在高质量数据（例如，由gpt-4生成的数据）上进行对齐训练也有助于改进LLM智能体。总之，我们的贡献是：

- 我们引入了评估LLM作为智能体的概念，并提出了AGENTBENCH，一个全面的基准来标准化评估。它定义了基于现实世界场景的3种类型的8个不同环境，为LLM的广泛能力提供了一个实用的测试平台。
- 我们使用AGENTBENCH对29种不同的LLM进行了彻底的评估，揭示了领先的基于API的商业LLM与许多不超过70B参数的开源模型之间的显著性能差距。我们还定量分析了现有LLM智能体失败的原因，并强调了改进方向，如提高指令遵循能力、使用更高质量的对齐数据。此外，我们表明代码训练可能是一把双刃剑，它改进了某些智能体任务而损害了其他任务。
- 为了促进LLM作为智能体的评估，我们引入了一个基于服务器-客户端架构的集成工具包，注重模块化和可扩展的设计原则。这使得任何LLM都可以通过HTTP协议轻松定制模型评估。配合其相关的数据集和环境，该工具包现已向更广泛的研究社区开放。

## 2 LLM作为智能体：定义与预备知识

在此，我们正式定义描述LLM作为智能体评估的术语，以及在智能体评估背景下使用LLM所需的预备知识。

**定义：LLM作为智能体的交互式评估。** LLM作为智能体的交互式评估可以被视为一个部分可观察马尔可夫决策过程（POMDP）⟨S, A, T, R, U, O⟩，包括状态空间S、动作空间A、转移函数T: S × A → S、奖励分配函数R、任务指令空间U和观察空间O。这里，我们将LLM智能体记为M。

**链式思考（CoT）及其他推理策略。** 由于LLM作为智能体需要LLM具备强大的推理能力，CoT（Wei et al., 2022b）——连同动作一起（Yao et al., 2023b）被认为是相关评估中的事实标准策略——也在AGENTBENCH中被采用。尽管后来提出了许多改进策略，如引入集成（Wang et al., 2023c）、反思（Shinn et al., 2023）和搜索（Yao et al., 2023a），我们在AGENTBENCH中使用最原始的CoT来评估LLM。无需多次试验、重复生成或复杂策略，CoT是人们部署LLM智能体最简单、最便宜和最常用的方式。

**典型的结束原因类型。** 尽管LLM具备能力，但我们在AGENTBENCH中表明，即使是最强大的gpt-4也不足以作为实际可用的智能体。我们将LLM智能体在AGENTBENCH任务上的结束原因识别并分类为五种典型类型：

- **上下文超限（CLE）**：交互历史的长度超过了LLM的最大上下文长度（仅发生在2,048长度的LLM，即text-davinci-002和003）。
- **无效格式（IF）**：智能体未遵循格式指令。
- **无效动作（IA）**：智能体遵循了格式指令，但其选择的动作无效。
- **任务超限（TLE）**：智能体在达到预定义的最大交互轮次后仍未解决问题，或开始重复生成多轮。
- **完成**：任务正常结束。

其中，IF和IA主要是由LLM指令遵循能力差引起的，而TLE通常表明在某些任务中多轮能力较弱。

## 3 AGENTBENCH的构成：简要概览

在本节中，我们简要介绍构成AGENTBENCH的数据集和环境。与以前的智能体评估基准（Côté et al., 2019; Fan et al., 2022）相比，AGENTBENCH专注于通过链式思考（CoT）（Wei et al., 2022b; Yao et al., 2023b）提示对LLM进行实际评估，包括代码场景、游戏场景和网络场景。它们为LLM的自主任务完成应用指明了有前景的方向，并且它们的多样性避免了特定任务模型（如代码专用LLM）在AGENTBENCH上过度表现。由于篇幅限制，关于构建、评估和提示示例的详细信息请参见附录。

### 3.1 代码类环境

由于LLM可以生成高质量的代码（Chen et al., 2021），LLM智能体的一个非常实用的任务是协助人类与计算机界面进行交互。这里，我们介绍三个依赖编码和推理能力的环境作为AGENTBENCH中的代表。

**操作系统（OS）。** 允许LLM在终端中访问和操作操作系统是一个迷人但具有挑战性的任务。尽管有尝试将自然语言转换为Shell命令（Lin et al., 2018），但很少有前期工作在可执行环境中评估模型。我们的目标是在真实的交互式bash环境（即Ubuntu Docker（Merkel et al., 2014））中评估LLM，处理具有确定性答案的人类问题（例如，操作系统中拥有非/home目录的用户数量）或为实现实际目标的一系列操作（例如，递归地将所有目录文件设置为只读，不包括我的文件）。我们采用**成功率（SR）**作为评估指标。（更多详情参见附录B）

**数据库（DB）。** 由于数据库分析在日常事务中至关重要但又困难重重，检查LLM通过SQL在真实数据库上操作的能力至关重要。先前的研究主要关注单个过程，如SQL与自然语言之间的转换（Zhong et al., 2017; Gao et al., 2023; Pourreza & Rafiei, 2023; Ruan et al., 2023），或给定单个小表回答问题（Nan et al., 2021; Iyyer et al., 2017）。然而，很少有人考虑将模型作为一个完整的流水线进行评估。因此，AGENTBENCH在真实的SQL接口、数据库和不同类型的查询上评估LLM，正如现实世界场景中所发现的那样。我们采用**SR**作为主要评估指标。（更多详情参见附录C）

**知识图谱（KG（Anonymous, 2023））。** 与当代知识图谱交互——这些知识图谱通常规模巨大（例如，FREEBASE（Bollacker et al., 2008）拥有超过4500万个实体和30亿个事实）——需要智能体具备广泛的技能（Gu et al., 2023）。在这样的环境中操作（该环境仅部分可观察）要求智能体在不完全信息下做出决策，并运用各种技能管理固有的不确定性，包括语言理解（例如，复杂性和细微差别）、规划（例如，将指令分解为更易管理的组成部分）和工具使用（例如，与KG接口交互）。因此，我们提出KG作为评估AI智能体决策能力的代表性测试场。我们采用问答作为基本任务形式，因此采用**答案F1**作为指标。（更多详情参见附录D）

### 3.2 游戏类环境

玩游戏通常需要强大的策略设计、指令遵循和推理能力。与代码类任务不同，游戏类环境中的任务不需要编码专业知识，而是需要对常识和世界知识有更全面的理解。

**数字卡牌游戏（DCG）。** 游戏通常可以作为智能体开发的模拟环境。DCG（例如，炉石传说（Hoover et al., 2020））是纯文本LLM的理想选择。它通常涉及丰富的卡牌文本描述，需要深思熟虑的获胜策略，测试模型对游戏规则、操作逻辑的理解以及基于游戏中当前情况形成战略决策的能力。在AGENTBENCH中，我们采用来自2021年清华大学智能体竞赛（THUAC）的简化DCG系统**Aquawar**来评估LLM作为智能体。在Aquawar中，智能体作为一个玩家，控制一队具有不同天赋的鱼，以回合制形式与另一个基于算法的队伍战斗。我们报告LLM的**胜率**作为评估指标。（更多详情参见附录E）

**横向思维谜题（LTP）。** 横向思维谜题（Sloane, 1992; De Bono, 1970），也称为情景谜题或**海龟汤**，是全球流行的团体游戏，推动参与者从非常规角度解开谜题。通常，一人主持，其他人通过策略性提问来猜测谜底，回答仅限于"是"、"否"或"无关"。在这个数据集中，我们首先建立了一个LTP主持系统用于自动评判。我们收集了各种基于网络的谜题，难度各异，并将情节简化为几个要点（即游戏进度）。通过这项评估，我们旨在深入了解LLM横向推理能力的深度和敏捷性。（更多详情参见附录F）

**家务处理（HH，ALFWorld（Shridhar et al., 2020b））。** 诸如家务处理等需要强常识基础的具身游戏环境，已经很好地建立用于语言智能体评估（Côté et al., 2019）。在AGENTBENCH中，我们在经典的ALFWorld（Shridhar et al., 2020b）上评估模型在物理家务环境中完成任务的能力，该数据集源自成熟的文本游戏工具包TextWorld（Côté et al., 2019）。智能体需要完成如"把平底锅放在餐桌上"之类的家务任务。我们采用**SR**作为评估指标。（更多详情参见附录G）

### 3.3 网络类环境

网页一直是人们在现实世界中进行交互的主要界面。因此，评估LLM智能体在复杂网络环境中的行为对于未来发展至关重要。在这里，我们改编了两个现有的网络浏览数据集，用于对LLM进行实际评估。

**网页购物（WS，WebShop（Yao et al., 2022））。** 在线购物是现代生活中非常实用和重要的部分。其轨迹包括在真实电子商务网站上搜索、查看和选择所需物品，这需要自主智能体具备强大的推理和决策能力。Webshop（Yao et al., 2022）是一个模拟的在线购物环境，正是为此目的而评估语言智能体。虽然它最初是在专门训练的模型上评估的，但我们提出仅使用提示来评估LLM。（更多详情参见附录H）

**网页浏览（WB，Mind2Web（Deng et al., 2023））。** 通用网络环境是训练和评估智能体的理想沙盒。Mind2Web（Deng et al., 2023）是一个最近发布的通用基准，用于开发和评估能够根据高级用户指令在各种网站领域执行复杂任务的网络智能体。它设计了可行的网站交互动作，如点击、选择和输入，从而促进了对LLM作为网络智能体的全面评估。与Mind2Web的原始设置相比，我们进行了调整，以允许对提示的LLM进行评估，无需额外的微调。（更多详情参见附录I）

## 4 AGENTBENCH的评估

我们广泛评估了29个LLM，包括基于API的商业模型和开源LLM，以形成对LLM作为智能体现有性能的系统性看法。我们还设计并发布了一个简单的即插即用评估工具包，以促进相关的LLM作为智能体的研究。

**表2: AGENTBENCH评估中8个环境的统计数据和指标。"SR"代表成功率。"#Avg. Round"表示解决单个问题所需的估计交互轮次数。在"#Dev"和"#Test"中，我们提供了查询样本数量和总预期交互轮次数。此外，"Weight−1"指的是在我们的评估中，所有模型在某个任务上的平均得分。**

| 指标 | 操作系统 | 数据库 | 知识图谱 | 数字卡牌游戏 | 横向思维谜题 | 家务处理 | 网页购物 | 网页浏览 |
|------|---------|-------|---------|------------|-----------|--------|--------|--------|
| #Avg. Round | 8 | 5 | 15 | 30 | 25 | 35 | 5 | 10 |
| 指标 | SR | SR | F1 | 奖励 | 游戏进度 | SR | 奖励 | 步骤SR |
| #Dev | 26/240 | 60/300 | 20/300 | 12/360 | 20/500 | 20/700 | 80/400 | 31/400 |
| #Test | 144/1200 | 300/1500 | 150/2250 | 20/600 | 50/1250 | 50/1750 | 200/1000 | 100/1000 |
| Weight−1 | 10.8 | 13.0 | 13.9 | 12.0 | 3.5 | 13.0 | 30.7 | 11.6 |

### 4.1 评估设置

**数据集统计。** 我们在表2中报告了AGENTBENCH数据集的统计数据。为简洁起见，后续部分将使用每个数据集的缩写。所有数据集都是实用的多轮交互挑战，每个问题的估计解决轮次从5到50不等。我们为每个数据集提供了两个划分：开发集和测试集。所有数据集都是公开可用的。

我们在AGENTBENCH设计中仔细平衡了评估的全面性和效率，因为LLM的多轮交互可能非常耗时。我们将开发集和测试集的大小分别设置为269和1,014，导致大约3k和11k次推理调用，大约与MMLU（Hendrycks et al., 2021b）所需的推理调用次数相同。

**待评估的LLM。** 作为对现有LLM在LLM-as-Agent方面进行基准测试的系统尝试，我们总共纳入了29个模型进行评估，这些模型大致可分为两类：

- **基于API的商业LLM**：主要包括未公开参数数量的LLM API（参见表1）。由于投入更多，它们的性能通常更好。
- **开源（OSS）LLM**：主要来自学术界和一些公司（参见表1）。由于计算资源有限，这里我们只包含小于70B的开源LLM。值得注意的是，这个规模已经涵盖了大多数表现出色且经过特定聊天或指令任务微调的开源LLM（极少数例外）。

**工具包：以API为中心的方法和环境隔离简化LLM评估。** 随着LLM系统在复杂性上的不断进步且主要通过API访问，我们开发了一个与API导向理念一致的评估工具包。该工具包经过精心设计，可与API交互，简化了适配和测试不同LLM的过程。有兴趣在AGENTBENCH上评估其LLM的研究人员只需设置一个可通过HTTP协议访问的模型服务器即可。

此外，处理多样且复杂的交互环境是一个重大挑战。统一配置所有这些环境可能很困难，并可能导致冲突。为解决这个问题，我们实施了两种关键策略。首先，我们将具有复杂环境的任务封装到Docker镜像中。研究人员可以通过挂载代码路径并轻松启动评估过程来使用这些镜像。其次，我们将每个任务细分为独立的工作进程，确保这些任务的环境保持隔离且无冲突。（更多详情请参见附录A。）

**评估提示设置。** 为了适应大多数现有的对话模型，我们的对话范例如下结构化：两个角色——用户（即指令和环境反馈）和智能体——相互交替进行。我们将交互轨迹记录为涉及用户和智能体的对话历史(u0, a0, ..., uk, ak)，其中ui, ai表示对话历史的第i轮。当我们进行推理时，对话历史应符合(u0, a0, ..., uk)的格式。我们选择最小的r使得(u0, ar, ur+1, ..., uk)中所有token的数量不超过3500。然后我们将"[注意] 已省略2r条消息。"附加到u0中。之后，序列(u0, ar, ur+1, ..., uk)被视为多轮聊天格式的最终输入。

然而，为了考虑非聊天模型，我们附加了一个后处理器。对于支持多轮的聊天模型，我们将历史输入模型。对于仅支持文本补全的模型（如text-davinci-003），我们在历史中的每个项目前添加"USER:"或"AGENT:"，最后添加字符串"AGENT:"以使模型生成智能体的内容。

对于任务提示组织，我们改编了（Yao et al., 2023b）的格式，将"思考"（用于CoT）和"动作"都包含在同一轮中。通常，任务指令中会提供一个简单的CoT演示，以获得更好的输出格式。为确保结果的可重复性，我们在所有任务的推理中设置temperature=0（即贪心解码），遵循（Wei et al., 2022b）的做法。

**总体得分计算。** 我们观察到，由于任务难度不同，每个任务的分数分布差异很大。因此，简单平均的分数会受到通常得分较高的任务（例如，我们观察到的网页购物）的严重影响，掩盖了得分较低的任务，不适合AGENTBENCH的目的。因此，我们首先生成总体得分，方法是将我们评估的所有模型中每个任务的平均得分调整到1，然后对每个模型的所有任务得分进行平均（参见表2）。为标准化和简化未来研究的分数计算，我们利用所有测试LLM在每个任务中的倒数平均得分作为未来总体得分计算的固定权重。然后，总得分通过将每个任务的得分乘以其相应权重后获得的平均值来计算。这种方法确保了评估的公平性和一致性，使得未来研究中更容易进行比较和分析。

### 4.2 主要结果

AGENTBENCH中的总体和数据集特定得分报告在表3中。令人惊讶的是，在这个具有挑战性的基准测试上，我们发现一些顶级LLM具备了处理现实世界环境交互的扎实能力。例如，gpt-4在AGENTBENCH的8个数据集中的6个上表现最佳；在家务处理中，它达到了78%的成功率，表明其在此场景中的实际可用性。claude-2和claude紧随gpt-4之后，但明显优于gpt-3.5-turbo。尽管其他基于API的LLM性能相对较差，但无论任务如何，它们中的大多数都能解决一定比例的问题。所有基于API的LLM的AGENTBENCH总体得分均高于1.00。

**表3: AGENTBENCH测试集（标准）结果。顶级商业LLM（如gpt-4）与开源LLM竞争者之间存在明显的性能差距。"VER"代表模型版本；"OA"代表AGENTBENCH总体得分，是所有环境的加权平均值（参见第4.1节）。**

| LLM类型 | 模型 | VER | OA | 代码类 |  |  | 游戏类 |  |  | 网络类 |  |
|---------|------|-----|-----|--------|--|--|--------|--|--|--------|--|
|  |  |  |  | 操作系统 | 数据库 | 知识图谱 | 数字卡牌游戏 | 横向思维谜题 | 家务处理 | 网页购物 | 网页浏览 |
| **API** | gpt-4 | 0613 | **4.01** | 42.4 | 32.0 | 58.8 | 74.5 | 16.6 | 78.0 | 61.1 | 29.0 |
|  | claude-3 | opus | 3.11 | 22.9 | 51.7 | 34.6 | 44.5 | 14.3 | 70.0 | 27.9 | 26.0 |
|  | glm-4 | - | 2.89 | 29.2 | 42.3 | 46.3 | 34.1 | 14.2 | 34.0 | 61.6 | 27.0 |
|  | claude-2 | - | 2.49 | 18.1 | 27.3 | 41.3 | 55.5 | 8.4 | 54.0 | 61.4 | 0.0 |
|  | claude | v1.3 | 2.44 | 9.7 | 22.0 | 38.9 | 40.9 | 8.2 | 58.0 | 55.7 | 25.0 |
|  | gpt-3.5-turbo | 0613 | 2.32 | 32.6 | 36.7 | 25.9 | 33.7 | 10.5 | 16.0 | 64.1 | 20.0 |
|  | text-davinci-003 | - | 1.71 | 20.1 | 16.3 | 34.9 | 3.0 | 7.1 | 20.0 | 61.7 | 26.0 |
|  | claude-instant | v1.1 | 1.60 | 16.7 | 18.0 | 20.8 | 5.9 | 12.6 | 30.0 | 49.7 | 4.0 |
|  | chat-bison-001 | - | 1.39 | 9.7 | 19.7 | 23.0 | 16.6 | 4.4 | 18.0 | 60.5 | 12.0 |
|  | text-davinci-002 | - | 1.25 | 8.3 | 16.7 | 41.5 | 11.8 | 0.5 | 16.0 | 56.3 | 9.0 |
| **OSS(大)** | llama-2-70b | chat | 0.78 | 9.7 | 13.0 | 8.0 | 21.3 | 0.0 | 2.0 | 5.6 | 19.0 |
|  | guanaco-65b | - | 0.54 | 8.3 | 14.7 | 1.9 | 0.1 | 1.5 | 12.0 | 0.9 | 10.0 |
| **OSS(中)** | codellama-34b | instruct | 0.96 | 2.8 | 14.0 | 23.5 | 8.4 | 0.7 | 4.0 | 52.1 | 20.0 |
|  | vicuna-33b | v1.3 | 0.73 | 15.3 | 11.0 | 1.2 | 16.3 | 1.0 | 6.0 | 23.9 | 7.0 |
|  | wizardlm-30b | v1.0 | 0.46 | 13.9 | 12.7 | 2.9 | 0.3 | 1.8 | 6.0 | 4.4 | 1.0 |
|  | guanaco-33b | - | 0.39 | 11.1 | 9.3 | 3.2 | 0.3 | 0.0 | 6.0 | 6.2 | 5.0 |
| **OSS(小)** | vicuna-13b | v1.5 | 0.93 | 10.4 | 6.7 | 9.4 | 0.1 | 8.0 | 8.0 | 41.7 | 12.0 |
|  | llama-2-13b | chat | 0.77 | 4.2 | 11.7 | 3.6 | 26.4 | 0.0 | 6.0 | 25.3 | 13.0 |
|  | openchat-13b | v3.2 | 0.70 | 15.3 | 12.3 | 5.5 | 0.1 | 0.0 | 0.0 | 46.9 | 15.0 |
|  | wizardlm-13b | v1.2 | 0.66 | 9.0 | 12.7 | 1.7 | 1.9 | 0.0 | 10.0 | 43.7 | 12.0 |
|  | vicuna-7b | v1.5 | 0.56 | 9.7 | 8.7 | 2.5 | 0.3 | 6.4 | 0.0 | 2.2 | 9.0 |
|  | codellama-13b | instruct | 0.56 | 3.5 | 9.7 | 10.4 | 0.0 | 0.0 | 0.0 | 43.8 | 14.0 |
|  | codellama-7b | instruct | 0.50 | 4.9 | 12.7 | 8.2 | 0.0 | 0.0 | 2.0 | 25.2 | 12.0 |
|  | koala-13b | - | 0.34 | 3.5 | 5.0 | 0.4 | 0.1 | 4.4 | 0.0 | 3.9 | 7.0 |
|  | llama-2-7b | chat | 0.34 | 4.2 | 8.0 | 2.1 | 6.9 | 0.0 | 0.0 | 11.6 | 7.0 |
|  | codegeex2-6b | - | 0.27 | 1.4 | 0.0 | 4.8 | 0.3 | 0.0 | 0.0 | 20.9 | 11.0 |
|  | dolly-12b | v2 | 0.14 | 0.0 | 0.0 | 0.0 | 0.1 | 1.2 | 0.0 | 0.4 | 9.0 |
|  | chatglm-6b | v1.1 | 0.11 | 4.9 | 0.3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5 | 4.9 |
|  | oasst-12b | sft-4 | 0.03 | 1.4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.3 | 1.0 |

我们测试的开源LLM通常无法解决某些具有挑战性任务中的问题，如知识图谱、数字卡牌游戏和家务处理。我们在图3中绘制了它们的性能与模型规模的关系。总体而言，大多数开源LLM在AGENTBENCH上的表现远差于基于API的LLM（平均0.51对比2.32）。评估范围内最强大的不超过70B的开源LLM是codellama-34b，总体得分为0.96，但与gpt-3.5-turbo仍有明显的性能差距。我们的社区仍需要付出大量努力来产生更强大的开源LLM。

**图3: 所有测试的开源LLM的AGENTBENCH OA得分与参数规模的关系。**

### 4.3 分析

在评估中，我们分析了一些影响LLM智能体在AGENTBENCH上性能的重要因素，包括执行结果比例分析、代码训练以及基于API的商业LLM与开源LLM竞争者之间的差异。更多关于规划、自我纠正和工具使用能力的见解和案例研究见附录J.2。

**不同类型执行结果的比例。** 表4报告了执行结果的比例（参见第2节）。AGENTBENCH任务中最主要的失败原因是**任务超限**，揭示了LLM推理和决策能力的薄弱。这一数据支撑了现有LLM的弱点，可能指导未来的发展（请参考我们的框架）。

在数据库和数字卡牌游戏任务中，由于严格的格式要求，**无效格式**错误经常发生（参见附录J.2.1）。相反，家务处理和网页浏览任务经常面临**无效动作**错误，这是因为LLM生成了超出预定义动作空间的动作。更多详细比例请参见附录J.1。

**表4: 所有模型平均的8种任务中不同类型执行结果的比例。（CLE: 上下文超限, TLE: 任务超限）**

|  | 操作系统 | 数据库 | 知识图谱 | 数字卡牌游戏 | 横向思维谜题 | 家务处理 | 网页购物 | 网页浏览 |
|--|---------|-------|---------|------------|-----------|--------|--------|--------|
| 已完成 | 75.0 | 37.9 | 30.1 | 51.2 | 14.0 | 13.1 | 54.9 | 56.6 |
| CLE | 0.1 | 0.7 | 2.0 | 0.0 | 3.5 | 0.7 | 0.0 | 0.0 |
| 无效格式 | 0.0 | 53.3 | 0.0 | 38.5 | 0.0 | 0.0 | 17.2 | 0.0 |
| 无效动作 | 0.9 | 0.0 | 0.0 | 10.2 | 0.0 | 64.1 | 0.0 | 8.4 |
| TLE | 23.9 | 8.0 | 67.9 | 0.0 | 82.5 | 22.1 | 27.8 | 35.0 |

**代码训练的矛盾影响。** 我们发现代码微调可能会深刻影响模型的推理生成和思维方式，甚至超越纯编码主题。从codellama和llama-2系列的比较来看，代码微调似乎使模型在遵循相对静态程序的任务（如网页购物）中具有优势。但是，这种微调也可能影响模型的通用思维能力，因为codellama系列在数字卡牌游戏中的表现不如llama-2系列，在操作系统中也是如此——与Linux系统交互比编写bash代码更重要。这指出了在微调LLM时，擅长遵循程序和擅长通用思维之间需要保持平衡。

**高质量对齐数据训练的影响。** 另一个有用的比较是vicuna-13b和llama-2-13b。虽然它们共享相同的基础LLM，但vicuna-13b通过在ShareGPT数据（由gpt-4和gpt-3.5-turbo生成、由用户共享）上进行训练而对齐，而llama-2-13b是从头开始对齐的。结果，vicuna-13b在AGENTBENCH上优于llama-2-13b，甚至与三倍大的codellama-34b表现相当。这表明高质量对齐仍然是开发更好的LLM智能体的关键。

**llama-2-13b和llama-2-70b出乎意料的相似性能。** 在我们的实验中，我们惊讶地发现，尽管llama-2-13b和llama-2-70b的规模存在显著差距，但它们的表现相似。在仔细检查和重新运行实验后，结果没有变化。我们认为这表明llama-2-70b的预训练不足。虽然llama-2-13b和llama-2-70b都使用了2T个token进行预训练，但根据缩放定律（Hoffmann et al., 2022），更大的LLM应该使用更多的token进行训练。另一个可能的原因是llama-2-70b在指令遵循方面没有充分对齐，导致其遵循指令的能力相对滞后（参见附录J.2.5）。

## 5 相关工作

**LLM的评估。** 自监督（Liu et al., 2021）LLM（Brown et al., 2020; Chowdhery et al., 2022; Zhang et al., 2022; Scao et al., 2022; Zeng et al., 2022; Touvron et al., 2023），特别是那些经过聊天对齐的LLM（Ouyang et al., 2022; Anthropic, 2023a; OpenAI, 2023）的通用能力，刷新了人们对深度学习系统的印象，并显著超越了传统NLP评估的范围。这使得LLM的评估成为一个紧迫且具有挑战性的问题。与以往专注于特定任务子集的工作（Wang et al., 2019; Wang et al.; Gehrmann et al., 2021）相比，越来越多的基准测试在评估中包含了更广泛的任务和数据集谱系（Hendrycks et al., 2021b; Liang et al., 2022; Srivastava et al., 2023）。然而，它们中的大多数仍然局限于传统任务，因此未能评估LLM的开放式生成、多轮交互和作为智能体的能力。

**LLM作为智能体。** 在前LLM时代，基于BERT（Devlin et al., 2019）和强化学习的文本游戏环境如TextWorld（Côté et al., 2019）、Jericho（Hausknecht et al., 2020）和LIGHT（Urbanek et al., 2019）在语言智能体研究中占主导地位。随着LLM的出现，LLM智能体的研究开始蓬勃发展（Huang et al., 2022），尤其是在链式思考（Wei et al., 2022b）出现之后。ReAct（Yao et al., 2023b）是将CoT推理和动作结合到智能体任务中的先驱工作。后来，出现了大量高级推理策略（Kim et al., 2023; Shinn et al., 2023; Wang et al., 2023d; Liu et al., 2023; Yao et al., 2023a; Gu et al., 2023）和应用程序，包括框架（Richards, 2023; Nakajima, 2023; age, 2023）和多智能体系统（Park et al., 2023; Hong et al., 2023; Wu et al., 2023），引起了公众的极大兴趣。然而，关于该主题的数据集和模型有限，缺乏标准的全面基准。AGENTBENCH提出了第一个系统性的基准，用于评估LLM作为智能体，涵盖了广泛的任务和可用的LLM。此外，它还开创了采用智能体任务来衡量LLM性能的想法。

**在可执行环境中评估LLM。** 随着LLM在处理现实世界挑战方面变得越来越强大，也出现了一种趋势，即在可执行环境中而不是静态数据集中评估它们。除了文本游戏（如ALFWorld（Shridhar et al., 2020b））之外，另一主要工作流在于代码执行。APPS（Hendrycks et al., 2021a）、HumanEval（Chen et al., 2021）和MBPP（Austin et al., 2021）开创了评估代码LLM的功能正确性而非文本相似性的先河。该范式后来被广泛认可并在后续工作中采用（Li et al., 2022b; Zheng et al., 2023; Nijkamp et al., 2023）。然而，很少有先前的代码评估框架考虑多轮交互。一项同期工作InterCode（Yang et al., 2023）发布了一个框架，允许评估模型与Bash和SQL环境之间的交互，这类似于AGENTBENCH中的OS和DB任务。

## 6 结论

我们提出了AGENTBENCH，一个系统设计的、多维度的、不断发展的基准，用于评估LLM作为智能体，首次涵盖了多达29个LLM，为敏捷评估建立了统一的测试框架和工具包。基于评估，我们呈现了关于智能体任务、LLM行为以及改进LLM在AGENTBENCH上表现的潜在方法的广泛见解。我们期望AGENTBENCH将为后续的LLM智能体研究奠定基础。

## 致谢

我们要感谢匿名审稿人和Shunyu Yao对本工作改进的建议，以及智谱AI承担本研究中产生的所有GPU和API费用。Yuxiao Dong得到国家自然科学基金（NSFC）62276148的支持。Jie Tang得到科技部科技创新2030—"新一代人工智能"重大项目2022ZD0118600、国家自然科学基金杰出青年科学基金61825602、清华大学自主科研计划20233080067以及新基石科学基金会通过科学探索奖的支持。本工作还得到智谱AI的研究基金支持。

---

## 参考文献

（此处保留原文所有参考文献，为节省篇幅以原文为准）

Agentgpt. Python. https://github.com/reworkd/AgentGPT, 2023.

Michael Ahn, Anthony Brohan, Noah Brown, Yevgen Chebotar, Omar Cortes, Byron David, Chelsea Finn, Chuyuan Fu, Keerthana Gopalakrishnan, Karol Hausman, et al. Do as i can, not as i say: Grounding language in robotic affordances. arXiv preprint arXiv:2204.01691, 2022.

Rohan Anil, Andrew M Dai, Orhan Firat, Melvin Johnson, Dmitry Lepikhin, Alexandre Passos, Siamak Shakeri, Emanuel Taropa, Paige Bailey, Zhifeng Chen, et al. Palm 2 technical report. arXiv preprint arXiv:2305.10403, 2023.

Anonymous. Knowledge base question answering as tool learning. under review, 2023.

Anthropic. Introducing claude, 2023a. URL https://www.anthropic.com/index/introducing-claude.

Anthropic. Claude 2, 2023b. URL https://www.anthropic.com/index/claude-2.

Anthropic. Introducing the next generation of claude, 2024. URL https://www.anthropic.com/news/claude-3-family.

Jacob Austin, Augustus Odena, Maxwell Nye, Maarten Bosma, Henryk Michalewski, David Dohan, Ellen Jiang, Carrie Cai, Michael Terry, Quoc Le, et al. Program synthesis with large language models. arXiv preprint arXiv:2108.07732, 2021.

Kurt D. Bollacker, Colin Evans, Praveen K. Paritosh, Tim Sturge, and Jamie Taylor. Freebase: a collaboratively created graph database for structuring human knowledge. In Proceedings of the ACM SIGMOD International Conference on Management of Data, SIGMOD 2008, pp. 1247–1250, 2008.

Tom B. Brown et al. Language models are few-shot learners. In NIPS'20, 2020.

Mark Chen et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021.

Wei-Lin Chiang et al. Vicuna: An open-source chatbot impressing gpt-4 with 90%* chatgpt quality. 2023.

Aakanksha Chowdhery et al. Palm: Scaling language modeling with pathways. arXiv preprint arXiv:2204.02311, 2022.

Karl Cobbe et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.

Mike Conover et al. Free dolly: Introducing the world's first truly open instruction-tuned llm, 2023.

Marc-Alexandre Côté et al. Textworld: A learning environment for text-based games. In Computer Games: 7th Workshop, CGW 2018, pp. 41–75, 2019.

Edward De Bono. Lateral thinking. New York, pp. 70, 1970.

Xiang Deng et al. Mind2web: Towards a generalist agent for the web. arXiv preprint arXiv:2306.06070, 2023.

Tim Dettmers et al. Qlora: Efficient finetuning of quantized llms. arXiv preprint arXiv:2305.14314, 2023.

Jacob Devlin et al. Bert: Pre-training of deep bidirectional transformers for language understanding. In NAACL-HLT 2019, pp. 4171–4186, 2019.

Zhengxiao Du et al. Glm: General language model pretraining with autoregressive blank infilling. In ACL 2022, pp. 320–335, 2022.

Jack Edmonds and Richard M Karp. Theoretical improvements in algorithmic efficiency for network flow problems. JACM, 19(2):248–264, 1972.

Linxi Fan et al. Minedojo: Building open-ended embodied agents with internet-scale knowledge. NeurIPS, 35:18343–18362, 2022.

Dawei Gao et al. Text-to-sql empowered by large language models: A benchmark evaluation. arXiv preprint arXiv:2308.15363, 2023.

Sebastian Gehrmann et al. The gem benchmark: Natural language generation, its evaluation and metrics. In GEM 2021, pp. 96–120, 2021.

Xinyang Geng et al. Koala: A dialogue model for academic research. Blog post, April, 1, 2023.

Yu Gu et al. Beyond i.i.d.: Three levels of generalization for question answering on knowledge bases. In WWW 2021, 2021.

Yu Gu, Xiang Deng, and Yu Su. Don't generate, discriminate: A proposal for grounding language models to real-world environments. In ACL 2023, pp. 4928–4949, 2023.

Matthew Hausknecht et al. Interactive fiction games: A colossal adventure. In AAAI, 34:7903–7910, 2020.

Dan Hendrycks et al. Measuring coding challenge competence with apps. arXiv preprint arXiv:2105.09938, 2021a.

Dan Hendrycks et al. Measuring massive multitask language understanding. In ICLR, 2021b.

Jordan Hoffmann et al. Training compute-optimal large language models. arXiv preprint arXiv:2203.15556, 2022.

Sirui Hong et al. Metagpt: Meta programming for multi-agent collaborative framework. arXiv, abs/2308.00352, 2023.

Amy K Hoover et al. The many ai challenges of hearthstone. KI-Künstliche Intelligenz, 34:33–43, 2020.

Wenlong Huang et al. Language models as zero-shot planners: Extracting actionable knowledge for embodied agents. In ICML, pp. 9118–9147, 2022.

Mohit Iyyer et al. Search-based neural structured learning for sequential question answering. In ACL 2017, pp. 1821–1831, 2017.

Mandar Joshi et al. Triviaqa: A large scale distantly supervised challenge dataset for reading comprehension. In ACL 2017, pp. 1601–1611, 2017.

Geunwoo Kim et al. Language models can solve computer tasks. arXiv preprint arXiv:2303.17491, 2023.

Heinrich Küttler et al. The nethack learning environment. NeurIPS, 33:7671–7684, 2020.

LAION. Open-assistant. https://github.com/LAION-AI/Open-Assistant, 2023.

Shuang Li et al. Pre-trained language models for interactive decision-making. In NeurIPS, 2022a.

Xuechen Li et al. Alpacaeval: An automatic evaluator of instruction-following models, 2023.

Yujia Li et al. Competition-level code generation with alphacode. Science, 378(6624):1092–1097, 2022b.

Percy Liang et al. Holistic evaluation of language models. arXiv preprint arXiv:2211.09110, 2022.

Chin-Yew Lin. ROUGE: A package for automatic evaluation of summaries. In Text Summarization Branches Out, pp. 74–81, 2004.

Xi Victoria Lin et al. Nl2bash: A corpus and semantic parser for natural language interface to the linux operating system. In LREC 2018, 2018.

Bo Liu et al. Llm+ p: Empowering large language models with optimal planning proficiency. arXiv preprint arXiv:2304.11477, 2023.

Xiao Liu et al. Self-supervised learning: Generative or contrastive. IEEE TKDE, 35(1):857–876, 2021.

Pattie Maes. Agents that reduce work and information overload. CACM, 37:30–40, 1994.

Dirk Merkel et al. Docker: lightweight linux containers for consistent development and deployment. Linux j, 239(2):2, 2014.

Yohei Nakajima. Babyagi. Python. https://github.com/yoheinakajima/babyagi, 2023.

Linyong Nan et al. Fetaqa: Free-form table question answering, 2021.

Erik Nijkamp et al. Codegen: An open large language model for code with multi-turn program synthesis. In ICLR, 2023.

OpenAI. Introducing chatgpt, 2022. URL https://openai.com/blog/chatgpt.

R OpenAI. Gpt-4 technical report. arXiv, pp. 2303–08774, 2023.

Philip Osborne et al. A survey of text games for reinforcement learning informed by natural language. TACL, 10:873–887, 2022.

Long Ouyang et al. Training language models to follow instructions with human feedback. NeurIPS, 35:27730–27744, 2022.

Joon Sung Park et al. Generative agents: Interactive simulacra of human behavior. arXiv, abs/2304.03442, 2023.

Mohammadreza Pourreza and Davood Rafiei. Din-sql: Decomposed in-context learning of text-to-sql with self-correction. arXiv preprint arXiv:2304.11015, 2023.

Scott Reed et al. A generalist agent. TMLR, 2022.

Toran Bruce Richards. Auto-gpt: An autonomous gpt-4 experiment, 2023.

Baptiste Rozière et al. Code llama: Open foundation models for code. arXiv preprint arXiv:2308.12950, 2023.

Jingqing Ruan et al. Tptu: Task planning and tool usage of large language model-based ai agents. arXiv preprint arXiv:2308.03427, 2023.

Victor Sanh et al. Multitask prompted training enables zero-shot task generalization. In ICLR, 2022.

Teven Le Scao et al. Bloom: A 176b-parameter open-access multilingual language model. arXiv preprint arXiv:2211.05100, 2022.

John R. Searle. Speech acts: An essay in the philosophy of language. Language, 46:217, 1970.

Bokui Shen et al. igibson 1.0: A simulation environment for interactive tasks in large realistic scenes. In IROS 2021, pp. 7520–7527, 2021.

Tianlin Shi et al. World of bits: An open-domain platform for web-based agents. In ICML, pp. 3135–3144, 2017.

Noah Shinn et al. Reflexion: an autonomous agent with dynamic memory and self-reflection. arXiv preprint arXiv:2303.11366, 2023.

Mohit Shridhar et al. Alfred: A benchmark for interpreting grounded instructions for everyday tasks. In CVPR 2020, pp. 10740–10749, 2020a.

Mohit Shridhar et al. Alfworld: Aligning text and embodied environments for interactive learning. In ICLR, 2020b.

Paul Sloane. Lateral thinking puzzlers. Sterling Publishing Company, Inc., 1992.

Aarohi Srivastava et al. Beyond the imitation game: Quantifying and extrapolating the capabilities of language models. TMLR, 2023.

Sanjana Srivastava et al. Behavior: Benchmark for everyday household activities in virtual, interactive, and ecological environments. In CoRL, pp. 477–490, 2022.

Alon Talmor and Jonathan Berant. The web as a knowledge-base for answering complex questions. In NAACL-HLT 2018, pp. 641–651, 2018.

Alon Talmor et al. Commonsenseqa: A question answering challenge targeting commonsense knowledge. In NAACL-HLT 2019, pp. 4149–4158, 2019.

Hugo Touvron et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023.

Daniel Toyama et al. Androidenv: A reinforcement learning platform for android. arXiv preprint arXiv:2105.13231, 2021.

Jack Urbanek et al. Learning to speak and act in a fantasy text adventure game. In EMNLP-IJCNLP 2019, pp. 673–683, 2019.

Alex Wang et al. Glue: A multi-task benchmark and analysis platform for natural language understanding. In ICLR.

Alex Wang et al. Superglue: A stickier benchmark for general-purpose language understanding systems. NeurIPS, 32, 2019.

Guan Wang et al. Openchat: Advancing open-source language models with mixed-quality data, 2023a.

Guanzhi Wang et al. Voyager: An open-ended embodied agent with large language models. arXiv, abs/2305.16291, 2023b.

Xuezhi Wang et al. Self-consistency improves chain of thought reasoning in language models. In ICLR, 2023c.

Zihao Wang et al. Describe, explain, plan and select: Interactive planning with large language models enables open-world multi-task agents. arXiv preprint arXiv:2302.01560, 2023d.

Jason Wei et al. Finetuned language models are zero-shot learners. In ICLR, 2022a.

Jason Wei et al. Chain-of-thought prompting elicits reasoning in large language models. NeurIPS, 35:24824–24837, 2022b.

Michael Wooldridge and Nicholas R Jennings. Intelligent agents: Theory and practice. Knowledge engineering review, 10(2):115–152, 1995.

Qingyun Wu et al. Autogen: Enabling next-gen llm applications via multi-agent conversation framework. arXiv, abs/2308.08155, 2023.

Can Xu et al. Wizardlm: Empowering large language models to follow complex instructions. arXiv preprint arXiv:2304.12244, 2023.

John Yang et al. Intercode: Standardizing and benchmarking interactive coding with execution feedback. arXiv preprint arXiv:2306.14898, 2023.

Shunyu Yao et al. Webshop: Towards scalable real-world web interaction with grounded language agents. NeurIPS, 35:20744–20757, 2022.

Shunyu Yao et al. Tree of thoughts: Deliberate problem solving with large language models. arXiv preprint arXiv:2305.10601, 2023a.

Shunyu Yao et al. React: Synergizing reasoning and acting in language models. In ICLR, 2023b.

Aohan Zeng et al. Glm-130b: An open bilingual pre-trained model. arXiv preprint arXiv:2210.02414, 2022.

Susan Zhang et al. Opt: Open pre-trained transformer language models. arXiv preprint arXiv:2205.01068, 2022.

Qinkai Zheng et al. Codegeex: A pre-trained model for code generation with multilingual evaluations on humaneval-x. arXiv preprint arXiv:2303.17568, 2023.

Victor Zhong et al. Seq2sql: Generating structured queries from natural language using reinforcement learning. CoRR, abs/1709.00103, 2017.

Xizhou Zhu et al. Ghost in the minecraft: Generally capable agents for open-world environments via large language models with text-based knowledge and memory. arXiv, abs/2305.17144, 2023.

---

# 第一部分：附录

## 目录

**A 框架** 
- A.1 传统评估框架
- A.2 我们设计的评估框架
- A.3 最大流算法的实现

**B 操作系统**
- B.1 数据集详情
- B.2 动作
- B.3 提示示例

**C 数据库**
- C.1 数据集详情
- C.2 数据增强
- C.3 提示示例
- C.4 数据增强中的偏差研究

**D 知识图谱**
- D.1 数据集详情
- D.2 提示示例

**E 数字卡牌游戏**
- E.1 数据集详情
- E.2 鱼的属性
- E.3 提示示例
- E.4 战斗生成

**F 横向思维谜题**
- F.1 数据集详情
- F.2 LTP系统评估
- F.3 LTP游戏进度与终止
- F.4 提示示例

**G 家务处理**
- G.1 数据集详情
- G.2 提示示例

**H 网页购物**
- H.1 数据集详情
- H.2 提示示例

**I 网页浏览**
- I.1 数据集详情
- I.2 提示示例

**J 详细分析**
- J.1 执行结果的有效性分析
- J.2 研究发现

---

## A 框架

### A.1 传统评估框架

传统的评估框架可分为两类：

**传统任务（如单轮生成、分类等）。** 这些框架是为特定任务设计的，可能不适用于涉及多轮交互的更复杂任务。

**基于智能体的任务（具有多轮交互的任务）。** 这些框架通常由数据集的创建者针对特定任务定制。它们通常存在以下几个局限性：
- 它们是为特定任务设计的，限制了其对其他任务的适用性。
- 组件（任务、智能体和评估）之间的通信通常发生在单个进程内或通过创建子进程进行，需要在同一设备上进行评估。
- 它们一次只能评估一个智能体的一个任务。

### A.2 我们设计的评估框架

为解决传统基于智能体的评估框架的局限性，我们设计了一个具有以下功能的新型框架：

**解耦的S/C架构。** 我们的框架将任务服务器、智能体服务器和评估客户端组件解耦，使它们可以独立部署。它们可以通过HTTP交互进行通信，允许它们在不同的设备上运行，从而消除了为了同时满足任务和智能体需求而必须位于同一位置的要求。

**智能体-任务协同评估。** 我们的框架支持同时以各种组合对多个智能体和任务进行协同评估。这种灵活性使得测试场景更加全面。

**网络流算法。** 我们已将网络流算法纳入评估客户端，最大限度地提高了评估效率。这种优化确保智能体和工作进程都得到充分利用。

**可恢复评估。** 我们的框架包括一个可恢复的评估功能，使得在中断时可以无缝恢复和继续评估。

凭借这些进步，我们的评估框架克服了传统方法的局限性，为评估多轮任务中的智能体提供了更通用、高效和可扩展的解决方案。

我们框架的整体结构如图5所示。

**图5: AGENTBENCH的工具包经过精心设计，用于任务和智能体的无缝部署，以及高效的评估分配系统。智能体服务器（左侧）以多种形式存在，使我们能够部署模型服务器并通过HTTP协议公开可访问的API。任务服务器（右侧）由任务控制器和多个任务工作进程组成，其环境位于隔离环境中，确保无冲突和最佳的任务执行。评估客户端（中心）建立智能体-任务图，并使用最大流算法优化交互。这种优化使客户端工作者能够与智能体和任务服务器无缝交互，促进任务和评估的顺利执行。**

### A.3 最大流算法的实现

在我们的评估过程中，我们采用Edmonds-Karp算法（Edmonds & Karp, 1972）作为Ford-Fulkerson方法（Ford Jr & Fulkerson, 1962）的实用实现，用于计算网络中的最大流，时间复杂度为O(|V||E|²)。

为了形式化该问题，考虑有n个智能体的场景，记为A1, A2, ..., An，以及m个任务，记为T1, T2, ..., Tm。我们的目标是在l个不同的组中进行评估，每个组关注一对(Axk, Tyk)，其中1 ≤ k ≤ l。此外，对于每一对(Axk, Tyk)，我们应该评估sk个样本。智能体Ak和任务Tk的工作进程数量分别记为w(Ak)和w(Tk)。

我们构建的流图可以描述为G = <V, E>，其中顶点集V定义为：

V = {Ak | 1 ≤ k ≤ n} ∪ {Tk | 1 ≤ k ≤ m} ∪ {S, D}  (1)

加权边集E定义为：

E = {(Axk, Tyk, sk) | 1 ≤ k ≤ l} ∪ {(S, Ak, w(Ak)) | 1 ≤ k ≤ n} ∪ {(Tk, D, w(Tk)) | 1 ≤ k ≤ m}  (2)

我们从源顶点S到目标顶点D应用最大流算法。对于每条流边(Ai, Tj, f(i,j))，我们为智能体Ai和任务Tj分配f(i,j)个样本。分配后，边的权重应减去流量值。评估完成后，连接到S或D的边的权重应增加1。

我们还建立了一个定期间隔，用于将算法应用于网络以获取新的可用评估三元组。

---

## B 操作系统

### B.1 数据集详情

**构建细节。** OS数据集中的每个评估样本包含以下内容：

- **指令**：需要用自然语言描述的问题，需要LLM解决。
- **Docker环境**：启动的docker镜像（例如，预设的默认local-os/default）。
- **初始化脚本（可选）**：在交互开始前需要独立执行的bash脚本（docker exec）（例如，用户配置、文件、系统状态）。
- **启动脚本（可选）**：在创建shell之后、交互之前执行的bash脚本。
- **检查流水线**：用于判断LLM回答或操作正确性的检查方法。
- **示例脚本（可选）**：作为参考解决方案的bash脚本。换言之，如果在交互中执行它们，结果是正确的。仅用于下面介绍的单元测试。

我们在OS评估中设计了两种类型的任务，超越了传统的仅QA评估。

- **问答（QA）**：LLM需要输出命令来解决OS中的特定问题（例如，汇总数字、查看文件内容）。在这种情况下，它们最终必须提交答案。
- **操作**：LLM需要输出命令来在操作系统上执行某些可验证的操作（例如，更改文件/用户状态）。在这种情况下，它们不需要提交最终答案。

得益于检查流水线，两种类型的任务可以在统一的解决方案中进行评估。

收集关于OS的挑战性问题可能很困难。在实践中，大约一半的指令是由人类创建或收集的，而另一半主要是由gpt-4生成的QA问题，并通过单元测试严格筛选（即产生正确的答案/状态）。

对于人类指令，我们首先从Stack Overflow收集了6000个带有bash或shell标签的真实问题和解决方案。然后我们根据得分（点赞数）对它们进行排序。我们邀请了8名主修编程的标注员选择有挑战性的问题。对于每个选定的问题，他们创建一个或多个任务指令，并编写详细的问题描述、初始化脚本、启动脚本和检查流水线。最后，我们对每个评估样本进行交叉验证，确保其正确性。每个问题大约需要2小时进行标注。

对于生成的问题，我们的单元测试包含以下部分：1) 初始化脚本校正：我们执行初始化脚本并移除退出代码不等于0的错误初始化样本。2) 示例代码校正：我们执行示例代码和检查流水线来判断答案的正确性。我们移除答案错误的样本。

最终，我们精选了144个高质量、多样化的OS评估样本，配有测试交互环境和相应的检查流水线（即脚本）。智能体使用1-shot CoT提示以更好地格式化其响应（参见附录B）。

**评估设置。** 对于每个问题（即指令），执行过程可分为3个部分。

- **初始化**：我们使用特定镜像创建一个docker容器，并运行初始化bash脚本来设置指令指定的环境。
- **交互**：我们在此docker中启动一个新的shell，并运行指令指定的启动bash脚本。然后向待测试的LLM提供指令和问题描述。它开始与shell进行交互。在每一轮中，提供两个动作。一个是运行bash脚本，允许模型在shell中生成并运行一系列命令。另一个是提交答案，允许模型终止交互过程。值得注意的是，如果超过回合限制（默认为8），模型将被判定为未能解决问题。
- **检查**：对于每个问题，有一个检查流水线包含一个脚本列表f1, f2, ..., fn，其中fk表示流水线中的第k个脚本片段。对于fk，模型的答案o0以及ft(t < k)的输出ot将作为输入参数输入fk，即ok = fk(o0, o1, ..., ok-1)。当且仅当所有脚本以代码0退出时，结果才是正确的。

**指标。** 我们测量LLM在执行中解决问题的**成功率**。每个问题的最终状态只有两种：错误或正确。

### B.2 动作

在OS评估中，我们设计了两种主要类型的动作：`bash`和`commit`。

- **Bash**：启动一个bash命令（使用`content`字段中的文本输入）。
- **Commit**：宣布目标的完成。如果任务是QA问题，则智能体应在`content`字段中提交最终答案；否则检查流水线将自动检查系统状态以判断正确性。

### B.3 提示示例

OS评估的提示由指令和交互轨迹的格式组成。指令提示的示例如下：

（以下为英文提示示例的中文翻译，原文为英文提示）

```
你是一个将像人一样行动的助手，我将扮演linux(ubuntu)操作系统的角色。你的目标是实现我要求的操作或回答我提出的问题。
在你的每个回合中，你应该首先思考你应该做什么，然后采取以下三种动作之一："bash"、"finish"或"answer"。
1. 如果你认为你应该执行一些bash代码，采取bash动作，并这样输出：
思考：在这里放你的想法。
动作：bash
```bash
# 在这里放你的bash代码
```
2. 如果你认为你已经完成了任务，采取finish动作，并这样输出：
思考：在这里放你的想法。
动作：finish
3. 如果你认为你已经得到了问题的答案，采取answer动作，并这样输出：
思考：在这里放你的想法。
动作：answer(你对问题的答案应放在这对括号内)
如果输出太长，我会截断它。被截断的输出不完整。你必须自己处理截断问题。注意，你的bash代码不应包含任何输入操作。再次强调，你在每个回合中只能采取三种动作中的一种。
```

轨迹以CoT风格组织，我们使用一个1-shot示例使模型更好地理解动作空间。

（随后是1-shot示例，其中USER和AGENT交替对话，在bash shell中解决一个计数问题——原文英文内容已在上文中展示，为节省篇幅此处略去具体交互示例的翻译。核心模式是：用户给出指令，智能体先思考再执行bash命令，观察输出后再决定下一步行动。）

---

## C 数据库

### C.1 数据集详情

**构建细节。** 我们通过重用和合并几个已建立的数据集来获取源查询和数据库：WikiSQL（Zhong et al., 2017）、WikiTableQuestions（Pasupat & Liang, 2015）、SQA（Iyyer et al., 2017）、HybridaQA（Chen et al., 2020）和FeTaQA（Nan et al., 2021），确保指令和数据的多样性。

为了进一步丰富数据集（并避免数据泄露），我们使用gpt-3.5-turbo进行数据增强。给定表的标题信息和原始行，gpt-3.5-turbo生成十个新行。利用表名、标题信息和一些SQL示例，我们让gpt-3.5-turbo生成五个额外的SQL查询。每个获得的SQL语句随后被依次输入gpt-3.5-turbo，指示其在不改变原意的情况下改写句子。有效条目被过滤并采样到最终数据集中，共300条，分为三种基本类型的DB操作：**select**、**insert**或**update**。

因此，数据集中的每个样本包含：

- **指令**：描述问题的内容，指导智能体的行动。
- **表信息**：关于表名和列名的说明（即元信息）。
- **表内容**：表中实际内容，用于创建数据库。
- **正确答案**：对于选择类型的样本，是文本答案；对于其他类型的条目（即insert、update），是正确修改后的表的哈希码。

**评估设置。** 我们通过以下过程评估数据集中的每个问题：

- **初始化**：基于表内容构建初始SQL脚本，并在docker容器中初始化一个MySQL数据库，该数据库提供一个转发的端口用于交互。
- **交互**：初始提示引导智能体提供可执行的SQL命令及其推理。向智能体提供提示、指令和表信息描述，期望其以给定格式返回响应。我们执行SQL并将结果直接返回给智能体，继续此循环直到智能体提交最终答案或遇到错误（例如，达到最大回合限制或无法解析动作）。
- **检查**：对于选择类型的问题，我们将智能体的回答与标准文本答案进行比较，不考虑顺序，但期望精确匹配。如果答案是单个数字，所有等价表示都被接受（例如，5、"5.0"、'+5'被视为相同）。对于插入或更新类型的问题，我们计算并比较智能体操作后表的哈希值与正确SQL操作后的哈希值。

**指标。** 我们测量智能体完成指令的**成功率**。总体成功率是三个类别成功率的宏平均。

### C.2 数据增强

我们详细阐述了基于现有SQL数据集（Zhong et al., 2017; Pasupat & Liang, 2015; Iyyer et al., 2017; Chen et al., 2020; Nan et al., 2021）的三种类型DB任务的数据增强，这些数据集都是QA问题，没有包含插入和更新等常见操作。我们首先测试了原始数据的有效性，然后从每个类别中随机抽样过滤后的数据以形成最终数据集。我们采用gpt-3.5-turbo来丰富和重写原始指令。

- **Insert**：给定表名、标题信息和原始行，我们生成5个用于插入的SQL语句。随后我们重写句子，不改变其含义（使用更短或更长的表达，或改变顺序）。
- **Update**：给定表名、标题信息和之前生成的5个用于插入的SQL语句，我们基于给定语句生成5个用于修改的SQL语句。我们按照上述标准重写句子。

为确保数据质量，每个增强后的查询语句都必须通过单元测试脚本。

查询类型的任务属于Text-to-SQL评估的传统范畴，我们仅对其进行采样和分类以进行评估。现有数据集中的每个查询语句被分类为以下类型之一：'计数'、'聚合-MIN'、'聚合-MAX'、'聚合-AVG'、'聚合-SUM'、'排序'或'比较'。每个只能属于一种类型。其余的分类为"其他"。

### C.3 提示示例

我们使用以下提示格式：

（英文原提示的中文翻译）
```
用户：
我将问你一个问题，然后你应该帮助我使用SQL操作MySQL数据库来回答问题。
你必须向我解释问题和你的解决方案，并写下你的想法。
在充分思考和解释之后，每轮你可以选择操作或回答。
你的操作应该是这样的：
动作：操作
```sql
SELECT * FROM table WHERE condition;
```
你必须将SQL放在markdown格式中，不附带任何其他注释。你的SQL应该在一行中。
每次你只能执行一条SQL语句。我将只执行第一个SQL代码块中的语句。每次你编写SQL时，我都会为你执行并给你输出。
如果你操作完毕，想要提交最终答案，请写：
动作：回答
最终答案：["答案1", "答案2", ...]
除非你对自己的答案有把握，否则不要写这个模式。我期望一个准确正确的答案。
你的答案必须与正确答案完全相同。
如果问题是关于修改数据库的，那么在完成操作后，你的答案字段可以是任何内容。
如果你的响应与我之前提到的任何模式不匹配，你将立即被判定为失败。
你的输入将是原始的MySQL响应，你必须自己处理它。
```

### C.4 数据增强中的偏差研究

为了验证我们的数据集在增强过程中没有引入模型引起的偏差，我们使用Claude-2重新标注了一小批数据，以gpt-4和gpt-3.5-turbo为例。

如表5所示，数据始终呈现相似的得分模式，即gpt-4在UPDATE操作上表现较差，但在INSERT任务上表现出更高的熟练度。这一观察结果表明，我们的数据集增强方法不太可能引入实质性偏差，在不同操作上保持了固有的得分关系。

**表5: 对gpt-4和gpt-3.5-turbo重新标注的数据与原始数据的对比。**

| 类型 | SELECT | INSERT | UPDATE |
|------|--------|--------|--------|
| gpt-4 原始 | 0.32 | 0.32 | 0.32 |
| gpt-3.5-turbo 原始 | 0.21 | 0.23 | 0.66 |
| gpt-4 新 | - | 0.27 | 0.66 |
| gpt-3.5-turbo 新 | - | 0.19 | 0.92 |

---

## D 知识图谱

### D.1 数据集详情

**构建细节。** 为了衡量LLM的决策能力，特别是它们在长期规划方面的熟练程度，我们精心编制了一个数据集，来源于FREEBASE上已有的知识库问答（KBQA）数据集，包括GrailQA（Gu et al., 2021）、ComplexWebQuestions（Talmor & Berant, 2018）和GraphQuestions（Su et al., 2016）。

我们将KBQA视为一个工具学习设置，从而为LLM配备一系列KG查询工具。通过利用（Gu & Su, 2022）中标注的S表达式，我们可以准确建立与每个问题对应的最佳工具应用序列。为了保持任务的高难度，我们选择只保留那些需要至少五次工具调用的问题。通过这种严格的选择方法，我们积累了一个包含1,663个问题的数据集。数据集中的每个数据条目具有以下字段：

- **输入问题**：涉及复杂KG信息搜索的自然语言表达。
- **主题实体**：输入问题中提到的一组主题实体。我们避免了执行实体链接的需要，使LLM能够专注于长期规划。
- **动作序列**：导致目标答案的金标准动作序列（即工具调用）。
- **金标准答案**：问题的金标准答案，通常以一组KG实体为特征。

注意，与在AgentBench中与数据库交互不同——数据库的细节和内容都集成到输入中——向LLM描述一个广泛的知识图谱并不是特别可行的。该任务的特点是部分可观察的环境，这是其性质的一个关键方面。

**评估设置。** 为了支持我们的评估，我们首先使用Virtuoso托管最新版本的FREEBASE。由于SPARQL查询的复杂性，我们决定不让LLM自己编写SPARQL查询。相反，我们实现了一系列与Virtuoso后端交互的API，允许LLM更轻松地查询KG。

我们使用数据集中的前500个任务进行评估。每个任务，如果成功执行，理想情况下应按以下阶段进行。

- **初始化**：我们向LLM提示具体的任务描述，包括我们提供的每个KG查询工具的具体描述。
- **交互**：在此阶段，LLM应调用不同的工具来访问KG，并积累必要的信息以准确回答问题。重要的是，该过程完全是自主的，意味着LLM完全自己确定工作流程。
- **最终答案预测**：在与KG交互期间，LLM可能会生成一个变量列表，每个变量代表一组独特的实体。如果LLM确定某个特定变量应表示最终答案，它将呈现该变量作为输出并结束任务。

**指标。** 我们使用**F1分数**作为本研究中的主要评估指标，通过将模型的预测答案与金标准答案进行比较来计算。除了F1分数，我们还使用**精确匹配**指标。然而，与以前基于逻辑形式测量精确匹配的研究不同，我们基于预测答案集和金标准答案集之间的精确匹配进行评估。最后，我们还评估模型生成的动作序列的**可执行性**。如果模型的动作序列在执行时产生任何答案集，则在可执行性上得分为1.0。如果未能产生答案，则得分为0。

### D.2 提示示例

任务描述（英文原提示的中文翻译）：

```
用户：
你是一个基于知识库中存储的知识回答问题的智能体。为此，你可以使用以下工具来查询KB。
1. get_relations(variable: var) -> list of relations
   变量可以是实体或实体集（即先前查询的结果）。此函数帮助导航与变量连接的所有KB中的关系，因此你可以决定哪个关系对找到问题的答案最有用。
   简单用例：get_relations(Barack Obama)，查找从实体Barack Obama开始的所有关系/边。
   get_relations的参数应始终是实体或变量（例如#0），而不是其他任何东西。
2. get_neighbors(variable: var, relation: str) -> variable
   给定一个变量，此函数返回通过给定关系与该变量连接的所有实体。注意，get_neighbors()只能在使用了get_relations()找到一组可行关系后才能使用。
   简单用例：get_neighbors(Barack Obama, people.person.profession)，返回Obama在Freebase中的职业。
3. intersection(variable1: var, variable2: var) -> variable
   给定两个变量，此函数返回两个变量的交集。两个变量必须是相同类型！
4. get_attributes(variable: var) -> list of attributes
   此函数帮助找到变量的所有数值属性。只有在该问题寻求极值累积（即argmax或argmin）时才使用它。
5. argmax(variable: var, attribute: str) -> variable
   给定一个变量，此函数返回具有给定属性最大值的实体。只能在使用了get_attributes()找到一组可行属性后才能使用。
   简单用例：argmax(variable, age)，返回属于该变量的最老实体。
6. argmin(variable: var, attribute: str) -> variable
   给定一个变量，此函数返回具有给定属性最小值的实体。只能在使用了get_attributes()找到一组可行属性后才能使用。
   简单用例：argmin(variable, age)，返回属于该变量的最年轻实体。
7. count(variable: var) -> int
   给定一个变量，此函数返回属于该变量的实体数量。
在过程中产生一个变量后，你需要判断某个变量是否是问题的最终答案。每个变量以从0开始的ID表示。例如，#0是第一个变量，#1是第二个变量，依此类推。
一旦找到答案，请用'最终答案：#id'回复，其中id是你认为是最终答案的变量的ID。例如，如果你认为#3是最终答案，你必须回复'最终答案：#3'。
你一次只能采取一个动作！在从执行中获得观察结果后，你可以采取另一个动作。你最多可以采取15个动作来找到问题的答案。
```

由于使LLM能够查询KB的内在复杂性，我们观察到在零样本设置下，LLM很难生成任何具有实质相关性的输出。因此，我们在提示中额外提供了一个教学示例（此处省略具体示例以节省篇幅，示例展示了一个完整的从问题到最终答案的推理轨迹，包括逐步调用工具和推理过程）。

---

## E 数字卡牌游戏

### E.1 数据集详情

**构建细节。** 我们使用Aquawar框架作为交互系统的基础。第一种交互类型是**行动**阶段，模型需要选择想要行动的鱼，然后选择技能目标。为确保模型操作的有效性，我们执行有效动作检查。第二种交互类型是**猜测**阶段，我们向模型提供已知信息，包括鱼种和技能描述、敌人的目标。我们有两种简单的策略（随机和贪心搜索）用于测试目的。以下是游戏过程的详细定义和描述。

- **玩家和卡牌**：这是一个双人对战游戏，每队有四条宠物鱼（即卡牌）。卡池由十种鱼组成（附录E.2），双方玩家在游戏开始前选择四条确定的鱼。
- **初始状态**：每条鱼有400初始生命值、200初始攻击力、主动技能和被动技能。
- **基本规则**：玩家每回合选择一条活着的鱼对其主动技能或普通攻击作用于一条敌方鱼。所有活着的鱼的被动技能在满足特定条件时会自动触发。
- **猜测机制**：玩家鱼的身份最初是隐藏的。对方玩家每回合可以猜测一条玩家鱼的身份。如果对方猜对了，该玩家鱼的身份被揭示，并且该玩家的所有鱼都会受到伤害。
- **回合过程**：在一个游戏回合中，该回合的玩家首先猜测对方一条活着的且身份未被揭示的鱼的身份。如果猜测正确，对方所有仍然活着的鱼都受到伤害。随后，该回合的玩家可以命令一条活着的鱼执行普通攻击或主动技能。之后，任何满足条件的鱼将释放其被动技能。
- **胜利条件**：在游戏结束时拥有更多活着的鱼的一方获胜。

为了同时平衡智能体的参与度和游戏复杂度，我们设计了两个阶段的游戏逻辑。我们在第一阶段移除猜测机制，而在第二阶段保留猜测机制。我们在第一阶段和第二阶段分别测试所有模型，并选择平均性能作为最终得分。

我们选择两种简单的游戏策略作为基线：
- 第一种策略是从所有可用动作空间中简单随机选择。
- 第二种策略会尽量使用AOE攻击，并持续评估是否能一击必杀。然后尝试使用主动技能，最后才使用普通攻击。总体而言，此策略遵循特定模式，但不一定是最优的。

**评估设置。** 每次游戏时，我们按以下步骤进行评估：

- **初始化**：我们启动修改后的游戏逻辑环境（使用pybind编译）和基线游戏代理，在Ubuntu 20.04环境下运行。
- **交互**：我们根据不同的游戏阶段在指令提示中放置规则描述，LLM智能体在游戏逻辑环境中与基线进行交互和策略竞争。我们给LLM智能体五次机会以正确格式响应。如果在给定尝试次数内未能输出合法动作，它将立即被视为失败。同时，我们鼓励模型以CoT格式输出其推理过程。
- **结果计算**：在交互过程中，我们将记录整个游戏过程以进行战斗回放，并计算结果以获得该任务的指标。

**指标。** 我们的综合评估使用从基本游戏元素开始的指标，如**获胜轮次**、**总轮数**、**胜率**、**造成的总伤害与总生命值之比（伤害率）**，最终我们根据上述指标提供一个最终奖励分数：

奖励 = 0.7 × 胜率指标 + 0.3 × 伤害率指标

### E.2 鱼的属性

根据游戏规则，有十种鱼：

- **Spray（喷水鱼）**：
  - 反击（被动）：当队友生命值低于30%时，对攻击者造成30点伤害。
  - 群体攻击（主动）：攻击所有敌人，造成自身攻击力35%的伤害。
- **Flame（火焰鱼）**：
  - 反击（被动）：当队友生命值低于30%时，对攻击者造成30点伤害。
  - 内斗（主动）：对一个活着的队友造成75点伤害，并使自身攻击力增加140。
- **Eel（鳗鱼）**：
  - 偏转（被动）：受到攻击时，将70%的伤害分配给队友，自身承受30%。累计承受200点伤害后获得40点攻击力。
  - 群体攻击（主动）：攻击所有敌人，造成自身攻击力35%的伤害。
- **Sunfish（翻车鱼）**：
  - 偏转（被动）：受到攻击时，将70%的伤害分配给队友，自身承受30%。累计承受200点伤害后获得40点攻击力。
  - 内斗（主动）：对一个活着的队友造成75点伤害，并使自身攻击力增加140。
- **Barracuda（梭鱼）**：
  - 减免（被动）：每次有30%的概率避免任何来袭伤害。
  - 暴击（主动）：对敌人造成120点暴击伤害。
- **Mobula（蝠鲼）**：
  - 减免（被动）：每次有30%的概率避免任何来袭伤害。
  - 削弱（主动）：选择一个队友或自己，使其受到攻击时伤害减少70%，并增加其20点攻击力。
- **Octopus（章鱼）**：
  - 治愈（被动）：受到攻击时如生命值仍大于0，回复20点生命值。
  - 内斗（主动）：对一个活着的队友造成75点伤害，并使自身攻击力增加140。
- **Whiteshark（大白鲨）**：
  - 治愈（被动）：受到攻击时如生命值仍大于0，回复20点生命值。
  - 暴击（主动）：对生命值最低的敌人造成自身攻击力120%的暴击伤害。如果目标生命值低于160，暴击伤害增加至140%。
- **Hammerhead（锤头鲨）**：
  - 爆炸（被动）：受到攻击但未死亡时，对攻击源造成40点伤害。当生命值低于20%时，增加15点攻击力。
  - 暴击（主动）：对生命值最低的敌人造成自身攻击力120%的暴击伤害。如果目标生命值低于160，暴击伤害增加至140%。

可以看出，不同宠物鱼的主动和被动技能之间存在重叠，这是为了更好地隐藏游戏中宠物鱼的身份信息，增加游戏的策略性。

### E.3 提示示例

我们使用以下提示格式进行动作（英文原提示的中文翻译）：

```
这是一个双人对战游戏，每队有四条宠物鱼。鱼的种类可能不同。
每条鱼有400初始生命值、200攻击力、主动技能和被动技能。
每回合你可以选择一条活着的鱼使用其主动技能或普通攻击（造成攻击力一半的伤害）攻击一条敌方鱼。
当条件满足时，鱼的被动技能会自动触发，无论它是否被选中。
你的鱼的身份最初是隐藏的。敌人每回合可以猜测你一条鱼的身份。如果敌人猜对了，你的鱼的身份被揭示，你的每条鱼都会受到50点伤害。
胜利条件是在游戏结束时拥有更多活着的鱼。
以下是你的四条宠物鱼的类型：
{鱼的详细信息}
以下是敌人的四条宠物鱼的类型：
{鱼的详细信息}
和我一起玩游戏。在每一轮中，你应该输出你的思考过程，并用以下JSON格式返回你的行动：
{'pick_fish': '选择一条活着的鱼，给出活着的鱼的名字', 'action': '从[normal, active]中选择', 'target_position': "目标位置，必须从[0,3]中选择"}
注意！你必须在每一轮中返回你的行动。否则，你将被视为失败。
```

阶段2中猜测的提示格式类似，要求模型以JSON格式输出猜测的鱼类型和目标位置。

### E.4 战斗生成

在我们的研究正文中，我们为公平评估固定了某些预设，使所有模型在相同的战斗场景中进行测试。然而，这些任务的生成确实可以包含随机性。游戏中的随机性主要体现在以下方面：

- **队伍组成**：双方宠物鱼的选择，包括数量和类型。
- **属性确定**：双方每条宠物鱼属性的具体数值。

我们允许选择不同的难度级别来生成随机战斗。在本节中，我们将解释这种难度概念如何运作。

#### E.4.1 战斗力

为了有效评估战斗力，认识到其基本原则至关重要：在两队的对抗中，战斗力较强的一方通常有更高的获胜概率。

设鱼c的生命值为HPc，其攻击力（标准攻击的预期伤害）为ATKc。

设想一个简单的场景：两条鱼相互对抗，一条来自我方记为f（友方），另一条来自对方记为h（敌方）。它们同时进行战斗，互相造成伤害。每方能承受战斗的时长分别为HPf/ATKh和HPh/ATKf。在这种情况下，如果HPf/ATKh ≥ HPh/ATKf，即等价于HPf·ATKf ≥ HPh·ATKh，我方更有可能获胜。

因此，对于单鱼队伍，我们将其战斗力定义为HP·ATK，与上述标准一致。

当考虑一个包含多条鱼的队伍T时，排除任何特殊能力，每个战斗回合涉及选择我方一条鱼攻击对方的一条鱼。这允许我们将队伍作为一个整体来处理，总生命值为所有鱼的生命值之和，并考虑平均攻击力（在正常情况下，最高攻击力会是合理的选择，但由于对手通常会先攻击攻击力最高的鱼，降低其持久性，我们假设所有鱼的攻击频率相等）。

由此我们得出队伍T的战斗力Power(T)的定义：

Power(T) = (1/#T) × ΣHPc × ΣATKc（对所有c∈T）

#### E.4.2 难度：战斗力之比

游戏的难度由双方队伍战斗力之比来衡量：

ρ(H|F) = Power(H) / Power(F)

在此公式中，F代表我方队伍，H代表敌方队伍。值得注意的是，比值为1表示平衡或正常的难度级别，表明队伍之间的均势。

此外，这个难度度量意味着ρ(T1|T2)个T2队伍在力量上等同于T1队伍。

有了这个框架，研究人员可以准确设置特定的难度级别来评估各种策略的胜率，从而有效衡量其效力。

---

## F 横向思维谜题

### F.1 数据集详情

**构建细节。** 每个样本由一对故事（谜语，例如：一个男人走进一家餐厅，点了一碗海龟汤，吃完后自杀了。他为什么这么做？）和真相组成。我们将样本分为四个难度级别：简单、中等、困难、专家。LLM智能体的LTP规则如下：

- **角色**：LTP评估中的角色是主持人和求解者。主持人知道故事和真相，向求解者提供故事，并引导其猜出真相。求解者由LLM扮演和操作，通过提问和综合主持人的回答来找出真相。
- **解决步骤**：每个游戏有最大轮数，例如25轮。求解者需要每轮基于已知事实提出一个问题。问题应该是可以用"是"、"否"或"无关"回答的。主持人用正确答案回复问题。为降低LLM智能体的难度，当求解者陷入错误的推理方向时，主持人有时会在响应中提供一些提示。
- **游戏终止**：当求解者认为已经猜出真相的主要部分时，可以向主持人宣布猜测的情节。如果正确，主持人将宣布游戏结束。

**评估设置。** 对于每对故事和真相，我们按以下步骤评估模型：

- **初始化**：通过本地python包安装或Web API设置LTP主持系统。
- **交互**：我们为LLM设置系统提示以建立其玩家角色。LLM作为求解者在每个游戏的最大回合内进行测试，如果LLM不超过最大token长度。在自动评估中，我们将答案限制为主要是"是"、"否"或"无关"，并从gpt-3.5-turbo的响应中提取答案。LLM还被要求在自动评估中总结其推理，以帮助终止检测更准确。
- **检查**：我们对每个LLM进行试点研究，收集游戏过程中的所有情况，并设计检查方案。对于自动评估，我们为gpt-3.5-turbo设置一些关键词来回答，并提醒模型考虑一些灵活的情况如同义词。

**指标。** 我们通过两个自创指标来评估LLM的横向推理能力：

- **单局游戏准确性（SGA）**：在单局游戏中LLM接近真相的轮次比例。
- **轮次效率（RE）**：模型在最大轮数内猜出真相的速度。
- **查询相关性（QR）**：模型问题与真相之间的相关性。
- **游戏进度（GP）**：游戏结束前的进度，作为主要指标。我们将真实情况分解为多个要点，并测量智能体达到了多少个要点。

### F.2 LTP系统的评估

我们通过人工验证来评估LTP系统，验证系统在里程碑识别和事实验证方面的准确性。我们比较了自动评估和人工评估之间的单局游戏准确性（SGA）和查询相关性（QR），发现自动评估有时对智能体更宽容，这使SGA和QR看起来比人工评估更好，尤其是在开源模型上。我们计划专门为游戏主持人训练一个模型，以提供更好的游戏体验和更精确的评估。对于游戏进度和轮次效率，LTP系统提供了客观的评估，可以匹配人工评估的水平。

### F.3 LTP游戏进度与终止

游戏的进度定义为命中的真相关键点的比例。关键点由gpt-3.5-turbo总结，并在数据集中作为"answer_keys"（见下面的示例）得出。

（示例故事：他们那天晚上去了废弃的建筑记录楼梯数。他们验证了网上说的，晚上数楼梯时会少一阶。然而，当他们第二天去废弃建筑核实时，发现根本没有楼梯。）

关键点：
1. 他们想数废弃建筑的楼梯数。
2. 发生了超自然事件。
3. 他们看到了一个网上的说法：晚上数楼梯会少一阶。
4. 第二天，当他们去废弃建筑核实时，发现没有楼梯。
5. 他们崩溃了，因为他们被吓坏了。

不同样本的关键点数量不同。关于判断智能体是否猜出关键点的决定，我们首先将相关问题改为陈述句，然后将句子简化为一个句子。猜出一个关键点后，我们删除该关键点和相关推论，以避免重复猜测。

### F.4 提示示例

**智能体提示**（英文原提示的中文翻译）：

```
你是一个游戏玩家，正在玩横向思维谜题，也称为情景谜题。
横向思维谜题是一个演绎推理游戏，以下是游戏规则：
1. 游戏开始时，你会收到一段叙述，称为"故事"。基于故事，你需要提出可以用"是"、"否"或"无关"回答的问题来猜出"真相"。
2. 通过提问，你缩小可能性范围，直到最终猜出真相。
3. 每次你只能问一个问题。
4. 记住你的角色是玩家。你不能宣布游戏结束、放弃推理或要求新游戏。
5. 你不能直接重复故事中已经提供的信息。
6. 你不能直接以"为什么"问题的形式询问故事的细节；你需要自己猜测真相。
7. 你不能直接询问故事；你必须自己进行推理。
接下来，请充分利用上述提供的信息进行游戏推理。记住，你的问题应该可以用"是"、"否"或"无关"回答，并且你一次只能问一个问题。
这是你的故事：
{story}
你可以开始猜测真相的内容，我将回答你的问题。请注意，你的问题应该可以用"是"、"否"或"无关"回答。
```

**主持人提示**（英文原提示的中文翻译）：

```
用户：
我需要你担任一个名为横向思维谜题的游戏主持人。横向思维谜题是一个由故事和真相组成的游戏。你的故事是：'{story}'
你的真相是：'{answer}'
以下是游戏规则：
1. 你既知道"故事"也知道"真相"。当用户想要玩横向思维谜题时，你向他们提供"故事"。用户只知道"故事"，不知道"真相"。
2. 用户提出可以用"是"、"否"或"无关"回答的问题。他们的问题旨在猜测"真相"。基于"真相"，你使用"是"、"否"或"无关"来回答用户的问题，引导他们猜出正确的真相。
3. 如果用户直接以"为什么"问题的形式询问真相的细节，告知他们需要自己进行猜测。
4. 你必须充分理解并准确解释来自真相的信息。基于真相的信息和用户过去的问题，你回答用户的问题。用户的问题可能不一定包含真相中的信息，但你的回答必须符合真相的事实。
5. 只有当真相无法提供直接或间接答案时，你才能回答"无关"。注意，这是回答"无关"的唯一条件；否则，你应该回答"是"或"否"。
6. 即使用户直接询问，你也不能直接透露真相中的信息。
7. 你需要整体判断用户的问题并理解其总体意图。避免仅基于特定点回答；你的回答必须符合真相的事实。
8. 在用户猜测真相的过程中，如果他们接近某些真相但仍有差距，无法理解完整的真相，你可以提供某些切入点提示。然而，你不能直接透露真相中的信息。
在游戏过程中，请遵守上述游戏规则，以确保用户获得良好的游戏体验。密切关注所提的问题，并确保你的回答既符合游戏规则也符合真相的信息。当用户请求玩游戏时，向他们提供故事，并通过回答"是"、"否"或"无关"来帮助他们猜测真相。记住，在每次回应时，你必须充分理解并遵守上述游戏规则，以及故事和真相。这将确保流畅的用户体验，避免你无法回答或违反游戏规则的情况。
```

---

## G 家务处理

### G.1 数据集详情

**构建细节。** ALFWorld基准包含旨在模拟家庭场景的文本环境，提供了一个交互环境，智能体可以通过基于文本的界面执行决策任务。给定家庭环境描述和目标指令，智能体的目标是将复杂的高级目标分解为一系列简单动作。在每一步之后，智能体接收环境反馈，允许智能体动态调整计划并继续执行后续任务，最终完成主要目标。

ALFWorld数据集中每个评估样本包含以下内容：

- **环境描述**：整个家庭环境的详细描述，包括智能体的初始位置和包含物体及其ID的房间快照。
- **目标**：需要在环境中由智能体完成的目标，通常需要多步推理和探索（例如，把灯放在桌子上）。
- **模拟环境**：在智能体的每个动作之后，模拟环境给出即时反馈并评估智能体是否完成了任务。

在数据集中，我们从ALFWorld评估集的分布外分割中使用了134个可解决的问题。所有问题被分为六类：拾取并放置、拾取清洁后放置、拾取加热后放置、拾取冷却后放置、查看物体、拾取两个物体。

**评估设置。** 由于问题本身固有的复杂性和输出格式的高标准要求，我们采用1-shot评估设置。对于每个类别的问题，我们使用训练集中一个相同类别的相对简单且完整的交互过程作为示例。遵循ReAct（Yao et al., 2023b），我们采用了相应仓库中的少样本示例和提示。此外，如果LLM输出格式无效，我们使用BLEU指标评估输出与所有有效动作选项的相似度。相似度最高的选项将作为模型在该轮的动作。

对于每个样本，评估过程可分为两个部分。

- **初始化**：我们向模型描述任务并提供一个成功的示例。随后，我们详细说明环境并描述需要完成的目标。
- **交互**：模型基于从先前交互中获得的反馈和环境信息生成一些思考并执行下一个动作。从模型接收到动作后，环境提供反馈（环境的变化或模型观察到的信息）。重复此过程，直到模型成功实现其目标（视为成功）或达到最大动作数（视为失败）。值得注意的是，有时经过几次不成功的尝试后，模型可能重复输出相同内容。为节省评估时间，如果模型连续三次输出相同内容，则判定为因重复而失败。

**指标。** 我们采用总体**成功率**作为模型性能的衡量标准，即模型成功完成的任务数除以总任务数。

### G.2 提示示例

为了将输出格式与模拟环境支持的合法命令对齐，我们采用1-shot评估设置，其中一个成功完成的任务示例被拼接在指令之后。在交互开始时，我们使用以下指令向模型描述任务（英文原提示的中文翻译）：

```
与一个家庭环境交互以解决一个任务。想象你是家庭环境中的一个智能体，你的目标是执行动作以完成目标任务。
在交互开始时，你将收到当前环境的详细描述和你要完成的目标。
在每个回合，你将收到一个动作列表，你可以从中选择一个在本次执行。
你应该从两个动作中选择："THOUGHT"或"ACTION"。
如果你选择"THOUGHT"，你应该首先思考当前状况并规划未来的动作，然后输出当前回合的动作。你的输出必须严格遵循以下格式："THOUGHT: 你的想法。\n ACTION: 你的下一个动作\n"
如果你选择"ACTION"，你应该直接输出当前回合的动作。你的输出必须严格遵循以下格式："ACTION: 你的下一个动作\n"
在你的每个回合之后，环境将给予你即时反馈，基于此你规划接下来的几步。
如果环境输出"Nothing happened"，则表示前一个动作无效，你应该尝试更多选项。
提醒：
1. 动作必须从给定的可用动作中选择。任何超出提供的可用动作范围的动作将被视为非法。
2. 必要时进行思考，在过程中尽量直接行动。
```

（随后给出一个1-shot示例，展示了在家庭环境中搜索肥皂瓶并放置在马桶上的完整交互过程。）

---

## H 网页购物

### H.1 数据集详情

**构建细节。** 环境向智能体显示网页的文本观察结果和可用动作。智能体可以像在现实世界中一样自由浏览网站，通过可点击的按钮浏览商品。约一百万个产品从amazon.com抓取，形成网站数据库。然后为每个产品标注代表其自身属性的标签。收集了12,087条人类指令，并与目标以及预期属性相关联。更多数据集构建细节请参考（Yao et al., 2022）。

**评估设置。** 我们采用12,087条指令中的前500条作为测试集（遵循（Yao et al., 2022）的官方实现）。每轮交互可分解为以下步骤：

- **指令**：在初始提示告诉环境信息和LLM应响应的格式后，我们给出关于我们想要购买什么产品的指令。
- **交互**：智能体按给定格式响应，包含其想法和想要采取的动作。动作可分为两类：search和click，对应于在现实世界中分别使用搜索引擎和点击按钮的实际动作。环境以简化的文本版网页和可用按钮列表响应智能体的动作。此过程重复，直到智能体点击"buy now"按钮或超过回合限制。
- **计算奖励**：我们使用论文中的奖励函数作为指标。奖励根据我们期望的属性与购买产品实际拥有的属性之间的相似度映射到0和1之间的数字。

**指标。** 由于给定查询可能有一个以上的合适商品，Webshop采用匹配奖励作为评估指标：

奖励 = (|Uatt ∩ Yatt| + |Uopt ∩ Yopt| + I[yprice ≤ uprice]) / (|Uatt| + |Uopt| + 1) × rtype

其中U和Y分别代表目标和所选产品，att和opt代表属性和选项。TextMatch是所选产品标题与目标产品标题之间的代词、名词和专有名词的文本匹配度。

### H.2 提示示例

（英文原提示的中文翻译）

```
用户：
你正在网络购物。
我会给你关于做什么的指令。
你必须遵循指令。
每轮我会给你一个观察结果和一个可用动作列表，你必须基于状态和指令响应该动作。
如果搜索可用，你可以使用搜索动作。
你可以点击可点击按钮之一。
动作应具有以下结构：
search[关键词]
click[值]
如果动作无效，则不执行任何操作。
搜索中的关键词由你决定，但click中的值必须是可用动作列表中的值。
记住，搜索中的关键词应仔细设计。
你的响应应使用以下格式：
思考：
我认为...
动作：
click[某个值]
```

随后是一个1-shot示例，展示了从搜索产品到选择规格再到最终购买的完整交互过程。

---

## I 网页浏览

### I.1 数据集详情

**构建细节。** Mind2Web涵盖旅行、信息、服务、购物和娱乐等领域，使用SimilarWeb排名作为参考进行组装。它雇佣标注员首先基于当前网站提出任务目标，然后记录他们的交互轨迹作为专家演示。我们对它的采用主要关注跨环境的泛化，即跨领域测试集，包含来自73个网站的912个任务，分布在住房、工作、社交媒体、教育、健康、政府、家庭服务等领域。更多数据集构建细节请参考（Deng et al., 2023）。每个任务样本包含以下内容：

- **任务描述**：可以在网站上实现的高级（而非逐步）目标，例如"获取评分最高的SAP S/4 HANA课程评分为4，时长在3到6小时之间，适合中级水平，将其添加到购物车并结账"。
- **（参考）动作序列**：在标注的交互序列中，第t步的元动作包括{et, ot}，其中et代表目标元素的唯一后端ID，ot代表在et上执行的符号动作（即Click、Type和Select Options）。对于Type和Select Options，还包括相应的文本输入。
- **网页信息**：每个步骤中网页浏览环境的详细观察。在手动的标注过程中，每个观察步骤捕获一个快照，包含来自网站的原始HTML代码以及先前的交互轨迹。

已经发现，LLM在处理现实网页附带的繁重原始HTML代码时始终面临挑战。因此，Mind2Web提出使用小型语言模型（如DeBERTa）对HTML元素进行排序和过滤，以提高推理效率。

给定用户的高级指令，智能体通过接收当前页面内容的观察和操作历史，然后预测下一个动作（包括目标元素和预期操作），持续与网络系统进行交互。

**评估设置。** 评估涉及一个双重过程以提高效率（遵循（Deng et al., 2023）的方法）。首先使用微调后的小型语言模型对HTML元素进行排序，选择前k个候选。随后，我们将元素选择表述为一个多选QA问题，每轮提供五个候选。对于Type和Select Options操作，额外提示智能体指定操作的参数，即要输入的文本或要选择的选项。

**指标。** 对于评估，按照原始论文的建议，我们考虑以下指标：

- **元素准确率**：计算所选元素et的准确率。
- **动作F1**：确定操作ot的token级匹配分数。由于存在文本值，Type和Select Option操作有所区别。
- **成功率**：评估预测动作与参考动作相比的正确性。对于**步骤成功率**，如果所选元素et正确且预测的操作ot与步骤的金标准值匹配，则判定为成功。同样，对于**任务成功率**，只有当所有步骤都已成功时，任务才被视为成功，使其成为一项严格的度量标准。不幸的是，即使是最好的LLM现在也只能实现个位数的任务成功百分比。由于LLM目前在确保整体任务成功率方面存在困难，我们报告**步骤成功率**作为主要指标，显示每个动作步骤的独立准确率。关于实验设置，我们选择topk=10个候选来构建使用CoT少样本提示的多选题。因此，GPT-3.5的结果可能与原始论文（Deng et al., 2023）在topk为50的设置和不同提示策略下的结果有所不同。

### I.2 提示示例

我们使用以下包含3个示例的CoT提示进行Mind2Web评估：

（每个示例展示了：给定一个HTML网页的结构化表示和任务描述，以及先前的动作历史，模型需要从多个候选中选择正确的下一个动作，并输出动作类型和相应的值。）

---

## J 详细分析

### J.1 执行结果的有效性分析

#### J.1.1 有效性分析的动机

在人工智能和机器学习领域，模型的有效性、精确性和可靠性对于实际实施至关重要。评估多个模型可以了解它们各自的优势和局限性，从而更好地判断哪些模型最适合特定任务。本次有效性分析的目的是提供一种系统的方法来辨别不同模型的表现，特别是在任务完成、上下文大小限制、返回格式准确性、动作准确性和任务限制方面。这种对性能参数的深入探讨不仅增进了我们对模型能力的了解，还有助于为未来的应用优化模型。

#### J.1.2 有效性分析的定义

为了进行全面的有效性分析，我们将结果划分为五个不同的类别：

- **已完成（Completed）**：表示模型无论最终结果如何，成功按照指令完成了任务。
- **上下文超限（Context Limit Exceeded）**：表示模型的长度受到API限制，主要出现在text-davinci模型中。
- **无效格式（Invalid Format）**：表示尽管收到清晰的指令，模型未能以预期格式返回响应。
- **无效动作（Invalid Action）**：表示模型以正确格式返回，但其动作要么在允许的动作空间之外，要么动作参数不正确。
- **任务超限（Task Limit Exceeded）**：表示任务达到了终止标准，例如超过规定的轮数。

通过将结果分类，我们可以更清晰地了解每个模型的优势和挑战所在，从而进行有针对性的改进。

#### J.1.3 模型的有效性分析

在我们的评估中，我们审查了29个不同模型的有效性表现。除了具有固有的严格API上下文长度限制的text-davinci模型外，其他模型的结果主要属于已完成、无效格式、无效动作和任务超限这四类。

从展示的详细分析中出现了关键趋势。如图6所示，图表清晰地展示了不同模型和定义类别中的有效性分布，使我们能够得出有洞察力的结论。

**图6: 模型的有效性分析。无效格式、无效动作和任务超限是常见错误。上下文超限错误仅出现在text-davinci模型中。**

（图6展示了各模型的完成情况比例分布，包括已完成（绿色）、上下文超限（蓝色）、无效格式（橙色）、无效动作（红色）和任务超限（紫色）的比例。）

### J.2 研究发现

#### J.2.1 指令遵循至关重要

基于表6中呈现的数据，我们可以得出关于商业API模型和开源模型之间性能差异的一些重要观察。值得注意的是，在无效格式和无效动作方面，开源模型报告了更多挑战。具体而言，10.4%的开源模型结果被标记为无效格式，而商业API模型为6.0%。类似地，开源模型中无效动作的出现比例（13.6%）高于商业API模型（4.6%）。这些差异可能表明商业模型的鲁棒性和泛化能力更强，或者可能在模型设计和训练阶段更加关注细节，特别是在指令遵循方面。

**表6: 两类模型的结果分布比较。**

| 模型类别 | 已完成 | 上下文超限 | 无效格式 | 无效动作 | 任务超限 |
|---------|-------|-----------|---------|---------|---------|
| 商业API模型 | 61.5% | 3.0% | 6.0% | 4.6% | 24.9% |
| 开源模型 | 39.1% | 0.0% | 10.4% | 13.6% | 36.9% |

同样值得注意的是，即使是一些最好的模型有时也可能忽略重要的指令。

尽管我们明确指示了DB任务的正确格式：
```
你的操作应该是这样的：
动作：操作
```sql
SELECT * FROM table WHERE condition;
```
```

即使是gpt-4有时仍然不能正确响应。

（示例显示了gpt-4未能以要求的格式输出，而是提供了一段解释性文本而没有正确的动作标签和SQL语句。）

#### J.2.2 智能体规划中的一致性和执行

智能体的一个基本能力是拥有连贯和统一的思维过程，使其能够基于现实条件制定和实施可行的计划。

许多模型在遇到问题时具备分析和制定初步计划的能力。然而，即使是一些最先进的模型也容易偏离或忘记其原始计划。不同模型在执行计划时持续遵循思维序列的能力差异相对较大。这种能力深刻影响着语言模型作为智能体的效能和操作能力。这里我们以家务处理环境为例说明这一现象。

家务处理环境包含一个模拟的家庭场景，其中模型需要根据任务提供的周围环境观察和给定目标，从给定的动作空间中选择合适的动作。由于实体众多且可用动作丰富，家务处理环境提供了高度的自由度，对模型保持清晰连贯思维过程的能力提出了严峻挑战。

**gpt-4的成功示例**（展示了从搜索肥皂条到清洗再到放置在台面上的完整且逻辑清晰的推理和行动过程）。

**图7: gpt-4的思维和计划。** gpt-4通过遵循清晰的步骤序列系统地完成了任务。它首先将任务分解为查找→清洁→放置的序列。随后，它在抽象规划树内进行了深度优先搜索。令人印象深刻的是，每次探索后，它都成功回溯到父节点。这种一致的认知能力显著推动了gpt-4领先于其他模型。

此外，值得注意的是，gpt-4在检查了马桶后未能找到所需的肥皂条时经历了片刻的困惑。然而，它迅速意识到还有一个最后的位置没有检查——台面。最初，gpt-4可能以为需要从其他地方取肥皂条放到台面上，而没有考虑肥皂条可能已经在台面上的可能性。显然，gpt-4展示了自我反思的能力，使其能够在某些假设被证明无用时重新评估和修改假设。这种自我评估和重新调整的能力进一步帮助gpt-4完成了需要更深层次思考的任务。

**gpt-3.5-turbo在同一任务上的表现**（展示了模型在重复失败后无法坚持原始计划，陷入重复打开和关闭同一个柜子的循环，无法推进到新的位置）。

#### J.2.3 理解任务完成：已完成轨迹中的轮次和token分布

在本节中，我们通过检查已完成轨迹中轮次和token的分布，深入探讨任务完成的详细特征。我们的分析揭示了对任务常见完成模式的重要见解。

如图8所示，轮次分布的中位数为6.0，平均值为7.95，中间50%的任务在4.0到9.0轮之间。这一观察结果表明，虽然任务完成所需的轮数存在可变性，但相当大一部分任务在相对有限的轮数内完成。关于token分布，其中位数为1850.0，平均值为2220.1，中间50%的任务需要761到2709个token才能完成。此外，分析指出绝大多数任务在3000个token内完成，表明完成任务所需典型信息交换的上限。

了解轮次和token的常见范围对于预测任务需求至关重要，并可作为评估各种任务轨迹效率和有效性的基准。

**图8: 已完成任务轨迹中的轮次（左）和token（右）分布。** 对于轮次分布，中位数为6.0，平均值为7.95，中间50%在4.0至9.0轮之间。对于token分布，中位数为1850.0，平均值为2220.1，中间50%在761至2709个token之间。

#### J.2.4 任务超限的主要原因：模型倾向于重复先前内容

我们的观察（在第4.3节中详述）表明，任务超限（TLE）是任务未完成的主要因素，因此对其进行分析至关重要。在本节中，我们探讨了TLE事件的主要原因，这严重阻碍了模型成功完成任务的能力。

理解TLE为何发生对于理解模型为何未能完成任务以及制定提高模型性能的策略至关重要。我们的分析确定了模型倾向于重复先前生成的内容是TLE事件的最重要贡献因素。

我们详细分析了TLE交互轨迹。首先，我们发现TLE结果包含平均25.5轮的轨迹，远大于已完成轨迹中的轮数。并且它们中的大多数因轮次限制而被强制终止。

我们统计了在最后n轮中模型重复了某些内容的TLE结果百分比，其中这里的**重复**意味着两次响应在对话中共享较高的Rouge-L f值（Lin, 2004）。为了排除省略策略的影响，在取最后n轮之前，我们截断轨迹并保留总token数在3500以内的最长前缀。我们考虑最后n轮中的重复，而不仅仅是最后两轮，因为模型可能循环通过一系列状态。例如，模型可能重复循环通过一系列动作，如进入房间、打开抽屉、关闭抽屉、离开房间。在这种情况下，模型将在四个不同状态中循环，这意味着内容的精确重复只会在最后5轮中显现，而不仅仅是最后两轮。

正式地，我们将T定义为导致任务超限（TLE）结果的交互轨迹中智能体响应序列的集合。此集合中的每个元素表示为一个序列(r1, r2, ..., rm)，其中rk代表智能体在第k轮交互中的响应。我们将重复百分比P(n, t)定义如下：

P(n, t) = #{(r1, r2, ..., rm) ∈ T | ∃i, j(m-n < i < j ≤ m ∧ RougeL(ri, rj) ≥ t)} / #T

如图9所示，超过90%经历任务超限（TLE）的轨迹表现出显著的重复水平。这通过至少两个在最后10轮内的响应共享0.8或更高的Rouge-L分数来证明，表明存在显著的冗余程度。

**图9: P(n, t)，在所有TLE轨迹中，在省略策略开始前的最后n轮中存在一对响应其Rouge-L分数不低于t的百分比。**

**图10: webshop的平均样本有效性比率**

|  | 已完成 | 上下文超限 | 无效动作 | 无效格式 | 任务超限 |
|--|-------|-----------|---------|---------|---------|
| CodeLlama | 50.3% | 11.9% | 4.1% | - | 33.7% |
| Llama2 | 36.5% | 18.7% | 8.9% | - | 35.9% |

#### J.2.5 代码微调对LLM作为智能体的影响

鉴于汇总结果，我们认为代码微调显著有助于模型在相对简单和程序化的任务中的表现。结果表显示，CodeLlama系列在webshop任务中始终优于Llama2系列。然而，代码微调的负面影响似乎是可能损害模型的逻辑推理能力和情境意识。在数字卡牌游戏场景中，CodeLlama系列落后于Llama2系列。两种场景之间的主要区别在于所提供的指导。在webshop中，one-shot提示精确概述了一个购物过程模板，当被简单遵循时，可以获得令人满意的分数。相比之下，数字卡牌游戏要求模型评估双方的当前状态，制定复杂的对抗策略，并在没有简单程序化模板支持的情况下获得高分。

如图10所示，codellama系列在WebShop任务中的完成率显著高于llama2系列。

#### J.2.6 自我纠正能力

在许多测试案例中，模型失败的主要原因是无法从环境提供的错误反馈中识别自己的错误。这在DB任务中尤为明显。具有自我纠正SQL语句能力的模型显著优于其他模型。我们使用claude-2作为代表性示例来说明这种能力。

在一个数据库问题中，claude-2首先编写SQL查询，但在遇到MySQL语法错误（字段名包含空格未加反引号）后，它成功地从错误信息中识别出问题，纠正了语法（为字段名和表名添加反引号），最终成功执行查询并获得结果。这表明claude-2具有从错误中学习和自我纠正的能力。

（交互示例展示了claude-2逐步从SQL语法错误中学习并自我纠正的过程。）

---
