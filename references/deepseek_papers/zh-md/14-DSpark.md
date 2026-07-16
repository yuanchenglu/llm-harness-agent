# DSpark: 基于置信度调度的半自回归推测解码

**英文原题：** DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation
**发表时间：** 2026年6月27日
**作者：** 程鑫 1,2,\*，余兴凯 2,\*，邵晨泽 2,\*，李家石 2,\*，熊云帆 2,\*，钱毅 2，朱嘉琦 2，马世荣 2，张小康 2，叶嘉胜 2，陈钦宇 2，邓承启 2，余继平 2，戴大迈 2，张正彦 2，魏宜轩 2，谭宜轩 2，杨文凯 2，徐润欣 2，吴宇 2，徐哲安 2，王宣宇 2，陈牧阳 2，田睿 2，毕晓 2，郝哲文 2，陈少远 2，曹焕琦 2，张文涛 2，徐安忆 2，张会帅 1，赵东岩 1，梁文锋 2
**机构：** 1 北京大学，2 DeepSeek-AI
**通讯：** {chengxin, xingkai, shaochenze, js.li, yunfanxiong}@deepseek.com

---

<!-- Page 1 -->

## 摘要

推测解码通过将草稿生成与目标验证解耦来加速大语言模型推理。虽然最近的并行草稿器能在单次前向传播中高效生成长 token 序列，但由于缺乏 token 间依赖，其接受率快速衰减。此外，不加区分地验证这些扩展模块会将重要的批次容量浪费在高拒绝风险的 token 上，在高并发服务系统中严重降低吞吐量。我们提出 DSpark，一个统一了高吞吐并行生成与自适应、负载感知验证的推测解码框架。为保持草稿质量，DSpark 采用半自回归架构——将并行主干与轻量级顺序模块耦合——引入块内依赖建模，缓解后缀衰减。为优化系统效率，DSpark 采用置信度调度验证，基于估计的前缀存活概率和引擎特定的吞吐量特征，为每个请求动态定制验证长度。在跨领域的离线基准测试中，DSpark 在接受长度上显著超越最先进的自回归和并行草稿器。当部署在 DeepSeek-V4 服务系统中经受真实用户流量时，DSpark 成功缓解了验证浪费。相较于既定生产基线（MTP-1），DSpark 在匹配吞吐水平下将单用户生成速度提升 60%–85%。更重要的是，通过在严格的交互性约束下防止严重的吞吐退化，DSpark 实现了以前无法达到的性能层级，推动了我们服务系统的帕累托前沿。为促进社区进步，我们开源了 DSpark 检查点以及 DeepSpec——一个算法驱动的推测解码训练仓库。

---

<!-- Page 2 -->

## 1. 引言

大语言模型采用自回归方式生成文本：每个新 token 都需要一次完整的以所有先前 token 为条件的前向传播，因此推理延迟与输出长度成线性比例。由此产生的低 GPU 利用率和长用户感知等待时间构成了生产环境 LLM 服务的主要瓶颈，尤其是在延迟敏感场景中，如实时对话助手和多轮 Agent 工作流。推测解码提供了一种原则性解决方案：一个轻量级草稿模型快速生成候选 token 块，完整的目标模型通过拒绝采样在一次前向传播中验证整个块，接受与目标分布一致的最长前缀并附加一个奖励 token。由于验证是并行的，而且接受规则精确地保持了目标分布，推测解码能在不损失质量的情况下加速生成。

草稿模型的设计决定着草稿延迟与接受率之间的权衡。早期的草稿器是自回归的，每个位置都以前面已采样的 token 为条件。然而，它们的草稿延迟随块大小线性增长，迫使这些方法使用短块和浅层架构。为打破这一串行瓶颈，并行草稿器已成为一种极具吸引力的替代方案：所有草稿位置在一次前向传播中生成，使得草稿延迟几乎与块大小无关。这种结构优势在理论上允许并行草稿器高效地生成长得多的草稿块。

然而，充分发挥大并行草稿块的潜力引入了两个关键瓶颈——一个是生成质量，另一个是系统效率。首先，由于并行草稿器独立预测每个位置，它们无法建模块内的 token 间依赖。这种独立性导致多模态冲突以及后面位置的接受率快速衰减。其次，确定最优验证长度仍然是一个挑战。虽然并行生成可以轻松产生长草稿块，但不加区分地验证所有提议的 token 会降低系统吞吐量，特别是在高并发负载下。理想的验证长度沿着两个维度变化。在数据方面，像代码这样的结构化请求自然比开放式对话保持更高的接受率。在系统方面，轻负载下验证额外 token 几乎免费。然而，在重负载下，验证具有高拒绝风险的 token 占用了本可以为其他活跃请求服务的关键批次容量。

为解决这些瓶颈，我们提出 DSpark，一个将高吞吐并行生成与自适应、负载感知验证相统一的推测解码框架。其核心通过两种互补机制来解决草稿生成和验证中的固有权衡。

- **首先**，为克服缺乏 token 间依赖，DSpark 采用半自回归架构。它保持计算代价高昂的草稿主干完全并行，仅附加一个轻量级的串行输出头来注入局部转移信息。这种设计保留了并行模型的草稿速度，同时显著缓解了后缀衰减。

- **其次**，为了解决系统级瓶颈，DSpark 采用置信度调度验证。通过将估计每位置前缀存活概率的置信度头与硬件感知调度器相结合，DSpark 为每个请求动态定制验证长度。该调度器利用实时引擎吞吐量特征，将目标模型验证预算仅分配给预期回报最高的 token。

<!-- Page 3 -->

我们在受控离线基准测试和生产级在线部署中广泛评估了 DSpark。在涵盖数学推理、代码生成和日常对话的受控离线基准测试中，DSpark 持续超越强基线。具体而言，在 Qwen3-4B、8B 和 14B 目标模型上，它相对于自回归 Eagle3 将宏平均接受长度分别提升了 30.9%、26.7% 和 30.0%，相对于并行 DFlash 分别提升了 16.3%、18.4% 和 18.3%。超越顶层指标，我们细粒度的位置级分析揭示了不同草稿器的不同生成特征，凭经验证明了 DSpark 如何成功地结合了并行模型的高初始 token 容量与自回归模型的后缀连贯性。

除离线评估外，我们在 DeepSeek-V4 服务系统中部署了 DSpark，以评估其在真实用户流量下的性能。与之前的 MTP-1 生产基线相比，DSpark 显著拓宽了系统的运行包络。具体而言，在匹配的总吞吐容量下，它以一致的加速将单用户生成速度提升了 60%–85%（V4-Flash）和 57%–78%（V4-Pro）。此外，在严格的 SLA 约束下——基线容量在这些约束下严重恶化——DSpark 缓解了验证开销以维持稳健的吞吐量。通过克服这一性能悬崖，DSpark 解锁了以前不可能达到的严格交互层级，有效地推动了 LLM 服务的帕累托前沿。

为促进开源社区的集体进步，我们公开了我们的成果。具体来说，我们发布了针对 DeepSeek-V4-Flash（预览版）和 DeepSeek-V4-Pro（预览版）训练好的 DSpark 检查点。此外，我们还开源了 DeepSpec——一个算法驱动的训练仓库，包含 Eagle3、DFlash 和 DSpark。这些成果旨在支持高效 LLM 服务的进一步研究。

---

## 2. 背景

### 2.1. 推测解码

自回归语言模型每次前向传播生成一个 token，使得推理延迟与输出长度成比例。推测解码通过使用轻量级草稿模型加速目标模型的推理。在每个解码周期中，草稿模型提议 γ 个候选 token。目标模型在一次前向传播中验证所有候选，接受与自身分布一致的最长前缀。

具体而言，在每个草稿位置 k，目标模型计算自己的分布并比较与草稿分布的差异。token x_k 以概率 min(1, p^t_k(x_k)/p^d_k(x_k)) 被接受。验证从左到右进行：在位置 k 的第一次拒绝会丢弃所有后续 token，无论其质量如何。

令 τ 表示每个周期接受的 token 数量，T_draft 和 T_verify 分别表示草稿和验证阶段的挂钟时间。每个生成 token 的平均延迟为：

L = (T_draft + T_verify) / τ

因此，提高加速比归结为三个杠杆：降低 T_draft（更快地草稿），提高 τ（更好地草稿），或降低有效 T_verify（更聪明地验证）。

### 2.2. 草稿器架构

草稿模型的设计决定了 T_draft 和 τ 之间的权衡。现有方法分为两类。

