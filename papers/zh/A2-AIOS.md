# AIOS：LLM智能体操作系统

**发表于 COLM 2025 会议论文**

Kai Mei, Xi Zhu, Wujiang Xu, Mingyu Jin, Wenyue Hua, Zelong Li
Shuyuan Xu, Ruosong Ye, Yingqiang Ge, Yongfeng Zhang
罗格斯大学计算机科学系*

## 摘要

基于LLM的智能代理（agent）在部署时面临重大挑战，特别是在资源管理方面。允许无限制地访问LLM或工具资源可能导致低效甚至有害的资源分配和利用。此外，当前智能体设计中缺乏适当的调度和资源管理机制，阻碍了并发处理并限制了整体系统效率。为了解决这些挑战，本文提出了AIOS（基于LLM的AI智能体操作系统）架构，用于管理基于LLM的智能体。该架构引入了一种新颖的架构来服务基于LLM的智能体，通过将资源和LLM特定服务从智能体应用程序中隔离到AIOS内核中。该AIOS内核为运行时智能体提供基础服务（例如调度、上下文管理、内存管理、存储管理、访问控制）。为了增强可用性，AIOS还包含一个AIOS SDK，这是一套全面的API，用于利用AIOS内核提供的功能。实验结果表明，使用AIOS可以为各种智能体框架构建的智能体实现高达2.1倍的执行速度提升。源代码可在 https://github.com/agiresearch/AIOS 获取。

## 1 引言

在自主智能体领域，研究工作（Wooldridge & Jennings, 1995; Jennings et al., 1998; Bresciani et al., 2004）致力于开发能够感知环境、理解指令、做出决策、采取行动并从反馈中学习的智能体。大语言模型（LLM）的出现（Achiam et al., 2023; Touvron et al., 2023a; Team et al., 2023）为智能体开发带来了新的可能性（Ge et al., 2023a）。当前的LLM在理解指令（Ouyang et al., 2022; Chung et al., 2022; Touvron et al., 2023b; Geng et al., 2022）、推理和解决问题（Kojima et al., 2022; Nijkamp et al., 2022; Taylor et al., 2022; Hao et al., 2023; Kim et al., 2023）以及与人类用户（Ross et al., 2023）和外部环境（Driess et al., 2023; Brohan et al., 2023）交互方面展现出了强大的能力。基于这些强大的LLM，新兴的基于LLM的智能体（Ge et al., 2023a; Yao et al., 2023; Shinn et al., 2023; Deng et al., 2023; Packer et al., 2023; Wu et al., 2024）在从虚拟助手到更复杂的推理和问题解决系统等多样化的环境中展示出了强大的任务完成能力。

图1展示了一个基于LLM的智能体执行真实世界任务的示例，其中旅行智能体处理一个旅行组织请求。该智能体有条不紊地将该请求分解为可执行的步骤——根据用户偏好预订航班、预订住宿、处理付款和更新日历。在整个执行过程中，智能体展现出源自其LLM基础的推理和决策能力，这使其区别于受预定功能或工作流程约束的传统应用程序。实现这个旅行场景需要智能体无缝集成LLM相关服务（偏好检索、API选择、响应生成）与传统的操作系统服务（磁盘访问、软件执行）。

当前的智能体框架存在关键的设计局限性，它们授予智能体直接访问系统级资源（如LLM和工具）的权限（Qin et al., 2024），这损害了资源优化并引入了潜在的漏洞。没有适当的调度，智能体可能垄断资源，例如让LLM被请求淹没而其他智能体只能等待。缺乏有效的资源管理机制会显著损害系统效率。在并发条件下，现有框架（例如Autogen、Langchain）对LLM调用采用低效的试错方法：提示被转换为张量并加载到GPU内存中，直到CUDA内存限制触发异常，迫使张量释放并需要多次重试，这大大降低了在众多智能体竞争有限LLM资源的场景下的系统吞吐量。

为了缓解上述限制，我们引入了AIOS，一种旨在更高效地服务基于LLM的智能体的架构。我们的贡献如下：

- **新的智能体服务架构。** 我们引入了AIOS，一种新颖的基于LLM的智能体服务架构。AIOS将智能体应用程序和智能体资源（如LLM和工具）划分为不同的层，即应用层和内核层。这种分离有助于系统化的资源管理、效率优化和安全性增强。

- **AIOS内核设计与实现。** 在AIOS的核心，我们设计并实现了一个AIOS内核，以封装资源管理抽象。在该内核中，智能体查询被分解为子执行单元（即AIOS系统调用）以促进并行性。我们设计了一个智能体调度器来协调跨模块的系统调用执行，而内存管理器、存储管理器、工具管理器和LLM核心负责处理分派的系统调用。我们还设计了上下文管理器来处理上下文中断，并设计了访问管理器来验证智能体操作，以确保AIOS内核的可靠性。

- **AIOS SDK开发。** 我们开发了AIOS SDK，它提供了内核功能的高级抽象，允许开发者专注于应用逻辑和高级功能，而无需被复杂的内核细节所困扰。

- **实证结果。** 我们对使用各种智能体框架开发的智能体进行了广泛的AIOS评估。结果表明，AIOS能够在标准智能体基准测试中保持智能体的性能，并且在使用工具调用的基准测试中甚至能够提升性能。此外，AIOS显著提高了执行效率，在不同框架的服务智能体中实现了高达2.1倍的执行速度提升。这些实验结果强调了AIOS在优化智能体性能和执行速度方面的有效性。

## 2 AIOS架构

如图2所示，AIOS架构分为三个不同的层：应用层、内核层和硬件层。这种分层设计旨在在系统内建立清晰的关注点分离。更高级别的应用抽象了底层实现的复杂性，通过明确定义的接口（如SDK和系统调用）与它们交互。

**应用层。** 应用层利用AIOS SDK，提供用于请求AIOS内部系统资源的接口。这种设计使智能体摆脱了资源管理的负担，同时通过防止直接资源操作来强制执行隔离。AIOS SDK既支持原生智能体开发，也支持从不同框架（包括ReAct（Yao et al., 2023）、Reflexion（Shinn et al., 2023）、Autogen（Wu et al., 2023）、Open-Interpreter（Lucas, 2024）和MetaGPT（Hong et al., 2023））适配的非原生智能体。非原生智能体通过适配器函数与AIOS内核资源交互，而原生开发则通过调用系统调用的预定义API进行简化。这种抽象允许开发者关注智能体逻辑而非资源管理细节。

**内核层。** 内核层集成了两个组件：用于非LLM计算任务的传统操作系统内核和我们创新的AIOS内核。在AIOS内核内部，专门的模块通过系统调用处理智能体请求。调度器使用先进的调度策略（详见第3.3节）将这些调用分派到适当的模块。我们设计了一个统一的接口，将LLM封装为核心的单元，类似于CPU核心，从而能够集成多样化的LLM端点。为了支持LLM上下文切换，我们实现了一个具有快照和恢复功能的上下文管理器（第3.4节）。为了高效处理智能体数据，我们开发了一个用于运行时操作的内存管理器（第3.5节）和一个用于持久化存储的存储管理器（第3.6节）。此外，工具管理器加载工具并解决AIOS SDK支持的工具的调用冲突（第3.7节），而访问管理器则实现访问控制和用户干预协议（第3.8节）。

**硬件层。** 硬件层由系统的物理组件组成，如CPU、GPU、内存、磁盘和外围设备。硬件层并非本工作的主要关注点——AIOS内核不直接与硬件交互，而是依赖操作系统系统调用来访问硬件层的物理资源。

## 3 AIOS内核

在本节中，我们首先概述AIOS内核，重点介绍每个模块如何与其他模块协作以支持集成的功能。随后，我们深入探讨每个模块的设计和实现，讨论它们在整体AIOS架构中的角色和贡献。

### 3.1 模块间的关系与连接

在AIOS内核内部，智能体查询被分解为分类的系统调用（LLM处理、内存访问、存储操作、工具使用），如图3所示，完整的系统调用目录见附录A.1。每个系统调用都绑定到一个线程，并由调度器分派，调度器集中管理所有模块的队列。系统调用根据其属性集被路由到适当的模块队列，每个模块监控其指定的队列以获取待调度的调用。上下文管理器将在LLM核心内部被触发以处理上下文中断，而不是通过调度器进行调度。

### 3.2 LLM核心

由于LLM的部署方式多种多样，例如使用哪个LLM、LLM是托管在云端还是本地设备、LLM需要什么硬件条件、或者使用什么推理框架，我们将采用不同部署选项的每个LLM实例封装为一个核心，类似于传统操作系统中的CPU核心。这种设计允许我们将每个LLM实例视为一个专用的处理单元，增强了AIOS架构中的模块化和可扩展性。为了容纳不同的LLM实例，我们为每个LLM实例引入了一个封装器，并在该封装器内部设计了统一的系统调用，专门用于LLM推理。通过将LLM实例抽象为核心并实现标准化的系统调用，AIOS提供了一种灵活的方式来集成不同部署选项下的LLM实例，这归功于LLM核心的模块化设计。LLM核心的详细信息见附录A.2。

### 3.3 调度器

我们将所有队列集中到调度器模块中，而不是分布在各个处理模块中，从而隔离请求管理职责，使每个模块能够专注于执行。这种集中化简化了跨模块的任务协调，并提供了一个统一的调度框架。为了管理系统调用，我们实现了两种经典算法：先来先服务（FIFO），按到达顺序处理调用，但可能增加后续请求的等待时间；以及轮转调度（RR），以时间片方式循环处理调用以实现更均衡的资源分配。RR策略由我们用于LLM推理的上下文中断机制支持，详见附录A.3。

### 3.4 上下文管理器

LLM推理时间通过长时间运行的系统调用制造了瓶颈，这些调用会垄断资源。我们的上下文中断机制通过任务中断和恢复（通过快照和恢复操作）解决了这个问题。上下文管理器设计了两种方法：基于文本的方法（适用于无法访问logits的闭源LLM，保存解码后的输出）和基于logits的方法（保留中间搜索树结构以实现更细粒度的状态恢复）。基于logits的方法如图4所示。使用束搜索（LLM中常用（Touvron et al., 2023b; Jiang et al., 2023; Biderman et al., 2023）），为简化起见设束宽为1，我们演示了该过程：当处理"确定航班UA057目的地是否会下雨"时，LLM在每一步评估候选词元。如果被调度器在生成过程中暂停，上下文管理器会对中间结果进行快照。恢复时，它重新加载此快照，从中断点继续，得出最终答案：Search weather in Paris，无需重新开始计算。

