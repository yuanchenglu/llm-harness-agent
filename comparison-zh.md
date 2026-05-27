# 8 款 Agent 产品深度对比

> 不是 benchmark，不是功能清单——是一个 builder 把每款产品用到极致之后的理解。

---

## 一句话总结

| 产品 | 一句话 |
|------|--------|
| **Hermes** | 系统性最强的 Agent——Memory + Skills + Cron + Gateway 四件套 |
| **Claude Code** | 长任务之王——上下文压缩没人打得过，但生态封闭 |
| **OpenCode** | 最灵活的调度——插件生态最开放，但长任务稳定性不行 |
| **Codex** | OpenAI 亲儿子——原生工具链完整，bridge 模式是国产模型的救命稻草 |
| **OpenClaw** | 弱 Memory 反而是优势——清零式创新的最佳载体 |
| **Cursor** | 最好的 AI 编辑器——但只是编辑器，不是 Agent |
| **Coze** | 最好的 Workflow 平台——但不是 Agent，没有自主 Planning |
| **pi agent** | Session Tree 是革命性的——但没有 Memory/Cron，不是完整产品 |
| **CodeWhale** | 开源项目（DeepSeek-TUI）——我在上面实测了 DeepSeek KV Cache 在 Agent 场景的优势 |

---

## 逐款深度分析

### Hermes Agent

**我把它当什么用**：CEO + CTO，管理 3 个研发小组 + 1 个市场运营组。多期参与火山方舟 Hermes Agent 内部众测。

**核心优势**：

1. **Memory（三层体系）**
   - SQLite 持久化：跨 session 记住用户偏好、项目结构、关键决策
   - Skills 系统：成功经验自动沉淀为 Skill，下次直接加载
   - Session 上下文：当前对话内的短期记忆
   
   这是所有其他 Agent 都不具备的。Claude Code 和 OpenCode 每次对话都从零开始。

2. **Skills 自进化**
   完成一个复杂任务后，Agent 可以提议「把刚才的做法保存为 Skill」。下次遇到类似场景，Skill 自动加载，不需要重复消耗推理 Token。这是 Token 节省金字塔的第一层。

3. **Cronjob**
   为数不多支持定时任务的 Agent。我的「每日对话总结」和「群聊记录总结」就是两个 cronjob，每天自动运行。OpenClaw 虽有调度能力，但 Hermes 的 cron 是与 Agent 推理管线深度集成的。

4. **Gateway 多平台桥接**
   同一个 Agent 可以通过飞书、微信、Discord 等平台交互。这意味着我的 Agent 矩阵不只是「命令行工具」，是可以随时通过手机飞书发指令的「随身研发团队」。

**核心短板**：

1. **Plan 是扁平结构**
   PlanStep 只有 `text` + `status`，没有 `parent_id`、`dependency_ids`、`association_strength`。改第 3 步需求，4-7 步不会自动级联修正。

2. **跨 session 记忆连续性有瓶颈**
   虽然 Memory 是 SQLite 持久化的，但实际使用中，跨 session 的记忆恢复质量不稳定。越长的 session 间隙，记忆恢复越差。

3. **Skill 自进化只有正向学习**
   Hermes 的 Skill 是「成功→固化」的正向学习闭环。但缺少「失败→自查→固化」的负向纠偏闭还。也就是说，Agent 会记住「怎么做是对的」，不会从「做错了」中学习。

**我的对策**：
- 收敛型任务（研发调度、Bug 修复、代码审查）→ Hermes，利用 Memory 的持久性
- 每一次重开 session 时注入关键上下文（项目结构、当前分支、进行中的任务）

---

### Claude Code

**我把它当什么用**：二组研发核心，负责长任务和复杂重构

**核心优势**：

1. **上下文压缩——业界最强，没有之一**
   Claude Code 的 compaction 系统在长对话稳定性上远超其他产品。分段摘要 + split turn 处理 + 累计文件追踪——这三层压缩方案让它在 30+ 轮的对话中依然能保持准确。

   对比 Hermes 的简单压缩，Claude Code 在保持语义完整性上超过一个量级。

2. **长任务稳定性**
   这是 Claude Code 最让我放心的。我敢交给它一个需要 2-3 小时持续执行的任务（重构跨 10 个文件的功能），不用担心中途中上下文腐烂导致跑偏。

**核心短板**：

