# OpenHands：面向通用型AI软件开发者的开放平台

**发表于 ICLR 2025**

王兴耀¹,¹⁰，李博宣²，宋宇凡²，Frank F. Xu²，唐祥如³，  
诸葛明辰⁶，潘嘉逸⁴，宋悦琪²，Bowen Li，Jaskirat Singh⁷，  
Hoang H. Tran⁸，Li Fuqiang，Ren Ma，Zheng Mingzhang，Bill Qian³，邵彦君³，  
Niklas Muennighoff⁵，Yizhe Zhang，Binyuan Hui⁹，Junyang Lin⁹，  
Robert Brennan¹⁰，Hao Peng¹，Heng Ji¹，Graham Neubig²,¹⁰  

¹ UIUC  ² CMU  ³ Yale  ⁴ UC Berkeley  ⁵ Contextual AI  ⁶ KAUST  ⁷ ANU  
⁸ HCMUT  ⁹ Alibaba  ¹⁰ All Hands AI  

xingyao6@illinois.edu, gneubig@cs.cmu.edu  

## 摘要

软件是人类所拥有的最强大的工具之一；它使熟练的程序员能够以复杂而深刻的方式与世界互动。与此同时，得益于大语言模型（LLM）的进步，与周围环境交互并影响其变化的AI代理也在快速发展。在本文中，我们介绍了OpenHands（原名OpenDevin），一个用于开发强大而灵活的AI代理的平台，这些代理以类似于人类开发者的方式与世界互动：通过编写代码、与命令行交互和浏览网页。我们描述了该平台如何支持新代理的实现、与沙箱环境的安全交互以执行代码、多代理之间的协调以及评估基准的整合。基于我们当前整合的基准，我们对代理在15个具有挑战性的任务上进行了评估，包括软件工程（如SWE-Bench）和网页浏览（如WebArena）等。OpenHands在宽松的MIT许可下发布，是一个涵盖学术界和工业界的社区项目，拥有来自188多位贡献者的超过2100次贡献。

**代码**: https://github.com/All-Hands-AI/OpenHands  
**Slack**: http://bit.ly/OpenHands-Slack  

---

## 1 引言

在大语言模型（LLM；OpenAI 2024b；Team et al. 2023；Jiang et al. 2024；Chang et al. 2024）的驱动下，面向用户的AI系统（如ChatGPT）在执行复杂任务方面变得越来越强大，例如准确响应用户查询、解决数学问题和生成代码。特别是，AI代理——能够感知并作用于外部环境的系统——最近获得了越来越多的研究关注。它们正朝着执行复杂任务的方向发展，如开发软件（Jimenez et al., 2024）、浏览真实世界网站（Zhou et al., 2023a）、做家务（Ahn et al., 2022），甚至进行科学研究（Boiko et al., 2023；Tang et al., 2024a）。

随着AI代理有能力解决复杂问题，它们的开发和评估也变得具有挑战性。最近有许多创建开源框架以促进代理开发的努力（Hong et al., 2023；Chen et al., 2024；Wu et al., 2023）。这些代理框架通常包括：1）代理与外部世界交互的接口（如基于JSON的函数调用或代码执行），2）代理运行的环境，以及3）人机或代理间通信的交互机制。这些框架以各种方式简化和减轻了开发过程（表1，§C）。

在设计AI代理时，我们也可以考虑人类如何与世界互动。人类目前与世界互动的最强大方式是通过软件——软件支撑着我们生活的方方面面，从基本需求的物流到科学、技术和AI本身的进步。鉴于软件的力量，以及围绕其高效开发、使用和部署的现有工具，它为AI代理以复杂方式与世界互动提供了理想的接口。然而，构建能够有效开发软件的代理本身也带来了独特的挑战。我们如何使代理能够有效地在复杂软件系统中创建和修改代码？我们如何为它们提供即时收集信息以调试问题或收集任务所需信息的工具？我们如何确保开发过程安全，避免对用户系统产生负面影响？

在本文中，我们介绍了OpenHands（原名OpenDevin），一个社区驱动的平台，旨在开发通过软件与世界互动的通用型和专精型AI代理¹。它具有以下特点：

（1）一种交互机制，允许用户界面、代理和环境通过强大而灵活的事件流架构进行交互（§2.1）。

（2）一个运行时环境，包含一个带有bash shell的Docker沙箱操作系统、一个网页浏览器和IPython服务器，供代理与之交互（§2.2）。

（3）一个允许代理以类似于真实软件工程师的方式与环境交互的接口（§2.3）。我们为代理提供了以下能力：a）创建和编辑复杂软件，b）在沙箱中执行任意代码，以及c）浏览网站以收集信息。

（4）多代理委派，允许多个专门化的代理协同工作（§2.4）。

（5）评估框架，便于在广泛的任务范围内评估代理（§4）。

重要的是，OpenHands不仅仅是一个概念框架，它还包括一个全面且立即可用的代理、环境和评估实现。截至本文撰写时，OpenHands包含一个拥有超过10个已实现代理的代理中心（§3），包括一个基于CodeAct架构（Wang et al., 2024a）实现的强通用型代理，并增加了网页浏览（ServiceNow）和代码编辑专家（Yang et al., 2024）的扩展。用户交互通过一个基于聊天的用户界面实现，该界面可视化代理的当前操作并允许实时反馈（图1，§D）。此外，评估框架目前支持15个基准测试，我们使用这些基准测试来评估我们的代理（§4）。

OpenHands在允许商业使用的宽松MIT许可下发布，旨在支持学术界和工业界的多样化研究和实际应用。OpenHands已获得了显著的增长，拥有32K GitHub星标，来自188多位贡献者的超过2100次贡献。我们期待OpenHands成为由广泛实践者社区驱动的未来研究创新和多样化应用的催化剂。

> ¹虽然最初受AI软件工程师Devin（Cognition.ai）启发，但OpenHands通过多样的社区贡献已迅速发展为支持远超软件工程的更广泛应用程序。

---

## 2 OpenHands 架构

接下来我们将详细描述OpenHands的使用。具体来说，我们将讨论：1）如何定义和实现一个代理（§2.1），2）每个动作执行如何产生观察结果（§2.2），3）如何可靠地管理和扩展代理常用技能（§2.3），以及4）如何组合多个代理共同解决任务（§2.4）。图2提供了一个概览。