### 3.5 内存管理器

与传统操作系统内存管理器处理物理RAM不同，AIOS的内存管理器处理运行时智能体交互历史（Lerman & Galstyan, 2003; Zhang et al., 2024），包括对话日志和工具调用结果。它管理内存结构、分配、读/写操作、删除和更新。智能体内存默认驻留在RAM中，但当分配的空间接近容量时，管理器会在RAM和磁盘之间实现内存交换。当智能体的内存使用超过其块限制（例如分配的80%）时，内存管理器启动K-最近最少使用（LRU-K）驱逐策略，通过存储管理器（详见第3.6节）将项目从RAM转移到磁盘。LRU-K优先保留最近被访问至少K次的项目在RAM中，而将访问频率较低的项目移到磁盘。这通过卸载不常访问的数据来平衡内存效率，同时确保在需要时可检索。内存管理器的详细实现在附录A.5中。

### 3.6 存储管理器

存储管理器处理智能体的持久化数据存储，包括智能体运行所依赖的文件或知识库，以及需要持久存储的智能体记忆。在智能体运行期间，当智能体的内存使用超过分配的限制时，内存管理器调用存储管理器将数据交换到磁盘。具体来说，存储管理器根据从内存管理器传递的智能体ID读取和写入数据。除了内存管理器之外，智能体本身也可能在运行时请求读取和写入磁盘上的数据，这些智能体请求也由存储管理器处理。具体来说，智能体调用SDK中的存储API，该API进一步转换为与存储相关的系统调用，并由调度器放入存储队列。然后存储管理器处理队列中的请求以满足智能体请求。存储管理器使用本地文件和向量数据库（例如chromadb）实现。存储管理器的实现细节见附录A.6。

### 3.7 工具管理器

AIOS内核中的工具管理器负责管理AIOS SDK支持的一套广泛的API工具。

**标准化工具加载。** 管理器采用标准化接口统一处理多样化的工具，同时在执行前进行参数验证以防止工具崩溃。当通过名称调用时，工具管理器动态加载工具实例，包括可执行文件的初始化和依赖关系验证。

**工具调用冲突解决。** 对于具有并行访问约束的工具，系统使用哈希映射来监控实时实例计数。请求处理涉及针对使用和并行限制的哈希映射验证；检测到冲突后，系统前进到后续队列请求，直到找到无冲突的候选。实现细节见附录A.7。

### 3.8 访问管理器

AIOS内核中的访问管理器提供以下两个关键功能。

**访问控制。** 访问管理器通过实现基于权限的访问控制机制来规范跨智能体的数据读/写操作。它将每个智能体分配到一个特定的权限组，并通过一个将智能体ID映射到其对应权限组的哈希映射架构来强制执行权限。访问请求在执行前根据此权限结构进行验证，确保智能体只能在其共享权限域内访问其他智能体的资源。

**用户干预。** 为了减轻不可逆操作（删除、覆盖、权限修改）的风险，提供了一个用户干预界面以供用户确认。这强制要求在对文件或工具执行潜在的破坏性操作之前进行明确的用户验证。实现细节见附录A.8。

### 3.9 AIOS SDK

我们设计了AIOS SDK，以简化在AIOS架构上的智能体开发和集成。该SDK不仅使开发者能够构建与AIOS内核中核心功能交互的智能体，而且还抽象了复杂的系统调用，使开发者能够专注于智能体的内部工作流程。

**工具集成。** 为了支持多样化的智能体功能，AIOS SDK集成了来自各种平台的广泛工具，并支持不同的输入输出模态。这些集成工具的详细信息见附录B.3。

**与AIOS内核的交互接口。** 为了便于利用AIOS内核中AIOS系统调用提供的功能，SDK定义了智能体可以用来调用系统调用和请求资源的不同API函数。

**智能体框架适配器。** 为了支持使用各种智能体创建框架（如Autogen（Wu et al., 2023）、Open-Interpreter（Lucas, 2024）和MetaGPT（Hong et al., 2023））构建的智能体，AIOS SDK为这些框架提供了适配器。这些适配器定位上述框架中的核心函数，并将它们重定向到AIOS中的函数。这种适配使得来自不同框架的智能体无需修改智能体代码即可在AIOS环境中运行。每个智能体框架的核心函数和具体适配的更多细节见附录B.5。

## 4 评估

在本节中，我们进行实验以回答以下研究问题。

- **RQ1：** 在同时运行多个智能体实例时，AIOS能否保持甚至提升智能体在标准基准测试上的性能？
- **RQ2：** 在服务大量基于不同智能体框架构建的智能体时，AIOS能多有效地优化系统执行吞吐量并减少响应延迟？
- **RQ3：** 随着并发运行的智能体数量增加，AIOS的可扩展性如何？

### 4.1 设置

**模型。** 我们使用GPT-4o-mini（Achiam et al., 2023）作为闭源API，并使用两个开源LLM，即Llama-3.1-8b（Dubey et al., 2024）和Mistral-7b（Jiang et al., 2023），作为LLM核心。开源模型均为指令调优版本，我们使用float16精度。

**硬件。** 我们的实验在配备NVIDIA RTX A5000 GPU（24GB）的Ubuntu 22.04机器上进行。我们使用单个A5000 GPU运行所有实验。

**智能体框架。** 我们通过运行来自多种流行智能体框架的智能体进行评估：ReAct（Yao et al., 2023）、Reflexion（Shinn et al., 2023）、Autogen（Wu et al., 2023）、Open-Interpreter（Lucas, 2024）和MetaGPT（Hong et al., 2023）。这些智能体框架的详细信息见附录B.5。

**工作负载。** 我们在资源受限的场景下进行评估，其中智能体并发运行，只有一个部署的LLM，每次只能处理一个提示请求。为了创建这些并发条件，我们默认将最大工作线程数设置为250，即最多250个智能体可以同时并发运行。增加智能体数量的影响将在第4.4节中分析。默认情况下，我们使用RR作为AIOS运行智能体的调度策略。使用其他策略（即FIFO）的影响见附录D。

### 4.2 智能体性能（RQ1）

为了评估使用AIOS对标准基准测试中智能体性能的影响，我们采用了四个智能体基准测试，即HumanEval（Chen et al., 2021a）、MINT（代码子集）（Wang et al., 2023b）、GAIA（Mialon et al., 2023）和SWE-Bench-Lite（Jimenez et al., 2024），分别在不使用和使用AIOS的情况下运行智能体。我们使用成功率（SR%）作为指标，与原始基准测试一致，并使用GPT-4o-mini作为LLM核心来运行所有智能体。我们在所有实验中将GPT-4o-mini的温度设置为1.0。基准测试设置和配置的详细描述见附录C。

如表1所示，引入AIOS能够一致地在标准基准测试中保持智能体的性能。在某些情况下，AIOS还能促进智能体性能的提升。例如，在代码生成基准测试（如MINT、HumanEval和SWE-Bench-Lite）中，AIOS通过提示增强来提升智能体性能，该增强在LLM封装器中将系统提示嵌入更具结构性的输入和输出。这些增强的提示为LLM提供了额外的上下文和结构指导，用于响应生成。在工具调用基准测试（如GAIA）中，智能体性能通过以下两种机制得到提升：执行前的参数验证（通过结构化正则表达式在工具调用执行前检查格式）和冲突解决哈希映射（以缓解并发访问问题）。

### 4.3 效率分析（RQ2）

在我们的效率实验中，我们使用两个关键指标评估系统性能：吞吐量和延迟。吞吐量通过计算每秒执行的AIOS系统调用数量来衡量，表示系统并行处理多个请求的能力。另一方面，延迟衡量智能体经历的从提交查询到完成响应的平均等待时间，反映系统的响应性。为了确保受控且一致的测试环境，我们使用两个本地托管的开源模型Llama-3.1-8b和Mistral-7b进行这些评估。本地托管这些模型减少了由于网络相关延迟问题导致的LLM API响应时间的潜在变异性。

如图6a和图7a所示，结果表明AIOS在不同智能体框架上实现了显著更高的吞吐量，在使用基于Reflexion的智能体在Llama-3.1-8b上时吞吐量提升高达2.1倍。这种改进归功于AIOS内核中采用的调度机制，它通过避免加载无法加载到GPU执行的提示来防止不必要的试错尝试。在延迟方面，如图6b和图7b所示，智能体的平均等待时间也显著减少。这种减少突出了AIOS在服务基于LLM的智能体方面的效率。

### 4.4 可扩展性分析（RQ3）

我们通过将活跃智能体从250个逐步增加到2000个来评估AIOS的可扩展性，使用Llama-3.1-8b和Mistral-7b模型在HumanEval基准测试上进行。我们复制了HumanEval的164个样本以匹配智能体数量，实现大规模并发执行。如图8所示，AIOS在总体执行时间和平均智能体等待时间方面与智能体数量保持近似线性关系。这表明即使需求增加，AIOS也能高效处理工作负载。相比之下，不使用AIOS和使用AIOS之间的执行时间和等待时间差距随着智能体数量的增加而扩大。这种不断增长的差异强调了AIOS在高并发工作负载下的可扩展性。

## 5 相关工作

操作系统（OS）的演进已从简陋系统发展为复杂的交互式系统。这种演进经历了从基本批处理（IBM, 2010）到高级进程管理（包括分时（Ritchie & Thompson, 1974）和多任务处理（Hoare, 1974; Engler et al., 1995））的转变，使得复杂任务处理成为可能。发展朝着模块化架构推进，配备了用于进程调度（Liu & Layland, 1973; Dijkstra, 2002）、内存管理（Denning, 1968; Daley & Dennis, 1968）和文件系统操作（Rosenblum & Ousterhout, 1992; McKusick et al., 1984）的专门组件，提高了系统效率。Macintosh、Windows和GNOME中图形用户界面（GUI）的引入增强了用户交互。目前，AI模型，特别是LLM，正在从应用层迁移到系统层，为跨应用提供标准化服务。

