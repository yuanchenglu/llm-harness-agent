# LLM + Harness = Agent：Agent 操作系统的第一性原理框架

> **也是论文草稿，也是一个 builder 把手弄脏之后的理解。**
> 5000+ 小时 · 10+ 款 Agent 产品 · 5 台机器上的 Agent 矩阵 · 多期火山方舟 Hermes 众测

---

> **摘要**：当前 AI Agent 的主流思路是「等下一代模型」——更大的 Context Window、更强的推理、更好的指令跟随。本文论证这个思路走不通：Transformer 的软注意力机制决定了上下文越长，每条指令的注意力权重越低——这是物理硬约束，不是模型能力问题。真正的突破口在 Harness：一套运行在模型之外的操作系统，管理系统提示词的持久性（Memory）、自动化任务的成功经验（Skills）、长时间运行的规划与调度（Kanban + Cron）、以及多平台多 Agent 的协作（Gateway + delegate）。本文提出 Agent 操作系统的四层架构，将 12 个在实践中验证过的设计模式归入 4 条第一性原理推导出的设计原则，并给出 5 机 Agent 矩阵 + 8 款产品实测的实证基础。核心论点：模型改进是线性的，Harness 改进是指数的。

---

## 1. 导论：为什么 Harness 比模型更重要

### 1.1 一个反直觉的发现

2025 年，我在 5 台机器上跑了一个 Agent 矩阵——3 个研发小组（OpenCode、ClaudeCode、CodeX）+ 1 个市场运营组（OpenClaw），由 Hermes 做 CEO 统一调度。所有 Agent 都接入同一个底层模型（DeepSeek V4）。

同一个模型，在不同的 Harness 上的表现天差地别。

- **Claude Code**：长任务稳定性无人能敌，但生态封闭，只认自家模型
- **OpenCode**：插件生态最开放，但长任务跑到第 8 轮就开始「忘事」
- **Codex**：OpenAI 亲儿子，工具链完整，但 bridge 模式接入国产模型时上下文管理是短板
- **Hermes**：Memory（SQLite）+ Skills（自进化）+ Cron（定时任务）+ Gateway（多平台）四件套，让它从「编程工具」进化为 Agent 操作系统

同一个 DeepSeek V4，ClaudeCode 上能跑 30 轮不丢逻辑，OpenCode 上跑到 15 轮就开始重复造轮子——**模型没变，变的是 Harness 对上下文的调度策略**。

### 1.2 问题的根因：注意力的物理学

Transformer 的自注意力机制是 O(n²) 的计算。当序列长度 L 从 2K 增长到 128K，System Prompt 中任意一条指令的注意力权重被稀释约 64 倍。1M Context Window 只是把这个稀释从第 15 轮推迟到第 50 轮——问题不变，只是来得更晚。

形式化：设有 n 条行为约束 C = {c₁, c₂, ..., cₙ}，对话 t 轮后序列长度 L(t)。注意力权重 αᵢ(t) ∝ 1/L(t)。当 L(t) → ∞，αᵢ(t) → 0。**这是一个单调递减函数，没有拐点。**

这意味着什么？意味着「让模型更强」这条路的边际收益是递减的。GPT-5 的指令跟随能力比 GPT-4 好 20%——但如果你的 Agent 需要跑 100 轮对话，这 20% 在第 30 轮就会被注意力稀释抵消掉。

**真正的问题不是「模型不够聪明」，而是「模型在长对话中必然遗忘」。这不是 bug，是 Transformer 的物理特性。**

### 1.3 Harness 的定义

Harness 是运行在 LLM 之外的一套系统软件，管理：

1. **什么进入上下文窗口**（Memory 选择、Skill 注入、上下文压缩策略）
2. **什么在上下文之外持久化**（Memory SQLite、Skill 文件、Plan 状态）
3. **什么时候执行什么任务**（Cron 调度、Kanban 任务分解、子 Agent 编排）
4. **如何与外部世界交互**（Gateway 多平台桥接、工具调用、浏览器控制）

一句话：**模型是 CPU，Harness 是进程调度器 + 文件系统 + 内存管理 + 网络栈。没有操作系统的 CPU 只是一块硅片。**

---

## 2. Harness 的四层架构

