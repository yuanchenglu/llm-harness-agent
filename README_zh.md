# LLM + Harness = Agent

> 从模型能力到可验证 Agent 系统——基于长期实践、源码审计与待验证实验的理论框架

[**Read in English**](README.md) · [**⭐ 点个 Star**](https://github.com/yuanchenglu/llm-harness-agent)，有新论文第一时间通知

---

## TL;DR

1. **模型能力不等于产品能力**。同一个模型经过不同的上下文、工具、权限、状态与验证机制，会表现出明显不同的可靠性、成本和用户体验。
2. **Harness 是模型与真实世界之间的协议层、控制层和证据层**。它能放大模型能力，也可能引入新的错误，因此必须基于源码和 benchmark 评估。
3. **本文档集是理论与调研入口，不是已经完成的产品 benchmark**。长期实践用于提出问题，源码审计用于确认实现，协议与成本实验用于决定哪些结论可以进入 DeepSeek Agent。

---

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

**一句话**：模型像概率推理引擎，Harness 则负责把它连接到上下文、工具、权限、状态和证据。CPU/操作系统类比便于理解，但不能代替真实的协议与运行时分析。

---

## 导航

### 推荐先读

| 文章 | 用途 |
|---|---|
| [DeepSeek Agent 理论总纲](zh/theory/theory-guide.md) | 从模型、上下文、工具、编排和证据五层理解产品理论 |
| [研究方法与事实校准](zh/theory/research-method.md) | 了解哪些观点已被源码确认，哪些仍是待验证假设 |
| [DeepSeek API 与 Prefix Cache Benchmark Harness 计划](zh/blueprint/benchmark-harness-plan.md) | 下一阶段唯一任务的实验矩阵、验收门槛与结果决策树 |
| [产品对比](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | 理解不同 Agent 产品的边界与适用场景 |

### 核心创新点（每篇独立深度文章）

| # | 文章 | 一句话 |
|---|------|--------|
| [01](zh/innovations/01-agent-immune-system.md) | **Agent 免疫系统** | Prompt 指令可能在长任务中失效，让 Harness 自查自修而非让模型硬记 |
| [02](zh/innovations/02-bidirectional-agent.md) | **大脑主动驱动小脑** | 从「Harness→LLM」单向流变为「LLM⇄Harness」双向主动流 |
| [03](zh/innovations/03-attention-budget.md) | **注意力预算管理** | Agent 表现退化不一定是模型问题，也可能来自上下文与注意力管理 |
| [04](zh/innovations/04-kv-cache-prefix.md) | **KV Cache 硬约束前缀注入** | 把稳定约束与可压缩历史分离，降低约束在压缩中丢失的风险 |
| [05](zh/innovations/05-document-kv-cache.md) | **文档 KV Cache 优化结构** | 把 Agent 内部的优化原理应用到文档规范上——元层面的自指 |
| [06](zh/innovations/06-okr-planstep-cascade.md) | **OKR 增强型 PlanStep + 级联修正** | Plan 从扁平清单升级为有向依赖图，改一步自动级联修正 |
| [07](zh/innovations/07-review-switching.md) | **KV Cache 驱动的审查深度切换** | 审查标准不该是固定阈值，应该是 f(KV Cache, Plan 复杂度) |
| [08](zh/innovations/08-scope-creep.md) | **两层面范围蔓延的分治策略** | 需求蔓延和技术蔓延是两种病，不能用同一种药 |
| [09](zh/innovations/09-skills-self-evolution.md) | **Skills 自进化闭环** | Agent 完成复杂任务→提议沉淀为 Skill→下次减少重复推理 |
| [10](zh/innovations/10-intent-routing.md) | **7+1 意图→策略自动切换** | 识别任务意图→自动匹配采访深度/审查标准/执行模式 |
| [11](zh/innovations/11-checkpoint-review.md) | **Checkpoint 快照驱动的多轮审查** | 用独立快照控制审查上下文，而不是反复携带完整历史 |
| [12](zh/innovations/12-memory-granularity.md) | **Memory 粒度控制** | Memory 不是越强越好——收敛任务要强记忆，发散任务要弱记忆 |
| [13](zh/innovations/13-byte-stable-prefix-architecture.md) | **Byte-Stable Prefix 作为架构约束** | 不只是缓存 System Prompt——让整个 Agent 以 Cache 优先 |
| [14](zh/innovations/14-reasoning-content-stripping.md) | **Reasoning Content 回传陷阱** | Agent 应该知道什么不该回传——每个 Token 都要证明自己的存在价值 |

### 产品分析

| 文章 | 内容 |
|------|------|
| [9 款 Agent 产品校准对比](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Hermes / ClaudeCode / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent / CodeWhale 的校准对比 + Agent 矩阵分工 |
| [DeepSeek-Reasonix 深度分析](zh/blueprint/03-Agent竞品Harness调研-Agent-Competitor-Harness-Research/7-a-Reasonix-PrefixCache架构深度分析.md) | Reasonix 源码级技术分析 + Hermes vs CodeWhale 三方对比 + 9 个 DeepSeek Prefix Cache 优化 |

---

## 关于我

袁成路。DeepinOS 开源社区十年，编程猫产品总监 → 迷你编程创始人。

现在用 5 台机器跑 Agent 矩阵：3 个研发小组（OpenCode / ClaudeCode / CodeX）+ 1 个市场运营组（OpenClaw），由 Hermes 做 CEO 统一调度。多期参与火山方舟 Hermes Agent 内部众测。

我相信 LLM + Harness = Agent。模型和 Harness 会共同演进。DeepSeek 提供了新的模型能力与成本结构，现在需要用可验证的系统工程把这些能力变成可靠产品。

---

## 参与讨论

- **深度技术交流 / 工作机会**：yuanchenglu001@gmail.com
- **GitHub Issue**：对任何创新点有不同看法，开 Issue 讨论
- **协议**：[CC BY-NC-SA 4.0](LICENSE.md) — 允许非商业分享和改编，需署名并以相同方式共享。详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

*本文为「LLM + Harness = Agent」系列的总入口。每篇创新点文章都可以独立阅读，也互相关联。建议从 01 开始，按顺序读——它们共享同一个核心逻辑：「把不可丢失的和可以压缩的分开」。*
