# ToolLLM: 促进大型语言模型掌握 16000+ 真实世界 API

**论文原文**: arXiv:2307.16789v2 [cs.AI] 3 Oct 2023  
**作者**: Yujia Qin¹\*, Shihao Liang¹\*, Yining Ye¹, Kunlun Zhu¹, Lan Yan¹, Yaxi Lu¹, Yankai Lin³†, Xin Cong¹, Xiangru Tang⁴, Bill Qian⁴, Sihan Zhao¹, Lauren Hong¹, Runchu Tian¹, Ruobing Xie⁵, Jie Zhou⁵, Mark Gerstein⁴, Dahai Li²,⁶, Zhiyuan Liu¹†, Maosong Sun¹†  
**机构**: ¹清华大学 ²ModelBest Inc. ³中国人民大学 ⁴耶鲁大学 ⁵微信AI, 腾讯公司 ⁶知乎公司  
**联系**: yujiaqin16@gmail.com  
**\*** 表示同等贡献。 **†** 通讯作者。

---

## 摘要

尽管开源大型语言模型（LLM）如 LLaMA 取得了进步，但在工具使用能力方面——即利用外部工具（API）来执行人类指令——仍然显著受限。原因是当前的指令微调主要集中在基本语言任务上，而忽略了工具使用领域。这与最先进的闭源 LLM（如 ChatGPT）卓越的工具使用能力形成鲜明对比。为弥合这一差距，我们提出了 ToolLLM，一个通用的工具使用框架，涵盖数据构建、模型训练和评估。我们首先介绍 ToolBench，一个用于工具使用的指令微调数据集，该数据集使用 ChatGPT 自动构建。具体来说，构建过程分为三个阶段：(i) API 收集：我们从 RapidAPI Hub 收集了涵盖 49 个类别的 16,464 个真实世界 RESTful API；(ii) 指令生成：我们提示 ChatGPT 生成涉及这些 API 的多样化指令，涵盖单工具和多工具场景；(iii) 解决方案路径标注：我们使用 ChatGPT 为每条指令搜索有效的解决方案路径（API 调用链）。为了增强 LLM 的推理能力，我们开发了一种新颖的基于深度优先搜索的决策树算法。它使 LLM 能够评估多个推理轨迹并扩展搜索空间。此外，为了评估 LLM 的工具使用能力，我们开发了一个自动评估器：ToolEval。基于 ToolBench，我们对 LLaMA 进行微调得到 ToolLLaMA，并为其配备一个神经 API 检索器来为每条指令推荐合适的 API。实验表明，ToolLLaMA 展现了执行复杂指令和泛化到未见 API 的卓越能力，并表现出与 ChatGPT 相当的性能。我们的 ToolLLaMA 还在一个分布外工具使用数据集 APIBench 上展示了强大的零样本泛化能力。代码、训练好的模型和演示可在 https://github.com/OpenBMB/ToolBench 公开获取。

---

## 1 引言

工具学习旨在释放大型语言模型的能力，使其能够有效地与各种工具（API）交互以完成复杂任务。通过将 LLM 与 API 集成，我们可以极大地扩展其实用性，并使其成为用户与庞大应用生态系统之间的高效中介。尽管开源 LLM（如 LLaMA）通过指令微调已具备多样化的能力，但在执行更高级的任务（如适当地与工具交互以满足复杂的人类指令）方面仍显不足。这种缺陷是因为当前的指令微调主要关注基本语言任务，而相对忽视了工具使用领域。另一方面，当前最先进的 LLM（如 ChatGPT 和 GPT-4）在利用工具方面展示了令人印象深刻的能力，但它们是闭源的，内部机制不透明。这限制了 AI 技术的民主化以及社区驱动创新和发展的范围。因此，我们认为迫切需要赋予开源 LLM 熟练掌握多样化 API 的能力。

虽然先前的研究已经探索了为工具使用构建指令微调数据，但它们未能充分激发 LLM 内部的工具使用能力，并且存在固有的局限性：(1) **API 数量有限**：它们要么不涉及真实世界的 API（如 REST API），要么只考虑了少量且多样性差的 API；(2) **场景受限**：现有工作局限于只涉及单一工具的指令。然而，现实场景可能要求多个工具交织在一起进行多轮工具执行以解决复杂任务。此外，它们通常假设用户预先手动指定给定指令的理想 API 集合，这对于大量真实世界 API 来说是不可行的；(3) **规划与推理能力不足**：现有工作采用 CoT 或 ReACT 进行模型推理，这些方法无法充分激发 LLM 中存储的能力，因此无法处理复杂指令。此外，一些工作甚至不执行 API 来获取真实响应，而这些响应是后续模型规划的重要信息。

为了促进开源 LLM 的工具使用能力，我们提出了 ToolLLM，一个通用的工具使用框架，包括数据构建、模型训练和评估。如图 1 所示，我们收集了一个高质量的指令微调数据集 ToolBench。它是使用具有函数调用功能的 ChatGPT（gpt-3.5-turbo-16k）自动构建的。ToolBench 与先前工作的比较见表 1。具体来说，ToolBench 的构建包含三个阶段：

*   **API 收集**：我们从 RapidAPI（一个托管大量开发者提供的真实世界 API 的平台）收集了 16,464 个 REST API。这些 API 涵盖 49 个不同的类别，如社交媒体、电子商务和天气。对于每个 API，我们从 RapidAPI 爬取详细的 API 文档，包括功能描述、所需参数、API 调用的代码片段等。通过理解这些文档来学习执行 API，LLM 可以泛化到训练中未见过的新的 API；
*   **指令生成**：我们首先从整个 API 集合中采样 API，然后提示 ChatGPT 为这些 API 生成多样化的指令。为了覆盖实际场景，我们策划了涉及单工具和多工具场景的指令。这确保我们的模型不仅学会如何与单个工具交互，还学会如何组合它们以完成复杂任务；
*   **解决方案路径标注**：每个解决方案路径可能包含多轮模型推理和实时 API 调用，以得到最终响应。然而，即使是最复杂的 LLM（即 GPT-4），对于复杂的人类指令也只能达到较低的通过率，使得标注效率低下。为此，我们开发了一种新颖的基于深度优先搜索的决策树（DFSDT）来增强 LLM 的规划和推理能力。与传统的 ReACT 相比，DFSDT 使 LLM 能够评估大量推理路径，并做出深思熟虑的决策，要么回退步骤，要么沿着有希望的路径前进。在实验中，DFSDT 显著提高了标注效率，并成功完成了那些使用 ReACT 无法完成的复杂指令。

为了评估 LLM 的工具使用能力，我们开发了一个由 ChatGPT 支持的自动评估器 ToolEval。它包括两个关键指标：(1) **通过率**：衡量 LLM 在有限预算内成功执行指令的能力；(2) **胜率**：比较两个解决方案路径的质量和实用性。我们证明 ToolEval 与人工评估具有高度相关性，为机器工具使用提供了稳健、可扩展且可靠的评估。

通过在 ToolBench 上微调 LLaMA，我们得到了 ToolLLaMA。基于我们的 ToolEval 进行评估后，我们得出以下发现：

