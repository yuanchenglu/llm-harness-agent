# LLM + Harness = Agent

> 为什么「Harness」比模型更重要——5000+ 小时、10+ 款 Agent 产品、5 台机器上的系统性验证

---

## TL;DR

1. **LLM 的智商是常数**。Transformer 的物理边界决定了上下文越长，注意力越稀释。模型改进是线性增长，Harness 改进是指数释放。
2. **同一个 DeepSeek V4，在不同 Harness 上的表现天差地别**。我跑过 Hermes、ClaudeCode、OpenCode、Codex、OpenClaw、pi、Cursor、Coze——每一款都在同一个模型上暴露了不同的能力边界。
3. **我在 5 台机器上跑了一个 Agent 矩阵当研发团队使**。多期参与火山方舟 Hermes Agent 内部众测。这篇文章是系统性实战输出。不是综述，不是 benchmark，是一个 builder 把手弄脏之后的理解。

---

## 核心架构

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   LLM (推理引擎)              HermesTech (运营系统)            │
│   ─────────────              ─────────────────────            │
│                                                              │
│   理解用户意图    ──→         持久记忆 (Memory)                │
│   生成代码/文本  ──→         技能进化 (Skills)                │
│   逻辑推理       ──→         任务调度 (Kanban + delegate)      │
│   模式识别       ──→         定时任务 (Cron)                  │
│                             多平台桥接 (Gateway)              │
│                             子代理编排 (delegate_task)        │
│                             上下文管理 (Compaction)           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**一句话**：模型是 CPU，HermesTech 是进程调度器 + 文件系统 + 内存管理 + 网络栈。没有操作系统的 CPU 只是一块硅片。

---

## 导航

### 核心创新点（每篇独立深度文章）

| # | 文章 | 一句话 |
|---|------|--------|
| [01](innovations/01-agent-immune-system-zh.md) | **Agent 免疫系统** | Prompt 指令必然衰减，让 Harness 自查自修而非让模型硬记 |
| [02](innovations/02-bidirectional-agent-zh.md) | **大脑主动驱动小脑** | 从「Harness→LLM」单向流变为「LLM⇄Harness」双向主动流 |
| [03](innovations/03-attention-budget-zh.md) | **注意力预算管理** | Agent 变傻不是模型问题，是 Harness 没管好注意力分配 |
| [04](innovations/04-kv-cache-prefix-zh.md) | **KV Cache 硬约束前缀注入** | 约束不丢不是靠压缩算法聪明，是靠约束根本不在压缩范围里 |
| [05](innovations/05-document-kv-cache-zh.md) | **文档 KV Cache 优化结构** | 把 Agent 内部的优化原理应用到文档规范上——元层面的自指 |
| [06](innovations/06-okr-planstep-cascade-zh.md) | **OKR 增强型 PlanStep + 级联修正** | Plan 从扁平清单升级为有向依赖图，改一步自动级联修正 |
| [07](innovations/07-review-switching-zh.md) | **KV Cache 驱动的审查深度切换** | 审查标准不该是固定阈值，应该是 f(KV Cache, Plan 复杂度) |
| [08](innovations/08-scope-creep-zh.md) | **两层面范围蔓延的分治策略** | 需求蔓延和技术蔓延是两种病，不能用同一种药 |
| [09](innovations/09-skills-self-evolution-zh.md) | **Skills 自进化闭环** | Agent 完成复杂任务→自动提议保存为 Skill→下次零推理 Token |
| [10](innovations/10-intent-routing-zh.md) | **7+1 意图→策略自动切换** | 识别任务意图→自动匹配采访深度/审查标准/执行模式 |
| [11](innovations/11-checkpoint-review-zh.md) | **Checkpoint 快照驱动的多轮审查** | 审查上下文不是越来越大——第二轮的上下文比第一轮更小 |
| [12](innovations/12-memory-granularity-zh.md) | **Memory 粒度控制** | Memory 不是越强越好——收敛任务要强记忆，发散任务要弱记忆 |

### 产品分析

| 文章 | 内容 |
|------|------|
| [8 款 Agent 产品深度对比](comparison-zh.md) | Hermes / ClaudeCode / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent 的实战对比 + 我的 Agent 矩阵分工 |

---

## 为什么选择 Hermes 做中枢

不是因为它「最好」，是因为它将这些系统级能力**一体化集成在 Agent 推理管线中**：

| 能力 | 为什么重要 | 其他产品有吗 |
|------|-----------|------------|
| **Memory (SQLite)** | 跨 session 记住偏好和决策 | ❌ 主流编码Agent（ClaudeCode/OpenCode/Codex/Cursor）均无 |
| **Skills 自进化** | 成功经验自动沉淀，下次不重复消耗 Token | ❌ 其他平台均无此机制 |
| **Cronjob** | 定时自动化——每日总结、定期巡检 | ⚠️ OpenClaw 有调度，但 Hermes 是唯一将 cron 和 Agent 推理深度集成的 |
| **Gateway 多平台** | 飞书/微信/Discord 统一入口 | ⚠️ OpenClaw 本质即为 Gateway 产品，Hermes 的 Gateway 是与 Agent 内核一体化设计的 |

这四件套让 Hermes 从「编程工具」进化为「Agent 操作系统」。

---

## 关于我

袁成路。DeepinOS 开源社区十年，编程猫产品总监 → 迷你编程创始人。

现在用 5 台机器跑 Agent 矩阵：3 个研发小组（OpenCode / ClaudeCode / CodeX）+ 1 个市场运营组（OpenClaw），由 Hermes 做 CEO 统一调度。多期参与火山方舟 Hermes Agent 内部众测。

我相信 LLM + Harness = Agent。引擎的改进是线性的，底盘的改进是指数的。DeepSeek 把引擎造好了，现在轮到我们把底盘造好。

---

## 参与讨论

- **深度技术交流 / 工作机会**：yuanchenglu001@gmail.com
- **GitHub Issue**：对任何创新点有不同看法，开 Issue 讨论
- **协议**：[CC BY 4.0](LICENSE.md) — 自由分享和改编，需署名。详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

*本文为「LLM + Harness = Agent」系列的总入口。每篇创新点文章都可以独立阅读，也互相关联。建议从 01 开始，按顺序读——它们共享同一个核心逻辑：「把不可丢失的和可以压缩的分开」。*
