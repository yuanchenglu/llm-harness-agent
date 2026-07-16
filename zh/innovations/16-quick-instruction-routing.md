# Quick Instruction 路由: DeepSeek V4 的内置任务分发机制

> **证据说明：** 本文基于 `encoding_dsv4.py` 源码中 Quick Instruction 特殊 Token 的定义与消息渲染逻辑提出设计假设。各 Task 的实际效果需要在真实 API 场景中验证。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> 创新索引: I-16
> **LLM + Harness = Agent** · 第 16 篇
> 系列: [LLM + Harness = Agent](../../README.md)
> 上一篇: [I-15 DSML 工具调用格式优化](15-dsml-tool-call-optimization.md)
> 下一篇: [I-17 推理强度控制](17-reasoning-effort-control.md)

---

## 问题: 一个模型如何同时做聊天、搜索路由、标题生成？

传统做法是每种任务部署一个专用模型或 prompt。聊天有聊天模型，搜索意图识别有分类模型，标题生成有摘要模型。每个模型独立训练、独立部署、独立调用——延迟叠加，成本叠加。

DeepSeek V4 的做法不同：**一个模型处理所有这些任务，通过特殊 Token 在文本流中触发不同行为模式。**这就是 Quick Instruction 系统。

---

## 关键证据: 六个任务 Token 的定义

`encoding_dsv4.py` 明确定义了六种 Quick Instruction 特殊 Token（L28-35）：

```python
# Task special tokens for internal classification tasks
DS_TASK_SP_TOKENS = {
    "action": "<｜action｜>",
    "query": "<｜query｜>",
    "authority": "<｜authority｜>",
    "domain": "<｜domain｜>",
    "title": "<｜title｜>",
    "read_url": "<｜read_url｜>",
}
VALID_TASKS = set(DS_TASK_SP_TOKENS.keys())
```

这些 Token 不是给用户看的，也不是给 Agent 开发者手动拼接的。它们通过消息对象的 `task` 字段注入到编码后的 prompt 中。

---

## 机制: Task Token 如何触发模型行为

在 `render_message()` 中（L369-383），当消息携带 `task` 字段时，编码逻辑会根据 task 类型在消息末尾附加对应的特殊 Token：

```python
task = messages[index].get("task")
if task is not None:
    assert task in VALID_TASKS, f"Invalid task: '{task}'..."
    task_sp_token = DS_TASK_SP_TOKENS[task]

    if task != "action":
        # Non-action tasks: append task sp token directly after the message
        prompt += task_sp_token
    else:
        # Action task: append Assistant + thinking token + action sp token
        prompt += ASSISTANT_SP_TOKEN
        prompt += thinking_end_token if thinking_mode != "thinking" else thinking_start_token
        prompt += task_sp_token
```

关键区别:
- **非 action 任务**（query, authority, domain, title, read_url）：Task Token 直接附加在消息后面，不带 Assistant 前缀。这意味着模型被要求直接输出任务结果，不需要生成完整的对话回复。
- **action 任务**：在 Token 前额外添加 `＜｜Assistant｜＞` 和 thinking 标记，模拟一个标准的 assistant 回复开头。模型从这个起点开始生成，输出的是路由决策（如 "Search" 或 "Answer"）。

---

## 六个 Task 各司何职

| Task | 编码位置 | 用途 |
|------|---------|------|
| **action** | 用户消息后 + `＜｜Assistant｜＞` + thinking + `＜｜action｜＞` | 判断用户问题是否需要联网搜索，还是可以直接回答。输出一个简短的路由决策。 |
| **query** | 直接附加在用户消息后 | 根据用户 prompt 生成搜索引擎查询词。不生成完整回复，只输出查询字符串。 |
| **authority** | 直接附加在用户消息后 | 分类用户 prompt 对信息权威性的需求程度（如金融、医疗需要高权威来源）。 |
| **domain** | 直接附加在用户消息后 | 识别用户 prompt 的领域分类（如编程、数学、文学等）。 |
| **title** | 附加在 Assistant 回复后 | 根据对话内容生成简洁的对话标题。用于多轮对话列表展示。 |
| **read_url** | 伴随 `＜｜extracted_url｜＞` 使用 | 判断 prompt 中提到的每个 URL 是否需要抓取和阅读。 |

---

## 为什么这对 Harness 重要

### 1. 请求延迟的大幅降低

传统架构下，一个"用户问问题→搜索→回答"的流程可能需要 3 次模型调用：路由（要不要搜）、查询生成（搜什么）、最终回答。每次调用的网络延迟是独立叠加的。

Quick Instruction 把 routing 和 query generation 压缩到单 token 或极短输出中。`action` 任务输出可能只有 "Search" 一个词——几个 token 就能完成原来一整轮推理的工作。

### 2. 实现成本

Quick Instruction Token 是拼接到 prompt 末尾的，不额外增加 system prompt 长度。但每次 Quick Instruction 调用仍然是一次独立的 API 请求，prompt 需要重新发送。如果你的应用需要在"search"和"no-search"之间快速路由，可以先用短 prompt + action task 做决策，再决定是否构造完整的 search prompt——而不是每条消息都带完整的 system prompt 和工具定义。

### 3. Harness 层面的集成

Harness 可以在消息对象中设置 `task` 字段来触发这些行为：

```python
# 判断是否需要搜索
messages = [
    {"role": "user", "content": "今天天气怎么样？", "task": "action"}
]
# → model outputs "Search"

# 生成搜索查询词
messages = [
    {"role": "user", "content": "今天天气怎么样？", "task": "query"}
]
# → model outputs "北京 天气预报 2026-07-16"
```

不需要额外的模型或 prompt engineering。Harness 只需要知道哪个场景用哪个 task，然后把 `task` 字段塞进消息对象即可。

---

## 局限与待验证

1. **Task 输出不可控。**Quick Instruction 的输出格式没有严格 schema。模型可能返回 "Search" 也可能返回 "Search\n" 或带额外解释。Harness 需要做输出清洗。
2. **与其他功能交互未知。**当 message 同时有 `task` 和 `tools` 时行为如何？源码中的行为是 task token 拼接在消息末尾，但如果消息同时有 tool_calls，可能会出现意外的 token 序列。
3. **不同 thinking mode 下的行为差异。**`action` task 在 chat mode 和 thinking mode 下的编码逻辑不同（L381），但实际上两者的最小差异需要实验验证。

---

## 验证路径

1. 对同一 prompt 分别设置 `task="action"` 和 `task=None`，对比模型输出的长度和内容差异。
2. 测量 action task 的端到端延迟：`task="action"` 的一次调用 vs. 完整对话的第一轮推理——验证延迟优势。
3. 测试 task 与 tool_calls 共存时的行为：是否会产生 token 序列错误。

---

*本文基于 `encoding_dsv4.py` 第 28-35 行 `DS_TASK_SP_TOKENS` 定义与第 369-383 行 task token 渲染逻辑，结合 DeepSeek V4 编码文档中的 Quick Instruction 描述。*