一个完整的 Agent 操作系统需要四层能力。每一层解决一个根本问题——这些问题模型本身解决不了。

```
┌─────────────────────────────────────────────────────────┐
│                     Gateway 层                           │
│   飞书 / 微信 / Discord / X / Telegram / 浏览器         │
│   「Agent 和世界的接口」                                 │
├─────────────────────────────────────────────────────────┤
│                     Scheduling 层                        │
│   Cron 定时调度 / Kanban 任务分解 / delegate 子代理      │
│   「谁、什么时候、做什么」                               │
├─────────────────────────────────────────────────────────┤
│                     Skills 层                            │
│   成功经验固化 / 故障模式库 / 自进化闭环                  │
│   「学到的经验，下次别重复踩坑」                         │
├─────────────────────────────────────────────────────────┤
│                     Memory 层                            │
│   用户偏好 / 环境信息 / 决策历史 / 项目约定              │
│   「跨 session 的知识，不该每次重新发现」                │
└─────────────────────────────────────────────────────────┘
```

### 2.1 Memory 层：跨 Session 的持久化

**核心问题**：每次新对话，Agent 从零开始。你不知道用户用什么操作系统、偏好什么语言、项目的目录结构——除非用户每次都重新告诉你。

**解决方案**：Memory 是一个结构化 SQLite 数据库，存用户偏好、环境事实、项目约定。每个 Session 开始时自动注入——不需要用户重复。

**关键设计决策**：Memory 不是日志。不存任务进度、不存"今天修了 bug X"、不存临时 TODO。原因是：7 天后这些信息全是噪音。Memory 只存**稳定事实**——那些 7 天后仍然为真的信息。

这个设计原则对应创新点 [I-12：Memory 粒度控制](innovations/12-memory-granularity-zh.md)——收敛任务（需要稳定上下文）要强 Memory，发散任务（探索性对话）要弱 Memory。

### 2.2 Skills 层：成功经验的固化与自进化

**核心问题**：Agent 完成一个复杂任务后，下次遇到类似任务，又要从头推理一遍。同样的错误可能再犯一次。

**解决方案**：Skills 是结构化的操作手册——不是自然语言提示，是可执行的检查步骤、命令模板、配置示例。Agent 完成任务后，自动提议将成功做法保存为 Skill。下次触发同类任务，Skill 直接注入上下文——零推理 Token。

这是创新点 [I-09：Skills 自进化闭环](innovations/09-skills-self-evolution-zh.md) 的核心——Agent 不是每次都重新发明轮子，而是把成功经验晶体化。

与之互补的是 [I-01：Agent 免疫系统](innovations/01-agent-immune-system-zh.md)——正向学习（成功→Skill）Hermes 已做，负向纠偏（遗忘→自查→Skill）是我提出的新机制：当系统检测到某个 Prompt 约束被违反时，自动将约束固化为 Skill，外挂到执行流，下次不再依赖模型的记忆。

### 2.3 Scheduling 层：从一次性执行到自主运行

**核心问题**：LLM 是「一问一答」的——你问，它答。但真正的 Agent 需要在没有人发消息的时候自己干活：每天早上汇总新闻、每隔 30 分钟检查服务器状态、每月 1 号出上月报告。

**解决方案**：Cron 调度 + Kanban 任务分解 + delegate 子代理编排。

- **Cron**：定时触发 Agent 执行预定义任务。支持复杂调度（cron 表达式）、链式任务（任务 A 完成 → 自动触发任务 B）、多平台自动分发（完成后推送到飞书/Discord/Telegram）
- **Kanban**：复杂任务分解为子任务 → 按依赖关系排序 → 逐个执行 → 完成后级联修正（[I-06：OKR PlanStep + 级联修正](innovations/06-okr-planstep-cascade-zh.md)）
- **delegate_task**：spawn 独立子 Agent 处理子任务，主 Agent 只接收摘要——不污染主上下文窗口

这一层的本质是**把 Agent 从「被动应答」变成「主动执行」**。一个不能自己安排时间的 Agent，只是一个聊天机器人。

### 2.4 Gateway 层：与世界交互

