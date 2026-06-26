# 使用大语言模型进行自主化学研究

**Article | Nature | Vol 624 | 2023年12月21/28日 | 第570-578页**

Daniil A. Boiko¹, Robert MacKnight¹, Ben Kline² & Gabe Gomes¹,³,⁴✉

¹ 卡内基梅隆大学化学工程系，宾夕法尼亚州匹兹堡，美国  
² Emerald Cloud Lab，加州南旧金山，美国  
³ 卡内基梅隆大学化学系，宾夕法尼亚州匹兹堡，美国  
⁴ 卡内基梅隆大学威尔顿·E·斯科特能源创新研究所，宾夕法尼亚州匹兹堡，美国  
✉ 电子邮箱：gabegomes@cmu.edu

---

**摘要**  
基于Transformer的大语言模型在自然语言处理¹⁻⁵、生物学⁶⁷、化学⁸⁻¹⁰和计算机编程¹¹¹²等多个领域正取得显著进展。在此，我们展示了Coscientist——一个由GPT-4驱动的人工智能系统——的开发与能力，该系统通过融合大语言模型并赋予其互联网与文档搜索、代码执行和实验自动化等工具，能够自主设计、规划和执行复杂实验。Coscientist在六个不同的任务中展示了其加速研究的潜力，包括成功优化钯催化交叉偶联反应，同时展现出（半）自主实验设计和执行的高级能力。我们的研究结果表明，像Coscientist这样的人工智能系统在推动研究方面具有多功能性、高效性和可解释性。

---

## 引言

大语言模型（LLMs），特别是基于Transformer的模型，近年来正经历快速发展。这些模型已成功应用于多个领域，包括自然语言¹⁻⁵、生物学⁶⁷和化学研究⁸⁻¹⁰以及代码生成¹¹¹²。如OpenAI所展示的，模型的极端规模化¹³已在相关领域带来了重大突破¹¹⁴。此外，诸如基于人类反馈的强化学习¹⁵等技术可以显著提升生成文本的质量以及模型在执行多样化任务时对其决策进行推理的能力¹⁶。

2023年3月14日，OpenAI发布了其迄今为止最强大的LLM——GPT-4¹⁴。尽管GPT-4的技术报告中关于模型训练、规模和所用数据的具体细节有限，但OpenAI的研究人员已提供了大量证据证明该模型卓越的问题解决能力。这些能力包括——但不限于——在SAT和BAR考试、LeetCode挑战中取得高百分位数成绩，以及从图像中提取上下文解释（包括小众笑话）等¹⁴。此外，该技术报告还提供了该模型如何用于解决化学相关问题的示例。

与此同时，化学研究的自动化也取得了重大进展。相关例子涵盖从自主发现¹⁷¹⁸和优化有机反应¹⁹，到开发自动化流动系统²⁰²¹和移动平台²²。

实验室自动化技术与强大LLMs的结合，为开发能够自主设计和执行科学实验的备受期待的系统打开了大门。为实现这一目标，我们旨在回答以下问题：LLMs在科学过程中具备哪些能力？我们能实现何种程度的自主性？如何理解自主智能体所做的决策？

在这项工作中，我们提出了一个基于多个LLM的智能智能体（以下简称Coscientist），能够自主设计、规划和执行复杂的科学实验。Coscientist可以使用工具浏览互联网和相关文档，使用机器人实验应用程序接口（APIs），并利用其他LLM完成各种任务。这项工作与自主智能体领域其他研究²³⁻²⁵独立且并行地开展，其中ChemCrow²⁶是该领域在化学方面的另一个示例。在本文中，我们展示了Coscientist在六个任务中的多功能性和性能：（1）利用公开数据规划已知化合物的化学合成；（2）高效搜索和浏览大量硬件文档；（3）利用文档在云实验室中执行高级命令；（4）通过低级指令精确控制液体处理仪器；（5）处理需要同时使用多个硬件模块和整合多种数据源的复杂科学任务；（6）解决需要对先前收集的实验数据进行分析的优化问题。

---

## Coscientist系统架构

Coscientist通过与多个模块（网络和文档搜索、代码执行）交互以及执行实验来获取解决复杂问题所需的知识。主模块（"规划器"）的目标是基于用户输入，通过调用下文定义的命令来进行规划。规划器是一个GPT-4聊天补全实例，扮演助手的角色。初始用户输入以及命令输出被视为发送给规划器的用户消息。规划器的系统提示（定义LLM目标的静态输入）以模块化方式设计¹²⁷，由四个定义动作空间的命令描述：`GOOGLE`、`PYTHON`、`DOCUMENTATION`和`EXPERIMENT`。规划器根据需求调用这些命令中的每一个来收集知识。

