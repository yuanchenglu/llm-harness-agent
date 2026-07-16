# Reasoning Content Stripping: Agent 应该知道什么不该回传

> **证据说明：** 本文提出的是 Harness 设计假设与验证路径。除非明确给出固定版本源码、运行路径和可复现实验，否则“验证”不等于已证明普遍最优。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> 创新索引: I-14
> **LLM + Harness = Agent** · 第 14 篇
> 系列: [LLM + Harness = Agent](../../README.md)
> 关联: [I-13 Byte-Stable Prefix 架构](13-byte-stable-prefix-architecture.md)

---

## 问题: 花了钱但没有任何价值的 Token

一个看起来简单的问题：推理模型思考完之后，你应该把它的思维链发回 API 下一轮吗？

直觉答案是"应该——模型需要之前的推理来保持连贯性。"Claude Code 这么做。大多数 Agent 这么做。OpenAI API 格式甚至在 assistant message 上有一个专门的 `reasoning_content` 字段，暗示你应该回传。

但用 DeepSeek 时，实际发生了这个：

```
第 1 轮: 用户提问
  → 模型生成: reasoning_content (~800 tokens) + response (~200 tokens)
  → 计费: prompt (cached) + completion (1000 tokens)

第 2 轮: 用户追问
  → 你发送: system + 第1轮消息(含 800 tokens reasoning_content) + 新问题
  → DeepSeek 把那 800 tokens 的 reasoning_content 当作: 普通 PROMPT INPUT
  → 计费: prompt (多了 800 tokens，不享受 cache) + completion
  → 每轮浪费: ~500 tokens 的无意义 prompt input，每一轮
```

50 轮编程 session，大约 25,000 tokens 的纯浪费。绝对值不大（¥0.007），但问题是：**100% 的浪费。**你在付钱让模型重读它自己的想法，而得不到任何回报。

---

## 行业默认: 全部回传

看看目前 Agent 对 reasoning content 的处理：

| Agent | 行为 | 成本影响 |
|-------|------|---------|
| **Claude Code** | 回传 thinking blocks（Anthropic 要求，tool-call 连续性） | 零 — Anthropic cache 覆盖 signed thinking blocks |
| **Hermes** | 存入 `assistant_msg["reasoning"]`，包含在消息历史中 | Provider 依赖；未专门 strip |
| **CodeWhale** | 未专门文档化 | 未知 |
| **Reasonix** | **条件 strip** reasoning_content in `buildRequest()`：非 tool-call 轮次剥离；tool-call 轮次保留（API 协议要求） | 源码确认：非 tool-call 轮次减少输入；tool-call 轮次因 API 要求保留 |

行业默认是全量回传。大多数 Agent 框架把消息历史当作完整日志——模型说了什么，你全发回去。这是最简单的实现：`messages.append(response)`，完事。没有过滤逻辑。没有特殊情况。

但"最简单的实现"不等于"正确的行为"。而两者之间的差距随着推理模型成为默认而扩大。

---

## 关键区分: 模型需要的 vs. 模型已经有的

核心洞察出奇地简单：

> **是否需要回传推理内容是 provider 协议问题，而不是普遍真理。** 模型通常需要用户消息、工具调用和工具结果来保持任务连续性；推理内容是否还需要回传，必须按 endpoint、thinking 模式和工具调用协议测试。

想一下推理是怎么工作的。模型生成思维链来得到答案。这条思维链是**得到答案的过程**，不是**未来答案的上下文**。答案一旦给出，推理就完成了它的使命。

这和工具结果有根本区别。工具结果告诉模型它之前不知道的东西——文件内容、命令输出、grep 匹配。那是塑造未来决策的新信息。Reasoning content 只是模型如何处理已有信息的记录。

**Assistant 输出的三类内容：**