### 2.1 代理定义与实现

代理能够感知环境状态（例如，先前的动作和观察结果），并在解决用户指定任务时产生一个待执行的动作。

**状态与事件流。** 在OpenHands中，状态是一个封装了代理执行所有相关信息的数据结构。该状态的一个关键组成部分是事件流，它是过去动作和观察结果的时间顺序集合，包括代理自身的动作和用户交互（例如，指令、反馈）。除了事件流，状态还包含代理运行所需的辅助信息，如LLM调用的累积成本、跟踪多代理委派的元数据（§2.4）以及其他执行相关参数。

**动作。** 受CodeAct（Wang et al., 2024a）启发，OpenHands通过一组核心通用动作将代理与环境连接起来。`IPythonRunCellAction`和`CmdRunAction`动作使代理能够在沙箱环境（例如，一个安全隔离的Linux操作系统）内执行任意Python代码和bash命令。`BrowserInteractiveAction`使用BrowserGym（Drouin et al., 2024）引入的领域特定浏览语言实现与网页浏览器的交互。选择这些动作是为了提供一套全面而灵活的原语，覆盖人类软件工程师和分析师执行的大多数任务。基于编程语言（PL）的动作空间足够强大和灵活，可以用不同形式的工具（如Python函数、REST API等）执行任何任务，同时保持可靠且易于维护（Wang et al., 2024a）。

这种设计也与需要预定义工具列表的现有工具调用代理（Chase, 2022）兼容。也就是说，用户可以轻松地使用原始动作支持的编程语言定义工具（例如，编写一个用于计算器的Python函数），并通过JSON风格的工具调用体验（Qin et al., 2023）使这些工具对代理可用。此外，框架强大的基于编程语言的原语还使代理能够在缺乏完成任务所需API时自行创建工具（例如，通过生成Python函数，Yuan et al. 2023）。关于这些基于编程语言的核心动作如何组合成多样化的工具集，请参见§2.3。

**观察结果。** 观察结果描述了代理观察到的环境变化（例如，先前动作的执行结果、来自人类用户的文本消息等）。

**实现新代理。** 代理抽象设计得简单而强大，允许用户轻松创建和定制适合各种任务的代理。代理抽象的核心在于`step`函数，它以当前状态作为输入，并根据代理的逻辑生成适当的动作。图3展示了代理抽象的简化示例代码。通过提供这种抽象，OpenHands允许用户专注于定义所需的代理行为和逻辑，而无需担心动作如何执行的底层细节（§2.2）。

### 2.2 代理运行时：动作执行如何产生观察结果

代理运行时提供了一个通用环境，为代理配备了与人类软件开发人员相媲美的动作空间，使OpenHands代理能够处理广泛的软件开发和基于Web的任务，包括复杂的软件开发工作流、数据分析项目、网页浏览任务等。它允许代理访问bash终端来运行代码和命令行工具，利用Jupyter notebook即时编写和执行代码，并与网页浏览器交互以执行基于Web的任务（例如，信息检索）。

**Docker沙箱。** 对于每个任务会话，OpenHands会启动一个安全隔离的Docker容器沙箱，所有来自事件流的动作都在其中执行。OpenHands通过运行在沙箱内部的REST API服务器（即OpenHands动作执行API）连接到沙箱，执行来自事件流的任意动作（如bash命令、Python代码），并将执行结果作为观察结果返回。一个包含用户希望代理处理的文件的可配置工作目录会被挂载到该安全沙箱中，供OpenHands代理访问。

**OpenHands动作执行API。** OpenHands维护一个运行在Docker沙箱内部的API服务器，用于监听来自事件流的动作执行请求。该API服务器维护着：

（1）一个与操作系统环境（由Docker镜像指定）连接的bash shell，用于命令执行。
（2）一个Jupyter IPython服务器，用于处理交互式Python（IPython）代码执行请求，并将执行结果返回给事件流。
（3）一个基于Playwright的Chromium浏览器。该浏览器提供由BrowserGym（ServiceNow；Drouin et al., 2024）定义的一组动作原语，如导航、点击、输入和滚动。完整的动作集详见§J。执行这些动作后，浏览器运行时会提供关于浏览器当前状态的丰富观察结果，包括HTML、DOM、可访问性树（Mozilla）、截图、打开的标签页等。

**支持任意Docker镜像。** OpenHands通过支持基于任意Docker镜像的运行时，允许代理在不同的软件环境下运行各种操作系统。OpenHands实现了一个构建机制，它接收用户提供的任意Docker镜像，并将OpenHands动作执行API安装到该镜像中，以实现代理交互。我们在§F中包含了OpenHands代理运行时的详细描述。

### 2.3 代理技能：可扩展的代理-计算机接口

SWE-Agent（Yang et al., 2024）强调了精心设计的代理-计算机接口（ACI，即针对特定任务的专门工具）在成功解决复杂任务中的重要性。然而，创建、维护和分发大量工具可能是一项艰巨的工程挑战，尤其是当我们希望使这些工具适用于不同的代理实现时（§3）。为了解决这些问题，我们构建了一个AgentSkills库，这是一个旨在增强代理能力的工具箱，提供了通过基本bash命令或Python代码不易获得的实用工具。

**易于创建和扩展工具。** AgentSkills被设计为一个Python包，由不同的实用函数（即工具）组成，这些函数会自动导入到Jupyter IPython环境（§2.2）中。将Python函数定义为工具的简便性降低了社区成员向库贡献新工具的门槛。Python包的通用性也允许不同的代理实现通过我们的核心动作之一`IPythonRunCellAction`（§2.1）轻松利用这些工具。

**纳入标准和理念。** 在AgentSkills库中，我们不旨在包装每一个可能的Python包并重新教授代理它们的用法（例如，LLM已经知道可以读取CSV文件的`pandas`库，所以我们不需要重新创建一个教授代理读取相同文件格式的工具）。我们仅在以下情况下添加新技能：（1）通过直接编写代码不易实现（例如，编辑代码并替换某些行），和/或（2）涉及调用外部模型（例如，调用语音转文本模型，或用于代码编辑的模型（Sanger））。

