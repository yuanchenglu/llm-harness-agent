# 意图→策略自动切换：从已观察路由到 7+1 设计提案

> **证据等级：A1 + B**  
> - **A1**：固定源码可确认 OMO 使用 CLEAR/UNCLEAR 路由与 Trivial/Standard/Architecture 分级；Hermes 存在面向场景的路由机制。  
> - **B**：本文的 `refactor / new / medium / collaboration / architecture / research / simple + spec-driven` 是扩展设计提案，并非 OMO 或 Hermes 已完整实现的事实。  
> 请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-10  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[09 Skills 自进化闭环](09-skills-self-evolution.md)  
> **下一篇**：[11 Checkpoint 驱动的多轮审查](11-checkpoint-review.md)

---

## 摘要

不同任务需要不同执行策略：

- 简单修改不应经过十轮需求访谈；
- 高风险重构不能跳过契约和回归分析；
- 调研任务不能用“是否改完代码”作为唯一完成标准；
- 协作任务需要接口、隔离和合并策略；
- 架构决策需要权衡、Evidence 和决策记录。

源码观察表明，一些 Agent 已经使用粗粒度分类和条件路由。但本文的 7+1 体系是进一步的产品设计：

```text
Task Classification
→ Strategy Bundle
→ Runtime Observation
→ Upgrade / Downgrade
→ Evidence and Feedback
```

路由的目标不是追求漂亮的类别名称，而是为当前任务选择合适的：

```text
澄清深度
Plan 粒度
工具范围
Memory / Skill 范围
审查模式
模型与预算
人工审批
完成证据
```

---

## 1. 源码事实与设计提案的边界

### 1.1 OMO 可确认机制

固定源码审计确认 OMO 的规划入口包含：

```text
CLEAR / UNCLEAR
+ Trivial / Standard / Architecture
```

它主要用于决定：

- 是否需要继续澄清；
- 任务复杂度；
- 规划深度。

不能写成 OMO 已实现完整 7+1 意图体系。

### 1.2 Hermes 可确认机制

Hermes 的研究价值包括场景路由、工具注册、Memory、Skills 和长期运行能力。具体分类、触发条件和策略绑定必须按固定版本源码描述，不能把产品概念直接扩展成更细的已实现能力。

### 1.3 本文提案

7+1 体系用于探索：是否可以用可解释类别快速绑定默认策略，并用 Spec-Driven 模式覆盖未知任务。

它尚需验证：

- 分类准确率；
- 策略是否真的改善任务结果；
- 用户是否认为澄清和审查适量；
- 错误分类的代价；
- 不同模型和项目的迁移性。

---

## 2. 为什么需要策略路由

固定流程通常在两个方向失配：

### 2.1 过轻

任务：重构遗留支付模块。

如果直接执行，可能遗漏：

- 向后兼容；
- 模块契约；
- 状态共享；
- 数据迁移；
- 回滚；
- 回归测试。

### 2.2 过重

任务：修正 README 中一个错误命令。

如果强制：

- 深度访谈；
- 多 Agent 规划；
- 架构审查；
- 完整发布流程；

则协调成本超过任务价值。

### 2.3 更准确的问题

不是：

```text
这个任务属于哪个标签？
```

而是：

```text
为了安全、正确、经济地完成任务，需要哪些执行控制？
```

---

## 3. 多轴任务表示

固定单标签容易丢失信息，建议先输出多轴特征：

```yaml
task_profile:
  kind: refactor
  ambiguity: medium
  change_scope: multi_module
  risk: R2
  reversibility: reversible_with_tests
  novelty: high
  collaboration: single_agent
  deliverable: code_and_report
  evidence_required:
    - diff
    - unit_tests
    - integration_tests
    - compatibility_review
```

### 3.1 任务种类

候选：

```text
simple
bugfix
refactor
new_feature
new_project
research
architecture
operations
collaboration
```

类别可扩展，不必强制所有任务只能属于一个类别。

### 3.2 模糊度

```text
clear
partially_clear
unclear
conflicting
```

### 3.3 风险与可逆性

使用 I-07 的风险模型：

```text
R0–R4
fully_reversible → irreversible
```

### 3.4 改动范围

```text
no_change
single_file
multi_file
multi_module
multi_service
external_system
```

### 3.5 交付物

```text
answer
document
code
diff
configuration
release artifact
external side effect
```

---

## 4. 7+1 默认类别

以下类别是策略模板，不是自然界唯一分类。

### C1：Simple

适用：低风险、范围小、目标明确。

默认策略：

- 最少澄清；
- 一步或无显式 Plan；
- M1 自动验证；
- 默认低预算；
- 结果可逆。

### C2：Medium Change

适用：现有项目中 3–10 个文件的功能修改。

默认策略：

- 轻量澄清范围和验收；
- 文件/组件级 Plan；
- Diff + Tests + Light Review；
- 写入需要 ChangeSet。

### C3：Refactor

适用：结构变化但外部行为应保持。

默认策略：

- 读取现有架构和调用链；
- 明确不可变契约；
- 细粒度 Plan；
- 回归、兼容和性能证据；
- 高影响部分独立 Review。

### C4：New

适用：新项目或新模块。

默认策略：

- 确认核心用户价值和非目标；
- 避免把所有最佳实践一次性塞入 MVP；
- 里程碑 Plan；
- 基础可运行闭环优先。

### C5：Architecture

适用：跨模块、长期影响、难逆决策。

默认策略：

- 约束和非功能需求显式化；
- 备选方案和 Trade-off；
- ADR；
- 多维 Review；
- 不直接把架构讨论当作实现完成。

### C6：Research

适用：不确定性高、产出是知识和建议。

