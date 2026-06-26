# HuggingGPT：使用ChatGPT及其在Hugging Face上的伙伴解决AI任务

Yongliang Shen¹,²,\*, Kaitao Song²,\*,†, Xu Tan², Dongsheng Li², Weiming Lu¹,†, Yueting Zhuang¹,†

浙江大学¹, 微软亚洲研究院²

{syl, luwm, yzhuang}@zju.edu.cn, {kaitaosong, xuta, dongsli}@microsoft.com

https://github.com/microsoft/JARVIS

## 摘要

解决涉及不同领域和模态的复杂AI任务是迈向通用人工智能的关键一步。尽管有大量适用于各种领域和模态的AI模型，但它们无法自主处理复杂的AI任务。考虑到大语言模型（LLM）在语言理解、生成、交互和推理方面展现出的卓越能力，我们主张LLM可以作为控制器来管理现有AI模型，以解决复杂的AI任务，而语言则作为赋能此过程的通用接口。基于这一理念，我们提出了HuggingGPT，一个由LLM驱动的智能体，它利用LLM（如ChatGPT）连接机器学习社区（如Hugging Face）中的各种AI模型来解决AI任务。具体来说，我们在接收到用户请求时使用ChatGPT进行任务规划，根据Hugging Face上可用的模型功能描述选择模型，使用所选AI模型执行每个子任务，并根据执行结果总结响应。通过利用ChatGPT强大的语言能力和Hugging Face丰富的AI模型，HuggingGPT可以处理跨不同模态和领域的广泛复杂AI任务，并在语言、视觉、语音及其他挑战性任务上取得令人印象深刻的结果，这为实现通用人工智能开辟了一条新道路。

## 1 引言

大语言模型（LLM）[1, 2, 3, 4, 5, 6]，如ChatGPT，由于其在各种自然语言处理（NLP）任务上的卓越表现，引起了学术界和工业界的广泛关注。基于大规模文本语料库的大规模预训练和人类反馈强化学习[2]，LLM在语言理解、生成和推理方面展现出卓越的能力。LLM的强大能力也推动了许多新兴研究课题（例如，上下文学习[1, 7, 8]、指令学习[9, 10, 11, 12, 13, 14]和思维链提示[15, 16, 17, 18]）进一步探索LLM的巨大潜力，并为我们推进通用人工智能带来了无限可能。

尽管取得了这些巨大成功，当前的LLM技术仍然不完善，在构建先进AI系统的道路上还面临一些紧迫的挑战。我们从以下几个方面进行讨论：1）受限于文本生成的输入和输出形式，当前的LLM缺乏处理视觉和语音等复杂信息的能力，尽管它们在NLP任务上取得了显著成就；2）在现实场景中，一些复杂的任务通常由多个子任务组成，因此需要多个模型的调度和协作，这也超出了语言模型的能力范围；3）对于某些具有挑战性的任务，LLM在零样本或少样本设置下表现出色，但仍然弱于某些专家模型（例如，微调模型）。如何解决这些问题可能是LLM迈向通用人工智能的关键一步。

在本文中，我们指出，为了处理复杂的AI任务，LLM应该能够与外部模型协调以利用它们的能力。因此，关键问题是如何选择合适的中间件来桥接LLM和AI模型之间的连接。为了解决这个问题，我们注意到每个AI模型都可以通过总结其功能以语言形式进行描述。因此，我们引入了一个概念："语言作为LLM与AI模型协作的通用接口"。换句话说，通过将这些模型描述融入提示中，LLM可以被视为管理AI模型的大脑，如规划、调度和协作。因此，这种策略使LLM能够调用外部模型来解决AI任务。然而，当将多个AI模型集成到LLM中时，另一个挑战出现了：解决大量AI任务需要收集大量高质量的模型描述，而这又需要大量的提示工程。巧合的是，我们注意到一些公共机器学习社区通常提供广泛适用的模型，并带有定义良好的模型描述，用于解决特定的AI任务，如语言、视觉和语音。这些观察给我们带来了一些启发：我们能否通过基于语言的接口，将LLM（如ChatGPT）与公共ML社区（如GitHub、Hugging Face¹等）连接起来，以解决复杂的AI任务？

在本文中，我们提出了一个名为HuggingGPT的LLM驱动智能体，用于自主处理各种复杂的AI任务。它连接LLM（即ChatGPT）和ML社区（即Hugging Face），并能处理来自不同模态的输入。更具体地说，LLM充当大脑：一方面，它根据用户请求分解任务，另一方面，根据模型描述为任务分配合适的模型。通过执行模型并整合规划任务中的结果，HuggingGPT可以自主完成复杂的用户请求。如图1所示，HuggingGPT的整个过程可以分为四个阶段：

- **任务规划**：使用ChatGPT分析用户请求以理解其意图，并将其分解为可能可解决的任务。
- **模型选择**：为了解决规划好的任务，ChatGPT根据模型描述选择托管在Hugging Face上的专家模型。
- **任务执行**：调用并执行每个选定的模型，并将结果返回给ChatGPT。
- **响应生成**：最后，利用ChatGPT整合所有模型的预测并为用户生成响应。

得益于这样的设计，HuggingGPT可以自动从用户请求中生成计划并使用外部模型，使其能够集成多模态感知能力并处理各种复杂的AI任务。更值得注意的是，这种流水线使HuggingGPT能够持续吸收特定任务专家的能力，促进AI能力的增长和可扩展性。

总的来说，我们的贡献可以总结如下：

1. 为了互补大语言模型和专家模型的优势，我们提出了HuggingGPT及其模型间协作协议。HuggingGPT将LLM作为规划和决策的大脑，并自动调用和执行每个特定任务的专家模型，为设计通用AI解决方案提供了新途径。
2. 通过将Hugging Face Hub及其大量特定任务模型集成到ChatGPT周围，HuggingGPT能够处理涵盖多种模态和领域的通用AI任务。通过模型的开放协作，HuggingGPT可以为用户提供多模态和可靠的对话服务。
3. 我们指出了任务规划和模型选择在HuggingGPT（以及自主智能体）中的重要性，并制定了一些实验评估来衡量LLM在规划和模型选择方面的能力。
4. 在语言、视觉、语音和跨模态等多个具有挑战性的AI任务上的广泛实验，证明了HuggingGPT在理解和解决来自多种模态和领域的复杂任务方面的能力和巨大潜力。

## 2 相关工作

近年来，自然语言处理（NLP）领域被大语言模型（LLM）的出现所革命[1, 2, 3, 4, 5, 19, 6]，以GPT-3[1]、GPT-4[20]、PaLM[3]和LLaMa[6]等模型为代表。由于其庞大的语料库和密集的训练计算，LLM在零样本和少样本任务以及更复杂的任务（如数学问题和常识推理）中展示了令人印象深刻的能力。为了扩展大语言模型（LLM）的范围，超越文本生成，当前研究可分为两个分支：1）一些工作设计了统一的 multimodal 语言模型来解决各种AI任务[21, 22, 23]。例如，Flamingo[21]结合了冻结的预训练视觉和语言模型进行感知和推理。BLIP-2[22]利用Q-Former协调语言和视觉语义，Kosmos-1[23]将视觉输入纳入文本序列以融合语言和视觉输入。2）最近，一些研究者开始研究在LLM中集成工具或模型的使用[24, 25, 26, 27, 28]。Toolformer[24]是开创性工作，它在文本序列中引入外部API标记，促进LLM访问外部工具的能力。随后，许多工作将LLM扩展到涵盖视觉模态。Visual ChatGPT[26]将视觉基础模型（如BLIP[29]和ControlNet[30]）与LLM融合。Visual Programming[31]和ViperGPT[25]通过使用编程语言将视觉查询解析为可解释的步骤（表示为Python代码），将LLM应用于视觉对象。关于相关工作的更多讨论见附录B。