**大语言模型智能体**被用于解决复杂的规划和推理任务（Xie et al., 2024; Ge et al., 2023a）。单个智能体与数字环境或物理环境互动，可能涉及调用API（Ge et al., 2023a; Schick et al., 2023; Yao & Narasimhan, 2023; Parisi et al., 2022; Tang et al., 2023; Xie et al., 2024）、浏览网站（Nakano et al., 2022; Deng et al., 2023; Wu et al., 2024）或执行代码（Zhang et al., 2023; Yang et al.），而物理环境中的智能体可能操作物体（Brohan et al., 2023; Fan et al., 2022; Wang et al., 2023a）、进行实验室实验（Boiko et al., 2023; Bran et al., 2023）或制定可执行决策（Huang et al., 2022; Xiang et al., 2023）。基于LLM的多智能体系统（MAS）利用多个智能体之间的交互来解决问题。多个智能体之间的关系可以是合作性的（Wang et al., 2023c; Mandi et al., 2023）、竞争性的（Chan et al., 2023; Du et al., 2023）或合作与竞争的混合（Ge et al., 2023b）。在合作性多智能体系统中，每个智能体获取并评估其他智能体提供的信息，从而共同解决复杂任务，如角色扮演（Li et al., 2023; Chen et al., 2023; Zhu et al., 2023）、社会模拟（Park et al., 2023）和软件开发（Hong et al., 2023; Qian et al., 2023; Wu et al., 2023; Josifoski et al., 2023）。

## 6 结论与未来工作

本文介绍了AIOS，一种通过创新内核服务基于LLM的智能体的架构，该内核将资源和LLM服务与智能体应用隔离开来。互补的AIOS SDK使智能体应用能够高效地利用内核功能。实验验证证实，AIOS在标准基准测试中保持或提升了智能体性能，同时显著加快了执行时间，提高了系统吞吐量，并展示了随着并发智能体负载增加的可扩展性。我们期望这项工作能够催化未来的创新，完善和扩展该架构，以满足开发和部署基于LLM的智能体不断变化的需求。

## 7 致谢

我们感谢Balaji Rama、Hang Gao、Shuhang Lin、Jian Zhang和Zhenting Wang在项目期间提供的宝贵讨论和建议。

## 参考文献

Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.

Stella Biderman, Hailey Schoelkopf, Quentin Gregory Anthony, Herbie Bradley, Kyle O'Brien, Eric Hallahan, Mohammad Aflah Khan, Shivanshu Purohit, USVSN Sai Prashanth, Edward Raff, et al. Pythia: A suite for analyzing large language models across training and scaling. In International Conference on Machine Learning, pp. 2397–2430. PMLR, 2023.

Daniil A Boiko, Robert MacKnight, and Gabe Gomes. Emergent autonomous scientific research capabilities of large language models. arXiv preprint arXiv:2304.05332, 2023.

Andres M Bran, Sam Cox, Andrew D White, and Philippe Schwaller. Chemcrow: Augmenting large-language models with chemistry tools. arXiv preprint arXiv:2304.05376, 2023.

Paolo Bresciani, Anna Perini, Paolo Giorgini, Fausto Giunchiglia, and John Mylopoulos. Tropos: An agent-oriented software development methodology. Autonomous Agents and Multi-Agent Systems, 8:203–236, 2004.

Anthony Brohan, Yevgen Chebotar, Chelsea Finn, Karol Hausman, Alexander Herzog, Daniel Ho, Julian Ibarz, Alex Irpan, Eric Jang, Ryan Julian, et al. Do as i can, not as i say: Grounding language in robotic affordances. In Conference on robot learning, pp. 287–318. PMLR, 2023.

Chi-Min Chan, Weize Chen, Yusheng Su, Jianxuan Yu, Wei Xue, Shanghang Zhang, Jie Fu, and Zhiyuan Liu. Chateval: Towards better llm-based evaluators through multi-agent debate. In The Twelfth International Conference on Learning Representations, 2023.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Josh Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer, Peter Welinder, Bob McGrew, Dario Amodei, Sam McCandlish, Ilya Sutskever, and Wojciech Zaremba. Evaluating large language models trained on code. 2021a.

Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, et al. Evaluating large language models trained on code. arXiv preprint arXiv:2107.03374, 2021b.

Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chen Qian, Chi-Min Chan, Yujia Qin, Yaxi Lu, Ruobing Xie, et al. Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents. arXiv preprint arXiv:2308.10848, 2023.

Hyung Won Chung, Le Hou, Shayne Longpre, Barret Zoph, Yi Tay, William Fedus, Yunxuan Li, Xuezhi Wang, Mostafa Dehghani, Siddhartha Brahma, et al. Scaling instruction-finetuned language models. arXiv preprint arXiv:2210.11416, 2022.

Robert C Daley and Jack B Dennis. Virtual memory, processes, and sharing in multics. Communications of the ACM, 11(5):306–312, 1968.

Xiang Deng, Yu Gu, Boyuan Zheng, Shijie Chen, Samuel Stevens, Boshi Wang, Huan Sun, and Yu Su. Mind2web: Towards a generalist agent for the web. Advances in Neural Information Processing Systems, 36, 2023.

Peter J Denning. The working set model for program behavior. Communications of the ACM, 11(5):323–333, 1968.

Edsger W Dijkstra. Cooperating sequential processes. In The origin of concurrent programming: from semaphores to remote procedure calls, pp. 65–138. Springer, 2002.

Danny Driess, Fei Xia, Mehdi SM Sajjadi, Corey Lynch, Aakanksha Chowdhery, Brian Ichter, Ayzaan Wahid, Jonathan Tompson, Quan Vuong, Tianhe Yu, et al. Palm-e: an embodied multimodal language model. In Proceedings of the 40th International Conference on Machine Learning, pp. 8469–8488, 2023.

Yilun Du, Shuang Li, Antonio Torralba, Joshua B Tenenbaum, and Igor Mordatch. Improving factuality and reasoning in language models through multiagent debate. arXiv preprint arXiv:2305.14325, 2023.

Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. The llama 3 herd of models. arXiv preprint arXiv:2407.21783, 2024.

Dawson R Engler, M Frans Kaashoek, and James O'Toole Jr. Exokernel: An operating system architecture for application-level resource management. ACM SIGOPS Operating Systems Review, 29(5):251–266, 1995.

Linxi Fan, Guanzhi Wang, Yunfan Jiang, Ajay Mandlekar, Yuncong Yang, Haoyi Zhu, Andrew Tang, De-An Huang, Yuke Zhu, and Anima Anandkumar. Minedojo: Building open-ended embodied agents with internet-scale knowledge. Advances in Neural Information Processing Systems, 35:18343–18362, 2022.

Yingqiang Ge, Wenyue Hua, Kai Mei, Juntao Tan, Shuyuan Xu, Zelong Li, and Yongfeng Zhang. OpenAGI: When LLM Meets Domain Experts. Advances in Neural Information Processing Systems, 36, 2023a.

Yingqiang Ge, Yujie Ren, Wenyue Hua, Shuyuan Xu, Juntao Tan, and Yongfeng Zhang. LLM as OS, Agents as Apps: Envisioning AIOS, Agents and the AIOS-Agent Ecosystem. arXiv:2312.03815, 2023b.

Shijie Geng, Shuchang Liu, Zuohui Fu, Yingqiang Ge, and Yongfeng Zhang. Recommendation as language processing (rlp): A unified pretrain, personalized prompt & predict paradigm (p5). In Proceedings of the 16th ACM Conference on Recommender Systems, pp. 299–315, 2022.

Shibo Hao, Yi Gu, Haodi Ma, Joshua Hong, Zhen Wang, Daisy Wang, and Zhiting Hu. Reasoning with language model is planning with world model. In Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, pp. 8154–8173, 2023.

Charles Antony Richard Hoare. Monitors: An operating system structuring concept. Communications of the ACM, 17(10):549–557, 1974.

Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Jinlin Wang, Ceyao Zhang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, et al. Metagpt: Meta programming for multi-agent collaborative framework. In The Twelfth International Conference on Learning Representations, 2023.

Wenlong Huang, Pieter Abbeel, Deepak Pathak, and Igor Mordatch. Language models as zero-shot planners: Extracting actionable knowledge for embodied agents. In International Conference on Machine Learning, pp. 9118–9147. PMLR, 2022.

Corporation IBM. What is batch processing? z/OS Concepts, 2010.

Nicholas R Jennings, Katia Sycara, and Michael Wooldridge. A roadmap of agent research and development. Autonomous agents and multi-agent systems, 1:7–38, 1998.

Albert Q Jiang, Alexandre Sablayrolles, Arthur Mensch, Chris Bamford, Devendra Singh Chaplot, Diego de las Casas, Florian Bressand, Gianna Lengyel, Guillaume Lample, Lucile Saulnier, et al. Mistral 7b. arXiv preprint arXiv:2310.06825, 2023.

Carlos E Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, and Karthik R Narasimhan. SWE-bench: Can language models resolve real-world github issues? In The Twelfth International Conference on Learning Representations, 2024.

Martin Josifoski, Lars Klein, Maxime Peyrard, Yifei Li, Saibo Geng, Julian Paul Schnitzler, Yuxing Yao, Jiheng Wei, Debjit Paul, and Robert West. Flows: Building blocks of reasoning and collaborating ai. arXiv preprint arXiv:2308.01285, 2023.

Geunwoo Kim, Pierre Baldi, and Stephen McAleer. Language models can solve computer tasks. Advances in Neural Information Processing Systems, 36, 2023.

Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. Large language models are zero-shot reasoners. Advances in neural information processing systems, 35:22199–22213, 2022.

Kristina Lerman and Aram Galstyan. Agent memory and adaptation in multi-agent systems. In Proceedings of the second international joint conference on Autonomous agents and multiagent systems, pp. 797–803, 2003.

Guohao Li, Hasan Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem. Camel: Communicative agents for "mind" exploration of large language model society. Advances in Neural Information Processing Systems, 36, 2023.

