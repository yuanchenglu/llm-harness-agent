# 思维树：基于大型语言模型的审慎问题求解

**Shunyu Yao**（普林斯顿大学）  
**Dian Yu**（Google DeepMind）  
**Jeffrey Zhao**（Google DeepMind）  
**Izhak Shafran**（Google DeepMind）  
**Thomas L. Griffiths**（普林斯顿大学）  
**Yuan Cao**（Google DeepMind）  
**Karthik Narasimhan**（普林斯顿大学）  

*第37届神经信息处理系统大会（NeurIPS 2023）*  
*arXiv:2305.10601v2 [cs.CL] 2023年12月3日*

## 摘要

语言模型越来越多地被部署用于跨广泛任务的通用问题求解，但在推理过程中仍然局限于词元级别、从左到右的决策过程。这意味着它们在需要探索、战略性前瞻或初始决策起关键作用的任务中可能会表现不足。为了克服这些挑战，我们提出了一个新的语言模型推理框架——"思维树"（Tree of Thoughts，ToT），它推广了流行的"思维链"（Chain of Thought）提示方法，并使得能够对作为问题求解中间步骤的连贯文本单元（"思维"）进行探索。ToT 允许语言模型通过考虑多个不同的推理路径、自我评估选择以决定下一步行动，以及在必要时进行前瞻或回溯以做出全局选择，从而执行审慎的决策。我们的实验表明，ToT 在三个需要非平凡规划或搜索的新任务上显著增强了语言模型的问题求解能力：24点游戏、创意写作和小型纵横填字游戏。例如，在24点游戏中，使用思维链提示的 GPT-4 仅解决 4% 的任务，而我们的方法实现了 74% 的成功率。包含所有提示的代码仓库：https://github.com/princeton-nlp/tree-of-thought-llm。

## 1 引言

最初设计用于生成文本的、规模化后的语言模型（如 GPT [25, 26, 1, 23] 和 PaLM [5]）已被证明在越来越多的需要数学、符号、常识和知识推理的任务中表现出越来越强的能力。也许令人惊讶的是，所有这些进步的基础仍然是原始的自回归文本生成机制——它逐个地、从左到右地做出词元级别的决策。这样一个简单的机制是否足以让语言模型构建成为一个通用的问题求解器？如果不是，什么问题会挑战当前的范式，又应该采用什么替代机制？

关于人类认知的文献为回答这些问题提供了一些线索。对"双过程"模型的研究表明，人类在决策时有两种模式——一种快速、自动、无意识的模式（"系统1"）和一种缓慢、审慎、有意识的模式（"系统2"）[30, 31, 16, 15]。这两种模式此前已被联系到机器学习中使用的各种数学模型。例如，对人类和其他动物的强化学习的研究探索了它们在何种情况下进行联想性的"无模型"学习或更具审慎性的"基于模型"的规划 [7]。语言模型的简单联想性词元级别选择也让人联想到"系统1"，因此可能受益于更具审慎性的"系统2"规划过程的增强，该过程能够（1）维持并探索当前选择的多种不同替代方案，而不是仅仅选择一个；以及（2）评估当前状态并主动前瞻或回溯以做出更全局的决策。

为了设计这样一个规划过程，我们回到人工智能（以及认知科学）的起源，从 Newell、Shaw 和 Simon 自20世纪50年代开始探索的规划过程中汲取灵感 [21, 22]。Newell 及其同事将问题求解 [21] 描述为通过一个组合问题空间的搜索，该空间以树的形式表示。因此，我们提出了用于语言模型通用问题求解的思维树（ToT）框架。如图1所示，现有的方法（下文详述）对连续语言序列进行采样以解决问题，而 ToT 则主动维护一棵思维树，其中每个思维是一个连贯的语言序列，作为问题求解的中间步骤（表1）。这种高层语义单元允许语言模型通过一个同样在语言中实例化的审慎推理过程，来自我评估不同中间思维在解决问题方面的进展（图2、4、6）。这种通过语言模型自我评估和审慎推理来实现搜索启发式的方法是新奇的，因为以往的搜索启发式要么是编程实现的，要么是学习得到的。最后，我们将这种基于语言生成和评估多样思维的能力与搜索算法（如广度优先搜索 BFS 或深度优先搜索 DFS）相结合，这些算法允许通过前瞻和回溯来系统地探索思维树。

在实验方面，我们提出了三个即使使用最先进的语言模型 GPT-4 [23] 也对现有语言模型推理方法构成挑战的新问题：24点游戏、创意写作和纵横填字游戏（表1）。这些任务需要演绎、数学、常识和词汇推理能力，以及整合系统规划或搜索的方法。我们展示了 ToT 在所有三个任务上取得了优越的结果，因为它足够通用和灵活，可以支持不同层次的思维、不同的思维生成和评估方式，以及适应不同问题性质的不同搜索算法。我们还通过系统的消融实验分析了这些选择如何影响模型性能，并讨论了更好地训练和使用语言模型的未来方向。

## 2 背景

我们首先形式化一些使用大型语言模型进行问题求解的现有方法，我们的方法受其启发，并在后续与之进行比较。我们用 $p_\theta$ 表示一个具有参数 $\theta$ 的预训练语言模型，用小写字母 $x, y, z, s, \cdots$ 表示一个语言序列，即 $x = (x[1], \cdots, x[n])$，其中每个 $x[i]$ 是一个词元，因此 $p_\theta(x) = \prod_{i=1}^n p_\theta(x[i] | x[1...i])$。我们用大写字母 $S, \cdots$ 表示语言序列的集合。

**输入-输出（IO）提示** 是将问题输入 $x$ 转化为输出 $y$ 的最常见方式：$y \sim p_\theta(y | \text{prompt}_{IO}(x))$，其中 $\text{prompt}_{IO}(x)$ 将输入 $x$ 与任务指令和/或少样本输入-输出示例包装在一起。为简便起见，让我们记 $p_\theta^{\text{prompt}}(\text{output} | \text{input}) = p_\theta(\text{output} | \text{prompt}(\text{input}))$，这样 IO 提示可以形式化为 $y \sim p_\theta^{IO}(y | x)$。

