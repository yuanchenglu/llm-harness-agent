# DeepSeek-Coder-V2：打破代码智能中闭源模型的壁垒

**作者：** Qihao Zhu*, Daya Guo*, Zhihong Shao*, Dejian Yang* 等
**所属机构：** DeepSeek-AI
**论文编号：** arXiv:2406.11931v1 [cs.SE] | 2024年6月17日

---

## 摘要

我们推出 **DeepSeek-Coder-V2**，一个在代码任务上性能媲美 GPT-4 Turbo 的开源 MoE 代码语言模型。具体来说，DeepSeek-Coder-V2 从 DeepSeek-V2 的中间检查点出发，以额外的 6 万亿 token 继续预训练。通过这一持续预训练，DeepSeek-Coder-V2 大幅增强了 DeepSeek-V2 的代码和数学推理能力，同时保持了相当的一般语言性能。相比 DeepSeek-Coder-33B，DeepSeek-Coder-V2 在代码相关任务的各个方面以及推理和通用能力上都有显著提升。此外，DeepSeek-Coder-V2 将编程语言支持从 86 种扩展到 338 种，上下文长度从 16K 扩展到 128K。在标准基准评估中，DeepSeek-Coder-V2 在代码和数学基准上取得了优于 GPT-4 Turbo、Claude 3 Opus 和 Gemini 1.5 Pro 等闭源模型的性能。

---

## 1. 引言

开源社区在代码智能方面取得了显著进展（StarCoder、CodeLlama、DeepSeek-Coder、Codestral 等），但这些模型与 GPT-4 Turbo、Claude 3 Opus、Gemini 1.5 Pro 等顶级闭源模型间仍存在差距。为弥合这一差距，我们推出 DeepSeek-Coder-V2 系列，基于 DeepSeek-V2 并在额外 6 万亿 token 上继续预训练。

预训练阶段数据集：60% 源代码、10% 数学语料、30% 自然语言语料。源代码包含来自 GitHub 和 CommonCrawl 的 1,170B token，编程语言从 86 种扩展到 338 种。数学语料包含 221B token（约 DeepSeekMath 120B 的两倍）。总计 DeepSeek-Coder-V2 在预训练阶段接触了 10.2T 高质量 token（4.2T 来自 DeepSeek-V2，6T 来自新数据集）。

对齐阶段：先构建包含代码、数学和通用指令数据的 SFT 训练集，然后使用 GRPO 算法进行 RL。

贡献：
1. 推出 DeepSeek-Coder-V2（16B 和 236B 两个规模），激活参数仅 2.4B 和 21B，支持 338 种编程语言和 128K 上下文
2. 首个在代码和数学任务上超越 GPT-4 Turbo、Claude 3 Opus、Gemini 1.5 Pro 的开源千亿参数代码模型
3. 开源发布，允许研究和商业使用

关键评估结果：
- **代码**：HumanEval 90.2%，MBPP+ 76.2%（EvalPlus 新 SOTA），LiveCodeBench 43.4%，SWE-Bench 首个超 10% 的开源模型
- **数学**：MATH 75.7%（接近 GPT-4o 的 76.6%），AIME 2024 超越所有闭源模型
- **通用**：MMLU 79.2%，MT-Bench 8.77，AlignBench 7.84

---

## 2. 数据收集

预训练数据：60% 源代码、10% 数学、30% 自然语言。

**代码数据：** 收集 GitHub 上 2023 年 11 月前创建的公开仓库，应用与 DeepSeek-Coder 相同的过滤规则和近去重。获得 821B 代码（338 种语言）和 185B 代码相关文本。通过 fastText 模型从 CommonCrawl 迭代收集代码相关和数学相关的网页文本。经过三次迭代收集了 70B 代码相关 token 和 221B 数学相关 token。

**数据有效性验证：** 使用 1B 参数模型消融，新代码语料相比 DeepSeek-Coder 的语料在 HumanEval（30.5%→37.2%）和 MBPP（44.6%→54.0%）上分别提升 6.7% 和 9.4%。

---

## 3. 训练策略

### 3.1 训练目标

DeepSeek-Coder-V2 16B 使用下一个 token 预测和 FIM（50% PSM 率）。DeepSeek-Coder-V2 236B 仅使用下一个 token 预测。

### 3.2 模型架构

与 DeepSeek-V2 一致。训练中遇到了指数归一化技术导致的梯度尖峰问题，已回退到传统归一化方法。

### 3.3 超参数

使用 AdamW 优化器（β₁=0.9，β₂=0.95，weight_decay=0.1）。余弦衰减学习率调度，2000 预热步。从 DeepSeek-V2 的中间检查点（4.2T token）继续预训练，总计 10.2T token。

### 3.4 长上下文扩展

使用 YaRN 方法扩展到 128K 上下文。

---

## 4. 评估

### 4.1 代码生成

| 模型 | HumanEval | MBPP+ | Aider | LiveCodeBench | SWE-Bench |
|------|-----------|-------|-------|---------------|-----------|
| GPT-4-Turbo | 94.9 | 88.2 | 57.1 | 45.7 | 18.3 |
| **DeepSeek-Coder-V2** | **90.2** | **76.2** | **49.2** | **43.4** | **11.7** |
| Gemini-1.5-Pro | 95.0 | 84.9 | 51.1 | 34.1 | 12.7 |
| Claude-3-Opus | 93.7 | 83.5 | 28.7 | 34.6 | 2.7 |
| Codestral | 68.4 | 63.9 | 31.0 | 18.7 | — |

### 4.2 数学推理

| 模型 | GSM8K | MATH | AIME 2024 |
|------|-------|------|-----------|
| **DeepSeek-Coder-V2** | **93.0** | **75.7** | **43.6** |
| GPT-4o | 96.1 | 76.6 | 33.3 |
| GPT-4-Turbo | 94.9 | 73.7 | 13.3 |

### 4.3 通用语言

MMLU 79.2%，MT-Bench 8.77，AlignBench 7.84——与其他代码专用模型相比显著更好，与通用开源模型相当。

---

## 5. 对齐

SFT 阶段：集成来自 DeepSeek-Coder、DeepSeek-Math 和 DeepSeek-V2 的指令数据。

RL 阶段：使用 GRPO，偏好数据通过编译器和测试用例反馈在代码领域收集。

---

> *参考文献（共 45 篇）已省略。完整文献列表请参见原始 PDF。*