Chung Laung Liu and James W Layland. Scheduling algorithms for multiprogramming in a hard-real-time environment. Journal of the ACM (JACM), 20(1):46–61, 1973.

Killian Lucas. Open interpreter. https://github.com/OpenInterpreter/open-interpreter, 2024.

Zhao Mandi, Shreeya Jain, and Shuran Song. Roco: Dialectic multi-robot collaboration with large language models. arXiv preprint arXiv:2307.04738, 2023.

Marshall K McKusick, William N Joy, Samuel J Leffler, and Robert S Fabry. A fast file system for unix. ACM Transactions on Computer Systems (TOCS), 2(3):181–197, 1984.

Grégoire Mialon, Clémentine Fourrier, Craig Swift, Thomas Wolf, Yann LeCun, and Thomas Scialom. Gaia: a benchmark for general ai assistants. arXiv preprint arXiv:2311.12983, 2023.

Reiichiro Nakano, Jacob Hilton, Suchir Balaji, Jeff Wu, Long Ouyang, Christina Kim, Christopher Hesse, Shantanu Jain, Vineet Kosaraju, William Saunders, Xu Jiang, Karl Cobbe, Tyna Eloundou, Gretchen Krueger, Kevin Button, Matthew Knight, Benjamin Chess, and John Schulman. Webgpt: Browser-assisted question-answering with human feedback, 2022.

Erik Nijkamp, Bo Pang, Hiroaki Hayashi, Lifu Tu, Huan Wang, Yingbo Zhou, Silvio Savarese, and Caiming Xiong. Codegen: An open large language model for code with multi-turn program synthesis. arXiv preprint arXiv:2203.13474, 2022.

Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, et al. Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35:27730–27744, 2022.

Charles Packer, Vivian Fang, Shishir G Patil, Kevin Lin, Sarah Wooders, and Joseph E Gonzalez. Memgpt: Towards llms as operating systems. arXiv preprint arXiv:2310.08560, 2023.

Kishore Papineni, Salim Roukos, Todd Ward, and Wei-Jing Zhu. Bleu: a method for automatic evaluation of machine translation. In Proceedings of the 40th annual meeting of the Association for Computational Linguistics, pp. 311–318, 2002.

Aaron Parisi, Yao Zhao, and Noah Fiedel. Talm: Tool augmented language models. arXiv preprint arXiv:2205.12255, 2022.

Joon Sung Park, Joseph O'Brien, Carrie Jun Cai, Meredith Ringel Morris, Percy Liang, and Michael S Bernstein. Generative agents: Interactive simulacra of human behavior. In Proceedings of the 36th Annual ACM Symposium on User Interface Software and Technology, pp. 1–22, 2023.

Chen Qian, Xin Cong, Cheng Yang, Weize Chen, Yusheng Su, Juyuan Xu, Zhiyuan Liu, and Maosong Sun. Communicative agents for software development. arXiv preprint arXiv:2307.07924, 2023.

Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu, Yankai Lin, Xin Cong, Xiangru Tang, Bill Qian, et al. Toolllm: Facilitating large language models to master 16000+ real-world apis. ICLR, 2024.

Dennis M Ritchie and Ken Thompson. The unix time-sharing system. Communications of the ACM, 17(7):365–375, 1974.

Mendel Rosenblum and John K Ousterhout. The design and implementation of a log-structured file system. ACM Transactions on Computer Systems (TOCS), 10(1):26–52, 1992.

Steven I Ross, Fernando Martinez, Stephanie Houde, Michael Muller, and Justin D Weisz. The programmer's assistant: Conversational interaction with a large language model for software development. In Proceedings of the 28th International Conference on Intelligent User Interfaces, pp. 491–514, 2023.

Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Toolformer: Language models can teach themselves to use tools. arXiv preprint arXiv:2302.04761, 2023.

Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. Reflexion: Language agents with verbal reinforcement learning. Advances in Neural Information Processing Systems, 36, 2023.

Qiaoyu Tang, Ziliang Deng, Hongyu Lin, Xianpei Han, Qiao Liang, and Le Sun. Toolalpaca: Generalized tool learning for language models with 3000 simulated cases. arXiv preprint arXiv:2306.05301, 2023.

Ross Taylor, Marcin Kardas, Guillem Cucurull, Thomas Scialom, Anthony Hartshorn, Elvis Saravia, Andrew Poulton, Viktor Kerkez, and Robert Stojnic. Galactica: A large language model for science. arXiv preprint arXiv:2211.09085, 2022.

Gemini Team, Rohan Anil, Sebastian Borgeaud, Yonghui Wu, Jean-Baptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, et al. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805, 2023.

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, et al. Llama: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023a.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, et al. Llama 2: Open foundation and fine-tuned chat models. arXiv preprint arXiv:2307.09288, 2023b.

Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, and Anima Anandkumar. Voyager: An open-ended embodied agent with large language models. In Intrinsically-Motivated and Open-Ended Learning Workshop@ NeurIPS2023, 2023a.

Xingyao Wang, Zihan Wang, Jiateng Liu, Yangyi Chen, Lifan Yuan, Hao Peng, and Heng Ji. Mint: Evaluating llms in multi-turn interaction with tools and language feedback. arXiv preprint arXiv:2309.10691, 2023b.

Zhenhailong Wang, Shaoguang Mao, Wenshan Wu, Tao Ge, Furu Wei, and Heng Ji. Unleashing cognitive synergy in large language models: A task-solving agent through multi-persona self-collaboration. arXiv preprint arXiv:2307.05300, 1(2):3, 2023c.

Michael Wooldridge and Nicholas R Jennings. Intelligent agents: Theory and practice. The knowledge engineering review, 10(2):115–152, 1995.

Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Shaokun Zhang, Erkang Zhu, Beibin Li, Li Jiang, Xiaoyun Zhang, and Chi Wang. Autogen: Enabling next-gen llm applications via multi-agent conversation framework. arXiv preprint arXiv:2308.08155, 2023.

Zhiyong Wu, Chengcheng Han, Zichen Ding, Zhenmin Weng, Zhoumianze Liu, Shunyu Yao, Tao Yu, and Lingpeng Kong. Os-copilot: Towards generalist computer agents with self-improvement. arXiv preprint arXiv:2402.07456, 2024.

Jiannan Xiang, Tianhua Tao, Yi Gu, Tianmin Shu, Zirui Wang, Zichao Yang, and Zhiting Hu. Language models meet world models: Embodied experiences enhance language models. Advances in neural information processing systems, 36, 2023.

Jian Xie, Kai Zhang, Jiangjie Chen, Tinghui Zhu, Renze Lou, Yuandong Tian, Yanghua Xiao, and Yu Su. Travelplanner: A benchmark for real-world planning with language agents. arXiv preprint arXiv:2402.01622, 2024.

John Yang, Carlos E Jimenez, Alexander Wettig, Kilian Lieret, Shunyu Yao, Karthik Narasimhan, and Ofir Press. Swe-agent: Agent-computer interfaces enable automated software engineering.

Shunyu Yao and Karthik Narasimhan. Language agents in the digital world: Opportunities and risks. princeton-nlp.github.io, 2023.

Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. ReAct: Synergizing reasoning and acting in language models. International Conference on Learning Representations, 2023.

Kechi Zhang, Ge Li, Jia Li, Zhuo Li, and Zhi Jin. Toolcoder: Teach code generation models to use apis with search tools. arXiv preprint arXiv:2305.04032, 2023.

Tianyi Zhang, Varsha Kishore, Felix Wu, Kilian Q Weinberger, and Yoav Artzi. Bertscore: Evaluating text generation with bert. arXiv preprint arXiv:1904.09675, 2019.

Zeyu Zhang, Xiaohe Bo, Chen Ma, Rui Li, Xu Chen, Quanyu Dai, Jieming Zhu, Zhenhua Dong, and Ji-Rong Wen. A survey on the memory mechanism of large language model based agents. arXiv preprint arXiv:2404.13501, 2024.

Xizhou Zhu, Yuntao Chen, Hao Tian, Chenxin Tao, Weijie Su, Chenyu Yang, Gao Huang, Bin Li, Lewei Lu, Xiaogang Wang, et al. Ghost in the minecraft: Generally capable agents for open-world enviroments via large language models with text-based knowledge and memory. arXiv preprint arXiv:2305.17144, 2023.

---

## 附录

本附录包含本文的补充细节。附录的组织如下：附录A提供AIOS内核实现细节。附录B报告更多关于AIOS SDK的内容。附录C报告更多关于智能体基准测试的细节。附录D展示更多额外的实验结果。附录E进行分析讨论。

## A AIOS内核实现细节

### A.1 AIOS系统调用

AIOS中的模块通过调用系统调用来实现其功能。表2显示了与不同模块相对应的更全面的系统调用列表，并展示了调用这些系统调用的参数。

**表2：AIOS模块及其对应的系统调用**

| 模块 | 系统调用 |
|------|---------|
| LLM核心 | execute_llm_syscall, get_model_response, process_model_response |
| 调度器 | execute_syscall, start, stop |
| 上下文管理器 | generate_response_with_interruption, load_context, clear_context |
| 内存管理器 | execute_memory_syscall, add_memory, remove_memory, update_memory, retrieve_memory |
| 存储管理器 | execute_storage_syscall, sto_create_file, sto_create_directory, sto_mount, sto_write, sto_retrieve, sto_rollback, sto_share |
| 工具管理器 | execute_tool_syscall, load_tool_instance |
| 访问管理器 | add_privilege, check_access, ask_permission |

**线程绑定。** AIOS中的每个系统调用都绑定到一个独立的线程以进行执行，从而允许并发处理。线程绑定通过继承Thread类并重写其init和run方法来实现。

```python
class SysCall(Thread):
    def __init__(self, agent_name, request_data):
        super().__init__()
        self.agent_name = agent_name
        self.request_data = request_data
        self.event = threading.Event()
        self.pid = None
        self.status = None
        self.response = None
        self.time_limit = None
        self.created_time = None
        self.start_time = None
        self.end_time = None
    
    def run(self):
        self.set_pid(self.native_id)
        self.event.wait()
```

### A.2 LLM核心