与这些方法不同，HuggingGPT在以下方面向更通用的AI能力迈进：1）HuggingGPT使用LLM作为控制器，将用户请求路由到专家模型，有效结合了LLM的语言理解能力与其他专家模型的专业知识；2）HuggingGPT的机制使其能够通过LLM组织模型间的协作，处理任何模态或任何领域的任务。得益于HuggingGPT中任务规划的设计，我们的系统可以自动有效地生成任务流程并解决更复杂的问题；3）HuggingGPT提供了一种更灵活的模型选择方法，它基于模型描述分配和编排任务。通过仅提供模型描述，HuggingGPT可以持续且方便地集成来自AI社区的多样专家模型，而无需改变任何结构或提示设置。这种开放和持续的方式使我们离实现通用人工智能更近了一步。

## 3 HuggingGPT

HuggingGPT是一个用于解决AI任务的协作系统，由一个大语言模型（LLM）和来自ML社区的众多专家模型组成。其工作流程包括四个阶段：任务规划、模型选择、任务执行和响应生成，如图2所示。给定一个用户请求，采用LLM作为控制器的HuggingGPT将自动部署整个工作流程，从而协调和执行专家模型以完成目标。表1展示了HuggingGPT中详细的提示设计。在以下子节中，我们将介绍每个阶段的设计。

### 3.1 任务规划

通常，在现实场景中，用户请求通常包含一些复杂的意图，因此需要编排多个子任务来完成目标。因此，我们将任务规划作为HuggingGPT的第一阶段，旨在使用LLM分析用户请求，然后将其分解为结构化任务的集合。此外，我们要求LLM确定这些分解任务的依赖关系和执行顺序，以建立它们之间的连接。为了增强LLM中任务规划的效果，HuggingGPT采用了提示设计，包括基于规范的指令和基于演示的解析。我们在以下段落中介绍这些细节。

**基于规范的指令** 为了更好地表示用户请求的预期任务并将其用于后续阶段，我们期望LLM通过遵循特定规范（例如，JSON格式）来解析任务。因此，我们设计了标准化的任务模板并指示LLM通过槽填充进行任务解析。如表1所示，任务解析模板包含四个槽（"task"、"id"、"dep"和"args"），分别表示任务名称、唯一标识符、依赖关系和参数。每个槽的更多细节可以在模板描述中找到（见附录A.1.1）。通过遵循这些任务规范，HuggingGPT可以自动使用LLM分析用户请求并相应解析任务。

**基于演示的解析** 为了更好地理解任务规划的意图和标准，HuggingGPT在提示中加入了多个演示。每个演示由一个用户请求及其对应输出组成，输出表示预期的解析任务序列。通过纳入任务间的依赖关系，这些演示帮助HuggingGPT理解任务之间的逻辑连接，促进准确确定执行顺序和识别资源依赖关系。我们演示的详细信息见表1。此外，为了支持更复杂的场景（例如，多轮对话），我们通过追加以下指令将聊天日志包含在提示中："为了辅助任务规划，聊天历史记录以{{ Chat Logs }}的形式提供，您可以在其中追踪用户提及的资源并将其纳入任务规划阶段。"这里{{ Chat Logs }}代表之前的聊天日志。这种设计使HuggingGPT能够更好地管理上下文并在多轮对话中回应用户请求。

### 3.2 模型选择

在任务规划之后，HuggingGPT进入将任务与模型匹配的阶段，即为解析出的任务列表中的每个任务选择最合适的模型。为此，我们使用模型描述作为语言接口来连接每个模型。更具体地说，我们首先从ML社区（如Hugging Face）收集专家模型的描述，然后采用动态的上下文任务-模型分配机制为任务选择模型。这种策略支持增量式模型接入（只需提供专家模型的描述），并且可以更开放、更灵活地使用ML社区。下一段将介绍更多细节。

**上下文任务-模型分配** 我们将任务-模型分配表述为一个单选题问题，其中可用模型作为给定上下文中的选项呈现。通常，基于提示中提供的用户指令和任务信息，HuggingGPT能够为每个解析出的任务选择最合适的模型。然而，由于最大上下文长度的限制，在一个提示中包含所有相关模型的信息是不可行的。为了缓解这个问题，我们首先根据任务类型过滤模型，以选择与当前任务匹配的模型。在这些选定的模型中，我们根据它们在Hugging Face上的下载量²进行排序，然后选择前K个模型作为候选。这种策略可以大大减少提示中的令牌使用量，并有效为每个任务选择合适的模型。

### 3.3 任务执行

一旦为解析出的任务分配了特定模型，下一步就是执行该任务（即进行模型推理）。在此阶段，HuggingGPT将自动将这些任务参数输入模型，执行这些模型以获得推理结果，然后将结果发送回LLM。有必要在此阶段强调资源依赖问题。由于前置任务的输出是动态产生的，HuggingGPT在启动任务之前也需要动态指定任务所依赖的资源。因此，在此阶段建立具有资源依赖关系的任务之间的连接是具有挑战性的。

**资源依赖** 为了解决这个问题，我们使用一个独特的符号"<resource>"来维护资源依赖关系。具体来说，HuggingGPT将前置任务生成的资源标识为<resource>-task_id，其中task_id是前置任务的ID。在任务规划阶段，如果某些任务依赖于先前执行任务的输出（例如，task_id），HuggingGPT将此符号（即<resource>-task_id）设置在参数中对应的资源子字段中。然后在任务执行阶段，HuggingGPT动态地将此符号替换为前置任务生成的资源。因此，这种策略使HuggingGPT能够在任务执行期间高效地处理资源依赖关系。

此外，对于剩余没有任何资源依赖关系的任务，我们将直接并行执行这些任务，以进一步提高推理效率。这意味着如果多个任务满足前置依赖条件，它们可以同时执行。此外，我们提供混合推理端点来部署这些模型，以加速和保证计算稳定性。更多细节请参考附录A.1.3。

### 3.4 响应生成

在所有任务执行完成后，HuggingGPT需要生成最终响应。如表1所示，HuggingGPT在此阶段将前三个阶段（任务规划、模型选择和任务执行）的所有信息整合成简洁的摘要，包括规划的任务列表、为任务选择的模型以及模型的推理结果。

其中最重要的是推理结果，这是HuggingGPT做出最终决策的关键点。这些推理结果以结构化格式呈现，例如目标检测模型中的带有检测概率的边界框、问答模型中的答案分布等。HuggingGPT允许LLM接收这些结构化推理结果作为输入，并以友好的人类语言形式生成响应。此外，LLM不仅仅是简单聚合结果，而是生成主动响应用户请求的响应，并提供具有置信度的可靠决策。

## 4 实验

### 4.1 设置

在我们的实验中，我们采用了GPT模型系列的gpt-3.5-turbo、text-davinci-003和gpt-4变体作为主要的LLM，这些模型可通过OpenAI API³公开访问。为了实现LLM更稳定的输出，我们将解码温度设置为0。此外，为了规范LLM输出以满足预期格式（例如，JSON格式），我们在格式约束（例如，"{"和"}"）上设置了logit_bias为0.2。我们在表1中提供了为任务规划、模型选择和响应生成阶段设计的详细提示，其中{{variable}}表示需要在使用前填入相应文本的插槽。

