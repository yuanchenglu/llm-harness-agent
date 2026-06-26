# 用化学工具增强大型语言模型

**Andres M. Bran**¹²∗ **Sam Cox**³∗ **Oliver Schilter**²⁴ **Carlo Baldassari**⁴ **Andrew D. White**³ **Philippe Schwaller**¹²

¹ 瑞士洛桑联邦理工学院（EPFL）人工智能化学智能实验室（LIAC）
² 瑞士国家科学基金会（NCCR）催化研究中心，EPFL
³ 罗切斯特大学化学工程系
⁴ IBM Research – Europe，加速发现部门

∗ 同等贡献。

andrew.white@rochester.edu
philippe.schwaller@epfl.ch

## 摘要

在过去的几十年里，优秀的计算化学工具得到了长足发展。将它们集成到单一平台中并提高可访问性，有助于克服陡峭的学习曲线，从而充分发挥其潜力。最近，大型语言模型（LLM）在跨领域的任务中展现出强大的性能，但在与化学相关的问题上仍存在困难。此外，这些模型缺乏对外部知识源的访问，限制了它们在科学应用中的实用性。在本研究中，我们引入了 **ChemCrow**，一个旨在完成有机合成、药物发现和材料设计等任务的 LLM 化学智能体。通过集成 18 个专家设计的工具，ChemCrow 增强了 LLM 在化学领域的性能，并涌现出新的能力。我们的智能体自主规划并执行了驱虫剂、三种有机催化剂的合成，并指导了一种新型发色团的发现。我们的评估（包括 LLM 评估和专家评估）证明了 ChemCrow 在自动化各种化学任务方面的有效性。令人惊讶的是，我们发现 GPT-4 作为评估者无法区分明显错误的 GPT-4 补全结果与 ChemCrow 的性能。我们的工作不仅帮助了化学专家并降低了非专家的入门门槛，还通过弥合实验化学与计算化学之间的差距促进了科学进步。公开可用的代码可在 https://github.com/ur-whitelab/chemcrow-public 获取。

---

## 1 引言

在过去的几年中，语言语言模型（LLM）¹⁻⁵ 通过自动化自然语言任务，改变了多个领域。其中一个典型的例子是 2021 年 GitHub Copilot 的推出⁶，以及更近期的 StarCoder⁷，它们根据文件上下文和打开的窗口提供建议的代码补全，从而提高了开发者的生产力⁸。大多数最新的进展基于 Transformer 架构⁹，该架构最初为神经机器翻译而引入，并扩展到各种自然语言处理任务，展现出 remarkable 的少样本和零样本性能²。然而，认识到 LLM 的局限性至关重要，这些模型常常在看似简单的任务（如基本数学和化学运算）上遇到困难¹⁰,¹¹。例如，GPT-4¹² 和 GPT-3.5¹³ 无法一致且准确地计算 12345*98765，或将 IUPAC 名称转换为相应的分子图¹⁴。这些缺陷可以归因于模型的核心设计——专注于预测后续词元。为了解决这些局限性，一种可行的方法是用专用的外部工具或插件来增强大型语言模型，例如用于数学运算的计算器，或用于 IUPAC 名称到结构转换的 OPSIN¹⁵。这些专门的工具提供精确的答案，从而补偿 LLM 在特定领域的固有缺陷，并提升其整体性能和适用性。

*预印本。正在评审中。*
*arXiv:2304.05376v5 [physics.chem-ph] 2023年10月2日*

化学作为一个领域，已经受到了专家设计的人工智能（AI）系统的影响，这些系统解决特定的问题，如反应预测¹⁶⁻²⁰、逆合成规划²¹⁻²⁷、分子性质预测²⁸⁻³²、从头分子生成³³,³⁴、材料设计³⁵,³⁶以及最近的贝叶斯优化³⁷⁻³⁹。由于其训练的性质，已有研究表明，生成代码的 LLM 确实具备一定的化学理解能力¹⁴。这里所说的理解，是指 LLM 能够适应观察结果、进行多步规划，并正确响应意图¹³,⁴⁰⁻⁴⁴。然而，化学领域达到的自动化水平相对于其他领域仍然较低，这主要是由于其高度实验性的本质、数据的缺乏，以及计算工具即使在指定领域内也存在范围和适用性的限制⁴⁵。

这些工具的集成往往发生在孤立的环境中，例如 RXN for Chemistry¹⁸,²⁴,⁴⁶⁻⁴⁸ 和 AIZynthFinder²⁵,⁴⁹,⁵⁰，并受到促进可集成性的企业指导方针的推动。尽管大多数工具是由开源社区开发的，或通过应用程序编程接口（API）提供访问，但它们的集成和互操作性对实验化学家构成了相当大的挑战，主要是由于他们缺乏计算技能，以及工具种类繁多且学习曲线陡峭，从而阻碍了其潜力的充分发挥。

**图 1：概览与工具集。a) 任务求解过程概览。** 使用各种化学相关的包和软件，创建一组工具。这些工具和用户输入被提供给 LLM。LLM 随后通过自动的、迭代的思维链过程进行推理，决定其路径、工具选择和输入，最终得出最终答案。示例展示了常见驱虫剂 DEET 的合成过程。**b) ChemCrow 中实现的工具集：** 反应、分子、安全、搜索和标准工具。

受其他领域成功应用的启发¹⁰,⁵¹,⁵²，我们提出了一个由 LLM 驱动的化学引擎——**ChemCrow**，旨在简化药物和材料设计及合成等各领域中各种常见化学任务的推理过程。ChemCrow 利用多个专家设计的化学工具的力量，通过向 LLM（在我们的实验中为 GPT-4）提示关于任务和所需格式的特定指令来运行，如图 1a 所示。LLM 获得工具名称列表、其用途描述以及预期输入/输出的详细信息。然后指示它使用提供的工具（必要时）回答用户给出的提示。模型被引导遵循 **Thought, Action, Action Input, Observation** 格式⁴³，这要求它推理当前任务状态，考虑其与最终目标的相关性，并据此规划下一步，从而展示其理解水平。在 Thought 步骤的推理之后，LLM 请求一个工具（以关键词 "Action" 开头）和该工具的输入（以关键词 "Action Input" 开头）。然后文本生成暂停，程序尝试使用提供的输入执行请求的函数。结果以关键词 "Observation" 开头返回给 LLM，LLM 再次进入 Thought 步骤。它继续迭代，直到得出最终答案。

这个工作流程此前在 ReAct⁴³ 和 MRKL⁵³ 论文中有所描述，有效地将思维链推理与任务相关的工具结合起来。结果，如后续章节所示，LLM 从一个过度自信——虽然通常是错误的——信息源，转变为一个推理引擎，被提示反思任务、使用适当的工具收集额外信息、观察工具的响应，并重复这一循环，直到得出最终答案。与本文同期，⁵⁴ 描述了一种类似的方法，用工具增强 LLM 以完成化学任务，这些任务 GPT-4 单独无法完成。他们的重点特别放在云实验室上，而我们的研究则调查了广泛的任务和工具，包括连接到云连接的机器人合成平台。我们实现了 18 个工具，包括网络和文献搜索，以及分子特异性和反应特异性工具，如图 1b 所示，并在第 5.3 节中描述，这些工具不仅赋予 ChemCrow 关于分子和反应性质的知识，还赋予其在实体实验室中直接执行任务的能力。虽然所包含的工具列表并非详尽无遗，但 ChemCrow 被设计为易于通过提供工具及其预期用途描述（全部通过自然语言）来适应新的应用。ChemCrow 充当专家化学家的助手，同时通过提供访问准确化学知识的简单界面，降低非专家的入门门槛。我们在 14 个用例（见附录 G）中分析了 ChemCrow 的能力，包括合成目标分子、安全控制，以及搜索具有相似作用模式的分子。

---

## 2 结果与讨论

### 2.1 自主化学合成

从简单的用户输入，如 *"规划并执行一种驱虫剂的合成"*（图 1a）和 *"找到并合成一种能加速 Diels-Alder 反应的硫脲有机催化剂"*（图 2b），ChemCrow 找到了相应的分子，规划了合成路线，并在 IBM Research 的云连接专有 RoboRXN 平台⁵⁵ 上执行了合成。使用 RoboRXN，ChemCrow 自主运行了驱虫剂（DEET）和三种已知硫脲有机催化剂（Schreiner⁵⁶,⁵⁷、Ricci⁵⁸ 和 Takemoto⁵⁹）的合成。为此，ChemCrow 顺序查询工具，如 **LitSearch/WebSearch**、**Name2SMILES**、**ReactionPlanner**，最后是 **ReactionExecute**，以结合信息并完成任务。合成所得的结构如图 2d 所示，工具的详细描述见第 5.3 节。四种合成均成功得到了预期化合物，证明了与合成规划和执行相关的 LLM 智能体与物理世界的交互。

标准化的合成程序是成功执行的关键。然而，预测的程序⁴⁶ 并不总是可以直接在 RoboRXN 平台上执行；典型的问题包括"溶剂不足"或"无效的纯化操作"。解决这些问题需要人工干预来修复无效操作，然后再尝试执行合成。ChemCrow 能够自主查询平台的合成验证数据，并迭代调整合成程序（例如增加溶剂量），直到合成程序完全有效。**ActionCleaner** 功能包含在 **ReactionExecute** 工具中，无需人工干预。这个例子展示了 ChemCrow 自主适应并成功执行标准化合成程序的能力，减轻了实验室安全问题，并使其适应机器人平台的特定条件。

### 2.2 人机协作

人机交互尤其富有成效，特别是在化学领域——决策通常基于实验结果做出，而实验本身的执行可能具有挑战性，甚至超出最先进的自动驾驶实验室的能力。这里我们展示这种交互如何导致一种新型发色团的发现。对于这个例子，ChemCrow 被指示训练一个机器学习模型，以帮助筛选候选发色团库。如图 3 所示，ChemCrow 能够加载、清理和处理数据，训练和评估随机森林模型，并最终基于模型和给定的目标吸收最大波长 369 nm 提供建议。提出的分子（见图 3）随后被合成和分析，确认发现了一种具有约期望性质（实测吸收最大波长为 336 nm）的新型发色团。