AIOS通过LLMAdapter类实现统一的接口，该类为集成来自各种后端的LLM实例提供了一致的函数接口。这种架构允许与不同的LLM提供商无缝交互，同时保持标准化的API。表3展示了AIOS框架中支持的LLM后端及其各自的功能。

**表3：AIOS中适配的LLM后端及支持的功能**

| 后端 | 结构化输出 | 函数调用 |
|------|-----------|---------|
| OpenAI（云端） | ✓ | ✓ |
| Anthropic（云端） | ✓ | ✓ |
| Google（云端） | ✓ | ✓ |
| Groq（云端） | ✓ | ✓ |
| Bedrock（云端） | ✓ | ✓ |
| Huggingface（本地） | ✓ | ✓ |
| vllm（本地） | ✓ | ✓ |
| Ollama（本地） | ✓ | ✓ |

```python
class LLMAdapter:
    # LLMAdapter类是一个抽象层，封装来自不同LLM后端的LLM核心实例
    def __init__(
        self,
        llm_configs: List[Dict[str, Any]],
        api_key: Optional[Union[str, List[str]]] = None,
        log_mode: str = "console",
        use_context_manager: bool = False,
        strategy: Optional[RouterStrategy] = RouterStrategy.Sequential,
    ):
        # 初始化LLMAdapter
        pass

    def setup_api_keys(self) -> None:
        # 从配置或环境为不同的提供商设置API密钥
        pass

    def initialize_llms(self) -> None:
        # 基于配置初始化LLM后端
        pass

    def initialize_single_llm(self, config: LLMConfig) -> None:
        # 基于其配置初始化单个LLM
        pass

    def handle_completion_error(self, error: Exception) -> LLMResponse:
        # 处理LLM补全期间发生的错误
        pass

    def execute_llm_syscall(self, llm_syscall, temperature: float = 0.0) -> LLMResponse:
        # 处理来自智能体的请求
        pass

    def get_model_response(self, model_name: str, model: Union[str, HfLocalBackend, OpenAI],
                           messages: List[Dict], tools: Optional[List], llm_syscall,
                           api_base: Optional[str] = None,
                           message_return_type: Optional[str] = "text",
                           response_format: Optional[Dict[str, Dict]] = None,
                           temperature: float = 1.0, max_tokens: int = 1000) -> Any:
        # 从模型获取响应
        pass

    def process_response(self, completed_response: str | List, finished: bool,
                         tools: Optional[List] = None,
                         model: Union[str, OpenAI, HfLocalBackend] = None,
                         message_return_type: Optional[str] = None) -> LLMResponse:
        # 将模型的响应处理为适当的格式
        pass
```

### A.3 调度器

AIOS通过BaseScheduler类实现灵活的调度器架构，该类作为各种调度策略的基础。通过设计可扩展的继承模型，专门的调度器（实现FIFO、轮转调度和基于优先级的调度等算法）可以从这个基类派生。这种模块化设计确保可以引入新的调度算法而无需修改现有实现，从而保持不同调度策略之间的强隔离，并增强整体系统的灵活性。

```python
class BaseScheduler:
    # 任务调度器实现
    def __init__(self, llm: LLMAdapter, memory_manager: MemoryManager,
                 storage_manager: StorageManager, tool_manager: ToolManager,
                 log_mode: str, get_llm_syscall: LLMRequestQueueGetMessage,
                 get_memory_syscall: MemoryRequestQueueGetMessage,
                 get_storage_syscall: StorageRequestQueueGetMessage,
                 get_tool_syscall: ToolRequestQueueGetMessage):
        # 初始化调度器
        pass

    def _execute_syscall(self, syscall: Any, executor: Any, syscall_type: str) -> Optional[Dict[str, Any]]:
        # 使用适当的状态跟踪和错误处理执行系统调用
        pass

    def process_llm_requests(self) -> None:
        # 处理来自队列的LLM请求
        pass

    def process_memory_requests(self) -> None:
        # 处理来自队列的内存请求
        pass

    def process_storage_requests(self) -> None:
        # 处理来自队列的存储请求
        pass

    def process_tool_requests(self) -> None:
        # 处理来自队列的工具请求
        pass

    def start(self) -> None:
        # 启动所有请求处理线程
        pass

    def stop(self) -> None:
        # 停止所有请求处理线程
        pass
```

### A.4 上下文管理器

SimpleContextManager实现了一种高效的机制，用于管理LLM生成上下文，具有时间感知的中断能力。该组件通过在生成阶段之间保留LLM状态来实现抢占式多任务处理。当LLM在其分配的时间片内成功开始生成词元（通过至少一个解码词元证明）时，上下文管理器捕获并保留中间生成状态。这确保了后续恢复可以从中断的确切点继续，消除了冗余计算。这种架构通过统一的接口支持各种LLM后端（OpenAI、HuggingFace等），同时在生成任务上强制执行严格的时间边界。通过管理流式响应和执行时间限制，上下文管理器有助于提高不同LLM查询之间的公平性。

```python
class SimpleContextManager(BaseContextManager):
    """
    一个简单的上下文管理器，用于处理LLM上下文的保存和加载。
    此类提供保存LLM生成当前状态、加载先前保存的状态以及管理不同进程上下文的功能。
    """
    def __init__(self):
        # 使用空上下文字典初始化SimpleContextManager
        pass

    def get_streaming_completion_response(self, model_or_client: Union[str, OpenAI],
                                           model_name: str, messages: List[Dict[str, str]],
                                           tools: Optional[List[Dict[str, Any]]],
                                           temperature: float, max_tokens: int,
                                           response_format: Optional[Dict[str, Any]] = None,
                                           stream: bool = True) -> Any:
        # 从litellm或OpenAI客户端获取补全响应
        pass

    def process_completion_streaming_response(self, response: Any, initial_content: str,
                                                time_limit: float) -> Tuple[str, bool]:
        # 处理带有时间限制执行的流式响应
        pass

    def _is_huggingface_model(self, model) -> bool:
        # 检查模型是否为HuggingFace模型实例
        pass

    def generate_with_time_limit_hf(self, model, messages: List[Dict[str, str]],
                                      max_tokens: int, temperature: float, pid: int,
                                      time_limit: float) -> Tuple[str, bool, Dict]:
        # 使用带有时间限制执行的HuggingFace模型生成文本
        pass

    def generate_response_with_interruption(self, model_name: str,
                                             model: Union[str, OpenAI, Any],
                                             messages: List[Dict[str, str]],
                                             tools: Optional[List[Dict[str, Any]]],
                                             message_return_type: str,
                                             temperature: float, max_tokens: int,
                                             pid: Union[int, str], time_limit: float,
                                             response_format: Optional[Dict[str, Any]] = None) -> Tuple[Any, bool]:
        # 保存LLM生成的上下文。此方法处理不同类型的LLM模型（基于字符串、OpenAI客户端或HuggingFace）以及不同类型的响应（文本、JSON或工具调用）。它管理流式响应并强制执行时间限制。
        pass

    def load_context(self, pid):
        # 加载先前保存的进程上下文
        pass

    def clear_context(self, pid):
        # 清除已保存的进程上下文
        pass
```

### A.5 内存管理器

内存管理器为AIOS系统提供基于RAM的内存操作，处理临时会话特定数据，这些数据在智能体会话结束时清除。它基于BaseMemoryManager类构建，通过原子操作、自动元数据同步和线程安全的访问模式提供全面的内存访问。该系统通过一整套CRUD操作和高级检索机制高效地处理内存，类似于低级编程中的指针管理，同时确保并发操作期间的数据完整性。

```python
class BaseMemoryManager:
    # 此类提供AIOS系统中内存操作的核心功能，包括添加、删除、更新和检索记忆。它充当内存访问的封装器，类似于使用低级语言中的指针。
    def __init__(self, log_mode):
        # 初始化BaseMemoryManager
        pass

    def _analyze_query_to_memory(self, query: MemoryQuery) -> 'MemoryNote':
        # 将MemoryQuery转换为MemoryNote对象
        pass

    def execute_memory_syscall(self, memory_syscall):
        # 将内存系统调用路由到适当的方法
        pass

    def add_memory(self, memory_note):
        # 向存储中添加记忆笔记
        pass

    def remove_memory(self, memory_id):
        # 从存储中移除记忆笔记
        pass

    def update_memory(self, memory_note):
        # 更新现有记忆笔记
        pass

    def get_memory(self, memory_id: str) -> 'MemoryNote':
        # 按ID检索记忆笔记
        pass

    def _retrieve_memory_raw(self, memory_query: MemoryQuery):
        # 检索与查询内容相似的记忆
        pass

    def retrieve_memory(self, memory_query: MemoryQuery):
        # 检索与查询内容相似的记忆
        pass
```

### A.6 存储管理器

存储管理器协调AIOS中的持久数据操作，结合传统文件存储与向量数据库功能。它实现了版本化文件管理、通过特定文件锁实现的线程安全访问以及语义搜索功能。存储管理器提供文件操作，包括文件管理、语义文件检索、带有回滚功能的版本控制以及文件共享。函数接口如下所示。

```python
class StorageManager:
    """
    存储管理器提供版本控制、锁定和向量数据库集成，用于高效的文件操作和检索。
    """
    def __init__(self, root_dir, use_vector_db=True, max_versions=20):
        # 使用指定的根目录和配置初始化LSFS
        pass

    def __del__(self):
        # 析构函数，在删除LSFS实例时停止文件系统观察器
        pass

    def get_file_hash(self, file_path: str) -> str:
        # 为文件路径生成SHA-256哈希
        pass

    def get_file_lock(self, file_path: str) -> threading.Lock:
        # 获取或创建特定文件路径的线程锁
        pass

    def handle_file_change(self, file_path: str, change_type: str):
        # 使用适当的锁管理处理文件更改
        pass

    def get_file_history(self, file_path: str, limit: int = None) -> list:
        # 从Redis缓存检索文件的版本历史记录
        pass

    def restore_version(self, file_path: str, version_index: int) -> bool:
        # 将文件恢复到先前的版本
        pass

    def execute_storage_syscall(self, storage_syscall):
        # 处理存储系统调用并将其路由到适当的文件系统操作
        pass

    def sto_create_file(self, file_name: str, file_path: str, collection_name: str = None) -> bool:
        # 在文件系统中创建新的空文件
        pass

    def sto_create_directory(self, dir_name: str, dir_path: str, collection_name: str = None) -> bool:
        # 在文件系统中创建新目录
        pass

    def sto_mount(self, collection_name: str, root_dir: str) -> str:
        # 为智能体挂载目录并构建向量数据库
        pass

    def sto_retrieve(self, collection_name: str, query_text: str, k: str = "3", keywords: str = None) -> list:
        # 使用语义搜索从向量数据库中检索文档
        pass

    def sto_rollback(self, file_path, n=1, time=None) -> bool:
        # 按索引或时间戳将文件回滚到先前的版本
        pass

    def generate_share_link(self, file_path: str) -> str:
        # 生成用于共享文件的可公开访问链接
        pass

    def sto_share(self, file_path: str, collection_name: str = None) -> dict:
        # 通过生成带有适当锁管理的公共访问链接来共享文件
        pass
```

