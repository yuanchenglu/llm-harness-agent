# Byte-Stable Prefix 作为架构约束：不只是缓存 System Prompt——让整个 Agent 以 Cache 优先

> **证据说明：** 本文提出的是 Harness 设计假设与验证路径。除非明确给出固定版本源码、运行路径和可复现实验，否则“验证”不等于已证明普遍最优。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> 创新索引: I-13
> **LLM + Harness = Agent** · 第 13 篇
> 系列: [LLM + Harness = Agent](../../README.md)
> 关联: [I-04 KV Cache Prefix 硬约束注入](04-kv-cache-prefix.md) · [I-05 文档 KV Cache 优化](05-document-kv-cache.md)

---

## 问题: Cache 意识应该是架构，而不是补丁

I-04 确立了一个原则："约束能活下来，不是因为压缩算法聪明，而是因为它们从未进入过压缩区。"那是物理隔离——把关键指令放进 KV Cache 前缀区，压缩碰不到它们。

但有一个更深的问题潜伏着：**"cache 意识"应该是一个你后来加上的功能，还是一个决定整个 Agent 架构的约束？**

看一下行业现状。每个主流 Agent 平台都有某种形式的缓存优化：

- **Hermes** 把 `_cached_system_prompt` 持久化到 Session DB，下一轮恢复使用
- **Claude Code** 用 Anthropic 的 1 小时 prompt cache，做 system prompt 分段
- **CodeWhale** 把 `<user_memory>` 放在 prompt 组装中 "volatile-content boundary 之上"

这些都是**功能**。一个函数调用，一个条件判断。System prompt 在方便的时候缓存，需要的时候重建。Cache 意识是架构树上的一片叶子。

但还有另一种做法。

如果 cache 稳定性不是一个功能，而是所有架构决策都要遵守的**根约束**呢？

如果每个组件——Memory、Skills、Plan Mode、Model Switching、Context Compaction——在做任何事之前必须先回答一个问题：

> **"这个决策是否保持了 system prompt 前缀的字节稳定性？"**

这就是我在 **DeepSeek-Reasonix**（esengine/DeepSeek-Reasonix）里发现的架构。这不是营销话术。它在源码的每一层。

---

## 架构: Cache-First 作为根约束

"cache-first 架构"在代码里到底长什么样。以下每一项都对照 Go 源码 `internal/` 验证过。

### 启动序列: 组装一次，永久冻结

```go
// boot.go L100-124 — system prompt 在启动时组装一次
sysPrompt = outputstyle.Apply(sysPrompt, st)     // 1. Output style
sysPrompt += "\n\n" + config.LanguagePolicy       // 2. 静态语言策略
sysPrompt = memory.Compose(sysPrompt, mem)         // 3. Memory（base 在前）
sysPrompt = skill.ApplyIndex(sysPrompt, skills)    // 4. Skills 索引（仅名称，不含 body）
```

这之后，`sysPrompt` 是一段冻结的字节序列。整个 session 期间永不改变。用户切 Plan Mode？不变。Memory 被写入？不变。Background job 完成？不变。

任何必须让模型感知的变化都走 **turn tail**——注入到用户消息中，而不是系统前缀：

```go
// input.go L18-52 — Compose() 把瞬态上下文注入到用户消息头部
func (c *Controller) Compose(text string) string {
    if plan { text = PlanModeMarker + "\n\n" + text }       // Plan mode → 用户消息
    if len(notes) > 0 { text = "<memory-update>..." + text }  // Mid-session memory → 用户消息
    if c.jobs != nil { text = "<background-jobs>..." + text }  // BG 完成 → 用户消息
    return text
}
```

这就是架构反转。在大多数 Agent 里，你会直接改 system prompt。在 cache-first agent 里，你把它视为受控变更，而不是随意变更。System prompt 默认冻结；安全更新、工具变化或错误修复仍允许显式重建。

---

### 这个约束如何塑造六个子系统

#### 1. Memory: Base-First 协议 + Mid-Session 注入

```go
// memory.go L148-152
// Base stays first (it is the most stable text, so
// it remains a valid cache prefix even when memory changes between sessions)
```

两个设计决策：