**图 2：实验验证。a)** 用户启动 ChemCrow 运行的脚本示例。**b)** 硫脲有机催化剂的查询与合成。**c)** 实验执行的 IBM Research RoboRXN 合成平台（图片由 International Business Machines Corporation 提供转载许可）。**d)** 经实验验证的化合物。

| 人类化学家 | 人机协作 | ChemCrow |
|---|---|---|
| **任务输入：** <br>这是一些发色团数据。<br>• 清理数据。<br>• 仅使用乙腈作为溶剂的数据。<br>• 预处理数据。<br>• 训练一个随机森林模型来预测分子的吸收最大波长。<br>• 然后对选择池中的分子进行预测。<br>• 最后，为波长最接近 369 nm 的分子提出一个合成方案。 | **ChemCrow 操作：**<br>1. 检查数据行以了解格式。<br>2. 过滤数据、溶剂和相关列。<br>3. 计算 Morgan 指纹并将数据集分为训练/测试集。<br>4. 训练和评估随机森林模型。<br>5. 从选择池中提出分子。<br>6. 预测所选分子的 2 步合成程序。<br>**人类操作：**<br>• 合成所提出的分子。<br>• 使用 MS(ESI) 和 NMR 确认产物。<br>• 分析 UV-Vis 吸收光谱。 | 合成 (E)-3-甲基-4-(2-(3'-(甲基磺酰胺基)-[1,1'-联苯]-4-基)乙烯基)苯甲酸酯，其预测最大吸收波长最接近 369 nm。随机森林模型的均方根误差为 37 nm。 |
| | 波长 [nm] 吸光度 [AU] | **最终答案：** <br>O<br>O<br>H<br>N<br>S<br>O<br>O<br>O<br>O<br>H<br>N<br>S<br>O<br>O<br>在乙腈中 |

**图 3：人机模型交互导致新型发色团的发现。** 左：人类输入、操作和观察。右：ChemCrow 的操作和最终答案，包含新型发色团的建议。

### 2.3 跨多样化化学用例的评估

近年来，机器学习在化学中的应用激增，产生了丰富的数据集和基准⁶⁰,⁶¹。然而，很少有基准专注于评估 LLM 在化学特定任务上的表现，并且由于进展迅速，标准化的评估技术尚未建立，这给评估我们在此展示的方法带来了挑战。为了解决这个问题，我们与化学专家合作，开发了一组测试 LLM 使用化学特定工具和解决问题能力的任务。选定的任务由 ChemCrow 和 GPT-4（后者被提示扮演化学专家的角色）执行，这些结果通过基于 LLM 的评估和人类专家评估相结合的方式进行评价。对于前者，我们从⁵,⁶²,⁶³ 中描述的评估方法中汲取灵感，作者使用一个评估者 LLM，被指示扮演教师评估学生的角色。在我们的案例中，我们调整了提示，使评估者 LLM（我们称之为 **EvaluatorGPT**）仅根据任务是否得到解决以及整体思维过程是否正确来评分。EvaluatorGPT 进一步被指示强调每种方法的优点和缺点，并提供关于每个回答如何改进的进一步反馈，为解释 LLM 的评估提供基础。涵盖药物合成规划、具有相似性质和作用模式的新型化合物设计以及反应机理解释等若干任务的完整结果见附录 G。完整的示例也可在 https://github.com/ur-whitelab/chemcrow-runs 获取。

**图 4：评估结果。** GPT-4 和 ChemCrow 在一系列任务上的比较性能。**a.** 每任务偏好。对于每个任务，评估者被问及他们对哪个回答更满意。任务分为三类：合成、分子设计和化学逻辑。任务按类别内难度递增排序。**b.** 有机合成任务中回答的化学准确性（事实性），按目标的合成可及性排序。**c.** 人类评估者对所有任务各指标的综合结果，与 EvaluatorGPT 得分进行比较。误差线代表置信区间（95%）。

值得指出的是，ChemCrow 回答的有效性既取决于工具的质量，也取决于智能体的推理过程，两者在 ChemCrow 的执行过程中相互影响。例如，合成规划能力可以受益于改进的底层合成引擎——这是一个活跃的研究领域²³,⁶⁴,⁶⁵。即便如此，如果使用工具背后的推理存在缺陷，或者向工具提供了垃圾输入，任何工具都会变得无用。类似地，工具的不准确输出可能导致智能体得出错误结论。由于这些原因，我们请一组化学专家从三个维度评估每个模型在每项任务上的表现：1. 化学正确性，2. 推理质量，以及 3. 任务完成程度，见附录 B。如图 4 所示，ChemCrow 优于不使用工具的 LLM，特别是在需要更扎实的化学推理的更复杂任务上。另一方面，GPT-4 系统性地无法提供事实准确的信息，然而其风格更流畅和完整，因而被 EvaluatorGPT 青睐；但其产生的幻觉在彻底检查后仍然会被揭露。如图 4a 和 4b 所示，GPT-4 仅在较简单的任务上优于 ChemCrow，这些任务的目标非常清晰，且所有必要信息都是 GPT-4 训练数据的一部分，使其能够基于几乎纯粹的训练数据记忆提供更完整的回答（例如 DEET 和扑热息痛的合成）。相比之下，ChemCrow 在多个目标和难度级别上始终提供更好的解决方案，导致化学专家强烈偏好 ChemCrow，显示了其作为从业化学家工具的潜力。

注意图 4 中人类评估与 LLM 评估之间的差异。虽然人类在所有三个提出的指标上都偏好 ChemCrow 并给予高分，但 EvaluatorGPT 得出结论，平均而言 GPT-4 是更好的模型，其判断通常基于回答的流畅性和表面的完整性。GPT-4 最近被提出并用作自我评估方法⁵,⁶²，但这些结果表明，当它缺乏理解提示所需的信息时，它也缺乏评估提示补全所需的信息，从而无法提供可信的评估，使其在事实性在评估中起关键作用时无法用于 LLM 能力的基准测试。

---

## 3 风险管理策略

像 ChemCrow 这样由 LLM 驱动的化学引擎的实施和使用，通过促进不同专家设计工具输出的简化组合，为非专家研究人员提供了能力。在任何自动化化学平台上，都有操作人员和化学专家进行高水平的审查和控制。尽管如此，确保 LLM 智能体的负责任开发和使用至关重要⁶⁶⁻⁶⁸。

我们讨论潜在的风险并提出可能的缓解策略。这些可以通过远见和安全保障措施来实现，同时仍然促进开放和透明的科学，以便研究界的广泛监督和反馈。

**潜在风险** 仅向经过培训的化学家提供化学实验室访问权限是世界性的安全标准。然而，尝试基于 LLM 驱动引擎的建议进行实验可能导致事故或危险情况。为了减轻这些风险，我们为智能体提供了必须遵守的安全指令，例如在继续推进任务之前检查安全信息。如图 5 所示，ChemCrow 遵循一组硬编码的指导方针（见附录 D），检查查询的分子是否不是已知的受控化学品以及其他安全信息；在这种情况下，执行会停止。如果不是，则继续执行，并且这些信息被模型重用，以提供更完整的答案，包括建议物质的安全问题，以及关于如何安全处理它们的合理建议。另一个更通用的缓解策略可能涉及整合安全检查与专家审查系统，确保建议符合既定安全标准和协议。

由于 LLM 驱动引擎缺乏足够的化学知识而导致的不准确或不完整的推理构成了另一个风险，因为它可能导致有缺陷的决策或有问题的实验结果。本文的关键点之一是，专家设计的工具的集成有助于减轻通常与这些模型相关的幻觉问题，从而降低不准确的风险。然而，当模型由于对化学概念的理解有限而无法充分分析不同的观察结果时，仍可能出现问题，可能导致次优结果。为了解决这个问题，开发者可以专注于提高训练数据的质量和广度，融入更先进的化学知识，并完善 LLM 对复杂化学概念的理解。此外，可以纳入内置的验证或同行评审系统——类似于 GPT-3.5⁶⁹,⁷⁰ 实施的 RLHF——以帮助确保引擎推荐的可靠性。

鼓励用户批判性地评估 LLM 驱动引擎提供的信息，并将其与既定文献和专家意见进行交叉参考，可以进一步减轻依赖有缺陷推理的风险⁷¹。通过结合这些方法，开发者可以努力减少化学知识不足对引擎推理过程的影响，并提高像 ChemCrow 这样的 LLM 驱动化学引擎的整体有效性⁷²。

解决知识产权问题对于像 ChemCrow 这样的生成式 AI 模型的负责任开发和使用至关重要⁷³。需要建立关于化学结构或材料的生成合成、其预测应用以及专有信息潜在侵权的所有权的更清晰指导方针和政策。与法律专家和行业利益相关者的合作有助于应对这些复杂问题，并实施适当措施来保护知识产权。

**图 5：ChemCrow 提供的安全指南。** 示例任务，其中明确要求安全信息以及扑热息痛的合成程序（左）。该分子未被发现是受控化学品，因此执行继续，同时包含一般实验室安全信息。在输入分子被发现是受控化学品的情况下（右），执行停止并发出警告，表明提出与受控化学品性质相似的化合物是非法且不道德的。

总之，必须仔细考虑和解决与 LLM 驱动的化学引擎（如 ChemCrow）相关的潜在缺点，以确保其安全和负责任的应用。通过集成专家设计的工具，可以减轻模型幻觉问题，同时提高训练数据的质量和广度可以增强引擎对复杂化学概念的理解。实施有效的缓解策略，如访问控制、安全指南和道德政策，进一步有助于最小化风险，并最大化这些引擎对化学领域的积极影响。随着技术的不断发展，开发者、用户和行业利益相关者之间的合作与警惕对于识别和应对新风险和挑战⁷⁴,⁷⁵至关重要，促进 LLM 驱动化学引擎领域的负责任创新与进步。

