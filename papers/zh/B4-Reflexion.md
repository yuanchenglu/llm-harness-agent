# Reflexion: 具有语言反馈强化学习的语言智能体

**作者：** Noah Shinn（东北大学）, Federico Cassano（东北大学）, Edward Berman（东北大学）, Ashwin Gopinath（麻省理工学院）, Karthik Narasimhan（普林斯顿大学）, Shunyu Yao（普林斯顿大学）

## 摘要

大型语言模型（LLMs）越来越多地被用于与外部环境（例如游戏、编译器、API）交互，作为目标驱动的智能体。然而，这些语言智能体如何快速高效地从试错中学习仍然是一个挑战，因为传统的强化学习方法需要大量的训练样本和昂贵的模型微调。我们提出**Reflexion**，一种新颖的框架，它不通过更新权重来强化语言智能体，而是通过语言反馈。具体来说，Reflexion智能体对任务反馈信号进行**语言反思**，然后将自身的反思文本维护在**情景记忆**缓冲区中，以在后续尝试中诱导更好的决策。Reflexion足够灵活，可以整合各种类型（标量值或自由形式的语言）和来源（外部或内部模拟）的反馈信号，并在多样化的任务（顺序决策、编程、语言推理）上相对于基线智能体获得了显著的改进。例如，Reflexion在HumanEval编程基准上达到了91%的pass@1准确率，超过了之前达到80%的GPT-4的最新成果。我们还使用不同的反馈信号、反馈整合方法和智能体类型进行了消融实验和分析研究，并提供了它们如何影响性能的洞察。我们已在 https://github.com/noahshinn024/reflexion 公开了所有代码、演示和数据集。

## 1 引言

最近的研究成果如ReAct[30]、SayCan[1]、Toolformer[22]、HuggingGPT[23]、生成式智能体[19]和WebGPT[17]已经证明了基于大语言模型（LLM）核心构建的自主决策智能体的可行性。这些方法使用LLM来生成文本和可在API调用中使用并在环境中执行的"动作"。由于它们依赖于具有海量参数的大型模型，这些方法迄今为止仅限于使用上下文示例作为教导智能体的方式，因为更传统的优化方案（如基于梯度下降的强化学习）需要大量的计算和时间。

在本文中，我们提出一种称为**Reflexion**的替代方法，它使用**语言反馈**来帮助智能体从先前的失败中学习。Reflexion将来自环境的二元或标量反馈转换为文本摘要形式的语言反馈，然后将其作为额外的上下文添加到下一个回合的LLM智能体中。这种自我反思反馈充当了一种"语义"梯度信号，为智能体提供具体的改进方向，帮助它从先前的错误中学习以更好地完成任务。这类似于人类如何以少量示例的方式迭代学习完成复杂任务——通过反思先前的失败，为下一次尝试形成改进的进攻计划。例如，在图1中，一个Reflexion智能体通过尝试、错误和自我反思来学习优化自身行为，以解决决策、编程和推理任务。

生成有用的反思反馈是具有挑战性的，因为它需要模型很好地理解在何处犯了错误（即信用分配问题[25]），以及生成包含可操作改进见解的摘要的能力。我们探索了三种实现方式——简单的二元环境反馈、针对常见失败情况的预定义启发式方法，以及自我评估，例如使用LLM进行二元分类（决策任务）或自写单元测试（编程任务）。在所有的实现中，评估信号被放大为自然语言的经验摘要，这些摘要可以存储在长期记忆中。

与更传统的基于策略或价值的RL方法相比，Reflexion具有几个优势：1）它是轻量级的，不需要微调LLM；2）它允许更细粒度的反馈形式（例如动作的针对性更改），相比于难以进行精确信用分配的标量或向量奖励；3）它允许对先前经验进行更明确和可解释的情景记忆形式；4）它为未来回合中的动作提供了更明确的提示。与此同时，它也存在依赖LLM自我评估能力（或启发式方法）的局限性，并且没有成功的正式保证。然而，随着LLM能力的提升，我们预计这一范式只会随着时间的推移变得更好。

我们在以下任务上进行了实验：（1）决策任务，测试长轨迹上的顺序动作选择；（2）推理任务，测试知识密集型、单步生成的改进；（3）编程任务，教导智能体有效使用编译器、解释器等外部工具。在所有三类任务中，我们观察到Reflexion智能体是更好的决策者、推理者和编程者。更具体地说，Reflexion智能体在AlfWorld[24]决策任务上，通过在12次迭代学习步骤中比强基线方法提高了22%的绝对性能，在HotPotQA[28]的推理问题上提高了20%，在HumanEval[6]的Python编程任务上提高了高达11%。

总结来说，我们的贡献如下：

- 我们提出了Reflexion，一种新的"语言"强化范式，将策略参数化为智能体的记忆编码与选择的LLM参数配对。
- 我们探索了LLM中这种自我反思的新兴特性，并通过实验证明自我反思在少量尝试中学习复杂任务极为有用。
- 我们引入了LeetcodeHardGym，一个包含40个具有挑战性的Leetcode问题（"困难级别"）和19种编程语言的代码生成RL竞技环境。
- 我们展示了Reflexion在多个任务上相对于强基线的改进，并在多个代码生成基准上取得了最先进的结果。

## 2 相关工作

**推理与决策** Self-Refine[15]采用了一种迭代的自我精炼框架，通过自我评估自主改进生成内容。这些自我评估和自我改进步骤以给定的任务约束为条件，例如"如何让这段生成内容以更积极的方式撰写"。Self-Refine是有效的，但仅限于单次生成的推理任务。Pryzant等人[21]进行了类似的语义提示词优化，但也仅限于单次生成任务。Paul等人[20]微调评论家模型以在轨迹内提供中间反馈，从而改进推理回答。Xie等人[27]使用随机束搜索在动作上进行更高效的决策搜索策略，由于其自我评估组件，使智能体能够利用前瞻优势。Yoran等人[31]和Nair等人[16]使用决策模型在多个生成结果上进行推理。Kim等人[10]在没有评估步骤的情况下，在固定步数内使用重试模式。Goodman[9]执行一个定性评估步骤，对先前的生成结果提出优化建议。在本文中，我们展示了这些概念中的几个可以通过自我反思得以增强，从而构建持久性的自我反思经验记忆，使智能体能够识别自身错误并自我建议从错误中吸取的教训。

