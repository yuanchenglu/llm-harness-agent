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

*本文基于追踪 Reasonix OpenAI provider 中 `buildRequest()` 如何构建 API payload，并对比 Hermes `run_conversation()` 的消息组装和 Anthropic 的 signed-thinking 协议。*