---

## 4 结论

在这项研究中，我们展示了 **ChemCrow** 的开发，一种在化学中集成计算工具的新型 LLM 驱动方法。通过将 LLM 的推理能力与计算工具中的化学专家知识相结合，ChemCrow 展示了首批与物理世界交互的化学相关 LLM 智能体之一。ChemCrow 成功规划并合成了驱虫剂、三种有机催化剂，并指导了具有目标性质的新型发色团的筛选和合成。此外，ChemCrow 能够独立解决化学中的推理任务，从简单的药物发现循环到跨广泛分子复杂度的物质合成规划，表明其作为未来化学助手（类 ChatGPT）的潜力。

尽管当前的结果受到所选工具数量和质量的限制，但可能性空间是巨大的，特别是因为潜在的工具不限于化学领域。其他基于语言的工具、图像处理工具等的整合可以显著增强 ChemCrow 的能力。此外，虽然选定的评估任务有限，但进一步的研究和开发可以扩展和多样化这些任务，以真正推动这些系统所能达到的极限。

化学专家的评估显示，ChemCrow 在化学事实性、推理和回答完整性方面优于 GPT-4，特别是对于日益复杂的任务。虽然 GPT-4 在涉及记忆的任务（如合成众所周知的分子如扑热息痛和阿司匹林）上可能表现更好，但 ChemCrow 在任务新颖或鲜为人知时表现出色，而这是最有用和最具挑战性的情况。相比之下，LLM 驱动的评估倾向于偏好 GPT-4，主要是因为其回答更流畅且看起来更完整。然而，重要的是要注意，LLM 驱动的评估在评估模型在化学推理中的真实有效性方面可能不如人类评估可靠。这种差异凸显了进一步完善评估方法的需求，以更好地捕捉像 ChemCrow 这样的系统在解决复杂的现实世界化学问题时的独特能力。

评估过程并非没有挑战，改进的实验设计可以提高结果的有效性。一个主要挑战是当前基于 API 的 LLM 方法下个体结果缺乏可重复性，因为闭源模型提供的控制有限，见附录 E。最近的开源模型⁷⁶⁻⁷⁸ 为这个问题提供了潜在的解决方案，尽管可能在推理能力上有所权衡。此外，任务选择中的隐性偏见以及大规模测试任务解决方案背后化学逻辑的固有局限性，给评估 ML 系统带来了困难。

尽管存在这些挑战，我们的结果证明了像 ChemCrow 这样的系统在化学实验室中担任有价值的助手以及在多样化领域解决化学任务的有前途的能力和潜力。

---

## 5 方法

### 5.1 大型语言模型（LLM）

近年来 LLM 的兴起，以及它们在最近几个月的快速进步、可用性和规模扩展，为广泛的应用和想法打开了大门。当作为某些旨在利用其零样本推理能力的框架的一部分使用时，LLM 的使用变得更加强大，如 ReAct⁴³ 和 MRKL⁵³ 等架构所示。这些架构允许将思维链⁴¹ 推理的成功与 LLM 使用工具的能力结合起来¹⁰。在我们的实验中，我们使用了 OpenAI 的 GPT-4¹²，温度为 0.1。

### 5.2 LLM 应用框架——LangChain

LangChain⁷⁹ 是一个综合框架，旨在通过为各种模块提供支持来促进语言模型应用的开发，包括访问各种 LLM、提示、文档加载器、链、索引、智能体、记忆和聊天功能。借助这些模块，LangChain 使用户能够创建各种应用，如聊天机器人、问答系统、摘要工具和数据增强生成系统。LangChain 不仅为这些模块提供标准接口，还协助与外部工具的集成、尝试不同的提示和模型，以及评估生成模型的性能。在我们的实现中，我们通过 LangChain 集成外部工具，因为已有研究表明 LLM 与工具配合使用时表现更好¹⁰,³²,⁸⁰。

### 5.3 工具

虽然我们的实现使用了有限的工具集，但必须指出，这个工具集可以根据需求和可用性非常容易地扩展。

所使用的工具可以分为通用工具、分子工具和化学反应工具。

#### 5.3.1 通用工具

**WebSearch（网络搜索）** 网络搜索工具旨在为语言模型提供从网络中获取相关信息的能力。利用 SerpAPI⁸¹，该工具查询搜索引擎并编译来自 Google 搜索结果第一页的精选摘要。这使得模型能够在广泛科学主题中收集当前和相关信息。这个工具的一个显著特点是，当模型遇到无法处理的问题或不确定应用何种工具时，它可以作为一个起跳板。集成此工具使语言模型能够高效扩展其知识库，简化应对常见科学挑战的过程，并验证其提供信息的精确性和可靠性。默认情况下，智能体优先使用 **LitSearch** 而非 **WebSearch** 工具。

**LitSearch（文献搜索）** 文献搜索工具专注于从科学文档（如 PDF 或文本文件，包括原始 HTML）中提取相关信息，以提供准确且有依据的答案。该工具利用 paper-qa Python 包（https://github.com/whitead/paper-qa）。通过利用 OpenAI Embeddings⁸² 和 FAISS⁸³（一种向量数据库），该工具有效地嵌入和搜索文档。然后，语言模型基于这些嵌入向量帮助生成答案。文献搜索过程涉及将文档和查询嵌入为向量，并搜索文档中前 k 个相关段落。一旦识别出这些相关段落，该工具会创建每个段落相对于查询的摘要。然后将这些摘要纳入提示中，使语言模型能够生成有依据的答案。通过将回答锚定在现有科学文献中，文献搜索工具显著增强了模型为常规科学任务提供可靠和准确信息的能力，同时包含相关论文的参考文献。

**Python REPL** LangChain 的标准工具之一，Python REPL 为 ChemCrow 提供了一个功能性的 Python shell。此工具使 LLM 能够直接编写和运行 Python 代码，使其更容易完成各种复杂任务。这些任务范围从执行数值计算到训练 AI 模型和执行数据分析。

**Human（人工）** 此工具作为人机交互的直接接口，允许引擎提出问题并期待用户的响应。LLM 在遇到困难或对下一步不确定时可能会请求使用此工具。在我们的示例中，展示了这个工具如何通过直接指示智能体请求执行某些任务的权限（如在机器人平台上启动实验或继续数据分析工作流），从而赋予用户对 ChemCrow 操作的更多控制权。

#### 5.3.2 分子工具

**Name2SMILES** 此工具专门设计用于获取给定分子的 SMILES 表示。通过输入分子名称（或 CAS 号），返回相应的 SMILES 字符串。该工具允许用户通过自然语言引用分子（例如咖啡因、他汀类药物等）、IUPAC 名称等，请求涉及分子分析和操作的任务。我们的实现首先查询 chem-space⁸⁴ 作为主要来源，失败时查询 PubChem⁸⁵ 和 IUPAC 到 SMILES 转换器 OPSIN⁸⁶ 作为最后选项。

**SMILES2Price** 此工具的目的是提供有关特定分子的可购买性和商业成本的信息。通过输入分子，它首先利用 molbloom⁸⁷ 检查该分子是否可购买（在 ZINC20⁸⁸ 中）。然后，使用 chem-space API⁸⁴ 返回市场上的最低价格，使 LLM 能够就所查询分子的可负担性和可用性做出明智决策，以解决给定任务。

**Name2CAS** 该工具旨在通过查询 PubChem⁸⁵ 数据库，使用各种类型的输入引用（如通用名称、IUPAC 名称或 SMILES 字符串），来确定给定分子的化学文摘社（CAS）号。通过将这些分子表示转换为唯一的 CAS 号，它极大地方便了任何分子的网络搜索和信息检索。CAS 号作为一种精确且普遍认可的化学标识符，使研究人员能够轻松访问相关数据和资源，并确保他们获得关于目标分子的准确和一致的信息⁸⁹。

**Similarity（相似性）** 此工具的主要功能是评估两个分子之间的相似性，利用基于输入分子 ECFP2 分子指纹⁹¹ 的 Tanimoto 相似性度量⁹⁰。该工具接收两个分子，返回分子结构相似性的度量，这对于评估分子类似物在各种应用（如药物发现和化学研究）中的潜力很有价值。此工具允许模型计算和比较分子对之间的相似性。Tanimoto 相似性方法提供了分子结构的稳健和可靠比较，使科学家在探索新的候选分子或研究构效关系时能够做出明智的决策。

**ModifyMol（分子修饰）** 此工具旨在通过对给定分子使用逆合成和正向合成规则生成其局部化学空间来对其进行修改。它采用 SynSpace 包⁹²，最初用于分子机器学习的反事实解释⁹³。修饰过程使用 50 种稳健的药物化学反应⁹⁴，逆合成通过 PostEra Manifold¹⁸,⁹⁵（在 API 密钥可用时）或通过对 50 种稳健反应进行反转来执行。可购买的构建块来自 Purchasable Mcule 供应商构建块目录⁹⁶，但也可提供定制选项。通过将分子的 SMILES 表示作为输入，该工具返回由小变化产生的单个修饰分子。此工具赋予模型探索结构相似分子并生成新分子的能力。这使得研究人员能够探索新的分子结构、衍生物，并为其特定应用（如药物发现和化学研究）微调候选分子。

**PatentCheck（专利检查）** 专利检查工具旨在验证分子是否已被专利保护，无需网络请求。它利用 molbloom⁸⁷（一个用于针对布隆过滤器检查字符串的 C 库），使其成为针对已知数据库评估化合物的高效工具。此工具在实现中的主要应用是通过检查 ZINC 可购买化合物数据库来确定分子是否可购买。通过输入分子的 SMILES 表示，专利检查工具告知 LLM 该特定分子是否存在专利，从而帮助其避免潜在的知识产权冲突并确定给定化合物是否具有新颖性。