`GOOGLE`命令负责通过"网络搜索器"模块搜索互联网，该模块本身也是一个LLM。`PYTHON`命令允许规划器使用"代码执行"模块进行计算以准备实验。`EXPERIMENT`命令通过`DOCUMENTATION`模块描述的API实现"自动化"。与`GOOGLE`类似，`DOCUMENTATION`命令从特定来源向主模块提供信息，在此情况下是关于所需API的文档。在本研究中，我们展示了与Opentrons Python API和Emerald Cloud Lab（ECL）符号实验室语言（SLL）的兼容性。这些模块共同构成Coscientist，它接收来自用户的简单纯文本输入提示（例如，"执行多个Suzuki反应"）。该架构如图1所示。

此外，某些命令可以使用子动作。`GOOGLE`命令能够将提示转换为适当的网络搜索查询，通过Google搜索API运行查询，浏览网页，并将答案回传给规划器。类似地，`DOCUMENTATION`命令执行必要文档（例如，机器人液体处理器或云实验室的文档）的检索和摘要，供规划器调用`EXPERIMENT`命令。

`PYTHON`命令使用隔离的Docker容器执行代码（不依赖任何语言模型），以保护用户机器免受规划器请求的任何意外操作的影响。重要的是，规划器背后的语言模型能够在出现软件错误时修复代码。这同样适用于自动化模块的`EXPERIMENT`命令，该命令在相应硬件上执行生成的代码，或为手动实验提供合成步骤。

---

## 网络搜索模块

为演示网络搜索器模块的功能之一，我们设计了一个由七种化合物组成的测试集，如图2a所示。网络搜索器模块的版本表示为"search-gpt-4"和"search-gpt-3.5-turbo"。我们的基线模型包括OpenAI的GPT-3.5和GPT-4、Anthropic的Claude 1.3²⁸和Falcon-40B-Instruct²⁹——后者在实验时根据OpenLLM排行榜³⁰被认为是性能最好的开源模型之一。

我们提示每个模型提供详细的化合物合成方案，并按以下标准对输出进行评分（图2）：
- **5分**：非常详细且化学准确的步骤描述
- **4分**：详细且化学准确的描述，但不包含试剂用量
- **3分**：正确的化学描述，但不包含逐步操作步骤
- **2分**：极为模糊或不可行的描述
- **1分**：回答错误或未能遵循指令
- 所有低于3分的评分表示任务失败。需要注意的是，所有3到5分之间的答案在化学上都是正确的，但详细程度不同。尽管我们试图更好地规范化评分标准，但标注本质上是主观的，因此不同标注者之间可能存在差异。

在不能浏览网页的模型中，GPT-4的两个版本表现最佳，Claude v.1.3表现出相似的性能。GPT-3表现显著较差，Falcon 40B在大多数情况下失败。所有不能浏览网页的模型都错误地合成了布洛芬（图2c）。硝基苯胺是另一个例子；尽管对化学知识的一些概括可能促使模型提出直接硝化，但这种方法在实验上不可行，因为它会产生产物的混合物，且目标产物含量极低（图2b）。只有GPT-4模型偶尔提供了正确的答案。

基于GPT-4的网络搜索器在合成规划方面显著提升。在对乙酰氨基酚、阿司匹林、硝基苯胺和酚酞的所有试验中，它都达到了最高分（图2b）。尽管它是唯一一个在布洛芬上达到最低可接受分数（3分）的模型，但在乙酸乙酯和苯甲酸上，它的表现低于其他一些模型，可能是因为这些化合物较为常见。这些结果显示了让LLM基于实际信息以避免"幻觉"¹³¹的重要性。总体而言，基于GPT-3.5的网络搜索器性能落后于其GPT-4竞争对手，主要是因为它在输出格式方面未能遵循具体指令。

将规划器的动作空间扩展到利用反应数据库（如Reaxys³²或SciFinder³³）应能显著提升系统性能（尤其是对于多步合成）。另外，分析系统先前的表述是提高其准确性的另一种方法。这可以通过高级提示策略实现，例如ReAct³⁴、思维链（Chain of Thought）³⁵和思维树（Tree of Thoughts）³⁶。

---

## 文档搜索模块

处理软件组件及其交互的复杂性对于将LLM与实验室自动化集成至关重要。一个关键挑战在于使Coscientist能够有效利用技术文档。LLM可以通过解释和学习相关的技术文档来完善其对常见API（如Opentrons Python API³⁷）的理解。此外，我们展示了GPT-4如何学习使用ECL SLL进行编程。