### A.7 工具管理器

工具管理器模块负责加载工具并使用工具冲突预防机制执行工具。实现细节如下所示。

```python
class ToolManager:
    def __init__(self, log_mode: str = "console"):
        pass

    def execute_tool_syscall(self, tool_syscall) -> ToolResponse:
        pass

    def load_tool_instance(self, tool_org_and_name):
        pass
```

### A.8 访问管理器

访问管理器提供两个关键功能：第一是在智能体尝试访问其他智能体的资源时检查访问权限。第二是在智能体执行不可逆操作（如删除文件）之前请求用户许可。函数接口如下所示。

```python
class AccessManager:
    def __init__(self):
        pass

    def add_privilege(self, sid, tid):
        # 将智能体分配到另一个智能体的权限组
        pass

    def check_access(self, sid, tid):
        # 检查源智能体是否在目标智能体的权限组中
        pass

    def ask_permission(self, operation):
        # 在不可逆操作之前提示用户确认
        pass
```

### A.9 模块钩子

为了有效分离调用AIOS内核模块的接口与实现细节，我们采用钩子机制来初始化模块并导出必要的调用接口。以下是用于初始化模块的钩子。

```python
@validate(LLMParams)
def useLLM(params: LLMParams) -> LLM:
    """初始化并返回一个语言学习模型（LLM）实例。
    Args:
        params (LLMParams): LLM初始化所需的参数。
    Returns:
        LLM: 初始化后的LLM实例。
    """
    return LLM(**params.model_dump())

@validate(MemoryManagerParams)
def useMemoryManager(params: MemoryManagerParams) -> MemoryManager:
    """初始化并返回一个内存实例。
    Args:
        params (MemoryParams): 内存管理器初始化所需的参数。
    Returns:
        MemoryManager: 初始化后的内存管理器实例。
    """
    return MemoryManager(**params.model_dump())

@validate(StorageManagerParams)
def useStorageManager(params: StorageManagerParams) -> StorageManager:
    """初始化并返回一个存储实例。
    Args:
        params (StorageManagerParams): 存储管理器初始化所需的参数。
    Returns:
        StorageManager: 初始化后的存储管理器实例。
    """
    return StorageManager(**params.model_dump())

@validate(ToolManagerParams)
def useToolManager(params: ToolManagerParams) -> ToolManager:
    """初始化并返回一个工具实例。
    Args:
        params (ToolManagerParams): 工具管理器初始化所需的参数。
    Returns:
        ToolManager: 初始化后的工具管理器实例。
    """
    return ToolManager(**params.model_dump())
```

## B AIOS SDK

AIOS SDK通过不同的功能模块在用户设备应用和AIOS内核之间提供结构化的接口。来自这些模块的所有查询最终都通过SDK中的一个中心send_request()函数进行传输，然后通过HTTP请求（发送到本地主机或远程URL）与AIOS内核通信。从智能体开发者的角度来看，他们的智能体基本上由代码片段组成，这些代码片段可能包括智能体逻辑和与LLM、内存、存储和工具相关的资源命令，这些命令通过SDK API与各自的模块交互。这在应用程序逻辑和内核资源请求之间创建了清晰的分离。

### B.1 查询与响应

AIOS SDK定义了一个健壮的查询-响应架构，使智能体应用和AIOS内核之间能够实现无缝通信。该框架建立在两个基础数据结构之上：Query（查询）和Response（响应），它们促进了整个系统的结构化数据交换。

**查询结构。** Query类充当所有输入请求的抽象基类，为智能体与内核的交互建立了一致的接口。它分支为四个专门的实现：

- **LLMQuery：** 促进自然语言交互，具有可配置的温度、词元限制参数，以及包括聊天、JSON输出、工具调用和文件操作在内的多种操作类型。
- **MemoryQuery：** 处理瞬态数据操作，包括添加、检索、更新和删除记忆，并专门支持智能体记忆管理。
- **StorageQuery：** 通过参数化的文件和目录操作请求来管理持久化存储操作。
- **ToolQuery：** 通过结构化的工具调用启用对外部能力的访问，扩展系统的功能。

**响应结构。** Response类为来自AIOS内核的标准化输出提供了互补的结构。每个响应类型对应其查询对应项：

- **LLMResponse：** 返回语言模型操作生成的文本、工具调用结果、完成状态和错误信息。
- **MemoryResponse：** 提供记忆管理功能相关的记忆内容、元数据、搜索结果和操作状态。
- **StorageResponse：** 提供存储相关活动的操作结果、完成状态和错误详情。
- **ToolResponse：** 返回外部工具操作的工具执行结果、完成状态和错误信息。

```python
class Query(BaseModel):
    """
    AIOS系统中所有查询类型的基类。
    此类作为专用查询类（如LLMQuery、MemoryQuery、StorageQuery和ToolQuery）的基础。
    它定义了AIOS生态系统中有效查询所需的最小结构。
    Attributes:
        query_class: 查询类型的标识符，必须为["llm", "memory", "storage", "tool"]之一
    """
    query_class: Literal["llm", "memory", "storage", "tool"]

class Response(BaseModel):
    """
    AIOS系统中所有响应类型的基类。
    此类作为专用响应类（如LLMResponse、MemoryResponse、StorageResponse和ToolResponse）的基础。
    它定义了AIOS生态系统中有效响应所需的最小结构。
    """
    response_class: Literal["llm", "memory", "storage", "tool"]

class LLMQuery(Query):
    query_class: str = "llm"
    llms: Optional[List[Dict[str, Any]]] = Field(default=None)
    messages: List[Dict[str, Union[str, Any]]]
    tools: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    action_type: Literal["chat", "chat_with_json_output", "chat_with_tool_call_output", "call_tool", "operate_file"] = Field(default="chat")
    temperature: float = Field(default=1.0)
    max_new_tokens: int = Field(default=1000)
    message_return_type: Literal["text", "json"] = Field(default="text")
    response_format: Optional[Dict[str, Any]] = Field(default=None)
    class Config:
        arbitrary_types_allowed = True

class LLMResponse(Response):
    """
    LLM操作的响应类。
    此类表示执行LLM操作后的输出结构。
    """
    response_class: str = "llm"
    response_message: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200
    class Config:
        arbitrary_types_allowed = True

class MemoryQuery(Query):
    """
    内存操作的查询类。
    """
    query_class: str = "memory"
    operation_type: Literal["add_memory", "get_memory", "update_memory", "remove_memory", "retrieve_memory", "add_agentic_memory", "retrieve_memory_raw"]
    params: Dict[str, Any] = Field(default_factory=dict)
    class Config:
        arbitrary_types_allowed = True

class MemoryResponse(Response):
    """
    内存操作的响应类。
    """
    response_class: str = "memory"
    memory_id: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    search_results: Optional[List[Dict[str, Any]]] = None
    success: bool = False
    error: Optional[str] = None
    class Config:
        arbitrary_types_allowed = True

class StorageQuery(Query):
    """
    存储操作的查询类。
    """
    query_class: str = "storage"
    params: Dict[str, Union[str, Any]]
    operation_type: str = Field(default="text")
    class Config:
        arbitrary_types_allowed = True

class StorageResponse(Response):
    """
    存储操作的响应类。
    """
    response_class: str = "storage"
    response_message: Optional[str] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200

class ToolQuery(Query):
    """
    工具操作的查询类。
    """
    query_class: str = "tool"
    tool_calls: List[Dict[str, Union[str, Any]]]
    class Config:
        arbitrary_types_allowed = True

class ToolResponse(Response):
    """
    工具操作的响应类。
    """
    response_class: str = "tool"
    response_message: Optional[str] = None
    finished: bool = False
    error: Optional[str] = None
    status_code: int = 200
```

### B.2 AIOS SDK API

AIOS SDK还提供了多个使用Query和Response数据结构以及send_request()函数构建的API函数。可用的API如表4所示。

**表4：AIOS SDK API**

| 模块 | API |
|------|-----|
| LLM核心 | llm_chat, llm_chat_with_json_output, llm_chat_with_tool_call_output, llm_call_tool, llm_operate_file |
| 内存 | create_memory, get_memory, delete_memory, update_memory, search_memories |
| 存储 | mount, retrieve_file, create_file, create_dir, write_file, rollback_file, share_file |
| 工具 | call_tool |

### B.3 支持的工具

如表5所示，AIOS SDK集成了多样化的计算工具，以解决广泛的信息处理任务。该SDK包含17个原生工具，涵盖多种模态和功能，支持跨文本、图像和音频领域的复杂交互模式。这些工具可以分为三个主要来源：成熟的技术提供商（Google、Bing、WolframAlpha）、专门的API中心（Rapid API Hub）和高级AI模型提供商（Huggingface）。

该工具包的架构在基于文本的操作方面展现出特别的优势，有12个工具支持文本输入或输出模态。这包括基本信息检索服务（Arxiv、BingSearch、Wikipedia）、专门的分析工具（CurrencyConverter、MoonPhaseSearch）以及特定领域的应用程序（ImdbRank、TripAdvisor）。此外，该SDK还通过VisualQuestionAnswering（图像-文本集成）、TextToAudio（文本到语音合成）和VoiceActivityRecognition（语音到文本转换）等工具展现出强大的跨模态能力。

**表5：AIOS SDK支持的工具（按名称字母顺序排列）**