*   ToolLLaMA 展现了处理单工具和复杂多工具指令的令人信服的能力。如图 2 所示，ToolLLaMA 优于 Text-Davinci-003 和 Claude-2，达到了与"教师模型"ChatGPT 相当的性能，仅略逊于 GPT-4。此外，ToolLLaMA 对之前未见过的 API 表现出强大的泛化能力，仅需 API 文档即可有效适应新 API。这种灵活性允许用户无缝地整合新 API，从而增强模型的实际效用。
*   我们证明 DFSDT 是一种通用的决策制定策略，可以增强 LLM 的推理能力。DFSDT 通过考虑多个推理轨迹扩展了搜索空间，并实现了比 ReACT 显著更优的性能。
*   我们训练了一个神经 API 检索器，在实际应用中减轻了从大型 API 池中手动选择的需求。如图 1 所示，给定一条指令，API 检索器推荐一组相关的 API，这些 API 被发送给 ToolLLaMA 进行多轮决策，以得出最终答案。尽管需要从大型 API 池中筛选，但检索器表现出卓越的检索精度，返回的 API 与真实情况紧密对齐。
*   ToolLLaMA 在分布外数据集 APIBench 上展现了强大的泛化性能。尽管没有在 APIBench 的任何 API 或指令上进行训练，ToolLLaMA 的表现与专门为 APIBench 设计的 Gorilla 模型相当。

---

## 2 数据集构建

我们介绍 ToolBench 的三阶段构建过程：API 收集（§2.1）、指令生成（§2.2）和解决方案路径标注（§2.3）。所有过程均基于 ChatGPT（gpt-3.5-turbo-16k），只需最少的人工监督，并且可以轻松扩展到新的 API。

### 2.1 API 收集

我们首先介绍 RapidAPI 及其层次结构，然后介绍我们如何爬取和筛选 API。

**RapidAPI Hub** RapidAPI 是一个领先的 API 市场，将开发者与数以千计的真实世界 API 连接起来，简化了将多样化服务集成到应用程序中的过程。开发者只需注册一个 RapidAPI 密钥即可测试和连接各种 API。RapidAPI 中的所有 API 可分为 49 个粗粒度类别，如体育、金融和天气。这些类别将 API 与最相关的主题关联起来。此外，该中心还提供 500 多个细粒度的分类，称为集合（collections），例如中文 API 和数据库 API。同一集合中的 API 共享共同特征，通常具有相似的功能或目标。

**RapidAPI 的层次结构** 如图 3 所示，每个工具可能由多个 API 组成。对于每个工具，我们爬取以下信息：工具的名称和描述、主机的 URL，以及属于该工具的所有可用 API；对于每个 API，我们记录其名称、描述、HTTP 方法、必需参数、可选参数、请求体、可执行的 API 调用代码片段以及一个示例 API 调用响应。这些丰富而详细的元数据是 LLM 理解和有效使用 API 的宝贵资源，即使是在零样本方式下也能发挥作用。

**API 筛选** 最初，我们从 RapidAPI 收集了 10,853 个工具（53,190 个 API）。然而，这些 API 的质量和可靠性差异很大。特别是，一些 API 可能维护不善，例如返回 404 错误或其他内部错误。为此，我们进行了严格的筛选过程（详见附录 A.1），以确保 ToolBench 的最终工具集是可靠且功能正常的。最终，我们只保留了 3,451 个高质量工具（16,464 个 API）。

### 2.2 指令生成

与先前的工作不同，我们特别关注指令生成的两个关键方面：(1) **多样性**：训练 LLM 处理广泛的 API 使用场景，从而提高其泛化能力和鲁棒性；(2) **多工具使用**：反映现实世界中经常需要多种工具协同的情况，提高 LLM 的实际适用性和灵活性。为此，我们不是从头开始构思指令然后搜索相关的 API，而是采样不同的 API 组合，并构建涉及这些 API 的各种指令。

**为 API 生成指令** 定义总 API 集为 S_api，每次我们从 S_api 中采样少量 API：S_sub_N = {API1, ..., APIN}。我们提示 ChatGPT 理解这些 API 的功能，然后生成 (1) 涉及 S_sub_N 中 API 的可能指令列表 Inst\*，以及 (2) 每条指令 Inst\* 的相关 API 集合 S_rel\* ⊂ S_sub_N，即生成 {[S_rel_1, Inst1], ..., [S_rel_N', InstN']}，其中 N' 表示生成的实例数量。这些（指令，相关 API）对将用于训练 §3.1 中的 API 检索器。我们使用不同的采样策略（稍后介绍）来覆盖所有 API 及其大多数组合，从而确保指令的多样性。

ChatGPT 的提示由以下部分组成：(1) 预期指令生成任务的一般描述；(2) S_sub_N 中每个 API 的完整文档，帮助 ChatGPT 理解其功能和相互作用；(3) 三个上下文内种子示例 {seed1, seed2, seed3}。每个种子示例都是由人类专家编写的理想指令生成样例。这些种子示例被用于通过上下文学习更好地规范 ChatGPT 的行为。我们总共为单工具/多工具设置编写了 12/36 个多样化的种子示例（S_seed），每次随机采样三个示例。指令生成的具体提示在附录 A.7 中描述。

总体而言，生成过程可以表述如下：

ChatGPT({[S_rel_1, Inst1], ..., [S_rel_N', InstN']} | API1, ..., APIN, seed1, ..., seed3)，其中 API1,...,APIN ∈ S_API，seed1,...,seed3 ∈ S_seed。

**不同场景的采样策略** 如图 3 所示，对于单工具指令（I1），我们遍历每个工具并为其 API 生成指令。然而，对于多工具设置，由于 RapidAPI 中不同工具之间的关联稀疏，从整个工具集中随机采样工具组合通常会导致一系列不相关的工具，无法通过单条指令自然地覆盖。为解决这个稀疏性问题，我们利用 RapidAPI 的层次结构信息。由于属于同一 RapidAPI 类别或集合的工具在功能和目标上通常是相关的，我们从同一类别/集合中随机选择 2-5 个工具，并从每个工具中最多采样 3 个 API 来生成指令。我们将生成的指令分别称为**类别内多工具指令（I2）**和**集合内多工具指令（I3）**。通过严格的人工评估，我们发现以这种方式生成的指令已经具有很高的多样性，涵盖了各种实际场景。我们还使用 Atlas 提供了指令的可视化来支持我们的观点。

在生成初始指令集后，我们通过评估相关 API 是否存在于 S_sub_N 中来进一步筛选那些包含幻觉相关 API 的指令。最终，我们收集了近 20 万个合格的（指令，相关 API）对，其中 I1、I2 和 I3 分别包含 87,413、84,815 和 25,251 个实例。

### 2.3 解决方案路径标注

如图 4 所示，给定一条指令 Inst\*，我们提示 ChatGPT 搜索一个有效的动作序列：{a1, ..., aN}。这个多步骤的决策过程被转化为 ChatGPT 的多轮对话。在每一轮 t，模型基于之前的交互生成一个动作 at，即 ChatGPT(at | {a1, r1, ..., a_{t-1}, r_{t-1}}, Inst\*)，其中 r\* 表示真实的 API 响应。对于每个 at，ChatGPT 应指定其"思考"（thought）、要使用哪个 API 以及该 API 的具体参数，即 at 的格式为："思想: ..., API 名称: ..., 参数: ..."。

为了利用 ChatGPT 的函数调用功能，我们将每个 API 视为一个特殊函数，并将其 API 文档输入到 ChatGPT 的函数字段中。这样，模型就能理解如何调用该 API。对于每条指令 Inst\*，我们将所有采样的 API S_sub_N 作为可用函数提供给 ChatGPT。为了让 ChatGPT 完成动作序列，我们定义了两个额外的函数，即"用最终答案结束"和"放弃并结束"。前者有一个参数对应于原始指令的详细最终答案；而后者用于在多次尝试 API 调用后，所提供的 API 无法完成原始指令的情况。