**自回归草稿器。** 自回归草稿器顺序生成草稿 token，每个位置以之前已采样的 token 为条件。这种显式依赖提供了强建模能力，但草稿成本随块大小线性增长：T_draft ∝ γ，迫使自回归草稿器使用小的 γ 和浅层架构来保持 T_draft 低。为补偿短块，基于树的验证将候选扩展为树并通过树注意力验证多条路径，但大量的验证 token 降低了整体服务吞吐量。

**并行草稿器。** 并行草稿器在一次前向传播中生成所有 γ 个草稿 token，使 T_draft 几乎与块大小无关。这允许使用更大的块（例如 γ=16）而无需成比例增加延迟。

<!-- Page 4 -->

其中，DFlash 是一种最先进的并行草稿器，它通过从目标模型提取的丰富上下文特征（KV 注入）来条件化其草稿模型。在预填充阶段，来自一组目标层的隐藏状态被拼接并投影到草稿隐藏空间中。这些上下文特征通过沿键和值的序列维度与草稿块表示拼接，被注入每个草稿层。块内的所有位置彼此之间以及与注入的目标上下文之间进行双向注意力。草稿模型共享目标模型的嵌入层和语言模型头（均冻结）。它以锚点 token 后跟 γ 个掩码 token 嵌入为输入，并在一次前向传播中为所有掩码位置生成 logits。由于无论块大小如何，草稿仅需一次前向传播，DFlash 在相同延迟预算下可以负担比自回归草稿器更深的架构和更大的块。

---

<!-- Page 5 -->

## 3. 架构

DSpark 的概览如图 1 所示。回顾公式 1，推测解码的每 token 延迟为 L = (T_draft + T_verify)/τ。自回归草稿器实现高 τ 但付出 T_draft ∝ γ 的代价；并行草稿器将 T_draft 压缩为一次前向传播，但由于每个位置独立预测而牺牲 τ。同时，固定长度验证将 T_verify 浪费在几乎肯定被拒绝的低置信度后缀 token 上。DSpark 通过两个互补组件解决这些限制：

- **半自回归生成**（第 3.1 节）。一个并行主干处理草稿计算的主体部分，使 T_draft 几乎与 γ 无关。然后一个轻量级顺序块在草稿 token 之间注入依赖，以最小的额外延迟提高 τ。

- **置信度调度验证**（第 3.2 节）。一个置信度头估计每个位置的接受概率，一个硬件感知调度器使用这些估计来修剪低置信度的后缀 token，减少不必要的验证计算。

<!-- 图 1 描述 -->
**图 1 | DSpark 架构和解码周期。** 给定 prompt token ABC，目标模型执行一步生成下一个 token D，作为草稿阶段的锚点。以 D 为输入，DSpark 使用重型并行主干和轻量级顺序头生成草稿 token EFGH 及其对应的置信度分数 c1–c4。硬件感知前缀调度器然后评估这些分数，保留前缀 EFG 并丢弃低置信度的 token H。最后，目标模型并行验证调度后的前缀。如图所示，E 和 F 被接受而 G 被拒绝，促使模型生成修正后的 token G\* 以完成当前周期。

结合这两种组件，DSpark 能更好地草稿、更聪明地验证。下面我们详细说明每一部分。

### 3.1. 半自回归生成

一个并行草稿器在一次前向传播中产生所有 γ 个草稿 logits，因此每个预测不能以块中其他地方采样的 token 为条件。当上下文允许多个合理的延续时，例如"of course"和"no problem"，并行草稿器可能产生不连贯的组合如"of problem"或"no course"，因为每个位置对所有可能的前驱进行边际化而不是以实际采样的那个为条件。因此接受率沿块快速衰减，浪费了草稿和验证的计算量。因此我们采用**半自回归**结构，将草稿生成分为两个阶段：

**并行阶段。** 一个并行主干（在我们的实现中是 DFlash）对整个块运行单次前向传播，产生隐藏状态 h_1, ..., h_γ 和基础 logits U_1, ..., U_γ。我们对原始 DFlash 主干做了一个小修改：不传入锚点 token 加 γ 个掩码 token 并仅预测掩码位置，而是将锚点本身作为第一个预测位置，因此 γ 个输入 token（锚点 + γ-1 个掩码）产生 γ 个草稿 logits。这减少了草稿计算，同时保持了类似的草稿质量。

<!-- Page 6 -->

**顺序阶段。** 顺序阶段用依赖于前缀的转移偏差 B_k(x_0, x_{<k}, x_k) 补充基础 logits，允许每个草稿位置以块内先前采样的 token 为条件。顺序阶段不定义一个全局归一化的能量模型，而是通过自回归分解引入一个因果块分布：

P(X | x_0) = ∏_{k=1}^γ p_k(x_k | x_0, x_{<k})

p_k(v | x_0, x_{<k}) = exp(U_k(v) + B_k(x_0, x_{<k}, v)) / ∑_{u∈V} exp(U_k(u) + B_k(x_0, x_{<k}, u))

这里，x_0 表示前一个验证周期的锚点 token，U_k 是并行主干在位置 k 产生的基础 logit 向量，V 是词表。在推理时，顺序块根据 p_k(· | x_0, x_{<k}) 从左到右采样。由于这个采样过程本质上是顺序的，块必须是计算轻量级的（T_sequential ≪ T_parallel），使得总体草稿延迟仍然由并行阶段主导。下面我们描述顺序块的两种实现。

- **马尔可夫头。** 最简单的实现将 B_k 限制为仅依赖紧邻的前一个 token，将其简化为一个一阶转移 B(x_{k-1}, x_k)。原则上这是一个完整的 V×V 矩阵 B；我们用一个低秩分解 B = W_1 W_2 来近似，其中 W_1 ∈ R^{V×r}，W_2 ∈ R^{r×V}。给定前一个 token x_{k-1}，位置 k 的转移偏差为：

B(x_{k-1}, ·) = W_1[x_{k-1}] W_2 ∈ R^V

其中 W_1 作为嵌入查找表，W_2 作为 logit 投影。低秩分解（默认 r=256）使存储和每步计算都很小，使顺序循环即使在词表很大时也很高效。回到前面的例子：一旦位置 1 采样了"of"，马尔可夫头就提升"course"并抑制"problem"在位置 2 的出现，从而缓解跨模式冲突。

- **RNN 头。** 马尔可夫头在一步之外没有记忆——位置 k 无法访问 x_{k-1} 之前的 token。RNN 头通过维护一个累积块内完整前缀历史的循环状态 s_k 来放宽这一限制。在每个步骤中，该模块将当前状态 s_{k-1} ∈ R^r，前一个 token 嵌入 W_1[x_{k-1}] ∈ R^r，以及主干隐藏状态 h_k ∈ R^d 拼接成输入向量 z_k = [s_{k-1}; W_1[x_{k-1}]; h_k] ∈ R^{2r+d}，然后应用一个门控更新。

### 3.2. 置信度调度验证

半自回归架构使 DSpark 能够高效地生成大草稿块。然而，产生更多草稿 token 并不会自动转化为更高的端到端加速。不加区分地验证完整草稿块实际上会降低整体系统吞吐量，尤其是在高并发场景中。

<!-- Page 7 -->

这个性能瓶颈来自两个相互作用的因素。首先，在数据方面，草稿接受率在不同领域之间固有差异：像代码这样的结构化文本自然产生高接受率，而开放式对话的接受率明显较低。其次，在系统方面，验证额外 token 的实际成本严格依赖于引擎负载。在系统轻负载下，额外验证即使被拒绝也几乎不引入惩罚。然而，在高并发部署中，每一次不必要的验证都占用了目标模型的批次容量，这些容量原本可以用于服务其他活跃请求。

因此，充分释放大草稿块的潜力需要一个统一的机制，将目标模型的计算仅导向具有正预期回报的 token。DSpark 通过耦合一个预测前缀存活概率的**置信度头**（第 3.2.1 节）和一个基于当前系统负载动态确定最优验证长度的**硬件感知前缀调度器**（第 3.2.2 节）来实现这一点。

#### 3.2.1. 置信度头

受已有工作启发，置信度头为每个草稿位置 k 输出一个标量估计 c_k ∈ (0,1)。关键的是，c_k 建模了草稿 token 在位置 k 将通过目标验证的**条件**概率，假设块中所有前面的 token 已被接受。该架构采用一个轻量级的线性投影后接 sigmoid 函数：

c_k = σ(w^T [h_k; W_1[x_{k-1}]])

其中 h_k 是主干的隐藏状态，W_1[x_{k-1}] 是来自前一个草稿 token 的马尔可夫嵌入。我们使用每步分析接受率 c\*_k 来监督 c_k。该率由草稿分布与目标分布之间的总变差距离确定：

c\*_k = 1 - ½ ‖p^d_k - p^t_k‖_1