**当前支持的技能。** AgentSkills库包括改编自SWE-Agent（Yang et al., 2024）和Aider（Gauthier）的文件编辑实用工具，如`edit_file`，它允许修改指定行开始的现有文件；滚动函数`scroll_up`和`scroll_down`用于查看文件的不同部分。它还包含支持阅读多模态文档的工具，如`parse_image`和`parse_pdf`，分别用于使用视觉语言模型（如GPT-4V）从图像中提取信息和从PDF中读取文本。支持的技能完整列表见§I。

### 2.4 代理委派：协作式多代理交互

OpenHands还允许多个代理之间的交互。为此，我们使用了一种特殊的动作类型`AgentDelegateAction`，它使一个代理能够将特定的子任务委派给另一个代理。例如，通用型的CodeActAgent在网页浏览方面支持有限，可以使用`AgentDelegateAction`将网页浏览任务委派给专门的BrowsingAgent，以执行更复杂的浏览活动（如导航网页、点击按钮、提交表单等）。

---

## 3 代理中心：社区贡献的代理集散地

基于我们的代理抽象（§2.1），OpenHands支持广泛的社区贡献的代理实现，供最终用户选择，并作为不同代理任务的基线。

**CodeAct代理。** CodeActAgent是基于CodeAct框架（Wang et al., 2024a）的默认通用型代理。在每一步，代理可以（1）通过自然语言与人类对话以请求澄清、确认等，或者（2）通过执行代码（即CodeAct）来执行任务，包括执行bash命令、Python代码或浏览器专用编程语言（§2.2）。这种通用动作空间允许代理（v1.5及以上版本）执行各种任务，包括编辑文件、浏览网页、运行程序等。

**浏览代理。** 我们实现了一个名为BrowsingAgent的通用型Web代理，作为Web代理任务的简单而有效的基线。该代理类似于WebArena（Zhou et al., 2023a）中的代理，但具有改进的观察结果和操作，仅使用零样本提示。完整提示见§K。

**GPTSwarm代理。** GPTSwarm（Zhuge et al., 2024）开创了使用可优化图来构建代理系统的方法，通过模块化统一了语言代理框架。每个节点代表一个不同的操作，而边定义了协作和通信路径。这种设计允许对节点和边进行自动优化，推动创建多代理系统的进步。

**微代理。** 此外，OpenHands支持创建微代理（micro agent），即专门针对特定任务的代理。微代理重用现有通用型代理（如CodeAct Agent）的大部分实现。它旨在降低代理开发的门槛，社区成员可以分享针对其特定用例效果良好的专门提示。

---

## 4 评估

为了系统地跟踪构建通用型数字代理的进展，如表2所列，我们在OpenHands中集成了15个已建立的基准测试。这些基准测试涵盖软件工程、网页浏览和杂项辅助任务。在本节中，我们将OpenHands与开源可复现基线进行比较，这些基线不会基于基准测试内容进行手动的提示工程。请注意，为简洁起见，本节其余部分我们使用"OH"作为OpenHands的缩写。

### 4.1 结果概览

在OpenHands中，我们的目标是开发能够通过软件接口与世界交互的通用数字代理（如§2.1中描述的代码动作所示）。我们认识到，一个软件代理不仅应在代码编辑方面表现出色，还应在网页浏览和各种辅助任务中表现出色，例如回答关于代码仓库的问题或进行在线研究。

表3展示了一组精选的评估结果。虽然OpenHands代理可能并非在每个类别中都达到顶尖性能，但它们是本着通用性的理念设计的。值得注意的是，相同的CodeAct代理，无需修改其系统提示，在三大任务类别中展现了具有竞争力的性能：软件开发、网页交互和杂项任务。与通常为特定任务类别设计和优化的基线代理相比，这一点尤为重要。

### 4.2 软件工程

接下来，我们在表4中报告专门针对软件工程基准的结果。

**SWE-Bench**（Jimenez et al., 2024）旨在评估代理解决现实世界GitHub问题（如错误报告或功能请求）的能力。代理与仓库交互，并尝试通过文件编辑和代码执行来修复提供的问题。代理修改后的代码仓库会与一组测试套件进行比较，该套件包含了人类开发者针对同一问题修复所添加的新测试。每个测试实例附带一段"提示文本"，包含解决问题的自然语言建议。在本文中，我们报告所有结果时不使用提示文本。一个规范子集SWE-bench Lite是为了促进可访问和高效的测试而创建的。出于成本节约的考虑，我们默认使用该子集进行测试²。**结果。** 如表4所示，我们最新版本的CodeActAgent v1.8，使用claude-3.5-sonnet，与其他开源SWE专家相比，达到了具有竞争力的26%解决率。

#### 4.2.1 HumanEvalFix

**HumanEvalFix**（Muennighoff et al., 2024）要求代理根据提供的测试用例修复给定函数中的错误。这些错误被设计为导致一个或多个测试用例失败。我们专注于该基准的Python子集，并允许模型通过多轮自我调试来解决问题，并结合测试执行的反馈。我们遵循Muennighoff et al.（2024）的设置，使用pass@k（Chen et al., 2021）。**结果。** 在表4中，OpenHands CodeActAgent成功修复了Python分集中79.3%的错误。这显著优于所有非代理方法，几乎是StarCoder2-15B（Lozhkov et al., 2024；Li et al., 2023c）性能的两倍。虽然SWE-Agent达到了87.7%，但Yang et al.（2024）为模型提供了测试数据集中修复其中一个错误的完整成功示例轨迹（"1-shot"），而我们对OpenHands的评估是0-shot。由于HumanEvalFix由人类创建且所有错误都经过仔细验证，在该基准上达到100%是完全可行的，我们将在OpenHands的未来迭代中寻求实现这一目标。

**ML-Bench**（Tang et al., 2024b）评估代理解决跨18个GitHub仓库的机器学习任务的能力。该基准包含跨越169个多样化ML问题的9,641个任务，要求代理根据用户指令生成bash脚本或Python代码。在沙箱环境中，代理可以迭代地执行命令并接收反馈，使其能够逐步理解仓库上下文并满足用户要求。遵循原始论文的设置，我们在ML-Bench的四分之一子集上执行代理评估。