**基于深度优先搜索的决策树** 在我们的初步研究中，我们发现 CoT 或 ReACT 存在固有的局限性：(1) **错误传播**：一个错误的动作可能会进一步传播错误，导致模型陷入错误的循环，例如持续以错误方式调用 API 或产生 API 幻觉；(2) **探索有限**：CoT 或 ReACT 只探索一个可能的方向，导致对整个动作空间的探索有限。因此，即使是 GPT-4 也常常无法找到有效的解决方案路径，使得标注变得困难。

为此，我们提出构建一个决策树来扩展搜索空间，并增加找到有效路径的可能性。如图 4 所示，我们的 DFSDT 允许模型评估不同的推理路径，并选择要么 (1) 沿着一条有希望的路径前进，要么 (2) 通过调用"放弃并结束"函数放弃现有节点并扩展一个新节点。在节点扩展期间，为了多样化子节点并扩展搜索空间，我们用之前生成的节点的信息提示 ChatGPT，并明确鼓励模型生成不同的节点。对于搜索过程，我们优先选择深度优先搜索（DFS）而不是广度优先搜索（BFS），因为只要找到一条有效路径，标注就可以完成。使用 BFS 将花费过多的 OpenAI API 调用。更多细节在附录 A.8 中描述。我们对所有生成的指令执行 DFSDT，并只保留那些通过的解决方案路径。最终，我们生成了 126,486 个（指令，解决方案路径）对，用于在 §3.2 中训练 ToolLLaMA。

---

## 3 实验

在本节中，我们研究 ToolLLM 框架的性能。我们首先介绍评估指标，并评估 API 检索器和 DFSDT 的有效性（§3.1）。然后我们在 §3.2 中呈现主要实验，接着在 §3.3 中进行泛化实验。

### 3.1 初步实验

**ToolEval** 考虑到 RapidAPI 上 API 的时间变化性以及一条指令的无限潜在解决方案路径，为每个测试指令标注一个固定的真实解决方案路径是不可行的。此外，在比较不同模型时，确保它们在评估期间使用相同版本的 API 至关重要。考虑到人工评估可能耗时，我们遵循 AlpacaEval 的方法，开发了一个基于 ChatGPT 的高效评估器 ToolEval，它包含两个评估指标（详见附录 A.5）：(1) **通过率**：计算在有限预算内成功完成指令的比例。该指标衡量 LLM 对指令的可执行性，可被视为理想工具使用的基本要求；(2) **胜率**：我们向 ChatGPT 评估器提供一条指令和两个解决方案路径，并获取其偏好（即哪一个更好）。我们为这两个指标预定义了一组标准，这些标准被组织为 ChatGPT 评估器的提示。我们基于 ChatGPT 进行多次评估以提高可靠性。然后我们计算评估器的平均结果。

通过严格测试（详见附录 A.5），我们发现 ToolEval 在通过率方面与人工标注者达到 87.1% 的高度一致性，在胜率方面达到 80.3%。这表明 ToolEval 在很大程度上能够反映和代表人工评估。

**API 检索器的有效性** API 检索器旨在检索与指令相关的 API。我们采用 Sentence-BERT 基于 BERT-BASE 训练一个密集检索器。API 检索器将指令和 API 文档编码为两个嵌入向量，并通过嵌入相似度计算它们的相关性。对于训练，我们将 §2.2 中生成的每条指令的相关 API 视为正例，并采样一些其他 API 作为负例进行对比学习。作为基线方法，我们选择 BM25 和 OpenAI 的 text-embedding-ada-002。我们使用 NDCG 评估检索性能。我们在单工具指令（I1）、类别内多工具指令（I2）和集合内多工具指令（I3）上训练和评估模型。

如表 2 所示，我们的 API 检索器在所有设置中一致优于基线方法，表明其在存在海量 API 的现实场景中的可行性。此外，I1 的 NDCG 得分通常高于 I2 和 I3，这意味着单工具指令检索比多工具设置更简单。

**DFSDT 相对于 ReACT 的优越性** 在解决方案路径标注之前，我们验证了 DFSDT 的有效性。基于 ChatGPT，我们使用通过率指标比较 DFSDT 和 ReACT。由于 DFSDT 消耗的 OpenAI API 调用比 ReACT 更多，为了更公平的比较，我们还建立了一个"ReACT@N"基线，即进行多次 ReACT 直到总成本达到与 DFSDT 相同的水平。一旦 ReACT@N 找到了有效的解决方案，我们就认为它通过了。

从表 3 可以看出，DFSDT 在所有场景中均显著优于两个基线。由于我们只保留那些通过的标注作为训练数据，在相同预算下，使用 DFSDT 可以标注更多的指令。这使得 DFSDT 成为一种更高效的方式，节省了总标注成本。我们还发现，DFSDT 的性能提升对于更难的指令（即 I2 和 I3）比简单指令（I1）更为明显。这意味着通过扩展搜索空间，DFSDT 可以更好地解决那些困难的、复杂的、无论进行多少次 ReACT 都无法解决的指令。在我们的数据集中包含这样的"困难示例"可以充分激发复杂场景下的工具使用能力。

### 3.2 主要实验

**ToolLLaMA** 我们使用指令-解决方案对微调 LLaMA-2 7B 模型。原始 LLaMA-2 模型的序列长度为 4096，在我们的设置中不够用，因为 API 响应可能非常长。为此，我们使用位置插值将上下文长度扩展到 8192（训练细节见附录 A.3）。

**设置** 理想情况下，通过扩展训练数据中指令和独特工具的数量和多样性，ToolLLaMA 有望泛化到训练中未见过的新的指令和 API。这很有意义，因为用户可以定义自定义 API，并期望 ToolLLaMA 根据文档进行适应。为此，我们努力在三个层面上评估 ToolLLaMA 的泛化能力：(1) **指令**：训练数据中同一工具集上的未见指令；(2) **工具**：属于训练数据中工具的同一（已见）类别的未见工具；(3) **类别**：属于训练数据中工具的不同（未见）类别的未见工具。

我们在三种场景上进行实验：单工具指令（I1）、类别内多工具指令（I2）和集合内多工具指令（I3）。对于 I1，我们对上述三个层面进行评估（I1-指令、I1-工具和 I1-类别）；对于 I2，由于训练指令已经涉及同一类别的不同工具，我们只进行级别 1 和级别 3 的泛化评估（I2-指令和 I2-类别）；类似地，对于 I3，我们只进行级别 1 的泛化评估（I3-指令），因为它已经涵盖了涉及不同类别工具的各种组合的指令（RapidAPI 集合中的工具可能来自不同的 RapidAPI 类别）。对于每个测试指令，我们将真实 API 集 S_sub_N 提供给每个模型。这模拟了用户指定他们偏好的 API 集的场景。

**基线** 我们选择两个为通用对话微调的 LLaMA 变体，即 Vicuna 和 Alpaca。我们还选择"教师模型"ChatGPT、Text-Davinci-003、GPT-4 和 Claude-2 作为基线，并对它们应用 DFSDT 和 ReACT。在计算胜率时，每个模型与 ChatGPT-ReACT 进行比较。

**主要结果** 结果见表 4，从中我们得出：

1.  尽管我们进行了大量的提示工程，Vicuna 和 Alpaca 都未能通过任何指令（通过率和胜率均为 0），这意味着它们的指令遵循能力不涵盖工具使用领域。这凸显了当前主要关注语言技能的指令微调尝试的不足；
2.  对于所有 LLM，使用 DFSDT 在通过率和胜率方面都显著优于 ReACT。值得注意的是，ChatGPT+DFSDT 在通过率上超过了 GPT-4+ReACT，并且在胜率上表现相当。这凸显了 DFSDT 在决策制定方面相对于 ReACT 的优越性；
3.  当使用 DFSDT 时，ToolLLaMA 的性能远优于 Text-Davinci-003 和 Claude-2，并且达到了几乎与 ChatGPT（教师模型）相当的结果。总的来说，尽管需要泛化到未见指令和工具，ToolLLaMA+DFSDT 在所有场景中都展示了有竞争力的泛化性能，其通过率仅次于 GPT4+DFSDT。