**核心问题**：Agent 跑在服务器上，但用户可能在飞书、微信、Discord、邮件——Agent 需要能在所有平台上收发消息、管理文件、控制浏览器，像一个真正的团队成员。

**解决方案**：Gateway 统一桥接多平台——同一个 Agent 从飞书接到需求，完成后的产出通过 Discord 发给团队，同时在 GitHub 上开 Issue。平台差异对 Agent 透明。

这是创新点 [I-10：7+1 意图→策略路由](innovations/10-intent-routing-zh.md) 的基础设施——Agent 识别任务意图后自动切换执行策略。没有 Gateway，Agent 只能活在终端里。

---

## 3. 十二个设计模式：从第一性原理到工程实现

本章将 12 个在实践中验证过的设计模式归入 4 个根本问题。每个模式不是独立的想法——它们是同一个原则在不同维度上的展开：**把不可丢失的和可以压缩的分开**。

### 3.1 上下文管理（解决注意力稀释）

Transformer 的注意力稀释是物理硬约束。不能阻止它——只能管理它。让最重要的信息在每一步推理时都拥有最高的注意力权重。

| # | 设计模式 | 核心方法 | 解决的问题 |
|---|---------|---------|-----------|
| I-03 | [注意力预算管理](innovations/03-attention-budget-zh.md) | 把上下文视为有限预算，按任务类型动态分配各区块配额 | Agent 变傻不是模型问题，是 Harness 没管好注意力分配 |
| I-04 | [KV Cache 硬约束前缀注入](innovations/04-kv-cache-prefix-zh.md) | 不可丢失的约束放在不可压缩的前缀区，不是放在可被压缩的正文里 | 约束不丢不是靠压缩聪明，是靠约束根本不在压缩范围里 |
| I-05 | [文档 KV Cache 优化结构](innovations/05-document-kv-cache-zh.md) | 把 Agent 内部的 KV Cache 优化原理应用到文档写作规范——元层面的自指 | 稳定内容（定义、结构）在前，变化内容（进度、日期）在后 |
| I-07 | [KV Cache 驱动的审查深度切换](innovations/07-review-switching-zh.md) | 审查深度 = f(KV Cache 占用率, Plan 复杂度)，不是固定阈值 | 上下文紧张时不能做深度审查，否则审查本身就是干扰 |
| I-11 | [Checkpoint 多轮审查](innovations/11-checkpoint-review-zh.md) | 第二轮审查的上下文比第一轮更小——不是越来越大 | 每轮审查只看上一轮的决策摘要，不看全部历史 |

**统一逻辑**：这 5 个模式都遵循同一条原则——**信息分两层：不可丢失的（硬约束、核心决策）和可以压缩的（执行细节、对话噪音）。硬约束放在不可压缩区，审查只看摘要。**

### 3.2 稳定与纠偏（解决长期运行中的漂移）

Agent 跑得越久，越偏离初始目标。这不是 Agent「变心」了——是对话的历史包袱让每一步决策都基于越来越模糊的上下文。

| # | 设计模式 | 核心方法 | 解决的问题 |
|---|---------|---------|-----------|
| I-01 | [Agent 免疫系统](innovations/01-agent-immune-system-zh.md) | 独立审查 Agent 检查约束遵守情况 → 违反的约束自动固化为 Skill | Prompt 遗忘是必然的，让系统自己发现并修复 |
| I-06 | [OKR PlanStep + 级联修正](innovations/06-okr-planstep-cascade-zh.md) | Plan 从扁平清单升级为有向依赖图，改一步自动级联更新下游 | 执行到第 7 步时发现第 2 步错了——不用从第 3 步开始重做 |
| I-08 | [两层范围蔓延分治](innovations/08-scope-creep-zh.md) | 需求蔓延和技术蔓延是两种病，用不同的药 | Agent 做任务做着做着越做越大——区分是用户加的锅还是自己卷的 |

**统一逻辑**：长期运行的 Agent 需要「纠偏闭环」——不是靠模型自己「记性好」，是靠 Harness 在运行时检查 + 定向干预。

### 3.3 知识进化（解决 Agent 不会自己变强的问题）

传统 Agent 每次任务独立运行。昨天的成功经验不会自动应用到今天。用户必须记住每一个坑，然后手动告诉 Agent。