**事后校准。** 与基于阈值的验证启发式方法不同——它们只需要置信度分数正确地对草稿 token 质量进行排序——我们的硬件感知调度方法精确地需要累积接受概率的绝对大小来计算期望接受长度 τ。因为神经网络的置信度估计经常过于自信，直接使用原始置信度分数会扭曲吞吐量估计，导致次优调度。

为解决这个问题，我们提出**顺序温度缩放（STS）**。由于每个 c_i 建模一个条件概率，链式法则规定了草稿前缀被接受的联合概率分解为累积乘积 ∏_{i≤k} c_i。使用一个留出的验证集，STS 从左到右连续校准这一联合概率。具体地，在每个位置 k ∈ {1, ..., γ}，我们执行一个简单的一维网格搜索，找到使累积乘积的期望校准误差（ECE）最小的最优温度标量，同时保持所有先前位置已经校准的分数固定。关键的是，温度缩放是一种保序变换：它修正预测概率以匹配经验接受率，而不会扰乱置信度头学到的相对草稿 token 排序。

#### 3.2.2. 硬件感知前缀调度器

<!-- Page 8 -->

**算法 1 硬件感知前缀调度器**

**输入：** 活跃请求 r ∈ {1, ..., R}；每个请求的置信度序列 c_{r,1}, ..., c_{r,γ}；预分析的步骤吞吐曲线 SPS(B)
**输出：** 每个请求选定的前缀长度 ℓ\*_1, ..., ℓ\*_R

1: for r = 1 to R do
2:   计算前缀存活概率：a_{r,j} ← ∏_{i≤j} c_{r,i} 对 j = 1, ..., γ
3: end for
4: 构建候选空间 E ← {(r, j) | a_{r,j} > 0}，按 a_{r,j} 降序排序
5: 初始化状态：ℓ_r ← 0 对所有 r；批次大小 B ← R；期望接受 τ\* ← R
6: 初始化追踪：Θ_best ← R · SPS(R)；选定长度 ℓ\*_r ← 0 对所有 r
7: for each (r, j) ∈ E 按排序顺序 do
8:   ℓ_r ← j; B ← B + 1; τ\* ← τ\* + a_{r,j}
9:   当前吞吐量 Θ ← τ\* · SPS(B)
10:   if Θ > Θ_best then
11:     Θ_best ← Θ; 更新选定长度 ℓ\*_r ← ℓ_r
12:   else
13:     break
14:   end if
15: end for
16: return (ℓ\*_1, ..., ℓ\*_R) 实现 Θ_best

先前的方法通常对置信度分数应用静态阈值来确定验证长度。虽然在孤立的单请求假设下有效，但在高并发生产系统中静态阈值可能是次优的，因为验证草稿 token 的价值高度依赖于当前系统负载。

为解决这个问题，我们将验证长度选择形式化为一个全局吞吐量最大化问题（算法 1）。考虑一批 R 个活跃请求。对于请求 r，令 c_{r,1}, ..., c_{r,γ} 为每位置置信度估计，ℓ_r ∈ {0, ..., γ} 表示调度的验证长度。由于推测解码仅以连续前缀的方式动态接受草稿 token，位置 j 处的 token 的存活概率是累积乘积 a_{r,j} = ∏_{i≤j} c_{r,i}。在单次验证步骤中，发送给目标模型的总批次大小（以 token 计）为 B = ∑_{r=1}^R (1 + ℓ_r)，期望的成功接受 token 数为 τ = ∑_{r=1}^R (1 + ∑_{j=1}^{ℓ_r} a_{r,j})。令 SPS(B) 表示引擎吞吐量，以每秒步数计量，对于给定前向传播批次大小 B。关键的是，这个容量曲线在引擎初始化时被预分析一次，并作为轻量级成本表存储。我们的调度器旨在通过动态选择验证长度 ℓ_1, ..., ℓ_R 来最大化期望的系统级 token 吞吐量 Θ = τ · SPS(B)。

虽然找到 Θ 的全局最大值看起来是一个组合搜索问题，但目标结构允许一个高效的贪心解法。由于 a_{r,j} 关于 j 单调非增（即 a_{r,j} ≤ a_{r,j-1}），将请求 r 的验证长度从 j-1 扩展到 j 的边际收益恰好是 a_{r,j}。这种单调性确保全局按 a_{r,j} 对候选 token 排序自然尊重了块内前缀依赖。因此，如果总验证批次大小 B 是固定的，最优分配 {ℓ_r} 将由从所有 {a_{r,j}} 的全局池中贪心地选择最高存活概率的草稿 token 来确定。

<!-- Page 9 -->

基于这一洞见，可以沿着这条贪心接纳路径来评估优化目标。我们首先对所有有效前缀扩展按存活概率降序全局排序。为动态确定最优目标批次大小 B，我们从这个排序池中递增地接纳 token，通过从预分析的成本表中进行 O(1) 查找来更新期望吞吐量 Θ。

无损推测解码严格需要**非前瞻性**属性：接纳决策不能依赖于未来的候选 token。因为我们的置信度头依赖于先前采样 token 的**马尔可夫特征**，计算下一个存活概率 a_{r,k+1} 显式地需要实例化的候选 token x_{r,k}。回顾性全局搜索会无意中将 x_{r,k} 泄露到位置 k 的接纳决策中，引入选择偏差（我们在附录 A 中提供了一个具体的反例来证明这种理论违规）。

为强制严格因果性，调度器（算法 1）采用一种早停机制。通过当吞吐量下降时（Θ ≤ Θ_best）立即中断贪心搜索，截断决策仅依赖于处理到该精确步骤的前缀。这隔离了来自未来 token 的接纳事件，确保了精确的目标分布恢复。注意，这种逐步早停在且仅当目标 Θ 是单峰时才会产生全局最大吞吐量，这隐含地假设了一个平滑衰减的硬件容量曲线。我们在第 5.2 节讨论了针对现实世界中非平滑 SPS 特征和异步系统流水线所需的工程适配。

### 3.3. 训练

在训练期间，我们从每个目标序列中随机采样多个锚点位置形成 γ-token 块作为训练数据。目标模型在整个训练过程中保持冻结；草稿模型共享其嵌入层和语言模型头并保持它们冻结，仅更新主干草稿器、顺序块和置信度头。

训练目标包含三个项：交叉熵损失 L_ce、分布匹配损失 L_tv 和置信度损失 L_conf。所有三个损失都按位置乘以权重 w_k = exp(-(k-1)/γ)，强调在基于前缀验证下对期望接受长度贡献更大的较早块位置。

交叉熵损失 L_ce 训练草稿器预测正确的下一 token：
L_ce = -∑_{k=1}^γ w_k log p^d_k(x\*_k)

其中 x\*_k 是真实 token，p^d_k 是草稿分布。

分布匹配损失 L_tv 惩罚草稿与目标分布之间的总变差距离：
L_tv = ∑_{k=1}^γ w_k ‖p^d_k - p^t_k‖_1

由于总变差距离是接受率的直接代理：每步接受概率等于 1 - ½‖p^d - p^t‖_1，最小化 L_tv 直接最大化期望接受率。

置信度损失 L_conf 是一个二元交叉熵，训练置信度头预测来自公式 8 的软接受标签 c\*_k：
L_conf = -∑_{k=1}^γ w_k [c\*_k log c_k + (1 - c\*_k) log(1 - c_k)]

<!-- Page 10 -->

总体目标是三个项的加权组合（默认权重 α_ce=0.1，α_tv=0.9，α_conf=1.0）：
L = α_ce L_ce + α_tv L_tv + α_conf L_conf

---

## 4. 实验

在本节中，我们使用离线基准测试验证 DSpark 的草稿质量，并在第 5 节报告在线生产流量下置信度调度器的有效性。实验设置在第 4.1 节描述，主要结果在第 4.2 节，额外分析包含在第 4.3 节。

### 4.1. 实验设置

**目标模型和草稿模型。** 我们在四个覆盖不同规模和模型系列的目标模型上评估 DSpark：Qwen3-{4B, 8B, 14B} 和 Gemma4-12B。对于草稿模型，我们将 DSpark 与两个代表性草稿器进行比较：DFlash（最先进的并行草稿器）和 Eagle3（基于训练时测试的自回归草稿器）。为公平比较，我们在**同一训练框架**中和**同一数据**上重新训练所有草稿器。我们将 Eagle3 的 TTT 视野与 DFlash 和 DSpark 使用的块大小对齐，并对所有草稿器使用相同的目标模型特征层。对于草稿模型层数，Eagle3 设为 1，DSpark 和 DFlash 设为 5。除非另有说明，DSpark 默认指马尔可夫头变体；我们在第 4.3.2 节研究 RNN 头变体。