### 4.2 定性结果

图1和图2展示了HuggingGPT的两个演示。在图1中，用户请求包含两个子任务：描述图像和计算物体数量。针对该请求，HuggingGPT规划了三个任务：图像分类、图像描述和目标检测，并分别启动了google/vit[32]、nlpconnet/vit-gpt2-image-captioning[33]和facebook/detr-resnet-101[34]模型。最后，HuggingGPT整合了模型推理的结果并生成响应（描述图像并提供包含物体的数量）给用户。

一个更详细的例子如图2所示。在这个案例中，用户的请求包括三个任务：检测示例图像中人物的姿态、基于该姿态和指定文本生成新图像、以及创建描述该图像的语音。HuggingGPT将这些解析为六个任务，包括姿态检测、基于姿态的文本到图像生成、目标检测、图像分类、图像描述和文本到语音。我们观察到HuggingGPT可以正确编排任务之间的执行顺序和资源依赖关系。例如，基于姿态的文本到图像任务必须在姿态检测之后进行，并将其输出作为输入。此后，HuggingGPT为每个任务选择合适的模型，并将模型执行的结果综合成最终响应。更多演示请参阅附录A.3。

### 4.3 定量评估

在HuggingGPT中，任务规划在整个工作流程中起着关键作用，因为它决定了在后续流水线中将执行哪些任务。因此，我们认为任务规划的质量可以用来衡量LLM作为HuggingGPT中控制器的能力。为此，我们进行了定量评估来衡量LLM的能力。这里我们简化了评估，只考虑任务类型而不考虑其相关参数。为了更好地进行任务规划评估，我们将任务分为三个不同的类别（见表2），并为它们制定不同的指标：

- **单一任务**指只涉及一个任务的请求。我们认为当且仅当任务名称（即"task"）与预测标签完全相同，规划才是正确的。在此上下文中，我们使用F1和准确率作为评估指标。
- **顺序任务**表示用户的请求可以分解为多个子任务的序列。在这种情况下，我们使用F1和归一化编辑距离[35]作为评估指标。
- **图任务**表示用户请求可以分解为有向无环图。考虑到图任务中可能存在多种规划拓扑结构，仅依靠F1分数不足以反映LLM在规划方面的能力。为了解决这个问题，遵循Vicuna[36]的做法，我们采用GPT-4作为评判者来评估规划的正确性。准确率通过评估GPT-4的判断获得，称为GPT-4 Score。关于GPT-4 Score的详细信息见附录A.1.5。

**数据集** 为了进行评估，我们邀请了一些标注员提交请求。我们收集这些数据作为评估数据集。我们使用GPT-4生成任务规划作为伪标签，涵盖单一、顺序和图任务。此外，我们邀请了一些专家标注员对一些复杂请求（46个样本）进行任务规划标注，作为高质量的人工标注数据集。我们还计划改进该数据集的质量和数量，以进一步协助评估LLM的规划能力，这仍是未来的工作。关于该数据集的更多细节见附录A.2。使用该数据集，我们对各种LLM进行了任务规划的实验评估，包括Alpaca-7b[37]、Vicuna-7b[36]和GPT模型。

**性能** 表3、4和5分别展示了HuggingGPT在GPT-4标注数据集的三个类别上的规划能力。我们观察到GPT-3.5表现出更突出的规划能力，在所有类型的用户请求上都优于开源LLM Alpaca-7b和Vicuna-7b。具体来说，在更复杂的任务（如顺序和图任务）中，GPT-3.5展现了绝对的领先优势。这些结果也表明任务规划的评估可以反映LLM作为控制器的能力。因此，我们相信发展技术来提高LLM在任务规划方面的能力非常重要，我们将其作为未来的研究方向。

此外，我们在高质量人工标注数据集上进行了实验，以获得更精确的评估。表6报告了人工标注数据集上的比较结果。这些结果与上述结论一致，突出了更强大的LLM在任务规划中表现出更好的性能。此外，我们比较了人工标注和GPT-4标注的结果。我们发现，尽管GPT-4优于其他LLM，但与人工标注相比仍存在显著差距。这些观察进一步强调了增强LLM规划能力的重要性。

### 4.4 消融研究

如前文默认设置中所述，我们应用少样本演示来增强LLM理解用户意图和解析任务序列的能力。为了更好地研究演示对我们框架的影响，我们从两个角度进行了一系列消融研究：演示的数量和演示的多样性。表7报告了不同演示多样性下的规划结果。我们观察到，增加演示的多样性可以适度提高LLM进行规划的性能。此外，图3展示了不同演示数量下任务规划的结果。我们可以发现，添加一些演示可以略微提高模型性能，但当数量超过4个演示时，这种改进将受到限制。未来，我们将继续探索更多能够在不同阶段提升LLM能力的要素。

### 4.5 人工评估

除了客观评估外，我们还邀请人类专家在实验中进行主观评估。我们收集了130个多样化请求，以评估HuggingGPT在各个阶段的性能，包括任务规划、模型选择和最终响应生成。我们设计了三个评估指标，即通过率、合理性和成功率。每个指标的定义见附录A.1.6。结果报告在表8中。从表8中，我们可以观察到类似的结论：GPT-3.5在不同阶段（从任务规划到响应生成阶段）都以较大幅度显著优于Alpaca-13b和Vicuna-13b等开源LLM。这些结果表明我们的客观评估与人工评估一致，并进一步证明了在自主智能体框架中需要强大的LLM作为控制器的必要性。

## 5 局限性

HuggingGPT为设计AI解决方案提出了一种新范式，但我们想指出仍然存在一些局限或改进空间：1）HuggingGPT中的规划严重依赖LLM的能力。因此，我们不能保证生成的计划始终可行且最优。因此，探索优化LLM以增强其规划能力的方法至关重要；2）效率是我们框架中的一个共同挑战。为了建立这样一个具有任务自动化能力的协作系统（即HuggingGPT），它严重依赖强大的控制器（如ChatGPT）。然而，HuggingGPT在整个工作流程中需要与LLM进行多次交互，从而增加了生成响应的时间成本；3）令牌长度是使用LLM时的另一个常见问题，因为最大令牌长度始终是有限的。尽管一些工作已将最大长度扩展到32K，但如果我们想连接大量模型，这仍然是不够的。因此，如何简洁有效地总结模型描述也值得探索；4）不稳定性主要是由于LLM通常不可控。尽管LLM擅长生成，但在预测过程中仍可能无法遵守指令或给出错误答案，导致程序工作流程中出现异常。如何减少推理过程中的这些不确定性，应在系统设计中加以考虑。

## 6 结论

在本文中，我们提出了一个名为HuggingGPT的系统来解决AI任务，以语言作为接口连接LLM与AI模型。我们系统的原理是：LLM可以被视为管理AI模型的控制器，并且可以利用来自ML社区（如Hugging Face）的模型来自动解决用户的不同请求。通过利用LLM在理解和推理方面的优势，HuggingGPT可以剖析用户的意图并将其分解为多个子任务。然后，基于专家模型描述，HuggingGPT能够为每个任务分配最合适的模型，并整合不同模型的结果以生成最终响应。通过利用来自机器学习社区的大量AI模型的能力，HuggingGPT在解决具有挑战性的AI任务方面展示了巨大潜力，从而为实现通用人工智能铺平了新的道路。