**思维链（CoT）提示** [38] 被提出用于处理输入 $x$ 到输出 $y$ 的映射非平凡的情况（例如，当 $x$ 是一个数学问题而 $y$ 是最终的数值答案时）。关键思想是引入思维链 $z_1, \cdots, z_n$ 来桥接 $x$ 和 $y$，其中每个 $z_i$ 是一个连贯的语言序列，作为通向问题求解的有意义的中间步骤（例如，$z_i$ 可以是数学问答的中间方程式）。为了用 CoT 解决问题，每个思维 $z_i \sim p_\theta^{CoT}(z_i | x, z_{1...i-1})$ 被顺序采样，然后输出 $y \sim p_\theta^{CoT}(y | x, z_{1...n})$。在实践中，$[z_{1...n}, y] \sim p_\theta^{CoT}(z_{1...n}, y | x)$ 被作为一个连续的语言序列采样，而思维的分解（例如每个 $z_i$ 是一个短语、一个句子还是一个段落）是模糊的。

**带自一致性的 CoT（CoT-SC）** [36] 是一种集成方法，它采样 $k$ 条独立同分布的思维链：$[z_{1...n}^{(i)}, y^{(i)}] \sim p_\theta^{CoT}(z_{1...n}, y | x)$（$i = 1 \cdots k$），然后返回最频繁的输出：$\arg\max_y \#\{i | y^{(i)} = y\}$。CoT-SC 改进了 CoT，因为对于同一个问题通常有不同的思维过程（例如，证明同一个定理的不同方式），通过探索更丰富的思维集合，输出的决策可以更加可靠。然而，在每条链内部，没有对不同思维步骤的局部探索，而且"最频繁"启发式仅当输出空间有限时（例如多项选择问答）才适用。

## 3 思维树：语言模型的审慎问题求解

> 真正的问题求解过程涉及反复使用可用信息来启动探索，这反过来揭示更多信息，直到最终发现解决问题的方法。—— Newell 等 [21]

对人类问题求解的研究表明，人们通过一个组合问题空间进行搜索——这是一个树，其中节点代表部分解，分支代表修改这些解的操作符 [21, 22]。选择哪个分支由启发式方法决定，这些方法帮助导航问题空间并引导问题求解者走向解决方案。这一视角突显了现有使用语言模型解决通用问题的方法的两个关键缺陷：1）局部上，它们不会在一个思维过程中探索不同的延续——即树的分支。2）全局上，它们没有整合任何类型的规划、前瞻或回溯来帮助评估这些不同的选项——而这是人类问题求解中似乎特有的启发式引导搜索。

为了解决这些缺陷，我们引入了思维树（ToT），这是一种允许语言模型在思维上探索多个推理路径的范式（图1(c)）。ToT 将任何问题框架化为在一棵树上进行搜索，其中每个节点是一个状态 $s = [x, z_{1...i}]$，表示一个包含输入和到目前为止的思维序列的部分解。ToT 的特定实例化涉及回答四个问题：
1. 如何将中间过程分解为思维步骤；
2. 如何从每个状态生成潜在的思维；
3. 如何启发式地评估状态；
4. 使用什么搜索算法。

**1. 思维分解。** 虽然 CoT 连贯地采样思维而没有显式的分解，但 ToT 利用问题属性来设计和分解中间思维步骤。如表1所示，根据不同的任务，一个思维可以是几个词（纵横填字）、一行方程（24点游戏）或一整段写作计划（创意写作）。一般来说，一个思维应该足够"小"以使语言模型能够生成有希望且多样化的样本（例如，生成整本书通常太"大"而无法保持连贯），但又足够"大"以使语言模型能够评估其对解决问题的前景（例如，生成一个词元通常太"小"而无法评估）。

**2. 思维生成器 $G(p_\theta, s, k)$。** 给定树状态 $s = [x, z_{1...i}]$，我们考虑两种策略来生成下一个思维步骤的 $k$ 个候选：

(a) 从 CoT 提示中采样独立同分布的思维（创意写作，图4）：$z^{(j)} \sim p_\theta^{CoT}(z_{i+1} | s) = p_\theta^{CoT}(z_{i+1} | x, z_{1...i})$（$j = 1 \cdots k$）。当思维空间丰富（例如每个思维是一个段落）且独立同分布采样带来多样性时，这种方法效果更好；

(b) 使用"提议提示"顺序地生成思维（24点游戏，图2；纵横填字，图6）：$[z^{(1)}, \cdots, z^{(k)}] \sim p_\theta^{\text{propose}}(z_{i+1}^{(1...k)} | s)$。当思维空间更加受限（例如每个思维只是一个单词或一行）时，这种方法效果更好，因为在同一上下文中提出不同的思维可以避免重复。

**3. 状态评估器 $V(p_\theta, S)$。** 给定一个边界上的不同状态集合，状态评估器评估它们在解决问题方面的进展，作为搜索算法的启发式方法，以决定哪些状态值得继续探索以及探索顺序。虽然启发式方法是解决搜索问题的标准方法，但它们通常是编程实现的（如 DeepBlue [3]）或学习得到的（如 AlphaGo [29]）。我们提出第三种替代方案——利用语言模型来审慎地推理状态。在适用的情况下，这种审慎的启发式方法可以比编程规则更灵活，比学习模型更节省样本。与思维生成器类似，我们考虑两种独立或联合评估状态的策略：

(a) 独立评估每个状态：$V(p_\theta, S)(s) \sim p_\theta^{\text{value}}(v | s)$ 对于所有 $s \in S$，其中价值提示对状态 $s$ 进行推理，生成一个标量值 $v$（例如 1-10）或一个分类（例如 sure/likely/impossible），这些可以启发式地转化为一个值。这种评估推理的基础可以因问题和思维步骤而异。在这项工作中，我们通过少量前瞻模拟（例如，快速确认 5、5、14 可以通过 5 + 5 + 14 达到 24，或者"hot l"可以通过在" "中填入"e"来表示"inn"）加上常识（例如，1 2 3 太小无法达到 24，或者没有单词可以以"tzxc"开头）来进行评估。前者可能促进"好"的状态，而后者有助于消除"坏"的状态。这样的评估不必完美，只需对决策有近似帮助即可。

(b) 跨状态投票：$V(p_\theta, S)(s) = \mathbb{1}[s = s^*]$，其中"好"状态 $s^* \sim p_\theta^{\text{vote}}(s^* | S)$ 是通过在投票提示中审慎比较 $S$ 中不同状态而投票选出的。当问题成功难以直接评估时（例如段落连贯性），自然的做法是比较不同的部分解并为最有希望的候选投票。这在精神上类似于一种"逐步"的自一致性策略，即将"探索哪个状态"转化为多项选择问答，并使用语言模型样本进行投票。