| 类别 | 示例 | 应该回传？ | 原因 |
|------|------|----------|------|
| **Tool calls** | `read_file("main.go")` | ✅ 是 | 模型需要知道调了什么工具和结果 |
| **最终回答** | "bug 在 42 行" | ⚠️ 看情况 | 对话连贯性需要，但可压缩 |
| **Reasoning content** | "让我想想...先检查..." | ⚠️ 按协议 | 可能只用于展示，也可能是工具调用连续性所需字段 |

这里 provider 特定知识变得关键。Anthropic 的 thinking blocks 带加密签名，且当 tool call 跟随 thinking 时*必须*回传——这是协议要求，且被缓存。部分 DeepSeek-compatible 实现可以不回传 `reasoning_content`，另一些 thinking/tool-call 路径可能要求或主动 replay。它的计费与缓存行为也应以具体 endpoint 的实际 usage 数据为准。

一个聪明的 Agent 应该知道自己连的是哪个 provider，并据此调整回传行为。

---

## 实现案例: 少发送字段可能节省输入 Token

Reasonix 的做法极其简单——但有重要例外。在 `openai.go` 的 `buildRequest()` 里：

```go
// reasoning_content is deliberately NOT sent back for non-tool-call turns:
// it's a response-only field. DeepSeek accepts it but counts it as ordinary
// prompt input (measured ~500 extra tokens per turn on a reasoner chain).
//
// ⚠️ 重要例外：当 assistant turn 包含 tool_calls 时，reasoning_content 必须保留
// （DeepSeek API 协议要求——tool_calls 轮次丢失 reasoning_content 会导致 400 错误）
cm := chatMessage{
    Role:       string(m.Role),
    Content:    m.Content,       // ← 主内容
    ToolCallID: m.ToolCallID,
    Name:       m.Name,
    // ReasoningContent 在非 tool-call 轮次不传；tool-call 轮次必须保留
}
```

就这些。`Message` 结构体有 `ReasoningContent` 字段。它存在 session 里。它展示给用户。但在构建 API 请求时，它就是不复制到 wire format 里。

这段“少发送字段”的代码可能在长 session 中减少输入 token；实际节省量与正确性必须按 endpoint 和任务复现。

---

## DeepSeek V4 原生实现：`_drop_thinking_messages`

Reasonix 的实现是一个 Harness 层面的正确选择。但更有趣的问题是：**DeepSeek 自己是怎么处理这个问题的？**

V4 的 `encoding_dsv4.py` 给出了明确答案。这不是事后补救，而是 V4 训练时就已经嵌入 tokenizer 编码层的原生逻辑。

### 核心机制：双层过滤架构

V4 的 reasoning content stripping 不是单一策略，而是**数据层 + 渲染层**双层防护：

```
encode_messages() 入口 (L510: drop_thinking=True)
  │
  ├─ 第一层：_drop_thinking_messages() — 数据层 (L575-599)
  │   └─ 在渲染前修改消息列表本身：
  │        · 保留 role ∈ {user, system, tool, latest_reminder, direct_search_results}
  │        · 保留 last_user_idx 之后的所有消息
  │        · last_user_idx 之前的 assistant：移除 reasoning_content 字段
  │        · last_user_idx 之前的 developer：整条丢弃
  │
  └─ 第二层：render_message() 中的 drop_thinking — 渲染层 (L344-348)
      └─ 即使 reasoning_content 意外残留，渲染时也跳过 thinking_part
```

#### 第一层：`_drop_thinking_messages` — 在数据结构上做减法 (L575-599)

```python
# encoding_dsv4.py L575-599
def _drop_thinking_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Drop reasoning_content and non-essential messages before the last user message.

    Behavior:
    - Messages with role in ["user", "system", "tool", "latest_reminder"] are always kept.
    - Messages at or after the last user index are always kept.
    - Assistant messages before the last user get reasoning_content removed.
    - Developer messages before the last user are dropped entirely.
    """
    last_user_idx = find_last_user_index(messages)  # L209
    result = []
    keep_roles = {"user", "system", "tool", "latest_reminder", "direct_search_results"}

    for idx, msg in enumerate(messages):
        role = msg.get("role")
        if role in keep_roles or idx >= last_user_idx:
            result.append(msg)
        elif role == "assistant":
            msg = copy.copy(msg)
            msg.pop("reasoning_content", None)  # ← 就地删除字段
            result.append(msg)
        # developer and other roles before last_user_idx are dropped

    return result
```