我们的方法涉及为Coscientist配备针对特定任务的关键文档（如图3a所示），使其能够提高使用API的准确性，并提升其在自动化实验中的性能。

信息检索系统通常基于两种候选选择方法：倒排搜索索引和向量数据库³⁸⁻⁴¹。对于第一种方法，搜索索引中的每个唯一单词都被映射到包含该单词的文档。在推理时，所有包含查询中单词的文档都会被选中，并根据各种手动定义的公式进行排序⁴²。第二种方法首先通过神经网络将文档嵌入为向量，或将其表示为词频-逆文档频率（TF-IDF）嵌入向量⁴³，然后构建向量数据库。在推理时，从该数据库中检索相似向量，通常使用近似最近邻搜索算法之一⁴⁴。当使用Transformer模型时，有更多机会原生地处理同义词，而无需像第一种方法那样进行基于同义词的查询扩展⁴⁵。

按照第二种方法，OT-2 API文档的所有部分都使用OpenAI的ada模型进行了嵌入。为确保正确使用API，为规划器的查询生成了ada嵌入向量，并通过基于距离的向量搜索选择文档片段。这种方法对于为Coscientist提供执行化学反应所需的加热-振荡器硬件模块信息至关重要（图3b）。

将这种方法应用于更多样化的机器人生态系统（如ECL）时，会出现更大的挑战。尽管如此，我们可以探索提供ECL SLL信息的有效性——GPT-4模型目前尚不了解该语言。我们针对SLL进行了三项独立研究：（1）提示到函数（prompt-to-function）；（2）提示到SLL（prompt-to-SLL）；（3）提示到样本（prompt-to-samples）。这些研究的详细信息见补充信息中的"ECL实验"部分。

对于研究1，我们为文档搜索器提供了来自ECL的文档指南，内容涉及运行实验的所有可用函数⁴⁶。图3c总结了一个示例，其中用户向系统提供了一个简单提示，规划器随后接收到相关的ECL函数。在所有情况下，函数都被正确识别以用于相应任务。

图3c,d继续描述了研究2——提示到SLL研究。为任务选择了一个适当的函数，并将文档传递给另一个GPT-4模型以进行代码保留和摘要。在完整文档被处理完毕后，规划器接收到使用信息，以提供用SLL编写的`EXPERIMENT`代码。例如，我们提供了一个简单示例，需要使用`ExperimentHPLC`函数。正确使用此函数需要熟悉SLL中定义的特定"模型"和"对象"。生成的代码已成功在ECL上执行；详见补充信息。样本为咖啡因标准品。其他参数（色谱柱、流动相、梯度）由ECL的内部软件确定（高级别描述见补充信息中的"HPLC实验参数估计"部分）。实验结果见补充信息中的"云实验室HPLC实验结果"部分。可以看到，气泡与分析物溶液一起被注入。这说明了在云实验室中开发自动化质量控制技术的重要性。后续实验需要利用网络搜索来指定和/或优化额外的实验参数（色谱柱化学、缓冲体系、梯度等），以优化实验结果。关于此项研究的进一步细节见补充信息中的"ECL文档搜索结果分析"部分。

独立的研究3——提示到样本研究——通过提供可用样本目录进行，使Coscientist能够识别ECL货架上相关的储备液。为展示此功能，我们为文档搜索器模块提供了目录中全部1,110个模型样本。只需提供一个搜索词（例如，"乙腈"），所有相关样本就会被返回。此内容也可在补充信息中找到。

---

## 控制实验室硬件

访问文档使我们能够为Coscientist提供足够的信息，以在物理世界中开展实验。为启动研究，我们选择了Opentrons OT-2——一个具有完善文档的Python API的开源液体处理器。其文档中的"入门"页面被提供给了规划器的系统提示。其他页面使用上述方法进行了向量化。在此研究中，我们没有授予对互联网的访问权限（图4a）。

我们从简单的板布局特定实验开始。自然语言中的直接提示，如"用你选择的颜色每隔一行着色"，产生了准确的方案。当由机器人执行时，这些方案与所请求的提示高度吻合（图4b–e）。

最终，我们旨在评估系统同时集成多个模块的能力。具体来说，我们提供了`UVVIS`命令，该命令可用于将微孔板传送至在紫外-可见波长范围内工作的读板机。为评估Coscientist使用多种硬件工具的能力，我们设计了一个简单的任务：在一个96孔板的3个孔中分别含有三种不同的颜色——红、黄、蓝。系统必须在不事先了解任何信息的情况下，确定这些颜色及其在板上的位置。