- **Base 永远在最前面。**即使 session 之间的 Memory 变了，base prompt 不变 → DeepSeek 的 prefix cache 仍然命中 base 部分
- **Mid-session Memory 写入绝不碰前缀。**`remember` 工具保存 fact 时，立即写磁盘，但模型通过**下一轮用户消息中的 `<memory-update>` 块**感知到它，而不是 system prompt 突变。它在下一次 session 启动时自然融入前缀

这不是"追加到 system prompt"——这是一个时间协议：session N-1 写入 → session N 的 boot 将其吸收进不可变前缀。

#### 2. Skills: 索引在 Prefix，Body 按需

```go
// index.go L9 — 包的声明式契约
// cache-stable system-prompt prefix; bodies never enter the prefix.
```

只有 skill 的**名称和一行描述**进入系统前缀。每个 skill body 通过 `run_skill` 工具或 `/name` 按需加载。Body 一旦进入前缀——你安装新 skill、编辑已有 skill——缓存就炸了。

#### 3. Plan Mode: 零痕迹切换

```go
// agent.go L127-130
// planMode, when true, refuses any tool call whose ReadOnly() is false.
// The system prompt and tool list never change with the toggle
```

Plan mode 切换 Agent 的一个布尔值。行为变了——writer 被拒绝，模型收到 "blocked" 结果。但 system prompt 和 tool schema 字节完全相同。切换的缓存代价：**零**。

#### 4. 双模型协作: 独立 Session 或不协作

```go
// coordinator.go L25-27
// Coordinator runs two models in separate sessions to keep each one's
// prompt prefix cache-stable. The sessions never mix.
```

显而易见的做法：让 executor 在对话中途调用 planner——切换模型一轮、拿到计划、切回来。大多数实现会这么做。

Reasonix 反其道而行。Planner 和 executor 各有**独立的 Session 和独立的 system prompt**。它们从不共享消息。SPEC 明说：

> "switching models inside one shared conversation would break the prefix and tank cache hits, so we don't."

当"cache 稳定"是根约束，你不会修复模型切换问题——你让模型切换在架构上不可能。

#### 5. Reasoning Content: 不要为思考付两次费

```go
// openai.go L171-184
// reasoning_content is deliberately NOT sent back: DeepSeek accepts it but
// counts it as ordinary prompt input (~500 extra tokens per turn)
```

`reasoning_content` 的回传策略取决于具体 endpoint 与 thinking/tool-call 协议。某些实现选择不回传以降低输入，另一些路径会 replay；必须用协议和 usage 实验裁决。

Reasonix 在 `buildRequest()` 中显式 strip。Session 本地保留供 display/archive，但绝不再传到 API。

#### 6. Context Compaction: 主要的显式 Cache Reset 点

```
SPEC.md L177-197
- prompt_tokens 达到 compactRatio (0.8) × context_window 时，compact 一次
- Session 变成: system + summary + recentKeep (默认 8) 完整消息
- 这是设计上主要的显式历史重写点；配置、安全策略和工具变化仍可能触发重建
- 两次 compaction 之间，session 纯追加增长
```

Compaction 不是持续的后台进程。恰好触发一次。之后前缀重置——一个刻意的 cache-reset 点。默认：1M token window × 0.8 = **800K prompt tokens** 才 compact 第一次。

---

### 7. DeepSeek V4 编码层：模型原生的前缀稳定性

以上六个子系统是从 **Agent 框架层**（Reasonix Go 源码）确立的 cache-first 架构。但这里有一个更深的问题：**这个原则是 Agent 工程的发明，还是 Transformer 注意力物理规律的必然？**

答案藏在 DeepSeek V4 的官方模型编码层。`encoding/encoding_dsv4.py`（Flash 与 Pro 版本实现一致）中有一个看似细节的函数——`_drop_thinking_messages`（L575-599）——它做的事情，与 Reasonix 的 cache-first 架构在逻辑上完全同构，只是作用在**模型编码层**而非 Agent 框架层。

#### 核心机制：`_drop_thinking_messages` 的角色过滤

```python
# encoding_dsv4.py L510 — drop_thinking 默认 True
def encode_messages(
    messages: List[Dict[str, Any]],
    thinking_mode: str,
    context: Optional[List[Dict[str, Any]]] = None,
    drop_thinking: bool = True,  # 默认丢弃旧轮次的 reasoning
    ...
)
```

`encode_messages` 的默认行为是：**丢弃所有 `last_user_idx` 之前的 assistant 消息中的 `reasoning_content`**。但关键在于它**不是**简单粗暴地全删——它有一个精确的角色过滤规则：