## 致谢

我们感谢Hugging Face团队帮助我们改进GitHub项目和网络演示。此外，我们也感谢Bei Li、Kai Shen、Meiqi Chen、Qingyao Guo、Yichong Leng、Yuancheng Wang、Dingyao Yu在数据标注方面的贡献，以及Wenqi Zhang、Wen Wang、Zeqi Tan在论文修改方面的贡献。

本工作部分得到中央高校基本科研业务费（No. 226-2023-00060）、浙江省重点研发计划（No. 2023C01152）、国家重点研发计划（No. 2018AAA0101900）以及教育部数字图书馆工程研究中心的支持。

## 参考文献

[1] Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, and Dario Amodei. Language Models are Few-Shot Learners. In NeurIPS, 2020.

[2] Long Ouyang, Jeff Wu, Xu Jiang, Diogo Almeida, Carroll L. Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, John Schulman, Jacob Hilton, Fraser Kelton, Luke Miller, Maddie Simens, Amanda Askell, Peter Welinder, Paul F. Christiano, Jan Leike, and Ryan Lowe. Training language models to follow instructions with human feedback. CoRR, abs/2203.02155, 2022.

[3] Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Paul Barham, Hyung Won Chung, Charles Sutton, Sebastian Gehrmann, and others. Palm: Scaling language modeling with pathways. ArXiv, abs/2204.02311, 2022.

[4] Susan Zhang, Stephen Roller, Naman Goyal, Mikel Artetxe, Moya Chen, Shuohui Chen, Christopher Dewan, Mona Diab, Xian Li, Xi Victoria Lin, Todor Mihaylov, Myle Ott, Sam Shleifer, Kurt Shuster, Daniel Simig, Punit Singh Koura, Anjali Sridhar, Tianlu Wang, and Luke Zettlemoyer. Opt: Open Pre-trained Transformer Language Models. ArXiv, abs/2205.01068, 2022.

[5] Aohan Zeng, Xiao Liu, Zhengxiao Du, Zihan Wang, Hanyu Lai, Ming Ding, Zhuoyi Yang, Yifan Xu, Wendi Zheng, Xiao Xia, Weng Lam Tam, Zixuan Ma, Yufei Xue, Jidong Zhai, Wenguang Chen, Zhiyuan Liu, Peng Zhang, Yuxiao Dong, and Jie Tang. Glm-130b: An Open Bilingual Pre-trained Model. ICLR 2023 poster, 2023.

[6] Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, Aurelien Rodriguez, Armand Joulin, Edouard Grave, and Guillaume Lample. Llama: Open and Efficient Foundation Language Models. ArXiv, abs/2302.13971, 2023.

[7] Sang Michael Xie, Aditi Raghunathan, Percy Liang, and Tengyu Ma. An Explanation of In-context Learning as Implicit Bayesian Inference. ICLR 2022 Poster, 2022.

[8] Sewon Min, Xinxi Lyu, Ari Holtzman, Mikel Artetxe, Mike Lewis, Hannaneh Hajishirzi, and Luke Zettlemoyer. Rethinking the Role of Demonstrations: What Makes In-Context Learning Work? In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP). Association for Computational Linguistics, 2022.

[9] Jason Wei, Maarten Bosma, Vincent Zhao, Kelvin Guu, Adams Wei Yu, Brian Lester, Nan Du, Andrew M. Dai, and Quoc V Le. Finetuned language models are zero-shot learners. In International Conference on Learning Representations, 2022.

[10] Yizhong Wang, Swaroop Mishra, Pegah Alipoormolabashi, Yeganeh Kordi, Amirreza Mirzaei, Atharva Naik, Arjun Ashok, Arut Selvan Dhanasekaran, Anjana Arunkumar, David Stap, Eshaan Pathak, Giannis Karamanolakis, Haizhi Gary Lai, Ishan Virendrabhai Purohit, Ishani Mondal, Jacob William Anderson, Kirby C. Kuznia, Krima Doshi, Kuntal Kumar Pal, Maitreya Patel, Mehrad Moradshahi, Mihir Parmar, Mirali Purohit, Neeraj Varshney, Phani Rohitha Kaza, Pulkit Verma, Ravsehaj Singh Puri, Rushang Karia, Savan Doshi, Shailaja Keyur Sampat, Siddhartha Mishra, Sujan Reddy A, Sumanta Patro, Tanay Dixit, Xudong Shen, Chitta Baral, Yejin Choi, Noah A. Smith, Hannaneh Hajishirzi, and Daniel Khashabi. Super-NaturalInstructions: Generalization via Declarative Instructions on 1600+ NLP Tasks. In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing (EMNLP). Association for Computational Linguistics, 2022.

[11] S. Iyer, Xiaojuan Lin, Ramakanth Pasunuru, Todor Mihaylov, Daniel Simig, Ping Yu, Kurt Shuster, Tianlu Wang, Qing Liu, Punit Singh Koura, Xian Li, Brian O'Horo, Gabriel Pereyra, Jeff Wang, Christopher Dewan, Asli Celikyilmaz, Luke Zettlemoyer, and Veselin Stoyanov. Opt-IML: Scaling Language Model Instruction Meta Learning through the Lens of Generalization. ArXiv, abs/2212.12017, 2022.

[12] Hyung Won Chung, Le Hou, Shayne Longpre, Barret Zoph, Yi Tay, William Fedus, Eric Li, Xuezhi Wang, Mostafa Dehghani, Siddhartha Brahma, Albert Webson, Shixiang Shane Gu, Zhuyun Dai, Mirac Suzgun, Xinyun Chen, Aakanksha Chowdhery, Sharan Narang, Gaurav Mishra, Adams Yu, Vincent Y. Zhao, Yanping Huang, Andrew M. Dai, Hongkun Yu, Slav Petrov, Ed H. Chi, Jeff Dean, Jacob Devlin, Adam Roberts, Denny Zhou, Quoc V. Le, and Jason Wei. Scaling instruction-finetuned language models. CoRR, abs/2210.11416, 2022.

[13] Yizhong Wang, Yeganeh Kordi, Swaroop Mishra, Alisa Liu, Noah A. Smith, Daniel Khashabi, and Hannaneh Hajishirzi. Self-instruct: Aligning language model with self generated instructions, 2022.

[14] Shayne Longpre, Le Hou, Tu Vu, Albert Webson, Hyung Won Chung, Yi Tay, Denny Zhou, Quoc V. Le, Barret Zoph, Jason Wei, and Adam Roberts. The flan collection: Designing data and methods for effective instruction tuning. CoRR, abs/2301.13688, 2023.

[15] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed Chi, Quoc V Le, and Denny Zhou. Chain of Thought Prompting Elicits Reasoning in Large Language Models. In Conference on Neural Information Processing Systems (NeurIPS), 2022.

[16] Takeshi Kojima, Shixiang (Shane) Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. Large Language Models are Zero-Shot Reasoners. In Conference on Neural Information Processing Systems (NeurIPS), 2022.

[17] Luyu Gao, Aman Madaan, Shuyan Zhou, Uri Alon, Pengfei Liu, Yiming Yang, Jamie Callan, and Graham Neubig. Pal: Program-aided Language Models. ArXiv, abs/2211.10435, 2022.