**编程** 过去和近期的一些工作采用了测试驱动开发或代码调试实践的变体。AlphaCode[14]在隐藏测试用例上评估一组生成结果。CodeT[5]使用自生成的单元测试来对生成的函数实现进行评分。Self-Debugging[7]采用了一个调试组件，根据代码执行环境的反馈来改进现有的实现。CodeRL[12]将问题置于RL框架中，使用演员-评论家设置，根据执行环境的反馈来调试程序。AlphaCode、Self-Debugging和CodeRL在修复较不复杂的程序错误方面是有效的，但它们依赖于会使得pass@1资格失效的真实测试用例，并且不使用自我反思来弥合错误识别与实现改进之间的差距。CodeT不访问隐藏测试用例，但并没有实现自我学习步骤来改进代码编写。

## 3 Reflexion：通过语言反思实现强化

我们开发了Reflexion的模块化表述，利用三个不同的模型：**Actor**（记为Ma），生成文本和动作；**Evaluator**（评估器，记为Me），对Ma产生的输出进行评分；以及**Self-Reflection**（自我反思模型，记为Msr），生成语言强化提示以帮助Actor进行自我改进。我们提供了每个模型的详细描述，随后阐明它们在Reflexion框架内的协作机制。

**Actor** Actor建立在大语言模型（LLM）之上，经过特定的提示设计，根据状态观测生成必要的文本和动作。类似于传统的基于策略的RL设置，我们在时间t从当前策略πθ中采样一个动作或生成结果at，并从环境中接收一个观测ot。我们探索了多种Actor模型，包括Chain of Thought[26]和ReAct[30]。这些多样化的生成模型使我们能够在Reflexion框架内探索文本和动作生成的不同方面，为它们的性能和有效性提供有价值的洞察。此外，我们还添加了一个记忆组件mem，为该智能体提供额外的上下文。这一改编受到Brooks等人[3]的启发，他们提出了一种使用上下文学习的策略迭代方法。关于如何填充该记忆的细节如下所述。

**Evaluator** Reflexion框架中的Evaluator组件在评估Actor产生的输出质量方面起着关键作用。它以生成的轨迹为输入，计算一个反映其在给定任务上下文中表现效果的奖励分数。定义适用于语义空间的有效价值和奖励函数是困难的，因此我们研究了Evaluator模型的几种变体。对于推理任务，我们探索了基于精确匹配（EM）评分的奖励函数，确保生成的输出与预期解决方案紧密对齐。在决策任务中，我们采用针对特定评估标准量身定制的预定义启发式函数。此外，我们还尝试使用LLM自身的不同实例化作为Evaluator，为决策和编程任务生成奖励。这种多方面的Evaluator设计方法使我们能够考察不同的生成输出评分策略，提供关于它们在各种任务中有效性和适用性的洞察。

**Self-Reflection** 自我反思模型（实例化为LLM）在Reflexion框架中起着关键作用，通过生成语言自我反思来为未来的试验提供宝贵的反馈。给定稀疏的奖励信号（如二元成功状态：成功/失败）、当前轨迹及其持久记忆mem，自我反思模型会生成细致且具体的反馈。这种反馈比标量奖励信息量更丰富，随后存储在智能体的记忆（mem）中。例如，在一个多步决策任务中，当智能体收到失败信号时，它可以推断出特定的动作ai导致了后续的错误动作ai+1和ai+2。然后智能体可以用语言陈述它本应采取不同的动作a'i，这将导致a'i+1和a'i+2，并将这一经验存储在其记忆中。在后续的试验中，智能体可以利用其过去的经验，在时间t通过选择动作a'i来调整其决策方法。这种尝试、错误、自我反思和持久记忆的迭代过程使智能体能够通过利用信息丰富的反馈信号在各种环境中快速提高其决策能力。

**记忆** Reflexion过程的核心组件是短期记忆和长期记忆的概念。在推理时，Actor基于短期和长期记忆来调节其决策，类似于人类既记住细粒度的近期细节，又从长期记忆中回忆起重要的精炼经验。在RL设置中，轨迹历史作为短期记忆，而自我反思模型的输出则存储在长期记忆中。这两个记忆组件协同工作，提供既具体又受到多次试验经验教训影响的上下文，这是Reflexion智能体相对于其他LLM动作选择工作的一个关键优势。

**Reflexion过程** Reflexion被形式化为算法1中的一个迭代优化过程。在第一次试验中，Actor通过与环境交互生成轨迹τ0。然后Evaluator产生一个分数r0，计算为rt = Me(τ0)。rt只是第t次试验的标量奖励，随着任务特定性能的提高而改善。在第一次试验后，为了将r0放大为LLM可用于改进的反馈形式，自我反思模型分析{τ0, r0}集合以生成摘要sr0，存储在记忆mem中。srt是第t次试验的语言经验反馈。Actor、Evaluator和自我反思模型在一个循环中通过多次试验协同工作，直到Evaluator认为τt正确为止。如第3节所述，Reflexion的记忆组件对其有效性至关重要。每次试验t后，srt被追加到mem中。在实践中，我们将mem限制为最大存储经验数量Ω（通常设置为1-3），以适应最大上下文LLM的限制。

## 4 实验

我们在决策、推理和代码生成任务上评估了各种自然语言RL设置。具体来说，我们让智能体在HotPotQA[28]上执行基于搜索的问答，在AlfWorld[24]的常见家庭环境中执行多步任务，以及在HumanEval[6]、MBPP[2]和我们新提出的基准LeetcodeHard中使用解释器和编译器在类似竞赛的环境中进行代码编写任务。最值得注意的是，Reflexion在AlfWorld上比强基线提高了22%，在HotPotQA上提高了20%，在HumanEval上提高了11%。

### 4.1 顺序决策：ALFWorld