总的来说，这些结果表明 ToolBench 能够充分激发 LLM 内部的工具使用能力，并使它们能够熟练地掌握各种指令中甚至从未见过的 API。

**将 API 检索器与 ToolLLaMA 集成** 在现实场景中，要求用户从大型 API 池中手动推荐 API 可能不切实际。为模拟这种实际设置并测试我们的 API 检索器的效率，我们将 API 检索器推荐的前 5 个 API（而不是真实 API 集 S_sub_N）提供给 ToolLLaMA。如表 4 所示，使用检索到的 API 甚至比使用真实的 API 集在性能上有所提升（通过率和胜率均提高）。这是因为真实 API 集中的许多 API 可以被具有更好功能的其他类似 API 替代，而我们的 API 检索器能够成功识别这些替代品。换句话说，我们的检索器扩展了相关 API 的搜索空间，并为当前指令找到了更合适的 API。这有力证明了我们的 API 检索器在检索相关 API 方面的卓越能力，特别是考虑到检索器从包含 16,000 多个 API 的庞大池中进行选择。

### 3.3 对 APIBench 的分布外泛化

**设置** 我们进一步将 ToolLLaMA 扩展到分布外数据集 APIBench，以验证其泛化能力。为了评估 ToolLLaMA 在这些新领域的泛化能力，我们为 ToolLLaMA 配备了两个检索器：我们训练的 API 检索器和真实检索器。我们评估 APIBench 的三个领域，即 TorchHub、TensorHub 和 HuggingFace。我们将 ToolLLaMA 与 Gorilla（一个使用 APIBench 训练数据微调的 LLaMA-7B 模型）进行比较。遵循原始论文，我们采用 Gorilla 的两个官方设置：零样本设置（ZS）和检索感知设置（RS）。后者意味着检索到的 API 作为提示的一部分发送给模型；而前者在训练模型时不将 API 纳入提示中。我们采用官方评估指标，报告 AST 准确率和幻觉率。

**结果** 结果如表 5 所示。总的来说，尽管在完全不同的 API 领域和指令领域上训练，ToolLLaMA 在所有三个数据集上都取得了显著的分布外泛化性能。具体来说，ToolLLaMA+我们的 API 检索器在 HuggingFace 和 TorchHub 上的 AST 准确率方面，优于两种训练设置（ZS/RS）下的 Gorilla+BM25。使用相同的真实检索器时，ToolLLaMA 与 Gorilla-ZS 相比始终具有优势。需要注意的是，由于我们更复杂的设置（如多工具使用和多步推理），Gorilla 模型无法泛化到我们的 ToolBench 数据集。

---

## 4 相关工作

**工具学习** 最近的研究揭示了 LLM 在掌握工具和在复杂环境中做出决策方面不断增强的能力。获取外部工具使 LLM 具备了实时事实知识、多模态功能和垂直领域的专业技能。然而，开源 LLM 在工具使用方面仍远落后于最先进的 LLM，并且 SOTA LLM 如何获得工具使用能力仍不清楚。在本文中，我们旨在弥合这一差距并探究其底层机制。

**指令微调** 指令微调增强了 LLM 理解人类指令和生成适当响应的能力。由于手动标注指令微调数据耗时费力，self-instruct 方法提出从 SOTA LLM 生成高质量数据，这促进了最近多轮对话数据整理的趋势。然而，与对话相比，考虑到 API 的巨大多样性和多工具指令的复杂性，工具学习本质上更具挑战性。因此，即使是 GPT-4 也常常无法找到有效的解决方案路径。然而，现有的工具学习数据集及其构建方法无法有效满足真实的人类需求，如 §1 所述。相反，我们的 ToolBench 是为实际场景设计的，改进了以前的工具学习数据构建流程。

**提示 LLM 进行决策制定** 提示促进了 LLM 将高层次任务分解为子任务并生成基于实际的计划。ReACT 通过允许 LLM 为某个动作给出适当的理由并结合环境反馈进行推理，整合了推理和行动。然而，这些研究没有纳入决策撤回机制，这在初始错误可能导致后续级联错误时变得有问题。最近，Reflexion 通过要求 LLM 反思之前的失败来缓解这个问题。我们的 DFSDT 将 Reflexion 扩展为一种更通用的方法，允许 LLM 评估不同的推理路径并选择最有前途的一条。需要注意的是，DFSDT 与同期工作——思维树（ToT）推理——有着相似的思想。然而，我们的 DFSDT 针对的是决策空间无限的通用决策问题，而 ToT 处理的是可以通过暴力搜索解决的相对简单的任务，如"24 点游戏"和"填字游戏"。DFSDT 和 ToT 的不同目标决定了它们在实现细节上的显著差异。

---

## 5 结论

在这项工作中，我们介绍了如何激发 LLM 内部的工具使用能力。我们首先提出了一个指令微调数据集 ToolBench，它涵盖了 16,000 多个真实世界的 API 和各种实际用例场景，包括单工具和多工具任务。ToolBench 的构建完全使用 ChatGPT，只需要最少的人工监督。此外，我们提出了 DFSDT 来增强 LLM 的规划和推理能力，使它们能够策略性地在推理路径中导航。为了高效评估工具学习，我们设计了一个自动评估器 ToolEval。通过在 ToolBench 上微调 LLaMA，得到的模型 ToolLLaMA 与 ChatGPT 的性能相匹配，并展现出对未见 API 的卓越泛化能力。此外，我们开发了一个神经 API 检索器来为每条指令推荐相关的 API。该检索器可以与 ToolLLaMA 集成，形成一个更自动化的工具使用流程。在实验中，我们展示了我们的流程对分布外领域的泛化能力。总的来说，这项工作为未来在指令微调和工具使用交叉领域的研究铺平了道路。

---

## 参考文献

