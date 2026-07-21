# LLM + Harness = Agent

> 让 AI 模型在真实场景中可靠工作——18 篇深度分析从理论与源码验证两条线回答同一个问题。
>
> 不是学术论文，是一线实践者的工程笔记。

**[English](README_en.md)** · **[简体中文](README.md)**

***

## 这个仓库是干什么的

你打开这个仓库，大概率是因为遇到了这几个问题之一：

- 同一个模型（DeepSeek V4 / GPT-4o...）在不同 Agent 框架里的表现天差地别，不知道问题在哪
- 试了几个 Agent 产品（Claude Code、OpenCode、Cursor...），想知道哪个架构更值得深度绑定
- 听说过 KV Cache、Prefix Cache、Reasoning Effort，想知道怎么用到自己项目里
- 想做自己的 Agent，但不知道从何开始——理论太多、代码不敢抄、论文读不完

**这个仓库就是这些问题的回答。** 它不是一份标准的 README，而是一个持续更新的知识库，记录了过去一年在一线实践中沉淀的理论框架、源码审计结论和未经验证的实验假设。

**核心结论**：模型能力只决定 Agent 的下限，Harness（执行框架）的设计决定上限。同一条 DeepSeek API，经过不同的上下文管理、工具编排、权限控制，吞吐量可以差出 10 倍。这不是猜想，是代码层面能看见的事实。

***

## 谁该看这个