| # | 设计模式 | 核心方法 | 解决的问题 |
|---|---------|---------|-----------|
| I-09 | [Skills 自进化](innovations/09-skills-self-evolution-zh.md) | 完成复杂任务→自动提议保存为 Skill→下次零推理 Token | Agent 不是每次都重新发明轮子 |
| I-12 | [Memory 粒度控制](innovations/12-memory-granularity-zh.md) | Memory 不是越强越好——收敛任务要强记忆，发散任务要弱记忆 | 不该记的记了 = 噪音污染；该记的没记 = 重新踩坑 |

**统一逻辑**：Agent 的知识管理有两个维度——**持久化什么**（Memory 层的粒度决策）和**固化什么**（Skills 层的模式提取）。两者共享同一条判断标准：这个信息 7 天后还会为真吗？

### 3.4 人机共生（解决 Agent 与用户的关系）

传统 Agent 是「用户发指令 → Agent 执行」的单向流。但真正的团队成员不是这样工作的——团队是双向的：你推动我，我也推动你。

| # | 设计模式 | 核心方法 | 解决的问题 |
|---|---------|---------|-----------|
| I-02 | [大脑驱动小脑](innovations/02-bidirectional-agent-zh.md) | 从「Harness→LLM」单向流变为「LLM⇄Harness」双向主动流 | LLM 不仅是执行者——它可以主动调用 Harness 能力、发起 Skill 保存、调整 Cron 策略 |
| I-10 | [7+1 意图→策略路由](innovations/10-intent-routing-zh.md) | 识别用户消息的意图类型→自动匹配采访深度、审查标准、执行模式 | 用户说「帮我看看这段代码」和「为什么这段代码这么慢」——应该用完全不同的策略 |

**统一逻辑**：Agent 不应该只是「响应式」的，应该是「共生式」的。它能感知任务类型、主动推动流程、在需要时拉用户进来——不是等用户下命令。

---

## 4. 实证基础

### 4.1 5 机 Agent 矩阵的实战验证

我的 Agent 矩阵是实打实在跑的，不是纸上架构：

| 机器 | 角色 | 运行的 Agent | 模型 |
|------|------|-------------|------|
| 机器 1 | CEO + CTO | Hermes（中枢调度） | DeepSeek V4 Pro |
| 机器 2 | 研发一组 | OpenCode + OpenSpec + OMO | DeepSeek V4 Pro |
| 机器 3 | 研发二组 | ClaudeCode + SuperPowers + OMC | Claude Sonnet 4 |
| 机器 4 | 研发三组 | CodeX + OMX（走 bridge） | GLM 5.1 |
| 机器 5 | 市场运营 | OpenClaw | DeepSeek V4 Flash |

矩阵的运转逻辑：Hermes 作为中枢接收任务 → 分解为子任务 → 通过 delegate_task 分配给各小组 → 各小组用各自最优的 Harness + 模型组合执行 → 结果返回 Hermes 汇总。

关键发现：
- **同一模型在不同 Harness 上的表现差异，远超不同模型在同一 Harness 上的差异**。DeepSeek V4 在 Hermes 上能记住 3 天前的决策并应用到新任务中（Memory 层的作用），在 OpenCode 上每次新 Session 都要重新对齐。
- **Harness 的能力决定 Agent 的「自主性上限」**：没有 Cron 的 Agent 不能自主运行——你睡着的时候它也在睡觉。没有 Skills 的 Agent 不会积累经验——昨天踩过的坑今天照样踩。
- **Gateway + Scheduling 的组合，让 Agent 从「程序员工具」变成了「团队成员」**：飞书上发一条需求，Hermes 分解、分配、执行、推送结果——全程不需要开终端。

### 4.2 8 款产品实测对比

详见 [8 款 Agent 产品深度对比](comparison-zh.md)。核心发现：

| 能力维度 | Hermes 独有 | 部分竞品有 | 主流产品缺失 |
|---------|-----------|-----------|------------|
| Memory (跨 Session 持久化) | ✅ SQLite | — | ClaudeCode/OpenCode/Codex/Cursor 均无 |
| Skills 自进化 | ✅ 自动提议保存 | — | 所有平台均无此机制 |
| Cron 定时调度 | ✅ 深度集成 Agent 推理 | OpenClaw 有调度 | 其他平台无 |
| Gateway 多平台 | ✅ 与 Agent 内核一体 | OpenClaw 本身即 Gateway | Cursor/Codex 无多平台能力 |