1. Michael Ahn 等. Do as i can, not as i say: Grounding language in robotic affordances. *arXiv preprint*, abs/2204.01691, 2022.
2. Stephen Bach 等. Promptsource: An integrated development environment and repository for natural language prompts. *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics: System Demonstrations*, pp. 93–104, 2022.
3. Sébastien Bubeck 等. Sparks of artificial general intelligence: Early experiments with gpt-4. *arXiv preprint arXiv:2303.12712*, 2023.
4. Shouyuan Chen 等. Extending context window of large language models via positional interpolation. *arXiv preprint arXiv:2306.15595*, 2023.
5. Wei-Lin Chiang 等. Vicuna: An open-source chatbot impressing gpt-4 with 90%\* chatgpt quality, March 2023.
6. Jacob Devlin 等. BERT: Pre-training of deep bidirectional transformers for language understanding. *Proceedings of NAACL 2019*, pp. 4171–4186, 2019.
7. Ning Ding 等. Enhancing chat language models by scaling high-quality instructional conversations. *arXiv preprint arXiv:2305.14233*, 2023.
8. Difei Gao 等. Assistgpt: A general multi-modal assistant that can plan, execute, inspect, and learn. *arXiv preprint arXiv:2306.08640*, 2023.
9. Tanmay Gupta, Aniruddha Kembhavi. Visual programming: Compositional visual reasoning without training. *Proceedings of IEEE/CVF CVPR*, pp. 14953–14962, 2023.
10. Shibo Hao 等. Toolkengpt: Augmenting frozen language models with massive tools via tool embeddings. *arXiv preprint arXiv:2305.11554*, 2023.
11. Wenlong Huang 等. Language models as zero-shot planners: Extracting actionable knowledge for embodied agents. *ICML 2022*, 2022a.
12. Wenlong Huang 等. Inner monologue: Embodied reasoning through planning with language models. *arXiv preprint*, abs/2207.05608, 2022b.
13. Kalervo Järvelin, Jaana Kekäläinen. Cumulated gain-based evaluation of ir techniques. *ACM Transactions on Information Systems*, 20(4):422–446, 2002.
14. Qiao Jin 等. Genegpt: Augmenting large language models with domain tools for improved access to biomedical information. *arXiv*, 2023.
15. Minghao Li 等. Api-bank: A benchmark for tool-augmented llms. *arXiv preprint arXiv:2304.08244*, 2023a.
16. Xuechen Li 等. Alpacaeval: An automatic evaluator of instruction-following models. 2023b.
17. Swaroop Mishra 等. Cross-task generalization via natural language crowdsourcing instructions. *Proceedings of ACL 2022 (Volume 1: Long Papers)*, pp. 3470–3487, 2022.
18. Reiichiro Nakano 等. Webgpt: Browser-assisted question-answering with human feedback. *arXiv preprint*, abs/2112.09332, 2021.
19. OpenAI. OpenAI: Introducing ChatGPT, 2022.
20. OpenAI. Gpt-4 technical report, 2023.
21. Shishir G Patil 等. Gorilla: Large language model connected with massive apis. *arXiv preprint arXiv:2305.15334*, 2023.
22. Guilherme Penedo 等. The refinedweb dataset for falcon llm: outperforming curated corpora with web data, and web data only. *arXiv preprint arXiv:2306.01116*, 2023.
23. Cheng Qian 等. Creator: Disentangling abstract and concrete reasonings of large language models through tool creation. *arXiv preprint arXiv:2305.14318*, 2023.
24. Yujia Qin 等. Webcpm: Interactive web search for chinese long-form question answering. *arXiv preprint arXiv:2305.06849*, 2023a.
25. Yujia Qin 等. Tool learning with foundation models. *arXiv preprint arXiv:2304.08354*, 2023b.
26. Nils Reimers, Iryna Gurevych. Sentence-bert: Sentence embeddings using siamese bert-networks. *arXiv preprint arXiv:1908.10084*, 2019.
27. Stephen Robertson 等. The probabilistic relevance framework: Bm25 and beyond. *Foundations and Trends® in Information Retrieval*, 3(4):333–389, 2009.
28. Timo Schick 等. Toolformer: Language models can teach themselves to use tools. *arXiv preprint*, abs/2302.04761, 2023.
29. Yongliang Shen 等. Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface, 2023.
30. Noah Shinn 等. Reflexion: Language agents with verbal reinforcement learning, 2023.
31. Yifan Song 等. Restgpt: Connecting large language models with real-world applications via restful apis. *arXiv preprint arXiv:2306.06624*, 2023.
32. Qiaoyu Tang 等. Toolalpaca: Generalized tool learning for language models with 3000 simulated cases. *arXiv preprint arXiv:2306.05301*, 2023.
33. Rohan Taori 等. Stanford alpaca: An instruction-following llama model. 2023.
34. Hugo Touvron 等. Llama: Open and efficient foundation language models. *arXiv preprint arXiv:2302.13971*, 2023a.
35. Hugo Touvron 等. Llama 2: Open foundation and fine-tuned chat models. *arXiv preprint arXiv:2307.09288*, 2023b.
36. Sai Vemprala 等. Chatgpt for robotics: Design principles and model abilities. Technical Report MSR-TR-2023-8, Microsoft, 2023.
37. Yizhong Wang 等. Self-instruct: Aligning language model with self generated instructions. *arXiv preprint arXiv:2212.10560*, 2022.
38. Jason Wei 等. Finetuned language models are zero-shot learners. *arXiv preprint arXiv:2109.01652*, 2021.
39. Jason Wei 等. Chain-of-thought prompting elicits reasoning in large language models, 2023.
40. Chenfei Wu 等. Visual chatgpt: Talking, drawing and editing with visual foundation models. *arXiv preprint*, abs/2303.04671, 2023.
41. Can Xu 等. Wizardlm: Empowering large language models to follow complex instructions, 2023a.
42. Qiantong Xu 等. On the tool manipulation capability of open-source large language models. *arXiv preprint arXiv:2305.16504*, 2023b.
43. Linyao Yang 等. Chatgpt is not enough: Enhancing large language models with knowledge graphs for fact-aware language modeling. *arXiv preprint arXiv:2306.11489*, 2023.
44. Shunyu Yao 等. React: Synergizing reasoning and acting in language models. *arXiv preprint*, abs/2210.03629, 2022.
45. Shunyu Yao 等. Tree of thoughts: Deliberate problem solving with large language models. *arXiv preprint arXiv:2305.10601*, 2023.
46. Yining Ye 等. Large language model as autonomous decision maker. *arXiv preprint arXiv:2308.12519*, 2023.
47. Yuchen Zhuang 等. Toolqa: A dataset for llm question answering with external tools. *arXiv preprint arXiv:2306.13304*, 2023.

---

## 附录 A 实现细节

### A.1 RapidAPI 筛选细节

我们执行了严格的筛选过程，以确保 ToolBench 的最终工具集可靠且功能正常。筛选过程如下：(1) **初始测试**：我们首先测试每个 API 的基本功能，以确认它们是否可运行。我们丢弃任何不符合此基本标准的 API；(2) **示例响应评估**：我们进行 API 调用以获取示例响应。然后我们通过响应时间和质量来评估它们的有效性。我们省略那些始终表现出较长响应时间的 API。此外，我们过滤掉响应质量低的 API，例如返回 HTML 源代码或其他错误消息的 API。

### A.2 API 响应压缩

在检查每个 API 返回的响应时，我们发现一些响应可能包含冗余信息，并且太长而无法输入到 LLM 中。由于 LLM 的上下文长度有限，这可能导致问题。因此，我们执行响应压缩，以减少 API 响应的长度，同时保留其关键信息。

由于每个 API 都有固定的响应格式，我们使用 ChatGPT 分析一个响应示例，并删除响应中不重要的键以缩短其长度。ChatGPT 的提示包含每个 API 的以下信息：(1) 工具文档，包括工具名称、工具描述、API 名称、API 描述、参数和一个示例 API 响应。这给 ChatGPT 提供了 API 功能的提示；(2) 3 个上下文学习示例，每个示例包含一个原始 API 响应和一个由专家编写的压缩响应模式。通过这种方式，我们获得了所有 API 的响应压缩策略。在推理过程中，当 API 响应长度超过 1024 个 token 时，我们通过删除不重要信息来压缩响应。如果压缩后的响应仍然超过 1024，我们只保留前 1024 个 token。通过人工评估，我们发现这种压缩保留了 API 响应中包含的重要信息，并成功去除了噪声。

### A.3 训练 ToolLLaMA 的细节

我们以多轮对话模式训练模型。对于训练数据格式，我们保持输入和输出与 ChatGPT 相同。由于不清楚 ChatGPT 如何组织函数调用字段，我们只是将此信息连接到输入中，作为 ToolLLaMA 提示的一部分。对于训练超参数，我们使用学习率 5×10⁻⁵、预热比例 4×10⁻²、总批量大小 64、最大序列长度 8192，并使用位置插值比例 2。我们训练模型两个 epoch，并在开发集上选择性能最佳的模型检查点，然后在测试集上进行评估。