**Gorilla APIBench**（Patil et al., 2023）评估代理使用API的能力。它包含关于TorchHub、TensorHub和HuggingFace的任务。在评估过程中，模型会收到一个与API使用相关的问题，例如"识别一个能够将录音中的口语转换为文本的API"。正确性基于模型的API调用是否在正确的领域内进行评估。

**ToolQA**（Zhuang et al., 2024）评估代理使用外部工具的能力。该基准包括关于各种主题的任务，如航班状态、咖啡价格、Yelp数据和Airbnb数据，需要使用各种工具，如文本工具、数据库工具、数学工具、图形工具、代码工具和系统工具。它具有两个级别：简单和困难。简单问题更侧重于单工具使用，而困难问题强调推理。我们采用简单子集进行评估。

**BioCoder**（Tang et al., 2024c）是一个仓库级别的代码生成基准，评估代理在生物信息学相关任务上的表现，特别是检索和准确利用上下文的能力。原始提示包含代码的相关上下文；然而，在本研究中，我们已将其移除，以展示OpenHands在多轮交互中进行上下文检索、自我调试和推理的能力。BioCoder由157个Python和50个Java函数组成，每个函数针对生物信息学中的特定领域，如蛋白质组学、基因组学和其他专业领域。该基准通过在实际仓库中生成代码来针对现实世界代码，其中相关代码已被屏蔽。

**BIRD**（Li et al., 2023b）是一个面向文本到SQL任务（即将自然语言转换为可执行SQL查询）的基准，旨在模拟现实和大型数据库环境。我们从开发集中选择了300个样本集成到OpenHands中，并在执行准确率上进行评估。此外，我们扩展了设置，允许代理进行多轮交互以得出最终的SQL查询，使其能够通过观察SQL执行的结果来纠正历史结果。

### 4.3 网页浏览

我们在表5中报告了网页浏览基准的评估结果。

**WebArena**（Zhou et al., 2023a）是一个自托管、基于执行的Web代理基准，允许代理自由选择完成给定任务的路径。WebArena包括812个人工策划的任务指令，涵盖各个领域，包括购物、论坛、开发者平台和内容管理系统。**结果。** 从表5可以看出，我们的BrowsingAgent在使用带有领域通用提示技术的LLM的代理中取得了具有竞争力的性能。

**MiniWoB++**（Liu et al., 2018）是一个交互式网页基准，具有内置奖励函数。任务在125个不同的简约网页界面上合成初始化。与WebArena不同，任务相对简单，没有页面变化，所需步骤较少，并提供低层次的逐步任务指导。请注意，它包含一部分需要视觉能力才能成功处理的环境，许多现有工作选择只关注任务的子集（Kim et al., 2024；Li et al., 2023d；Shaw et al., 2023）。尽管如此，我们仍报告完整集的性能，并且只包含在完整集上评估的基线。

### 4.4 杂项辅助任务

杂项辅助基准的结果报告在表6中。

**GAIA**（Mialon et al., 2023）评估代理的通用任务解决能力，涵盖不同的真实世界场景。它需要多种代理能力，包括推理、多模态理解、网页浏览和编码。GAIA包括466个跨三个级别的策划任务。由于将各种工具与代理集成的复杂性，设置GAIA传统上具有挑战性，但OpenHands的基础设施（如运行时§2.2，工具§2.3）显著简化了集成过程。

**GPQA**（Rein et al., 2023）评估代理在解决具有挑战性的研究生级别问题时协调使用工具的能力。工具使用（如Python）和网络搜索通常有助于帮助代理回答这些问题，因为它们提供了LLM通常无法准确进行的计算，并能访问LLM参数知识库之外的信息。

**AgentBench**（Liu et al., 2023）评估代理在多轮、开放式生成环境中的推理和决策能力。我们选择了基于代码的操作系统（OS）子集，包含144个任务。来自OpenHands的代理以多轮方式直接使用bash命令与特定任务的OS交互，结合交互和推理来自动完成任务。

**MINT**（Wang et al., 2024b）是一个基准，旨在通过多轮交互评估代理使用工具和GPT-4模拟的自然语言反馈解决具有挑战性任务的能力。我们使用了Yuan et al.（2024）中使用的编码和数学子集。我们遵循原始论文，允许代理最多进行五次迭代交互，并有两次机会提出解决方案。

**ProofWriter**（Tafjord et al., 2021）是一个合成数据集，旨在评估LLM的演绎推理能力。与Logic-LM（Pan et al., 2023）相同，我们专注于最具挑战性的子集，其中包含600个需要5跳推理的实例。为尽量减少语义解析中潜在错误的影响，我们使用Logic-LM提供的逻辑形式。

**Entity Deduction Arena（EDA）**（Zhang et al., 2024a）评估代理通过策略性提问推断未知实体的能力，类似于"20个问题"游戏。该基准测试代理在多轮对话中的状态跟踪、策略规划和归纳推理能力。我们评估了两个数据集"Things"和"Celebrities"，每个包含100个实例，并报告这两个数据集上的平均成功率。

---

## 5 结论

我们介绍了OpenHands，一个社区驱动的平台，支持开发通过软件接口与世界交互的代理。通过提供强大的交互机制、安全的沙箱环境、必要的代理技能、多代理协作能力以及全面的评估框架，OpenHands加速了代理型AI系统的研究创新和实际应用。尽管在开发安全可靠的代理方面存在挑战（§A），我们对我们充满活力的社区感到兴奋，并期待OpenHands的持续发展。

---

## 参考文献

（完整参考文献列表请参见原文，此处省略详细翻译——所有参考文献保持原有英文格式）

---

## 作者贡献

这项工作是一项跨多个机构的开源协作努力。我们采用基于积分的系统来确定贡献和授予作者身份，技术贡献以拉取请求（PR）为单位进行跟踪和衡量³。王兴耀领导了该项目，协调整体开发和论文撰写工作。详细贡献如下：

**• 代理开发（§3）：** 王兴耀领导了CodeAct Wang et al.（2024a）和CodeActSWE代理的实现。Frank F. Xu领导了网页浏览代理的开发 Zhou et al.（2023a）。诸葛明辰协调了GPTSwarm代理 Zhuge et al.（2024）的集成。Robert Brennan和Bobby Li领导了微代理的开发。