关键点：`msg.pop("reasoning_content", None)` 是**就地删除**（L595），不是过滤整条消息。assistant 消息仍然保留在列表中——`content` 和 `tool_calls` 完好无损——只是 `reasoning_content` 字段没了。这确保后续的 `render_message()` 拿到的消息结构已经干净。

#### 第二层：`render_message` 中的防御 (L344-348)

```python
# encoding_dsv4.py L344-348
if thinking_mode == "thinking" and not prev_has_task:
    if not drop_thinking or index > last_user_idx:
        thinking_part = thinking_template.format(reasoning_content=rc) + thinking_end_token
    else:
        thinking_part = ""  # ← 即使是残留数据，渲染层也跳过
```

渲染层有独立的 `drop_thinking` 检查：即使第一层的数据清理因某种原因失败，渲染层也不会把旧轮次的推理内容编码进 prompt。

### tools 自动禁用 drop：协议优先于优化

V4 最值得注意的设计选择是 L548-551：

```python
# encoding_dsv4.py L548-551
# Resolve drop_thinking: if any message has tools defined, don't drop thinking
effective_drop_thinking = drop_thinking
if any(m.get("tools") for m in full_messages):
    effective_drop_thinking = False
```

只要消息历史中**任何一条**消息带有 `tools` 字段，整个 session 的 `drop_thinking` 就被强制设为 `False`。这印证了论文之前提到的 Reasonix 观察——tool-call 轮次丢失 reasoning_content 会导致 API 报错（400）——但 V4 的实现策略不同：**不是"检测当前轮是否有 tool_calls 然后条件保留"，而是"全有或全无"**——有工具就全保留，没工具就全剥离。

这种"全有或全无"策略有两个优势：
1. **实现简单**：不需要逐轮判断 tool_calls 存在性，一次 Boolean 决定整个 session
2. **防错安全**：不存在"应该保留 reasoning 但判断失误"的边界情况——要么全留，要么全不留

代价是 tool-call session 中每个轮次的 reasoning 都保留，即使其中某些轮次不包含 tool_calls 且理论上可以安全剥离。

### Reasonix Go 实现 vs DeepSeek V4 Python 实现

| 维度 | Reasonix `buildRequest()` (Go) | V4 `_drop_thinking_messages` (Python) |
|------|-------------------------------|--------------------------------------|
| 剥离方式 | 在构建 API 请求时**不复制** `ReasoningContent` 字段到 wire format | 在编码 prompt 前**就地 pop** `reasoning_content` 字段 + 渲染层防御 |
| tool-call 处理 | 非 tool-call 轮次 strip；tool-call 轮次保留（API 协议要求）| 有 tools 则**全局禁用** drop；无 tools 则全部 strip |
| 保护层数 | 1 层（wire format 边界） | 2 层（数据结构层 + 渲染层） |
| 策略粒度 | 逐轮判断 | 全有或全无 |
| 处理时机 | API 请求构建时 | Tokenizer 编码时（早在 API 请求之前） |
| 对其他消息类型的处理 | 仅聚焦 reasoning content | 同时处理 developer 消息（整条丢弃）、保留 keep_roles 消息 |
| 证据等级 | A0（源码确认，实际运行） | A1（源码确认，未在实际部署中复现） |

### 设计洞察：为什么 V4 把 stripping 放在 tokenizer 层

Reasonix 是在 API 边界做 stripping——具体说是在构建 HTTP 请求 body 时决定发什么不发什么。V4 则在 tokenizer 编码层做这件事，更早，更深。

这意味着：