1. **不支持多模型编排**
   只能用 Claude 系列模型。DeepSeek V4 上了之后，Claude Code 的「只能用 Claude」变成了硬伤。KV Cache 成本优势完全用不上。

2. **Plugin 系统封闭**
   Superpowers（社区的「多 Agent 编排插件」）功能强大，但架构封闭。你只能在它定义的框架内操作，不能自己扩展。

3. **没有 Memory**
   每次对话从零开始。你在上一轮教它的项目约定、文件结构、个人偏好，全清零。

4. **OAuth 授权需要自己补**
   Claude Code 的 GitHub 集成需要 OAuth，但它的授权流程不完整。我是自己补上的。

**我的对策**：
- 需要持续上下文的任务给 Claude Code（它有最好的压缩）
- 需要跨 session 记忆的任务给 Hermes（它有 Memory）
- 写完代码后切到 Hermes 做审查（用 Skills 做最后的合规检查）

---

### OpenCode

**我把它当什么用**：一组研发核心，日均重度使用

**核心优势**：

1. **工具调度最灵活**
   OpenCode 的 tool call 机制是所有 Agent 里最灵活的。它支持自定义 tool、自定义 agent role、自定义审查规则。比 Claude Code 的封闭工具链好一个量级。

2. **OMO（Oh My OpenAgent）插件**
   59K+ Stars 的社区驱动插件。7+1 意图分类（重构/新建/中等/协作/架构/调研/简单 + Spec-Driven）是业界最完整的意图→策略自动切换体系。

3. **OpenSPEC 的文档驱动优于 Superpowers**
   OpenSPEC 的 `propose → apply → archive` 工作流让需求文档化和执行追踪变得非常清晰。

**核心短板**：

1. **缺乏 DeepSeek KV Cache 原生优化**
   OpenCode 的上下文管理是为 GPT/Claude 设计的（Token 贵 → 激进压缩）。DeepSeek 的 KV Cache 成本优势被浪费了。

2. **审查机制不随上下文状态调整**
   OMO 的 Momus 审查 Agent 是「80% 清晰就批准」的固定策略。上下文膨胀时审查质量急剧下降，但它不会自动切换模式。

3. **多模型编排仍需手工配置**
   虽然有 model routing，但切换模型需要手动改配置，不能根据任务类型自动选择最优模型。

**我的对策**：
- 一组走 OpenCode + OMO，利用 OMO 的意图分类做任务分派
- 二组走 Claude Code，处理需要超长上下文的复杂重构
- 两组互为备份——OpenCode 出问题了切 Claude Code，反过来也一样

---

### Codex（OpenAI）

**我把它当什么用**：三组研发，走 bridge 接国产模型

**核心优势**：

1. **OpenAI 原生工具链**
   与 GPT 系列模型深度集成。如果只用 OpenAI，Codex 的原生体验最好。

2. **Bridge 模式支持国产模型**
   通过 bridge 可以接入 GLM、DeepSeek 等国产模型。虽然不是原生支持，但至少能跑起来。

**核心短板**：

1. **对非 OpenAI 模型支持弱**
   走 bridge 后稳定性明显下降。tool call 准确率、上下文管理质量都不如原生 OpenAI。

2. **工具链生态仍在早期**
   相比 OpenCode 的 OMO（59K Stars）和 Claude Code 的 Superpowers（34K Stars），Codex 的插件生态还很不成熟。

**我的对策**：
- 三组是「实验组」——测试国产模型在 Agent 场景下的表现
- 主力任务不走三组，只走实验性和低风险任务

---

### OpenClaw

**我把它当什么用**：CMO，负责市场运营和内容创作

**核心优势**：

**弱 Memory 反而是优势**。这是我刻意利用的一个特性。

Hermes 的 Memory 越来越懂我，但也越来越「像我」——它给出的创意建议被我的历史偏好局限了。OpenClaw 没有强 Memory，每次对话都是近乎「清零」的状态——这恰恰是创意的理想环境。不被历史偏好束缚，能做真正的新方向探索。

同时 OpenClaw 作为纯调度器 + 消息中台表现出色——它可以把消息分发到不同平台、触发不同的工作流。

**核心短板**：

1. **长任务基本不可用**
   上下文管理是 OpenClaw 最弱的环节。没有 Claude Code 级别的自动压缩机制，超过 15 轮的对话基本跑偏。