**训练数据。** 我们使用 Open-PerfectBlend，一个由 130 万样本组成的开源版本。它是一个通用指令数据集，包含对话（17.6%）、数学（39.4%）、代码（38.9%）和指令遵循数据（4.1%）。我们仅使用 Open-PerfectBlend 的 prompt；响应由每个目标模型以推荐的采样参数重新生成。每个草稿器训练 10 个 epoch 以确保完全收敛。对于数据生成和评估，我们采用非思考模式。

**评估协议。** 我们在三个领域评估不同算法的性能：
1. **数学推理**，包括 GSM8K、MATH500 和 AIME25。
2. **代码生成**，包括 MBPP、HumanEval 和 Live-CodeBench。
3. **日常对话**，包括 MT-Bench、Alpaca 和 Arena-Hard。

对于所有基准测试，我们使用标准推测解码，采样温度设为 1.0。我们报告每个解码轮次的接受长度（τ）。对于所有草稿器，我们使用基于链的草稿。

<!-- Page 11 -->

**表 1 | 主要推测解码结果。** 我们报告不同目标模型和领域的每解码轮次接受长度（τ，越高越好）。**粗体**标出最佳结果。

| 目标模型 | 草稿器 | GSM8K | MATH | AIME25 | MBPP | HumanEval | LCB | MT-Bench | Alpaca | Arena-Hard |
|---------|--------|-------|------|--------|------|-----------|-----|----------|-------|-----------|
| **Qwen3-4B** | Eagle3 | 5.14 | 4.62 | 3.92 | 3.69 | 4.16 | 3.77 | 2.39 | 2.26 | 2.55 |
| | DFlash | 5.40 | 4.85 | 4.15 | 4.40 | 4.74 | 4.18 | 3.07 | 2.96 | 2.83 |
| | DSpark | **6.11** | **5.70** | **4.89** | **5.13** | **5.38** | **4.86** | **3.64** | **3.54** | **3.29** |
| **Qwen3-8B** | Eagle3 | 5.30 | 4.77 | 3.91 | 3.96 | 4.33 | 4.17 | 2.66 | 2.54 | 2.54 |
| | DFlash | 5.33 | 4.91 | 4.07 | 4.36 | 4.64 | 4.39 | 3.11 | 2.98 | 2.81 |
| | DSpark | **6.17** | **5.78** | **5.01** | **5.16** | **5.52** | **5.17** | **3.72** | **3.58** | **3.21** |
| **Qwen3-14B** | Eagle3 | 5.24 | 4.60 | 3.71 | 3.81 | 4.14 | 4.01 | 2.62 | 2.47 | 2.48 |
| | DFlash | 5.41 | 4.84 | 3.98 | 4.44 | 4.59 | 4.33 | 3.10 | 2.94 | 2.72 |
| | DSpark | **6.21** | **5.74** | **4.94** | **5.26** | **5.43** | **5.02** | **3.70** | **3.58** | **3.13** |
| **Gemma4-12B** | Eagle3 | 5.87 | 5.46 | 4.83 | 4.72 | 5.37 | 4.16 | 3.19 | 3.06 | 2.72 |
| | DFlash | 5.45 | 5.04 | 4.22 | 4.39 | 4.95 | 3.70 | 2.98 | 2.84 | 2.59 |
| | DSpark | **6.05** | **5.78** | **5.12** | **5.11** | **5.64** | **4.51** | **3.49** | **3.35** | **2.92** |

### 4.2. 实验结果

为隔离原始草稿质量与系统级调度策略，我们的离线评估禁用了置信度调度器，强制所有草稿器提出固定数量的 token 块。主要结果以每轮平均接受长度（τ）来衡量，报告于表 1。

DSpark 在所有评估的目标模型和基准领域上持续超越自回归基线（Eagle3）和并行基线（DFlash）。具体而言，在 Qwen3-4B、8B 和 14B 模型上，DSpark 相对于 Eagle3 的宏平均接受长度分别提升了 30.9%、26.7% 和 30.0%。同样，与 DFlash 相比，DSpark 在三个规模上分别产生 16.3%、18.4% 和 18.3% 的相对提升。关键的是，这一优势在模型家族间泛化，如 Gemma4-12B 目标上一致性的性能增益所示。

超越平均改进，表 1 还揭示了显著的领域效应：结构化任务（例如 Qwen3-4B 上数学为 5.57，代码为 5.12）上的接受长度天然高于开放式对话（3.49）。这种数据可预测性的固有方差意味着静态验证长度经常将计算浪费在极有可能被拒绝的后缀 token 上。这直接激励了我们的置信度调度验证，它基于期望接受率动态修剪草稿块。

### 4.3. 实验分析

#### 4.3.1. 为什么并行生成能超越自回归？

表 1 呈现了一个反直觉的观察：并行草稿器（DFlash）和半自回归草稿器（DSpark）往往比完全自回归草稿器（Eagle3）产生更长的接受长度。这一发现与标准的预期——即逐步自回归比并行模型产生更高质量序列——形成对比。

<!-- Page 12 -->

为分析这种行为，我们超越宏观层面的接受长度来检视性能。使用 Qwen3-4B 目标模型和第 4.1 节描述的基准集，我们引入**位置级条件接受率**，在实际推测解码 rollout 期间进行追踪。具体而言，对于给定草稿位置 k，评估分母仅计算目标模型已成功验证并接受了从 1 到 k-1 所有先前草稿 token 的实例。该指标然后计算在这些有效实例中，位置 k 的 token 也被接受的比例。这种方法确保对位置 k 的评估不会受到先前前缀错误的惩罚，揭示了每个特定步骤的底层预测质量。图 2 详细展示了这些测量结果，清晰地展示了不同架构之间的行为差异。

**位置 1 的容量优势。** 在第一个草稿位置，两种架构都仅基于目标上下文预测下一个 token。这里的性能差异严格源于架构容量：像 Eagle3 这样的自回归模型因其 O(γ) 延迟而受限于浅层网络，而 O(1) 的并行草稿器可以负担更深的网络。这种结构性差距在位置 1 产生了显著的精度优势，DFlash 的起始值明显高于 Eagle3（例如，数学任务上 0.88 vs 0.81，对话任务上 0.72 vs 0.53）。由于推测解码作为一个严格的前缀匹配存活过程运作，第一个 token 拥有最高的杠杆——在这里的拒绝会立即使整个块失效。因此，这种初始容量优势不成比例地提升了最终接受长度，解释了为什么尽管后面位置接受率快速衰减，并行草稿器总体上仍然优于自回归草稿器。

**后面位置独立性的局限。** 检查曲线的尾部（位置 2 到 7）暴露了独立并行生成的固有局限性。随着前面的 token 锁定特定的语义路径，后续 token 自然变得更可预测。像 Eagle3 这样的自回归模型有效利用了这种条件确定性，在块中维护甚至增加了条件接受率（例如对话任务上从 0.53 到 0.74）。相比之下，DFlash 遭受快速接受衰减，在代码任务上从 0.87 下降到 0.78，在对话任务上从 0.72 下降到 0.63。由于每个并行位置对所有可能的先前 token 进行边际化，而不是以精确采样的前缀为条件，该模型经常提出不一致的后缀组合——一种称为多模态冲突的模式。

**用半自回归缓解后缀衰减。** 前面的分析突显了一个清晰的架构目标：将并行主干对初始 token 的高容量与自回归模型对后续 token 的依赖建模结合起来。这直接激励了 DSpark 的半自回归设计。如图 2 所示，DSpark 继承了深并行草稿器的高初始接受率（例如数学任务起始于 0.93）。同时，其轻量级顺序头缓解了并行生成中典型的快速接受衰减。通过解决这一权衡，DSpark 在整个草稿块中保持了高且稳定的条件接受率。

<!-- Page 13 -->

**图 3 | 草稿器深度的影响。** 在提议长度固定的条件下，DSpark 的性能随着草稿器层数的增加而提升。值得注意的是，一个浅层 2 层 DSpark 超越了更深的 5 层 DFlash 基线，突显了顺序建模的参数效率。

**图 4 | 提议长度和延迟开销的影响。** DSpark 在各种块大小下持续优于 DFlash（左侧三个面板）。最右侧的面板展示了顺序头在服务期间引入了极小的延迟开销。

#### 4.3.2. 一点自回归就能走很远

基于第 4.3.1 节的洞见，我们沿着两个维度探索 DSpark 的架构设计空间：草稿器深度（Transformer 层数）和提议长度（块大小 γ）。除非另有说明，本节所有实验使用 Qwen3-4B 作为目标模型并遵循第 4.1 节详述的评估协议。