**注意**：OpenClaw 本质是 Gateway 产品——它的调度和多平台能力是强项。Hermes 的差异化在于：Gateway 不是外挂模块，而是与 Agent 推理管线深度集成的——飞书的 thread context 会直接进入 Memory 层和意图路由。

### 4.3 火山方舟 Hermes 众测经验

多期参与火山方舟 Hermes Agent 内部众测。最重要的发现不是「Hermes 哪里好」，而是「Harness 迭代速度远超模型迭代速度」。

- 模型升级周期：3-6 个月（训练 + 对齐 + 测试）
- Harness 迭代周期：可以按天——今天发现 Memory 粒度太粗导致噪音污染，今晚改配置，明天生效
- **模型的边际改进在不断递减**（Transformer 的物理上限），**Harness 的改进空间几乎没有上限**（每一个交互细节都是优化空间）

---

## 5. 设计原则

从 12 个设计模式中提炼 4 条通用设计原则。这些原则不限于 Hermes——任何 Agent 系统都适用。

### 原则一：分离不可压缩与可压缩

**来源**：I-03, I-04, I-05, I-07, I-11

上下文管理的第一性原则：不要试图让模型记住更多——要减少模型需要记住的东西。把信息分成两层：
- **硬约束层**：行为规范、安全检查、项目约定 → 放在 KV Cache 前缀区，永不被压缩
- **软上下文层**：执行日志、对话细节、临时决策 → 可以被压缩，但压缩策略按任务类型动态调整

在实践中：我的 Hermes 配置中，Memory（用户偏好、环境信息）和 Skills（已验证的操作流程）注入到不可压缩前缀区。执行日志和过往对话放在可压缩区。压缩发生时，硬约束毫发无损。

### 原则二：Agent 必须是主动的，不是被动的

**来源**：I-02, I-06, I-10

传统人机交互是「用户拉取式」——用户发指令，系统执行。Agent 需要是「双向推动式」：
- **系统推用户**：定时汇报、异常告警、进度更新（Cron）
- **Agent 推系统**：自动保存经验（Skills）、自主调整策略（意图路由）、主动发起子任务（delegate）
- **用户推 Agent**：需求、反馈、优先级调整——不变

这叫「大脑驱动小脑」。LLM 不仅是执行者——它是决策者，可以主动调用 Harness 的任何能力。这个转变把 Agent 从「工具」变成了「团队成员」。

### 原则三：记忆的粒度要与任务类型匹配

**来源**：I-09, I-12

Memory 不是越强越好。错误粒度的 Memory 比没有 Memory 更糟：

- **收敛任务**（修复已知 Bug、执行标准运维）→ 强 Memory——依赖稳定的用户偏好和项目约定
- **发散任务**（探索新架构、头脑风暴）→ 弱 Memory——保留太多历史决策会限制探索空间
- **Skills vs Memory**：Skills 存「怎么做」（操作流程——收敛），Memory 存「是什么」（事实和偏好——可以被覆盖）

在实践中：我的 Hermes 做一个 Bug 修复时，Memory 会加载完整的项目结构、用户偏好、代码规范。做新产品架构设计时，Memory 只加载用户的核心原则和偏好——不加载上一次类似项目的历史决策，避免路径依赖。

### 原则四：自进化是终局，不是加分项

**来源**：I-01, I-09

一个不会自己变强的 Agent 是没有未来的。Agent 的自进化有两个方向：
- **正向**：成功完成复杂任务 → 自动提议保存为 Skill（I-09）
- **负向**：检测到约束被违反 → 自动固化为 Skill，下次不依赖模型记忆（I-01）

两者的组合形成完整的进化闭环：**成功经验被保留，失败模式被免疫**。每个 Skill 的诞生都意味着 0 推理 Token——Agent 变强的速度取决于它积累的 Skill 数量，而 Skill 积累会自动加速。

---

## 6. 展望

### 6.1 Harness 的下一步