```python
# encoding_dsv4.py L587
keep_roles = {"user", "system", "tool", "latest_reminder", "direct_search_results"}
```

这些角色是**永远保留的**。它们构成对话的前缀骨架——无论对话多长、thinking 块多大，这些角色的消息字节不会被触碰。再看具体逻辑：

```python
# encoding_dsv4.py L591-597
if role in keep_roles or idx >= last_user_idx:
    result.append(msg)              # 稳定角色 + 最新轮次 → 完整保留
elif role == "assistant":
    msg = copy.copy(msg)
    msg.pop("reasoning_content", None)  # 旧轮次的 assistant → 只剥离思考
    result.append(msg)                  # content 和 tool_calls 保留
# developer 和其他角色 → 整条丢弃（它们是瞬态调试内容）
```

#### 与 Reasonix Cache-First 的同构对应

这张表揭示了两者在不同层实现了同一个模式：

| 维度 | Reasonix（Agent 框架层） | V4 encoding_dsv4.py（模型编码层） |
|------|--------------------------|-----------------------------------|
| **稳定层（永远保留）** | System prompt（boot 时冻结）；Base memory（位置固定）；Skills 索引（名称+描述） | `system`、`user`、`tool`、`latest_reminder` 角色的消息 |
| **半稳定层（内容保留，负载剥离）** | Mid-session memory 写入磁盘但不碰前缀；Skill body 不进入前缀 | 旧轮次 `assistant` 消息：`content` 和 `tool_calls` 保留，`reasoning_content` 剥离 |
| **瞬态层（丢弃）** | Reasoning content 不传回 API（`openai.go` L171-184） | `developer` 角色消息整条丢弃；旧轮次的 `reasoning_content` 不编码 |
| **功能正确性优先** | SPEC 规定 switching models would break the prefix——宁可牺牲灵活性也不打破前缀 | L548-551：`tools` 存在时 `effective_drop_thinking = False`——tool-call 链需要完整推理上下文 |

最关键的对应是第四行：**前缀稳定性的最终目的是服务功能正确性**。Reasonix 说"切换模型会破坏前缀，所以我们不做"；V4 说"当有 tool-call 链时，需要完整推理上下文，所以不 drop thinking"。两者都不是为了缓存而缓存——缓存是手段，正确性是目的。

#### 为什么这件事重要：跨层印证

I-13 的论点来自 Agent 工程的实践观察：让 system prompt 字节保持稳定 → KV Cache 命中 → 成本降低且推理质量不退化。这看起来像一个"Agent 框架的设计选择"。

但 V4 `_drop_thinking_messages` 的存在表明：**模型团队在编码层也在做同样的事，基于同样的物理理解。** `system`、`user`、`tool` 角色被硬编码为"永不丢弃"——不是因为这些角色"重要"这样一个模糊的设计直觉，而是因为：

1. **Transformer 的 prefix cache 只对字节前缀生效。** 前缀中的任何字节变化（插入、删除、修改）都会使该位置之后的所有 cache 失效。
2. **`system`/`user`/`tool` 消息构成对话的结构骨架。** 它们是"变化最小"的部分——用户问一个新问题，上一轮的 system 指令不会变、tool 定义不会变、更早的 user 消息不会变。
3. **`reasoning_content` 是最大且最易变的负载。** 一个 thinking block 可能 2000+ tokens，且每轮内容完全不同——它是 prefix cache 的头号杀手。

V4 的 `_drop_thinking_messages` 是用 Python 写的，Reasonix 的 cache-first 是用 Go 写的。它们面向不同的调用方（V4 编码层被 API 服务端调用，Reasonix 被 Agent 客户端调用）。但背后是同一个物理规律：**在 Transformer 自回归架构下，"稳定前缀 + 瞬态尾缀"是最优的信息组织方式。**

这不是 Agent 框架的"最佳实践"——这是注意力机制的"物理定律"。

---

## 核心原则: 分离"变化的"和"不变的"

如果拉远来看，这六个设计决策都是同一个原则的实例：