Coscientist的首要行动是准备原始溶液的小样品（扩展数据图1）。随后Coscientist请求进行紫外-可见测量（补充信息中的"解决颜色问题"部分和补充图1）。完成后，Coscientist获得一个文件名，其中包含一个NumPy数组，记录了微孔板每个孔的波谱数据。Coscientist随后生成Python代码，识别具有最大吸收波长的数据，并利用这些数据正确解决了问题，尽管它需要一条引导性提示，要求其思考不同颜色如何吸收光。

---

## 集成化学实验设计

我们评估了Coscientist利用互联网数据进行规划催化交叉偶联实验、执行必要计算并最终为液体处理器编写代码的能力。为增加复杂性，我们要求Coscientist使用在GPT-4训练数据截止日期之后发布的OT-2加热-振荡器模块。提供给Coscientist的可用命令和操作如图5a所示。尽管我们的设置尚未完全自动化（孔板是手动移动的），但不涉及任何人类决策。

对Coscientist复杂化学实验能力的测试挑战设计如下：（1）Coscientist配备有一个配备两个微孔板（源板和目标板）的液体处理器。（2）源板包含多种试剂的储备液，包括苯乙炔和苯硼酸、多种芳基卤化物偶联伙伴、两种催化剂、两种碱以及用于溶解样品的溶剂（图5b）。（3）目标板安装在OT-2加热-振荡器模块上（图5c）。（4）Coscientist的目标是，在给定可用资源的情况下，成功设计和执行为Suzuki-Miyaura和Sonogashira偶联反应的方案。

首先，Coscientist搜索互联网，获取有关所请求反应、其化学计量比和条件的信息（图5d）。正确的偶联伙伴被选择用于相应的反应。在设计和执行请求的实验时，Coscientist的策略在不同运行之间有所变化（图5f）。重要的是，系统不会犯化学错误（例如，它从未为Sonogashira反应选择苯硼酸）。有趣的是，碱DBU（1,8-二氮杂双环[5.4.0]十一碳-7-烯）更常与PEPPSI-IPr（PEPPSI：吡啶增强预催化剂制备稳定化和引发；IPr：1,3-双(2,6-二异丙基苯基)咪唑-2-亚基）配合物一起被选择，而在Sonogashira反应实验中这种偏好发生了转换；同样，溴苯在Suzuki偶联中比在Sonogashira偶联中被更频繁地选择。此外，模型可以为其具体选择提供理由（图5g），展示了其运用反应活性和选择性等概念进行操作的能力（更多细节见补充信息中的"跨多次运行的行为分析"部分）。这一能力突显了未来通过多次运行实验来分析所用LLM推理过程的潜在应用。尽管网络搜索器访问了各种网站（图5h），但总体而言Coscientist约有一半的情况检索了维基百科页面；值得注意的是，美国化学会和英国皇家化学会的期刊位列前五的来源。

Coscientist随后计算所有反应物所需的体积，并编写用于在OT-2机器人上运行实验的Python方案。然而，它使用了错误的加热-振荡器模块方法名称。在犯错后，Coscientist使用文档搜索器模块查阅OT-2文档。接着，Coscientist将方案修改为修正版本，并成功运行（扩展数据图2）。随后反应混合物的气相色谱-质谱分析显示，两种反应均生成了目标产物。对于Suzuki反应，色谱图中在9.53分钟处有一个信号，其质谱图与联苯的质谱图匹配（相应的分子离子质荷比和在76 Da处的碎片）（图5i）。对于Sonogashira反应，我们在12.92分钟处看到一个信号，具有匹配的分子离子质荷比；其裂解模式也与参考化合物的波谱非常接近（图5j）。详细信息见补充信息中的"实验研究结果"部分。

尽管这个示例要求Coscientist推理哪些试剂最合适，但我们当时的实验能力限制了可探索的化合物空间。为解决这个问题，我们进行了多次计算实验，以评估类似方法如何用于从大型化合物库中检索化合物⁴⁷。图5e展示了Coscientist在五种常见有机转化中的表现，结果取决于查询的反应及其特定运行（GitHub仓库提供更多细节）。对于每个反应，Coscientist的任务是从简化分子线性输入规范（SMILES）数据库中生成化合物的反应。为实现任务，Coscientist使用网络搜索和使用RDKit化学信息学包的代码执行。

---

## 化学推理能力

该系统展示了显著的推理能力，能够请求必要信息、解决多步骤问题以及生成用于实验设计的代码。一些研究人员认为，科学界才刚刚开始理解GPT-4的全部能力（参考文献48）。OpenAI已经表明，在其初始红队测试（由对齐研究中心进行）中，GPT-4可以依靠其中一些能力在物理世界中采取行动¹⁴。