[18] Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc V Le, Ed H. Chi, Sharan Narang, Aakanksha Chowdhery, and Denny Zhou. Self-Consistency Improves Chain of Thought Reasoning in Language Models. ICLR 2023 poster, abs/2203.11171, 2023.

[19] Jason Wei, Yi Tay, Rishi Bommasani, Colin Raffel, Barret Zoph, Sebastian Borgeaud, Dani Yogatama, Maarten Bosma, Denny Zhou, Donald Metzler, Ed H. Chi, Tatsunori Hashimoto, Oriol Vinyals, Percy Liang, Jeff Dean, and William Fedus. Emergent abilities of large language models. CoRR, abs/2206.07682, 2022.

[20] OpenAI. Gpt-4 technical report, 2023.

[21] Jean-Baptiste Alayrac, Jeff Donahue, Pauline Luc, Antoine Miech, Iain Barr, Yana Hasson, Karel Lenc, Arthur Mensch, Katie Millican, Malcolm Reynolds, Roman Ring, Eliza Rutherford, Serkan Cabi, Tengda Han, Zhitao Gong, Sina Samangooei, Marianne Monteiro, Jacob Menick, Sebastian Borgeaud, Andrew Brock, Aida Nematzadeh, Sahand Sharifzadeh, Mikolaj Binkowski, Ricardo Barreira, Oriol Vinyals, Andrew Zisserman, and Karen Simonyan. Flamingo: a visual language model for few-shot learning, 2022.

[22] Junnan Li, Dongxu Li, S. Savarese, and Steven Hoi. Blip-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models. ArXiv, abs/2301.12597, 2023.

[23] Shaohan Huang, Li Dong, Wenhui Wang, Y. Hao, Saksham Singhal, Shuming Ma, Tengchao Lv, Lei Cui, O. Mohammed, Qiang Liu, Kriti Aggarwal, Zewen Chi, Johan Bjorck, Vishrav Chaudhary, Subhojit Som, Xia Song, and Furu Wei. Language Is Not All You Need: Aligning Perception with Language Models. ArXiv, abs/2302.14045, 2023.

[24] Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, M. Lomeli, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language Models Can Teach Themselves to Use Tools. ArXiv, abs/2302.04761, 2023.

[25] Dídac Surís, Sachit Menon, and Carl Vondrick. Vipergpt: Visual inference via python execution for reasoning, 2023.

[26] Chenfei Wu, Sheng-Kai Yin, Weizhen Qi, Xiaodong Wang, Zecheng Tang, and Nan Duan. Visual ChatGPT: Talking, Drawing and Editing with Visual Foundation Models. arXiv, 2023.

[27] Yaobo Liang, Chenfei Wu, Ting Song, Wenshan Wu, Yan Xia, Yu Liu, Yang Ou, Shuai Lu, Lei Ji, Shaoguang Mao, Yun Wang, Linjun Shou, Ming Gong, and Nan Duan. Taskmatrix.ai: Completing tasks by connecting foundation models with millions of apis, 2023.

[28] Yujia Qin, Shengding Hu, Yankai Lin, Weize Chen, Ning Ding, Ganqu Cui, Zheni Zeng, Yufei Huang, Chaojun Xiao, Chi Han, Yi Ren Fung, Yusheng Su, Huadong Wang, Cheng Qian, Runchu Tian, Kunlun Zhu, Shihao Liang, Xingyu Shen, Bokai Xu, Zhen Zhang, Yining Ye, Bowen Li, Ziwei Tang, Jing Yi, Yuzhang Zhu, Zhenning Dai, Lan Yan, Xin Cong, Yaxi Lu, Weilin Zhao, Yuxiang Huang, Junxi Yan, Xu Han, Xian Sun, Dahai Li, Jason Phang, Cheng Yang, Tongshuang Wu, Heng Ji, Zhiyuan Liu, and Maosong Sun. Tool learning with foundation models, 2023.

[29] Junnan Li, Dongxu Li, Caiming Xiong, and Steven C. H. Hoi. Blip: Bootstrapping Language-Image Pre-training for Unified Vision-Language Understanding and Generation. In International Conference on Machine Learning (ICML), pages 12888–12900, 2022.

[30] Lvmin Zhang and Maneesh Agrawala. Adding Conditional Control to Text-to-Image Diffusion Models. ArXiv, abs/2302.05543, 2023.

[31] Tanmay Gupta and Aniruddha Kembhavi. Visual Programming: Compositional visual reasoning without training. arXiv, abs/2211.11559, 2022.

[32] Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, and Neil Houlsby. An image is worth 16x16 words: Transformers for image recognition at scale, 2021.

[33] Ankur Kumar. The illustrated image captioning using transformers. ankur3107.github.io, 2022.

[34] Nicolas Carion, Francisco Massa, Gabriel Synnaeve, Nicolas Usunier, Alexander Kirillov, and Sergey Zagoruyko. End-to-end object detection with transformers, 2020.

[35] A. Marzal and E. Vidal. Computation of normalized edit distance and applications. IEEE Transactions on Pattern Analysis and Machine Intelligence, 15(9):926–932, 1993.

[36] Wei-Lin Chiang, Zhuohan Li, Zi Lin, Ying Sheng, Zhanghao Wu, Hao Zhang, Lianmin Zheng, Siyuan Zhuang, Yonghao Zhuang, Joseph E. Gonzalez, Ion Stoica, and Eric P. Xing. Vicuna: An open-source chatbot impressing gpt-4 with 90%* chatgpt quality, March 2023.

[37] Rohan Taori, Ishaan Gulrajani, Tianyi Zhang, Yann Dubois, Xuechen Li, Carlos Guestrin, Percy Liang, and Tatsunori B. Hashimoto. Stanford alpaca: An instruction-following llama model. https://github.com/tatsu-lab/stanford_alpaca, 2023.

## 附录A

### A.1 更多细节

在本节中，我们将呈现HuggingGPT每个阶段设计的更多细节。

#### A.1.1 任务规划模板

为了格式化解析后的任务，我们定义了模板 `[{"task": task, "id": task_id, "dep": dependency_task_ids, "args": {"text": text, "image": URL, "audio": URL, "video": URL}}]`，包含四个槽："task"、"id"、"dep"和"args"。表9展示了每个槽的定义。

**表9：任务规划中解析任务各槽位的定义**

| 名称 | 定义 |
|------|------|
| "task" | 表示解析任务类型。涵盖语言、视觉、视频、音频等方面的不同任务。HuggingGPT当前支持的任务列表见表13。 |
| "id" | 任务规划的唯一标识符，用于引用依赖任务及其生成的资源。 |
| "dep" | 定义执行所需的前置任务。仅当所有前置依赖任务完成后，该任务才会启动。 |
| "args" | 包含任务执行所需参数列表。包含三个子字段，根据任务类型填充文本、图像和音频资源。这些资源来自用户请求或依赖任务生成的资源。不同任务类型的对应参数类型见表13。 |

#### A.1.2 模型描述

通常，Hugging Face Hub托管有详细模型描述的专家模型，这些描述通常由开发者提供。这些描述涵盖了模型的各个方面，如其功能、架构、支持的语言和领域、许可及其他相关细节。这些全面的模型描述在辅助HuggingGPT的决策中起着关键作用。通过评估用户请求并将其与模型描述进行比较，HuggingGPT可以有效地确定给定任务的最合适模型。

#### A.1.3 系统部署中的混合端点

