# 推理强度控制: 如何让模型"多想一点"——以及代价是什么

> **证据说明：** 本文基于 `encoding_dsv4.py` 中 `REASONING_EFFORT_MAX` 的定义和 `reasoning_effort` 参数的渲染逻辑提出设计假设。三种推理强度（max/high/None）的实际效果差异需要端到端实验验证。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> 创新索引: I-17
> **LLM + Harness = Agent** · 第 17 篇
> 系列: [LLM + Harness = Agent](../../README.md)
> 上一篇: [I-16 Quick Instruction 路由](16-quick-instruction-routing.md)
> 下一篇: [I-18 最新提醒注入](18-latest-reminder-injection.md)

---

## 问题: 模型什么时候需要"多想"？

让模型多想一点，答案可能更好——但也更慢、更贵。不是所有问题都值得深度推理。"1+1=?"不需要思考，但"调试这个 200 行的并发 bug"需要。

理想状态：Harness 能根据问题复杂度动态调控推理深度。DeepSeek V4 的 `reasoning_effort` 参数给了这个能力，但只定义了三个档位。如何选择档位、何时切换、代价是什么——需要系统分析。

---

## 关键证据: 三段式推理强度设计

`encoding_dsv4.py` 中 `reasoning_effort` 参数接受三个值：`"max"`, `"high"`, `None`（L261）：

```python
assert reasoning_effort in ['max', None, 'high'], f"Invalid reasoning effort: {reasoning_effort}"
```

只有 `"max"` 等级有实际效果——它会在 thinking mode 下，在 prompt 的最开头（system message 之前）注入一段强推理指令（L262-263）：

```python
if index == 0 and thinking_mode == "thinking" and reasoning_effort == 'max':
    prompt += REASONING_EFFORT_MAX
```

而 `REASONING_EFFORT_MAX` 的内容（L64-68）：

```python
REASONING_EFFORT_MAX = (
    "Reasoning Effort: Absolute maximum with no shortcuts permitted.\n"
    "You MUST be very thorough in your thinking and comprehensively decompose "
    "the problem to resolve the root cause, rigorously stress-testing your logic "
    "against all potential paths, edge cases, and adversarial scenarios.\n"
    "Explicitly write out your entire deliberation process, documenting every "
    "intermediate step, considered alternative, and rejected hypothesis to ensure "
    "absolutely no assumption is left unchecked.\n\n"
)
```

这段指令花了约 350 个字符、约 90 个 token。语法上，它看起来像一条增强版 system prompt——但位置完全不同。

---

## 三个档位: 何时用哪个

### 1. `reasoning_effort=None`（默认）

不注入任何推理强度指令。模型使用默认推理深度。

**适用场景:** 日常问答、简单代码补全、知识查询、直译、格式转换。

**成本:** 零额外 token 开销。推理深度由模型自主决定。

### 2. `reasoning_effort="high"`

源码中 `"high"` 被验证为有效值（L261），但在 `render_message()` 中没有对应的特殊逻辑。

**大概率（>90%）** `"high"` 是后端参数，影响模型内部推理行为而非 prompt 结构。类似 OpenAI 的 `reasoning_effort` 参数，由推理引擎而非编码层消费。

**适用场景:** 中等复杂度任务——代码审查、单文件重构、数据解读、方案设计。

**成本:** 不增加 prompt 长度，但模型内部推理深度提升会延长延迟并增加 completion token 消耗。

### 3. `reasoning_effort="max"`

在 prompt 最开头注入 `REASONING_EFFORT_MAX` 指令。这条指令的位置是精心设计的：

- ✅ 在 `BOS` token 之后、`system prompt` 之前——它是模型看到的第一条内容
- ✅ 只在 `thinking_mode="thinking"` 时生效——chat mode 下此参数被忽略
- ✅ 只在 `index == 0` 时注入——只注入一次，不会重复出现在后续轮次

**适用场景:** 高难度任务——复杂 bug 调试、架构决策、安全审查、数学证明。

**成本:** ~90 额外的 prompt token + 显著增加的 reasoning 输出 token + 更长的思考延迟。

---

## 为什么 Prompt 位置是关键

`REASONING_EFFORT_MAX` 被注入在 prompt 的**绝对值位置**——比 system prompt 更靠前。这是精心设计的：

```
<bos>REASONING_EFFORT_MAX{system_prompt}<User>{question}...
```

在 KV Cache 架构中，越靠前的 token 在每一轮解码中都被注意力机制回看（它们是前缀），影响权重最大。把推理强度指令放在这里意味着：**模型的每一次 token 生成都会受到它的影响**——不是一个局部选项，而是一个全局约束。

对比一下：如果你把同样的指令放在 system prompt 的某个位置，它会被后续的其他 system prompt 内容稀释注意力。放在第一位，让它成为模型生成行为的底层基调。

---

## 对 Harness 的启示

### 1. 动态推理强度路由

最基础的集成就是把 `reasoning_effort` 变成一个动态参数：

```python
def classify_reasoning_effort(user_prompt: str) -> str:
    if contains_complex_bug_pattern(user_prompt):  return "max"
    if contains_code_review_pattern(user_prompt):   return "high"
    return None  # default
```

每次调用在 `encode_messages()` 前设置 `reasoning_effort` 的值。

### 2. 成本预算管理

三个档位意味着三种不同的成本预算：

| 维度 | None | high | max |
|------|------|------|-----|
| Prompt token 增量 | 0 | 0 | ~90 |
| Completion token 增量 | 基准 | 中等（≈1.5-2x） | 显著（≈2-5x） |
| 端到端延迟 | 基准 | 增加 20-50% | 增加 50-200% |
| 适用预算 | 日常 | 重要任务 | 关键任务 |

### 3. 与其他优化的协同

`reasoning_effort="max"` 下的推理输出量显著增大。这使得 [I-14 Reasoning Content Stripping](14-reasoning-content-stripping.md) 在长对话中变得格外重要——你不会想把 `max` 模式产生的超长推理内容全部塞回下一轮 prompt 中。

---

## 局限与待验证

1. **`"high"` 的实际行为未知。**源码只验证了它是合法值但没有前端逻辑（与 prompt 结构无关）。它可能通过 API 参数传递到后端推理引擎。效果差异需要端到端对比实验。
2. **不同模型的 reasoning_effort 含义不同。**DeepSeek V4 的三档语义不适用于 Anthropic 或 OpenAI 的推理参数。Harness 需要做 provider 适配。
3. **`REASONING_EFFORT_MAX` 是纯 prompt 效果还是模型微调特征？**如果这条指令模型在训练中没有见过，它的效果可能有限。但如果模型在训练中被 fine-tune 识别这条指令，效果会更可靠。目前不确定。

---

## 验证路径

1. 对同一高难度问题，分别以 `None`、`"high"`、`"max"` 调用，对比 reasoning output 长度和最终答案质量。
2. 测量三个档位的端到端延迟差异（5 个随机问题取平均）。
3. 对比 `REASONING_EFFORT_MAX` 放在 prompt 开头 vs. 放在 system prompt 内部的输出质量差异——验证"位置是关键"的假设。

---

*本文基于 `encoding_dsv4.py` 第 64-68 行 `REASONING_EFFORT_MAX` 定义与第 261-263 行 `reasoning_effort` 参数渲染逻辑。*