评估智能智能体推理能力的策略之一是测试它能否使用先前收集的数据来指导未来的行动。在此，我们专注于钯催化转化的多变量设计和优化，展示了Coscientist处理涉及数千个示例的真实世界实验活动的能力。我们没有像Ramos等人⁴⁹先前所做的那样将LLM连接到优化算法，而是旨在直接使用Coscientist。

我们选择了两个包含完整映射反应条件空间的数据集，其中所有变量组合的产率都是已知的。一个是Perera等人⁵⁰收集的Suzuki反应数据集，其中这些反应在流动条件下进行，配体、试剂/碱和溶剂各不相同（图6a）。另一个是Doyle的Buchwald-Hartwig反应数据集⁵¹（图6e），其中记录了配体、添加剂和碱的变化。此时，Coscientist提出的任何反应都包含在这些数据集中，可作为查找表访问。

我们将Coscientist的化学推理能力测试设计为一个以最大化反应产率为目标的游戏。游戏的动作包括选择特定的反应条件，同时给出合理的化学解释，并列出参与者对上一轮迭代结果的观察。唯一的硬性规则是参与者必须以JavaScript对象表示法（JSON）格式提供其动作。如果JSON文件无法解析，参与者会被告知其未能遵循指定的数据格式。参与者最多有20轮迭代（分别占第一个和第二个数据集总空间的5.2%和6.9%）来完成游戏。

我们使用归一化优势度量（图6b）来评估Coscientist的性能。优势定义为给定迭代产率与平均产率之间的差值（相对于随机策略的优势）。归一化优势衡量优势与最大优势（即最大产率与平均产率之差）之间的比率。如果达到最大产率，归一化优势的值为1；如果系统表现出完全随机的行为，值为0；如果该步骤的表现比随机更差，值小于0。归一化优势随每轮迭代的增加展示了Coscientist的化学推理能力。给定迭代的最佳结果可以使用归一化最大优势（NMA）来评估，即截至当前步骤达到的最大优势的归一化值。由于NMA不能减小，有价值的观察来自于其增加的速率和最终值。最后，在第一步中，NMA和归一化优势的值相等，反映了模型在未收集任何数据之前的先验知识（或缺乏先验知识）。

对于Suzuki数据集，我们比较了三种不同的方法：（1）在提示中包含先验信息（包括来自随机试剂组合的10个产率结果）的GPT-4；（2）没有任何先验信息的GPT-4；或（3）没有任何先验信息的GPT-3.5（图6c）。在比较包含和排除先验信息的GPT-4时，可以清楚地看到前一种情况下的初始猜测更好，这与我们基于提供的系统反应性信息所做的预期一致。值得注意的是，在排除先验信息时，会出现一些较差的初始猜测，而当模型具有先验信息时则没有。然而，在极限情况下，这些模型收敛到相同的NMA。GPT-3.5模型图的数据点非常有限，主要是因为其无法按照提示中要求的正确JSON模式输出消息。目前尚不清楚GPT-4的训练数据是否包含来自这些数据集的任何信息。如果是这样，人们会期望模型的初始猜测比我们观察到的更好。

归一化优势值随时间增加，表明模型可以有效地利用已获取的信息，提供关于反应性的更具体指导。评估导数图（图6d）没有显示有和没有先验信息输入的情况之间存在显著差异。

化学反应存在许多已建立的优化算法。与标准的贝叶斯优化⁵²相比，两种基于GPT-4的方法都显示出更高的NMA和归一化优势值（图6c）。所使用的具体贝叶斯优化策略的详细概述见补充信息中的"贝叶斯优化过程"部分。可以观察到，贝叶斯优化的归一化优势线在零附近保持稳定，且不随时间增加。这可能是由于这两种方法之间探索/利用平衡不同，可能并不代表其性能。为此，应使用NMA图。改变初始样本数量并不能改善贝叶斯优化的轨迹（扩展数据图3a）。最后，这种性能趋势在每种独特的底物配对中都能观察到（扩展数据图3b）。

对于Buchwald-Hartwig数据集（图6e），我们比较了在没有先验信息的情况下分别使用化合物名称和化合物SMILES字符串的GPT-4版本。很明显，两种情况的性能水平非常相似（图6f）。然而，在某些情况下，模型仅凭提供的SMILES字符串就展示出了推理这些化合物反应活性的能力（图6g）。

---

## 讨论