**FuncGroups（官能团）** 此工具旨在通过分析命名的 SMARTS（SMiles 任意目标规范）模式列表来识别给定分子中的官能团。通过输入单个分子的 SMILES 表示，官能团查找器搜索分子结构与预定义的表示各种官能团的 SMARTS 模式之间的匹配。识别出这些匹配后，该工具返回分子中存在的官能团列表。这些信息对于理解分子的反应性、性质和在各科学领域（如药物发现、化学研究和材料科学）中的潜在应用至关重要。通过提供分子官能团的全面概览，LLM 可以在设计实验、合成化合物或探索新的候选分子时做出明智的决策。

**SMILES2Weight** 此工具的目的是在给定分子 SMILES 表示的情况下计算该分子的分子量。该工具利用 RDKit⁹⁷ 从 SMILES 字符串中获取精确分子量。

#### 5.3.3 安全工具

如前几节所述，安全是开发像 ChemCrow 这样的工具时最突出的问题之一。所提出的风险管理策略之一是提供内置的安全评估功能，使 LLM 能够评估任何提出的分子、反应或程序的潜在风险。

**ControlledChemicalCheck（受控化学品检查）** 为减少意外风险而创建，此工具接收分子的 CAS 号，并对照多个公认的化学武器和前体清单（禁止化学武器组织附表 1-3⁹⁸ 和澳大利亚集团出口管制清单：化学武器前体⁹⁹）进行检查。当请求对给定分子进行合成方法或执行时，此工具会被自动调用。如果该分子在这些清单中找到——表明它可能是一种化学武器或前体——智能体立即停止执行。该工具用于提供关键的安全信息，使用户能够做出明智和更安全的决策。

**ExplosiveCheck（爆炸物检查）** 此工具利用全球化学品统一分类和标签制度（GHS）来识别爆炸性分子。它使用分子标识符（如通用名称、IUPAC 名称或 CAS 号）查询 PubChem 数据库。如果分子的 GHS 评级为"爆炸性"，则该工具确认其爆炸性质。此工具使用户能够就物质和反应的安全性做出明智决策。此外，当用户请求合成方法时，ChemCrow 会自动调用此工具，向用户发出适当的警告或错误，从而减轻相关风险。

**SafetySummary（安全摘要）** 此工具为任何给定分子提供通用安全概览。它通过查询 PubChem 数据库⁸⁵ 的数据生成安全摘要，并使用 LLM 作为接口来突出四个核心方面：操作安全（操作者的潜在风险，即处理给定物质时的健康问题）、GHS 信息（处理该物质的一般危害和建议）、环境风险（处理该物质的任何环境问题以及处理建议）以及社会影响：该物质是否为已知的受控化学品。当没有可用信息时，允许 LLM 填补空白，同时明确说明。在这种情况下，允许 GPT-4 填补空白，但必须明确说明。此工具提供了来自 PubChem 数据库的全面且易于理解的安全信息，使用户能够做出明智的决定并采取适当的安全措施。其填补数据空白的能力确保了完整、可访问的信息，简化了用户的流程。

#### 5.3.4 化学反应工具

**NameRXN（反应命名）** 此工具由 NextMove Software¹⁰⁰ 的专有软件 NameRxn 驱动，旨在根据其内部数据库中数百个命名反应来识别和分类给定的化学反应。通过输入反应 SMILES，该工具返回分类代码和反应名称（自然语言描述）。分类代码对应于 Carey、Laffan、Thomson 和 Williams¹⁰¹ 提出的层级结构中的位置。这些信息对于理解反应机理、选择适当的催化剂和优化实验条件至关重要。

**ReactionPredict（反应预测）** 反应预测工具利用 IBM Research 的 RXN4Chemistry API⁴⁸，该 API 使用专门为预测化学反应和逆合成路径定制的 Transformer 模型，基于 Molecular Transformer¹⁸,²⁴ 并提供高精度预测。该工具接收一组反应物作为输入，返回预测的产物，使 LLM 能够获得通常无法通过简单数据库查询获得的准确化学信息，而是需要化学家经过训练才能执行的某种抽象推理。虽然该 API 可免费使用，但需要注册。

**ReactionPlanner（反应规划器）** 这个强大的工具也使用 IBM Research 的 RXN4Chemistry API¹⁸,²⁴,⁴⁸，采用与反应预测工具相同的 Transformer 方法进行翻译任务，但增加了处理多步合成的搜索算法，以及将反应序列转换为机器可读的可操作步骤的操作预测算法，包括条件、添加剂和溶剂¹⁰²。为了与 ChemCrow 交互，我们增加了一个 LLM 处理步骤，将这些机器可读操作转换为自然语言。分子合成规划器旨在帮助 LLM 规划合成路线以制备所需的目标分子。通过输入所需产物的 SMILES 表示，此工具使 ChemCrow 能够设计并比较通往目标化合物的高效合成路径。

**ReactionExecute（反应执行）** 此工具允许 ChemCrow 通过机器人化学实验室平台与物理世界直接交互。同样基于 RXN4Chemistry API，该工具允许智能体规划、适应和执行给定分子的合成。在内部，该工具请求合成计划（使用 RXNPlanner 工具），获取要在机器人上执行的操作序列，并使用 LLM 驱动的循环来适应操作序列中的错误和警告。最后，它请求用户许可启动合成，并在成功启动操作序列后返回成功消息。

---

## 数据与代码可用性

本研究中进行的所有实验可在 https://github.com/ur-whitelab/chemcrow-runs 找到。此外，ChemCrow 平台的开源版本已在 https://github.com/ur-whitelab/chemcrow-public 发布，其中包括主要的智能体设置和原始实现中使用的 12 个工具的子集。

---

## 致谢

A.M.B.、O.S. 和 P.S. 感谢 NCCR 催化研究（资助号 180544）的支持，该研究是瑞士国家科学基金会资助的国家研究能力中心。S.C. 和 A.D.W. 感谢 NSF 资助号 1751471 的支持。本工作报告的研究得到了美国国立卫生研究院国家普通医学科学研究所的资助，资助号为 R35GM137966。作者感谢更广泛的 RXN for Chemistry 团队的支持，并感谢其授予对平台的有限访问权限，仅用于执行所报告的合成。

---

## 参考文献

[1] Devlin, J.; Chang, M.-W.; Lee, K.; Toutanova, K. Bert: Pre-training of deep bidirectional transformers for language understanding. *arXiv preprint arXiv:1810.04805* **2018**.

[2] Brown, T.; Mann, B.; Ryder, N.; Subbiah, M.; Kaplan, J. D.; Dhariwal, P.; Neelakantan, A.; Shyam, P.; Sastry, G.; Askell, A., et al. Language models are few-shot learners. *Advances in neural information processing systems* **2020**, *33*, 1877–1901.

[3] Bommasani, R.; Hudson, D. A.; Adeli, E.; Altman, R.; Arora, S.; von Arx, S.; Bernstein, M. S.; Bohg, J.; Bosselut, A.; Brunskill, E., et al. On the opportunities and risks of foundation models. *arXiv preprint arXiv:2108.07258* **2021**.

[4] Chowdhery, A.; Narang, S.; Devlin, J.; Bosma, M.; Mishra, G.; Roberts, A.; Barham, P.; Chung, H. W.; Sutton, C.; Gehrmann, S., et al. Palm: Scaling language modeling with pathways. *arXiv preprint arXiv:2204.02311* **2022**.

[5] Bubeck, S.; Chandrasekaran, V.; Eldan, R.; Gehrke, J.; Horvitz, E.; Kamar, E.; Lee, P.; Lee, Y. T.; Li, Y.; Lundberg, S., et al. Sparks of artificial general intelligence: Early experiments with gpt-4. *arXiv preprint arXiv:2303.12712* **2023**.

[6] GitHub Copilot: Your AI pair programmer. https://copilot.github.com.

[7] Li, R. et al. StarCoder: may the source be with you! **2023**.

[8] Ziegler, A.; Kalliamvakou, E.; Li, X. A.; Rice, A.; Rifkin, D.; Simister, S.; Sittampalam, G.; Aftandilian, E. Productivity assessment of neural code completion. **2022**, 21–29.

[9] Vaswani, A.; Shazeer, N.; Parmar, N.; Uszkoreit, J.; Jones, L.; Gomez, A. N.; Kaiser, Ł.; Polosukhin, I. Attention is all you need. *Advances in neural information processing systems* **2017**, *30*.

[10] Schick, T.; Dwivedi-Yu, J.; Dessì, R.; Raileanu, R.; Lomeli, M.; Zettlemoyer, L.; Cancedda, N.; Scialom, T. Toolformer: Language models can teach themselves to use tools. *arXiv preprint arXiv:2302.04761* **2023**.

[11] Castro Nascimento, C. M.; Pimentel, A. S. Do Large Language Models Understand Chemistry? A Conversation with ChatGPT. *Journal of Chemical Information and Modeling* **2023**, *63*, 1649–1655.

[12] OpenAI, GPT-4 Technical Report. **2023**.

[13] Ouyang, L.; Wu, J.; Jiang, X.; Almeida, D.; Wainwright, C.; Mishkin, P.; Zhang, C.; Agarwal, S.; Slama, K.; Ray, A., et al. Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems* **2022**, *35*, 27730–27744.

[14] White, A. D.; Hocky, G. M.; Gandhi, H. A.; Ansari, M.; Cox, S.; Wellawatte, G. P.; Sasmal, S.; Yang, Z.; Liu, K.; Singh, Y., et al. Assessment of chemistry knowledge in large language models that generate code. *Digital Discovery* **2023**.

[15] Lowe, D. M.; Corbett, P. T.; Murray-Rust, P.; Glen, R. C. Chemical Name to Structure: OPSIN, an Open Source Solution. *Journal of Chemical Information and Modeling* **2011**, *51*, 739–753, PMID: 21384929.

[16] Coley, C. W.; Barzilay, R.; Jaakkola, T. S.; Green, W. H.; Jensen, K. F. Prediction of organic reaction outcomes using machine learning. *ACS central science* **2017**, *3*, 434–443.