### A.4 DFSDT 细节

在实践中，平衡有效性与成本（OpenAI API 调用的数量）至关重要。经典的 DFS 算法在每一步生成多个子节点，然后对所有子节点进行排序，并选择得分最高的节点进行扩展。在贪心地扩展到终端节点后，DFS 回溯以探索附近的节点，扩展搜索空间。在整个算法中，最耗费资源的部分是子节点的排序过程。如果我们使用 LLM 一次评估两个节点，则需要大约 O(n log n) 复杂度的 OpenAI API 调用，其中 n 是子节点的数量。

实际上，我们凭经验发现，在大多数情况下，排名最高的节点通常是首先生成的节点。因此，我们跳过了子节点的排序过程，选择前序遍历（DFS 的一种变体）进行树搜索。这种设计具有以下优点：

*   如果模型没有撤回某个动作（例如，对于简单指令的情况），那么 DFSDT 退化为 ReACT，使其与 ReACT 一样高效。
*   算法完成后，通过这种方法探索的节点几乎与经典 DFS 搜索找到的节点相同。因此，它也可以处理只有 DFS 才能解决的复杂指令。

总的来说，这种设计实现了与 DFS 相似的性能，同时显著降低了成本。还应注意的是，ReACT 可以被视为 DFSDT 的退化版本。因此，尽管 ToolLLaMA 是在由 DFSDT 创建的数据上训练的，但在推理过程中，该模型可以通过 ReACT 或 DFSDT 来使用。

### A.5 ToolEval 细节

我们采用两个指标进行自动工具使用能力评估：通过率和胜率。

**通过率细节** 为了评估解决方案路径是否完成了原始指令中概述的任务并成功通过，我们首先需要考虑指令的可解性。原则上，一条指令可以分为 (1) **可解的**：例如，提供的工具中至少有一个可能有助于解决原始指令；或 (2) **不可解的**：例如，所有 API 都与指令无关，或指令提供了无效信息（如无效的电子邮件地址）。

为了确定解决方案路径是否被视为通过，我们需要考虑指令是可解的还是不可解的。在我们的评估中，每条解决方案路径可以被赋予三种标签：通过、失败和不确定。具体而言，我们定义以下不同规则：

如果指令是可解的：
1.  如果模型给出结束类型"放弃并结束"：
    (a) 如果在尝试了所有 API 后未从 API 收到有用信息，该解决方案路径被视为**通过**。
    (b) 如果模型只调用了少数 API 或从 API 收到了有效信息，该解决方案路径被视为**失败**。
2.  如果模型给出结束类型"用最终答案结束"：
    (a) 如果 API 没有提供有效信息，并且模型已尝试所有 API 来检索有用信息，但最终答案仍未解决原始指令或表示拒绝，该解决方案路径被视为**通过**。
    (b) 如果工具提供了有效信息，但最终答案没有完全解决指令或表示拒绝，该解决方案路径被视为**失败**。
    (c) 如果最终答案完全解决了原始指令，该解决方案路径被视为**通过**。
    (d) 如果无法根据最终答案的内容确定指令是否被解决，该解决方案路径被视为**不确定**。

如果指令是不可解的：
1.  如果模型给出结束类型"用最终答案结束"：
    (a) 如果最终答案解决了一个最初被认为是不可解的指令，该解决方案路径被视为**通过**。
    (b) 如果最终答案表示拒绝，该解决方案路径被视为**通过**。
    (c) 如果最终答案是由模型自己产生的幻觉，并提供了假阳性的响应，该解决方案路径被视为**失败**。
2.  如果模型给出结束类型"放弃并结束"：
    (a) 在这种情况下，该解决方案路径被视为**通过**。

对于每条解决方案路径，我们指示 ChatGPT 评估器生成多个（≥4）预测，并进行多数投票以得出最终的通过率。

**胜率细节** 由于通过率只衡量指令是否完成，而不衡量完成得好坏，我们采用了另一个指标：胜率。它通过比较给定指令的两个解决方案路径来衡量。我们假设通过的候选者优于失败的候选者，并只比较那些被 ChatGPT 评估器标注为"通过"或"失败"的解决方案路径。注意，与另一个解决方案路径相比，一个解决方案路径将被标注为以下之一：赢、输或平。我们为评估器的行为建立了规则，以决定哪个解决方案路径更好，标准如下：

1.  **信息丰富性**：最终答案是否包含回答原始指令所需的所有必要信息。显著更丰富的答案更好，而足以回答问题但丰富程度相似则算平局。
2.  **事实性**：是否准确描述了已执行的操作以及最终失败的原因。最终答案中更准确的描述更好。
3.  **推理**：如果查询仍未解决，是否提供了详细且准确的失败原因。更详细的原因更好。
4.  **里程碑**：计算执行期间达到的里程碑数量。
5.  **探索**：在执行过程中是否尝试了更多潜在有用的 API。使用更多 API 更好。
6.  **成本**：如果使用的 API 数量相同，则重复（冗余）API 调用更少更好。

对于每条解决方案路径，我们同样生成多个（≥4）预测，然后进行多数投票以得出最终的胜率。在表 4 中，为便于阅读，我们将平局比例拆分为两部分，分别加到胜和负中。在表 6 中，我们报告了原始数字作为参考。

**人工评估与 ToolEval 的比较** 为了验证 ChatGPT 评估器在通过率和胜率方面的可靠性，我们从四种不同方法（ChatGPT+ReACT, ChatGPT+DFSDT, ToolLLaMA+DFSDT 和 GPT4+DFSDT）中采样，为每种方法获得 300 个测试指令的解对。然后，我们请人工标注 ChatGPT+DFSDT、ToolLLaMA+DFSDT 和 GPT4+DFSDT 的通过率，以及 ChatGPT+ReACT 和 ChatGPT+DFSDT 之间的胜率。我们的 ChatGPT 评估器在通过率方面与人工标注者达到了 87.1% 的高度一致性，在胜率方面达到 80.3%。这一结果表明，我们的评估器生成了与人类高度相似的评估结果，可以被视为模拟人类在通过率和胜率上评估的可信评估器。

还应注意的是，工具学习的评估远比传统任务（如对话）复杂。原因在于每条指令可能存在无限条"正确"的解决方案路径。在我们的初步研究中，我们惊讶地发现即使是人类专家在决定哪个解决方案路径更好时也常常意见不一，导致一致性相对较低。例如，有人可能更喜欢只使用少数 API 来快速得出最终答案的解决方案路径；而另一些人可能更喜欢广泛尝试所有 API 以交叉验证特定信息的解决方案路径。对此，我们认为工具使用领域的公平评估仍有很长的路要走，我们相信这项工作已经为其铺平了道路。我们期待未来有更多的工作来探索这个有趣的研究问题。

### A.6 APIBench 实验细节

当将 ToolLLaMA 泛化到 APIBench 时，没有对 ToolLLaMA 进行任何训练更新，而是将提示中的每个 API 视为函数调用。我们定义一个函数来表示选择一个 API，提供调用它的代码，并用自然语言描述生成的输出。我们不考虑 APIBench 的零样本设置（即提示中不包含任何 API 描述），因为来自三个测试领域的 API 在训练期间从未遇到过。

### A.7 指令生成提示

下面我们列出了指令生成的详细提示，包括四个部分：任务描述、上下文学习示例、采样的 API 列表和其他要求。

