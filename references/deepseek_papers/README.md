# DeepSeek 官方论文系列 — 中文导航

> **LLM + Harness = Agent** 研究的配套论文资源
> 收录 DeepSeek 团队 2024–2026 年发表的 13 篇核心论文，全部提供完整简体中文翻译（Markdown 格式）。
> 翻译方式：逐篇通读原文 → 理解消化 → 逐节翻译（保留表格、公式、代码）。

---

## 快速索引

| # | 论文 | 时间 | 页数 | 核心主题 | Harness 关联度 |
|---|------|------|------|---------|--------------|
| 01 | [DeepSeek LLM](#01-deepseek-llm) | 2024.01 | 48p | 缩放定律 + 预训练基础 | ⭐⭐ |
| 02 | [DeepSeekMoE](#02-deepseekmoe) | 2024.01 | 33p | 细粒度专家分割 + 共享专家隔离 | ⭐⭐⭐ |
| 03 | [DeepSeek-Coder](#03-deepseek-coder) | 2024.01 | 23p | 代码智能 + FIM 训练 | ⭐⭐ |
| 04 | [DeepSeek-V2](#04-deepseek-v2) | 2024.06 | 52p | MLA + DeepSeekMoE 体系确立 | ⭐⭐⭐⭐ |
| 05 | [DeepSeek-Coder-V2](#05-deepseek-coder-v2) | 2024.06 | 19p | 开源代码模型超越 GPT-4 Turbo | ⭐⭐ |
| 06 | [Fire-Flyer AI-HPC](#06-fire-flyer-ai-hpc) | 2024.08 | 18p | 万卡集群软硬件协同设计 | ⭐⭐⭐ |
| 07 | [DeepSeek-V3](#07-deepseek-v3) | 2025.02 | 53p | 671B MoE + 无辅助损失均衡 + FP8 训练 | ⭐⭐⭐⭐⭐ |
| 08 | [DeepSeek-R1](#08-deepseek-r1) | 2026.01 | 86p | 纯 RL 激励推理 + 蒸馏 | ⭐⭐⭐⭐ |
| 09 | [Native Sparse Attention](#09-native-sparse-attention-nsa) | 2025.02 | 25p | 硬件对齐稀疏注意力 | ⭐⭐⭐ |
| 10 | [DeepSeek-V3 Insights](#10-deepseek-v3-insights) | 2025.05 | 15p | 扩展挑战 + 硬件架构反思 | ⭐⭐⭐⭐ |
| 11 | [DeepSeek-V3.2](#11-deepseek-v32) | 2025.12 | 23p | DSA + Agent 能力增强 | ⭐⭐⭐⭐⭐ |
| 12 | [mHC Hyper-Connections](#12-mhc-流形约束超连接) | 2025.12 | 19p | 流形约束超连接 | ⭐ |
| 13 | [Conditional Memory](#13-conditional-memoryengram) | 2026.01 | 33p | Engram 条件记忆模块 | ⭐⭐⭐⭐ |

---

## 论文详情

### 01. DeepSeek LLM

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek LLM: Scaling Open-Source Language Models with Longtermism |
| **发表时间** | 2024年1月5日 |
| **出处** | arXiv:2401.02954 |
| **作者** | DeepSeek-AI（80+ 作者） |
| **中文翻译** | [zh-md/01-DeepSeek-LLM.md](zh-md/01-DeepSeek-LLM.md) |

**摘要：** 深入研究缩放定律，提出新的模型/数据扩展分配策略（使用非嵌入 FLOPs/token M 替代参数量 N），发现数据质量影响缩放行为。在 2T token 上预训练 7B 和 67B 模型，67B Chat 超越 GPT-3.5。

**与本研究的关联：** ⭐⭐
DeepSeek 系列的开端。建立的缩放定律框架（超参数缩放、最优分配策略）是后续所有模型的基础。Harness 层面的启示：预训练数据质量直接影响模型 scaling 行为——Harness 层面的数据管理能力与模型性能直接相关。

---

### 02. DeepSeekMoE

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models |
| **发表时间** | 2024年1月11日 |
| **出处** | arXiv:2401.06066 |
| **中文翻译** | [zh-md/02-DeepSeekMoE.md](zh-md/02-DeepSeekMoE.md) |

**摘要：** 提出细粒度专家分割（Fine-Grained Expert Segmentation）和共享专家隔离（Shared Expert Isolation）两种策略，从 2B 验证到 145B 扩展。DeepSeekMoE 2B 接近稠密模型上限，16B 以 40% 计算量达 LLaMA2 7B 性能。

**与本研究的关联：** ⭐⭐⭐
MoE 架构本身就是 Harness 层的体现——路由机制、专家并行、负载均衡都是 Harness 组件。细粒度分割增加激活专家的组合灵活性（从 120 种到 44 亿种），共享专家隔离解决了知识冗余——这直接映射到 Harness 层的"工具注册表"和"状态存储"设计模式。

---

### 03. DeepSeek-Coder

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek-Coder: When the Large Language Model Meets Programming - The Rise of Code Intelligence |
| **发表时间** | 2024年1月26日 |
| **出处** | arXiv:2401.14196 |
| **中文翻译** | [zh-md/03-DeepSeek-Coder.md](zh-md/03-DeepSeek-Coder.md) |

**摘要：** 从头训练 1.3B–33B 代码模型，2T token + 87 种语言 + 仓库级数据 + FIM 训练（50% PSM 率）。33B 超越 CodeLlama 34B，Instruct 33B 超越 GPT-3.5 Turbo。

**与本研究的关联：** ⭐⭐
代码领域是 Harness 理论的最佳试验场——FIM 训练策略（Fill-in-the-Middle）本身就是 Harness 层的上下文管理设计模式。仓库级数据构建（依赖解析→拓扑排序）体现了 Harness 层的状态管理思想。

---

### 04. DeepSeek-V2

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model |
| **发表时间** | 2024年6月19日 |
| **出处** | arXiv:2405.04434 |
| **中文翻译** | [zh-md/04-DeepSeek-V2.md](zh-md/04-DeepSeek-V2.md) |

**摘要：** 236B 总参数/21B 激活，128K 上下文。**MLA（多头潜在注意力）** 通过低秩 KV 压缩减少 93.3% KV 缓存。8.1T token 预训练 + SFT + RL。性能超越 DeepSeek 67B，训练成本降低 42.5%，生成吞吐量提升 5.76 倍。

**与本研究的关联：** ⭐⭐⭐⭐
MLA 是 Harness 层"上下文管理器"的核心技术实现。通过低秩压缩将 KV 缓存从瓶颈变为可管理，使 128K 上下文成为可能——这直接解决了 Harness 理论中的"注意力稀释"问题。MLA + DeepSeekMoE 的组合确立了"模型架构 × Harness 设计"的协同范式。

---

### 05. DeepSeek-Coder-V2

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek-Coder-V2: Breaking the Barrier of Closed-Source Models in Code Intelligence |
| **发表时间** | 2024年6月17日 |
| **出处** | arXiv:2406.11931 |
| **中文翻译** | [zh-md/05-DeepSeek-Coder-V2.md](zh-md/05-DeepSeek-Coder-V2.md) |

**摘要：** 基于 DeepSeek-V2 中间检查点 + 额外 6T token 继续预训练。338 种编程语言，128K 上下文。HumanEval 90.2%（超越 GPT-4 Turbo 的 94.9% 以外所有模型），SWE-bench 首个超 10% 开源模型。

**与本研究的关联：** ⭐⭐
代码作为 Agent 的核心动作空间——Code-V2 展示了模型在代码任务上接近闭源模型的能力。对 Harness 的启示：代码生成能力是 Agent 执行层的关键组件，而代码评测基准（SWE-bench、LiveCodeBench）本身就是 Harness 评估接口（V 组件）的实现。

---

### 06. Fire-Flyer AI-HPC

| 字段 | 内容 |
|------|------|
| **英文标题** | Fire-Flyer AI-HPC: A Cost-Effective Software-Hardware Co-Design for Deep Learning |
| **发表时间** | 2024年8月（SC24, IEEE） |
| **出处** | arXiv:2408.14158 |
| **中文翻译** | [zh-md/06-Fire-Flyer-AI-HPC.md](zh-md/06-Fire-Flyer-AI-HPC.md) |

**摘要：** 10,000 块 PCIe A100 GPU 集群（非昂贵的 NVLink DGX 方案），成本降低 50%，能耗降低 40%。通过 HFReduce（CPU 异步 allreduce）、HaiScale、3FS 分布式文件系统和 HAI-Platform 实现与 DGX-A100 接近的性能。

**与本研究的关联：** ⭐⭐⭐
Harness 理论的硬件基础设施层面。Fire-Flyer 展示了"软件弥补硬件差距"的核心哲学——Harness 层不只是软件，还包括集群调度、通信优化、故障恢复等基础设施组件。PCIe vs NVLink 的选择映射了 Harness 设计中的"成本-性能"权衡。

---

### 07. DeepSeek-V3

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek-V3 Technical Report |
| **发表时间** | 2025年2月18日 |
| **出处** | arXiv:2412.19437 |
| **中文翻译** | [zh-md/07-DeepSeek-V3.md](zh-md/07-DeepSeek-V3.md) |

**摘要：** 671B 总参数/37B 激活。创新：**无辅助损失负载均衡**（bias 项动态调整）、**多 token 预测（MTP）**、**FP8 混合精度训练**（首次在极大规模验证）、**DualPipe**（双向流水线并行，仅 1.2% 理论气泡）。14.8T token 预训练，总训练仅 278.8 万 H800 GPU 小时（$5.576M）。全程无不可恢复损失尖峰。

**与本研究的关联：** ⭐⭐⭐⭐⭐
DeepSeek-V3 是 Harness 理论的最佳工程实践案例：
- **执行循环（E）**：DualPipe 算法——前向/反向的精细调度
- **工具注册表（T）**：256 路由专家的 Top-K 选择机制
- **上下文管理器（C）**：MLA + YaRN 128K 扩展
- **状态存储（S）**：FP8 精度状态管理
- **生命周期钩子（L）**：无辅助损失均衡的偏置动态调整
- **评估接口（V）**：完整的 SFT + RL 对齐流水线

MTP（多 token 预测）更是直接体现了 Harness 层"预测 × 执行"的分离设计。

---

### 08. DeepSeek-R1

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning |
| **发表时间** | 2026年1月4日 |
| **出处** | arXiv:2501.12948 |
| **中文翻译** | [zh-md/08-DeepSeek-R1.md](zh-md/08-DeepSeek-R1.md) |

**摘要：** **DeepSeek-R1-Zero**：纯 RL（无 SFT）从 V3-Base 出发，AIME 从 15.6% 提升至 77.9%，自发涌现自我反思、验证等高级推理模式。**DeepSeek-R1**：多阶段流水线（冷启动 SFT → RL → 拒绝采样 → 二次 RL），融合 R1 蒸馏。AIME 79.2%、Codeforces 2029 Rating。蒸馏小模型同样表现优异。

**与本研究的关联：** ⭐⭐⭐⭐
R1 是"Agent 自我进化"的实证——纯 RL 训练使模型自发产生了反思、验证、策略调整等高级 Agent 行为。这些行为本质上是 Harness 层的"执行循环（E）"和"生命周期钩子（L）"在模型内部的涌现。

核心启示：**Harness 层不仅可以外部构建（如 Hermes 的 Skills/Memory），也可以通过 RL 在模型内部自发形成**。R1 的"啊哈时刻"（模型说"Wait"后重新审视推理）展示了 Harness 层的自我修正机制如何从 RL 中涌现。

---

### 09. Native Sparse Attention (NSA)

| 字段 | 内容 |
|------|------|
| **英文标题** | Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention |
| **发表时间** | 2025年2月27日 |
| **出处** | arXiv:2502.11089 |
| **中文翻译** | [zh-md/09-Native-Sparse-Attention.md](zh-md/09-Native-Sparse-Attention.md) |

**摘要：** 分层稀疏注意力：压缩粗粒度 token + 选择性细粒度 token + 滑动窗口局部上下文。64K 序列加速：解码 11.6×、前向 9.0×、反向 6.0×。端到端可训练，保持 Full Attention 性能。

**与本研究的关联：** ⭐⭐⭐
NSA 是 Harness 层"上下文管理器（C）"的稀疏化实现。其分层次的设计（全局压缩 + 局部选择 + 窗口保持）直接映射到 Harness 层的"记忆层次"设计模式。硬件对齐优化体现了 Harness 层对基础设施的适配。

---

### 10. DeepSeek-V3 Insights

| 字段 | 内容 |
|------|------|
| **英文标题** | Insights into DeepSeek-V3: Scaling Challenges and Reflections on Hardware for AI Architectures |
| **发表时间** | 2025年5月（ISCA 2025, Industry Track） |
| **出处** | arXiv:2505.09343 |
| **中文翻译** | [zh-md/10-DeepSeek-V3-Insights.md](zh-md/10-DeepSeek-V3-Insights.md) |

**摘要：** 分析 DeepSeek-V3/R1 的扩展挑战：内存墙（MLA 解）、通信墙（DualPipe 解）、精度墙（FP8 解）、稳定墙（无辅助损失解）。对下一代 AI 硬件提出建议。

**与本研究的关联：** ⭐⭐⭐⭐
这篇论文直接论述了 Harness 层与硬件的关系。四个"墙"分别对应 Harness 的不同组件：内存墙→上下文管理器、通信墙→执行循环、精度墙→状态存储、稳定墙→生命周期钩子。对硬件设计的建议（稀疏计算单元、低位宽数据路径）指向了"Harness 层需要硬件原生支持"的方向。

---

### 11. DeepSeek-V3.2

| 字段 | 内容 |
|------|------|
| **英文标题** | DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models |
| **发表时间** | 2025年12月 |
| **出处** | arXiv:2512.02556 |
| **中文翻译** | [zh-md/11-DeepSeek-V3.2.md](zh-md/11-DeepSeek-V3.2.md) |

**摘要：** DSA（DeepSeek Sparse Attention）进一步优化注意力效率，FP8 训练增强，RL 扩展，**Agent 能力增强**（工具使用、函数调用）。

**与本研究的关联：** ⭐⭐⭐⭐⭐
DeepSeek 系列中直接提及"Agent 能力增强"的论文。DSA 延续了 NSA 的稀疏注意力思路，而 Agent 能力增强（工具使用、函数调用）直接对应 Harness 层的"工具注册表（T）"和"执行循环（E）"。这标志着 DeepSeek 从纯语言模型向 Agent 模型的转型。

---

### 12. mHC（流形约束超连接）

| 字段 | 内容 |
|------|------|
| **英文标题** | mHC: Manifold-Constrained Hyper-Connections |
| **发表时间** | 2025年12月 |
| **出处** | arXiv:2512.24880 |
| **中文翻译** | [zh-md/12-mHC-Hyper-Connections.md](zh-md/12-mHC-Hyper-Connections.md) |

**摘要：** 超连接（HC）扩展残差流宽度但破坏恒等映射。mHC 将连接模式约束在低维流形，在保持多样化连接的同时恢复恒等映射能力，训练更稳定。

**与本研究的关联：** ⭐
底层架构创新。与 Harness 层的关联较间接——但可被理解为 Harness 层"生命周期钩子（L）"的神经网络层面模拟：通过约束连接模式来保证梯度/信息的稳定流动，类似 Harness 层通过检查点/回滚来保证系统稳定。

---

### 13. Conditional Memory (Engram)

| 字段 | 内容 |
|------|------|
| **英文标题** | Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models |
| **发表时间** | 2026年1月 |
| **出处** | arXiv:2601.07372 |
| **中文翻译** | [zh-md/13-Conditional-Memory.md](zh-md/13-Conditional-Memory.md) |

**摘要：** 提出**条件记忆**作为 MoE 之外的新稀疏性维度。Engram 模块将 N-gram 嵌入现代化，实现 O(1) 知识查找，在保持计算效率的同时增强事实知识检索。

**与本研究的关联：** ⭐⭐⭐⭐
这是与 Harness 理论最直接相关的技术论文之一。条件记忆模块本质上是 Harness 层"状态存储（S）"的原生神经网络实现：
- 将知识查找从"通过计算模拟"变为"直接硬件查找"
- O(1) 查找对应 Harness 层的 Memory 组件的快速检索
- 可扩展的键值存储直接映射到 Hermes 的 MemOS 持久化记忆

Engram 表明：**Harness 层的记忆管理功能可以被嵌入模型架构而非仅作为外部系统**。

---

## 文件结构

```
deepseek_papers/
├── pdf/             # 原始 PDF（13 篇）
├── en-md/           # 英文 Markdown（经 PyMuPDF 提取，保留表格结构）
├── zh-md/           # 简体中文翻译（逐篇通读翻译）
│   ├── 01-DeepSeek-LLM.md
│   ├── 02-DeepSeekMoE.md
│   ├── 03-DeepSeek-Coder.md
│   ├── 04-DeepSeek-V2.md
│   ├── 05-DeepSeek-Coder-V2.md
│   ├── 06-Fire-Flyer-AI-HPC.md
│   ├── 07-DeepSeek-V3.md
│   ├── 08-DeepSeek-R1.md
│   ├── 09-Native-Sparse-Attention.md
│   ├── 10-DeepSeek-V3-Insights.md
│   ├── 11-DeepSeek-V3.2.md
│   ├── 12-mHC-Hyper-Connections.md
│   ├── 13-Conditional-Memory.md
│   └── README.md    ← 本文件
└── README.md
```

## 与 LLM + Harness = Agent 研究的交叉分析

按 Harness 六组件（E, T, C, S, L, V）映射：

| Harness 组件 | 对应 DeepSeek 论文 | 关键启示 |
|-------------|-------------------|---------|
| **E - 执行循环** | V3 (DualPipe), R1 (RL 涌现的反思循环) | 执行循环可以在模型内部涌现，也可以通过外部调度实现 |
| **T - 工具注册表** | V3.2 (Agent 能力增强), MoE 路由 | 专家路由 = 工具选择的特例；细粒度分割增加组合灵活性 |
| **C - 上下文管理器** | V2/V3 (MLA), NSA/DSA, V3.2 | 注意力稀释的解：低秩压缩 + 稀疏化 + 分层 |
| **S - 状态存储** | Engram (条件记忆), V2/V3 (KV 缓存管理) | 知识查找应从计算中分离，成为原生的存储操作 |
| **L - 生命周期钩子** | V3 (无辅助损失均衡), mHC | 负载均衡和梯度稳定都是"系统稳定性"的不同层面 |
| **V - 评估接口** | R1 (GRPO + 规则奖励), Code-V2 (基准测试) | 奖励设计 = Harness 评估接口的实例化 |

---

> 最后更新：2026年6月22日
> 翻译方式：逐篇通读原文 → 逐节翻译（保留表格、公式、代码）
> Skill：`single-paper-translation`（已固化至 ~/.hermes/skills/）