**我的对策**：
- 发散型任务（市场创意、内容策划）→ OpenClaw，利用清零式创新的优势
- 收敛型任务（研发调度）→ Hermes，利用 Memory 的持久性
- OpenClaw 只做创意提案，不执行——执行全走 Hermes 的 Kanban Worker

---

### Cursor

**我把它当什么用**：早期 AI 编程入口，已迁移到 Agent 工作流

**核心优势**：

**Tab 补全精准度最高**。在代码编辑场景下，Cursor 的内联补全体验是所有产品里最好的。它对上下文的感知粒度最细（基于编辑位置的局部上下文，而非对话窗口）。

**核心短板**：

**没有 Agent 级别的自主决策**。Cursor 是一个「AI 辅助编辑器」，不是「Agent」。它能帮你写下一行代码，但不能帮你拆解一个需求、分配子任务、审查执行结果。

从「AI 辅助」到「Agent 自主」的跃迁，Cursor 做不到。这个跃迁触发了我的 Harness 思考——当 Tab 补全已经足够好，下一个需要解决的问题不是「让补全更准」，而是「让补全变成规划」。

**我的对策**：
- 已经完全从 Cursor 迁移到 Hermes/OpenCode/ClaudeCode 的 Agent 矩阵
- Cursor 的思路保留——在 Agent 方案中，也采用了局部上下文感知的设计理念

---

### Coze（扣子）

**我把它当什么用**：2024 年初即重度使用，搭建 100+ 工作流

**核心优势**：

1. **Workflow 编排 + 插件生态**
   可视化的流程编排是 Coze 最强的地方。对于确定的、可模板化的任务（网页爬取→数据处理→格式化输出），Coze 的 Workflow 比 Agent 更适合。

2. **上手门槛低**
   不需要写代码，拖拽就能建 workflow。这是 AI 应用平民化的重要方向。

**核心短板**：

**Coze 不是 Agent**。这是本质区别。

Workflow 是预定义的流水线——如果 A 则 B，如果 C 则 D。Agent 是自主决策的——根据当前状态动态规划下一步做什么。

Coze 没有自主 Planning：它不会说「这个任务比我预想的复杂，我需要拆成更多步骤」。它没有 Error Recovery：一个步骤失败了，整个 workflow 停住。它没有上下文感知：每一步只知道自己的输入输出，不知道前面的步骤「为什么」做了这个决策。

**我从 Coze 学到的**：Workflow 和 Agent 的本质区别——不是「能力的量级差异」，是「决策权的差异」。Workflow 每一步是预设的，Agent 每一步是决策的。

---

### pi agent

**我把它当什么用**：学习对象——研究它的架构设计，不用于生产

**核心优势**：

1. **Session Tree（in-file branching）——革命性设计**
   在同一个 JSONL 文件里用 `id` + `parentId` 建树结构。可以回溯到任意历史点继续对话。这是 Hermes/ClaudeCode/OpenCode/Codex 都没有的能力。想象 Git 的 branch 概念应用到对话上——你可以在第 5 轮「分叉」出两条不同的对话路线，两条互相独立但都保留了完整的上下文。

2. **Compaction 系统——最精细的分段摘要**
   不是一次性压缩整个上下文，而是分主题、分时间段压缩，加上累计文件追踪。在保持语义完整性上，pi 的 compaction 是所有 Agent 里最精细的。

3. **Extension API——业界最丰富**
   2596 行文档，从工具注册到 TUI 组件渲染到事件拦截到状态持久化。这是「极简内核 + 插件做一切」哲学的工程实现。

4. **代码质量极高**
   617 个 .ts 文件，零 `any` 类型。Armin Ronacher（Flask + Jinja2 的创造者）的作品，工程级的艺术品。

**核心短板**：

1. **没有 Memory**——跨 session 从零开始
2. **没有 Cron**——不能做定时任务
3. **没有子代理**——不能 delegate_task
4. **没有多平台接入**——只能在终端用

pi 是一个「概念验证级」的产品——它在对话管理和可扩展性上做到极致，但不是一个「完整产品」。它需要你自己搭 Memory、自己写 Cron、自己做子代理编排。

**对我的启示**：Session Tree 是 Hermes 最值得学习的设计。如果 Hermes 能在 session 内支持「话题分支」，会让长对话的管理能力提升一个量级。

---

### CodeWhale（开源项目，DeepSeek 官方）

**我把它当什么用**：研究 DeepSeek 模型在 Agent 场景下实际表现的实验平台

