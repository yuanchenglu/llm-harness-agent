# 最新提醒注入: 为什么有些信息不应该放在 System Prompt 里

> **证据说明：** 本文基于 `encoding_dsv4.py` 中 `LATEST_REMINDER_SP_TOKEN` 的定义和 `latest_reminder` 角色的渲染逻辑提出设计假设。`latest_reminder` 相比 system prompt 的实际注意力权重差异需要实验验证。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> 创新索引: I-18
> **LLM + Harness = Agent** · 第 18 篇
> 系列: [LLM + Harness = Agent](../../README.md)
> 上一篇: [I-17 推理强度控制](17-reasoning-effort-control.md)
> 下一篇: (无)

---

## 问题: System Prompt 说了"今天是 2026-07-16"，模型为什么还在用昨天的日期？

你有一个精心设计的 system prompt。开头写了模型身份，中间列了工具说明，末尾加了一句"当前日期: 2026-07-16"。一切正确。

但模型回答时偶尔用错日期，或者询问当前时间。为什么？

答案在注意力机制里。System prompt 在 prompt 的**开头**。模型在生成了几百个 token 的推理、tool call、和回复之后，注意力已经大幅偏离了 system prompt 末尾的那行日期。它不是故意的——是物理距离造成的注意力衰减。

DeepSeek V4 提供了一个巧妙的解决方案：`latest_reminder` 角色。

---

## 关键证据: 一个特殊角色 + 一个特殊 Token

`encoding_dsv4.py` 定义了 `latest_reminder` 角色和它的专属特殊 Token（L25, L44, L313-314）：

```python
LATEST_REMINDER_SP_TOKEN = "<｜latest_reminder｜>"

latest_reminder_msg_template: str = "{content}"
```

在 `render_message()` 中，`latest_reminder` 角色的渲染逻辑极其简单：

```python
elif role == "latest_reminder":
    prompt += LATEST_REMINDER_SP_TOKEN + latest_reminder_msg_template.format(content=content)
```

就是直接拼接：`＜｜latest_reminder｜＞` + 内容。没有工具定义，没有格式模板，没有任何额外包装。

但简单并不代表不重要。关键在于它的**插入位置**。

---

## 核心设计: 插入位置决定注意力权重

看看 `render_message()` 中控制 `latest_reminder` 插入位置的逻辑（L366）：

```python
if index + 1 < len(messages) and messages[index + 1].get("role") not in ["assistant", "latest_reminder"]:
    return prompt
```

这条逻辑的表达是：**在 `latest_reminder` 消息之后，如果不跟着 assistant 或另一个 `latest_reminder`，就直接 return——不拼接任何过渡 Token。**

结合 `encode_messages()` 的主循环（L563-570），`latest_reminder` 消息在编码时会出现在消息列表中——通常被放在最后一条 user 消息之前。

这意味着在完整 prompt 中，`latest_reminder` 的位置是：

```
<bos>{system_prompt}
<User>{历史消息1}<Assistant>{回复1}<end>
<User>{历史消息2}<Assistant>{回复2}<end>
<latest_reminder>当前日期: 2026-07-16
<User>{最新用户问题}<Assistant>
```

注意：`latest_reminder` 紧贴在**最新一条用户消息**之前。在 KV Cache 架构中，这是注意力最集中的位置——离最新用户提问最近，离模型马上要生成的 token 最近。

对比一下：如果这条日期信息放在 system prompt 中，它的 token 位置离模型即将生成的位置可能差了数百甚至上千个 token。注意力会自然衰减。

---

## 与 System Prompt 的本质区别

| 维度 | System Prompt | latest_reminder |
|------|-------------|------------------|
| 位置 | Prompt 开头（离当前生成 token 最远） | 最后一条 user 之前（离当前生成 token 最近） |
| 内容性质 | 稳定：角色、规范、工具定义 | 变化：日期、时区、用户位置、临时指令 |
| 缓存行为 | 理想缓存对象（内容稳定、频繁复用） | 不应缓存——每次会话不同 |
| 注意力权重 | 低（随着 token 距离衰减） | 高（近因效应） |
| 适用信息 | "你是一位 Python 专家，遵循 PEP 8" | "今天是 2026-07-16，你在北京" |

这直接导向一个设计原则：**把稳定约束放在 system prompt（为了缓存），把时间敏感信息放在 latest_reminder（为了注意力）。**

---

## 对 Harness 的启示

### 1. 拆分 Prompt: 稳定层 vs. 变化层

传统 Agent 把所有信息都塞进一个 system prompt。DeepSeek V4 给了我们一个更好的方式：

```python
# 稳定层（每次复用 KV Cache）
system_prompt = "你是一位 Python 专家..."  # 角色、规范、工具

# 变化层（每轮动态注入）
latest_reminder = f"当前日期: {today()}，用户位置: {location}"

messages = [
    {"role": "system", "content": system_prompt},
    # ...历史消息...
    {"role": "latest_reminder", "content": latest_reminder},
    {"role": "user", "content": user_question},
]
```

### 2. 不只是日期和位置

`latest_reminder` 可以承载任何"需要模型在回答前看到"的动态信息：
- 用户当前所在页面或上下文
- 上一条回复的摘要（帮助模型记住长对话的关键点）
- 临时约束（"本次会话不要用 search 工具"）
- 用户状态（"用户已连续 3 次表达不满，谨慎回应"）

### 3. 与 [I-04 KV Cache 硬约束前缀注入](04-kv-cache-prefix.md) 的互补

I-04 讨论了在 KV Cache 前缀中注入稳定约束的策略。`latest_reminder` 是这条思路的对偶：**把不稳定的、需要高注意力的信息放在前缀的反面——最新内容区。**

两者配合：稳定约束走前缀缓存 → 节延迟，变化信息走 latest_reminder → 保注意力。

---

## 局限与待验证

1. **注意力权重提升的效果需要量化。**"离得近所以注意力高"是 Transformer 架构的理论性质，但 `latest_reminder` 相比 "在 system prompt 末尾放相同内容" 的实际效果差异需要受控实验。
2. **与 `drop_thinking` 的交互。**`_drop_thinking_messages()` 函数（L575-599）保留了 `latest_reminder` 角色的消息，但其他预处理函数（如 `merge_tool_messages`）是否会影响 `latest_reminder` 的语义需要排查。
3. **模型是否被训练来特别关注这个 Token。**如果 `<latest_reminder>` 只在 prompt engineering 层面存在、模型在训练中从未见过它作为特殊 Token，效果可能有限。但 Token 的命名（`SP_TOKEN`，即 special token）暗示它很可能是训练数据的一部分。
4. **与 system message 中的日期指令的区别。**需要在相同任务上做 A/B test: system prompt 中的日期 vs. latest_reminder 中的日期——看哪个被模型更准确地使用。

---

## 验证路径

1. 构造日期敏感任务（如"帮我查今天上映的电影"），对比 system prompt 中提供日期 vs. latest_reminder 中提供日期的准确率。
2. 在不同对话长度（5 轮、20 轮、50 轮）下重复测试，验证注意力衰减是否随对话变长而加剧（latest_reminder 的优势应随之增大）。
3. 测量 latest_reminder 对 KV Cache 行为的实际影响——是否阻止了部分缓存复用。

---

*本文基于 `encoding_dsv4.py` 第 25 行 `LATEST_REMINDER_SP_TOKEN` 定义、第 313-314 行 `latest_reminder` 角色渲染逻辑、以及第 366 行控制消息间转换 Token 的逻辑。*