**草稿器深度。** 增加 Transformer 层数自然地扩展了草稿模型的预测容量。为隔离这一效果，我们将块大小固定为 7 并改变 DSpark 的层数从 1 到 5，与 5 层的 DFlash 基线进行比较。图 3 汇总了数学、代码和对话领域的接受长度。如预期，DSpark 的性能随深度单调提升，最陡的边际增益发生在从一层到两层。值得注意的是，一个 2 层的 DSpark 在所有领域上都优于 5 层的 DFlash 基线。这表明通过轻量级顺序头注入局部自回归提供了一个非常有利的精度-参数权衡，比简单地堆叠更深并行层实现了更好的序列连贯性。

<!-- Page 14 -->

**提议长度。** 接下来，我们将草稿器深度固定为 5 层，并将草稿长度（提议长度 γ 加一个锚点 token）在 {4, 8, 12, 16} 范围内缩放，以评估更长草稿块上的性能。对于 DSpark，我们评估默认的马尔可夫头和 RNN 头。图 4 的前三个面板显示 DSpark 在每个提议长度上持续优于 DFlash。更重要的是，性能差距随着 γ 增加而稳定扩大。由于纯并行生成遭受快速接受衰减，其边际效用对于长块逐渐减少。DSpark 缓解了这种衰减，使其相对于 DFlash 的相对增益不断增长。例如，在 γ=7 时，DSpark 在数学、代码和对话上将接受长度分别提高了 16%、15% 和 18%；在 γ=15 时，这些增益分别扩大到 30%、26% 和 22%。此外，RNN 头相对于马尔可夫头仅提供边际的额外增益，主要在更长的提议长度时。考虑到其更高的实现复杂度和不太有利的部署特性，我们使用马尔可夫头作为默认选择。

**延迟开销。** 我们量化 DSpark 中顺序生成循环的开销。图 4 的最右侧面板报告了每轮引擎延迟——包括一次目标验证前向传播、并行草稿块前向传播和串行采样循环——在批次大小为 128 时测量。为防止序列长度偏差，报告的延迟是不同上下文长度上的算术平均。由于在此批次大小下目标模型主导验证计算时间，顺序块的延迟开销可忽略不计。因此，将草稿长度从 4 扩展到 16 仅在全轮延迟上增加了相对于 DFlash 基线的 0.2% 到 1.3%，尽管在接受长度上实现了最高 30% 的提升。

#### 4.3.3. 更聪明地验证，而非更长：置信度头的作用

虽然 DSpark 在长草稿块上维持了高接受率，但验证整个提议仍然低效。由于第 4.2 节指出的固有领域方差，开放式对话中的末尾 token 仍然面临高拒绝风险，使得盲目验证成为目标计算的一种浪费。为评估置信度头能否有效修剪这些无希望的后缀，我们使用 Qwen3-4B 进行了一个离线阈值扫描实验。我们在隔离中验证估计器，将硬件感知前缀调度器留到第 5 节的生产评估中。

**诊断：静态阈值扫描。** 图 5 绘制了跨置信度阈值的平均每步 token 数（柱状图）和总体接受率（线条）。随着阈值增加，接受率稳步上升，因为估计器过滤掉了最终会被拒绝的 token。这表明置信度头可以识别价值较低的后缀 token，且这种修剪在对话负载上最为显著，因为更高熵的 token 分布限制了固定长度验证的效率。在 Chat 子图中，提高阈值显著减少了被拒绝的 token，将接受率从 45.7% 提升到 95.7%。相比之下，结构化任务（数学和代码）经历了较温和的修剪并保留了更多草稿 token，接受率分别从 76.9% 提升到 92.5% 和从 67.6% 提升到 92.0%。

<!-- Page 15 -->

**图 5 | 置信度阈值扫描。** 阈值为 0 对应标准固定长度验证。随着阈值增加，总体接受率稳步上升，因为置信度头有效修剪了最终会被拒绝的 token。

**图 6 | Alpaca 数据集上的可靠性图。** 虽然原始置信度估计器实现了强辨别能力，但其预测本质上过于自信。应用事后校准有助于将前缀存活概率与经验接受率对齐。阴影背景直方图代表不同置信度区间内的样本计数频率分布。

**从静态阈值到校准调度。** 虽然对诊断有用，静态阈值在动态服务环境中是次优的，因为它忽略系统负载：验证低置信度 token 在低并发下机会成本极小，但在高并发下浪费关键的批次容量。这种负载依赖性激励了硬件感知前缀调度器。如第 3.2 节公式所述，最大化系统级吞吐量要求置信度模型同时具备强预测辨别能力和精确的校准能力，以准确估计累积存活概率。可靠性图（图 6）表明，虽然原始模型实现了强辨别能力（ROC-AUC 在 0.81 到 0.90 之间），但它过于自信（ECE 3%–8%）。应用事后 STS 缓解了这种过度自信，将平均 ECE 降低到约 1%，产生了可靠的存活估计。

---

<!-- Page 16 -->

## 5. DSpark 的实际部署

虽然第 4 节建立了 DSpark 在离线基准测试上的算法增益，但将其与 DeepSeek-V4 这样的大规模模型一起部署会引入训练和推理两方面的额外系统级挑战。在本节中，我们展示 DSpark 的端到端生产流水线。我们详述我们的可扩展训练机制、部署硬件感知前缀调度器所需的系统级优化，以及该框架在真实用户流量下的端到端性能。

### 5.1. 可扩展且灵活的培训

DSpark 草稿模型与 DeepSeek-V4-Flash 和 DeepSeek-V4-Pro 的预览版本共同部署。并行主干包含三个 MoE 层，带有 mHC 和 128 的滑动窗口注意力。我们配置最大块大小为 γ=5，并使用马尔可夫头进行顺序建模。此外，置信度头与草稿模型一起端到端训练，随后通过 STS 进行校准以提供可靠的调度信号。

训练草稿模型需要目标模型的输出分布作为监督。在整个文档上下文上评估两个模型会引入巨大的内存占用和 worker 间通信开销。为解决这些瓶颈，我们在内部训练框架中实现了两个系统级优化：

- **隐藏状态通信。** 将目标模型的完整词表 logits 跨并行 worker 传输会创建一个显著的带宽瓶颈。相反，我们临时缓存目标模型的前向传播激活，仅通信紧邻语言模型头之前的隐藏状态。LM 头投影然后在草稿模型的 worker 上仅为采样的目标位置本地执行。这将每 token 的通信复杂度降低到 O(d)，其中 d 是隐藏维度。

- **锚点限定序列打包。** 为将草稿模型的计算成本与目标模型的上下文长度解耦，我们从训练序列中采样固定数量的草稿锚点，并将这些隔离的预测块打包到密集的训练批次中。我们通过 token 级注意力索引而不是标准 2D 掩码来管理这种打包。这保持了跨多个独立序列和锚点的精确因果掩码，避免了与标准 padding 相关的计算和内存开销。

### 5.2. 实践中的硬件感知前缀调度器

在第 3.2.2 节中，算法 1 提供了一个理论上合理且无损的调度机制。然而，直接在生成环境中部署该算法暴露了两个与现实世界基础设施的基本冲突。首先，该算法假设一个平滑、单峰的容量曲线，而真实硬件容量 SPS(B) 是本质上离散的，表现出参差不齐的阶梯式退化。其次，该算法需要每步调度动态草稿 token，这与连续的 CUDA 图重放和零开销调度相冲突。

<!-- Page 17 -->

为在系统兼容性、吞吐量和算法正确性之间导航权衡，我们适配调度器以异步方式运行。由于 ZOS 要求下一步的批次大小在当前步骤完成之前已知，同步调度不可避免地会阻塞 GPU 流水线。相反，我们使用前两步的置信度头输出来近似即将到来的验证容量。在机制上，当前步骤的候选 token 仍然严格按照其实际、最新的累积置信度分数排序；前两步的历史预测仅用于确定动态截断长度（即批次容量限制 K）。这有效地将接纳过程转变为动态的 top-K 选择。虽然近似容量 K 引入了轻微的时间偏移，但选择机制从根本上保持保序性：最自信的草稿 token 总是优先用于验证。这种适配完全隐藏了调度延迟，确保了与 ZOS 的无缝集成。

在此异步流水线基础上，我们解决了硬件利用率瓶颈。为防止调度器被参差不齐的 SPS 悬崖困在局部最小值中，我们移除早停机制，启用无约束的全局搜索。通常，这种回顾性搜索会泄露未来 token 信息并违反无损保证。然而，我们由 ZOS 驱动的适配自然地防止了这种情况。因为无约束搜索仅评估来自两步前的历史预测，接纳决策与当前 token x_{r,k} 的实现相隔离。截断长度固有的只依赖于两步前可用的信息。因此，异步设计形成了一个因果屏障，在跨硬件悬崖时最大化物理吞吐量，同时保留精确的目标分布。

