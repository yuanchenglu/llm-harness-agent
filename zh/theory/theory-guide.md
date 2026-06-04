# DeepSeek Agent 理论总纲：从模型能力到可验证的 Agent 系统

> 本文是本项目的理论入口。它不把某个 Agent 产品当作最终答案，而是解释：为什么同一个模型在不同 Harness 中表现不同，哪些机制值得进入 DeepSeek Agent，以及哪些观点仍需实验验证。

## 摘要

一个可用的 Agent 不是“模型加几个工具”，而是由模型、上下文编译器、工具运行时、权限系统、状态存储、验证机制和产品界面共同组成的系统：

```text
Agent = Model × Harness × Environment × Evidence
```

这里用乘号而不是加号，是为了强调短板效应：模型很强但权限失控，系统不可用；工具很多但上下文混乱，模型无法正确选择；执行完成但没有测试和审查，用户无法信任结果。

本文提出 DeepSeek Agent 的理论主线：

```text
Cache-first        尽量保持可复用前缀稳定，但不牺牲正确性
Layout-driven      主动设计模型可见上下文，而不是把日志全部塞进去
Policy-enforced    模型提出动作，Runtime 决定动作能否执行
Checkpoint-gated  “完成”必须由证据与审查状态决定
Model-routed       Flash / Pro / Thinking 的分工由风险和任务状态决定
```

这些是设计假设和架构方向，不是已经全部被 benchmark 证明的定律。

---

## 1. 先理解 Harness 是什么

### 1.1 模型与 Harness 的分工

模型负责概率性工作：理解意图、生成候选方案、推理和表达。Harness 负责确定性工作：加载上下文、暴露工具、执行命令、限制权限、保存状态、统计成本、验证结果。

可以把模型类比为 CPU，但这个类比有边界：模型不是确定性处理器，Harness 也不只是操作系统。更准确地说，Harness 是模型与真实世界之间的**协议层、控制层和证据层**。

### 1.2 为什么同一个模型表现不同

同一个模型在不同 Agent 中表现不同，通常不是模型参数变化，而是它看到和经历的过程不同：

1. System prompt、项目规则和文件片段如何排列；
2. 工具描述是否清晰，工具结果是否干净；
3. 是否能读到正确文件，是否被无关历史干扰；
4. 权限和沙箱是否允许安全执行；
5. 失败后是否重试、重新规划或升级模型；
6. 是否有测试、审查和完成门槛。

因此，“Harness 重要”是可观察的工程结论；但“Harness 改进一定指数增长”不是已建立的普遍规律。

---

## 2. DeepSeek Agent 的五层理论模型

### 2.1 Model Profile：先承认模型有物理与协议边界

Harness 不应该把所有模型当成同一个 API。模型配置至少需要表达：

```text
context window
thinking / reasoning 模式
工具调用协议
reasoning_content 行为
cache hit/miss usage
价格、延迟与可用 endpoint
```

DeepSeek Agent 的第一原则不是“使用更长上下文”，而是“根据真实 API 契约编译请求”。例如，`reasoning_content` 是否需要回传、何时回传、是否影响计费，不能仅凭某个开源项目的策略决定，必须对具体 endpoint 做协议测试。

### 2.2 Context Compiler：上下文不是日志，而是编译产物

一个长期任务会产生大量本地状态，但不应全部进入模型请求。建议把信息分为四区：

```text
稳定前缀：系统规则、批准的项目约束、稳定工具契约
追加证据：关键决策、checkpoint、测试结果、审查结论
活跃工作集：当前任务、相关文件片段、最近工具结果
外部索引：完整轨迹、历史 session、归档材料
```

“Byte-stable prefix”是有价值的设计目标，但不是绝对戒律。安全策略更新、工具变化或错误前缀都必须允许重建；正确性优先于缓存命中。

### 2.3 Tool and Safety Runtime：模型建议，Runtime 执行

可靠 Agent 的工具层需要同时处理：

- 工具 schema 与按需披露；
- 参数校验、错误清洗与结果截断；
- ask / allow / deny 权限；
- workspace、worktree、容器或沙箱隔离；
- 文件版本或 hash 保护；
- LSP、测试与静态检查反馈。

关键原则是：不要用 prompt 代替权限系统，也不要用模型自述代替工具证据。

### 2.4 Orchestrator：多 Agent 是状态机，不是角色扮演

Planner、executor、reviewer 和 subagent 只有在满足以下条件时才有意义：

1. 每个角色有明确输入、输出和退出条件；
2. 会话隔离带来的质量收益高于额外成本；
3. 并发写入有 workspace 隔离与合并策略；
4. 只有一个 loop authority 控制任务是否继续；
5. 用户可以看到状态、预算和阻塞原因。

因此，角色名称不是能力；可观测、可恢复、可终止的编排协议才是能力。