AlfWorld是一套基于文本的环境套件，挑战智能体在基于TextWorld[8]的各种交互式环境中解决多步任务。遵循Yao等人[30]的方法，我们在134个AlfWorld环境中运行智能体，涵盖六种不同的任务，包括寻找隐藏物体（例如在抽屉里找铲子）、移动物体（例如将刀移到砧板上）以及用其他物体操作物体（例如在冰箱里冷藏番茄）。我们使用ReAct[30]作为动作生成器，因为Yao等人[30]已证明其在使用显式中间思想的长时间轨迹决策中取得了成功。AlfWorld任务自然需要一个自我评估步骤，因为环境只能发出任务是否完成的信号。为了实现完全自主的行为，我们实现了两种自我评估技术：使用LLM的自然语言分类和手写启发式方法。启发式方法很简单：如果智能体执行相同的动作并收到相同的响应超过3个循环，或者当前环境中采取的动作数量超过30（低效规划），我们就进行自我反思。在基线运行中，如果建议自我反思，我们跳过自我反思过程，重置环境，并开始新的试验。在Reflexion运行中，智能体使用自我反思来发现错误，更新其记忆，重置环境，并开始新的试验。为避免可能超过最大限制的过长提示窗口，我们将智能体的记忆截断为最近3次自我反思（经验）。

为避免语法错误，我们向智能体提供了两个领域特定的少样本轨迹。我们使用与Yao等人[30]相同的少样本轨迹示例，采用GPT-3作为LLM。AlfWorld任务、ReAct少样本提示和Reflexion示例包含在附录中。

**结果** ReAct + Reflexion显著优于ReAct，使用简单的启发式方法来检测幻觉和低效规划，完成了134个任务中的130个。此外，ReAct + Reflexion通过学习在12个连续试验中解决了额外的任务。在纯ReAct方法中，我们看到性能增长在试验6和7之间停滞。

**分析** 基线失败的AlfWorld轨迹中一个常见错误是智能体认为它已拥有某个物品但实际上并未拥有。智能体随后在长轨迹中执行多个动作，且无法回溯其动作以发现错误。Reflexion几乎消除了所有这些情况，通过使用自我反思将长的失败轨迹精炼为相关的经验，这些经验在未来被用作"自我提示"。在AlfWorld中，长期记忆帮助智能体的主要有两种情况：1）长轨迹中的早期错误可以很容易地被识别。智能体可以建议一个新的动作选择，甚至是一个新的长期计划。2）需要检查的表面/容器太多。智能体可以在多次试验中利用其经验记忆来彻底搜索一个房间。如图3所示，学习曲线表明学习过程跨越多次经验发生，这意味着智能体成功地在情况1和情况2之间取得了平衡——在最初两次试验之间立即出现性能提升，然后在接下来的11次试验中稳步提升到近乎完美的性能。另一方面，图3显示纯ReAct智能体在22%的幻觉率上收敛，没有长期恢复的迹象。

### 4.2 推理：HotpotQA

HotPotQA[28]是一个基于维基百科的数据集，包含113k个问答对，挑战智能体解析内容并在多个支持文档上进行推理。为了测试纯推理能力的改进，我们实现了Reflexion + Chain-of-Thought（CoT）[26]用于逐步的Q→A和Q，Cgt→A的实现，其中Q是问题，Cgt是数据集中提供的真实上下文，A是最终答案。由于CoT不是一种多步决策技术，我们向智能体提供Cgt，以便我们可以在提供的文本的大段内容上分离出推理行为。为了测试需要推理和动作选择的整体问答能力，我们实现了一个Reflexion + ReAct[30]智能体，它可以使用维基百科API检索相关上下文，并通过逐步显式思考推断答案。对于CoT实现，我们使用6次提示；对于ReAct，使用2次提示；对于自我反思，使用2次提示。所有示例均可在附录中找到。

稳健地评估自然语言答案是一个长期存在的NLP问题。因此，在试验之间，我们使用精确匹配答案评分，利用环境向智能体提供二元成功信号。每次试验后，启用自我反思循环以放大二元信号，类似于AlfWorld中4.1节的决策设置，记忆大小为3次经验。

**结果** Reflexion在多个学习步骤中显著优于所有基线方法。此外，纯ReAct、纯CoT和纯CoT(GT)实现均未能在任何任务上实现概率性改进，这意味着来自任何基线方法的第一次试验中的失败任务都无法在后续试验中使用温度0.7解决。在Reflexion运行中，我们允许智能体收集经验并在失败任务上重试，直到在特定任务上连续3次失败。自然地，CoT(GT)取得了更高的准确率分数，因为它可以访问问题的真实上下文。尽管如此，CoT(GT)智能体仍无法正确推断39%问题的正确答案，但Reflexion帮助智能体在无法访问真实答案的情况下纠正其错误，将其准确率提高了14%。

**分析** 我们进行了一项消融实验，以分离使用CoT(GT)作为基线方法进行推理时自我反思步骤的优势（图4）。回顾一下，CoT(GT)使用Chain-of-Thought推理并提供真实上下文，这测试了在长上下文上的推理能力。接下来，我们通过包含最近的轨迹来添加情景记忆（EPM）元素。对于Reflexion智能体，我们将标准的自我反思步骤作为最后的步骤实施。直观上，我们测试智能体是否通过使用以第一人称撰写的语言解释来更有效地迭代学习。图4表明，自我反思相比情景记忆学习优势带来了8%的绝对提升。这一结果支持了仅精炼方法不如自我反思引导的精炼方法有效的论点。

### 4.3 编程

我们在MBPP[2]、HumanEval[6]以及我们的新数据集LeetcodeHardGym上评估了基线和Reflexion方法在Python和Rust代码编写方面的能力。MBPP和HumanEval衡量给定自然语言描述的函数体生成准确率。我们使用基准语言编译器MultiPL-E[4]将HumanEval和MBPP的子集翻译为Rust语言。MultiPL-E是一个小型编译器集合，可用于将Python基准问题翻译为其他18种语言。我们包含了Rust代码生成的实验，以证明Reflexion的代码生成实现是语言无关的，可用于解释型和编译型语言。最后，我们引入了一个新的基准LeetcodeHardGym，这是一个交互式编程竞技场，包含40个Leetcode困难级别的问题，这些问题均在GPT-4[18]的预训练截止日期（2022年10月8日）之后发布。

编程任务提供了一个独特的机会来使用更基于实际的自我评估实践，例如自生成的单元测试套件。因此，我们的基于Reflexion的编程任务实现适用于pass@1准确率的报告。为了生成测试套件，我们使用Chain-of-Thought提示[26]来生成多样且全面的测试，并附有相应的自然语言描述。然后，我们通过尝试为每个提议的测试构建有效的抽象语法树（AST）来筛选语法有效的测试语句。最后，我们从生成的单元测试集合中采样n个测试，以生成测试套件T，记为{t0, t1, ..., tn}。我们将n设置为最多6个单元测试。除了单元测试套件组件外，Reflexion编程智能体的学习循环设置与推理和决策智能体相同，最大记忆限制为1次经验。