### 5.3. 高吞吐量和低延迟推理

在解码期间，生产服务系统必须同时优化两个竞争目标：每请求延迟和总吞吐量。前者控制个体用户的服务质量——在基于 Agent 的负载中这一因素日益关键——而后者决定同时服务的用户总数。由于推测解码不可避免地引入浪费的验证计算，它在固有的导航这一权衡中，用额外的系统计算换取更快的每请求生成。

然而，在我们的部署场景中，每步处理的请求数量经常受到资源限制和可用用户流量池的约束。因此，有效批次大小持续远低于 GPU 的计算饱和阈值。在这种机制下，传统的权衡简化了：给定一个固定的并发限制，最大化每 GPU 总 token 吞吐量和最大化每用户生成速度成为高度相关的目标，而非竞争目标。

为实现这种最大吞吐量，异步调度器主动将空闲计算路由到最有希望的草稿 token。然而，执行这种动态路由在物理执行层引入了一个严峻挑战：推理框架必须高效支持单批次内的变长查询。标准的解码核函数针对固定查询长度进行了重度优化；天真地处理变长验证前缀因填充和不均匀的工作负载分布导致严重的 GPU 利用不足。我们通过将物理执行与逻辑序列追踪解耦来解决这个问题。在我们的计算核函数中，跨不同请求的所有 token 被展平并作为独立元素相同处理。复杂的序列内依赖然后通过集成在我们的稀疏注意力实现中的标记张量来严格传达。特别在 DeepSeek-V4 架构上，只有索引注意力和压缩核函数需要修改以支持这种变长路由，使得动态调度器能够在不引入底层执行开销的情况下无缝运行。

<!-- Page 18 -->

### 5.4. 真实用户流量下的性能

我们评估 DSpark-5（最大草稿长度 γ=5）相对于 MTP-1 基线在 DeepSeek-V4-Flash 和 DeepSeek-V4-Pro 生产服务引擎中的表现。MTP-1 代表此前生产设置，在 DeepSeek-V4-preview 发布两周后被 DSpark 取代。这个单 token 基线的设立是为了防止部署静态多 token 草稿器在高并发下因过度验证开销而严格恶化总吞吐量。因此，将 DSpark 与此既定基线直接比较，清晰地展示了它在动态服务环境中安全解锁更大草稿块性能潜力的能力。在所有图表中，散点代表从真实用户流量直接采样的原始遥测数据，捕获了复杂、现实世界的请求分布，而实线代表拟合的性能前沿。

**服务帕累托前沿。** 图 7 说明了系统总吞吐量与每用户生成速度（交互性）之间的权衡。为量化 DSpark 在实际部署约束下的行为，我们在几个交互性 SLA 锚点处评估系统。这里，SLA 指定了系统必须保证的最小每用户生成速度。

对于 V4-Flash 引擎，我们在 80 和 120 tok/s/user 的 SLA 锚点处评估系统。在适中的 80 tok/s/user SLA 下，DSpark 比 MTP-1 基线提升总吞吐量 51%。更严格的 120 tok/s/user SLA 代表一个本质上不同的机制：在此约束下，单 token 的 MTP-1 基线接近其运行边界，只能维持非常小的并发批。因此，此点的相对吞吐比在数值上很大，DSpark 实现了名义上的 661% 更高总吞吐量。因此，我们主要将此高 SLA 点解释为 DSpark 扩展了可行交互性前沿的证据，而非对良好利用基线的代表性乘法加速。在匹配的实际吞吐水平下——这提供了更稳定的比较——DSpark 将每用户生成速度加速了 60% 到 85%。

<!-- Page 19 -->

V4-Pro 部署表现出相同的模式。在适中的 35 tok/s/user SLA 下，DSpark 将总吞吐量提升 52%。在更严格的 50 tok/s/user SLA 下，MTP-1 再次进入低并发机制，DSpark 获得名义上的 406% 相对吞吐量优势。与 V4-Flash 一样，我们将此点视为 DSpark 在基线无法有效支持的交互性目标下维持有用吞吐量的指示。在匹配的系统容量下，DSpark 交付了 57% 到 78% 更快的每用户生成速度。总体而言，这些结果表明 DSpark 将观察到的吞吐量-交互性前沿向外推移：它在适中 SLA 机制下提高了吞吐量，更重要的是，在严格交互性约束下保持了非退化的服务容量。

**图 8 | 负载自适应吞吐量和验证预算。** 上方行（a, b）：不同系统并发水平下的总输出吞吐量。下方行（c, d）：每请求分配的平均目标验证预算。随着并发负载增加，动态调度器自动限制每请求验证长度以防止资源争用。

**负载下的吞吐量动态。** 图 8 通过绘制总吞吐量（上方行）和动态验证预算（下方行）与系统并发度的关系，分析了驱动这些增益的底层机制。

- 在我们生产部署典型的适中并发机制下（V4-Flash 少于 200 个并发请求，V4-Pro 少于 150 个），硬件感知调度器利用可用的目标计算容量来分配更长的验证预算，从 MTP-1 的静态 2 token 扩展到每请求约 4-6 个 token。这种扩展的验证每次前向传播产生更多接受的 token，直接贡献了在帕累托前沿观察到的吞吐量增益。

- 随着系统并发度扩展且目标容量饱和，调度器动态限制这一预算。平均验证长度随负载平滑下降，确保低置信度的草稿 token 在消耗关键批次容量之前被修剪。这种负载感知行为稳定了生产部署：DSpark 在轻流量下最大化空闲计算的效用，同时在重流量下有效保留关键批次容量。

<!-- Page 20 -->

**局限性。** 虽然前缀调度器最小化了目标模型验证的浪费，DSpark 仍然有固定的草稿端成本来通过并行主干生成初始的 γ-token 块。对于内在地接受率极低的复杂查询，这种前置草稿计算是无法回收的。未来的优化可以在草稿模型内部引入难度感知的早退出机制，使此类请求能够跳过完整块生成。

---

## 6. 相关工作

**推测解码算法。** 推测解码通过将 token 提议与验证解耦来加速自回归生成。在早期的逐块方法基础上，现代方法采用拒绝采样来精确保持目标模型的分布。由于推理加速直接取决于草稿器的效率和准确性，大量研究集中于优化其架构。除了使用独立的小语言模型外，后续工作将多 token 头或特征外推器直接集成到目标模型中。其他策略包括通过早退出的自推测、动态词表压缩、prompt 查找、后缀自动机和检索。为消除草稿本身的串行瓶颈，最近的方法提出并行或逐块生成。P-EAGLE 并行化了 EAGLE 风格的草稿，而 PARD、DART 和 DFlash 使用受扩散启发的预测在一次前向传播中生成整个块，DDTree 然后将其扩展到可验证的草稿树。并行工作也在改进 DFlash：Domino 引入了一个因果编码器，概念上类似于我们的 RNN 头；而 DFlare 通过逐层融合解决了条件瓶颈。

**推测解码的系统感知调度。** 超越草稿器架构，另一条工作线专注于确定每轮生成或验证的最优推测 token 数。为此，各种方法使用置信度启发式方法、学习的接受率预测器或赌博机策略来动态调整草稿长度。此外，认识到推测解码本质上是一个系统级调度问题，最近的工作通过根据实时系统负载和请求优先级调整推测预算来优化总体有效吞吐量和延迟。

**并行生成。** 并行生成 token 的模型提供了几乎与输出长度无关的解码延迟，使其成为自回归解码的有吸引力的替代方案。非自回归 Transformer（NAT）通过单次前向传播独立预测所有位置开创了这一方向。然而，这迫使模型对所有合理模式进行平均，通常产生混合了来自不同有效序列的片段的结果。

<!-- Page 21 -->

两条主要工作线已经出现以解决这一限制。一个方向保持单次前向传播架构但改变模型看到的内容或训练方式：引入潜变量作为条件输入以引导所有位置朝向一致输出，或放宽训练目标使模型专注于产生一个连贯输出而非对所有有效替代的全分布建模。另一方向通过迭代重预测、逐块自回归或结构化输出层（如 CRF、CTC、HMM 和 PCFG）重新引入有限的顺序依赖。

