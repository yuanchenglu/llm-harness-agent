# LLM + Harness = Agent

> 从模型能力到可验证 Agent 系统——基于长期实践、源码审计与可证伪实验的理论框架

[**English**](README_en.md) · [**简体中文**](README.md) · [**当前状态**](STATUS.md)

---

## TL;DR

1. **模型能力不等于产品能力**。同一个模型经过不同的上下文、工具、权限、状态与验证机制，会表现出不同的可靠性、成本和用户体验。
2. **Harness 是模型与真实世界之间的协议层、控制层和证据层**。它既可能放大模型能力，也可能引入新的错误，因此必须基于固定源码、协议测试和任务 benchmark 评估。
3. **本仓库是研究、产品规格、架构决策与实验摘要知识库**，不是当前 DeepSeekAgent Runtime 的完整可执行代码仓库，也不单独证明生产版本已经发布。
4. **当前生产发布状态以 [`STATUS.md`](STATUS.md) 和 [`stage-gates.json`](zh/blueprint/stage-gates.json) 为准**。缺少实际 Runtime commit、tag、artifact、checksum 和平台矩阵时，Production Release Gate 保持未验证。

## 当前产品化入口

| 文档 | 用途 |
|---|---|
| [项目状态真源](STATUS.md) | 判断本仓库能确认什么、产品发布还缺哪些外部证据 |
| [中文表达与术语表](zh/prd-tech-plan/00-中文表达与术语表.md) | 解释 release artifact、production gate、checksum、runtime 等术语 |
| [PRD TechPlan](zh/prd-tech-plan/README.md) | 产品范围、PRD、技术方案、release gates 和决策记录 |
| [Blueprint 交接包](zh/blueprint/README.md) | 历史阶段、证据链和调研入口；其中旧状态必须服从当前状态真源 |

阅读顺序：先读 `STATUS.md` 判断当前事实，再读 PRD TechPlan 理解产品方向，最后回到 Blueprint 追溯历史证据。

---

## 核心架构

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   LLM（概率推理引擎）          Harness Runtime（控制与证据系统） │
│   ─────────────              ─────────────────────            │
│                                                              │
│   理解用户意图    ──→         持久记忆（Memory）                │
│   生成代码/文本  ──→         工具与权限（Tools + Policy）       │
│   逻辑推理       ──→         状态与编排（State + Orchestrator） │
│   模式识别       ──→         Checkpoint 与验证（Evidence）     │
│                             模型路由与成本遥测                 │
│                             沙箱、恢复与审查                   │
│                             上下文编译与压缩                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**一句话**：模型负责概率性理解与生成，Harness 负责上下文、工具、权限、状态、执行和证据。CPU/操作系统类比便于理解，但不能代替真实协议与运行时分析。

---

## 导航

### 推荐先读