### 2.5 Evidence Ledger：完成不是一句话，而是一组证据

Agent 说“已经完成”并不等于任务完成。建议把完成条件写成机器可验证状态：

```text
目标和范围已确认
变更与批准的 spec 一致
相关测试通过
关键错误已解释
diff 已审查
高风险变更已获得额外 reviewer verdict
成本与未解决风险已记录
```

Checkpoint 的价值不是多存一份摘要，而是把计划、执行、测试、审查和恢复连接成一个可追踪的证据链。

---

## 3. 从竞品研究中可以确认什么

### 3.1 可作为源码参考的机制

| 项目 | 可确认的参考价值 | 证据边界 |
|---|---|---|
| Claude Code | 插件、skills、hooks、产品交互范式 | 官方仓库不公开完整 engine |
| Codex | typed context、turn loop、compaction、guardian、sandbox | 快速演进，引用必须固定 commit |
| Trae Agent | 小型 Agent loop、trajectory、Docker、MCP、有状态 sequential thinking | 未发现开源 test-time scaling orchestrator |
| Reasonix | DeepSeek adapter、cache telemetry、plan gate、compaction | 成本与质量优势仍需 benchmark |
| Hermes Agent | tool registry、progressive disclosure、memory/skills/gateway/cron | “自进化持续变好”仍需长期评测 |
| CodeWhale | prefix drift check、cache/cost telemetry、auto router、side-git、LSP | 完整 three-zone request contract 尚未接入 |
| OpenCode | 多端开源 Runtime、provider/agent/permission/plugin 边界 | 需要 Pass 2 与适配 Spike |
| OpenSpec | 可版本化 change artifacts | 不替代 Runtime checkpoint |
| Superpowers | 可组合工程流程与完成前验证 | 强制力依赖宿主 Runtime |

### 3.2 不能直接当作事实的主张

以下观点可以作为研究假设，但不能直接写入产品承诺：

- 某种上下文布局必然适配稀疏注意力；
- planner/executor 一定更省钱或质量更高；
- 长上下文一定优于压缩上下文；
- reasoning content 应永远重传或永远删除；
- 自动路由天然优于固定模型；
- Memory 越强，Agent 越聪明；
- 多 Agent 数量越多，任务越可靠。

---

## 4. DeepSeek Agent 的理论闭环

```text
意图澄清
  → 可版本化 Spec / Design / Task
  → 风险与成本路由
  → 隔离执行与工具证据
  → Checkpoint
  → 独立验证 / 必要时 Pro Review
  → 归档决策与可复用经验
```

这个闭环吸收了多类项目的优点，但不等于把它们拼装在一起。DeepSeek Agent 的差异化应来自统一 Runtime 中的三个原创连接：

1. **模型路由与证据门控连接**：失败、风险和 checkpoint 决定是否升级模型；
2. **缓存布局与状态机连接**：模式切换尽量在 Runtime gate 中完成，减少无意义前缀漂移；
3. **Artifact 与执行证据连接**：文档中的 task 与实际 diff、测试、审查和成本一一绑定。

---

## 5. 如何验证这套理论

理论文档的价值不在于听起来完整，而在于能产生可证伪实验。当前最高优先级是：

1. 验证 `reasoning_content` drop/replay 的协议要求和成本；
2. 验证 system/tools 变化、工具顺序、mode 切换和 compaction 对 cache hit 的影响；
3. 比较单模型、Flash router、planner/executor、Pro review 的质量与成本；
4. 比较完整工具目录与 progressive disclosure；
5. 在同一真实任务集上统计成功率、返工、人工干预、延迟和成本。

在这些实验完成前，本项目使用“候选设计”“源码已确认”“待 benchmark”这样的措辞，而不使用“已经证明最优”。

---

## 6. 推荐阅读路线

### 有计算机基础的普通读者

1. 本文；
2. [研究方法与事实校准](research-method.md)；
3. [产品对比](../blueprint/04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/4-1-竞品对比分析.md)；
4. 创新点 03、11、12；
5. 创新点 13、14。

### 准备设计 Agent 产品的读者

1. 本文；
2. 创新点 01–14；
3. [Reasonix 源码分析](../blueprint/03-Agent竞品Harness调研-Agent-Competitor-Harness-Research/7-a-Reasonix-PrefixCache架构深度分析.md)；
4. 研究方法中的待验证清单；
5. 建立自己的协议和 benchmark，而不是直接复制结论。

## 结论

`LLM + Harness = Agent` 最有价值的含义，不是“Harness 比模型重要”，而是：

> 模型能力只有通过可控上下文、可靠工具、安全执行、持久状态和可验证证据，才能成为用户真正可以依赖的产品能力。

这也是 DeepSeek Agent 应坚持的理论起点。