**表1：** 各种模型-策略-语言组合的Pass@1准确率。基础策略是单次代码生成样本。所有基于指令的模型都遵循零样本代码生成。

| 基准 + 语言 | 先前SOTA Pass@1 | SOTA Pass@1 | Reflexion Pass@1 |
|---|---|---|---|
| HumanEval (PY) | 65.8 (CodeT [5] + GPT-3.5) | 80.1 (GPT-4) | **91.0** |
| HumanEval (RS) | – | 60.0 (GPT-4) | **68.0** |
| MBPP (PY) | 67.7 (CodeT [5] + Codex [6]) | **80.1 (GPT-4)** | 77.1 |
| MBPP (RS) | – | 70.9 (GPT-4) | **75.4** |
| Leetcode Hard (PY) | – | 7.5 (GPT-4) | **15.0** |

**表2：** HumanEval和MBPP的总体准确率和测试生成性能。对于Rust，HumanEval是从HumanEval Python中翻译到Rust的最难的50个问题（使用MultiPL-E [4]）。TP：单元测试通过，解决方案通过；FN：单元测试失败，解决方案通过；FP：单元测试通过，解决方案失败；TN：单元测试失败，解决方案失败。

| 基准 + 语言 | 基础 | Reflexion | TP | FN | FP | TN |
|---|---|---|---|---|---|---|
| HumanEval (PY) | 0.80 | **0.91** | 0.99 | 0.40 | 0.01 | 0.60 |
| MBPP (PY) | **0.80** | 0.77 | 0.84 | 0.59 | 0.16 | 0.41 |
| HumanEval (RS) | 0.60 | **0.68** | 0.87 | 0.37 | 0.13 | 0.63 |
| MBPP (RS) | 0.71 | **0.75** | 0.84 | 0.51 | 0.16 | 0.49 |

**结果** Reflexion在所有基准测试中均优于所有基线准确率，并为Python和Rust的所有基准（MBPP Python除外）设立了新的最先进标准。我们进一步研究了Reflexion在MBPP Python上的较差性能。

**分析** 我们承认，自我反思型代码生成智能体受限于其编写多样且全面的测试的能力。因此，在模型生成不稳定的测试套件的情况下，所有测试可能在错误解决方案上通过，导致对代码补全产生假阳性标签[11]。另一方面，如果模型生成了编写错误的测试套件，部分测试可能在正确解决方案上失败，导致自我反思生成基于假阴性的代码补全。鉴于Reflexion的实现，假阴性优于假阳性，因为智能体可能能够使用自我反思来识别错误的测试并提示自己保持原始代码补全不变。另一方面，如果无效的测试套件返回假阳性补全（所有内部测试用例都通过但实现不正确），智能体将过早地报告无效提交。在表2中，我们测量了各种条件以分析超越pass@1准确率的性能。之前，我们展示了Reflexion在MBPP Python上相对于基线GPT-4的较差性能。在表2中，我们观察到内部测试执行产生的假阳性标签存在显著差异，即P(非pass@1生成正确 | 测试通过)。也就是说，给定提交通过了所有单元测试，它将会失败的概率。对于HumanEval和MBPP Python，基线pass@1准确率相对相似，分别为82%和80%。然而，MBPP Python的假阳性测试执行率为16.3%，而HumanEval Python的假阳性率仅为1.4%，导致了表1中所示的91%的总体准确率。

**表3：** 使用GPT-4作为基础模型在HumanEval Rust（50个最难问题）上对Reflexion方法的各类折衷方法的Pass@1准确率

| 方法 | 测试生成 | 自我反思 | Pass@1 (准确率) |
|---|---|---|---|
| 基础模型 | 否 | 否 | 0.60 |
| 省略测试生成 | 否 | 是 | 0.52 |
| 省略自我反思 | 是 | 否 | 0.60 |
| Reflexion | 是 | 是 | **0.68** |

**消融研究** 我们在HumanEval Rust 50个最难问题的子集上测试了Reflexion中测试生成和自我反思协作的组合方法。我们的Rust编译器环境提供了详细的错误日志和有用的调试提示，因此是测试折衷方法的良好试验场。首先，我们省略了内部测试生成和执行步骤，这会测试智能体在没有当前实现指导的情况下进行自我反思。表3显示准确率从60%（基线）下降到52%，这表明智能体无法在没有单元测试的情况下判断当前实现是否正确。因此，智能体必须在运行的所有迭代中参与，而没有提前退出的选项，从而对实现进行了有害的编辑。

接下来，我们通过省略失败单元测试套件评估之后的自然语言解释步骤来测试自我反思的贡献。直观上，这挑战了智能体将所有失败单元测试的错误识别和实现改进任务结合起来。有趣的是，折衷后的智能体并未比基线运行提高性能。我们观察到测试生成和代码编译步骤能够捕获语法和逻辑错误，但实现修复并未反映这些指示。这些实证结果表明，最近几个提出盲目的试错调试技术而没有自我反思的工作，在更困难的任务（如用Rust编写复杂程序）上是无效的。

## 5 局限性

Reflexion的核心是一种使用自然语言进行策略优化的优化技术。策略优化是通过经验改进动作选择的一种强大方法，但它仍然可能陷入非最优的局部最小值解决方案。在本研究中，我们将长期记忆限制为具有最大容量的滑动窗口，但我们鼓励未来的工作使用更高级的结构（例如向量嵌入数据库或传统SQL数据库）来扩展Reflexion的记忆组件。具体到代码生成，测试驱动开发在指定准确的输入-输出映射方面存在许多实际限制，例如非确定性生成器函数、与API交互的不纯函数、根据硬件规格变化输出的函数，或调用可能难以预测的并行或并发行为的函数。

## 6 更广泛的影响

大型语言模型越来越多地被用于与外部环境（例如互联网、软件、机器人等）和人类进行交互。我们的工作有潜力增强这些智能体以实现更高的自动化和工作效率，但同时也放大了这些智能体被误用时的风险。我们认为这一研究方向需要在安全和伦理考虑方面投入更多努力。