| 工具名称 | 来源 | 类型 | 模态（输入→输出） |
|---------|------|------|-----------------|
| Arxiv | Arxiv API | 文本→文本 |
| BingSearch | Bing API | 文本→文本 |
| CurrencyConverter | Rapid API Hub API | 文本→文本 |
| GooglePlace | Google API | 图像/文本→文本 |
| GoogleSearch | Google API | 文本→图像 |
| ImageCaption | Huggingface 本地模型/API | 文本→文本 |
| ImdbRank | Rapid API Hub API | 文本→文本 |
| MoonPhaseSearch | Rapid API Hub API | 文本→文本 |
| Shazam | Rapid API Hub API | 文本→文本/音频 |
| TextToAudio | Huggingface 本地模型/API | 文本→音频 |
| TextToImage | Huggingface 本地模型/API | 文本→图像 |
| TripAdvisor | Rapid API Hub API | 文本→文本 |
| VisualQuestionAnswering | Huggingface 本地模型/API | 图像和文本→文本 |
| VoiceActivityRecognition | Huggingface 本地模型/API | 音频→文本 |
| Wikipedia | Wikipedia API | 文本→文本 |
| WolframAlpha | WolframAlpha API | 文本→文本 |
| WordsAPI | Rapid API Hub API | 文本→文本 |

### B.4 智能体示例

以下是我们利用AIOS SDK开发的智能体示例。

**旅行智能体（TravelAgent）：** 旅行智能体专为行程规划而设计，包括搜索航班、住宿和当地活动。

**推荐智能体（RecAgent）：** 推荐智能体专为推荐电影和电视剧而设计。

**数学智能体（MathAgent）：** 该智能体专为解决方程、执行计算和为不同数学问题提供逐步解释而设计。

**创作智能体（CreationAgent）：** 创作智能体专为内容生成任务而设计，如写作、图形设计甚至视频编辑。

**学术智能体（AcademicAgent）：** 学术智能体专为支持研究和学习而设计，如文献综述和复杂学术主题的解释。

**TravelAgent配置文件**

描述：您是一位规划和管理旅行行程的专家。

工作流程：
1. 确定目的地并使用酒店位置搜索工具搜索酒店位置。
2. 根据酒店位置，使用酒店搜索工具查找合适的酒店，并选择最佳酒店。
3. 使用获取酒店详情工具获取所选酒店的详细信息。
4. 使用机场搜索工具搜索出发地最近的机场。
5. 使用机场搜索工具搜索目的地最近的机场。
6. 使用正确的日期通过航班搜索工具查找前往目的地机场的可用航班。
7. 使用餐厅位置搜索工具搜索目的地附近的餐厅位置。
8. 根据餐厅位置，使用餐厅搜索工具查找合适的餐厅。
9. 使用获取餐厅详情工具获取所选餐厅的详细信息。
10. 使用Wikipedia工具收集用户访问目的地的其他相关信息。
11. 整合之前步骤收集的信息，提供全面的旅行计划。

可用工具：
1. TripAdvisor
2. Wikipedia

任务输入示例：我想从2024年7月4日至7月10日去法国巴黎旅行，我从纽约市出发。请帮我规划这次旅行。

**RecAgent配置文件**

描述：您是一位擅长推荐电视剧和电影的专家。

工作流程：
1. 确定需要调用哪个工具来获取信息。
2. 根据信息，基于约束条件为用户提供推荐。

可用工具：
1. TripAdvisor
2. Wikipedia

任务输入示例：推荐三部来自过去五年、排名在1到20之间、评分在8.0以上的动作电影。

**CreationAgent配置文件**

描述：您是一位擅长内容创作的专家。

工作流程：
1. 将内容需求的模糊描述转换为具体对象并补充更多细节。
2. 根据填充的细节确定要调用哪个工具来创建内容。

可用工具：
1. SDXL-Turbo

任务输入示例：创建一张时尚、高科技未来城市且具有充满活力的夜生活氛围的图片。

**MathAgent配置文件**

描述：您是一位擅长解决数学问题的专家。

工作流程：
1. 确定调用哪个工具进行预计算。
2. 使用预计算的结果执行数学运算，可能涉及与其他数值进行加法、减法、乘法或除法来解决问题。

可用工具：
1. Currency Converter
2. WolframAlpha

任务输入示例：将15000墨西哥比索转换为加拿大元，如果1加元等于0.79美元，计算出相当于多少美元。

**AcademicAgent配置文件**

描述：您是一位擅长查找和获取学术文章信息的专家。

工作流程：
1. 根据学术需求确定要调用的工具并调用该工具。
2. 收集从工具获取的信息，撰写大纲或总结。

可用工具：
1. Arxiv API

任务输入示例：总结2018年至2023年间关于人工智能在药物发现中作用的最新研究。

### B.5 智能体框架支持

将现有智能体框架构建的智能体适配到AIOS的核心思想是识别将与系统资源交互的核心函数，并将其替换为我们的原生适配器中的函数。在本节中，我们说明了需要更改的关键适配函数，以便在AIOS上运行由其他智能体框架构建的智能体。

**ReAct（Yao et al., 2023）。** ReAct框架将语言模型中的推理和行动步骤结合起来，允许模型生成中间推理轨迹以及可操作步骤，以完成复杂任务。这种双重方法帮助模型不仅规划和跟踪其思维过程，还能与外部工具交互，提高了在问答、游戏环境和需要多步推理和适应性的决策问题等任务上的性能。通过在推理和行动之间交替，ReAct减少了单纯预测性响应的错误，并实现了更准确、上下文感知的任务完成。

**Reflexion（Shinn et al., 2023）。** Reflexion框架通过反馈驱动机制增强语言智能体，使其能够通过自我反思的反馈循环从错误中学习并调整行为。通过利用口头强化学习，智能体评估和调整其行动，通过迭代学习提高复杂任务的性能。这种方法使语言智能体更具韧性和适应性，使其能够处理具有变化需求和不确定性的任务。

**Autogen（Wu et al., 2023）。** AutoGen引入了一个框架，利用具有不同角色（如规划者、执行者和反射器）的多个语言模型智能体，通过结构化的、目标导向的对话协作解决复杂任务。通过使智能体能够通信和共享中间结果，AutoGen协调多步骤流程，如数据分析、决策和迭代问题解决，显著提高了超越单个模型能力的效率和准确性。这种方法赋能下一代应用程序，使LLM能够处理动态工作流程，适应任务特定的细微差别，并在真实世界场景中实现更高的性能。以下是适配Autogen到AIOS的代码。由于Autogen团队正在进行重构工作，仅支持Autogen-0.2（最新稳定版本）。

```python
@add_framework_adapter("AutoGen~0.2")
def prepare_autogen_0_2():
    """
    将OpenAIWrapper和ConversableAgent方法替换为AIOS的实现。
    此函数用于将autogen的API适配到AIOS的API，由AIOS内部使用。
    """
    # 替换OpenAIWrapper方法
    OpenAIWrapper.__init__ = adapter_autogen_client_init
    OpenAIWrapper.create = adapter_client_create
    OpenAIWrapper.extract_text_or_completion_object = adapter_client_extract_text_or_completion_object
    # 替换智能体方法
    ConversableAgent._print_received_message = _adapter_print_received_message
    ConversableAgent._generate_oai_reply_from_client = _adapter_generate_oai_reply_from_client
    ConversableAgent.generate_tool_calls_reply = adapter_generate_tool_calls_reply
    ConversableAgent.execute_function = adapter_execute_function
    ConversableAgent._a_execute_tool_call = _adapter_a_execute_tool_call
    ConversableAgent.update_tool_signature = adapter_update_tool_signature
    ConversableAgent.__init__ = adapter_autogen_agent_init
```

**Open-Interpreter（Lucas, 2024）。** Open Interpreter是一个开源框架，使用户能够通过类似ChatGPT的界面与LLM交互，直接在终端中解释和执行跨编程语言的复杂指令。它支持本地托管和基于云的LLM，使自然语言中的代码执行和调试变得流畅。通过将自然语言指令转换为可执行代码，Open Interpreter提供了一个直观的环境，不仅简化了开发工作流程，还通过为各种编码挑战提供详细解释和交互式支持来促进学习，使其适用于所有技能水平的开发者。以下是需要为Open-Interpreter适配的核心函数。

```python
@add_framework_adapter("Open-Interpreter")
def prepare_interpreter():
    # 准备解释器以在AIOS中运行LLM
    # 设置解释器中的补全函数
    interpreter.llm.completions = adapter_aios_completions

def adapter_aios_completions(**params):
    # AIOS补全替换解释器中的fixed_litellm_completions
    # 运行补全
    attempts = 2
    first_error = None
    for attempt in range(attempts):
        try:
            send_request = get_request_func()
            response = send_request(
                query=LLMQuery(
                    messages=params['messages'],
                    tools=(params["tools"] if "tools" in params else None)
                )
            )["response"]
            # 格式类似于解释器中的补全
            comletion = {'choices':[{'delta': {}}]}
            comletion["choices"][0]["delta"]["content"] = response["response_message"]
            if response.tool_calls is not None:
                comletion["choices"][0]["delta"]["tool_calls"] = format_tool_calls_to_interpreter(response["tool_calls"])
            return [comletion]  # 如果补全成功，退出函数
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)
        except Exception as e:
            if attempt == 0:
                # 存储第一个错误
                first_error = e
    if first_error is not None:
        raise first_error
```

**MetaGPT（Hong et al., 2023）。** MetaGPT提出了一种元编程方法，通过集成面向任务的编程范式来优化LLM驱动的多智能体系统，用于复杂的协作问题解决。MetaGPT将标准操作程序（SOP）直接编码到结构化的提示序列中，创建了精简的工作流程，赋予智能体人类般的领域专业知识，以系统性地验证中间输出并主动减轻错误。沿着这条思路，MetaGPT解决了现有基于LLM的框架的局限性，如幻觉和智能体链式推理过程中的级联错误。该框架有利于将复杂任务分解为可管理的、相互依赖的子任务，提高了整体系统的鲁棒性，特别是在可靠性对智能体交互至关重要的高风险的迭代过程中。以下是需要为MetaGPT适配的核心函数。