[17] Coley, C. W.; Jin, W.; Rogers, L.; Jamison, T. F.; Jaakkola, T. S.; Green, W. H.; Barzilay, R.; Jensen, K. F. A graph-convolutional neural network model for the prediction of chemical reactivity. *Chem. Sci.* **2019**, *10*, 370–377.

[18] Schwaller, P.; Laino, T.; Gaudin, T.; Bolgar, P.; Hunter, C. A.; Bekas, C.; Lee, A. A. Molecular transformer: a model for uncertainty-calibrated chemical reaction prediction. *ACS central science* **2019**, *5*, 1572–1583.

[19] Pesciullesi, G.; Schwaller, P.; Laino, T.; Reymond, J.-L. Transfer learning enables the molecular transformer to predict regio-and stereoselective reactions on carbohydrates. *Nat. Commun.* **2020**, *11*, 1–8.

[20] Irwin, R.; Dimitriadis, S.; He, J.; Bjerrum, E. J. Chemformer: a pre-trained transformer for computational chemistry. *Machine Learning: Science and Technology* **2022**, *3*, 015022.

[21] Szymkuć, S.; Gajewska, E. P.; Klucznik, T.; Molga, K.; Dittwald, P.; Startek, M.; Bajczyk, M.; Grzybowski, B. A. Computer-assisted synthetic planning: the end of the beginning. *Angew. Chem. -Int. Ed.* **2016**, *55*, 5904–5937.

[22] Segler, M. H.; Preuss, M.; Waller, M. P. Planning chemical syntheses with deep neural networks and symbolic AI. *Nature* **2018**, *555*, 604–610.

[23] Coley, C. W.; Thomas, D. A.; Lummiss, J. A.; Jaworski, J. N.; Breen, C. P.; Schultz, V.; Hart, T.; Fishman, J. S.; Rogers, L.; Gao, H., et al. A robotic platform for flow synthesis of organic compounds informed by AI planning. *Science* **2019**, *365*.

[24] Schwaller, P.; Petraglia, R.; Zullo, V.; Nair, V. H.; Haeuselmann, R. A.; Pisoni, R.; Bekas, C.; Iuliano, A.; Laino, T. Predicting retrosynthetic pathways using transformer-based models and a hyper-graph exploration strategy. *Chemical science* **2020**, *11*, 3316–3325.

[25] Genheden, S.; Thakkar, A.; Chadimová, V.; Reymond, J.-L.; Engkvist, O.; Bjerrum, E. AiZynthFinder: a fast, robust and flexible open-source software for retrosynthetic planning. *J. Cheminf.* **2020**, *12*, 1–9.

[26] Molga, K.; Szymkuć, S.; Grzybowski, B. A. Chemist Ex Machina: Advanced Synthesis Planning by Computers. *Acc. Chem. Res.* **2021**, *54*, 1094–1106.

[27] Schwaller, P.; Vaucher, A. C.; Laplaza, R.; Bunne, C.; Krause, A.; Corminboeuf, C.; Laino, T. Machine intelligence for chemical reaction space. *Wiley Interdisciplinary Reviews: Computational Molecular Science* **2022**, *12*, e1604.

[28] Mayr, A.; Klambauer, G.; Unterthiner, T.; Hochreiter, S. DeepTox: toxicity prediction using deep learning. *Frontiers in Environmental Science* **2016**, *3*, 80.

[29] Yang, K.; Swanson, K.; Jin, W.; Coley, C.; Eiden, P.; Gao, H.; Guzman-Perez, A.; Hopper, T.; Kelley, B.; Mathea, M., et al. Analyzing learned molecular representations for property prediction. *Journal of chemical information and modeling* **2019**, *59*, 3370–3388.

[30] Chithrananda, S.; Grand, G.; Ramsundar, B. Chemberta: Large-scale self-supervised pretraining for molecular property prediction. *arXiv preprint arXiv:2010.09885* **2020**.

[31] van Tilborg, D.; Alenicheva, A.; Grisoni, F. Exposing the limitations of molecular machine learning with activity cliffs. *Journal of Chemical Information and Modeling* **2022**, *62*, 5938–5951.

[32] Jablonka, K. M.; Schwaller, P.; Ortega-Guerrero, A.; Smit, B. Is GPT-3 all you need for low-data discovery in chemistry? **2023**.

[33] Gómez-Bombarelli, R.; Wei, J. N.; Duvenaud, D.; Hernández-Lobato, J. M.; Sánchez-Lengeling, B.; Sheberla, D.; Aguilera-Iparraguirre, J.; Hirzel, T. D.; Adams, R. P.; Aspuru-Guzik, A. Automatic Chemical Design Using a Data-Driven Continuous Representation of Molecules. *ACS Cent. Sci.* **2018**, *4*, 268–276, PMID: 29532027.

[34] Blaschke, T.; Arús-Pous, J.; Chen, H.; Margreitter, C.; Tyrchan, C.; Engkvist, O.; Papadopoulos, K.; Patronov, A. REINVENT 2.0: an AI tool for de novo drug design. *Journal of chemical information and modeling* **2020**, *60*, 5918–5922.

[35] Tao, Q.; Xu, P.; Li, M.; Lu, W. Machine learning for perovskite materials design and discovery. *npj Computational Materials* **2021**, *7*, 1–18.

[36] Gómez-Bombarelli, R. et al. Design of efficient molecular organic light-emitting diodes by a high-throughput virtual screening and experimental approach. *Nature Materials* **2016**, *15*, 1120–1127.

[37] Shields, B. J.; Stevens, J.; Li, J.; Parasram, M.; Damani, F.; Alvarado, J. I. M.; Janey, J. M.; Adams, R. P.; Doyle, A. G. Bayesian reaction optimization as a tool for chemical synthesis. *Nature* **2021**, *590*, 89–96.

[38] Torres, J. A. G.; Lau, S. H.; Anchuri, P.; Stevens, J. M.; Tabora, J. E.; Li, J.; Borovika, A.; Adams, R. P.; Doyle, A. G. A Multi-Objective Active Learning Platform and Web App for Reaction Optimization. *Journal of the American Chemical Society* **2022**, *144*, 19999–20007.

[39] Ramos, M. C.; Michtavy, S. S.; Porosoff, M. D.; White, A. D. Bayesian Optimization of Catalysts With In-context Learning. *arXiv preprint arXiv:2304.05341* **2023**.

[40] Marra, G.; Giannini, F.; Diligenti, M.; Gori, M. Integrating learning and reasoning with deep logic models. **2020**, 517–532.

[41] Wei, J.; Wang, X.; Schuurmans, D.; Bosma, M.; Chi, E.; Le, Q.; Zhou, D. Chain of thought prompting elicits reasoning in large language models. *arXiv preprint arXiv:2201.11903* **2022**.

[42] Ho, N.; Schmid, L.; Yun, S.-Y. Large Language Models Are Reasoning Teachers. *arXiv preprint arXiv:2212.10071* **2022**.

[43] Yao, S.; Zhao, J.; Yu, D.; Du, N.; Shafran, I.; Narasimhan, K.; Cao, Y. React: Synergizing reasoning and acting in language models. *arXiv preprint arXiv:2210.03629* **2022**.

[44] Zelikman, E.; Wu, Y.; Mu, J.; Goodman, N. Star: Bootstrapping reasoning with reasoning. *Advances in Neural Information Processing Systems* **2022**, *35*, 15476–15488.

[45] Zhao, Z.-W.; del Cueto, M.; Troisi, A. Limitations of machine learning models when predicting compounds with completely new chemistries: possible improvements applied to the discovery of new non-fullerene acceptors. *Digital Discovery* **2022**, *1*, 266–276.

[46] Vaucher, A. C.; Schwaller, P.; Geluykens, J.; Nair, V. H.; Iuliano, A.; Laino, T. Inferring experimental procedures from text-based representations of chemical reactions. *Nature communications* **2021**, *12*, 2573.

[47] Schwaller, P.; Probst, D.; Vaucher, A. C.; Nair, V. H.; Kreutter, D.; Laino, T.; Reymond, J.-L. Mapping the space of chemical reactions using attention-based neural networks. *Nature machine intelligence* **2021**, *3*, 144–152.

[48] rxn4Chemistry, rxn4Chemistry. https://github.com/rxn4chemistry/rxn4chemistry, **2020**; Accessed: April 2023.

[49] Thakkar, A.; Kogej, T.; Reymond, J.-L.; Engkvist, O.; Bjerrum, E. J. Datasets and their influence on the development of computer assisted synthesis planning tools in the pharmaceutical domain. *Chemical science* **2020**, *11*, 154–168.

[50] Thakkar, A.; Selmi, N.; Reymond, J.-L.; Engkvist, O.; Bjerrum, E. J. "Ring breaker": neural network driven synthesis prediction of the ring system chemical space. *Journal of medicinal chemistry* **2020**, *63*, 8791–8808.

[51] Yang, Z.; Li, L.; Wang, J.; Lin, K.; Azarnasab, E.; Ahmed, F.; Liu, Z.; Liu, C.; Zeng, M.; Wang, L. MM-REACT: Prompting ChatGPT for Multimodal Reasoning and Action. *arXiv preprint arXiv:2303.11381* **2023**.

[52] Shen, Y.; Song, K.; Tan, X.; Li, D.; Lu, W.; Zhuang, Y. HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in HuggingFace. **2023**.

[53] Karpas, E.; Abend, O.; Belinkov, Y.; Lenz, B.; Lieber, O.; Ratner, N.; Shoham, Y.; Bata, H.; Levine, Y.; Leyton-Brown, K., et al. MRKL Systems: A modular, neuro-symbolic architecture that combines large language models, external knowledge sources and discrete reasoning. *arXiv preprint arXiv:2205.00445* **2022**.

[54] Boiko, D. A.; MacKnight, R.; Gomes, G. Emergent autonomous scientific research capabilities of large language models. *arXiv preprint* **2023**.