**单工具指令的任务描述**：
你将获得一个工具、其描述、该工具所有可用的 API 函数、这些 API 函数的描述以及每个 API 函数所需的参数。你的任务是创建 10 个多样化、创新且详细的用户查询，这些查询使用一个工具的多个 API 函数。例如，如果工具"climate news"有三个 API 调用——"get all climate change news"、"look up climate today"和"historical climate"——你的查询应该表达类似这样的内容：首先，确定今天的天气，然后验证九月份俄亥俄州下雨的频率，最后查找有关气候变化的消息，帮助我理解气候是否会很快发生变化。这个查询展示了如何使用"climate news"的所有 API 调用。只使用一个 API 调用的查询将不被接受。此外，你必须包含每个 API 调用所需的输入参数。为此，为必需参数生成随机信息，如 IP 地址、位置、坐标等。例如，不要只说"一个地址"，提供具体的道路和区域名称。不要只提到"一个产品"，指定可穿戴设备、牛奶、蓝色毯子、平底锅等。不要提到"我的公司"，而是发明一个公司名称。十个查询中的前七个应该非常具体。每个单独的查询应以不同方式组合所有 API 调用的用法，并包含必要的参数。注意，你不应该问"使用哪个 API"，而是简单地陈述你的需求，这些需求可以通过这些 API 解决。你还应避免询问 API 调用所需的输入参数，而是直接在查询中提供参数。最后三个查询应该复杂且冗长，描述一个复杂的场景，其中所有 API 调用都可以在单个查询中提供帮助。你应该首先考虑可能的相关 API 组合，然后给出你的查询。相关 API 是可用于给定查询的 API；这些相关 API 必须严格来自提供的 API 名称。对于每个查询，应该有多个相关 API；对于不同的查询，相关 API 的重叠应尽可能少。按以下格式提供你的响应：[Query1: ......, 'related apis':[api1, api2, api3...], Query2: ......, 'related apis':[api4, api5, api6...], Query3: ......, 'related apis':[api1, api7, api9...], ...]

**多工具指令的任务描述**：
你将获得几个工具、工具描述、每个工具的所有可用 API 函数、这些 API 函数的描述以及每个 API 函数所需的参数。你的任务是创建 10 个多样化、创新且详细的用户查询，这些查询使用多个工具的 API 函数。例如，给定三个工具"nba news"、"cat-facts"和"hotels"："nba news"有 API 函数"Get individual NBA source news"和"Get all NBA news"；"cat-facts"有 API 函数"Get all facts about cats"和"Get a random fact about cats"；"hotels"有 API 函数"properties/get-details (Deprecated)"、"properties/list (Deprecated)"和"locations/v3/search"。你的查询应该表达类似这样的内容："我想以科比的名字命名我的新生小猫，并举办一个派对来庆祝它的出生。给我一些猫的事实和 NBA 新闻，为猫的名字收集灵感。此外，在我休斯顿市中心的家附近找一个合适的酒店来举办派对。"这个查询展示了如何使用所有给定工具的 API 调用。只使用一个工具的 API 调用的查询将不被接受。此外，你必须包含每个 API 调用所需的输入参数。为此，为必需参数生成随机信息，如 IP 地址、位置、坐标等。例如，不要只说"一个地址"，提供具体的道路和区域名称。不要只提到"一个产品"，指定可穿戴设备、牛奶、蓝色毯子、平底锅等。不要提到"我的公司"，而是发明一个公司名称。十个查询中的前七个应该非常具体。每个单独的查询应以不同方式组合不同工具的 API 调用，并包含必要的参数。注意，你不应该问"使用哪个 API"，而是简单地陈述你的需求，这些需求可以通过这些 API 解决。你还应避免询问 API 调用所需的输入参数，而是直接在查询中提供参数。最后三个查询应该复杂且冗长，描述一个复杂的场景，其中所有提供的 API 调用都可以在单个查询中提供帮助。你应该首先考虑可能的相关 API 组合，然后给出你的查询。相关 API 是可用于给定查询的 API；这些相关 API 必须严格来自提供的 API 名称。对于每个查询，应该有多个相关 API；对于不同的查询，相关 API 的重叠应尽可能少。按以下格式提供你的响应：[Query1: ......, 'related apis':[[tool name, api name], [tool name, api name], [tool name, api name]...], Query2: ......, 'related apis':[[tool name, api name], [tool name, api name], [tool name, api name]...], Query3: ......, 'related apis':[[tool name, api name], [tool name, api name], [tool name, api name]...], ...]

**上下文种子示例**。下面，我们展示一个单工具指令种子示例和一个多工具指令种子示例。

例如，对于工具 ASCII Art，给定的 API 名称是 'figlet', 'list figlet styles', 'cowsay', 'list cowsay styles', 'matheq'。
一些示例查询和相关 API 为：
"查询": "需要创建一个数学方程的 ASCII 艺术表示。方程是 'y = mx + c'，其中 m 和 c 是常数。帮助我为这个方程生成 ASCII 艺术。还要为文本 '牛顿第二运动定律' 生成 ASCII 艺术表示。"，"相关 API": ['figlet', 'list figlet styles', 'matheq']
"查询": "正在撰写关于牛的研究论文，需要包含各种牛的 ASCII 艺术表示。你能先检索可用的牛 ASCII 艺术风格吗？然后，你能为泽西牛、荷斯坦牛和格恩西牛生成 ASCII 艺术吗？最后，我希望牛在 ASCII 艺术中说 '哞！'。"，"相关 API": ['figlet', 'list figlet styles', 'cowsay', 'list cowsay styles']
"查询": "我正在写一篇关于 ASCII 艺术的博客文章，需要包含一些例子。你能为以下字符串生成 ASCII 艺术吗：'ASCII'、'art' 和 'gallery'？你可以先检索可用的 figlet 风格，然后使用这些风格为字符串生成 ASCII 艺术。"，"相关 API": ['figlet', 'list figlet styles']
"查询": "你好！我正在整理一个关于我们 furry 朋友的奇特幻灯片，需要你的帮助来添加一些 ASCII 艺术。你能好心地给我一份可用于动物的 ASCII 艺术风格目录吗？此外，我特别想展示熊猫、牛、大象和企鹅等生物的 ASCII 艺术。如果它们能在 ASCII 艺术中说出像 '你好！' 或 '拥抱！' 这样可爱的话，那就太好了！"，"相关 API": ['figlet', 'list figlet styles', 'cowsay', 'list cowsay styles']

例如，对于工具 ['Entrepreneur Mindset Collection', 'Random Words', 'thedigitalnewsfeederapi', 'Chemical Elements']，给定的 API 名称是 (工具 'Entrepreneur Mindset Collection') 的 'Random Quote in JSON format'，(工具 'Random Words') 的 'Get multiple random words' 和 'Get a random word'，(工具 'thedigitalnewsfeederapi') 的 'getting specific cricket articles'、'Getting Cricket Articles'、'getting specific news articles'、'Getting News Articles'、'getting all news articles'，(工具 'Chemical Elements') 的 'Get All Chemical Elements'。
一些示例查询和相关 API 为：
"查询": "为了我最好朋友的惊喜生日派对，我需要派对游戏和装饰的灵感。请建议一些可以作为派对主题的随机词汇。此外，我有兴趣收集关于最新派对趋势的新闻文章，以确保现代化的庆祝活动。同时，我希望了解我所在地区本地酒店的详情，以便住宿。非常感谢你的帮助。"，"相关 API": [['Random Words', 'Get multiple random words'], ['thedigitalnewsfeederapi', 'Getting News Articles'], ['thedigitalnewsfeederapi', 'Getting all news articles']]
"查询": "在为我的尊贵公司组织团队建设活动之际，我热切寻求您对激励活动的宝贵意见。能否恳请您提供一些体现团队合作和激励精神的随机名言？此外，我渴望探索展示成功团队建设活动的新闻文章，因为它们作为灵感的源泉。"
"相关 API": [['Entrepreneur Mindset Collection', 'Random Quote in JSON format'], ['thedigitalnewsfeederapi', 'Getting News Articles']]
"查询": "我需要讨论运动健康益处的特定板球文章，用于我的关于运动的研究论文。我还想知道与运动相关的化学元素，如铁（Fe）增加及其对骨髓的影响。"
"相关 API": [['thedigitalnewsfeederapi', 'getting specific cricket articles'], ['Chemical Elements', 'Get All Chemical Elements']]
"查询": "我正在启动一项新的商业项目，需要做一个宣布新时代到来的演讲。给我一些名言和词汇作为开场。我想收集关于成功企业家的新闻文章以获得灵感。"
"相关 API": [['Entrepreneur Mindset Collection', 'Random Quote in JSON format'], ['Random Words', 'Get multiple random words'], ['thedigitalnewsfeederapi', 'getting specific news articles']]