```
┌─────────────────────────────────────────────┐
│  稳定区（系统前缀，启动时冻结）                  │
│  • Base prompt                               │
│  • Output style / 语言策略                     │
│  • Memory（层级文档 + auto-index）             │
│  • Skills 索引（仅名称+描述）                   │
│  • Tool schemas                              │
│  ═══════════════════════════════════════════ │
│  → Mid-session 绝不改变                       │
│  → DeepSeek prefix cache 命中此区域 100%      │
├─────────────────────────────────────────────┤
│  可变区（turn 消息，追加）                      │
│  • Plan mode marker                          │
│  • Mid-session memory 更新                   │
│  • Background job 完成通知                    │
│  • Skill body（按需加载）                      │
│  • 用户输入 + tool 结果                        │
│  ═══════════════════════════════════════════ │
│  → Ride the turn tail                        │
│  → 下一次 session boot 时融入前缀              │
└─────────────────────────────────────────────┘
```

这不是一个功能。这是一个契约。每个组件必须遵守。

---

## Hermes 可以从中学到什么

Hermes 已经有 cache 意识——`_cached_system_prompt` 持久化、skill slash command 注入为 user message、Anthropic prompt cache 支持。这些是好的。但它们是**功能**，不是架构。

差距体现在这里：

| 场景 | Hermes（现状） | Reasonix（cache-first） |
|------|-------------|----------------------|
| **Mid-session memory 写入** | 可能修改 system prompt（取决于 provider） | 默认走 turn tail；重要安全/约束更新可显式重建 |
| **Plan mode 切换** | 可能修改 system prompt 或 tools | System prompt + tools 字节相同；marker 在 user message |
| **Mid-session 换模型** | 重建 system prompt（炸缓存） | 架构上不可能——独立 session |
| **Mid-session 装 skill** | 改变可用 skills 列表 | Index-only in prefix；新 skill 走 turn tail |
| **Reasoning 回传** | 未专门优化 | 显式 strip in buildRequest |

Hermes 的升级路径不是"加更多缓存功能"，而是：

1. **在 turn-0 冻结 system prompt。** Boot 之后，绝不变异。
2. **所有 mid-session 状态变化移到 turn tail 注入。** Memory 写、plan mode、模型提示——全部走 `Compose()`
3. **采用 base-first memory 协议。** 即使 memory 变化，base 保持字节一致。

---

## 为什么这件事超越 DeepSeek

DeepSeek 的定价让这个架构今天经济上合理：

- Cache Hit: ¥0.14 / 1M tokens
- Cache Miss (Input): ¥0.28 / 1M tokens
- **缓存 token 打五折**

但原则是模型无关的。Anthropic 有 prompt caching（1 小时 TTL）。OpenAI 有自动缓存。Google 有 context caching。每个主流 provider 都有某种 prefix-cache 折扣——而且折扣只在 prefix 字节稳定时生效。

Cache-first Agent 架构不只在 DeepSeek 上省钱。它在**每个提供 prefix caching 的 provider** 上省钱。而且随着 context window 增大、token 绝对价格下降但用量增加——可以被缓存的 token 比例增长速度超过单 token 成本的下降速度。

Cache-first 架构的经济论据随时间变强，不变弱。

---

## 更大的图景: 架构即节俭

I-04 教我们通过物理分离保护约束免受压缩。I-05 教我们结构化文档让 KV Cache 在读取间保持温暖。I-13 完成了三部曲：**让整个 Agent 架构 cache-stable，每个组件必须为任何违反此约束的行为给出理由。**

贯穿这三篇的统一线索是一种哲学：**token 不是免费的，省 token 的最好方式是从一开始就不发它们。**压缩减少 token。Cache-first 架构防止它们需要被发送。

Reasonix 目前是开源 Agent 代码中这一哲学最纯粹的表达。不是因为它"更好"——Hermes 有 Gateway、Cron、多 provider Memory 和 Reasonix 碰不到的生态。而是因为 Reasonix 问了一个更难的问题："如果 cache 稳定不是功能，而是法律，会怎样？"

而这就是值得带回来的创新。但 V4 `_drop_thinking_messages` 的发现增加了一层含义：cache-first 不是 Reasonix 的"设计选择"——它是 Transformer 物理规律在 Agent 框架层的投影。V4 的模型编码层独立得到了同构的结论，这印证了"稳定前缀优先"不是风格偏好，是物理约束。

---

## 5. 验证路径

### 5.1 已验证