| 文章 | 用途 |
|---|---|
| [DeepSeek Agent 理论总纲](zh/theory/theory-guide.md) | 从模型、上下文、工具、编排和证据五层理解产品理论 |
| [研究方法与事实校准](zh/theory/research-method.md) | 区分源码事实、官方声明、工程推论、实验观察和未找到实现 |
| [协议与 Prefix Cache 实证报告](zh/blueprint/03-5-DeepSeek-Agent协议与Benchmark验证-DeepSeek-Agent-Protocol-and-Benchmark-Validation/18-0-协议与Prefix-Cache实证报告-Protocol-and-Prefix-Cache-Evidence.md) | 查看历史实验边界、已证实项和未证实项 |
| [Benchmark Harness 计划](zh/blueprint/benchmark-harness-plan.md) | 历史实验设计、验收门槛与结果决策树；不是当前唯一执行任务 |
| [产品对比](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | 理解不同 Agent 产品的实现边界与适用场景 |

### 核心创新点

> 下列文章包含源码观察、设计提案和待验证假设。文章标题中的机制名称不等于已经完成公开 benchmark 或生产实现。

| # | 文章 | 当前准确定位 |
|---|------|-------------|
| [01](zh/innovations/01-agent-immune-system.md) | **Agent 加固闭环** | 把违规事件转化为可测试、可审批、可回滚的系统改进 |
| [02](zh/innovations/02-bidirectional-agent.md) | **模型元请求** | 模型声明上下文、工具、审查和升级需求，Runtime 保留控制权 |
| [03](zh/innovations/03-attention-budget.md) | **上下文分配** | 用可验证的上下文与证据控制替代未经支持的 `1/L` 稀释定律 |
| [04](zh/innovations/04-kv-cache-prefix.md) | **稳定约束与可压缩历史分区** | 分离保留、遵守、强制执行和 Provider Cache |
| [05](zh/innovations/05-document-kv-cache.md) | **Agent 可读文档结构** | 版本化摘要、稳定章节 ID、Evidence Index 和分层读取 |
| [06](zh/innovations/06-okr-planstep-cascade.md) | **PlanGraph** | Node、Typed Edge、Acceptance、Evidence 和级联失效 |
| [07](zh/innovations/07-review-switching.md) | **风险与证据审查路由** | 根据风险、可逆性、影响范围和证据完整性选择审查模式 |
| [08](zh/innovations/08-scope-creep.md) | **范围变更治理** | 区分产品范围扩张与实现依赖发现 |
| [09](zh/innovations/09-skills-self-evolution.md) | **受治理的 Skill 供应链** | 来源、权限、测试、审批、Canary、监控与回滚 |
| [10](zh/innovations/10-intent-routing.md) | **意图→策略路由** | 基于 OMO/Hermes 已观察机制扩展出的 7+1 设计提案 |
| [11](zh/innovations/11-checkpoint-review.md) | **可追溯 Checkpoint** | 版本化状态、Evidence Ref、失效 Verdict 和幂等恢复 |
| [12](zh/innovations/12-memory-granularity.md) | **按 Scope 编译 Memory** | 来源、范围、置信度、有效期、隐私和用户控制 |
| [13](zh/innovations/13-byte-stable-prefix-architecture.md) | **受约束的 Byte Stability** | Canonical Segment 与显式失效，正确性和安全优先 |
| [14](zh/innovations/14-reasoning-content-stripping.md) | **Reasoning Replay Policy** | 按 Provider、Endpoint、Tool State 和协议证据决定回传策略 |
| [15](zh/innovations/15-dsml-tool-call-optimization.md) | **DSML 编码层研究** | 内部编码表示不等于客户端 DSML 协议 |
| [16](zh/innovations/16-quick-instruction-routing.md) | **Quick Instruction Capability Probe** | 编码证据存在，公共 API 可用性仍需验证 |
| [17](zh/innovations/17-reasoning-effort-control.md) | **推理策略与预算** | 分离参数接受、语义生效和任务收益 |
| [18](zh/innovations/18-latest-reminder-injection.md) | **动态上下文位置实验** | 来源、Trust、Scope、TTL 和隐私比位置口号更重要 |

### 产品分析

| 文章 | 内容 |
|------|------|
| [9 款 Agent 产品校准对比](zh/blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md) | Hermes / Claude Code / OpenCode / Codex / OpenClaw / Cursor / Coze / pi agent / CodeWhale 的校准对比 |
| [DeepSeek-Reasonix 深度分析](zh/blueprint/03-Agent竞品Harness调研-Agent-Competitor-Harness-Research/7-a-Reasonix-PrefixCache架构深度分析.md) | Reasonix 源码级分析、边界和可借鉴机制 |

---

## 关于我

袁成路。DeepinOS 开源社区十年，编程猫产品总监 → 迷你编程创始人。

现在用多台机器运行 Agent 矩阵，持续研究模型、Harness、工具、Memory、Skills、上下文和证据系统如何共同影响真实任务结果。

我相信 `LLM + Harness = Agent`。模型和 Harness 会共同演进，但任何强结论都应能够回到固定源码、协议、实验和任务证据。

---

## 参与讨论

- **深度技术交流 / 工作机会**：yuanchenglu001@gmail.com
- **GitHub Issue**：对任何创新点有不同看法，可提交反例、源码证据或复现实验
- **协议**：[CC BY-NC-SA 4.0](LICENSE.md) — 允许非商业分享和改编，需署名并以相同方式共享。详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

*本仓库优先区分“已经看到什么、据此推断什么、准备验证什么”。稳定信息与变化信息分区是一条重要设计线索，但不是无需实验的普遍定律。*