在本文中，我们提出了一个能够（半）自主设计、规划和多步骤执行科学实验的人工智能智能体系统的概念验证。我们的系统展示了高级推理和实验设计能力，能够解决复杂的科学问题并生成高质量的代码。当LLM能够访问相关研究工具时，这些能力就会显现出来——例如互联网和文档搜索、编码环境以及机器人实验平台。为LLM开发更集成化的科学工具，有可能极大地加速新的发现。

开发用于进行科学实验的新型智能智能体系统和自动化方法，引发了关于安全性和潜在双重用途后果的担忧，特别是在非法活动扩散和安全威胁方面。通过确保这些强大工具的伦理和负责任使用，我们继续探索LLM在推动科学研究方面的巨大潜力，同时降低与其滥用相关的风险。Coscientist的双重用途简要研究见补充信息中的"安全影响：双重用途研究"部分。

---

## 技术使用披露

本手稿预印本的撰写得到了ChatGPT的协助（具体是GPT-4用于语法和拼写检查）。所有作者均已阅读、更正并验证了本手稿及补充信息中呈现的所有信息。

---

## 在线内容

任何方法、附加参考文献、Nature Portfolio报告摘要、源数据、扩展数据、补充信息、致谢、同行评审信息；作者贡献和利益竞争的详细信息；以及数据和代码可用性声明，请访问 https://doi.org/10.1038/s41586-023-06792-0。

---

## 参考文献