[55] IBM RoboRXN | Science | IBM Research — research.ibm.com. https://research.ibm.com/science/ibm-roborxn/, [Accessed 12-May-2023].

[56] Wittkopp, A.; Schreiner, P. R. Metal-Free, Noncovalent Catalysis of Diels–Alder Reactions by Neutral Hydrogen Bond Donors in Organic Solvents and in Water. *Chemistry – A European Journal* **2003**, *9*, 407–414.

[57] Schreiner, P. R.; Wittkopp, A. H-Bonding Additives Act Like Lewis Acid Catalysts. *Organic Letters* **2002**, *4*, 217–220.

[58] Herrera, R. P.; Sgarzani, V.; Bernardi, L.; Ricci, A. Catalytic Enantioselective Friedel–Crafts Alkylation of Indoles with Nitroalkenes by Using a Simple Thiourea Organocatalyst. *Angewandte Chemie International Edition* **2005**, *44*, 6576–6579.

[59] Okino, T.; Hoashi, Y.; Takemoto, Y. Enantioselective Michael Reaction of Malonates to Nitroolefins Catalyzed by Bifunctional Organocatalysts. *Journal of the American Chemical Society* **2003**, *125*, 12672–12673.

[60] Lowe, D. M. Extraction of chemical structures and reactions from the literature. Ph.D. thesis, University of Cambridge, **2012**.

[61] Wu, Z.; Ramsundar, B.; Feinberg, E. N.; Gomes, J.; Geniesse, C.; Pappu, A. S.; Leswing, K.; Pande, V. MoleculeNet: a benchmark for molecular machine learning. *Chemical science* **2018**, *9*, 513–530.

[62] Liu, Y.; Iter, D.; Xu, Y.; Wang, S.; Xu, R.; Zhu, C. GPTEval: NLG Evaluation using GPT-4 with Better Human Alignment. *arXiv preprint arXiv:2303.16634* **2023**.

[63] Eloundou, T.; Manning, S.; Mishkin, P.; Rock, D. Gpts are gpts: An early look at the labor market impact potential of large language models. *arXiv preprint arXiv:2303.10130* **2023**.

[64] Grzybowski, B. A.; Badowski, T.; Molga, K.; Szymkuć, S. Network search algorithms and scoring functions for advanced-level computerized synthesis planning. *WIREs Computational Molecular Science* **2023**, *13*, e1630.

[65] Thakkar, A.; Johansson, S.; Jorner, K.; Buttar, D.; Reymond, J.-L.; Engkvist, O. Artificial intelligence and automation in computer aided synthesis planning. *Reaction chemistry & engineering* **2021**, *6*, 27–51.

[66] Urbina, F.; Lentzos, F.; Invernizzi, C.; Ekins, S. Dual use of artificial-intelligence-powered drug discovery. *Nature Machine Intelligence* **2022**, *4*, 189–191.

[67] Urbina, F.; Lentzos, F.; Invernizzi, C.; Ekins, S. A teachable moment for dual-use. *Nature machine intelligence* **2022**, *4*, 607–607.

[68] Campbell, Q. L.; Herington, J.; White, A. D. Censoring chemical data to mitigate dual use risk. *arXiv preprint arXiv:2304.10510* **2023**.

[69] Gao, L.; Schulman, J.; Hilton, J. Scaling Laws for Reward Model Overoptimization. *arXiv preprint arXiv:2210.10760* **2022**.

[70] Radford, A.; Narasimhan, K.; Salimans, T.; Sutskever, I., et al. Improving language understanding by generative pre-training. **2018**.

[71] Li, B.; Qi, P.; Liu, B.; Di, S.; Liu, J.; Pei, J.; Yi, J.; Zhou, B. Trustworthy AI: From Principles to Practices. *ACM Computing Surveys* **2021**, *55*, 1–46.

[72] Hocky, G. M.; White, A. D. Natural language processing models that automate programming will transform chemistry research and teaching. *Digital Discovery* **2022**, *1*, 79–83.

[73] Henderson, P.; Li, X.; Jurafsky, D.; Hashimoto, T.; Lemley, M. A.; Liang, P. Foundation Models and Fair Use. *arXiv preprint arXiv:2303.15715* **2023**.

[74] Askell, A.; Brundage, M.; Hadfield, G. The Role of Cooperation in Responsible AI Development. **2019**.

[75] Neufville, R. d.; Baum, S. D. Collective action on artificial intelligence: A primer and review. *Technology in Society* **2021**, *66*, 101649.

[76] Touvron, H.; Lavril, T.; Izacard, G.; Martinet, X.; Lachaux, M.-A.; Lacroix, T.; Rozière, B.; Goyal, N.; Hambro, E.; Azhar, F.; Rodriguez, A.; Joulin, A.; Grave, E.; Lample, G. LLaMA: Open and Efficient Foundation Language Models. **2023**.

[77] Chiang, W.-L.; Li, Z.; Lin, Z.; Sheng, Y.; Wu, Z.; Zhang, H.; Zheng, L.; Zhuang, S.; Zhuang, Y.; Gonzalez, J. E.; Stoica, I.; Xing, E. P. Vicuna: An Open-Source Chatbot Impressing GPT-4 with 90%* ChatGPT Quality. **2023**; https://lmsys.org/blog/2023-03-30-vicuna/.

[78] Mukherjee, S.; Mitra, A.; Jawahar, G.; Agarwal, S.; Palangi, H.; Awadallah, A. Orca: Progressive Learning from Complex Explanation Traces of GPT-4. **2023**.

[79] Chase, H. LangChain. **2022**; https://github.com/hwchase17/langchain.

[80] Press, O.; Zhang, M.; Min, S.; Schmidt, L.; Smith, N. A.; Lewis, M. Measuring and Narrowing the Compositionality Gap in Language Models. *arXiv preprint arXiv:2210.03350* **2022**.

[81] SerpAPI, SerpAPI - Google Search Results API. **2023**; https://serpapi.com/.

[82] Neelakantan, A.; Xu, T.; Puri, R.; Radford, A.; Han, J. M.; Tworek, J.; Yuan, Q.; Tezak, N.; Kim, J. W.; Hallacy, C., et al. Text and code embeddings by contrastive pre-training. *arXiv preprint arXiv:2201.10005* **2022**.

[83] Johnson, J.; Douze, M.; Jégou, H. Billion-scale similarity search with GPUs. *IEEE Transactions on Big Data* **2019**, *7*, 535–547.

[84] ChemSpace, ChemSpace - Provider of Chemical Building Blocks, Fragment Libraries, and Screening Compounds. https://chem-space.com/, **2023**.

[85] National Center for Biotechnology Information, PubChem. https://pubchem.ncbi.nlm.nih.gov/, **2023**.

[86] Lowe, D. M.; Corbett, P. T.; Murray-Rust, P.; Glen, R. C. Chemical name to structure: OPSIN, an open source solution. **2011**.

[87] Medina, J.; White, A. D. Bloom filters for molecules. *arXiv preprint arXiv:2304.05386* **2023**.

[88] Irwin, J. J.; Tang, K. G.; Young, J.; Dandarchuluun, C.; Wong, B. R.; Khurelbaatar, M.; Moroz, Y. S.; Mayfield, J.; Sayle, R. A. ZINC20—a free ultralarge-scale chemical database for ligand discovery. *Journal of chemical information and modeling* **2020**, *60*, 6065–6073.

[89] Chemical Abstracts Service, CAS Registry Number. https://www.cas.org/content/cas-registry, Accessed: April 2023.

[90] TT, T. An elementary mathematical theory of classification and prediction; **1958**.

[91] Rogers, D.; Hahn, M. Extended-connectivity fingerprints. *Journal of chemical information and modeling* **2010**, *50*, 742–754.

[92] White, Andrew D, SynSpace. https://github.com/whitead/synspace, Accessed: April 2023; GitHub repository.

[93] Wellawatte, G. P.; Seshadri, A.; White, A. D. Model agnostic generation of counterfactual explanations for molecules. *Chemical science* **2022**, *13*, 3697–3705.

[94] MedChemComm. Accessed: 5 April 2023.

[95] Yang, Q.; Sresht, V.; Bolgar, P.; Hou, X.; Klug-McLeod, J. L.; Butler, C. R., et al. Molecular transformer unifies reaction prediction and retrosynthesis across pharma chemical space. *Chemical communications* **2019**, *55*, 12152–12155.

[96] Mcule, Purchasable Mcule. https://purchasable.mcule.com/, Accessed: April 2023.

[97] RDKit: Open-source cheminformatics. http://www.rdkit.org, [Online; accessed April 2023].

[98] Chemical Weapons Convention, Annex on Chemicals, B. Schedules of Chemicals. http://www.opcw.org, Accessed: May 2023.

[99] Group, A. Export Control List: Chemical Weapons Precursors. https://australiagroup.net/en/, Accessed: May 2023.

[100] NextMove Software, NameRxn. https://www.nextmovesoftware.com/namerxn.html, last accessed 2020/11/07; Accessed: 5 April 2023.

[101] Carey, J. S.; Laffan, D.; Thomson, C.; Williams, M. T. Analysis of the reactions used for the preparation of drug candidate molecules. *Organic & biomolecular chemistry* **2006**, *4*, 2337–2347.

[102] Vaucher, A. C.; Schwaller, P.; Geluykens, J.; Nair, V. H.; Iuliano, A.; Laino, T. Inferring experimental procedures from text-based representations of chemical reactions. *Nature Communications* **2021**, *12*, 2573.

[103] Edwards, C.; Lai, T.; Ros, K.; Honke, G.; Cho, K.; Ji, H. Translation between Molecules and Natural Language. **2022**.

[104] Christofidellis, D.; Giannone, G.; Born, J.; Winther, O.; Laino, T.; Manica, M. Unifying Molecular and Textual Representations via Multi-task Language Modelling. *arXiv preprint arXiv:2301.12586* **2023**.

[105] Azamfirei, R.; Kudchadkar, S. R.; Fackler, J. Large language models and the perils of their hallucinations. *Critical Care* **2023**, *27*, 1–2.