另一方面，强化学习一直受困于其黑盒策略和优化设置，使得可解释性和对齐性具有挑战性。我们提出的"语言"强化学习可能解决其中一些问题，使自主智能体更加可解释和可诊断。例如，在工具使用对人类来说可能过于难以理解的情况下，可以在使用工具之前监控自我反思以确保正确的意图。

## 7 结论

在这项工作中，我们提出了Reflexion，一种利用语言反馈来教导智能体从过去的错误中学习的方法。我们通过实验证明，Reflexion智能体通过利用自我反思，显著优于当前广泛使用的决策方法。在未来的工作中，Reflexion可用于采用在传统RL设置中已被深入研究的更先进技术，例如自然语言中的价值学习或离策略探索技术。

## 8 可复现性

我们强烈建议其他人在运行自主代码编写实验时使用隔离的执行环境，因为生成的代码在执行前未经验证。

## 参考文献

[1] Ahn, M., Brohan, A., Brown, N., Chebotar, Y., Cortes, O., David, B., Finn, C., Gopalakrishnan, K., Hausman, K., Herzog, A., et al. (2022). Do as i can, not as i say: Grounding language in robotic affordances. arXiv preprint arXiv:2204.01691.

[2] Austin, J., Odena, A., Nye, M., Bosma, M., Michalewski, H., Dohan, D., Jiang, E., Cai, C., Terry, M., Le, Q., et al. (2021). Program synthesis with large language models. arXiv preprint arXiv:2108.07732.

[3] Brooks, E., Walls, L., Lewis, R. L., and Singh, S. (2022). In-context policy iteration. arXiv preprint arXiv:2210.03821.

[4] Cassano, F., Gouwar, J., Nguyen, D., Nguyen, S., Phipps-Costin, L., Pinckney, D., Yee, M.-H., Zi, Y., Anderson, C. J., Feldman, M. Q., Guha, A., Greenberg, M., and Jangda, A. (2022). Multipl-e: A scalable and extensible approach to benchmarking neural code generation.

[5] Chen, B., Zhang, F., Nguyen, A., Zan, D., Lin, Z., Lou, J.-G., and Chen, W. (2022). Codet: Code generation with generated tests. arXiv preprint arXiv:2207.10397.

[6] Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. d. O., Kaplan, J., Edwards, H., Burda, Y., Joseph, N., Brockman, G., et al. (2021). Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374.

[7] Chen, X., Lin, M., Schärli, N., and Zhou, D. (2023). Teaching large language models to self-debug. arXiv preprint arXiv:2304.05128.

[8] Côté, M.-A., Kádár, A., Yuan, X., Kybartas, B., Barnes, T., Fine, E., Moore, J., Hausknecht, M., El Asri, L., Adada, M., et al. (2019). Textworld: A learning environment for text-based games. In Computer Games: 7th Workshop, CGW 2018, Held in Conjunction with the 27th International Conference on Artificial Intelligence, IJCAI 2018, Stockholm, Sweden, July 13, 2018, Revised Selected Papers 7, pages 41–75. Springer.

[9] Goodman, N. (2023). Meta-prompt: A simple self-improving language agent. noahgoodman.substack.com.

[10] Kim, G., Baldi, P., and McAleer, S. (2023). Language models can solve computer tasks. arXiv preprint arXiv:2303.17491.

[11] Lam, W., Winter, S., Wei, A., Xie, T., Marinov, D., and Bell, J. (2020). A large-scale longitudinal study of flaky tests. Proc. ACM Program. Lang., 4(OOPSLA).

[12] Le, H., Wang, Y., Gotmare, A. D., Savarese, S., and Hoi, S. C. H. (2022). Coderl: Mastering code generation through pretrained models and deep reinforcement learning. Advances in Neural Information Processing Systems, 35:21314–21328.

[13] Li, R., Allal, L. B., Zi, Y., Muennighoff, N., Kocetkov, D., Mou, C., Marone, M., Akiki, C., Li, J., Chim, J., et al. (2023). Starcoder: may the source be with you! arXiv preprint arXiv:2305.06161.

[14] Li, Y., Choi, D., Chung, J., Kushman, N., Schrittwieser, J., Leblond, R., Eccles, T., Keeling, J., Gimeno, F., Dal Lago, A., et al. (2022). Competition-level code generation with alphacode. Science, 378(6624):1092–1097.

[15] Madaan, A., Tandon, N., Gupta, P., Hallinan, S., Gao, L., Wiegreffe, S., Alon, U., Dziri, N., Prabhumoye, S., Yang, Y., et al. (2023). Self-refine: Iterative refinement with self-feedback. arXiv preprint arXiv:2303.17651.

[16] Nair, V., Schumacher, E., Tso, G., and Kannan, A. (2023). Dera: Enhancing large language model completions with dialog-enabled resolving agents. arXiv preprint arXiv:2303.17071.

[17] Nakano, R., Hilton, J., Balaji, S., Wu, J., Ouyang, L., Kim, C., Hesse, C., Jain, S., Kosaraju, V., Saunders, W., et al. (2021). Webgpt: Browser-assisted question-answering with human feedback. arXiv preprint arXiv:2112.09332.

[18] OpenAI (2023). Gpt-4 technical report. ArXiv.

[19] Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., and Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. arXiv preprint arXiv:2304.03442.

[20] Paul, D., Ismayilzada, M., Peyrard, M., Borges, B., Bosselut, A., West, R., and Faltings, B. (2023). Refiner: Reasoning feedback on intermediate representations. arXiv preprint arXiv:2304.01904.

[21] Pryzant, R., Iter, D., Li, J., Lee, Y. T., Zhu, C., and Zeng, M. (2023). Automatic prompt optimization with" gradient descent" and beam search. arXiv preprint arXiv:2305.03495.

[22] Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Zettlemoyer, L., Cancedda, N., and Scialom, T. (2023). Toolformer: Language models can teach themselves to use tools. arXiv preprint arXiv:2302.04761.

[23] Shen, Y., Song, K., Tan, X., Li, D., Lu, W., and Zhuang, Y. (2023). Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface. arXiv preprint arXiv:2303.17580.