理想的情况是我们只使用云服务上的推理端点（如Hugging Face）。然而，在某些情况下，我们必须部署本地推理端点，例如当某些模型的推理端点不存在、推理耗时较长或网络访问受限时。为了保持系统的稳定性和效率，HuggingGPT允许我们在本地拉取并运行一些常见或耗时的模型。本地推理端点速度快但覆盖的模型较少，而云服务（如Hugging Face）上的推理端点则相反。因此，本地端点的优先级高于云端推理端点。只有当匹配的模型未在本地部署时，HuggingGPT才会在Hugging Face等云端端点上运行模型。总的来说，我们认为如何为HuggingGPT或其他自主智能体设计和部署具有更好稳定性的系统，在未来将非常重要。

#### A.1.4 任务列表

截至目前，HuggingGPT已支持24个AI任务，涵盖语言、视觉、语音等领域。表13展示了HuggingGPT支持的任务列表的详细信息。

#### A.1.5 GPT-4评分

遵循Vicuna[36]使用的评估方法，我们采用GPT-4作为评估器来评估LLM的规划能力。更详细地说，我们在提示中包含用户请求和LLM规划的任务列表，然后让GPT-4判断任务列表是否准确，并提供理由。为了引导GPT-4做出正确判断，我们设计了一些任务指南：1）任务在支持的任务列表中（见表13）；2）规划的任务列表能够解决用户请求；3）任务之间的逻辑关系和顺序是合理的。在提示中，我们还补充了几个任务规划的正面和反面演示，为GPT-4提供参考。GPT-4评分的提示见表10。我们进一步强调，尽管GPT-4评分显示出高度相关性，但它并不总是正确的。因此，我们也期望探索更可靠的指标来评估LLM在规划方面的能力。

**表10：GPT-4评分的提示设计**

> 作为评判者，您的任务是评估AI助手是否根据用户的请求正确规划了任务。为此，请仔细检查用户请求和助手的输出，然后使用"Yes"或"No"做出决定（"Yes"表示规划准确，"No"表示规划不准确）。此外，请使用以下结构为您的选择提供理由：{"choice": "yes"/"no", "reason": "您选择的理由"}。请遵循以下指南：1. 任务必须从以下选项中选择：{{ Available Task List }}。2. 请注意任务之间存在逻辑关系和顺序。3. 仅关注任务规划的正确性，不考虑任务参数。正面示例：{{Positive Demos}} 负面示例：{{Negative Demos}} 当前用户请求：{{Input}} AI助手的输出：{{Output}} 您的判断：

#### A.1.6 人工评估

为了更好地与人类偏好对齐，我们邀请了三位人类专家评估HuggingGPT的不同阶段。首先，我们从Hugging Face的任务列表中选择了3-5个任务，然后基于所选任务手动创建用户请求。我们将丢弃那些无法从所选任务生成新请求的样本。总共，我们通过使用不同种子进行随机抽样，获得了130个多样化的用户请求。基于生成的样本，我们评估了LLM在不同阶段（如任务规划、模型选择和响应生成）的性能。这里，我们设计了三个评估指标：

- **通过率**：判断规划的任务图或选择的模型能否成功执行；
- **合理性**：评估生成的任务序列或选择的工具是否以合理的方式与用户请求对齐；
- **成功率**：验证最终结果是否满足用户请求。

三位人类专家根据我们精心设计的指标对提供的数据进行标注，然后计算平均值以获得最终分数。

### A.2 任务规划评估数据集

如前所述，我们创建了两个用于评估任务规划的数据集。这里我们提供关于这些数据集的更多细节。总共，我们收集了3,497个多样化用户请求。由于为每个请求标注任务规划工作量较大，我们利用GPT-4的能力进行标注。最后，这些自动标注的请求可以分为三类：单一任务（1,450个请求）、顺序任务（1,917个请求）和图任务（130个请求）。为了更可靠的评估，我们还构建了一个人工标注数据集。我们邀请了一些专家标注员标注了一些复杂请求，共包括46个样本。目前，人工标注数据集包括24个顺序任务和22个图任务。关于GPT-4标注和人工标注数据集的详细统计信息见表11。

**表11：任务规划评估数据集的统计信息**

| 数据集 | 按类型划分的请求数量 | 请求长度 | 任务数量 |
|--------|---------------------|---------|---------|
| | 单一 | 顺序 | 图 | 最大 | 平均 | 最大 | 平均 |
| GPT-4标注 | 1,450 | 1,917 | 130 | 52 | 13.26 | 13 | 1.82 |
| 人工标注 | - | 24 | 22 | 95 | 10.20 | 12 | 2.00 |

### A.3 案例研究

#### A.3.1 各种任务的案例研究

通过任务规划和模型选择，HuggingGPT这一多模型协作系统使LLM扩展了更广泛的能力。在这里，我们广泛评估了HuggingGPT在各种多模态任务上的表现，图4和图5展示了一些选定的案例。凭借强大的LLM和众多专家模型的合作，HuggingGPT有效处理了涵盖语言、图像、音频和视频等多种模态的任务。其能力涵盖多种任务形式，如检测、生成、分类和问答。

#### A.3.2 复杂任务的案例研究

有时，用户请求可能包含多个隐含任务或需要多方面的信息，这种情况下我们不能依赖单个专家模型来解决。为了克服这一挑战，HuggingGPT通过任务规划组织多个模型的协作。如图6、7和8所示，我们进行了实验评估HuggingGPT在复杂任务情况下的有效性：

- 图6展示了HuggingGPT在多轮对话场景中应对复杂任务的能力。用户将一个复杂请求分成几个步骤，通过多轮交互达到最终目标。我们发现HuggingGPT可以通过任务规划阶段的对话上下文管理来跟踪用户请求的上下文状态。此外，HuggingGPT展示了在对话场景中访问用户引用的资源并熟练解决任务间依赖关系的能力。
- 图7显示，对于一个简单的请求如"尽可能详细地描述图像"，HuggingGPT可以将其分解为五个相关任务，即图像描述、图像分类、目标检测、分割和视觉问答任务。HuggingGPT分配专家模型处理每个任务，从不同角度收集图像信息。最后，LLM整合这些多样化的信息，为用户提供全面详细的描述。
- 图8展示了一个用户请求可能包含多个任务的两种案例。在这些案例中，HuggingGPT首先通过编排多个专家模型的工作来执行用户请求的所有任务，然后让LLM聚合模型推理结果来响应用户。

总之，HuggingGPT建立了LLM与外部专家模型的协作，在各种复杂任务形式上展现了有前景的性能。

#### A.3.3 更多场景的案例研究

我们在这里展示更多案例，以说明HuggingGPT处理具有任务资源依赖、多模态、多资源等现实场景的能力。为了清晰展示HuggingGPT的工作流程，我们还提供了任务规划和任务执行阶段的结果。

- 图9展示了HuggingGPT在任务间存在资源依赖时的操作过程。在此案例中，HuggingGPT可以根据用户的抽象请求解析出具体任务，包括姿态检测、图像描述和基于姿态的条件图像生成任务。此外，HuggingGPT有效识别了任务#3与任务#1、#2之间的依赖关系，并在依赖任务完成后将任务#1和#2的推理结果注入任务#3的输入参数中。
- 图10展示了HuggingGPT在音频和视频模态上的对话能力。在这两个案例中，它展示了HuggingGPT分别通过专家模型完成用户请求的文本到音频和文本到视频任务。在上面的案例中，两个模型并行执行（同时生成音频和生成视频）；在下面的案例中，两个模型串行执行（先从图像生成文本，然后基于文本生成音频）。这进一步验证了HuggingGPT可以组织模型间的协作以及任务间的资源依赖关系。
- 图11展示了HuggingGPT整合多个用户输入资源进行简单推理的能力。我们可以发现，即使有多个资源，HuggingGPT也能将主任务分解为多个基本任务，最终整合来自多个模型的多次推理结果以获得正确答案。