1. **token 计算也是正确口径**：因为 stripping 发生在 tokenization 之前，被移除的 reasoning 既不参与 token 计数，也不进入 prompt cache 计算
2. **与其他编码逻辑一体**：`_drop_thinking_messages` 紧接在 `merge_tool_messages` 和 `sort_tool_results_by_call_order` 之后执行（L538-554），tool message 处理、排序、reasoning stripping 都在同一条处理管道中
3. **不依赖上层调用者**：即使 Harness 忘记处理 reasoning content，V4 的 encoding 层也会兜底清掉——只要 Harness 正确调用了 `encode_messages()`

> **证据等级：A1**（源码确认，Flash 和 Pro 实现一致）。`_drop_thinking_messages` 的存在和完整逻辑由 `encoding_dsv4.py` L575-599 验证；双层保护由 L344-348 和 L595 之间的协作确认；tools 全局禁用由 L548-551 验证。token 节省量的具体数值仍需实测（证据等级 B）。

---

## 通用原则: Agent 的"不发"清单

从 reasoning content 拉远来看。每个 Agent 都应该维护一个明确的清单：哪些东西不应该包含在 API 请求中——即使它把这些信息存在本地。

**"不发"检查清单:**

1. **Reasoning content** — 按 provider contract 决定 drop / replay / summarize，并记录 usage
2. **过大的 tool schemas** — 通过稳定排序和 progressive disclosure 缩小工具面；多数 API 每次请求仍要求完整 tools 字段，不能假设支持 delta
3. **过时的 system instructions** — 如果约束被取代，删除旧版本，不要只追加新版本
4. **冗余的错误信息** — 截断到可操作部分；模型不需要完整 stack trace
5. **冗余的文件内容** — 如果文件被读了、改了、又读了，旧读结果是噪音

每一条都是小优化。累积起来，这是一个"流血 token"的 Agent 和一个"外科手术般精准"的 Agent 之间的差距。

---

## 对 Hermes 意味着什么

Hermes 目前把 reasoning content 存在 `assistant_msg["reasoning"]` 中，包含在发送给 API 的消息历史里。对 Anthropic 模型这是对的（签名 thinking blocks，被缓存）。对 DeepSeek-compatible endpoint，需要先验证是否属于浪费以及是否会破坏工具调用连续性。

修复不复杂：

1. **Provider 感知的消息策略。**在构建 API 请求 payload 之前，根据 provider、模型、thinking 模式和工具调用阶段选择 drop / replay / summarize；只有协议测试确认可删除时才 strip。

2. **保留 reasoning 用于展示。**Session DB 和用户的聊天视图仍应显示 reasoning。Strip 只发生在 API 边界——HTTP 请求前的最后一层。

3. **做成可配置策略。**有些用户要 reasoning 在上下文里用于调试或研究。默认策略必须来自协议测试；允许按 provider、模型和模式配置，并在错误时安全回退。

---

## 更深层的洞察: 每个 Token 都应证明自己的存在价值

Reasoning content stripping 是最明显的案例，但底层原则更广：

> **API 请求中的每个 token 都应该有存在的明确理由。如果它既不提供模型需要的新信息，也不贡献于 cache 稳定性，就是浪费。**

这听起来像废话。但大多数 Agent 代码库不是这样运作的。它们按"包含 session 里的一切"运作。消息历史被当作完整日志，完整日志被发给 API。

Cache-first agent 反转这一点。它问："模型产生下一个响应需要的**最小** token 集合是什么？"其他所有东西——展示内容、调试日志、内部状态、过去的推理——留在本地。

Reasonix 在一个具体案例上做对了。下一步是把同样的审视应用到 Agent 发送的**每一个内容类别**上。

---

## 5. 验证路径

### 5.1 已验证（源码确认）

以下事实已由 `encoding_dsv4.py` 固定版本源码直接确认，证据等级 A1：