推测解码进一步要求草稿器必须为拒绝采样规则提供精确的每 token 概率。由于迭代细化、潜变量边际化或全局归一化，上述大多数技术无法轻易提供这样的概率。例如，在我们密切相关的设计中，CRF-NAT 也在并行隐藏状态上放置了一个顺序模块，但其全局归一化的配分函数阻止了精确的每 token 概率计算。同样，当将 CTC 输出层适配到并行推测解码时，由于对齐路径的潜变量边际化，CTC-drafter 被限制为贪心验证。DSpark 通过保持顺序修正的局部性来规避这些限制，因此每 token 概率仍然是精确的 softmax 评估。

---

<!-- Page 22 -->

## 7. 结论

在本文中，我们提出了 DSpark，一个旨在克服大语言模型推理在高并发生产环境中的结构和系统级瓶颈的推测解码框架。在算法层面，DSpark 引入了一个半自回归生成范式——将计算量大的并行主干与轻量级顺序头耦合——以缓解独立并行草稿器的快速后缀衰减。在系统层面，我们将验证长度选择形式化为一个全局吞吐量最大化问题，采用一个硬件感知前缀调度器，基于校准的存活概率和实时引擎负载动态调整目标模型的验证预算。广泛的离线评估表明，DSpark 在不同领域上显著优于最先进的自回归和并行基线。此外，其在 DeepSeek-V4 内的实际部署验证了其在生产服务中的实用价值：通过智能管理验证开销，DSpark 在重负载下维持稳健的并发性，一致性地加速了每用户生成速度，并有效将 LLM 服务的帕累托前沿向外推移。

---

## 参考文献

（注：参考文献条目保持原始英文格式，未翻译）

1. T. Abramovich et al. Speed-bench: A unified and diverse benchmark for speculative decoding. arXiv:2604.09557, 2026.
2. Z. An et al. PARD: Accelerating LLM inference with low-cost PARallel draft model adaptation. ICLR, 2026.
3. AngelSlim Team. D-Cut: Adaptive verification depth pruning for speculative decoding, 2026.
4. Z. Ankner et al. Hydra: Sequentially-dependent draft heads for medusa decoding. COLM, 2024.
5. M. Arriola et al. Block diffusion: Interpolating between autoregressive and diffusion language models. ICLR, 2025.
6. J. Austin et al. Structured denoising diffusion models in discrete state-spaces. NeurIPS, 2021.
7. J. Austin et al. Program synthesis with large language models. arXiv:2108.07732, 2021.
8. T. Cai et al. Medusa: Simple LLM inference acceleration framework with multiple decoding heads. ICML, 2024.
9. Y. Cai et al. Fastmtp: Accelerating llm inference with enhanced multi-token prediction, 2025.
10. C. Chen et al. Accelerating large language model decoding with speculative sampling. arXiv:2302.01318, 2023.
11. J. Chen et al. Dflash: Block diffusion for flash speculative decoding. arXiv:2602.06036, 2026.
12. M. Chen et al. Evaluating large language models trained on code, 2021.
13. Y. Cheng et al. Recurrent drafter for fast speculative decoding in large language models, 2024.
14. K. Cobbe et al. Training verifiers to solve math word problems. arXiv:2110.14168, 2021.
15. D. Dai et al. Deepseekmoe: Towards ultimate expert specialization in mixture-of-experts language models. ACL, 2024.
16. DeepSeek-AI. Deepseek-v3 technical report. arXiv:2412.19437, 2024.
17. DeepSeek-AI. Deepseek-v4: Towards highly efficient million-token context intelligence, 2026.
18. C. Du et al. Order-agnostic cross entropy for non-autoregressive machine translation. ICML, 2021.
19. C. Du et al. GliDe with a CaPE: A low-hassle method to accelerate speculative decoding. ICML, 2024.
20. M. Elhoushi et al. Layerskip: Enabling early exit inference and self-speculative decoding. ACL, 2024.
21. Fireworks AI. Speed, Python: Pick Two. How CUDA Graphs Enable Fast Python Code for Deep Learning, 2023.
22. T. Ge et al. Lossless acceleration for seq2seq generation with aggressive decoding. arXiv:2205.10350, 2022.
23. M. Ghazvininejad et al. Mask-predict: Parallel decoding of conditional masked language models. EMNLP, 2019.
24. F. Gloeckle et al. Better & faster large language models via multi-token prediction. ICML, 2024.
25. Google DeepMind. Gemma 4 model card, 2026.
26. J. Gu et al. Non-autoregressive neural machine translation. ICLR, 2018.
27. S. Gui et al. Non-autoregressive machine translation with probabilistic context-free grammar. NeurIPS, 2023.
28. C. Guo et al. On calibration of modern neural networks. ICML, 2017.
29. J. A. Hanley and B. J. McNeil. The meaning and use of the area under a receiver operating characteristic curve. Radiology, 1982.
30. Z. He et al. Rest: Retrieval-based speculative decoding, 2023.
31. X. Hu et al. Echo: Elastic speculative decoding with sparse gating for high-concurrency scenarios. arXiv:2604.09603, 2026.
32. Y. Hu et al. SAM decoding: Speculative decoding via suffix automaton. ACL, 2025.
33. F. Huang et al. On the learning of non-autoregressive transformers. ICML, 2022.
34. F. Huang et al. Directed acyclic transformer for non-autoregressive machine translation. ICML, 2022.
35. J. Huang et al. Domino: Decoupling causal modeling from autoregressive drafting in speculative decoding, 2026.
36. K. Huang et al. Specdec++: Boosting speculative decoding via adaptive candidate lengths. arXiv:2405.19715, 2024.
37. K. Huang et al. Adaspec: Adaptive speculative decoding for fast, slo-aware large language model serving. SoCC, 2025.
38. M. Hui et al. P-eagle: Parallel-drafting eagle with scalable training, 2026.
39. D. Israel et al. Accelerating diffusion llms via adaptive parallel decoding. NeurIPS, 2026.
40. N. Jain et al. Livecodebench: Holistic and contamination free evaluation of large language models for code. ICLR, 2025.
41. L. Kaiser et al. Fast decoding in sequence models using discrete latent variables. ICML, 2018.
42. W. Kwon et al. Efficient memory management for large language model serving with pagedattention. SOSP, 2023.
43. Y. Leviathan et al. Fast inference from transformers via speculative decoding. ICML, 2023.
44. G. Li et al. Diffuspec: Unlocking diffusion language models for speculative decoding, 2025.
45. R. Li et al. Nightjar: Dynamic adaptive speculative decoding for large language models serving, 2026.
46. T. Li et al. From live data to high-quality benchmarks: The arena-hard pipeline, 2024.
47. T. Li et al. From crowdsourced data to high-quality benchmarks: Arena-hard and benchbuilder pipeline. ICML, 2025.
48. X. L. Li et al. Diffusion-LM improves controllable text generation. NeurIPS, 2022.
49. Y. Li et al. EAGLE-2: Faster inference of language models with dynamic draft trees. EMNLP, 2024.
50. Y. Li et al. EAGLE: Speculative sampling requires rethinking feature uncertainty. ICML, 2024.
51. Y. Li et al. EAGLE-3: Scaling up inference acceleration of large language models via training-time test. NeurIPS, 2026.
52. J. Libovický and J. Helcl. End-to-end non-autoregressive neural machine translation with connectionist temporal classification. EMNLP, 2018.
53. H. Lightman et al. Let's verify step by step. ICLR, 2024.
54. F. Liu et al. Kangaroo: Lossless self-speculative decoding for accelerating llms via double early exiting. NeurIPS, 2024.
55. F. Liu et al. Dart: Diffusion-inspired speculative decoding for fast llm inference, 2026.
56. H. Liu et al. Not-a-bandit: Provably no-regret drafter selection in speculative decoding for llms, 2026.
57. T. Liu et al. Talon: Confidence-aware speculative decoding with adaptive token trees. arXiv:2601.07353, 2026.
58. X. Liu et al. Optimizing speculative decoding for serving large language models using goodput, 2024.
59. X. Liu et al. Turbospec: Closed-loop speculation control system for optimizing llm serving goodput. arXiv:2406.14066, 2024.
60. X. Ma et al. FlowSeq: Non-autoregressive conditional sequence generation with generative flow. EMNLP, 2019.
61. J. Mamou et al. Dynamic speculation lookahead accelerates speculative decoding of large language models. NeurIPS ENLSP, 2024.
62. X. Miao et al. Specinfer: Accelerating large language model serving with tree-based speculative inference and verification. ASPLOS, 2024.
63. M. P. Naeini et al. Obtaining well calibrated probabilities using bayesian binning. AAAI, 2015.
64. Y. Ovadia et al. Can you trust your model's uncertainty? evaluating predictive uncertainty under dataset shift. NeurIPS, 2019.
65. L. Qian et al. Glancing transformer for non-autoregressive neural machine translation. ACL, 2021.
66. Y. Ren et al. A study of non-autoregressive model for sequence generation. ACL, 2020.
67. L. Ringel and Y. Romano. Accelerating speculative decoding with block diffusion draft trees. arXiv:2604.12989, 2026.
68. R. Sadhukhan et al. Magicdec: Breaking the latency-throughput tradeoff for long context generation with speculative decoding. ICLR, 2025.
69. C. Saharia et al. Non-autoregressive machine translation with latent alignments. EMNLP, 2020.
70. J. Sandler et al. Specdiff-2: Scaling diffusion drafter alignment for faster speculative decoding. MLSys, 2026.
71. A. Saxena. Prompt lookup decoding, 2023.
72. C. Shao et al. Sequence-level training for non-autoregressive neural machine translation. CL, 2021.
73. C. Shao et al. Beyond MLE: Convex learning for text generation. NeurIPS, 2023.
74. Y. Shen et al. Draft less, retrieve more: Hybrid tree construction for speculative decoding, 2026.
75. S. Somasundaram et al. PLD+: Accelerating LLM inference by leveraging language model artifacts. NAACL Findings, 2025.
76. M. Stern et al. Blockwise parallel decoding for deep autoregressive models. NeurIPS, 2018.
77. X. Sun et al. Instantaneous grammatical error correction with shallow aggressive decoding. ACL, 2021.
78. Z. Sun et al. Fast structured decoding for sequence models. NeurIPS, 2019.
79. R. Taori et al. Stanford alpaca: An instruction-following llama model, 2023.
80. S. Tiwari et al. Cachewise: Understanding workloads and optimizing kvcache management for efficiently serving llm coding agents. arXiv:2606.16824, 2026.
81. C. Wang et al. Semi-autoregressive neural machine translation. EMNLP, 2018.
82. Z. Wang et al. THE END OF MANUAL DECODING: TOWARDS TRULY END-TO-END LANGUAGE MODELS. ICLR, 2026.
83. Z. Wen and Y. Feng. Specbound: Adaptive bounded self-speculation with layer-wise confidence calibration, 2026.
84. Z. Wen et al. Speculative decoding with ctc-based draft model for llm inference acceleration. NeurIPS, 2024.
85. M. Williams et al. Speculative decoding with a speculative vocabulary. arXiv:2602.13836, 2026.
86. Z. Wu et al. TETRIS: Optimal draft token selection for batch speculative decoding. ACL, 2025.
87. H. Xia et al. Speculative decoding: Exploiting speculative execution for accelerating seq2seq generation. EMNLP Findings, 2023.
88. H. Xia et al. Unlocking efficiency in large language model inference: A comprehensive survey of speculative decoding. ACL Findings, 2024.
89. H. Xia et al. SWIFT: On-the-fly self-speculative decoding for LLM inference acceleration. ICLR, 2025.
90. Z. Xie et al. mHC: Manifold-constrained hyper-connections. ICML, 2026.
91. T. Xu et al. The perfect blend: Redefining rlhf with mixture of judges. arXiv:2409.20370, 2024.
92. D. Yan et al. Demystifying tensor cores to optimize half-precision matrix multiply. IPDPS, 2020.
93. A. Yang et al. Qwen3 technical report. arXiv:2505.09388, 2025.
94. Zacks917. AutoMTP_vLLM, 2026.
95. J. Zhang et al. Draft & verify: Lossless large language model acceleration via self-speculative decoding. ACL, 2024.
96. J. Zhang et al. Dflare: Scaling up draft capacity for block diffusion speculative decoding, 2026.
97. L. Zhang et al. Learning harmonized representations for speculative sampling, 2025.
98. S. Zhang et al. Pacer: Blockwise pre-verification for speculative decoding with adaptive length. arXiv:2602.01274, 2026.
99. Y. Zhang and T. Math-AI. American invitational mathematics examination (aime) 2025, 2025.
100. C. Zhao et al. Insights into deepseek-v3: Scaling challenges and reflections on hardware for ai architectures. ISCA, 2025.
101. W. Zhao et al. Fr-spec: Accelerating large-vocabulary language models via frequency-ranked speculative sampling. ACL, 2025.
102. K. Zheng et al. Masked diffusion models are secretly time-agnostic masked models and exploit inaccurate categorical sampling. ICLR, 2025.
103. L. Zheng et al. Judging llm-as-a-judge with mt-bench and chatbot arena. NeurIPS, 2023.
104. L. Zheng et al. Sglang: Efficient execution of structured language model programs. NeurIPS, 2024.
105. Y. Zhong et al. Disaggregating prefill and decoding for goodput-optimized large language model serving. OSDI, 2024.
106. K. Zhu et al. Nanoflow: towards optimal large language model serving throughput. OSDI, 2025.

