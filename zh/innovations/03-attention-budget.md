# 注意力预算管理：从“稀释定律”改为可验证的上下文分配

> **证据等级：B（工程设计提案）**  
> 本文讨论 Harness 如何控制模型可见信息、干扰项和验证成本。它不再把“上下文越长，注意力必然按 `1/L` 衰减”写成 Transformer 物理定律。任何质量收益必须通过固定模型、固定任务集和可复现实验确认。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-03  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[02 大脑主动驱动小脑](02-bidirectional-agent.md)  
> **下一篇**：[04 稳定约束与可压缩历史分区](04-kv-cache-prefix.md)

---

## 摘要

长任务中的 Agent 可能出现约束遗漏、目标漂移、工具选择错误、重复读取和审查质量下降，但这些现象不能简单归因于“注意力被平均稀释”。更准确的工程问题是：

> 在有限上下文、成本和延迟预算下，Harness 应该让模型看到哪些信息、按什么结构看到、哪些规则必须由 Runtime 强制执行、哪些结果必须由外部证据验证？

本文把“注意力预算”定义为一个产品工程概念，而不是一个可直接从序列长度推出的数学量。核心方案是：

1. 把安全和权限约束下沉到确定性 Runtime；
2. 将稳定规则、活跃工作集、历史证据和外部索引分区；
3. Skill、Memory 和工具目录按需披露；
4. 子任务隔离，但摘要必须可追溯到原始证据；
5. 压缩、检索和布局策略用任务级 benchmark 比较；
6. Prefix Cache 只作为成本和延迟遥测，不作为质量保证。

---

## 1. 公开修正

### 1.1 `O(n²)` 不等于每个 Token 只能获得 `1/n` 注意力

标准全注意力的 `O(n²)` 描述 Query-Key 配对数量随序列长度增长的计算复杂度。单个 Token 的实际注意力权重由 Query、Key、层、注意力头、位置编码、训练分布和任务内容共同决定，并不要求均匀分配。

因此，以下推导不能作为事实：

```text
序列长度增长
→ 每条指令的权重必然等于 1/L
→ 约束遵守率必然与 1/L 成正比
```

长上下文可能增加检索难度、干扰项、位置敏感性和成本，但退化是否发生、何时发生、退化多少，必须对具体模型和任务测量。

### 1.2 长对话退化不一定单调，也不一定不可逆

质量变化可能来自：

- 相关信息没有被检索到；
- 新指令与旧指令冲突；
- 工具结果过长或格式混乱；
- 历史错误被继续传播；
- 压缩摘要遗漏关键事实；
- 模型或工具发生切换；
- 用户目标在多轮交互中改变；
- Runtime 没有对权限、状态和完成条件做确定性约束。

重新检索、清理工具结果、重建活跃工作集、回滚错误状态或切换独立审查上下文，都可能恢复质量。因此不能把“继续对话只会继续变差”写成普遍结论。

### 1.3 历史 `40% → 95%` 数据降级

早期文章曾写出：

- 约束保持率约 `40% → >95%`；
- 每任务节省 `8K–35K` Token；
- 上下文膨胀速度降低约 `60%`。

这些数字缺少完整任务集、Runner、原始结果、随机种子、基线定义、统计检验和独立复现，不能作为确认性实验结论。它们只保留为历史自测线索，不进入 README、产品承诺或 Release Gate。

### 1.4 Prefix Cache 不等于模型注意力，也不等于约束遵守

必须分开测量：

| 概念 | 问题 | 典型指标 |
| --- | --- | --- |
| 上下文保留 | 信息是否仍在请求中 | 字段/消息/摘要完整性 |
| Prefix Cache | Provider 是否复用了共同前缀计算 | hit/miss tokens、TTFT、成本 |
| 信息检索 | 模型是否找到了相关内容 | retrieval accuracy、引用正确率 |
| 约束遵守 | 最终动作是否满足规则 | violation rate、policy blocks |
| 任务质量 | 结果是否正确完成 | first-pass success、tests、human intervention |

前缀命中率高，不能证明模型遵守了约束；约束文本仍存在，也不能证明模型会执行它。

---

## 2. 问题定义

### 2.1 Harness 真正能控制什么

Harness 不能直接分配模型内部每一层的注意力权重，但可以控制模型输入和执行环境：

```text
可见信息集合
信息顺序与结构
工具 Schema 和工具结果
Memory / Skill 披露范围
压缩与检索策略
子任务边界
权限与副作用
验证器与完成条件
模型、预算与重试策略
```

因此，“注意力预算管理”更准确的定义是：

> Harness 对模型可见信息、确定性规则、推理成本和验证资源的联合分配。

### 2.2 质量模型

不把任务质量写成 `1/L` 的函数，而使用可实验分解：

```text
TaskQuality = f(
  model,
  task,
  relevant_context_recall,
  instruction_conflict,
  tool_result_quality,
  context_layout,
  state_correctness,
  policy_enforcement,
  verifier_quality,
  retry_budget
)
```

这个表达不声称知道闭式解。它的价值是把可能原因拆成可以单独控制和测量的变量。

---

## 3. 方案设计

### 3.1 确定性约束下沉到 Runtime

以下规则不应仅依赖 Prompt：