[24] Shridhar, M., Yuan, X., Côté, M.-A., Bisk, Y., Trischler, A., and Hausknecht, M. (2021). ALFWorld: Aligning Text and Embodied Environments for Interactive Learning. In Proceedings of the International Conference on Learning Representations (ICLR).

[25] Sutton, R. S. and Barto, A. G. (2018). Reinforcement Learning: An Introduction. The MIT Press, second edition.

[26] Wei, J., Wang, X., Schuurmans, D., Bosma, M., Chi, E., Le, Q., and Zhou, D. (2022). Chain of thought prompting elicits reasoning in large language models. arXiv preprint arXiv:2201.11903.

[27] Xie, Y., Kawaguchi, K., Zhao, Y., Zhao, X., Kan, M.-Y., He, J., and Xie, Q. (2023). Decomposition enhances reasoning via self-evaluation guided decoding. arXiv preprint arXiv:2305.00633.

[28] Yang, Z., Qi, P., Zhang, S., Bengio, Y., Cohen, W. W., Salakhutdinov, R., and Manning, C. D. (2018). HotpotQA: A dataset for diverse, explainable multi-hop question answering. In Conference on Empirical Methods in Natural Language Processing (EMNLP).

[29] Yao, S., Chen, H., Yang, J., and Narasimhan, K. (preprint). Webshop: Towards scalable real-world web interaction with grounded language agents. In ArXiv.

[30] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K., and Cao, Y. (2023). ReAct: Synergizing reasoning and acting in language models. In International Conference on Learning Representations (ICLR).

[31] Yoran, O., Wolfson, T., Bogin, B., Katz, U., Deutch, D., and Berant, J. (2023). Answering questions by meta-reasoning over multiple chains of thought. arXiv preprint arXiv:2304.13007.

---

# 附录

## A 使用其他模型的评估

我们进一步研究了使用不同强度的模型进行试错问题解决的适用性。我们发现，指定自我修正的能力是更强、更大的模型的一种新兴品质。

**表4：** 使用starchat-beta [13]在HumanEval Python上的Pass@1准确率

| 方法 | Pass@1准确率（8次试验平均） | Pass@1准确率（标准差） |
|---|---|---|
| 基线 | 0.26 | 0.00481 |
| Reflexion | 0.26 | 0.00305 |

**表5：** 使用不同模型在100个HotPotQA问题上的Pass@1准确率

| 模型 | 基线准确率 | Reflexion准确率 |
|---|---|---|
| CoT (GT) + text-davinci-003 | 0.60 | 0.77 |
| CoT (GT) + gpt-3.5-turbo | 0.57 | 0.71 |
| CoT (GT) + gpt-4 | 0.68 | 0.80 |
| ReAct + text-davinci-003 | 0.30 | 0.55 |
| ReAct + gpt-3.5-turbo | 0.26 | 0.38 |
| ReAct + gpt-4 | 0.39 | 0.51 |

## B 决策

**环境：** 你位于房间中央。快速环顾四周，你看到床1、书桌2、书桌1、抽屉6、抽屉5、抽屉4、抽屉3、抽屉2、抽屉1、垃圾桶1、洗衣篮1、保险柜1、架子6、架子5、架子4、架子3、架子2和架子1。

**任务：** 用台灯检查杯子。

**试验 #1**
> 思考：要解决这个任务，我需要找到并拿一个杯子，然后找到并使用一个台灯。
> 思考：首先我需要找到一个杯子。杯子更可能出现在抽屉(1-6)、书桌(1-2)、架子(1-6)、垃圾桶(1)、洗衣篮(1)中。我可以逐一检查，从抽屉1开始。
> 前往抽屉1
抽屉1是关闭的。
...
> 打开抽屉6
你打开了抽屉6。抽屉6现在是打开的。在里面，你看到钥匙链2。
> 前往书桌1
在书桌1上，你看到信用卡3、台灯1、笔记本电脑2、杯子1、笔1和铅笔1。
> 思考：现在我找到了杯子(1)。接下来，我需要拿起它。
> 从书桌1拿起杯子1
你从书桌1拿起了杯子1。
> 思考：现在我拿了杯子(1)。接下来，我需要找一个台灯。台灯更可能出现在书桌(1-2)、边桌(1-2)、架子(1-6)、床(1)、抽屉(1-6)中。我可以逐一检查，从书桌1开始。
> 前往书桌1
什么都没发生。
> 前往书桌2
在书桌2上，你看到闹钟1、碗1、杯子3、铅笔3和铅笔2。
> 思考：现在我找到了台灯(1)。接下来，我需要使用它。
> 使用台灯1
什么都没发生。
> 使用台灯1
什么都没发生。
**状态：失败**

**反思：** 在这个环境中，我的计划是先找一个杯子，然后找到并使用一个台灯。然而，任务是用台灯检查杯子。我应该先找台灯，然后再找杯子。我注意到台灯是在书桌1上找到的。在下次试验中，我将前往书桌1，找到台灯，然后寻找杯子并用台灯检查它。

**试验 #2**
> 前往书桌1
在书桌1上，你看到信用卡3、台灯1、笔记本电脑2、杯子1、笔1和铅笔1。
> 思考：要解决这个任务，我需要找到并拿一个杯子，然后找到并使用一个台灯。
> 从书桌1拿起杯子1
你从书桌1拿起了杯子1。
> 思考：要解决这个任务，我需要找到并拿一个杯子，然后找到并使用一个台灯。
> 使用台灯1
你打开了台灯1。
**状态：成功**

**图5：** [上方] 一个AlfWorld轨迹，智能体因低效规划而失败。在反思中，智能体意识到它应该先找台灯再找杯子，而不是先找杯子再找台灯。[下方] 智能体能够纠正其推理轨迹，并以简洁的方式执行一系列动作。

### B.1 WebShop局限性

在第5节中，我们简要指出Reflexion难以克服需要极具创造性的行为才能逃脱的局部最小值选择。我们在WebShop[29]的实验中观察到了这一缺点。WebShop是一个基于网络的问题解决基准，测试智能体导航电子商务网站以根据客户请求定位和购买产品的能力。我们在100个环境中测试了一个2-shot ReAct + Reflexion智能体。然而，仅四次试验后，我们就终止了运行，因为智能体没有显示出改进的迹象（图6）。此外，智能体在失败尝试后没有生成有帮助的、直观的自我反思。我们得出结论，Reflexion无法解决需要大量多样性和探索的任务。在AlfWorld中，智能体能够充分探索新环境，因为允许的动作可以在观测中看到。在HotPotQA中，智能体面临类似的WebShop搜索查询任务，但更为成功，因为维基百科文章的搜索空间更加多样化，且不需要那么精确的搜索查询。电子商务搜索引擎的一个常见问题是正确处理自然语言搜索解释中的歧义。因此，WebShop提出了一个需要Reflexion智能体做出非常多样化和独特行为的任务。