默认策略：

- 明确研究问题；
- 来源优先级；
- 事实/推论分离；
- 记录未找到证据；
- 允许迭代计划；
- 完成标准是证据覆盖，不是代码数量。

### C7：Collaboration

适用：多 Agent 或人机协作。

默认策略：

- 明确角色、输入、输出和 Loop Authority；
- Workspace 隔离；
- 接口契约；
- 合并和冲突策略；
- 子任务 Evidence 回传。

### +1：Spec-Driven

适用：

- 分类置信度低；
- 多类别混合；
- 高风险；
- 用户已有结构化 Spec；
- 默认模板不够表达。

由 Spec 的约束直接生成 Strategy Bundle，而不是强行归入某一类别。

---

## 5. Strategy Bundle

```yaml
strategy:
  clarification:
    mode: targeted
    max_questions: 3
  planning:
    granularity: component
    dependency_graph: true
  memory:
    mode: scoped_project
  skills:
    disclosure: index_then_on_demand
  tools:
    profile: code_safe_write
  model:
    default: flash
    escalation:
      - on_high_risk_checkpoint
      - on_repeated_verifier_failure
  review:
    mode: M2
  approval:
    required_for:
      - file_write
      - external_side_effect
  evidence:
    required:
      - diff
      - tests
      - rollback_point
```

策略字段必须可由 Runtime 执行，而不是只生成一段自然语言建议。

---

## 6. 路由流程

```text
Parse Task
→ Extract Task Profile
→ Generate Candidate Categories
→ Estimate Confidence and Risk
→ Select Strategy Bundle
→ Show Material Assumptions
→ Execute
→ Observe Runtime Signals
→ Upgrade / Downgrade Strategy
→ Record Outcome
```

### 6.1 路由输出

```yaml
route_id: route-123
category: refactor
alternatives:
  - medium_change
confidence: 0.72
risk: R2
reasons:
  - 涉及 4 个模块
  - 用户要求保持外部 API 不变
assumptions:
  - 当前测试覆盖可作为行为基线
strategy_ref: strategy-refactor-v2
```

### 6.2 Material Assumptions

高影响假设需要显示给用户或进入 Evidence，例如：

- “不改变外部 API”；
- “只支持 macOS”；
- “不迁移历史数据”；
- “不加入 OAuth”。

---

## 7. 运行时策略升级

初始分类可能错误。Runtime 需要根据事实升级：

```text
Simple
→ 发现跨模块依赖
→ Medium

Medium
→ 发现数据迁移和权限变化
→ Architecture / R3 Review

Research
→ 用户批准进入实现
→ New or Medium Change
```

降级也允许：

```text
Architecture
→ 约束明确且已有成熟模板
→ Medium Change
```

每次切换记录原因、成本和需要重新验证的 Evidence。

---

## 8. 不对称错误成本

| 错误 | 主要后果 | 默认处理 |
| --- | --- | --- |
| Simple → Refactor | 多问、多审查 | 可接受但需控制体验 |
| Refactor → Simple | 漏契约和回归 | 高风险，保守阈值 |
| Research → New | 未调研就开始实现 | 阻断写入，要求 Spec |
| Medium → Architecture | 过度设计 | 允许用户降级 |
| External Side Effect → Simple | 未审批执行 | 必须由 Runtime 风险分类兜底 |

风险分类和权限系统不能完全依赖意图路由。

---

## 9. 未知任务与开放集

分类器必须允许：

```text
unknown
mixed
needs_spec
needs_user_decision
```

不能为了覆盖率强行选择一个已知标签。

Spec-Driven 的价值是：

- 为未知任务提供可执行约束；
- 收集高频新模式；
- 未来再决定是否形成新类别。

---

## 10. 评测

### 10.1 分类

```text
confusion matrix
open-set rejection accuracy
confidence calibration
asymmetric cost-weighted error
```

### 10.2 策略效果

比较：

```text
fixed generic strategy
user-selected mode
automatic router
spec-driven strategy
```

指标：

```text
first-pass success
clarification turns
human correction
escaped defect
review cost
latency
cost per successful task
```

### 10.3 用户体验

- 问得太多/太少；
- 执行过慢/过快；
- 是否理解路由原因；
- 是否能手动覆盖；
- 覆盖后结果是否更好。

### 10.4 数据集纪律

需要：

- 多项目；
- 多任务类型；
- 模糊和混合任务；
- 高风险负样本；
- Held-out 项目；
- 不同模型。

不能用类别定义本身生成全部测试样本，否则分类器只是在复述模板。

---

## 11. 边界与风险

- 类别可能过多，维护成本上升；
- 路由模型可能自信但错误；
- 用户目标可能在执行中变化；
- 项目特定策略可能覆盖全局默认；
- 路由和模型选择可能破坏 Prefix Cache；
- 策略升级会增加成本；
- 自动分类不能替代 Runtime 安全边界；
- Spec 也可能不完整或错误。

需要用户覆盖、Runtime 兜底、版本化策略和失败回放。

---

## 12. 结论

本文的 7+1 不是对 OMO 已有实现的“完整披露”，而是基于已观察路由机制的扩展设计。

可靠的意图路由应：

1. 先提取多轴 Task Profile；
2. 用类别绑定可执行 Strategy Bundle；
3. 输出置信度、理由和关键假设；
4. 允许 Unknown 和 Spec-Driven；
5. 根据 Runtime 事实动态升级或降级；
6. 用不对称错误成本评估；
7. 让权限、Policy 和高风险审批独立兜底。

分类只是手段。真正目标是在正确的任务上采用足够、但不过度的澄清、规划、执行和审查策略。