这些只是向你展示如何编写查询的示例。不要使用上述示例中列出的 API，而是使用下面 INPUT 中列出的 API。

**采样的 API 列表（示例）**
```json
{
  "tool_description": "EntreAPI Faker is used to dynamically create mock, demo, test and sample data for your application",
  "name": "EntreAPI Faker",
  "api_list": [
    {
      "name": "Longitute",
      "url": "https://entreapi-faker.p.rapidapi.com/address/longitude",
      "description": "Generate a random longitude.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "max", "type": "NUMBER", "description": "Maximum value for latitude.", "default": ""},
        {"name": "min", "type": "NUMBER", "description": "Minimum value for latitude.", "default": ""},
        {"name": "precision", "type": "NUMBER", "description": "Precision for latitude.", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Boolean",
      "url": "https://entreapi-faker.p.rapidapi.com/datatype/boolean",
      "description": "Randomly generate a boolean value.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Past",
      "url": "https://entreapi-faker.p.rapidapi.com/date/past",
      "description": "Randomly generate a date value in the past.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "refDate", "type": "STRING", "description": "Starting reference date", "default": ""},
        {"name": "years", "type": "NUMBER", "description": "Number of years for the range of dates.", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Image Url",
      "url": "https://entreapi-faker.p.rapidapi.com/image/imageUrl",
      "description": "Randomly generate an image URL.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "width", "type": "NUMBER", "description": "Width of the image. Default is 640.", "default": ""},
        {"name": "height", "type": "NUMBER", "description": "Height of the image. Default is 480.", "default": ""},
        {"name": "useRandomize", "type": "BOOLEAN", "description": "Add a random number parameter to the returned URL.", "default": ""},
        {"name": "category", "type": "STRING", "description": "The category for the image. Can be one: abstract, animal, avatar, business, cats, city, fashion, food, nature, nightlife, people, sports, technics, transport", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Sentence",
      "url": "https://entreapi-faker.p.rapidapi.com/lorem/sentence",
      "description": "Randomly generate a sentence of Lorem Ipsum.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "wordCount", "type": "NUMBER", "description": "Number of words in the sentence.", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Gender",
      "url": "https://entreapi-faker.p.rapidapi.com/name/gender",
      "description": "Randomly select a gender.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "useBinary", "type": "BOOLEAN", "description": "Use binary genders only.", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Prefix",
      "url": "https://entreapi-faker.p.rapidapi.com/name/prefix",
      "description": "Randomly generate a prefix (e.g., Mr., Mrs., etc.)",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "gender", "type": "STRING", "description": "Optional gender.", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Array Element",
      "url": "https://entreapi-faker.p.rapidapi.com/random/arrayElement",
      "description": "Randomly select an array element.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "array", "type": "ARRAY", "description": "The list of elements to choose from. Default is [\"a\", \"b\", \"c\"].", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "Number Value",
      "url": "https://entreapi-faker.p.rapidapi.com/random/number",
      "description": "Randomly generate a number value.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [
        {"name": "min", "type": "NUMBER", "description": "Minimum value.", "default": ""},
        {"name": "max", "type": "NUMBER", "description": "Maximum value.", "default": ""},
        {"name": "precision", "type": "NUMBER", "description": "Precision of the number.", "default": ""}
      ],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    },
    {
      "name": "URL",
      "url": "https://entreapi-faker.p.rapidapi.com/internet/url",
      "description": "Randomly generate a URL.",
      "method": "GET",
      "required_parameters": [],
      "optional_parameters": [],
      "tool_name": "EntreAPI Faker",
      "category_name": "Data"
    }
  ]
}
```

**其他要求**：
请根据给定的要求和输入生成十个查询。这十个查询应展示多样化的句子结构：一些查询应为祈使句，一些为陈述句，另一些为疑问句。同样，它们应包含多种语气，有些有礼貌，有些直接。确保它们在长度上有所变化，并包含广泛的主题：我自己、我的朋友、家人和公司。尝试包含一些引人入胜的查询，只要它们与 API 调用相关。请记住，对于每个查询，仅调用一个 API 是不够的；每个查询应调用两到五个 API。但是，尽量避免在查询中明确指定要使用哪个 API。每个查询至少包含三十个单词。

### A.8 解决方案路径标注提示

在搜索解决方案路径时，我们使用以下提示。在扩展子节点时，我们使用多样性用户提示，显示先前子节点的信息。

```
system_prompt:
你是 Tool-GPT，能够利用众多工具和函数来完成给定的任务。
1. 首先，我将为你提供任务描述，然后你的任务开始。
2. 在每一步，你需要分析当前状态并通过执行函数调用来确定下一步行动。
3. 调用之后，你将收到结果，从而进入新状态。随后，你将分析当前状态，决定下一步，并重复这个过程。
4. 经过多次思考和函数调用后，你最终将完成任务并提供你的最终答案。
记住：
1. 状态变化是不可逆的，你无法返回到之前的状态。
2. 保持你的思路简洁，限制在最多五句话。
3. 你可以进行多次尝试。如果你计划连续尝试不同的条件，每次尝试执行一个条件。
4. 如果你认为已经收集了足够的信息，调用函数 "Finish: give_answer" 来为任务提供答案。
5. 如果你觉得从这一步起无法处理该任务，调用函数 "Finish: give_up_and_restart"。
让我们开始吧！
任务描述：{task_description}

diversity_user_prompt:
这不是你第一次尝试这个任务，所有之前的尝试都失败了。
在你为这个状态生成思考之前，我将先向你展示你在这个状态的先前动作，然后你必须生成与所有这些动作不同的动作。以下是先前的一些动作候选：
{previous_candidate}
记住，你现在处于一个尝试的中间状态，你将首先分析当前状态和先前的动作候选，然后做出与所有先前动作不同的动作。

Finish_function_description:
{
  "name": "Finish",
  "description": "如果你认为你已经获得了可以回答任务的结果，请调用此函数以提供最终答案。或者，如果你认识到在当前状态下无法继续执行任务，请调用此函数以重新开始。记住：你必须在每次尝试结束时调用此函数，并且唯一会展示给用户的部分是最终答案，因此它应包含足够的信息。",
  "parameters": {
    "type": "object",
    "properties": {
      "return_type": {
        "type": "string",
        "enum": ["give_answer", "give_up_and_restart"]
      },
      "final_answer": {
        "type": "string",
        "description": "你想要给用户的最终答案。如果 \"return_type\"==\"give_answer\"，你应包含此字段。"
      }
    },
    "required": ["return_type"]
  }
}
```
