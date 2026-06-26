# B1. ReAct：在语言模型中协同推理与行动

**英文标题：** ReAct: Synergizing Reasoning and Acting in Language Models
**作者：** Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
**出处：** ICLR 2023（CCF-A 会议）
**论文编号：** arXiv:2210.03629
**质量评级：** ✅ CCF-A 会议，引用量 11,000+

---

## 摘要

虽然 LLM 在推理和零样本泛化方面表现令人印象深刻，但它们仍依赖静态的单轮交互。我们提出 **ReAct**——一种将推理轨迹（思考）与特定任务动作（工具调用、环境交互）在统一循环中交织的通用框架。推理指导行动选择，行动结果反过来指导后续推理。ReAct 在问答、事实验证和交互式决策等基准上优于基线方法，同时提高了可解释性和可信度。

---

## 核心贡献

**范式：** 传统方法是"推理或行动"二选一。ReAct 的贡献在于将两者统一为"推理→行动→观察→推理"循环。LLM 不仅输出答案，而且交替生成：
1. **思考（Thought）**：分析当前情况、规划下一步
2. **行动（Action）**：调用工具或与环境交互
3. **观察（Observation）**：获取行动结果并融入后续推理

**示例（HotpotQA 问答）：**
```
Thought: I need to search for "Apple Remote" to find its features
Action: Search[Apple Remote]
Observation: The Apple Remote is a remote control...
Thought: Now I need to find the Apple Remote's compatibility  
Action: Lookup[compatible devices]
Observation: Compatible with Apple TV...
Thought: I have enough information to answer
Action: Finish[The Apple Remote is compatible with Apple TV]
```

---

## 实验结果

| 任务 | 基线 | ReAct | 提升 |
|------|------|-------|------|
| HotpotQA | 28.7 (CoT) | **35.1** | +22% |
| FEVER | 60.1 (CoT) | **61.8** | +3% |
| ALFWorld | 18% (BUTLER) | **71%** | +294% |
| WebShop | 29.1 (模仿) | **40.1** | +38% |

---

## 对 Harness 理论的启示

ReAct 是 **"LM + 行动 = Agent"** 概念的奠基论文。它证明驱动 Agent 行为的关键不是更好的模型，而是将推理与行动交织的**循环结构（执行循环 E 组件）**。每个现代 Agent 装备层（Claude Code、Codex、Hermes、OpenHands）都实现了 ReAct 循环的变体。