**图6：** Reflexion与ReAct在WebShop上跨100个客户购物请求的性能对比。ReAct + Reflexion未能显著优于ReAct。

## C 编程

由于LLM的广泛对话训练，编程LLM调用需要严格的指令以仅生成函数体。下面报告了几个编程示例，指令以蓝色突出显示并附有模板。完整实现请参见 https://github.com/noahshinn024/reflexion。

### C.1 编程函数实现示例（HumanEval Python）

**示例函数签名：**
```python
def minSubArraySum(nums):
    """
    给定一个整数数组nums，找到nums的任意非空子数组的最小和。
    示例：
    minSubArraySum([2, 3, 4, 1, 2, 4]) == 1
    minSubArraySum([-1, -2, -3]) == -6
    """
```

**示例函数体实现：**
```python
    min_sum = float('inf')
    for i in range(len(nums)):
        current_sum = 0
        for j in range(i, len(nums)):
            current_sum += nums[j]
            if current_sum < min_sum:
                min_sum = current_sum
    return min_sum
```

### C.2 Reflexion Actor指令

你是一个Python写作助手。你将获得你之前对函数的实现、一系列单元测试结果以及你对之前实现的自我反思。通过仅回复改进后的函数体来应用必要的更改。不要在回复中包含函数签名。你回复的第一行应有4个空格的缩进，以便在语法上与用户提供的签名匹配。用户将给你提供一些示例。

Reflexion Actor的生成遵循以下形式：
（指令）
（函数实现）
（单元测试反馈）
（自我反思）
（下一个函数实现的指令）

完整示例见 https://github.com/noahshinn024/reflexion。

### C.3 Reflexion自我反思指令和示例

你是一个Python写作助手。你将获得你之前对函数的实现、一系列单元测试结果以及你对之前实现的自我反思。通过仅回复改进后的函数体来应用必要的更改。不要在回复中包含函数签名。你回复的第一行应有4个空格的缩进，以便在语法上与用户提供的签名匹配。用户将给你提供一些示例。

Reflexion自我反思的生成遵循以下形式：
（指令）
（函数实现）
（单元测试反馈）

### C.4 Reflexion编程无自我反思消融示例

Reflexion无自我反思消融的Actor生成遵循以下形式：
（指令）
（函数实现）
（单元测试反馈）
（自我反思）
（下一个函数实现的指令）

### C.5 Reflexion编程无测试生成消融示例

Reflexion无测试生成消融的Actor生成遵循以下形式：
（指令）
（函数实现）
（单元测试反馈）
（自我反思）
（下一个函数实现的指令）

## D 推理

### D.1 完整示例

**试验 #1：** 问题：《Grown-Ups》的主演在《Allo 'Allo!》中以哪个角色最为人熟知？

思考1：我需要搜索《Grown-Ups》和《'Allo 'Allo!》，找到主演《Grown-Ups》的演员，然后找到他在《'Allo 'Allo!》中最为人熟知的角色。
动作1：搜索[Grown-Ups]
观察1：《Grown-Ups》是一部1980年BBC制作的英国电视电影，由Mike Leigh导演。主演包括Lesley Manville、Philip Davis、Brenda Blethyn、Janine Duvitski、Lindsay Duncan和Sam Kelly。由Robin Sales剪辑，Louis Marks为BBC制作，最初于1980年11月28日在BBC 2播出。
思考2：《Grown-Ups》的主演包括Lesley Manville、Philip Davis、Brenda Blethyn、Janine Duvitski、Lindsay Duncan和Sam Kelly。我需要搜索《'Allo 'Allo!》并找出哪个演员以哪个角色最为人熟知。
动作2：搜索["'Allo 'Allo!"]
观察2：未找到["'Allo 'Allo!"]。相似结果：["'Allo 'Allo!"、"List of 'Allo 'Allo! characters"、'Gorden Kaye'、"'Allo 'Allo! (series 2)"、'Allô, allô'、'Francesca Gonshaw'、"'Allo 'Allo! (series 4)"、'Kim Hartman'、"'Allo 'Allo! (series 6)"、'Jeremy Lloyd']
思考3：要找到在《'Allo 'Allo!》中以哪个角色最为人熟知的演员，我可以搜索Gorden Kaye。
动作3：搜索[Gorden Kaye]
观察3：Gordon Irving Kaye（1941年4月7日－2017年1月23日），艺名Gorden Kaye，是一位英国演员，以在电视喜剧系列《'Allo 'Allo!》中扮演好色的咖啡馆老板René Artois而最为人熟知。
思考4：Gorden Kaye在电视喜剧系列《'Allo 'Allo!》中以扮演好色的咖啡馆老板René Artois而最为人熟知。所以答案是Rene Artois。
动作4：结束[Rene Artois]
观察4：答案不正确

**试验 #2：** 问题：《Grown-Ups》的主演在《'Allo 'Allo!》中以哪个角色最为人熟知？

思考1：我需要搜索在《'Allo 'Allo!》中以某个角色而最为人熟知的演员，并找出他们以哪个角色最为人熟知。
动作1：搜索[Grown-Ups]
观察1：《Grown-Ups》是一部1980年BBC制作的英国电视电影...
思考2：这段文字没有提到在《'Allo 'Allo!》中以某个角色而最为人熟知的演员。我需要改为搜索演员的名字。
动作2：搜索[Sam Kelly]
观察2：Roger Michael Kelly（1943年12月19日－2014年6月14日），艺名Sam Kelly，是一位英国演员...他以在《'Allo 'Allo!》中扮演Captain Hans Geering、在《Porridge》中扮演Warren、在《On the Up》中扮演Sam以及在《Barbara》中扮演Ted Liversidge而最为人熟知。
思考3：Sam Kelly在《'Allo 'Allo!》中以扮演Captain Hans Geering而最为人熟知，所以答案是Captain Hans Geering。
动作3：结束[Captain Hans Geering]
观察3：答案正确