对于这两种策略，我们可以多次提示语言模型以聚合价值或投票结果，从而用时间/资源/成本换取更可靠/稳健的启发式方法。

---

**算法1：ToT-BFS($x$, $p_\theta$, $G$, $k$, $V$, $T$, $b$)**

**输入：** 输入 $x$，语言模型 $p_\theta$，思维生成器 $G()$ 和规模限制 $k$，状态评估器 $V()$，步骤限制 $T$，广度限制 $b$。

$S_0 \leftarrow \{x\}$

**对于** $t = 1, \cdots, T$ **执行：**
    $S'_t \leftarrow \{[s, z] \mid s \in S_{t-1},\ z_t \in G(p_\theta, s, k)\}$
    $V_t \leftarrow V(p_\theta, S'_t)$
    $S_t \leftarrow \arg\max_{S \subset S'_t, |S|=b} \sum_{s \in S} V_t(s)$
**结束循环**

**返回：** $G(p_\theta, \arg\max_{s \in S_T} V_T(s), 1)$

---

**算法2：ToT-DFS($s$, $t$, $p_\theta$, $G$, $k$, $V$, $T$, $v_{th}$)**

**输入：** 当前状态 $s$，步骤 $t$，语言模型 $p_\theta$，思维生成器 $G()$ 和规模限制 $k$，状态评估器 $V()$，步骤限制 $T$，阈值 $v_{th}$。

**如果** $t > T$ **则** 记录输出 $G(p_\theta, s, 1)$ **结束**

**对于** $s' \in G(p_\theta, s, k)$ **执行：** ▷ 排序后的候选
    **如果** $V(p_\theta, \{s'\})(s) > v_{thres}$ **则** ▷ 剪枝
        DFS($s', t+1$)
    **结束**
**结束循环**

---

**4. 搜索算法。** 最后，在 ToT 框架内，我们可以根据树结构即插即用不同的搜索算法。我们探索了两种相对简单的搜索算法，并将更高级的算法（如 A* [11]、MCTS [2]）留给未来工作：

(a) **广度优先搜索（BFS）**（算法1）每步维护 $b$ 个最有希望的状态集合。这用于24点游戏和创意写作，因为树的深度有限（$T \leq 3$），且初始思维步骤可以被评估并剪枝到一个小集合（$b \leq 5$）。

(b) **深度优先搜索（DFS）**（算法2）首先探索最有希望的状态，直到达到最终输出（$t > T$），或者状态评估器认为从当前 $s$ 无法解决问题（$V(p_\theta, \{s\})(s) \leq v_{th}$，其中 $v_{th}$ 是价值阈值）。在后一种情况下，从 $s$ 出发的子树被剪枝，以在探索与利用之间进行权衡。在两种情况下，DFS 回溯到 $s$ 的父状态以继续探索。

从概念上讲，ToT 作为语言模型通用问题求解方法具有几个优点：（1）**通用性**：IO、CoT、CoT-SC 和 self-refinement 都可以被视为 ToT 的特例（即有限深度和广度的树；图1）。（2）**模块化**：基础语言模型以及思维分解、生成、评估和搜索过程都可以独立变化。（3）**适应性**：可以适应不同的问题属性、语言模型能力和资源约束。（4）**便利性**：无需额外训练，只需要一个预训练的语言模型就足够了。下一节将展示这些概念优势如何转化为在不同问题上的强大实验性能。

## 4 实验

我们提出了三个即使使用最先进的语言模型 GPT-4 [23] 进行标准 IO 提示或思维链（CoT）提示采样也具有挑战性的任务。我们展示了思维树中的审慎搜索（ToT）如何产生更好的结果，更重要的是，展示了使用语言模型解决需要搜索或规划的问题的有前途的新方法。除非另有说明，我们使用 Chat Completion 模式下的 GPT-4[^1]，采样温度为 0.7。

[^1]: 实验于 2023 年 5 月 5 日至 16 日进行。

### 4.1 24点游戏

24点游戏是一项数学推理挑战，目标是使用4个数字和基本算术运算（+-*/）得到24。例如，给定输入"4 9 10 13"，一个解决方案输出可以是"(10 - 4) * (13 - 9) = 24"。

**表1：任务概览。** 输入、输出和思维示例以蓝色显示。

| 任务 | 24点游戏 | 创意写作 | 5×5纵横填字 |
|------|---------|---------|-----------|
| 输入 | 4个数字（4 9 10 13） | 4个随机句子 | 10条线索（h1. presented;...） |
| 输出 | 达到24的方程 (13-9)*(10-4)=24 | 4段落的文章，分别以4个句子结尾 | 5×5字母：SHOWN; WIRRA; AVAIL; ... |
| 思维 | 3个中间方程 (13-9=4 → 剩余4,4,10; 10-4=6 → 剩余4,6; 4*6=24) | 一个简短的写作计划 (1. Introduce a book that connects...) | 填写线索的单词: (h1. shown; v5. naled; ...) |
| #ToT步数 | 3 | 1 | 5-10（可变） |

**任务设置。** 我们从 4nums.com 抓取数据，该网站有按人类解题时间从易到难排序的 1,362 个游戏，我们使用索引 901-1,000 中相对较难的子集进行测试。对于每个任务，如果输出是一个等于 24 的有效方程，并且每个输入数字恰好使用一次，则认为成功。我们报告 100 个游戏的成功率作为指标。

**基线方法。** 我们使用带有 5 个上下文示例的标准输入-输出（IO）提示。对于思维链（CoT）提示，我们为每个输入-输出对增加 3 个中间方程，每个方程对两个剩余数字进行操作。例如，给定输入"4 9 10 13"，思维可以是"13 - 9 = 4 (剩余: 4 4 10); 10 - 4 = 6 (剩余: 4 6); 4 * 6 = 24 (剩余: 24)"。对于每个游戏，我们对 IO 和 CoT 提示各采样 100 次以获得平均性能。我们还考虑了一个 CoT 自一致性基线，它从 100 个 CoT 样本中取多数输出，以及一个在 IO 样本基础上进行最多 10 次迭代的迭代精化方法。在每次迭代中，如果输出不正确，语言模型会被基于所有先前历史条件化，以"反思你的错误并生成一个精化后的答案"。注意，它使用了关于方程正确性的真实反馈信号。

**ToT 设置。** 为了将24点游戏框架化为 ToT，很自然地将思维分解为 3 个步骤，每个步骤是一个中间方程。如图2(a)所示，在每个树节点，我们提取剩余数字并提示语言模型提出一些可能的下一步。同样的"提议提示"用于所有 3 个思维步骤，尽管它只有一个包含 4 个输入数字的示例。我们在 ToT 中执行广度优先搜索（BFS），在每一步保持最好的 $b = 5$ 个候选。为了在 ToT 中执行审慎的 BFS，如图2(b)所示，我们提示语言模型将每个思维候选评估为"sure/maybe/impossible"（确定/可能/不可能），判断其是否能够达到 24。目标是促进那些可以在少量前瞻试验中验证的正确部分解，基于"太大/太小"的常识消除不可能的部分解，并保留其余的"可能"。我们对每个思维采样 3 次价值评估。

**结果。** 如表2所示，IO、CoT 和 CoT-SC 提示方法在该任务上表现不佳，仅实现了 7.3%、4.0% 和 9.0% 的成功率。相比之下，广度为 $b = 1$ 的 ToT 已经实现了 45% 的成功率，而 $b = 5$ 达到了 74%。我们还考虑了 IO/CoT 的"神谕"设置，通过计算 $k$ 个样本中最佳的成功率（$1 \leq k \leq 100$）。为了比较 IO/CoT（最佳 $k$ 个）与 ToT，我们计算了 ToT 中 $b = 1 \cdots 5$ 下每个任务访问的树节点数，并在图3(a)中映射 5 个成功率，将 IO/CoT（最佳 $k$ 个）视为在赌博机中访问 $k$ 个节点。毫不奇怪，CoT 比 IO 扩展得更好，100 个 CoT 样本中的最佳实现了 49% 的成功率，但仍远不如在 ToT 中探索更多节点（$b > 1$）。

**表2：24点游戏结果。**

| 方法 | 成功率 |
|------|-------|
| IO 提示 | 7.3% |
| CoT 提示 | 4.0% |
| CoT-SC (k=100) | 9.0% |
| **ToT (ours) (b=1)** | **45%** |
| **ToT (ours) (b=5)** | **74%** |
| IO + Refine (k=10) | 27% |
| IO (best of 100) | 33% |
| CoT (best of 100) | 49% |

**错误分析。** 图3(b) 分解了 CoT 和 ToT 样本在哪个步骤失败，即 CoT 中的思维或 ToT 中的所有 $b$ 个思维是无效的或无法达到 24。值得注意的是，约 60% 的 CoT 样本在生成第一步后就已经失败，或者说，在生成前三个词（如"4 + 9"）后就已经失败。这凸显了直接从左到右解码的问题。

### 4.2 创意写作

接下来，我们设计了一个创意写作任务，其中输入是 4 个随机句子，输出应该是一篇包含 4 个段落的连贯文章，分别以这 4 个输入句子结尾。这样的任务是开放式的和探索性的，挑战创造性思维以及高层规划。

**任务设置。** 我们从 randomwordgenerator.com 采样随机句子以形成 100 个输入，每个输入约束没有对应的标准答案文章。由于我们发现 GPT-4 大多数时候能够遵循输入约束，我们专注于以两种方式评估段落连贯性：使用 GPT-4 零样本提示提供 1-10 的标量分数，或使用人工判断来比较不同方法输出对。对于前者，我们对每个任务输出采样 5 个分数并取平均值，我们发现这 5 个分数通常一致，在所有输出上的平均标准差约为 0.56。对于后者，我们采用一部分作者进行盲法研究，比较 CoT 与 ToT 生成的段落对的连贯性，其中段落的顺序在 100 个输入上随机翻转。

**基线方法。** 鉴于该任务的创造性，IO 和 CoT 提示都是零样本的。前者提示语言模型在给定的输入约束下直接生成连贯的段落，后者提示语言模型先做一个简要计划然后写段落，即计划作为中间思维步骤。我们为每个任务生成 10 个 IO 和 CoT 样本。我们还考虑了一个迭代精化方法（$k \leq 5$），在每个任务中基于一个随机 IO 样本，语言模型被条件化为输入约束和最后生成的段落，以决定段落是否已经"完美连贯"，如果不是则生成一个精化版本。

**ToT 设置。** 我们构建了一个深度为 2（只有 1 个中间思维步骤）的 ToT——语言模型首先生成 $k = 5$ 个计划并投票选出最好的一个（图4），然后类似地基于最佳计划生成 $k = 5$ 个段落并投票选出最好的一个。这里广度限制 $b = 1$，因为每一步只保留一个选择。一个简单的零样本投票提示（"分析下面的选项，然后总结哪个对指令最有前景"）用于在两个步骤中采样 5 次投票。

**结果。** 图5(a) 显示了 100 个任务的平均 GPT-4 分数，ToT（7.56）被认为平均生成比 IO（6.19）和 CoT（6.93）更连贯的段落。虽然这种自动指标可能有噪声，但图5(b) 通过显示在 100 个段落对中，人类在 41 个中更喜欢 ToT 而非 CoT，而只在 21 个中更喜欢 CoT 而非 ToT（其他 38 对被认为"相似连贯"）来确认了这一发现。最后，迭代精化在这个自然语言任务上更有效，它将 IO 连贯性分数从 6.19 提高到 7.67，将 ToT 连贯性分数从 7.56 提高到 7.91。我们认为这可以被看作 ToT 框架中思维生成的第三种方法，其中新思维可以来自对旧思维的细化，而不是独立同分布或顺序生成。

### 4.3 小型纵横填字游戏

在24点游戏和创意写作中，ToT 相对较浅——最多需要 3 个思维步骤即可达到最终输出。在这里，我们探索 5×5 小型纵横填字游戏作为一个更难的涉及自然语言的搜索问题。同样，目标不仅仅是解决任务，因为更通用的纵横填字游戏可以通过利用大规模检索而不是语言模型的专门 NLP 流水线 [34] 轻松解决。相反，我们旨在探索语言模型作为通用问题求解器的极限，它探索自己的思维并用审慎推理作为启发式来指导自己的探索。

**任务设置。** 我们从 GooBix 抓取数据，其中包含 156 个 5×5 小型纵横填字游戏。由于我们观察到相邻游戏包含相似线索，我们使用索引 1, 6, \cdots, 91, 96 的 20 个游戏进行测试，以及游戏 136, 141, 146, 151, 156 用于提示。对于每个任务，输入描述 5 个横向线索和 5 个纵向线索，输出应该是一个 5×5 = 25 个字母的棋盘来解决填字游戏。对于评估，我们考虑三个成功级别：正确字母的比例（每游戏 25 个）、单词（每游戏 10 个）和游戏。

**基线方法。** 我们在 IO 提示中提供 5 个示例输入-输出对，在 CoT 提示中额外按 h1..5 然后 v1..5 的顺序包含中间词。我们对每个提示运行 10 个样本并取平均结果。

**ToT 设置。** 我们利用深度优先搜索（算法2），持续探索最有希望的后续单词线索，直到该状态不再有希望，然后回溯到父状态以探索替代思维。为了使搜索可处理，后续思维被约束为不改变任何已填充的单词或字母，因此 ToT 最多有 10 个中间步骤。对于思维生成，在每个状态，我们将所有现有思维（例如图6(a)中状态的"h2.motor; h1.tasks"）转化为剩余线索的字母约束（例如"v1. To heap: tm\_;..."），并提示提议提示 5 次以提出下一步在哪里以及填入什么单词的候选。重要的是，我们还提示语言模型给出不同思维的置信度级别，并在不同提议中聚合这些信息，以获得一个排序的下一步思维列表以供探索（图6(a)）。对于状态评估，我们类似地将每个状态转化为剩余线索的字母约束，然后评估每个线索是否可以在给定约束下填充。如果任何剩余线索被认为"不可能"填充（例如"v1. To heap: tm\_s\_"），则状态子树的探索被剪枝，DFS 回溯到其父节点以探索下一个有希望的思维。我们将 DFS 搜索步骤限制为 100 步，并简单地将探索最深的状态（如果有多个，则为第一个探索到的）渲染为最终输出。

**结果。** 如表3所示，IO 和 CoT 提示方法表现较差，单词级成功率低于 16%，而 ToT 显著改善了所有指标，实现了 60% 的单词级成功率并解决了 20 个游戏中的 4 个。这种改进并不令人惊讶，因为 IO 和 CoT 缺乏尝试不同线索、更改决策或回溯的机制。

**表3：小型纵横填字游戏结果。**

| 方法 | 成功率 (%) | 单词 | 游戏 |
|------|-----------|------|------|
| IO | 38.7 | 14 | 0 |
| CoT | 40.6 | 15.6 | 1 |
| **ToT (ours)** | **78** | **60** | **20** |
| +best state | 82.4 | 67.5 | 35 |
| -prune | 65.4 | 41.5 | 5 |
| -backtrack | 54.6 | 20 | 5 |

**神谕和消融研究。** 当从每个任务的神谕最佳 DFS 状态（而不是启发式确定的最佳状态）输出时，ToT 性能更高，实际上解决了 7/20 个游戏（表3，"+best state"），表明我们的简单输出启发式方法可以轻松改进。有趣的是，有时当填字游戏实际上已经解决时，状态评估器可能仍然认为某些单词"不可能"并进行剪枝——这可能是因为 5×5 填字游戏设计上包含一些 GPT-4 无法识别的罕见或过时词汇[^2]。鉴于状态评估作为剪枝启发式方法并不完美，我们还探索了去除剪枝的情况，发现性能普遍较差（表3，"-prune"）。然而，它实际上可以找到 4/20 个游戏的正确解（尽管通过启发式只输出 1 个），其中 3 个是 ToT+剪枝在 100 步内无法解决的。因此，更好的 DFS 剪枝启发式方法在这种情况下对问题求解至关重要。最后，我们通过运行一个消融实验来确认回溯的重要性，该实验最多 20 步持续填充最有希望的线索，允许覆盖。这类似于广度限制为 $b = 1$ 的"贪心"BFS 搜索，表现较差，单词级成功率仅为 20%（表3，"-backtrack"）。

[^2]: 例如，"agend"是"agendum"的过时形式，但 GPT-4 认为它是"agenda"的拼写错误。外部检索或网页交互可以增强语言模型在知识不确定性下的问题求解能力。

## 5 相关工作

**规划与决策制定。** 智能规划和决策制定对于实现预定目标至关重要。由于语言模型在海量世界知识和人类示例上训练，已知它们已经吸收了丰富的常识，使其能够基于问题设置和环境状态提出合理的计划 [12, 42, 37, 13, 35, 41, 40]。我们提出的 ToT 方法通过在每个问题解决步骤同时考虑多个潜在可行的计划，并推进最有希望的计划，扩展了现有的规划形式。思维采样与价值反馈之间的整合有机地结合了规划和决策机制，实现了在解树内的有效搜索。另一方面，传统的决策程序通常需要像强化学习中那样训练专门的奖励和策略模型（例如 CHAI [33]），而我们使用语言模型本身来提供决策的价值估计。RAP [9] 是一个并行的工作，它将语言模型推理视为使用其内部世界模型进行规划，并提出了一个类似于 ToT 的基于 MCTS 的方法。然而，它的任务比我们的更简单，其框架缺乏整合不同树搜索算法的模块化能力。

**自我反思。** 使用 LLM 评估自身预测的可行性正成为问题求解中越来越重要的过程。[28, 20, 24] 引入了"自我反思"机制，其中语言模型对其生成的候选提供反馈。[4] 通过注入语言模型基于其代码执行结果生成的反馈消息，提高了语言模型的代码生成准确性。类似地，[17] 也引入了对动作和状态的"批评"或审查步骤，以决定在解决计算机操作任务中下一步采取什么行动。另一个与我们的工作非常相关的近期工作是"自评估引导解码" [39]。与我们的方法类似，自评估解码也遵循树搜索过程，叶子节点从随机束搜索解码中采样，然后由 LLM 自身用精心准备的自评估提示进行评估。然而，他们的方法使用 PAL 形式 [8]，将思维表示为代码，这使得难以处理像我们论文中考虑的创意写作这样的挑战性任务。因此，我们的思维树形式更加通用，能够处理 GPT-4 使用标准提示仅达到非常低准确率的挑战性任务。

**程序引导的 LLM 生成。** 我们的提议也与最近通过系统程序 [14, 44, 6, 43] 或符号程序引导来组织语言模型行为的进展相关。例如，Schlag 等 [27] 将语言模型嵌入算法搜索过程中，以帮助逐步解决问题，如问答，其中搜索树由可能提供答案的相关段落扩展。然而，这种方法与我们的不同之处在于，树是通过采样外部段落而非语言模型自身的思维来扩展的，并且没有反思或投票步骤。另一种方法，LLM+P [18]，更进一步，将实际规划过程委托给经典规划器。

**经典搜索方法。** 最后但同样重要的是，我们的方法可以被视为问题求解经典搜索方法的现代翻版。例如，它可以被视为像 A* [10] 这样的启发式搜索算法，其中每个搜索节点的启发式由语言模型的自我评估提供。从这个角度来看，我们的方法也与 NeuroLogic A*esque 解码 [19] 相关，该解码受 A* 搜索启发，但引入了对语言模型高效的前瞻启发式，以改进束搜索或 top-k 采样解码。然而，该方法仅限于句子生成任务，而我们的框架是为受价值反馈保护的复杂多步问题求解而设计的。

## 6 讨论

**局限性与未来方向。** 像 ToT 这样的审慎搜索可能对于 GPT-4 已经擅长的许多现有任务并非必要（见附录 B.1），作为初步步骤，本文仅探索了三个挑战 GPT-4 的相对简单任务（见附录 B.2 中一些 GPT-3.5 实验结果），并呼吁与语言模型结合的更好的搜索和规划能力。然而，随着我们开始将语言模型部署到更多现实世界的决策制定应用中（例如编码、数据分析、机器人技术等），可能会出现更复杂的任务，为研究这些研究问题提供新的机会。此外，像 ToT 这样的搜索方法比采样方法需要更多资源（例如 GPT-4 API 成本）以提高任务性能，但 ToT 的模块化灵活性允许用户定制这种性能-成本权衡，并且正在进行的开源努力 [32] 应该能在不久的将来轻松降低此类成本。关于成本和效率的更多细节在附录 B.3 中。最后，这项工作集中于使用现成的语言模型，而使用 ToT-style 的高层反事实决策制定（例如，审慎地考虑下一段的潜在选择，而不是预测下一个词元）来微调语言模型可能会为增强语言模型的问题求解能力提供机会。

**结论。** 语言模型的联想性"系统1"可以通过基于搜索问题解决方案的可能路径树的"系统2"得到有益的增强。思维树框架提供了一种将关于问题求解的经典见解转化为当代语言模型的可操作方法的方式。同时，语言模型解决了这些经典方法的一个弱点，提供了一种解决不易形式化的复杂问题（如创意写作）的方法。我们将语言模型与经典人工智能方法的这种交汇视为一个令人兴奋的方向。

## 更广泛的影响

ToT 是一个使语言模型能够更自主、更智能地做出决策和解决问题的框架。虽然当前的任务仅限于推理和搜索问题，但未来涉及与外部环境或人类交互的应用可能带来潜在危险，例如促进语言模型的有害使用。另一方面，ToT 也提高了模型决策的可解释性和人类对齐的机会，因为其生成的表示是可读的、高层的语言推理，而不是隐式的、低层的词元值。

## 致谢

SY 和 KN 感谢 Oracle Collaborative Research 奖和 National Science Foundation（Grant No. 2239363）的支持。本文表达的任何意见、发现、结论或建议仅代表作者观点，不一定反映 National Science Foundation 的观点。SY 还得到 Princeton 的 Harold W. Dodds Fellowship 的支持。

## 参考文献

[1] T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, et al. Language models are few-shot learners. *Advances in neural information processing systems*, 33:1877–1901, 2020.

[2] C. Browne, E. J. Powley, D. Whitehouse, S. M. M. Lucas, P. I. Cowling, P. Rohlfshagen, S. Tavener, D. P. Liebana, S. Samothrakis, and S. Colton. A survey of monte carlo tree search methods. *IEEE Transactions on Computational Intelligence and AI in Games*, 4:1–43, 2012.

[3] M. Campbell, A. J. Hoane Jr, and F.-h. Hsu. Deep blue. *Artificial intelligence*, 134(1-2):57–83, 2002.

[4] X. Chen, M. Lin, N. Schärli, and D. Zhou. Teaching large language models to self-debug, 2023.

[5] A. Chowdhery, S. Narang, J. Devlin, M. Bosma, G. Mishra, A. Roberts, P. Barham, H. W. Chung, C. Sutton, S. Gehrmann, et al. Palm: Scaling language modeling with pathways. *arXiv preprint arXiv:2204.02311*, 2022.

[6] A. Creswell and M. Shanahan. Faithful reasoning using large language models. *arXiv preprint arXiv:2208.14271*, 2022.

[7] N. D. Daw, Y. Niv, and P. Dayan. Uncertainty-based competition between prefrontal and dorsolateral striatal systems for behavioral control. *Nature neuroscience*, 8(12):1704–1711, 2005.

[8] L. Gao, A. Madaan, S. Zhou, U. Alon, P. Liu, Y. Yang, J. Callan, and G. Neubig. Pal: Program-aided language models, 2023.

[9] S. Hao, Y. Gu, H. Ma, J. J. Hong, Z. Wang, D. Z. Wang, and Z. Hu. Reasoning with language model is planning with world model. *arXiv preprint arXiv:2305.14992*, 2023.

[10] P. E. Hart, N. J. Nilsson, and B. Raphael. A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2):100–107, 1968.

[11] P. E. Hart, N. J. Nilsson, and B. Raphael. A formal basis for the heuristic determination of minimum cost paths. *IEEE transactions on Systems Science and Cybernetics*, 4(2):100–107, 1968.

[12] W. Huang, P. Abbeel, D. Pathak, and I. Mordatch. Language models as zero-shot planners: Extracting actionable knowledge for embodied agents, 2022.

[13] W. Huang, F. Xia, T. Xiao, H. Chan, J. Liang, P. Florence, A. Zeng, J. Tompson, I. Mordatch, Y. Chebotar, et al. Inner monologue: Embodied reasoning through planning with language models. *arXiv preprint arXiv:2207.05608*, 2022.

[14] J. Jung, L. Qin, S. Welleck, F. Brahman, C. Bhagavatula, R. L. Bras, and Y. Choi. Maieutic prompting: Logically consistent reasoning with recursive explanations. *arXiv preprint arXiv:2205.11822*, 2022.

[15] D. Kahneman. *Thinking, fast and slow*. Macmillan, 2011.

[16] D. Kahneman, S. Frederick, et al. Representativeness revisited: Attribute substitution in intuitive judgment. *Heuristics and biases: The psychology of intuitive judgment*, 49(49-81):74, 2002.

[17] G. Kim, P. Baldi, and S. McAleer. Language models can solve computer tasks, 2023.

[18] B. Liu, Y. Jiang, X. Zhang, Q. Liu, S. Zhang, J. Biswas, and P. Stone. Llm+p: Empowering large language models with optimal planning proficiency, 2023.

[19] X. Lu, S. Welleck, P. West, L. Jiang, J. Kasai, D. Khashabi, R. L. Bras, L. Qin, Y. Yu, R. Zellers, N. A. Smith, and Y. Choi. Neurologic a*esque decoding: Constrained text generation with lookahead heuristics. In *North American Chapter of the Association for Computational Linguistics*, 2021.

[20] A. Madaan, N. Tandon, P. Gupta, S. Hallinan, L. Gao, S. Wiegreffe, U. Alon, N. Dziri, S. Prabhumoye, Y. Yang, S. Welleck, B. P. Majumder, S. Gupta, A. Yazdanbakhsh, and P. Clark. Self-refine: Iterative refinement with self-feedback, 2023.

[21] A. Newell, J. C. Shaw, and H. A. Simon. Report on a general problem solving program. In *IFIP congress*, volume 256, page 64. Pittsburgh, PA, 1959.

[22] A. Newell, H. A. Simon, et al. *Human problem solving*. Prentice-Hall, 1972.

[23] OpenAI. Gpt-4 technical report. *ArXiv*, abs/2303.08774, 2023.

[24] D. Paul, M. Ismayilzada, M. Peyrard, B. Borges, A. Bosselut, R. West, and B. Faltings. Refiner: Reasoning feedback on intermediate representations, 2023.

[25] A. Radford, K. Narasimhan, T. Salimans, I. Sutskever, et al. Improving language understanding by generative pre-training. *OpenAI blog*, 2018.

[26] A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever, et al. Language models are unsupervised multitask learners. *OpenAI blog*, 1(8):9, 2019.

[27] I. Schlag, S. Sukhbaatar, A. Celikyilmaz, W. tau Yih, J. Weston, J. Schmidhuber, and X. Li. Large language model programs, 2023.

[28] N. Shinn, B. Labash, and A. Gopinath. Reflexion: an autonomous agent with dynamic memory and self-reflection, 2023.

[29] D. Silver, J. Schrittwieser, K. Simonyan, I. Antonoglou, A. Huang, A. Guez, T. Hubert, L. Baker, M. Lai, A. Bolton, et al. Mastering the game of go without human knowledge. *Nature*, 550(7676):354–359, 2017.

[30] S. A. Sloman. The empirical case for two systems of reasoning. *Psychological bulletin*, 119(1):3, 1996.

[31] K. E. Stanovich. *Who is rational? Studies of individual differences in reasoning*. Psychology Press, 1999.

[32] H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux, T. Lacroix, B. Rozière, N. Goyal, E. Hambro, F. Azhar, et al. Llama: Open and efficient foundation language models. *arXiv preprint arXiv:2302.13971*, 2023.

[33] S. Verma, J. Fu, S. Yang, and S. Levine. Chai: A chatbot ai for task-oriented dialogue with offline reinforcement learning. In *Proceedings of the 2022 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies*, pages 4471–4491, 2022.

[34] E. Wallace, N. Tomlin, A. Xu, K. Yang, E. Pathak, M. Ginsberg, and D. Klein. Automated crossword solving. *arXiv preprint arXiv:2205.09665*, 2022.

[35] L. Wang, W. Xu, Y. Lan, Z. Hu, Y. Lan, R. K.-W. Lee, and E.-P. Lim. Plan-and-solve prompting: Improving zero-shot chain-of-thought reasoning by large language models, 2023.

[36] X. Wang, J. Wei, D. Schuurmans, Q. Le, E. Chi, and D. Zhou. Self-consistency improves chain of thought reasoning in language models. *arXiv preprint arXiv:2203.11171*, 2022.

[37] Z. Wang, S. Cai, A. Liu, X. Ma, and Y. Liang. Describe, explain, plan and select: Interactive planning with large language models enables open-world multi-task agents, 2023.

[38] J. Wei, X. Wang, D. Schuurmans, M. Bosma, E. Chi, Q. Le, and D. Zhou. Chain of thought prompting elicits reasoning in large language models. *arXiv preprint arXiv:2201.11903*, 2022.

[39] Y. Xie, K. Kawaguchi, Y. Zhao, X. Zhao, M.-Y. Kan, J. He, and Q. Xie. Decomposition enhances reasoning via self-evaluation guided decoding, 2023.

[40] S. Yang, O. Nachum, Y. Du, J. Wei, P. Abbeel, and D. Schuurmans. Foundation models for decision making: Problems, methods, and opportunities, 2023.

[41] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, and Y. Cao. ReAct: Synergizing reasoning and acting in language models. *arXiv preprint arXiv:2210.03629*, 2022.

[42] S. Zhang, Z. Chen, Y. Shen, M. Ding, J. B. Tenenbaum, and C. Gan. Planning with large language models for code generation. In *The Eleventh International Conference on Learning Representations*, 2023.

[43] D. Zhou, N. Schärli, L. Hou, J. Wei, N. Scales, X. Wang, D. Schuurmans, C. Cui, O. Bousquet, Q. Le, et al. Least-to-most prompting enables complex reasoning in large language models. *arXiv preprint arXiv:2205.10625*, 2022.

[44] X. Zhu, J. Wang, L. Zhang, Y. Zhang, R. Gan, J. Zhang, and Y. Yang. Solving math word problem via cooperative reasoning induced language models. *arXiv preprint arXiv:2210.16257*, 2022.

---

## 附录 A：代码、提示、轨迹

所有代码可在 https://github.com/princeton-nlp/tree-of-thought-llm 获取。
所有提示可在 https://github.com/princeton-nlp/tree-of-thought-llm/tree/master/src/tot/prompts 获取。
轨迹可在 https://github.com/princeton-nlp/tree-of-thought-llm/tree/master/logs 获取。

## 附录 B：额外实验结果

鉴于探索和扩展语言模型能力前沿的动机，我们在正文中的实验集中于使用最先进的语言模型（GPT-4）以及为挑战它而设计的三个困难任务。在此，我们报告使用较弱 LLM 或较简单任务的额外实验，并讨论成本和效率。

### B.1 在零样本 ToT 下扩展到新任务（GSM8K、StrategyQA）

虽然更常见的 NLP 任务可能对 GPT-4 来说过于简单而不需要 ToT（这就是我们考虑更困难的新任务的原因），但我们相信将 ToT 应用于新任务可能是直接的。例如，我们为 GSM8K 和 StrategyQA 实现了一个简单且通用的零样本 ToT-BFS，类似于创意写作（采样 5 个问题解决策略然后投票选出最佳；然后基于最佳策略采样 5 个解决方案然后投票选出最佳），只需几行额外代码：

```python
# 定义新任务的答案格式
gsm8k_format = '"the answer is n" where n is a number'
strategyqa_format = 'either "the answer is yes" or "the answer is no"'

# 定义零样本 io 提示
standard_prompt = 'Answer the following question with {format}: {input}'

# 定义零样本 cot 和零样本 tot 的思维格式
cot_prompt = '''Answer the following question: {input}
Make a strategy then write. Your output should be of the following format:
Strategy:
Your strategy about how to answer the question.
Answer:
Your answer to the question. It should end with {format}.
'''

# 定义用于零样本 tot 的零样本投票
vote_prompt = '''Given an instruction and several choices,
decide which choice is most promising.
Analyze each choice in detail, then conclude in the last line
"The best choice is {s}", where s the integer id of the choice.
'''
```

我们在 100 个随机 GSM8K 测试和 StrategyQA 开发问题上进行了评估。如表4所示，正如预期的那样，ToT 在两个任务上都改进了 CoT（但改进幅度很小，因为 GPT-4 + CoT 在这些任务上已经非常好，而且 StrategyQA 的瓶颈是外部知识，而不是推理）。考虑到计算成本，对于传统的 NLP 任务，更适合尝试较小的 LLM + ToT；对于挑战 GPT-4 + CoT 推理的困难任务，则适合使用 GPT-4 + ToT。

**表4：使用零样本 ToT 和 GPT-4 的新任务结果。**

| 方法 | GSM8K | StrategyQA |
|------|-------|-----------|
| IO | 51 | 73 |
| CoT | 86 | 82 |
| ToT | 90 | 83 |

### B.2 扩展到新的语言模型（GPT-3.5）

为了理解 ToT 如何与其他 LLM 一起工作，我们还在 GPT-3.5-turbo 上运行了创意写作（表6）和24点游戏（表5）。在这两个任务上，"ToT > CoT > IO"的模式对 GPT-3.5 仍然成立。在创意写作中，我们发现 GPT-3.5+ToT 优于 GPT-4+IO，并且与 GPT-4+CoT 相似，这表明 ToT 也可以在较弱语言模型上良好工作。

在24点游戏中（我们将1-shot提议提示改为3-shot以使其工作），GPT-3.5+ToT 的 19% 远低于 GPT-4+ToT 的 74%。为了进一步理解生成与评估的重要性，我们运行了 GPT-4 生成 + GPT-3.5 评估（64%）和 GPT-3.5 生成 + GPT-4 评估（31%）。这表明该游戏的瓶颈在于思维生成，而不同的生成/评估语言模型可能在降低成本的同时获得不错的结果。

**表5：GPT-4 vs GPT-3.5 在24点游戏上的结果。**

| 方法 | GPT-4 | GPT-3.5 |
|------|-------|---------|
| IO | 7.3% | 6% |
| CoT | 4.0% | 3% |
| ToT | 74% | 19% |

**表6：GPT-4 vs GPT-3.5 在创意写作上的结果。**

| 方法 | GPT-4 | GPT-3.5 |
|------|-------|---------|
| IO | 6.19 | 4.47 |
| CoT | 6.93 | 5.16 |
| ToT | 7.56 | 6.62 |

### B.3 成本和效率

运行 ToT 需要比 IO 或 CoT 提示显著更多的计算。例如，在24点游戏中（表7），使用 ToT 解决一个问题需要 5.5k 补全词元，接近 100 次 CoT 试验（6.7k 词元）。但 ToT 的性能优于 100 次独立 CoT 试验中的最佳结果。

**表7：24点游戏成本分析。**

| 方法 | 生成/提示词元 | 每例成本 | 成功率 |
|------|-------------|---------|-------|
| IO (best of 100) | 1.8k / 1.0k | $0.13 | 33% |
| CoT (best of 100) | 6.7k / 2.2k | $0.47 | 49% |
| ToT | 5.5k / 1.4k | $0.74 | 74% |

在创意写作中（表8），我们发现 ToT 大约需要 5 倍的补全词元和费用，这很直观，因为 $b = 5$ 且大多数词元是生成的段落。

**表8：创意写作成本分析。**

| 方法 | 生成/提示词元 | 每例成本 |
|------|-------------|---------|
| IO | 0.9k / 0.4k | $0.06 |
| CoT | 0.9k / 0.4k | $0.07 |
| ToT | 4k / 2.9k | $0.32 |

因此，完成24点游戏和创意写作的主要 ToT 实验花费约为 $0.74 \times 100 + 0.32 \times 100 = 106 美元。纵横填字游戏的 DFS 实验也应在 100 美元以内。总的来说，ToT 的成本和效率高度依赖于所使用的提示和搜索算法，可能需要 CoT 的 5-100 倍的生成词元。一些可行的见解：

- 我们建议在需要审慎推理且 CoT 难以应付的任务上使用 ToT。
- ToT 的灵活性允许一定的性能-成本权衡，例如，改变 BFS 中的束大小或投票次数、少样本与零样本提示、GPT-3.5 与 GPT-4 等。可以根据某些资源约束或性能目标来配置设置。
- 提高效率还有很多空间，例如，BFS 可以在找到解决方案时提前停止，或者当某些思维"不可能"时缩减束大小。
- 我们相信，为了模型实现更强的智能，确实需要更多的计算，从长远来看这不应成为阻塞性问题，因为（开源）语言模型将变得便宜得多和高效得多。如何更好地训练/微调语言模型以进行思维生成和/或评估也是一个很好的方向。
