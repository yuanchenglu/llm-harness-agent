# DeepSeek-Reasonix 深度技术分析：Prefix Cache 优先的 Agent 架构

> **首次源码验证日期**: 2026-06-01；结论会随仓库演进而变化
> **仓库**: [esengine/DeepSeek-Reasonix](https://github.com/esengine/DeepSeek-Reasonix)
> **版本基线**: `main-v2` Go 重写版；引用实现时应固定具体 commit
> **本地路径**: `~/Code/DeepSeek-Reasonix`
> **对比对象**: Hermes Agent、CodeWhale (DeepSeek-TUI)

---

## 0. 一句话核心判断

**Reasonix 的突出特点，是把 DeepSeek Prefix Cache 命中率提升为一级架构约束。它不是已被证明的唯一实现，也不代表该策略已经在所有工作负载上最优。**

Readme 写得克制——"tuned around DeepSeek's prefix cache so token costs stay low across long sessions"。但源码里，这根本不是"调参"。整个系统提示词组装、Memory 注入、Skills 索引、Plan Mode 切换、Mid-session Memory 变更、双模型协作——每一处设计决策都受一条规则支配：

> **System prompt 必须是 byte-stable。任何变动都 ride the turn tail，绝不 touch the prefix。**

这跟现有的 LLM+Harness=Agent 系列形成了完美的技术对话——I-04 讲的是"约束不该进压缩区"，I-05 讲的是"文档结构应该 KV Cache 友好"。而 Reasonix 把这个逻辑推到了极致：**整个 Agent 的上下文管理都以 Prefix Cache 为中心**。

---

## 1. 源码架构速览

```
reasonix/ (Go, CGO_ENABLED=0, ~20MB static binary)
├── internal/
│   ├── agent/          # Session + 主循环 + 两模型协作(Coordinator) + 子Agent(task)
│   ├── boot/           # 一站式组装: config→provider→tools→memory→skills→controller
│   ├── control/        # 传输无关的 Controller: Compose/Checkpoint/Rewind/Branch
│   ├── provider/       # Provider接口 + Usage(cache hit/miss)
│   │   └── openai/     # OpenAI兼容实现; DeepSeek/MiMo仅是config
│   ├── tool/           # Tool接口 + Registry
│   │   └── builtin/    # read_file/write_file/edit_file/bash/grep/glob/ls
│   ├── memory/         # 层级memory(REASONIX.md/AGENTS.md) + auto-memory store
│   ├── skill/          # Skills: SKILL.md + frontmatter; index进prefix, body按需加载
│   ├── plugin/         # MCP client: stdio + Streamable HTTP
│   ├── permission/     # 逐call权限: deny > ask > allow
│   ├── sandbox/        # macOS Seatbelt; Linux bubblewrap planned
│   ├── command/        # 自定义slash命令(.reasonix/commands/*.md)
│   └── config/         # TOML配置解析
```

关键设计决策：
- **Go** 而非 Python/Rust/TS —— 单静态二进制，零依赖分发（只依赖一个 TOML parser）
- **Registry 模式** —— Provider 和 Tool 都是 interface，core 里没有 `switch model` 硬编码
- **Controller 是单一入口** —— 所有前端（TUI/HTTP SSE/Wails desktop）驱动同一个 `control.Controller`

---

## 2. 九个 DeepSeek 专属的 Prefix Cache 优化

以下每一项都经过源码验证，标注了具体文件和行号。

### 优化 1: Cache-Stable System Prompt — 整个前缀永不变异

**源码**: `internal/boot/boot.go` L100-124; `internal/control/input.go` L18-52

这是 Reasonix 最核心的设计原则。看 `boot.go` 的系统提示词组装流程：

```go
// boot.go L100-124
sysPrompt = outputstyle.Apply(sysPrompt, st)     // 1. 注入 output style
sysPrompt += "\n\n" + config.LanguagePolicy       // 2. 追加语言策略(静态文本)
sysPrompt = memory.Compose(sysPrompt, mem)         // 3. 追加 Memory（base 在前）
sysPrompt = skill.ApplyIndex(sysPrompt, skills)    // 4. 追加 Skills 索引（仅名称+描述）
```

这四步做完之后，`sysPrompt` 就是**整个 session 期间不变的字节序列**。Mid-session 的任何变化——Plan Mode 切换、Memory 写入、Background Job 完成——全部通过 `Compose()` 注入到**用户消息的头部**，而非系统前缀：

```go
// input.go L18-28
func (c *Controller) Compose(text string) string {
    if plan { text = PlanModeMarker + "\n\n" + text }       // Plan Mode marker → 用户消息
    if len(notes) > 0 { text = "<memory-update>..." + text }  // Mid-session Memory → 用户消息
    if c.jobs != nil { text = "<background-jobs>..." + text }  // BG Job完成 → 用户消息
    return text
}
```

**本质**: 系统前缀（base prompt + language + memory + skills index + tools schema）在 Agent 启动后就冻结。任何新的信息都 ride the turn tail，在当前轮生效，下一轮通过新 session 的 boot 自然融入前缀。这意味着 DeepSeek 的 Prefix Cache 只需要一次 warm-up，之后每个 turn 的 prompt_tokens 中绝大部分都是 cache hit。

---

### 优化 2: Reasoning Content 不回传 — 每轮省 ~500 tokens

**源码**: `internal/provider/openai/openai.go` L171-184

```go
// reasoning_content is deliberately NOT sent back: it's a response-only
// field. DeepSeek accepts it but counts it as ordinary prompt input
// (measured ~500 extra tokens per turn on a reasoner chain)
```

DeepSeek 的 `reasoning_content`（思维链）是 response-only 字段。如果在下一次请求中回传，DeepSeek 会把它当作普通 prompt input 计费——每轮多 ~500 tokens，没有任何缓存或推理连贯性收益。Reasonix 在 `buildRequest()` 中显式 strip，但 session 仍保留它供 display/archive。

---

### 优化 3: 专门的 Cache Hit 定价模型

**源码**: `internal/provider/provider.go` L94-99

```go
type Pricing struct {
    CacheHit float64   // 每 1M cached prompt tokens（比 Input 便宜得多）
    Input    float64   // 每 1M uncached prompt tokens
    Output   float64   // 每 1M completion tokens
}

func (p *Pricing) Cost(u *Usage) float64 {
    return (CacheHitTokens * CacheHit + CacheMissTokens * Input + CompletionTokens * Output) / 1e6
}
```

不是简单的 input/output 二分——单独 track cache hit tokens，按更低价计算。这对 DeepSeek 用户来说不是"锦上添花"，而是"成本模型正确性的必要条件"。

---

### 优化 4: 统一的 Cache 指标归一化

**源码**: `internal/provider/openai/openai.go` L311-321

```go
func normaliseUsage(u *wireUsage) *provider.Usage {
    hit := u.PromptCacheHitTokens          // DeepSeek: 顶层字段
    miss := u.PromptCacheMissTokens
    if hit == 0 && u.PromptTokensDetails != nil {
        hit = u.PromptTokensDetails.CachedTokens  // OpenAI/MiMo: 嵌套字段
    }
```

DeepSeek 把 cache 数据放在 `usage.prompt_cache_hit_tokens` / `prompt_cache_miss_tokens`（顶层），OpenAI/MiMo 放在 `usage.prompt_tokens_details.cached_tokens`（嵌套）。Reasonix 在 provider 层归一化，上层代码不关心 provider 是谁。

---

### 优化 5: Memory 的 Cache 优先级协议

**源码**: `internal/memory/memory.go` L148-152

```go
// Base stays first (it is the most stable text, so
// it remains a valid cache prefix even when memory changes between sessions)
```

`Compose(base, mem)` 保证 `base` 始终在最前面。即使两个 session 之间的 Memory 发生了变化，base prompt 不变 → DeepSeek 的 Prefix Cache 仍然 hit 了 base 部分。这不是一个"优化技巧"——是协议设计。

---

### 优化 6: Skills 索引与 Body 分离

**源码**: `internal/skill/index.go` L9; `internal/skill/skill.go`

```
// index.go:
// cache-stable system-prompt prefix; bodies never enter the prefix.
```

Skills 的**名称+描述**进入系统前缀（固定开销），**Body** 通过 `run_skill` 工具或 `/name` 按需加载。这跟 Hermes 的思路一致——Skills index 在 prefix 里，body 作为 tool 调用的结果注入——但 Reasonix 把这个原则写成了包的顶层注释。

---

### 优化 7: 双模型协作的独立 Session 隔离

**源码**: `internal/agent/coordinator.go` L25-27; `docs/SPEC.md` L166-175

```go
// Coordinator runs two models in separate sessions to keep each one's
// prompt prefix cache-stable: a low-frequency planner proposes an approach,
// then the executor carries it out. The sessions never mix, so
// neither model's prefix is disturbed by the other's turns.
```

这是对 SPEC.md 的精确执行：

> "switching models *inside one shared conversation* would break the prefix and tank cache hits, so we don't."

Planner 有自己的 `Session` + 独立 system prompt (`DefaultPlannerPrompt`)，无工具。Executor 有自己的 `Session`。两个 session 永不相交，各自 prepend-only 增长，各自享受 Prefix Cache。

---

### 优化 8: Context Compaction 被设计为少数显式 Cache Reset 点

**源码**: `docs/SPEC.md` L177-197

```
- When prompt_tokens reach compactRatio (default 0.8) of context_window, compact ONCE
- Summarizes older middle → session becomes system + summary + recentKeep (default 8)
- This is the ONLY point where the prompt prefix changes — a deliberate, rare
  "cache-reset point"
- Between compactions the session grows prepend-only and stays cache-friendly
```

Compaction 是**故意设计**的 cache reset 点，而不是随时可能发生的意外。频率由 `context_window` 和 `compactRatio` 控制。默认 1M token window × 0.8 = 每 800K prompt tokens 才 compact 一次。

---

### 优化 9: Plan Mode 的零 Cache 代价切换

**源码**: `internal/agent/agent.go` L127-130; `internal/control/input.go` L10-13

```go
// planMode, when true, refuses any tool call whose ReadOnly() is false.
// The system prompt and tool list never change with the toggle so the
// prompt-cache prefix stays valid; the gating happens at execute time
```

Plan Mode marker 是 `const PlanModeMarker` 字符串，注入到 user message 头部，**不在 system prompt，不在 tools schema**。所以 toggle plan mode 时，DeepSeek 的 Prefix Cache 完全不受影响。

---

## 3. 三方技术对比

### 3.1 与 Hermes Agent 的对比

| 维度 | Reasonix | Hermes |
|------|----------|--------|
| **语言/分发** | Go 静态二进制 (~20MB) | Python (pip/brew) |
| **Cache-First 设计深度** | ⭐⭐⭐⭐⭐ 核心架构原则，9 处显式优化 | ⭐⭐⭐⭐ 有 `_cached_system_prompt` 持久化恢复，但非全局架构约束 |
| **System Prompt 稳定性** | 启动后冻结；mid-session 变化全部 ride turn tail | 从 Session DB 恢复；可 rebuild（如 model switch 时） |
| **Memory 层设计** | Base-first 协议 → 跨 session cache hit；mid-session write 走 turn tail | 注入 system prompt；支持多种 memory provider（honcho/mem0/supermemory 等） |
| **Skills 机制** | Index-only in prefix；body on demand | Skill body 进入 system prompt（或 slash command 触发） |
| **双模型协作** | ✅ 独立 Session（planner + executor 不共享上下文） | ❌ 单 session |
| **Gateway/多平台** | ❌ 不支持 | ⭐⭐⭐⭐⭐ 15+ 平台（Feishu/Telegram/Discord/WeChat…） |
| **Cron/Scheduling** | ❌ 不支持 | ✅ 完整的 cronjob 系统 |
| **Checkpoints/Rewind** | ✅ Checkpoint store + Rewind | ❌ 无内置 checkpoint |
| **Sandbox** | macOS Seatbelt（Linux bubblewrap 规划中） | Docker/SSH 环境 |
| **Session 管理** | Branch/Tree/Rewind/Switch | Session DB + FTS5 搜索 + 恢复 |
| **社区规模** | 持续变化，需查看仓库当前数据 | 持续变化，需查看仓库当前数据 |

**关键差异**: 
- Reasonix 的 cache-first 是**全局架构原则**，Hermes 的 cache awareness 是**一个功能点**（`_cached_system_prompt`）
- Hermes 在 Gateway/Cron/Memory Provider 生态上压倒性领先
- Hermes 的 Memory 更灵活（多 provider），Reasonix 的 Memory 更 cache-friendly（base-first 协议）
- Reasonix 的 Go 单二进制 vs Hermes 的 Python 生态：前者分发简单，后者扩展性强

---

### 3.2 与 CodeWhale 的对比

| 维度 | Reasonix | CodeWhale |
|------|----------|-----------|
| **语言** | Go | Rust |
| **定位** | AI Coding Agent（通用） | 围绕 DeepSeek 模型构建的社区终端 Agent |
| **Cache-First 设计** | ⭐⭐⭐⭐⭐ 全局架构原则 | ⭐⭐⭐⭐ 有 prefix-cache 意识（MEMORY.md：above volatile-content boundary；SUBAGENTS.md：fork context 保留 prefix） |
| **Memory** | 层级文件 (REASONIX.md/AGENTS.md) + auto-memory store | `~/.deepseek/memory.md`（单一文件），通过 `remember` 工具写入 |
| **Skills** | SKILL.md + frontmatter (runAs/inline/subagent) + allowed-tools | 有 skills 目录扫描，但 Agent 不能自建 |
| **飞书桥** | ❌ | ✅ 已实现（SDK 长连接 + systemd + Lighthouse 部署） |
| **Multi-platform Gateway** | ❌ | ⚠️ 仅飞书（群聊需 /ds 前缀） |
| **Sub-Agent** | task 工具 + subagent skills | agent_open/agent_eval/agent_close + 7 种 role taxonomy |
| **Plan 确认** | Plan Mode + 权限门控 | Plan Confirmation 四选项弹窗（v0.8.44） |
| **CodeGraph** | ✅ 内置 codegraph MCP server（符号级代码理解） | ❌（用 grep/glob） |
| **Cron** | ❌ | ❌ |
| **社区规模** | 持续变化，需查看仓库当前数据 | 持续变化，需查看仓库当前数据 |

**关键差异**:
- CodeWhale 的缓存设计更实用主义——"让它能用就行"，Reasonix 是"把 cache 作为架构约束"
- CodeWhale 有更强的 sub-agent taxonomy（7 种角色），Reasonix 的子 agent 更简洁
- Reasonix 有内置 CodeGraph（符号级理解），CodeWhale 依赖 grep/glob
- CodeWhale 的飞书桥是生产级（README 推荐），Reasonix 完全没有消息平台

---

### 3.3 三方综合对比表

| 能力 | Reasonix | Hermes | CodeWhale |
|------|:--------:|:------:|:---------:|
| **Prefix Cache 作为架构原则** | ✅ 极致 | ⚠️ 部分 | ⚠️ 部分 |
| **Reasoning 不回传节省** | ✅ | ❌ | ❓ |
| **专门 Cache Hit 定价** | ✅ | ⚠️ 通过 Anthropic | ❓ |
| **双模型独立 Session** | ✅ | ❌ | ⚠️ fork context |
| **Gateway 多平台** | ❌ | ✅ 15+ | ⚠️ 仅飞书 |
| **Cron/定时任务** | ❌ | ✅ | ❌ |
| **Checkpoint/Rewind** | ✅ | ❌ | ❌ |
| **Sandbox** | macOS Seatbelt | Docker/SSH | Shell safety |
| **分发方式** | Go binary | pip/brew | cargo install |
| **记忆类型** | 4 种 (user/feedback/project/reference) | 多 provider (SQLite/Mem0/…) | 单一 timeline 文件 |
| **Skills 自建** | ✅ install_skill | ✅ (写入 ~/.hermes/skills/) | ❌ Agent 不能写 |
| **社区** | 持续变化 | 持续变化 | 持续变化 |

---

## 4. Hermes 的独有优势（Reasonix 和 CodeWhale 都没有的）

对比之后，有几个 Hermes 独有的能力值得强调：

1. **Memory 自进化** — Hermes 的 Memory 不只是"存下来下次读"，而是 SQLite + FTS5 的持久化系统，加上 `skill self-evolution`——成功的操作模式自动结晶为 Skills
2. **Gateway 多平台** — 15+ 平台统一入口，Reasonix 和 CodeWhale 都在终端里
3. **Cronjob** — 定时任务的 Agent 推理能力，另外两个都是手动交互
4. **Plugin 生态** — Memory providers（Honcho/Mem0/Supermemory…）、Model providers、Image gen、Kanban 等

---

## 5. 可续写的 LLM+Harness=Agent 深度文章

基于对 Reasonix 的源码分析，我识别出以下可续写的新创新点：

### 可直接写的新文章

**I-13: Byte-Stable Prefix as Architecture Constraint**
> 不是"缓存优化"——是整个 Agent 的架构都以 Prefix Cache 命中率为中心。System prompt 启动后冻结，mid-session 变化全部 ride the turn tail。这跟 I-04 "约束不进压缩区"形成对话——I-04 讲物理隔离，I-13 讲全架构约束。

**I-14: Reasoning Content Stripping — Agent Should Know What NOT to Send**
> DeepSeek 把 re-sent reasoning 当普通 input 计费（每轮 ~500 tokens 纯浪费）。Reasonix 显式 strip。推广：Agent 应该知道哪些内容是"display-only, never re-upload"。

**I-15: Two-Model Collaboration Without Cache Collapse**
> 双模型协作的经典方案是轮流切换模型——但这会炸掉 Prefix Cache。Reasonix 的方案：planner + executor 各占一个独立 Session，永不相交。这是 LLM+Harness 系列中"分离关注点"主题的自然延伸。

**I-16: Memory by Scope — Project vs User vs Auto-Memory**
> Reasonix 的 Memory 层次：REASONIX.md（项目共享）→ REASONIX.local.md（个人不上传）→ user-global → auto-memory store（按类型分类: user/feedback/project/reference）。对比 Hermes 的 SQLite-based Memory，讨论不同粒度选择对 Cache hit 的影响。

### 可写的对比/分析文章

**Product Analysis 2: Three Agent Architectures — Hermes vs Reasonix vs CodeWhale**
> 不是 feature 罗列，是三种架构哲学的碰撞：Hermes（OS 级全栈 Agent 平台）、Reasonix（Cache-first 单二进制）、CodeWhale（DeepSeek 社区终端 Agent + 消息桥接）。每种选择背后的 tradeoff。

**DeepSeek Agent 生态全景**
> DeepSeek 在 Agent 生态中的独特位置——它不是模型最好，但 Prefix Cache 机制让它成为"最经济的长时间开发 Agent 后端"。分析 DeepSeek API 的价格结构如何催生了 Reasonix 这类架构。

---

## 6. 附录：源码引用索引

| 优化点 | 源文件 | 关键行号 |
|--------|--------|---------|
| Cache-Stable System Prompt | `internal/boot/boot.go` | L100-124 |
| Compose (turn tail injection) | `internal/control/input.go` | L18-52 |
| Reasoning Content Stripping | `internal/provider/openai/openai.go` | L171-184 |
| Dedicated Cache Pricing | `internal/provider/provider.go` | L94-99 |
| Cache Metric Normalization | `internal/provider/openai/openai.go` | L311-321 |
| Memory Base-First Protocol | `internal/memory/memory.go` | L148-152 |
| Skills Index/Body Separation | `internal/skill/index.go` | L9 |
| Two-Model Separate Sessions | `internal/agent/coordinator.go` | L25-27 |
| Compaction as Cache Reset | `docs/SPEC.md` | L177-197 |
| Plan Mode Zero-Cache Toggle | `internal/agent/agent.go` | L127-130 |
| E2E Cache Stability Test | `internal/agent/cachehit_e2e_test.go` | L68, L173 |
| REASONIX.md (self-describing) | `REASONIX.md` | L3, L14-16 |