**• 架构开发（图2）：** Robert Brennan启动了架构设计。Bobby Li、Frank F. Xu、王兴耀、宋宇凡和郑明璋进一步完善和扩展了架构。Bobby Li实现了集成测试的初始版本（§E），维护了agentskills库（§2.3），管理配置，并解决了评估中的资源泄漏问题。Frank F. Xu为代理执行和评估开发了网页浏览环境（§J），并将其与代理和前端用户界面集成。王兴耀编写了agentskills库和Docker沙箱的初始代码。宋宇凡实现了评估的成本跟踪，而郑明璋开发了一个与镜像无关的Docker沙箱，用于更稳定的SWE-Bench评估。

**• 基准测试、集成和代码审查：** Bobby Li和宋宇凡领导了基准测试集成工作，包括协调、评估和代码审查。宋宇凡还帮助跟踪PR贡献。Graham Neubig、王兴耀、郑明璋、Robert Brennan、Hoang H. Tran、Frank F. Xu、唐祥如、Li Fuqiang和邵彦君在集成和代码审查中提供了额外支持。具体基准贡献包括：

  - SWE-Bench Jimenez et al.（2024）：Bowen Li和王兴耀
  - WebArena Zhou et al.（2023a）和MiniWob++ Liu et al.（2018）：Frank F. Xu
  - GAIA Mialon et al.（2023）：潘嘉逸（集成）和诸葛明辰（GPTSwarm评估）
  - API-Bench Patil et al.（2023）和ToolQA Zhuang et al.（2024）：宋悦琪
  - HumanEvalFix Muennighoff et al.（2024）：Niklas Muennighoff和唐祥如
  - ProofWriter Tafjord et al.（2021）：Ren Ma
  - MINT Wang et al.（2024b）：Hoang H. Tran
  - AgentBench Liu et al.（2023）：Li Fuqiang
  - BIRD Li et al.（2023b）：Binyuan Hui
  - GPQA Rein et al.（2023）：Jaskirat Singh
  - BioCoder Tang et al.（2024c）：唐祥如和Bill Qian
  - ML-Bench Tang et al.（2024b）：唐祥如和邵彦君
  - Entity-Deduction-Arena Zhang et al.（2024a）：Yizhe Zhang

**• 指导：** Graham Neubig指导了该项目，提供了指导、资源和实质性的论文编辑。Heng Ji和Hao Peng提供了额外的项目建议并协助论文撰写。Junyang Lin提供了咨询支持并赞助了资源。

> ³更多详情，请参考 https://github.com/All-Hands-AI/OpenHands/pull/1917。

---

## A 限制与未来工作

我们对充满活力的社区在OpenHands中奠定的基础感到兴奋，并期待其持续发展。我们确定了未来工作的几个方向：

**增强的多模态支持。** 虽然我们当前的实现已经通过预定义的代理技能支持了广泛的文件格式，但我们有兴趣通过标准的IPython和浏览器集成以原则性的方式启用多模态功能，例如通过浏览器使用视觉语言模型查看图像和视频，或使用代码处理XLSX文件。

**更强的代理。** 当前的代理仍然难以处理复杂任务，我们有兴趣通过训练和推理时技术来构建更好的代理。

**代理编辑改进。** 当前代理在编辑长文件时存在很多问题，我们有兴趣探索不同的方法来提高代理的文件编辑性能。

**网页浏览改进。** 由于OpenHands的可扩展性，可以提高代理性能的正交组件可以轻松集成。例如，得益于OpenHands的可扩展架构，Auto Eval & Refine Pan et al.（2024），一种带有Reflexion Shinn et al.（2024）提示和任务完成奖励模型的代理错误重试策略，将作为可选组件附加到我们的浏览代理上。

**自动化工作流生成。** 目前，OpenHands的工作流仍然需要大量的人工构建工作。我们相信基于图的框架，如GPTSwarm Zhuge et al.（2024）和LangGraph Chase（2022），可以作为构建代理的替代方案。特别是在GPTSwarm中，当代理使用图构建时，更容易纳入各种优化方法（如强化学习、元提示）。OpenHands考虑将这些方法作为在未来版本中实现自动化工作流生成的有前途解决方案的基础。

---

## B 伦理声明

今天的大多数AI代理仍然是研究产物，缺乏在现实世界中可靠地执行复杂、长期任务的能力。然而，随着它们的性能不断提升并越来越多地部署在现实世界中，它们既有潜力大幅提高生产力，也可能对社会构成重大安全风险。OpenHands通过以下方式帮助降低风险：

（1）支持对这些代理进行系统性评估，这可以在它们被广泛部署之前识别和解决风险。
（2）促进人机交互，而不是允许代理在没有监督的情况下自主运行。
（3）更重要的是，我们希望OpenHands能让世界各地的研究人员访问最佳的代理套件，以进行面向构建安全且有益的代理的前沿安全研究。

---

## C 相关工作

大语言模型（LLM）如ChatGPT OpenAI（2024a）和GPT-4 OpenAI et al.（2024）的突破显著增强了自主代理在各个领域的能力 Ye et al.（2023）；Tang et al.（2024d）；Park et al.（2023）；Cui et al.（2023）。这些进步催生了众多通用型代理方案 Gravitas（2023）；Nakajima（2023）；Wu et al.（2023），旨在执行多样化的用户任务，并引起了开发者及更广泛受众的关注。著名的作品如Auto-GPT Gravitas（2023）通过将用户目标分解为可执行的步骤来利用LLM完成任务。多代理协作系统利用LLM进行角色扮演和任务解决 Zhuge et al.（2023）；Li et al.（2023a）；Zhou et al.（2023b）；Team（2023），其中MetaGPT Hong et al.（2023）强调标准化操作流程，AutoGen Wu et al.（2023）为交互式系统提供了一个对话框架。AGENTS Zhou et al.（2023b）和AutoAgents Chen et al.（2024）为可定制的代理架构提供了新的范式，而XAgent Team（2023）和GPTSwarm Zhuge et al.（2024）分别引入了复杂的管理系统和可优化图，用于增强代理操作。