## 附录B 关于相关工作的更多讨论

ChatGPT及其后续变体GPT-4的出现，在LLM和AI领域掀起了一场革命性的技术浪潮。尤其是在过去的几周里，我们也见证了一些实验性但也非常有趣的LLM应用，如AutoGPT⁴、AgentGPT⁵、BabyAGI⁶等。因此，我们也对这些工作进行了一些讨论，并从多个维度（包括场景、规划、工具）进行比较，如表12所示。

**表12：HuggingGPT与其他自主智能体的比较**

| 名称 | 场景 | 规划 | 工具 |
|------|------|------|------|
| BabyAGI | 日常 | 迭代规划 | - |
| AgentGPT | 日常 | - | - |
| AutoGPT | 日常 | 迭代规划 | 网络搜索、代码执行器等 |
| HuggingGPT | AI领域 | 全局规划 | Hugging Face中的模型 |

**场景** 目前，这些实验性智能体（如AutoGPT、AgentGPT和BabyAGI）主要用于解决日常请求。而HuggingGPT则专注于利用Hugging Face的能力解决AI领域的任务（如视觉、语言、语音等）。因此，HuggingGPT可以被视为一个更专业的智能体。总的来说，用户可以根据需求（如日常请求或专业领域）选择最合适的智能体，或通过定义知识、规划策略和工具包来自定义自己的智能体。

**规划** BabyAGI、AgentGPT和AutoGPT都可以被视为自主智能体，它们为任务自动化提供了一些解决方案。对于这些智能体，它们都采用了逐步思考的方式，通过使用LLM迭代生成下一个任务。此外，AutoGPT在每次任务生成时还采用了一个额外的反思模块，用于检查当前预测的任务是否合适。与这些应用相比，HuggingGPT采用全局规划策略，在一次查询中获得整个任务队列。很难判断哪种更好，因为每种方法都有其缺陷，且都严重依赖LLM的能力，尽管现有的LLM并非专门为任务规划设计。例如，结合反思的迭代规划需要大量的LLM查询，如果某一步生成了错误预测，整个工作流程可能会进入无限循环。而对于全局规划，尽管它可以在一次查询中为每个用户请求生成解决方案，但仍不能保证每一步的正确性或整个计划的最优性。因此，迭代规划和全局规划各有优点，可以相互借鉴以减轻各自的缺点。此外，值得注意的一点是，任务规划的难度也与任务范围呈线性相关。随着任务范围的扩大，控制器预测精确计划变得更加困难。因此，优化控制器（即LLM）的任务规划能力对于构建自主智能体至关重要。

**工具** 在这些智能体中，AutoGPT是主要涉及使用其他工具的。更具体地说，AutoGPT主要使用一些常见工具（如网络搜索、代码执行器），而HuggingGPT则利用ML社区（如Hugging Face）的专家模型。因此，AutoGPT的任务范围更广但不适合更专业的问题，而HuggingGPT更专业化，专注于解决更复杂的AI任务。因此，LLM中使用的工具范围将是任务深度和任务范围之间的权衡。此外，我们也注意到一些用于LLM应用的行业产品（如ChatGPT插件⁷）和开发者工具（如LangChain⁸、HuggingFace Transformer Agent⁹、Semantic Kernel¹⁰）。我们相信这些快速发展也将促进社区探索如何更好地将LLM与外部工具集成。

总的来说，HuggingGPT也可以被视为一个自主智能体。与那些主要使用GPT模型为用户请求生成解决方案的实验性智能体相比，HuggingGPT系统地提出了一个包含四个阶段的清晰流水线：任务规划、模型选择、任务执行和响应生成。这样的流水线可以有效提高解决用户请求的成功率。此外，HuggingGPT还引入了全局规划策略来分解用户请求，从而实现任务自动化。更进一步，HuggingGPT是一个协作系统，充分利用来自ML社区的专家模型的能力来解决AI任务，展示了使用外部工具的巨大潜力。与这些智能体相比，HuggingGPT使我们能够更有效地在专业领域解决任务，并且可以轻松扩展到任何垂直领域。未来，我们将继续增强HuggingGPT，使其具有更强大的能力，以开发具有无限可能的多功能自主智能体。

---

¹ https://huggingface.co/models

² 在某种程度上，我们认为下载量可以反映模型的受欢迎程度和质量。

³ https://platform.openai.com/

⁴ https://github.com/Significant-Gravitas/Auto-GPT

⁵ https://github.com/reworkd/AgentGPT

⁶ https://github.com/yoheinakajima/babyagi

⁷ https://openai.com/blog/chatgpt-plugins

⁸ https://python.langchain.com/

⁹ https://huggingface.co/docs/transformers/transformers_agents

¹⁰ https://github.com/microsoft/semantic-kernel

---

## 附表与附图

### 表1：HuggingGPT中提示设计的详细信息

在提示中，我们设置了一些可注入的插槽，如{{ Demonstrations }}和{{ Candidate Models }}。这些插槽在输入LLM之前统一替换为相应的文本。

**任务规划提示**

> #1 任务规划阶段 - AI助手对用户输入进行任务解析，生成一个任务列表，格式如下：[{"task": task, "id": task_id, "dep": dependency_task_ids, "args": {"text": text, "image": URL, "audio": URL, "video": URL}}]。"dep"字段表示生成当前任务所依赖的新资源的前置任务的ID。标签"<resource>-task_id"表示来自对应task_id依赖任务的生成文本、图像、音频或视频。任务必须从以下选项中选择：{{ Available Task List }}。请注意任务之间存在逻辑连接和顺序。如果用户输入无法解析，则应提供空的JSON响应。以下是一些供您参考的案例：{{ Demonstrations }}。为了辅助任务规划，聊天历史记录以{{ Chat Logs }}的形式提供，您可以在其中追踪用户提及的资源并将其纳入任务规划阶段。

**模型选择提示**

> #2 模型选择阶段 - 给定用户请求和调用命令，AI助手帮助用户从模型列表中选择合适的模型来处理用户请求。AI助手仅输出最合适模型的模型ID。输出必须采用严格的JSON格式：{"id": "id", "reason": "您选择该模型的详细理由"}。我们有一个供您选择的模型列表{{ Candidate Models }}，请从列表中选择一个模型。

**响应生成提示**

> #4 响应生成阶段 - 根据输入和推理结果，AI助手需要描述过程和结果。之前的阶段可归纳为 - 用户输入：{{ User Input }}，任务规划：{{ Tasks }}，模型选择：{{ Model Assignment }}，任务执行：{{ Predictions }}。您必须首先以直接的方式回答用户的请求。然后以第一人称描述任务过程，并向用户展示您的分析和模型推理结果。如果推理结果包含文件路径，必须告知用户完整的文件路径。如果结果中没有任何内容，请告知无法完成。

### 表2：不同任务类型的任务规划评估