**反思：** 我搜索了错误的节目名称"'Allo 'Allo!"，导致没有结果。我应该搜索该节目的主要角色Gorden Kaye，以找到他在节目中最为人熟知的角色。

**图7：** 同一环境和任务中的两个HotPotQA试验。Reflexion + ReAct智能体使用自我反思来确定下一次试验更好的搜索方法。

### D.2 Chain-of-Thought + Reflexion

**试验 #1：** 问题：John Lanchester和Alan Dean Foster共同从事什么职业？

思考1：让我们逐步思考。John Lanchester是小说家、记者和评论家。Alan Dean Foster是小说家和编剧。所以John Lanchester和Alan Dean Foster共同从事的职业是小说家和编剧。
动作1：结束[小说家和编剧]
观察1：答案不正确

**试验 #2：** 问题：John Lanchester和Alan Dean Foster共同从事什么职业？

思考1：让我们逐步思考。John Lanchester是小说家、记者和金融记者。Alan Dean Foster是小说家和编剧。所以John Lanchester和Alan Dean Foster共同从事的职业是小说家。
动作1：结束[小说家]
观察1：答案正确

**反思：** 我对John Lanchester和Alan Dean Foster共同职业的推理失败，因为我错误地假设他们都有相同的职业。未来在回答这个问题时，我应该专注于更好地研究两位作者的个体背景，以确保准确识别他们的职业。此外，我应该考虑他们可能拥有多个共同职业的可能性。

### D.3 HotPotQA Chain-of-Thought (GT) + Reflexion

**上下文：** 白原战役是美国独立战争中纽约与新泽西战役的一部分，于1776年10月28日在纽约州白原附近进行。在撤退之后...

**试验 #1：** 问题：独立战争中为争夺纽约市和新泽西州的控制权而进行的一系列战役是什么，于1776年10月28日在纽约州白原附近发生？

思考1：这个问题问的是独立战争中为争夺纽约市和新泽西州控制权的一系列战役，于1776年10月28日在纽约州白原附近发生。从上下文中，我知道这是白原战役。
动作1：结束[白原战役]
观察1：答案不正确

**试验 #2：** 问题：独立战争中为争夺纽约市和新泽西州的控制权而进行的一系列战役是什么，于1776年10月28日在纽约州白原附近发生？

思考1：这个问题问的是独立战争中为争夺纽约市和新泽西州控制权的一系列战役，于1776年10月28日在纽约州白原附近发生。根据上下文，我知道这一系列战役是纽约与新泽西战役。
动作1：结束[纽约与新泽西战役]
观察1：答案正确

**反思：** 反思我提供的错误答案，我意识到我可能没有提供足够的上下文来准确回答问题。问题问的是一系列战役，但我只提供了一个战役的名称。为了在未来更好地回答这个问题，我将确保提供更多上下文，例如战役的名称（即纽约与新泽西战役），以及它是一系列战役的事实。此外，我将确保包含战役的日期和地点，以确保我的答案全面且准确。

### D.4 HotPotQA情景记忆（EPM）消融提示

#### D.4.1 (EPM) Chain-of-Thought + Reflexion

**试验 #1：** 问题：Jonny Craig和Pete Doherty中谁加入过更多的乐队？

思考1：让我们逐步思考。Jonny Craig曾是六个乐队的成员，包括Emarosa、Dance Gavin Dance和Slaves。Pete Doherty曾是七个乐队的成员，包括The Libertines、Babyshambles和The Puta Madres。所以Pete Doherty加入过更多的乐队。
动作1：结束[Pete Doherty]
观察1：答案不正确

**试验 #2：** 问题：Jonny Craig和Pete Doherty中谁加入过更多的乐队？

思考1：让我们逐步思考。我将研究两位音乐人过去和现在的乐队，以确保准确比较他们的乐队成员身份。经过研究，我发现Jonny Craig曾是七个乐队的成员，包括Emarosa、Dance Gavin Dance和Slaves。Pete Doherty曾是七个乐队的成员，包括The Libertines、Babyshambles和The Puta Madres。所以Jonny Craig加入过更多的乐队。
动作2：结束[Jonny Craig]
观察2：答案正确

**反思：** 我对哪位音乐人加入过更多乐队的推理失败，因为我没有考虑到Jonny Craig过去加入过更多的乐队，尽管Pete Doherty目前是更多乐队的成员。未来在回答这个问题时，我应该专注于研究两位音乐人过去和现在的乐队，以确保准确比较他们的乐队成员身份。

#### D.4.2 (EPM) Chain-of-Thought (GT) + Reflexion

**上下文：** Hari Bahadur Basnet是一位尼泊尔政治家。他是Rastriya Janashakti政党对外关系部的负责人。Basnet拥有工程学理学硕士学位。理学硕士（拉丁语："Magister Scientiae"；缩写为MS、M.S.、MSc、M.Sc.、MSci、M.Sci.、ScM、Sc.M.、SciM或Sci.M.）是科学领域的硕士学位...

**试验 #1：** 问题：Rastriya Janashakti政党对外关系部的负责人持有的可以缩写为MS、M.S.或ScM的学位是什么领域的？

（先前轨迹）
思考1：问题是Rastriya Janashakti政党对外关系部的负责人持有的学位是什么领域的。从上下文中，我知道这个学位是理学硕士学位，通常授予科学、工程和医学领域的研究。
动作1：结束[科学、工程和医学]
观察1：答案不正确

**试验 #2：** 问题：Rastriya Janashakti政党对外关系部的负责人持有的可以缩写为MS、M.S.或ScM的学位是什么领域的？

（先前轨迹）
思考1：问题是Rastriya Janashakti政党对外关系部的负责人持有的学位是什么领域的。从上下文中，我知道这个学位是理学硕士学位，通常授予科学、工程和医学领域的研究。然而，问题问的是研究领域，而不是学位。根据上下文，我知道Hari Bahadur Basnet拥有工程学理学硕士学位。
动作1：结束[工程学]
观察1：答案正确

**反思：** 第一次试验时，我误解了问题。我以为问题问的是一类学位，而不是一个具体的学位。我从错误中吸取了教训，在第二次试验中，我更仔细地关注了问题，理解到它问的是具体的研究领域。