代理开发的激增导致了旨在简化代理实现的专门框架。LangChain和LangGraph Chase（2022）提供了带有基本运行时支持的基础构建块，而CrewAI CrewAI（2024）专注于编排多代理通信。BrowserGym ServiceNow专门针对网页浏览能力，DSPy Khattab et al.（2024）强调端到端提示优化。AutoGen Wu et al.（2023）通过实现Python和bash执行能力（尽管是无状态命令执行）超越了基本框架，而像CrewAI这样的框架提供了沙箱化但功能有限的代码解释器功能。

软件开发作为应用基于LLM的代理的前沿领域，在促进开发过程的框架方面取得了进展 Hong et al.（2023）；Qian et al.（2023）。诸如ChatDev Qian et al.（2023）之类的创新自动化了类似于瀑布模型的软件开发生命周期，AutoCodeRover Zhang et al.（2024b）通过代码搜索和抽象语法树操作解决GitHub问题。AgentCoder Huang et al.（2024）通过集成测试和反馈迭代完善代码生成，而SWE-Agent Yang et al.（2024）集成LLM以自动修复GitHub问题，简化了软件工程。

---

## D 图形用户界面

除了从命令行运行外，OpenHands还拥有一个丰富的图形用户界面，可以可视化代理的当前操作（如浏览网页、执行基本命令或Python代码等），并允许用户实时反馈。用户界面的截图如图1所示。用户可以在代理工作时的任何时刻中断代理，以提供额外的反馈、评论或指令。该用户界面直接连接到事件流（§2.1），以控制和可视化代理及运行时，使其与代理和运行时无关。

---

## E 质量控制：代理集成测试

集成测试 Leung & White（1990）长期以来一直被软件开发人员用于确保软件质量。与具有简单输入输出模式的大语言模型不同，代理通常是复杂的软件，在开发过程中容易引入微小错误，从而损害最终的任务性能。虽然运行完整的评估套件（§4）是衡量性能下降的最终方法，但对每个代码更改运行完整评估可能极其缓慢和昂贵⁴。在OpenHands中，我们开创了一个端到端的代理测试框架，测试提示回归、动作和沙箱环境。它结合了软件工程中的集成测试和基础模型模拟以实现确定性行为，防止在代理开发过程中意外引入错误。

**定义集成测试。** OpenHands的集成测试框架旨在通过自动化任务执行和结果验证来验证端到端功能。开发者定义任务和预期结果；例如，一个任务可能涉及纠正名为"bad.txt"的文档中的拼写错误。通过OpenHands执行任务后，输出结果会与预定义的"金标准文件"进行比较，以确保准确性。

**模拟LLM以实现确定性行为。** 为解决大语言模型（LLM）的非确定性和相关高成本问题，该框架拦截所有LLM调用，并根据精确的提示匹配提供预定义的响应。这种方法不仅确保了测试结果的一致性，还通过减少对真实LLM的依赖来降低运营成本。

**在破坏性变更时重新生成LLM响应。** 提示-响应对通过一个脚本进行管理，该脚本在引入新测试或修改现有提示时生成并存储这些对。对于常规测试，该框架通过略微调整提示来尝试重用现有的LLM响应。影响任务处理的重要更改需要使用真实LLM重新生成这些对。

**集成测试的好处。** 该框架提供了几个优势，包括：1）**提示回归测试**：存储的提示-响应对便于变更跟踪，并为新团队成员理解LLM交互提供参考；2）**多平台支持**：自动为每个拉取请求和主分支上的提交安排测试，跨多个平台、环境和代理运行，包括Linux和Mac，以及在本地、SSH和执行沙箱中；3）**全面的错误检测**：捕获提示生成、消息传递和沙箱执行中的错误，从而保持高测试覆盖率。

> ⁴使用gpt-4o运行SWE-Bench Lite Jimenez et al.（2024）评估大约需要600美元。

---

## F OpenHands运行时工作原理

### F.1 工作流

OpenHands运行时系统使用基于Docker容器的客户端-服务器架构。参见图4了解其工作原理的概述。

（1）**用户输入：** 用户提供自定义的基础Docker镜像。

（2）**镜像构建：** OpenHands基于用户提供的镜像构建一个新的Docker镜像（"OH运行时镜像"）。这个新镜像包含OpenHands特定的代码，主要是"运行时客户端"（即§2.2中描述的运行时API服务器）。

（3）**容器启动：** 当OpenHands启动时，它使用OH运行时镜像启动一个Docker容器。

（4）**通信：** OpenHands后端（runtime.py）通过RESTful API与运行时客户端通信，发送动作并接收观察结果。

（5）**动作执行：** 运行时客户端接收来自后端的动作，在沙箱环境中执行它们，并返回观察结果。

（6）**观察结果返回：** 客户端将执行结果作为观察结果发送回OpenHands后端事件流。

**客户端的作用：**
- 作为OpenHands后端和沙箱环境之间的中介
- 在容器内安全地执行各种类型的动作（shell命令、文件操作、Python代码等）
- 管理沙箱环境的状态，包括当前工作目录和已加载的插件
- 格式化并将观察结果返回给后端，确保处理结果的一致接口

### F.2 OpenHands如何构建和维护运行时镜像

OpenHands构建和管理运行时镜像的方法确保了为生产环境和开发环境创建和维护Docker镜像的效率、一致性和灵活性。

#### F.2.1 镜像标签系统

OpenHands为其运行时镜像使用双标签系统，以在可重现性和灵活性之间取得平衡：

（1）**基于哈希的标签：** `{target_image_repo}:{target_image_hash_tag}`。例如：`runtime:abc123def456`
  - 此标签基于Docker构建文件夹的MD5哈希，其中包括源代码（运行时客户端及相关依赖）和Dockerfile
  - 相同的哈希标签保证镜像使用完全相同的源代码和Dockerfile构建
  - 这确保了可重现性；相同的哈希总是意味着相同的镜像内容

（2）**通用标签：** `{target_image_repo}:{target_image_tag}`。例如：`runtime:oh_v0.9.3_ubuntu_tag_22.04`
  - 此标签遵循格式：`runtime:oh_v{VERSION}_{BASE_IMAGE}_tag_{IMAGE_TAG}`
  - 它表示特定基础镜像和OpenHands版本组合的最新构建
  - 此标签在从相同基础镜像构建新镜像时更新，即使源代码发生变化