| 任务类型 | 图表示例 | 评估指标 |
|---------|---------|---------|
| 单一任务 | Task 1 | Precision, Recall, F1, Accuracy |
| 顺序任务 | Task 1 → Task 2 → Task 3 | Precision, Recall, F1, Edit Distance |
| 图任务 | Task 1 → Task 2 → Task 3 → Task 4 / Task 5 → Task 6 | Precision, Recall, F1, GPT-4 Score |

### 表3：单一任务评估

| LLM | Acc ↑ | Pre ↑ | Recall ↑ | F1 ↑ |
|-----|-------|-------|----------|------|
| Alpaca-7b | 6.48 | 35.60 | 6.64 | 4.88 |
| Vicuna-7b | 23.86 | 45.51 | 26.51 | 29.44 |
| GPT-3.5 | 52.62 | 62.12 | 52.62 | 54.45 |

### 表4：顺序任务评估

| LLM | ED ↓ | Pre ↑ | Recall ↑ | F1 ↑ |
|-----|------|-------|----------|------|
| Alpaca-7b | 0.83 | 22.27 | 23.35 | 22.80 |
| Vicuna-7b | 0.80 | 19.15 | 28.45 | 22.89 |
| GPT-3.5 | 0.54 | 61.09 | 45.15 | 51.92 |

### 表5：图任务评估

| LLM | GPT-4 Score ↑ | Pre ↑ | Recall ↑ | F1 ↑ |
|-----|---------------|-------|----------|------|
| Alpaca-7b | 13.14 | 16.18 | 28.33 | 20.59 |
| Vicuna-7b | 19.17 | 13.97 | 28.08 | 18.66 |
| GPT-3.5 | 50.48 | 54.90 | 49.23 | 51.91 |

### 表6：人工标注数据集评估

| LLM | 顺序任务 | 图任务 |
|-----|---------|-------|
| | Acc ↑ | ED ↓ | Acc ↑ | F1 ↑ |
| Alpaca-7b | 0 | 0.96 | 4.17 | 4.17 |
| Vicuna-7b | 7.45 | 0.89 | 10.12 | 7.84 |
| GPT-3.5 | 18.18 | 0.76 | 20.83 | 16.45 |
| GPT-4 | 41.36 | 0.61 | 58.33 | 49.28 |

### 表7：不同演示多样性的任务规划评估

| 演示多样性（#任务类型） | LLM | 单一任务 | 顺序任务 | 图任务 |
|-----------------------|-----|---------|---------|-------|
| | | Acc ↑ | F1 ↑ | ED(%) ↓ | F1 ↑ | F1 ↑ |
| 2 | GPT-3.5 | 43.31 | 48.29 | 71.27 | 32.15 | 43.42 |
| | GPT-4 | 65.59 | 67.08 | 47.17 | 55.13 | 53.96 |
| 6 | GPT-3.5 | 51.31 | 51.81 | 60.81 | 43.19 | 58.51 |
| | GPT-4 | 66.83 | 68.14 | 42.20 | 58.18 | 64.34 |
| 10 | GPT-3.5 | 52.83 | 53.70 | 56.52 | 47.03 | 64.24 |
| | GPT-4 | 67.52 | 71.05 | 39.32 | 60.80 | 66.90 |

### 表8：不同LLM的人工评估

| LLM | 任务规划 | 模型选择 | 响应 |
|-----|---------|---------|------|
| | 通过率 ↑ | 合理性 ↑ | 通过率 ↑ | 合理性 ↑ | 成功率 ↑ |
| Alpaca-13b | 51.04 | 32.17 | - | - | 6.92 |
| Vicuna-13b | 79.41 | 58.41 | - | - | 15.64 |
| GPT-3.5 | 91.22 | 78.47 | 93.89 | 84.29 | 63.08 |

### 表13：HuggingGPT中使用的任务列表

第一列和第二列是相应任务的名称和参数。第三列和第四列提供了一些候选模型示例及其模型描述。

**NLP任务：**
- Text-CLS: text — [cardiffnlp/twitter-roberta-base-sentiment, ...]
- Token-CLS: text — [dslim/bert-base-NER, ...]
- Text2text-Generation: text — [google/flan-t5-xl, ...]
- Summarization: text — [bart-large-cnn, ...]
- Translation: text — [t5-base, ...]
- Question-Answering: text — [deepset/roberta-base-squad2, ...]
- Conversation: text — [PygmalionAI/pygmalion-6b, ...]
- Text-Generation: text — [gpt2, ...]
- Tabular-CLS: text — [matth/flowformer, ...]

**CV任务：**
- Image-to-Text: image — [nlpconnect/vit-gpt2-image-captioning, ...]
- Text-to-Image: image — [runwayml/stable-diffusion-v1-5, ...]
- VQA: text + image — [dandelin/vilt-b32-finetuned-vqa, ...]
- Segmentation: image — [facebook/detr-resnet-50-panoptic, ...]
- DQA: text + image — [impira/layoutlm-document-qa, ...]
- Image-CLS: image — [microsoft/resnet-50, ...]
- Image-to-image: image — [radames/stable-diffusion-v1-5-img2img, ...]
- Object-Detection: image — [facebook/detr-resnet-50, ...]
- ControlNet-SD: image — [lllyasviel/sd-controlnet-canny, ...]

**音频任务：**
- Text-to-Speech: text — [espnet/kan-bayashi_ljspeech_vits, ...]
- Audio-CLS: audio — [TalTechNLP/voxlingua107-epaca-tdnn, ...]
- ASR: audio — [jonatasgrosman/wav2vec2-large-xlsr-53-english, ...]
- Audio-to-Audio: audio — [speechbrain/metricgan-plus-voicebank, ...]

**视频任务：**
- Text-to-Video: text — [damo-vilab/text-to-video-ms-1.7b, ...]
- Video-CLS: video — [MCG-NJU/videomae-base, ...]

---

> **图1：** 语言作为LLM（如ChatGPT）连接大量AI模型（如Hugging Face中的模型）解决复杂AI任务的接口。在此概念中，LLM充当控制器，管理和组织专家模型的协作。LLM首先根据用户请求规划任务列表，然后将专家模型分配给每个任务。专家执行任务后，LLM收集结果并响应用户。

> **图2：** HuggingGPT概述。以LLM（如ChatGPT）为核心控制器，专家模型为执行器，HuggingGPT的工作流程包括四个阶段：1）任务规划：LLM将用户请求解析为任务列表，并确定任务间的执行顺序和资源依赖关系；2）模型选择：LLM根据Hugging Face上专家模型的描述为任务分配适当的模型；3）任务执行：混合端点上的专家模型执行分配的任务；4）响应生成：LLM整合专家的推理结果并生成工作流程日志摘要以响应用户。

> **图3：** 不同演示数量下的任务规划评估。

> **图4：** 各种任务的案例研究（a）— 包括命名实体识别、目标检测、视觉问答、深度估计、文本生成、文本到图像生成。

> **图5：** 各种任务的案例研究（b）— 包括视频生成、音频生成、文档问答、图像到图像生成。

> **图6：** 复杂任务案例研究（a）— 多轮对话中的任务规划与执行。

> **图7：** 复杂任务案例研究（b）— 对"尽可能详细描述图像"请求的综合处理。

> **图8：** 复杂任务案例研究（c）— 多任务请求的规划与执行。

> **图9：** 具有资源依赖性的多模型协作定性分析。

> **图10：** 视频和音频模态下的多模型协作定性分析。

> **图11：** 多源多模型协作定性分析。