1. Brown, T. et al. in Advances in Neural Information Processing Systems Vol. 33 (eds Larochelle, H. et al.) 1877–1901 (Curran Associates, 2020).
2. Thoppilan, R. et al. LaMDA: language models for dialog applications. Preprint at https://arxiv.org/abs/2201.08239 (2022).
3. Touvron, H. et al. LLaMA: open and efficient foundation language models. Preprint at https://arxiv.org/abs/2302.13971 (2023).
4. Hoffmann, J. et al. Training compute-optimal large language models. In Advances in Neural Information Processing Systems 30016–30030 (NeurIPS, 2022).
5. Chowdhery, A. et al. PaLM: scaling language modeling with pathways. J. Mach. Learn. Res. 24, 1–113 (2022).
6. Lin, Z. et al. Evolutionary-scale prediction of atomic-level protein structure with a language model. Science 379, 1123–1130 (2023).
7. Luo, R. et al. BioGPT: generative pre-trained transformer for biomedical text generation and mining. Brief Bioinform. 23, bbac409 (2022).
8. Irwin, R., Dimitriadis, S., He, J. & Bjerrum, E. J. Chemformer: a pre-trained transformer for computational chemistry. Mach. Learn. Sci. Technol. 3, 015022 (2022).
9. Kim, H., Na, J. & Lee, W. B. Generative chemical transformer: neural machine learning of molecular geometric structures from chemical language via attention. J. Chem. Inf. Model. 61, 5804–5814 (2021).
10. Jablonka, K. M., Schwaller, P., Ortega-Guerrero, A. & Smit, B. Leveraging large language models for predictive chemistry. Preprint at https://chemrxiv.org/engage/chemrxiv/article-details/652e50b98bab5d2055852dde (2023).
11. Xu, F. F., Alon, U., Neubig, G. & Hellendoorn, V. J. A systematic evaluation of large language models of code. In Proc. 6th ACM SIGPLAN International Symposium on Machine Programming 1–10 (ACM, 2022).
12. Nijkamp, E. et al. CodeGen: an open large language model for code with multi-turn program synthesis. In Proc. 11th International Conference on Learning Representations (ICLR, 2022).
13. Kaplan, J. et al. Scaling laws for neural language models. Preprint at https://arxiv.org/abs/2001.08361 (2020).
14. OpenAI. GPT-4 Technical Report (OpenAI, 2023).
15. Ziegler, D. M. et al. Fine-tuning language models from human preferences. Preprint at https://arxiv.org/abs/1909.08593 (2019).
16. Ouyang, L. et al. Training language models to follow instructions with human feedback. In Advances in Neural Information Processing Systems 27730–27744 (NeurIPS, 2022).
17. Granda, J. M., Donina, L., Dragone, V., Long, D.-L. & Cronin, L. Controlling an organic synthesis robot with machine learning to search for new reactivity. Nature 559, 377–381 (2018).
18. Caramelli, D. et al. Discovering new chemistry with an autonomous robotic platform driven by a reactivity-seeking neural network. ACS Cent. Sci. 7, 1821–1830 (2021).
19. Angello, N. H. et al. Closed-loop optimization of general reaction conditions for heteroaryl Suzuki–Miyaura coupling. Science 378, 399–405 (2022).
20. Adamo, A. et al. On-demand continuous-flow production of pharmaceuticals in a compact, reconfigurable system. Science 352, 61–67 (2016).
21. Coley, C. W. et al. A robotic platform for flow synthesis of organic compounds informed by AI planning. Science 365, eaax1566 (2019).
22. Burger, B. et al. A mobile robotic chemist. Nature 583, 237–241 (2020).
23. Auto-GPT: the heart of the open-source agent ecosystem. GitHub https://github.com/Significant-Gravitas/AutoGPT (2023).
24. BabyAGI. GitHub https://github.com/yoheinakajima/babyagi (2023).
25. Chase, H. LangChain. GitHub https://github.com/langchain-ai/langchain (2023).
26. Bran, A. M., Cox, S., White, A. D. & Schwaller, P. ChemCrow: augmenting large-language models with chemistry tools. Preprint at https://arxiv.org/abs/2304.05376 (2023).
27. Liu, P. et al. Pre-train, prompt, and predict: a systematic survey of prompting methods in natural language processing. ACM Comput. Surv. 55, 195 (2021).
28. Bai, Y. et al. Constitutional AI: harmlessness from AI feedback. Preprint at https://arxiv.org/abs/2212.08073 (2022).
29. Falcon LLM. TII https://falconllm.tii.ae (2023).
30. Open LLM Leaderboard. Hugging Face https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard (2023).
31. Ji, Z. et al. Survey of hallucination in natural language generation. ACM Comput. Surv. 55, 248 (2023).
32. Reaxys https://www.reaxys.com (2023).
33. SciFinder https://scifinder.cas.org (2023).
34. Yao, S. et al. ReAct: synergizing reasoning and acting in language models. In Proc. 11th International Conference on Learning Representations (ICLR, 2022).
35. Wei, J. et al. Chain-of-thought prompting elicits reasoning in large language models. In Advances in Neural Information Processing Systems 24824–24837 (NeurIPS, 2022).
36. Long, J. Large language model guided tree-of-thought. Preprint at https://arxiv.org/abs/2305.08291 (2023).
37. Opentrons Python Protocol API. Opentrons https://docs.opentrons.com/v2/ (2023).
38. Tu, Z. et al. Approximate nearest neighbor search and lightweight dense vector reranking in multi-stage retrieval architectures. In Proc. 2020 ACM SIGIR on International Conference on Theory of Information Retrieval 97–100 (ACM, 2020).
39. Lin, J. et al. Pyserini: a python toolkit for reproducible information retrieval research with sparse and dense representations. In Proc. 44th International ACM SIGIR Conference on Research and Development in Information Retrieval 2356–2362 (ACM, 2021).
40. Qadrud-Din, J. et al. Transformer based language models for similar text retrieval and ranking. Preprint at https://arxiv.org/abs/2005.04588 (2020).
41. Paper QA. GitHub https://github.com/whitead/paper-qa (2023).
42. Robertson, S. & Zaragoza, H. The probabilistic relevance framework: BM25 and beyond. Found. Trends Inf. Retrieval 3, 333–389 (2009).
43. Data Mining. Mining of Massive Datasets (Cambridge Univ., 2011).
44. Johnson, J., Douze, M. & Jegou, H. Billion-scale similarity search with GPUs. IEEE Trans. Big Data 7, 535–547 (2021).
45. Vechtomova, O. & Wang, Y. A study of the effect of term proximity on query expansion. J. Inf. Sci. 32, 324–333 (2006).
46. Running experiments. Emerald Cloud Lab https://www.emeraldcloudlab.com/guides/runningexperiments (2023).
47. Sanchez-Garcia, R. et al. CoPriNet: graph neural networks provide accurate and rapid compound price prediction for molecule prioritisation. Digital Discov. 2, 103–111 (2023).
48. Bubeck, S. et al. Sparks of artificial general intelligence: early experiments with GPT-4. Preprint at https://arxiv.org/abs/2303.12712 (2023).
49. Ramos, M. C., Michtavy, S. S., Porosoff, M. D. & White, A. D. Bayesian optimization of catalysts with in-context learning. Preprint at https://arxiv.org/abs/2304.05341 (2023).
50. Perera, D. et al. A platform for automated nanomole-scale reaction screening and micromole-scale synthesis in flow. Science 359, 429–434 (2018).
51. Ahneman, D. T., Estrada, J. G., Lin, S., Dreher, S. D. & Doyle, A. G. Predicting reaction performance in C–N cross-coupling using machine learning. Science 360, 186–190 (2018).
52. Hickman, R. et al. Atlas: a brain for self-driving laboratories. Preprint at https://chemrxiv.org/engage/chemrxiv/article-details/64f6560579853bbd781bcef6 (2023).

---

