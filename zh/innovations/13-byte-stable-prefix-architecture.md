# Byte-Stable Prefix 作为架构约束：不只是缓存 System Prompt——让整个 Agent 以 Cache 优先

> **证据说明：** 本文提出的是 Harness 设计假设与验证路径。除非明确给出固定版本源码、运行路径和可复现实验，否则“验证”不等于已证明普遍最优。请先阅读 [研究方法与事实校准](../RESEARCH-METHOD-zh.md)。

> 创新索引: I-13
> **LLM + Harness = Agent** · 第 13 篇
> 系列: [LLM + Harness = Agent](../README-zh.md)
> 关联: [I-04 KV Cache Prefix 硬约束注入](04-kv-cache-prefix-zh.md) · [I-05 文档 KV Cache 优化](05-document-kv-cache-zh.md)

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

而这就是值得带回来的创新。

---

*本文基于阅读 Reasonix Go 源码的每一个相关行。分析溯源: `boot.go`, `input.go`, `memory.go`, `agent.go`, `coordinator.go`, `openai.go`, `provider.go`, `index.go`, `controller.go`, `store.go`, `SPEC.md`, `cachehit_e2e_test.go`。*