| 证据 | 层 | 状态 | 验证方式 |
|------|-----|------|----------|
| Reasonix cache-first 架构 | Agent 框架层（Go） | **源码确认** | `boot.go` L100-124（system prompt 冻结）；`input.go` L18-52（瞬态上下文走 turn tail）；`memory.go` L148-152（base-first 协议）；`openai.go` L171-184（reasoning 剥离）；`SPEC.md` L177-197（compaction 策略） |
| V4 `_drop_thinking_messages` | 模型编码层（Python） | **源码确认** | `encoding_dsv4.py` L575-599：`keep_roles = {"user", "system", "tool", "latest_reminder", "direct_search_results"}` 无条件保留；旧轮次 `assistant` 消息剥离 `reasoning_content`；`developer` 角色整条丢弃 |
| V4 `tools` 禁用 drop | 模型编码层（Python） | **源码确认** | `encoding_dsv4.py` L548-551：`any(m.get("tools") for m in full_messages)` → `effective_drop_thinking = False`——功能正确性优先于缓存优化 |
| I-04 前缀注入约束保持率 | Agent 框架层 | **实验** | 15 轮对话后约束保持率 > 95%（前缀区物理隔离，压缩碰不到）。详见 [I-04](04-kv-cache-prefix.md) §5.1 |

> **跨层印证的核心发现**：Reasonix（Agent 框架层）和 V4 `_drop_thinking_messages`（模型编码层）在独立的设计空间中得出了同构的前缀稳定性策略——稳定角色永远保留、瞬态内容按轮次剥离。这不是巧合，是 Transformer 的 prefix-cache 物理规律同时在两个层起作用的结果。

### 5.2 待验证

以下问题当前证据不足，需要独立实验或更多源码确认：

- **V4 drop_thinking 在极长对话中的注意力稀释**（优先级：高）。当前确认了 `_drop_thinking_messages` **物理上保留**了 `system`/`user`/`tool` 角色的字节序列。但物理保留 ≠ 注意力分配。在 100+ 轮对话后，即使 system prompt 字节完整，模型对前缀远端内容的注意力权重可能被后续的 KV 对稀释。需要测试：在 100 轮对话中持续注入一个关键约束（如"config 文件绝对不能动"），对比 `drop_thinking=True` vs `drop_thinking=False` 条件下模型在最后一轮是否仍然遵守该约束。

- **Harness 层 cache-first 与 V4 模型层 drop_thinking 的联合效果**（优先级：高）。当 Reasonix 的 cache-first（Harness 层冻结 sysPrompt + 剥离 reasoning）和 V4 的 `_drop_thinking_messages`（模型编码层保留稳定角色 + 剥离旧轮 reasoning）同时启用时，两者是否存在协同或冲突？例如：Harness 层剥离 reasoning 后，V4 编码层的 `_drop_thinking_messages` 是否仍然有 reasoning 可剥离？两者的优化效果是叠加还是冗余？

- **其他模型的编码层前缀保护机制**（优先级：中）。Qwen、Llama、Claude 等主流模型的官方编码层是否有类似的"角色过滤"或"前缀保护"机制？如果有，它们的 `keep_roles` 集合是什么？与 V4 的集合（`system`/`user`/`tool`/`latest_reminder`）有何异同？这可以验证"稳定前缀是 Transformer 通用定律"的假设。

- **`latest_reminder` 和 `direct_search_results` 的前缀语义**（优先级：中）。V4 将 `latest_reminder` 和 `direct_search_results` 也列入 `keep_roles`，但它们在多轮对话中的生命周期和稳定性与 `system`/`user`/`tool` 不同。需要确认：这些角色在连续多轮中是否始终保持字节稳定？如果不是，将它们列入 keep_roles 是否会反而降低 prefix cache 命中率？

- **cache-first 架构的成本-收益定量模型**（优先级：低）。当前有定性结论（cache hit token 五折），但缺少定量模型。需要测量：一个典型的 50 轮 Agent 会话中，cache-first 架构相比"每次都重建 system prompt"的基线，token 成本节省多少？这个节省与 session 长度的函数关系是什么？

---

*本文基于阅读 Reasonix Go 源码（`boot.go`, `input.go`, `memory.go`, `agent.go`, `coordinator.go`, `openai.go`, `provider.go`, `index.go`, `controller.go`, `store.go`, `SPEC.md`, `cachehit_e2e_test.go`）和 DeepSeek V4 官方编码层源码（`encoding/encoding_dsv4.py` L500-600，Flash 与 Pro 版本实现一致）的每一个相关行。*