- 不允许写出 Workspace；
- 不允许修改 `.git` 或受保护路径；
- 高风险动作必须审批；
- Approval 后原文件 Hash 变化则拒绝 Apply；
- 预算超限时停在 Checkpoint；
- 测试未通过时不能标记完成；
- 不可逆工具必须单独授权。

模型可以解释规则、提出动作和生成候选方案，但最终执行权由 Policy、Sandbox、ChangeSet 和 Verifier 决定。

### 3.2 上下文四区

```text
稳定规则区
  系统角色、批准的项目规则、稳定工具契约

追加证据区
  决策、测试、Checkpoint、审查结论、失败原因

活跃工作集
  当前目标、相关文件片段、最近工具结果、待处理风险

外部索引
  完整轨迹、历史 Session、归档文档、可按需读取的 Skill Body
```

分区目标不是宣称“前面的 Token 永远更受关注”，而是：

- 明确信息生命周期；
- 避免把完整历史默认塞入请求；
- 让压缩只作用于明确允许压缩的区域；
- 让 Evidence 和原始 Artifact 保持可追溯；
- 为 Prefix Cache 提供稳定前缀候选。

### 3.3 Skill、Memory 和工具按需披露

默认只加载索引和短描述；Body、详细 Memory 和低频工具在匹配到当前任务时再读取。

但按需披露必须处理两个风险：

1. **漏召回**：相关 Skill 或工具没有被加载；
2. **错召回**：加载了不相关或恶意内容，反而增加干扰和权限风险。

因此需要记录：

```text
candidate set
selected items
selection reason
confidence
fallback behavior
missed dependency
```

### 3.4 子任务隔离

子任务可以使用独立 Session，避免把全部工具轨迹带回主线程。但子任务返回的摘要不能成为无来源的“新事实”。至少应附带：

```text
source files / tool calls
diff or artifact hash
tests executed
unverified assumptions
failure samples
```

主 Agent 和 Reviewer 应能从摘要回到原始证据，而不是只相信另一模型的自然语言结论。

### 3.5 Checkpoint 和压缩

Checkpoint 保存的是任务状态和证据索引，不是简单摘要：

```text
objective
approved scope
completed steps
pending steps
changeset ids
test results
open risks
source refs
resume preconditions
```

压缩器可以重写历史叙述，但不能覆盖：

- 已批准约束；
- 当前 Workspace 和版本；
- 未解决错误；
- Diff / Test / Approval / Rollback Evidence；
- 恢复所需的幂等键和状态版本。

### 3.6 Prefix Cache 遥测

记录：

```text
prefix fingerprint
prefix length
hit tokens
miss tokens
drift reason
TTFT
total latency
input/output tokens
estimated cost
```

Cache 优化只有在以下条件同时成立时才有效：

- 任务质量不下降；
- 权限范围不扩大；
- 安全更新可以主动失效旧前缀；
- 总成本或延迟有可重复改善。

---

## 4. 验证设计

### 4.1 实验因素

对同一批 Held-out 任务控制以下变量：

| 因素 | 对照 | 处理 |
| --- | --- | --- |
| 上下文布局 | 全历史追加 | 四区布局 + 活跃工作集 |
| Skill | 全量加载 | 索引 + 按需 Body |
| 工具结果 | 原始全文 | 清洗、截断、Artifact 引用 |
| 子任务 | 共享历史 | 独立 Session + Evidence 返回 |
| 压缩 | 自由摘要 | 结构化 Checkpoint + 来源索引 |
| 安全规则 | Prompt 约束 | Runtime Policy |

### 4.2 核心指标

优先指标：

```text
first-pass task success
success within retry budget
constraint violation rate
incorrect tool-call rate
human intervention rate
rollback rate
source citation accuracy
```

资源指标：

```text
prompt/output tokens
cache hit/miss tokens
TTFT
total latency
cost per successful task
```

不得只报告 Token 下降，不报告正确性和失败样本。

### 4.3 数据集纪律

必须分开：

```text
development set
prompt-tuning set
validation set
final held-out test set
```

任务专用 acceptance hints、Verifier feedback 和多轮 retry 都必须记录，不能把调参后的最终完成率当作首次泛化成功率。

---

## 5. 边界与风险

- 短任务中，检索、分类和快照的开销可能超过收益；
- 过度隔离可能丢失跨任务依赖；
- 摘要可能产生错误事实或隐藏失败；
- 按需工具披露可能漏掉关键工具；
- 固定前缀可能阻碍安全规则更新；
- 更严格审查会增加成本，且不保证弥补模型能力不足；
- Provider Cache 行为可能随时间、区域、账户和 Endpoint 改变。

因此所有策略都必须允许：

```text
disable
fallback
rebuild context
invalidate cache
escalate to user
reproduce from evidence
```

---

## 6. 结论

“注意力预算”是一个有用的工程隐喻，但不是 `α = 1/L` 的物理定律。

可靠的 Harness 不试图通过口号让模型“记得更多”，而是：

1. 减少无关输入；
2. 把不可妥协的规则变成 Runtime Policy；
3. 保持状态和 Evidence 可追溯；
4. 按任务加载必要信息；
5. 用 Held-out 任务验证质量、成本和延迟的真实变化。

只有当实验同时证明正确性不下降、风险不增加、每成功任务成本或延迟稳定改善时，某种上下文策略才应进入产品默认值。