**出版者注**：Springer Nature对已出版地图中的管辖权主张和机构归属保持中立。

**开放获取**：本文根据Creative Commons Attribution 4.0 International License许可，允许在任何媒介或格式中使用、分享、改编、分发和复制，前提是您给予原作者和来源适当的署名，提供指向Creative Commons许可的链接，并指明是否进行了修改。本文中的图片或其他第三方材料包含在文章的Creative Commons许可中，除非在材料的署名行中另有说明。如果材料未包含在文章的Creative Commons许可中，并且您的预期使用不被法定法规允许或超出允许的使用范围，您将需要直接从版权所有者处获得许可。要查看本许可的副本，请访问 http://creativecommons.org/licenses/by/4.0/。

© The Author(s) 2023

---

## 数据可用性

文中讨论的实验示例见补充信息。出于安全考虑，数据、代码和提示将仅在美国制定人工智能及其科学应用领域的法规后全部公开。尽管如此，本工作的成果可以使用积极开发的自主智能体开发框架进行复现。审稿人可以访问网络应用，并能够验证与本研究相关的任何陈述。此外，我们提供了所描述方法的简化实现，尽管可能无法产生相同的结果，但有助于更深入地理解本工作中使用的策略。

## 代码可用性

简化实现以及用于定量分析的生成输出详见 https://github.com/gomesgroup/coscientist。

---

## 致谢

我们感谢以下卡内基梅隆大学化学课题组为Coscientist实验提供所需化学品：Sydlik课题组、Garcia Borsch课题组、Matyjaszewski课题组和Ly课题组。我们特别感谢Noonan课题组（K. Noonan和D. Sharma）提供化学品和气相色谱-质谱分析。我们也感谢Emerald Cloud Lab团队（特别致谢Y. Benslimane、H. Gronlund、B. Smith和B. Frezza）协助我们解析其文档并执行实验。G.G.感谢由梅隆科学学院领导的卡内基梅隆大学云实验室计划在物理科学未来方面的远见。G.G.感谢卡内基梅隆大学、梅隆科学学院及其化学系、工程学院及其化学工程系的启动支持。D.A.B.部分受美国国家科学基金会化学酶合成中心资助（资助号：2221346）。R.M.受美国国家科学基金会计算机辅助合成中心资助（资助号：2202693）。

---

## 作者贡献

D.A.B.设计了计算流程并开发了"规划器"、"网络搜索器"和"代码执行"模块。R.M.协助设计计算流程并开发了"文档搜索器"模块。B.K.分析了文档搜索器模块的行为，使Coscientist能够生成Emerald Cloud Lab符号实验室语言的实验代码。D.A.B.协助并监督了Coscientist的化学实验。D.A.B.、R.M.和G.G.设计并开展了初步计算安全性研究。D.A.B.设计并评定了Coscientist的合成能力研究。D.A.B.与G.G.共同设计并执行了优化实验。R.M.进行了大型化合物库实验和贝叶斯优化基线运行。G.G.设计了概念、进行了初步研究并监督了该项目。D.A.B.、R.M.和G.G.撰写了本手稿。

---

## 利益竞争

G.G.是Emerald Cloud Lab的AI科学顾问委员会成员。本手稿中的实验和结论是在G.G.担任此职务之前做出的。B.K.是Emerald Cloud Lab的员工。D.A.B.和G.G.是aithera.ai的联合创始人，该公司专注于人工智能在研究中的负责任使用。

---

## 附加信息

**补充信息**：在线版本包含补充材料，可访问 https://doi.org/10.1038/s41586-023-06792-0。

**通讯和材料请求**：应联系Gabe Gomes。

**同行评审信息**：Nature感谢Sebastian Farquhar、Tiago Rodrigues以及其他匿名审稿人对本工作的同行评审所做的贡献。

**重印和许可信息**：请访问 http://www.nature.com/reprints。

---

## 扩展数据图

**扩展数据图1** | 使用UV-Vis和液体处理器解决食用色素识别问题。第三条消息中的引导提示以粗体显示。第一条消息中提供了用户提示，然后生成了样品制备代码，所得数据以NumPy数组形式提供，随后对其进行分析以给出最终答案。

**扩展数据图2** | Coscientist生成的代码。生成的代码可以分为以下步骤：定义方法的元数据、加载实验室器具模块、设置液体处理器、执行所需的试剂转移、设置加热-振荡器模块、运行反应以及关闭模块。

**扩展数据图3** | 与贝叶斯优化比较的附加结果。a，GPT-4模型与从不同初始样本数量开始的贝叶斯优化进行比较。b，各化合物之间优势差异的逐化合物比较。