[106] Khapra, M. M.; Sai, A. B. A tutorial on evaluation metrics used in natural language generation. **2021**, 15–19.

[107] Melis, G.; Dyer, C.; Blunsom, P. On the state of the art of evaluation in neural language models. *arXiv preprint arXiv:1707.05589* **2017**.

[108] Flam-Shepherd, D.; Zhu, K.; Aspuru-Guzik, A. Language models can learn complex molecular distributions. *Nature Communications* **2022**, *13*, 3293.

---

## 附录 A 实验步骤

### A.1 驱虫剂

**N,N-二乙基-间甲苯酰胺（DEET）的合成**

将一个 100ml 不锈钢反应器通过真空和氮气冲洗三次进行惰性化处理。向反应器中加入二乙胺（0.3ml, 4.1mmol）和 DCM（15ml）。加入 3-甲基苯甲酰氯的溶液（3.2ml, 3.2mmol, 1M in DCM），混合物在 25°C 搅拌 60 分钟。反应混合物用水（15ml）和 DCM（10ml）萃取。收集有机层，取 0.3ml 样品进行分析。样品用乙腈稀释 100 倍，过滤后注入 HPLC/MS 设备。MS (ES): m/z 192 [M+H] 计算值，实测 192.14 m/z。

### A.2 硫脲催化剂

**Schreiner 催化剂的合成：1,3-双[3,5-双(三氟甲基)苯基]硫脲**

将一个 100ml 不锈钢反应器通过真空和氮气冲洗三次进行惰性化处理。向该反应器中加入 3,5-双(三氟甲基)苯基异硫氰酸酯的溶液（0.4ml, 4mmol, 1M in THF）和 3,5-双(三氟甲基)苯胺的溶液（0.3ml, 3mmol, 1M in THF）。混合物用 14.3ml THF 稀释，在 60°C 搅拌 1 小时。取 0.3ml 反应混合物样品，用乙腈（2.7ml）稀释 10 倍，过滤后注入 HPLC/MS 设备。MS (ES): m/z 501 [M+H] 计算值，实测 501.02 m/z。

**Takemoto 催化剂的合成：1-(3,5-双(三氟甲基)苯基)-3-((1R,2R)-2-(二甲氨基)环己基)硫脲**

将一个 100ml 不锈钢反应器通过真空和氮气冲洗三次进行惰性化处理。向该反应器中加入反式-N,N-二甲基环己烷-1,2-二胺的溶液（0.3ml, 3mmol, 1M in THF），用 14.7ml THF 稀释，然后加入 0.5ml 3,5-双(三氟甲基)苯基异硫氰酸酯（0.5ml, 5mmol, 1M in THF）。反应混合物在室温（25°C）搅拌 24 小时。取 0.3ml 反应混合物样品，用乙腈（2.7ml）稀释 10 倍，过滤后注入 HPLC/MS 设备。MS(ES): m/z 413 [M+H] 计算值，实测 413.14 m/z。

**Ricci 硫脲催化剂的合成：(1-(3,5-双(三氟甲基)苯基)-3-((1R,2S)-2-羟基-2,3-二氢-1H-茚-1-基)硫脲)**

向一个经过三次氮气和真空惰性化处理的 100ml 不锈钢反应器中加入装有 (1R,2S)-1-氨基-2-茚满醇（1.5mmol, 223.8mg）的玻璃安瓿。对反应器加压使玻璃安瓿破裂，然后向反应器中加入 15ml THF。向该混合物中加入 3,5-双(三氟甲基)苯基异硫氰酸酯的溶液（1.5ml, 1.5mmol, 1M in THF）。反应混合物在室温（25°C）搅拌 24 小时。取 0.3ml 反应混合物样品，用乙腈稀释 10 倍并过滤，然后注入 HPLC/MS 设备。MS(ES): m/z 421 [M+H] 计算值，实测 421.08 m/z。

### A.3 发色团合成

**步骤 1：N-(4'-乙烯基-[1,1'-联苯]-3-基)甲磺酰胺**

向一个圆底烧瓶中加入 1-溴-4-乙烯基苯（170.2mg, 0.122ml, 0.93mmol, 1 当量），随后加入 [3-(甲磺酰胺基)苯基]硼酸（200mg, 0.93mmol, 1 当量）、SPhosPd G2（70mg, 0.09mmol, 0.1 当量）和碳酸钠（123mg, 1.63mmol, 1.25 当量）。向该烧瓶中加入 8ml 乙腈和 2ml 水，混合物在 90°C 反应 2 小时 20 分钟。待混合物冷却至室温后，加入 10ml 水，用乙酸乙酯萃取两次（2×15ml）。合并有机层，用 15ml 盐水洗涤。有机层用 Na₂SO₄ 干燥。混合物浓缩后，使用柱色谱（硅胶柱）纯化，梯度洗脱（正己烷:乙酸乙酯从 10% 到 50%）。产物 N-(4'-乙烯基-[1,1'-联苯]-3-基)甲磺酰胺通过 MS(ESI) 和 NMR 确认。HPLC-MS(ESI)：保留时间 5.315 分钟。[M+H] 计算值 274.3573 m/z，实测 274.0901 m/z。[M+NH₄] 计算值 291.3839 m/z，实测 291.1171 m/z。¹H NMR（80 MHz, 氘代氯仿）δ 7.64 – 7.22 (m, 9H), 7.07 – 6.72 (m, 1H), 5.84 (d, J = 17.5 Hz, 1H), 5.34 (d, J = 10.8 Hz, 1H), 3.10 (s, 3H)。¹³C NMR（20 MHz, 氘代氯仿）δ 140.59, 139.41, 138.40, 137.35, 136.45, 130.16, 127.27, 126.78, 124.09, 119.56, 119.18, 114.32, 43.14。

**步骤 2：(E)-3-甲基-4-(2-(3'-(甲基磺酰胺基)-[1,1'-联苯]-4-基)乙烯基)苯甲酸甲酯**

向一个圆底烧瓶中加入 N-(4'-乙烯基-[1,1'-联苯]-3-基)甲磺酰胺（60.1mg, 0.22mmol, 1 当量），加入乙腈（2ml）形成混合物。加入 4-碘-3-甲基苯甲酸甲酯（66mg, 0.23mmol, 1.08 当量），随后加入乙酸钯（2.5mg, 0.01mmol, 0.05 当量）和三乙胺（217.8mg, 0.3ml, 2.15mmol, 9.78 当量）。混合物回流 4 小时后冷却。向冷却的混合物中加入 10ml 乙酸乙酯，用 2×10ml 1M 盐酸水溶液萃取。水相用 10ml 乙酸乙酯洗涤。合并有机层，用 20ml 盐水洗涤，然后用 Na₂SO₄ 干燥。混合物过滤后，使用柱色谱（硅胶）纯化，梯度洗脱（正己烷:乙酸乙酯从 30:70 到 50:50）。产物 (E)-3-甲基-4-(2-(3'-(甲基磺酰胺基)-[1,1'-联苯]-4-基)乙烯基)苯甲酸甲酯通过 MS(ESI) 和 NMR 确认。HPLC-MS(ESI)：保留时间 6.031 分钟。[M+H] 计算值 422.5159 m/z，实测 422.1418 m/z。[M+NH₄] 计算值 439.5425 m/z，实测 439.1686 m/z。¹H NMR（80 MHz, 氘代氯仿）δ 8.02 – 7.29 (m, 13H), 6.55 (s, 1H), 4.02 (s, 3H), 3.16 (s, 3H), 2.59 (s, 3H)。¹³C NMR（20 MHz, 氘代氯仿）δ 166.58, 139.89, 138.91, 137.84, 137.46, 136.20, 135.38, 131.73, 130.28, 130.12, 128.96, 127.56, 127.51, 127.45, 127.40, 126.48, 124.04, 120.91, 116.30, 53.23, 39.23, 19.96。

---

## 附录 B 人类评估

人类评估由四位化学专家组成的小组进行。为便于他们评估模型的表现，我们准备并提供了一份评估表。该表包含每个模型对每项任务的回答。每当文本中提及分子结构或反应（IUPAC 或 SMILES 表示法）时，都使用开源 IUPAC 解析工具 OPSIN¹⁵ 将其转换为相应的图形描述。准备这份表格被证明是一个挑战，因为 GPT-4 的一些回答需要大量的人工解读。下面和图 6 显示了一个示例回答及其相应的解读。

*"为了合成 Takemoto 有机催化剂（1-[3,5-双(三氟甲基)苯基]-3-[(1R,2R)-(-)-2-(二甲氨基)环己基]硫脲），我们可以采取分步方法。以下是可能的合成路线：*

*1. 以 (1R,2R)-(-)-2-(二甲氨基)环己醇为起始原料，使用适当的保护基（如叔丁基二甲基硅基（TBS）基团）保护醇基。这可以通过使起始原料与叔丁基二甲基氯硅烷（TBSCl）和咪唑在无水 DMF（二甲基甲酰胺）中反应来实现，得到 (1R,2R)-(-)-2-(二甲氨基)-4,4-二甲基-3-氧杂硅杂环己烷。*

*2. 接下来，将氨基转化为异硫氰酸酯基。这可以首先使用硫光气（CSCl₂）在无水 THF（四氢呋喃）中将胺转化为硫脲衍生物，然后用强碱如氢化钠（NaH）处理所得硫脲，得到 (1R,2R)-(-)-2-异硫氰酸酯基-4,4-二甲基-3-氧杂硅杂环己烷。*

*3. 在另一个反应中，以 3,5-双(三氟甲基)苯胺为起始原料合成 3,5-双(三氟甲基)苯胺。使用适当的保护基（如 Boc（叔丁氧羰基）基团）保护胺基。这可以通过使起始原料与二碳酸二叔丁酯（Boc₂O）和适当的碱（如三乙胺（Et₃N））在无水二氯甲烷（DCM）中反应来实现，得到 N-Boc-3,5-双(三氟甲基)苯胺。*