| # | 事实 | 证据 | 等级 |
|---|------|------|------|
| 1 | `encode_messages()` 默认 `drop_thinking=True` | L510 | A1 |
| 2 | 任何消息含 `tools` 字段时，`effective_drop_thinking` 强制设为 `False` | L548-551 | A1 |
| 3 | `_drop_thinking_messages` 保留 role ∈ `{user, system, tool, latest_reminder, direct_search_results}` 的消息 | L587 | A1 |
| 4 | `_drop_thinking_messages` 用 `msg.pop("reasoning_content", None)` 就地删除字段（L595），而非删除整条消息 | L594-595 | A1 |
| 5 | last_user_idx 之前的 developer 消息被整条丢弃 | L597（隐式：不在 keep_roles 中且不是 assistant，被跳过） | A1 |
| 6 | `render_message` 中有独立的 `drop_thinking` 检查作为渲染层防御（L344-348） | L344-348 | A1 |
| 7 | `_drop_thinking_messages` 在 `encode_messages()` 中调用，位于 tool message 合并和排序之后、渲染之前 | L553-554 | A1 |
| 8 | Reasonix 在 `buildRequest()` 中条件剥离 non-tool-call 轮次的 `reasoning_content` | Go 源码已审查 | A0 |

### 5.2 待验证

以下推论需要实测确认，当前证据等级 B（工程推论）：

#### 实验 1：token 节省量实测

```
工具：DeepSeek V4 API，100 轮编程 session（无 tool_calls）
对比：
  A. 回传所有 reasoning_content（drop_thinking=False）
  B. 剥离历史 reasoning_content（drop_thinking=True，默认）
测量：每轮 prompt input token 数、总 session 费用
预期：B 组每轮节省 ~500 tokens（与 Reasonix 文档所述量级一致），
      50 轮累计节省 ~25,000 tokens
```

#### 实验 2：tool-call session 的 reasoning 必要性

```
工具：DeepSeek V4 API，50 轮含 tool_calls 的编程 session
问题：V4 选择了"有 tools 就全保留"的策略（L548-551），
      但并非所有含 tool_calls 的轮次都需要前序 reasoning
对比：
  A. 全保留 reasoning（默认行为）
  B. 仅保留含 tool_calls 的轮次的 reasoning，剥离纯文本轮次的 reasoning
测量：模型是否正确完成多步工具调用任务、有无 400 错误
预期：B 组在特定场景下可能正常，但 V4 选择了安全优先的"全有或全无"
```

#### 实验 3：不同 thinking_mode 下的行为差异

```
工具：DeepSeek V4，thinking_mode="chat" vs "thinking"
对比：
  A. chat 模式 + drop_thinking=True
  B. chat 模式 + drop_thinking=False
  C. thinking 模式 + drop_thinking=True
  D. thinking 模式 + drop_thinking=False
测量：各模式的 token 消耗、推理质量（多轮一致性）、tool-call 正确率
注意：chat 模式下模型不产生 thinking block，drop_thinking 参数可能无实际效果
```

#### 实验 4：Harness 适配验证

```
任务：在 Reasonix 或 Hermes 中集成 V4 的 encoding_dsv4.py 作为 tokenization 层
测量：
  - 适配所需的代码行数（预估 ~50 行 Go/Python wrapper）
  - 是否正确利用 _drop_thinking_messages 的默认行为
  - _drop_thinking_messages 的 msg.pop() 是否会影响 Harness 本地消息缓存
关键问题：V4 的 stripping 修改了消息对象本身（L595: msg.pop），
          Harness 需要做 deep copy 以避免本地状态被意外修改
```

---

*本文基于追踪 Reasonix `buildRequest()` 的源码分析（Go），以及 DeepSeek V4 官方 `encoding/encoding_dsv4.py` 第 575-599 行 `_drop_thinking_messages` 和第 344-348 行 `render_message` 中 `drop_thinking` 逻辑的源码验证。V4 源码版本：Flash 和 Pro 完全一致（744 行）。*