基于哈希的标签确保了可重现性，而通用标签则提供了对特定配置最新版本的稳定引用。这种双标签方法允许OpenHands高效地管理开发和生成环境。

#### F.2.2 构建过程

（1）**镜像命名约定：**
  - 基于哈希的标签：`target_image_repo:target_image_hash_tag`。例如：`runtime:abc123def456`
  - 通用标签：`target_image_repo:target_image_tag`。例如：`runtime:oh_v0.9.3_ubuntu_tag_22.04`

（2）**构建过程：**
  a. 将基础镜像名称转换为OH运行时镜像名称。例如：`ubuntu:22.04` -> `runtime:oh_v0.9.3_ubuntu_tag_22.04`
  b. 生成构建上下文（Dockerfile和OpenHands源代码）并计算其哈希值
  c. 检查是否存在具有计算哈希值的现有镜像
  d. 如果未找到，检查是否存在最近的兼容镜像作为基础
  e. 如果没有兼容镜像，则从原始基础镜像开始从头构建
  f. 使用基于哈希的标签和通用标签标记新镜像

（3）**镜像复用和重建逻辑：** 系统遵循以下步骤来确定是从用户提供的基础镜像（如`ubuntu:22.04`）构建新镜像还是使用现有镜像：
  a. 如果存在具有相同哈希的镜像（如`runtime:abc123def456`），则直接复用
  b. 如果未找到精确哈希，系统将尝试使用最新的通用镜像（如`runtime:oh_v0.9.3_ubuntu_tag_22.04`）作为基础进行重建。这通过利用现有依赖来节省时间
  c. 如果既未找到哈希标签镜像，也未找到通用标签镜像，系统将从头开始完全构建镜像

**缓存与效率。** 系统尽可能尝试重用现有镜像以节省构建时间。如果找到精确匹配（按哈希），则直接使用而无需重建。如果找到兼容镜像，则将其用作重建的基础，从而节省依赖安装时间。

构建过程的流程图如图5所示。

---

## G GPQA基准的额外结果

我们在表7中展示了更详细的结果，包括在GPQA基准其他子集上的性能。

---

## H CodeActSWE代理的上下文内演示

提示改编自SWE-agent发布的轨迹（https://github.com/princeton-nlp/SWE-agent/tree/main/trajectories/demonstrations）。完整提示可在以下地址找到：https://github.com/All-Hands-AI/OpenHands/blob/main/agenthub/codeact_swe_agent/prompt.py。

---

## I 支持的代理技能

截至OpenHands v0.6，我们支持以下技能列表。请参阅源代码获取最新的技能列表：https://github.com/All-Hands-AI/OpenHands/blob/main/OpenHands/runtime/plugins/agent_skills/agentskills.py

```python
def open_file(path: str, line_number: Optional[int] = None) -> None:
    """
    在编辑器中打开给定路径的文件。如果提供了line_number，
    窗口将移动以包含该行。

    参数：
        path: str: 要打开的文件的路径。
        line_number: Optional[int]: 要移动到的行号。
    """

def goto_line(line_number: int) -> None:
    """
    移动窗口以显示指定的行号。
    参数：
        line_number: int: 要移动到的行号。
    """

def scroll_down() -> None:
    """将窗口向下移动100行。"""

def scroll_up() -> None:
    """将窗口向上移动100行。"""

def create_file(filename: str) -> None:
    """创建并打开一个具有给定名称的新文件。"""

def edit_file(start: int, end: int, content: str) -> None:
    """
    编辑文件。
    用给定的文本`content`替换打开文件中从`start`到`end`（含）的行。
    注意，编辑前必须先打开文件。
    参数：
        start: int: 起始行号。必须满足 start >= 1。
        end: int: 结束行号。必须满足 start <= end <= 文件行数。
        content: str: 用于替换这些行的内容。
    """

def search_dir(search_term: str, dir_path: str = './') -> None:
    """在dir中的所有文件中搜索search_term。如果未提供dir，则在当前目录中搜索。"""

def search_file(search_term: str, file_path: Optional[str] = None) -> None:
    """在文件中搜索search_term。如果未提供file，则在当前打开的文件中搜索。"""

def find_file(file_name: str, dir_path: str = './') -> None:
    """在指定目录中查找具有给定名称的所有文件。"""

def parse_pdf(file_path: str) -> None:
    """解析PDF文件的内容并打印。"""

def parse_docx(file_path: str) -> None:
    """解析DOCX文件的内容并打印。"""

def parse_latex(file_path: str) -> None:
    """解析LaTex文件的内容并打印。"""

def parse_audio(file_path: str, model: str = 'whisper-1') -> None:
    """
    解析音频文件的内容并打印。
    参数：
        model: 用于转录的音频模型。默认为'whisper-1'。
    """

def parse_image(file_path: str, task: str = '尽可能详细地描述此图像。') -> None:
    """
    解析图像文件的内容并打印描述。
    参数：
        task: API调用的任务描述。默认为'尽可能详细地描述此图像。'
    """

def parse_video(file_path: str, task: str = '尽可能详细地描述此图像。', frame_interval: int = 30) -> None:
    """
    解析视频文件的内容并打印描述。
    参数：
        frame_interval: 分析帧之间的间隔。默认为30。
    """

def parse_pptx(file_path: str) -> None:
    """解析pptx文件的内容并打印。"""
```

---

## J BrowserGym 动作

以下是BrowserGym⁵ v0.3.4中定义的所有支持的动作。这些动作可分为几种类型，并可配置为仅使用功能子集。包括代理控制动作、导航动作、基于页面元素的动作、基于坐标的动作以及与标签页相关的动作。我们使用BrowserGym库中的这些动作作为主要的浏览动作原语。