```python
@add_framework_adapter("MetaGPT")
def prepare_metagpt():
    """
    准备metagpt模块以在AIOS上运行。
    """
    prepare_metagpt_config()
    BaseLLM.aask = adapter_aask

async def adapter_aask(self, msg: Union[str, list[dict[str, str]]],
                       system_msgs: Optional[list[str]] = None,
                       format_msgs: Optional[list[dict[str, str]]] = None,
                       images: Optional[Union[str, list[str]]] = None,
                       timeout=USE_CONFIG_TIMEOUT, stream=True) -> str:
    rsp = await adapter_acompletion_text(message, stream=stream, timeout=self.get_timeout(timeout))
    return rsp if rsp else ""
```

## C 智能体基准测试详情

### C.1 HumanEval

作者（Chen et al., 2021b）¹引入了HumanEval，一个包含164个手写编程问题的基准数据集，用于评估代码生成模型的功能正确性。每个问题包括函数签名、文档字符串、实现主体和综合测试套件，平均每个问题有7.7个测试用例。这些问题的手写性质至关重要，因为现代语言模型通常在包含现有编程挑战和竞赛问题解决方案的大规模GitHub代码上进行训练。HumanEval旨在评估代码生成能力的多个方面：自然语言理解、逻辑推理、算法思维和数学运算。通过这个公开可用的基准测试，研究人员可以对代码生成模型进行严格和标准化的评估。

¹数据集可在 https://www.github.com/openai/human-eval 找到。

### C.2 MINT

MINT（Wang et al., 2023b）²引入了一个基准测试，用于评估LLM通过多轮交互解决挑战性任务的能力。该基准测试专注于需要LLM利用工具并结合自然语言反馈的代码生成、决策制定和推理任务。MINT通过整理多个单轮数据集构建，将原始的29,307个实例精简为586个精心挑选的示例。该基准测试使用成功率（SR）作为其主要评估指标，衡量成功完成任务的百分比。对于从1到5的给定交互限制k，每个LLM最多允许k轮交互，性能以SR@k衡量。在我们的实验中，我们设置k=5，并专门关注MINT的代码生成子集。

²https://xwang.dev/mint-bench/

### C.3 GAIA

通用AI助手（GAIA）（Mialon et al., 2023）³是一个基准测试，旨在通过评估通用智能所需的基本能力来代表AI研究的一个重要里程碑。与专注于专业领域知识的传统基准测试不同，GAIA强调需要核心能力的日常任务，包括逻辑推理、多模态处理、网页导航和有效工具利用。GAIA包含466个问题，评估AI助手在推理、多模态理解、编码和工具使用（特别是网页浏览）等多种能力，涉及各种数据格式的任务，如PDF、电子表格、图像、视频和音频。该基准测试根据所需步骤和工具的数量将问题组织为三个难度级别：Level 1需要最少的工具使用（≤5步），Level 2需要多种工具和5-10步，而Level 3通过复杂的多步序列测试高级通用辅助能力，需要多样化的工具组合。此外，虽然网页浏览是GAIA的核心，但该基准测试故意排除了复杂的网页交互（如文件上传或发表评论），将这些评估留待未来研究。

³https://huggingface.co/gaia-benchmark

### C.4 SWEBench-Lite

SWE-bench（Jimenez et al., 2024）⁴是一个软件工程基准测试，通过严格的三阶段流程构建，该流程处理来自12个流行的Python代码仓库的GitHub拉取请求（PR）。该流程基于属性（问题解决和测试贡献）和执行标准（成功安装和失败到通过的测试转换）过滤约90,000个PR，得到2,294个高质量任务实例。每个任务要求模型生成解决软件问题的补丁文件，成功与否由全面的测试覆盖率决定。该基准测试通过真实世界的挑战、广泛的输入上下文（平均每个问题195个词）、跨上下文编辑要求（通常涉及1.7个文件和32.8行每解决方案）以及基于测试的稳健评估而脱颖而出。值得注意的是，SWE-bench的自动化收集过程使得能够不断从GitHub代码仓库更新新的任务实例，确保基准测试随时间保持相关性。

⁴https://www.swebench.com/

## D 额外实验结果

### D.1 效率分析

我们还报告了在Llama-3.1-8b和Mistral-7b上运行其他三个基准测试的智能体的吞吐量和延迟，比较使用AIOS和不使用AIOS的情况。结果分别如图10和图11、图12和图13、图14和图15所示。

**不同调度策略的影响。** 为了进一步分析不同调度策略对系统效率的影响，我们在HumanEval基准测试上使用ReAct构建的智能体和Llama-3.1-8b模型进行了消融研究。我们测试了三种策略：不使用AIOS、FIFO和轮转调度（RR），并测量了总体执行时间和智能体等待时间（平均值和p90）。

如表6所示，FIFO策略相比其他策略实现了最短的总体执行时间。RR在总体执行和平均智能体等待时间方面位居第二，因为其上下文切换引入了额外的开销。然而，由于其更公平的调度方法，RR在p90指标（即90%的等待时间低于该值）上表现更好，这减少了后续任务可能经历更长等待时间的可能性，这种情况在FIFO中通常会发生。

**表6：使用不同调度策略的影响，其中NONE表示不使用AIOS，FIFO和RR表示使用AIOS的两种不同调度策略。所有指标以秒为单位报告。**

| 策略 | 总体执行时间 | 智能体等待时间（平均） | 智能体等待时间（p90） |
|------|------------|-------------------|-------------------|
| None | 152.1 | 9.8 | 11.0 |
| FIFO | 74.2 | 3.0 | 5.0 |
| RR | 77.3 | 3.2 | 4.2 |

### D.2 上下文切换的正确性

为了评估上下文管理器支持的上下文切换的正确性，我们使用BLEU分数（Papineni et al., 2002）和BERT分数（Zhang et al., 2019）来衡量文本相似度。相似度是针对相同条件下为相同智能体生成的最终输出计算的，仅根据上下文切换启用和禁用来变化。如表7所示，BLEU和BERT分数均达到了1.0。这表明上下文切换不会在输出质量上引入差异，证明了AIOS的可靠性。

**表7：上下文切换的正确性（基于文本和基于logits），检查启用和禁用上下文切换时生成的最终输出之间的相似性。**

| LLM核心 | 方法 | BLEU分数 | BERT分数 |
|---------|------|---------|---------|
| Mistral-7B | 基于文本 | 1.0 | 1.0 |
| | 基于logits | 1.0 | 1.0 |
| Llama-3-8B | 基于文本 | 1.0 | 1.0 |
| | 基于logits | 1.0 | 1.0 |

## E 讨论

### E.1 伦理考量

在本节中，我们讨论本工作潜在的正向和负向社会影响。

潜在的正向社会影响包括：1）增强效率和生产力：AIOS可以自动化常规任务，实现更高效的操作，优化资源分配，减少瓶颈，为智能体开发者带来更好的服务和更高的效率；2）改善用户体验：通过更好的上下文、内存和存储管理，AIOS可以提供更加个性化和响应式的交互，提升各种应用中的用户满意度；3）创新生态系统：AIOS的创建可以促进智能体开发者和研究人员的繁荣生态系统，推动AI技术和应用的创新。

潜在的负向社会影响包括：1）隐私问题：将LLM集成到操作系统中可能引发隐私问题，因为AI模型（如LLM）可能需要访问个人数据以提供有效的服务；2）安全风险：随着AI系统对关键基础设施变得更加重要，它们可能成为网络攻击的目标，可能危及敏感数据和操作；3）系统故障：集成系统的故障可能产生广泛的后果，同时影响多个部门并造成中断。

平衡影响：为了最大化积极影响并减轻负面影响，采取平衡的方法来开发和部署AIOS至关重要，例如：1）规则和标准：实施负责任的开发规则和标准，确保数据隐私、安全和AI的伦理使用；2）健壮的设计：实施健壮的系统设计、定期维护、全面测试、持续监控、备份和恢复计划、开发者培训、详尽的文档、清晰的沟通，以及利用AI进行预测性维护和自动恢复；3）公众参与：与公众互动，提高对AI的好处和挑战的认识，确保社会关切在开发过程中得到解决。

通过解决这些考量，社会可以利用AIOS的潜力，同时减轻其风险，引领一个更加公平和繁荣的未来。

### E.2 未来方向

以AIOS作为基础，未来研究有许多方向可以探索。本节概述了在AIOS基础上扩展的潜在研究领域。

**语义调度算法。** AIOS的调度功能为开发更高级的算法奠定了基础。未来的研究可以关注对智能体请求进行依赖分析的算法，优化计算资源的分配。此外，一些工具资源是本地部署的模型，也可以纳入调度范式。这包括工具状态和快照的管理，表明朝着统一调度框架（涵盖智能体及其工具）发展的趋势。

**上下文管理的效率。** 可以设计更高效的机制来辅助上下文管理。例如，追求时间高效的上下文管理技术可以通过加速上下文快照和恢复过程来显著增强用户体验。此外，在快照之前利用上下文压缩技术可以产生更节省空间的解决方案。

**内存和存储架构的优化。** 在智能体协作和通信的背景下，未来内存和存储系统的设计可以采用共享方法，使智能体之间能够共享内存和存储。这种架构将使智能体能够访问公共的内存和存储池，从而提高智能体的决策能力，因为一个智能体可以从其他智能体的内存或存储中受益。此外，未来的工作可以探索分层存储解决方案，旨在优化数据检索和存储效率。这可能涉及为频繁访问的数据优先提供更快的访问和更少的存储分配，而对较少访问的信息则相反。

**安全与隐私增强。** AIOS安全方面需要针对各种攻击的保护措施，确保系统对恶意攻击的抵抗力，例如LLM的越狱攻击或未经授权访问其他智能体的内存。在隐私领域，探索先进的加密技术对于保护AIOS内的数据传输至关重要，从而维护智能体通信的机密性。此外，水印技术的实施可以通过在输出中嵌入唯一标识符来保护智能体开发者的知识产权，便于数据溯源追踪。

简而言之，AIOS是一项具有激励作用的工作，带来了广泛的研究机会。每个提出的方向不仅可以在AIOS的基础元素上构建，还可以为该领域的整体进步做出贡献。