*4. 通过使保护后的苯胺与二硫化碳（CS₂）和适当的碱（如叔丁醇钾（t-BuOK））在无水 THF 中反应，将保护后的苯胺转化为相应的硫脲衍生物，得到 N-Boc-3,5-双(三氟甲基)苯基硫脲。*

*5. 现在，将步骤 2 和步骤 4 中得到的两个保护后的硫脲衍生物偶联起来。使 (1R,2R)-(-)-2-异硫氰酸酯基-4,4-二甲基-3-氧杂硅杂环己烷与 N-Boc-3,5-双(三氟甲基)苯基硫脲在适当的碱（如三乙胺）存在下，在无水 DCM 中反应，得到保护后的 Takemoto 有机催化剂。*

*6. 最后，脱除醇和胺基的保护基。用四丁基氟化铵（TBAF）在 THF 中处理保护后的有机催化剂以脱除 TBS 基团。然后用三氟乙酸（TFA）在 DCM 中处理中间体以脱除 Boc 基团。这将得到所需的 Takemoto 有机催化剂：1-[3,5-双(三氟甲基)苯基]-3-[(1R,2R)-(-)-2-(二甲氨基)环己基]硫脲。"*

在对这些输出结果的解读过程中，常见的问题包括给定的 IUPAC 名称与导致该物质的转化文字描述之间存在不一致。在某些情况下，通常可能得出多种可能的结论，使评估过程进一步复杂化。

为减轻评估中的潜在偏差，我们采取了以下步骤对模型的回答进行匿名化处理：1. 随机打乱模型的呈现顺序（即对于给定任务，ChemCrow 的回答随机地出现在 GPT-4 之前或之后）。2. 掩盖 ChemCrow 的风格，通过在 ChemCrow 智能体执行结束时添加额外的摘要层来隐藏其特征性的 ReAct 风格。这有效地将输出转换为更易读且类似助手的解决方案，使其在风格上更难以与其对应物 GPT-4 区分开来。

---

## 附录 C 合成示例：GPT-4 与 ChemCrow 对比

LLM 中的幻觉是 ChemCrow 试图通过添加专家工具来解决的问题。图 6 显示了 GPT-4 和 ChemCrow 在合成 Takemoto 有机催化剂（一种能够实现丙二酸酯对硝基烯烃的对映选择性 Michael 反应的双功能有机催化剂⁵⁹）任务上的结果。完整任务见附录 G.14。

**图 6：模型输出结果的专家分析。** GPT-4（左）提供了一个有缺陷的合成方案，无法导向合成目标，并含有多余的步骤使其进一步偏离。ChemCrow（右）提出了一个单步合成，受到人类评审员的高度评价，并提供了实验条件和用量。

如图所示，ChemCrow 提出的合成方案是一个简单的断开，得到一个异硫氰酸酯和手性取代环己烷以形成所需的硫脲，同时提供了实验条件如溶剂、温度和反应时间。GPT-4 的回答提出了一个冗长的合成，含有一系列不必要的保护/脱保护序列，使用了不必要的缩合反应使路线偏离目标，并提出了一种可能危及手性中心的断开方式（通过使用它来放置硫代异氰酸酯）。除此之外，GPT-4 产生的反应通常难以使用，因为它们需要大量的人类解读，并且所提出的分子（以 IUPAC 名称给出）通常与描述的反应不匹配。尽管如此，EvaluatorGPT 给 GPT-4 打了更高的分数，其论点是该模型"处理了立体化学和保护基策略。回答组织良好，展现了对有机合成的深刻理解"。

这突显了 LLM 驱动的评估在合成化学领域的明显局限性，因为它严重依赖于回答的自信度和流畅性，而不是思维过程的好坏或解决方案的准确性。此外，它还表明，对于这类系统的评估，人类评估仍然非常必要，特别是在化学这样事实性至关重要的领域。

---

## 附录 D 安全工作流程

**图 7：智能体每次收到提示时遵循的这些步骤。**

---

## 附录 E 可重复性

将 LLM 集成到科学工作流中最突出的问题之一是**可重复性**，特别是当闭源 LLM 发挥关键作用时。为了评估 ChemCrow 解决化学推理任务的可重复性，选择了任务 6（见附录 14）并进行了五次独立的 ChemCrow 执行来解决它。

**任务 6：** *预测 1-氯-4-乙炔基苯与 Lindlar 催化剂（使用 CC(=O)[O-].CC(=O)[O-].[Pd].[Pb+2]）混合的产物。预测相同的反应，但将催化剂替换为"[Pd]"。最后，比较两种产物并解释反应机理。*

该任务对我们的目的特别有用，因为得出解决方案需要查询多个工具并收集不同的信息，特别是来自文献搜索工具的信息，然后必须对其进行分析以形成最终答案。然后可以根据回答的深度或信息量以及它们的一致程度来评估可重复性。图 8 显示了执行结果的最终情况。可以看出，虽然 ChemCrow 设法系统性地获得了两种情况的正确产物（通过使用适当的工具），但在其解释结果的过程中出现了偏离正确响应的情况。在五次中有两次，LLM 将 SMILES 字符串 "CCc1ccc(Cl)cc1" 描述为反式烯烃产物，导致其在反应机理差异方面得出错误结论。由于问题出在分子结构解释上，ChemCrow 可以受益于允许进行分子描述等任务的先进文本/分子多模态模型的集成。尽管最近的方法¹⁰³,¹⁰⁴ 正在解决这个问题，但朝着人类水平的分子描述工具仍需要进一步研究。

**图 8：五个独立 ChemCrow 实例在同一任务上的输出（为清晰起见进行了总结），包括给出的产物和比较。**

---

## 附录 F 局限性

尽管 ChemCrow 在不同化学领域的各种任务上表现出令人印象深刻的性能，但要使其可靠地纳入日常化学工作流程，仍存在显著的局限性需要解决。其中最值得注意的是——最近关于 LLM 应用的出版物¹⁰⁵⁻¹⁰⁸ 也讨论过这些——幻觉、评估结果的困难以及可重复性。

在这项研究中，我们展示了化学工具如何显著增强 LLM 的事实正确性和决策能力。尽管如此，模型偶尔仍会因有缺陷的逻辑而产生错误。虽然添加工具确实改善了推理过程，但重要的是要注意，外部工具无法完全纠正 LLM 有缺陷的推理。

评估的挑战是另一个突出问题，阻碍了我们提供对 ChemCrow 在不同任务中的表现的坚实、可靠的评估，并准确确定其可以可靠使用的领域。正如我们的发现所表明的，现有的基于 LLM 的评估方法不足以彻底评估 ChemCrow 的性能，因为它们缺乏检测错误所需的知识，并且倾向于偏好更冗长和看起来更流畅的解决方案。这迫使我们严重依赖人类评估，从而限制了测量性能的速度和规模。此外，设计实验以展示基于 LLM 的工具的优势和劣势仍然是一个挑战，因为这是领域特定的，并且需要大量的人类专家监督。

不可否认，ChemCrow 的有效性也受到其使用工具的质量和数量的限制。例如，开源逆合成规划软件的局限性可以在多个方面看到，如它使用的数据、采用的算法以及在评估中面临的现有挑战。因此，期望 ChemCrow 能够超越其使用的逆合成工具是不合理的，尽管它可以通过集成不同的工具来提高其性能。化学特定机器学习领域的未来改进肯定会对 ChemCrow 有利。这包括开发更优越的工具、具有更深入化学理解的更先进的 LLM，以及智能体架构定义的进一步进展。

---

## 附录 G 任务与评估

以下展示了 ChemCrow 被评估的 14 个任务集，以及执行结果、普通 LLM（GPT-4）在同一任务上的结果，以及来自评估者 LLM 和人类专家委员会的评估结果。

### G.1 任务 1 - 沙芬酰胺的合成

**图 9：GPT-4 和 ChemCrow 在任务 1 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.2 任务 2 - 提出新型有机催化剂

**图 10：GPT-4 和 ChemCrow 在任务 2 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.3 任务 3 - 解释机理

**图 11：GPT-4 和 ChemCrow 在任务 3 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.4 任务 4 - 合成驱虫剂

**图 12：GPT-4 评估者对 GPT-4 和 ChemCrow 在任务 4 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.5 任务 5 - 如何制备目标化合物

**图 13：GPT-4 和 ChemCrow 在任务 5 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.6 任务 6 - 比较催化剂机理

**图 14：GPT-4 和 ChemCrow 在任务 6 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.7 任务 7 - 合成相似分子

**图 15：GPT-4 和 ChemCrow 在任务 7 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.8 任务 8 - Ricci 有机催化剂的合成规划

**图 16：GPT-4 和 ChemCrow 在任务 8 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.9 任务 9 - 预测反应成功与否

**图 17：GPT-4 和 ChemCrow 在任务 9 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.10 任务 10 - 反应产物的性质

**图 18：GPT-4 和 ChemCrow 在任务 10 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.11 任务 11 - 与硝酸甘油相似的分子

**图 19：GPT-4 评估者对 GPT-4 和 ChemCrow 在任务 11 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。在继续合成规划之前，ChemCrow 检查分子是否危险。发现分子具有爆炸性后，执行停止并发出警告。对于此示例，不提供分数，因为执行已停止。

### G.12 任务 12 - 阿托伐他汀的合成与成本

**图 20：GPT-4 和 ChemCrow 在任务 12 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.13 任务 13 - 阿司匹林的合成

**图 21：GPT-4 和 ChemCrow 在任务 13 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。

### G.14 任务 14 - Takemoto 有机催化剂的合成

**图 22：GPT-4 和 ChemCrow 在任务 14 上的表现结果。** 提示（顶部）同时提供给 ChemCrow 和 GPT-4；然后将输出提供给另一个 GPT-4 实例进行评估。提供了 ChemCrow 的总体工作流程以及第一个思维链步骤。报告了专家评估者（平均）和 EvaluatorGPT 的得分。