**背景**：CodeWhale 是 DeepSeek 官方的开源 Coding Agent（原名 DeepSeek-TUI）。我没有参与开发，但深度使用它来验证 DeepSeek 模型在 Agent 架构下的真实表现——因为它是直接跑在 DeepSeek API 上的，不像 OpenCode/ClaudeCode 那样受海外模型假设影响。

**核心发现**：

1. **DeepSeek KV Cache 长 session 稳定性验证**
   我用 CodeWhale 跑多 Agent 编排时发现：DeepSeek 在长上下文下的稳定性超过 Claude 和 GPT。这不是模型「更聪明」，是 KV Cache 更便宜 → 不需要激进压缩 → 语义保持更好。

2. **KV Cache 前缀注入的可行性验证**
   我在 CodeWhale 上做了硬约束前缀注入的原型验证。结果：约束注入前缀后，15 轮对话后约束保持率 > 95%（对比不注入的 ~40%）。这验证了 I-06 创新点的可行性。

3. **现有 Harness 工具的共性问题**
   OpenCode、ClaudeCode、Cursor——这些 Harness 工具都是为海外模型设计的。它们假设 Token 很贵，所以激进压缩。它们没有利用 DeepSeek 的 KV Cache 优势。这就是为什么需要一个原生的、为 DeepSeek 优化的 Harness。

---

## 我的 Agent 矩阵分工

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  CEO (Hermes) — 调度中枢                                     │
│  ├── 任务拆解 → Kanban                                      │
│  ├── 子代理分配 → delegate_task                             │
│  ├── 定时自动化 → cronjob                                    │
│  └── 持久记忆 → Memory (SQLite)                              │
│                                                             │
│  一组 (OpenCode + OMO) — 核心研发                            │
│  ├── Plugin 开发                                              │
│  ├── 代码审查 (Momus)                                        │
│  └── Spec 文档 (OpenSPEC)                                    │
│                                                             │
│  二组 (Claude Code) — 复杂重构                               │
│  ├── 跨文件大重构                                             │
│  ├── 长上下文任务（30+ 轮）                                    │
│  └── 上下文压缩后审查                                          │
│                                                             │
│  三组 (CodeX + bridge) — 国产模型实验                         │
│  ├── GLM/DeepSeek bridge 测试                                │
│  └── 低风险任务验证                                           │
│                                                             │
│  CMO (OpenClaw) — 市场运营                                   │
│  ├── 市场创意（清零式创新）                                    │
│  └── 内容策划                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 两种 Agent 哲学

这两个哲学的对比，比任何单一产品的对比都更有价值：

```
pi 哲学（Linux 内核）             Hermes 哲学（macOS）
─────────────────────────        ─────────────────────────
极简核心 + 插件做一切             自包含全家桶
4 个内置工具                     20+ 内置工具
Extension API 做扩展             Skills 做扩展
无 Memory / Cron / Gateway       Memory + Cron + Gateway
Session Tree 分支对话            线性 Session
适合：愿意自己搭建工具链的人       适合：需要开箱即用的人
```

**没有对错**。pi 的 Extension API 深度值得 Hermes 学习，Hermes 的 Memory + Cron 组合是 pi 不具备的护城河。最好的 Agent 平台可能是在两者之间找到一个平衡——内核稳定但外围可编程。

---

## 选型建议（如果让我重新开始）

| 你的场景 | 推荐 | 为什么 |
|---------|------|--------|
| 需要跨 session 记忆 | Hermes | 少数有 SQLite Memory 的 |
| 需要定时自动化 | Hermes | 少数有 cronjob 且与 Agent 深度集成的 |
| 需要多平台接入 | Hermes | Gateway 支持飞书/微信/Discord |
| 需要超长对话稳定性 | Claude Code | 上下文压缩最强 |
| 需要灵活的工具调度 | OpenCode | 工具链最开放 |
| 只用 OpenAI 模型 | Codex | 原生集成最好 |
| 做创意/市场工作 | OpenClaw | 弱 Memory = 清零创新 |
| 研究 Agent 架构 | pi agent | Session Tree 值得学习 |
| 做固定模板任务 | Coze | Workflow 比 Agent 更合适 |

---

*「Coze 不是 Agent」——这是我 100+ 个工作流之后的核心结论。Workflow 和 Agent 的区别不是能力大小，是决策权归属。*