**自进化 2.0**：目前的 Skills 自进化还是「人工审核 → 确认保存」的模式。下一步是「自动试用 → 自动评估 → 自动保存」，让 Skill 库像免疫系统一样自主进化——不需要人工介入，遇到新场景自动生成应对模式。

**多 Agent 协作**：当前 Agent 矩阵中，每个 Agent 的工作是独立的——Hermes 分配任务，各小组执行，结果汇总。真正的突破是 Agent 之间的**动态分工**：Agent A 发现自己卡住 → 自动 spawn Agent B 解决问题 → Agent B 的解决方案自动保存为所有 Agent 共享的 Skill。

**Harness-as-a-Service**：Harness 不应该绑定到某一个 Agent 产品。理想的未来是 Harness 层标准化——Memory 协议、Skill 格式、Gateway 接口统一——让任何 LLM 都能接入任何 Harness。就像 TCP/IP 让任何应用都能跑在任何网络上一样。

### 6.2 本文的局限

1. **12 个设计模式没有经过大规模用户验证**——我是一个 builder 在自己的场景里验证的，不是学术实验
2. **Harness 的度量体系还不成熟**——我们没有一个公认的指标来衡量「这个 Harness 比那个好多少」。本文用的是定性判断 + 使用体验，不是量化指标
3. **Gateway 层的多平台能力只在飞书 + Discord + 本地终端上验证过**——微信、Slack、Telegram 的能力是理论上的
4. **自进化 2.0 和 Agent 动态分工仅停留在设计阶段**——没有工程实现

---

## 7. 结论

LLM 的改进是线性的，Harness 的改进是指数的。

不是因为 Harness 比模型更重要——而是因为 Transformer 的注意力机制有物理上限，而 Harness 没有。模型每强一个版本，需要数百万美元的训练成本和 3-6 个月的时间。Harness 每强一个版本，可能只需要一次配置修改，明天就能生效。

**12 个设计模式不是终点，是一个方向**：从「等下一个更好的模型」转向「在当前模型上建设更好的运营系统」。DeepSeek 把引擎造好了，现在轮到我们把底盘造好。

---

## 创新点索引

| # | 文章 | 所属原则 |
|---|------|---------|
| [I-01](innovations/01-agent-immune-system-zh.md) | Agent 免疫系统 | 原则四：自进化 |
| [I-02](innovations/02-bidirectional-agent-zh.md) | 大脑主动驱动小脑 | 原则二：主动性 |
| [I-03](innovations/03-attention-budget-zh.md) | 注意力预算管理 | 原则一：分离不可压缩 |
| [I-04](innovations/04-kv-cache-prefix-zh.md) | KV Cache 硬约束前缀注入 | 原则一：分离不可压缩 |
| [I-05](innovations/05-document-kv-cache-zh.md) | 文档 KV Cache 优化结构 | 原则一：分离不可压缩 |
| [I-06](innovations/06-okr-planstep-cascade-zh.md) | OKR PlanStep + 级联修正 | 原则二：主动性 |
| [I-07](innovations/07-review-switching-zh.md) | KV Cache 驱动审查深度 | 原则一：分离不可压缩 |
| [I-08](innovations/08-scope-creep-zh.md) | 两层范围蔓延分治 | 原则二：主动性 |
| [I-09](innovations/09-skills-self-evolution-zh.md) | Skills 自进化 | 原则四：自进化 |
| [I-10](innovations/10-intent-routing-zh.md) | 7+1 意图→策略路由 | 原则二：主动性 |
| [I-11](innovations/11-checkpoint-review-zh.md) | Checkpoint 多轮审查 | 原则一：分离不可压缩 |
| [I-12](innovations/12-memory-granularity-zh.md) | Memory 粒度控制 | 原则三：粒度匹配 |

---

*本文为「LLM + Harness = Agent」系列的总纲论文。每篇创新点文章是独立的案例研究，本文是统一的理论框架。协议：[CC BY 4.0](LICENSE.md)。*

*下一篇：待定。12 个设计模式的原型（Prototype）验证正在进行中——不是概念验证，是工程实现。*

---

*联系方式：yuanchenglu001@gmail.com · [GitHub](https://github.com/yuanchenglu) · [X](https://x.com/yuanchenglu)*