```python
def send_msg_to_user(text: str):
    """向用户发送消息。"""

def report_infeasible(reason: str):
    """通知用户其指令不可行。"""

def noop(wait_ms: float = 1000):
    """不执行任何操作，并可选地等待指定的时间（毫秒）。"""

def fill(bid: str, value: str):
    """填写表单字段。聚焦元素并用输入的文本触发输入事件。
    适用于<input>、<textarea>和[contenteditable]元素。"""

def check(bid: str):
    """确保复选框或单选元素被选中。"""

def uncheck(bid: str):
    """确保复选框或单选元素未被选中。"""

def select_option(bid: str, options: str | list[str]):
    """在<select>元素中选择一个或多个选项。"""

def click(bid: str, button: Literal["left", "middle", "right"] = "left",
          modifiers: list[Literal["Alt", "Control", "Meta", "Shift"]] = []):
    """点击一个元素。"""

def dblclick(bid: str, button: Literal["left", "middle", "right"] = "left",
             modifiers: list[Literal["Alt", "Control", "Meta", "Shift"]] = []):
    """双击一个元素。"""

def hover(bid: str):
    """悬停在一个元素上。"""

def press(bid: str, key_comb: str):
    """聚焦匹配元素并按下组合键。"""

def focus(bid: str):
    """聚焦匹配元素。"""

def clear(bid: str):
    """清除输入字段。"""

def drag_and_drop(from_bid: str, to_bid: str):
    """执行拖放操作。"""

def scroll(delta_x: float, delta_y: float):
    """水平和垂直滚动。单位为像素，正值为向右或向下滚动，负值为向左或向上滚动。"""

def mouse_move(x: float, y: float):
    """将鼠标移动到一个位置。使用以像素为单位的绝对客户端坐标。"""

def mouse_up(x: float, y: float, button: Literal["left", "middle", "right"] = "left"):
    """移动鼠标到一个位置然后释放鼠标按钮。"""

def mouse_down(x: float, y: float, button: Literal["left", "middle", "right"] = "left"):
    """移动鼠标到一个位置然后按下并保持鼠标按钮。"""

def mouse_click(x: float, y: float, button: Literal["left", "middle", "right"] = "left"):
    """移动鼠标到一个位置并点击鼠标按钮。"""

def mouse_dblclick(x: float, y: float, button: Literal["left", "middle", "right"] = "left"):
    """移动鼠标到一个位置并双击鼠标按钮。"""

def mouse_drag_and_drop(from_x: float, from_y: float, to_x: float, to_y: float):
    """从一个位置拖放到另一个位置。使用以像素为单位的绝对客户端坐标。"""

def keyboard_press(key: str):
    """按下组合键。"""

def keyboard_up(key: str):
    """释放键盘按键。"""

def keyboard_down(key: str):
    """按下并保持键盘按键。"""

def keyboard_type(text: str):
    """通过键盘输入一串文本。"""

def keyboard_insert_text(text: str):
    """在当前聚焦元素中插入一串文本。"""

def goto(url: str):
    """导航到URL。"""

def go_back():
    """导航到历史记录中的上一页。"""

def go_forward():
    """导航到历史记录中的下一页。"""

def new_tab():
    """打开新标签页。它将变为活动标签页。"""

def tab_close():
    """关闭当前标签页。"""

def tab_focus(index: int):
    """将标签页前置（激活标签页）。"""

def upload_file(bid: str, file: str | list[str]):
    """点击元素并等待"filechooser"事件，然后选择一个或多个要上传的输入文件。"""

def mouse_upload_file(x: float, y: float, file: str | list[str]):
    """点击一个位置并等待"filechooser"事件，然后选择一个或多个要上传的输入文件。"""
```

> ⁵https://github.com/ServiceNow/BrowserGym/blob/main/core/src/browsergym/core/action/functions.py

---

## K 浏览代理详情

以下展示了一个示例提示，包含当前步骤所需的所有信息，以便预测下一个浏览动作。请注意，如果代理认为多个动作应在没有页面反馈的情况下顺序执行，我们也指示代理在一次回应中预测多个动作。这可以节省常见工作流的轮次，这些工作流由在同一页面上的一系列动作组成，观察结果不变，例如在登录页面中填写用户名和密码并提交。

```
# 指令
审查页面的当前状态和所有其他信息，
找到完成目标的最佳可能的下一个动作。
你的答案将由程序解释和执行，
确保遵循格式说明。

# 目标：
浏览localhost:8000，并告诉我关于生命的终极答案。
在任何时候都不要向我寻求确认。

# 动作空间
16种不同类型的动作可用。
noop(wait_ms: float = 1000)
send_msg_to_user(text: str)
scroll(delta_x: float, delta_y: float)
fill(bid: str, value: str)
select_option(bid: str, options: str | list[str])
click(bid: str, button: Literal['left', 'middle', 'right'] = 'left',
      modifiers: list[Literal['Alt', 'Control', 'Meta', 'Shift']] = [])
dblclick(bid: str, button: Literal['left', 'middle', 'right'] = 'left',
         modifiers: list[Literal['Alt', 'Control', 'Meta', 'Shift']] = [])
hover(bid: str)
press(bid: str, key_comb: str)
focus(bid: str)
clear(bid: str)
drag_and_drop(from_bid: str, to_bid: str)
upload_file(bid: str, file: str | list[str])
go_back()
go_forward()
goto(url: str)

可以一次提供多个动作。例如：
fill('a12', 'example with "quotes"')
click('51')
click('48', button='middle', modifiers=['Shift'])
多个动作将按顺序执行，中间不获取页面的反馈。
如果需要页面的反馈，不要一次执行多个动作。

# 当前可访问性树：
RootWebArea '终极答案', focused
[8] heading '终极答案'
[9] paragraph ''
StaticText '点击按钮以揭示关于生命、宇宙和一切的答案。'
[10] button '点击我', clickable

# 先前动作
goto('http://localhost:8000')

以下是一个带有思维链的有效动作示例，用于点击按钮：
"
为完成我的目标，我需要点击bid为12的按钮，
```click("12")```
"

上述提示的一个示例回应是：
为完成我的目标，我需要点击bid为10的按钮以揭示关于生命、宇宙和一切的答案。
```click("10")```

对于WebArena基准的评估，由于某些任务需要检查代理返回给用户的消息的精确匹配，我们添加了以下指令，让代理在给用户发消息时只回复一个简洁的答案字符串，以防止代理因额外文本而测试失败：

以下是一个带有思维链的有效动作示例，用于向用户提供简洁答案：
"
为完成我的目标，我需要将所询问的信息发送回用户。此页面列出了HP喷墨传真机的信息，这正是目标中标识的产品。其价格为$279.49。我将向用户发送带有答案的消息。
```send_msg_to_user("$279.49")```
"