---

<!-- Page 32 -->

## 附录 A：反例——没有早停的选择偏差

我们提供一个简单的反例来说明离线全局搜索，即在算法 1 中没有 **break** 条件运行时，如何违反无损推测解码所需的非前瞻性属性。正式地，第 k 个草稿 token 的接纳事件 ℓ_r ≥ k 必须在 token x_{r,k} 被采样之前由调度器可见的信息决定。它不能依赖于 x_{r,k} 本身的实现。

考虑一个单请求场景（R=1）和最大草稿长度 γ=2。假设第一个位置的预 token 置信度为 a_1=0.8，预分析的容量曲线为：
- SPS(1) = 1.0
- SPS(2) = 0.5
- SPS(3) = 0.45

验证 0 和 1 个草稿 token 的期望吞吐量为：
- Θ_0 = 1 · SPS(1) = 1.0
- Θ_1 = (1 + 0.8) · SPS(2) = 0.9

没有早停时，调度器在提交任何接纳决策之前继续评估 Θ_2。由于马尔可夫置信度头使用先前采样的 token，下一个置信度分数 c_2 显式依赖于 x_1 的实现。因此，第二个前缀的存活概率 a_2 = a_1 c_2 也依赖于 x_1。

考虑 x_1 的两种可能实现：

- **情况 1（x_1 产生高 c_2）：** 假设 x_1 导致 c_2=0.9。则 a_2 = 0.8 × 0.9 = 0.72。长度为 2 的期望吞吐量为 Θ_2 = (1 + 0.8 + 0.72) × 0.45 = 1.134。由于 Θ_2 是 {1.0, 0.9, 1.134} 中的全局最大值，调度器返回 ℓ=2。第一个 token x_1 被接纳到验证前缀中。

- **情况 2（x_1 产生低 c_2）：** 假设 x_1 导致 c_2=0。则 a_2=0。长度为 2 的期望吞吐量为 Θ_2 = (1 + 0.8 + 0) × 0.45 = 0.81。这里，全局最大值仍然是 Θ_0=1.0，因此调度器返回 ℓ=0。第一个 token x_1 不被接纳到验证前缀中。

因此，第一个草稿 token 的接纳动态地依赖于第一个草稿 token 本身的值。这种回顾性依赖引入了选择偏差：调度器倾向于引向高置信度延续的 token，即使 x_1 的接纳决策本应在观察到 x_1 之前做出。

<!-- Page 33 -->

我们现在明确这个分布偏差。设词表为 {A, B}，并考虑第一个位置的目标和草稿分布：
- p^t(A) = 0.7, p^t(B) = 0.3
- p^d(A) = 0.5, p^d(B) = 0.5

标准推测接受概率在第一个位置为：
∑_{x∈{A,B}} min(p^t(x), p^d(x)) = min(0.7, 0.5) + min(0.3, 0.5) = 0.8

匹配假设值 (a_1=0.8)。假设回顾性调度器行为如上：x_1=A 产生高延续置信度因此 ℓ=2，而 x_1=B 产生低延续置信度因此 ℓ=0。则第一个输出 token 分布如下。如果 x_1=A，草稿 token 被接纳并以概率 min(1, 0.7/0.5)=1 被接受，因此输出 token 是 A。如果 x_1=B，草稿 token 不被接纳；目标模型从 p^t 中生成一个新的 token。因此，

Pr(Y=A) = Pr(x_1=A) · 1 + Pr(x_1=B) · p^t(A) = 0.5 + 0.5 × 0.7 = 0.85

因此 Pr(Y=B) = 0.15。

这个输出分布 (0.85, 0.15) 与目标分布 (0.7, 0.3) 不同，证明了回顾性调度器不是无损的。早停机制在因果贪心调度器中防止了这个问题。由于 Θ_1 < Θ_0，调度器在评估任何依赖于延续的量（如 c_2）之前立即停止并返回 ℓ=0。第一个位置的接纳决策因此仅依赖于 token 前信息，不能被 x_1 的实现所偏置。这恢复了标准无损论证所需的非前瞻性属性。