| 如果你的角色是…                           | 建议从哪里读起                                                                                                                                         |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **产品经理 / CEO** — 想理解 Agent 产品的技术差异 | [PRD TechPlan](zh/prd-tech-plan/README.md) → [产品对比](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) |
| **开发者** — 想在自己的项目里用上这些思路           | [核心创新点](README.md#核心创新点) 从 01 开始 → [研究方法与事实校准](zh/theory/research-method.md)                                                                    |
| **研究者** — 关注 Agent 架构的学术脉络         | [论文引用数据库](https://github.com/yuanchenglu/llm-harness-agent/blob/master/references/papers.md) → [理论总纲](zh/theory/theory-guide.md)                |
| **只想快速上手** — 用现成的产品                | → [deepseek\_runtime](https://github.com/7colorai/deepseek_runtime) / [deepseekagent](https://github.com/yuanchenglu/deepseekagent)             |

***

## 快速导航

### 如果你是产品经理 / 决策者

先读这一套，建立对 Agent 产品的全局认知：

| 文档                                                                                                             | 一句话                                                                                       |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [PRD TechPlan](zh/prd-tech-plan/README.md)                                                                     | 当前产品化路线、release gates 和决策记录                                                               |
| [9 款 Agent 产品校准对比](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Hermes / Claude Code / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent / CodeWhale |
| [Blueprint 交接包](zh/blueprint/README.md)                                                                        | 阶段真相、证据链和历史调研入口                                                                           |

### 如果你是开发者

核心创新点从 01 开始按顺序读，每篇独立：

| 编号 | 文章                                                                                | 一句话价值                                     |
| -- | --------------------------------------------------------------------------------- | ----------------------------------------- |
| 01 | [Agent 免疫系统](zh/innovations/01-agent-immune-system.md)                            | Prompt 指令在长任务中会失效，让 Harness 自查自修而非让模型硬记   |
| 02 | [大脑主动驱动小脑](zh/innovations/02-bidirectional-agent.md)                              | 从「Harness→LLM」单向流变为「LLM⇄Harness」双向主动流     |
| 03 | [注意力预算管理](zh/innovations/03-attention-budget.md)                                  | Agent 表现退化不一定是模型问题，也可能是上下文与注意力管理的问题       |
| 04 | [KV Cache 硬约束前缀注入](zh/innovations/04-kv-cache-prefix.md)                          | 把稳定约束与可压缩历史分离，降低约束在压缩中丢失的风险               |
| 05 | [文档 KV Cache 优化结构](zh/innovations/05-document-kv-cache.md)                        | 把 Agent 内部的优化原理应用到文档规范上                   |
| 06 | [OKR 增强型 PlanStep + 级联修正](zh/innovations/06-okr-planstep-cascade.md)              | Plan 从扁平清单升级为有向依赖图，改一步自动级联修正              |
| 07 | [KV Cache 驱动的审查深度切换](zh/innovations/07-review-switching.md)                       | 审查标准是 f(KV Cache, Plan 复杂度) 而非固定阈值        |
| 08 | [两层面范围蔓延的分治策略](zh/innovations/08-scope-creep.md)                                  | 需求蔓延和技术蔓延是两种病，不能用同一种药                     |
| 09 | [Skills 自进化闭环](zh/innovations/09-skills-self-evolution.md)                        | Agent 完成复杂任务→提议沉淀为 Skill→下次减少重复推理         |
| 10 | [7+1 意图→策略自动切换](zh/innovations/10-intent-routing.md)                              | 识别任务意图→自动匹配采访深度/审查标准/执行模式                 |
| 11 | [Checkpoint 快照驱动的多轮审查](zh/innovations/11-checkpoint-review.md)                    | 用独立快照控制审查上下文，而非反复携带完整历史                   |
| 12 | [Memory 粒度控制](zh/innovations/12-memory-granularity.md)                            | 收敛任务要强记忆，发散任务要弱记忆                         |
| 13 | [Byte-Stable Prefix 作为架构约束](zh/innovations/13-byte-stable-prefix-architecture.md) | 不只是缓存 System Prompt——让整个 Agent 以 Cache 优先 |
| 14 | [Reasoning Content 回传陷阱](zh/innovations/14-reasoning-content-stripping.md)        | 每个 Token 都要证明自己的存在价值                      |
| 15 | [DSML 工具调用格式优化](zh/innovations/15-dsml-tool-call-optimization.md)                 | DeepSeek V4 独有的 XML 标记格式优化                |
| 16 | [Quick Instruction 路由](zh/innovations/16-quick-instruction-routing.md)            | V4 内置的 6 种特殊 token 路由                     |
| 17 | [推理强度控制](zh/innovations/17-reasoning-effort-control.md)                           | reasoning\_effort 三级控制策略                  |
| 18 | [最新提醒注入](zh/innovations/18-latest-reminder-injection.md)                          | 注入时效信息到注意力权重最高的位置                         |

### 我想直接动手——现成产品入口

如果你想跳过理论研究、直接用上这些思路：

| 产品                                                                              | 一句话                                         |
| ------------------------------------------------------------------------------- | ------------------------------------------- |
| [deepseek\_runtime](https://github.com/7colorai/deepseek_runtime)               | 可复用的 Python 运行时内核，在 DeepSeek API 之上构建 Agent |
| [deepseekagent](https://github.com/yuanchenglu/deepseekagent)                   | 面向用户的"一人公司"操作系统，10 层 Harness 优化             |
| [oh-my-deepseek-harness](https://github.com/yuanchenglu/oh-my-deepseek-harness) | Hermes Agent 插件，一条命令注入满血 DeepSeek 能力        |
| [deepcode](https://github.com/yuanchenglu/deepcode)                             | DeepSeek V4 深度优化的 AI 编程助手                   |

***

## 核心架构

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   LLM (概率推理引擎)           Harness Runtime (控制与证据系统) │
│   ─────────────              ─────────────────────            │
│                                                              │
│   理解用户意图    ──→         持久记忆 (Memory)                │
│   生成代码/文本  ──→         工具与权限 (Tools + Policy)       │
│   逻辑推理       ──→         状态与编排 (State + Orchestrator) │
│   模式识别       ──→         Checkpoint 与验证 (Evidence)     │
│                             模型路由与成本遥测                 │
│                             沙箱、恢复与审查                   │
│                             上下文编译与压缩                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**一句话**：模型像概率推理引擎，Harness 则负责把它连接到上下文、工具、权限、状态和证据。

***

## 关于我

袁成路。DeepinOS 开源Linux操作系统开发者，编程猫产品总监 → 迷你编程创始人。

现在用 5 台机器跑 Agent 矩阵：3 个研发小组（OpenCode / Claude Code / CodeX）+ 1 个市场运营组（OpenClaw），由 Hermes 做 CEO 统一调度。多期参与火山方舟 Hermes Agent 内部众测。

我相信 LLM + Harness = Agent。模型和 Harness 共同演进，DeepSeek 提供了新的模型能力与成本结构，但需要用可验证的系统工程把这些能力变成可靠产品。

***

## 参与讨论

- **深度技术交流 / 工作机会**：<yuanchenglu001@gmail.com>
- **GitHub Issue**：对任何创新点有不同看法，开 Issue 讨论
- **协议**：[CC BY-NC-SA 4.0](LICENSE.md) — 允许非商业分享和改编，需署名并以相同方式共享。详见 [CONTRIBUTING.md](CONTRIBUTING.md)

***

> ⭐ 如果这个仓库帮你省下了调研时间，点个 Star 让更多人看到。
>
> *「LLM + Harness = Agent」系列每篇都可以独立阅读，建议从 01 开始按顺序读——它们共享同一个核心逻辑：把不可丢失的和可以压缩的分开。*

