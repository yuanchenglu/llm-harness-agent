# 06-harness-implications-for-long-reasoning.md — mHC 对 DeepSeek Agent 长任务 Harness 的启发 v0.1

> 基于 V4 mHC / MoE 源码的 Harness 设计推论。

---

## 1. 总体判断

DeepSeek V4 的 mHC 和 MoE 共同说明：

> V4 是为长链路、多信号、多专家协同设计的模型；DeepSeek Agent 的 Harness 也必须是多信号分层架构，而不是普通 chat history 架构。

---

## 2. 多信号 Prompt 结构

由于 mHC 维护多份 hidden copies，prompt 不应是一段混合自然语言，而应显式分区：

```text
[GOAL_SIGNAL]
用户最终目标

[CONSTRAINT_SIGNAL]
必须遵守的硬约束

[EVIDENCE_SIGNAL]
当前证据和引用

[EXECUTION_SIGNAL]
当前执行状态

[REVIEW_SIGNAL]
验收标准和风险点

[NEXT_ACTION_SIGNAL]
下一步唯一动作
```

这不是因为模型“看不懂自然语言”，而是为了让模型内部多通道信号传播更清晰。

---

## 3. 长任务执行模式

建议 DeepSeek Agent 采用：

```text
Flash 执行
  ↓
Checkpoint snapshot
  ↓
Flash 自检
  ↓
Pro 审查关键 checkpoint
  ↓
继续执行
```

而不是：

```text
把所有历史日志塞入 1M context
  ↓
让模型自己总结自己
```

原因：

- V4 long-context 是 compressed/sparse retrieval；
- MoE routing 会根据 token/hidden state 选择专家；
- mHC 提升层内信号传播，不保证任务级记忆完整；
- 工具执行状态必须由 Harness 持久化。

---

## 4. Review 策略

### 4.1 Flash Review

适合：

```text
局部 diff 检查
格式检查
简单 checklist
小范围测试失败分析
```

### 4.2 Pro Review

适合：

```text
跨模块依赖检查
架构一致性
安全/权限/生产风险
长上下文 evidence conflict
最终交付前验收
```

### 4.3 Pro Max Review

适合：

```text
重大失败复盘
多轮执行偏航
复杂系统设计
用户明确要求最高可靠性
```

---

## 5. Prompt 标签稳定化

由于前 3 层 hash routing 由 token id 决定，Harness 应尽量固定关键标签。

推荐使用稳定标签：

```text
[CURRENT_GOAL]
[CURRENT_STEP]
[HARD_CONSTRAINTS]
[ACTIVE_FILES]
[CHECKPOINT]
[TEST_RESULT]
[RISK]
[NEXT_ACTION]
```

避免频繁变化：

```text
今天的目标是...
本轮我觉得...
刚刚这个问题...
总结一下情况...
```

不是不能用自然语言，而是核心控制信息必须结构化。

---

## 6. Checkpoint 应成为一等对象

V4 的内部稳定性并不替代外部任务状态。DeepSeek Agent 应把 checkpoint 作为一等对象：

```yaml
checkpoint_id: ckpt-20260604-001
goal: ...
current_step: ...
active_files:
  - ...
hard_constraints:
  - ...
decisions:
  - ...
evidence:
  - ...
test_results:
  - ...
risks:
  - ...
next_action: ...
review_required: true
recommended_model: pro_think
```

---

## 7. Agent Loop 推荐形态

```text
1. Intent Router
2. Context Layout Manager
3. Model Router
4. Tool Executor
5. Checkpoint Snapshotter
6. Review Switcher
7. Skill/Memory Writer
8. Cost/Cache Telemetry
```

其中：

- Intent Router 决定任务类型；
- Context Layout Manager 决定上下文分区；
- Model Router 决定 Flash/Pro/Think/Max；
- Checkpoint Snapshotter 负责外部状态；
- Review Switcher 根据风险升级 Pro；
- Telemetry 记录 cache hit/miss 和 route cost。

---

## 8. 为什么这不是泛 Agent 设计

普通 Agent 只会说：

```text
长上下文 + 工具调用 + Memory
```

DeepSeek V4-aware Agent 必须说：

```text
1M context 但 window=128
CSA/HCA 但 index_topk 有预算
MoE 但 Flash/Pro 每 token top-k 相同
前 3 层 hash routing
mHC 四份 hidden copies
FP4 routed experts + shared expert
reasoning effort 分层
cache hit/miss 分价
```

所以 Harness 设计必须是：

```text
layout-aware
routing-aware
checkpoint-aware
review-aware
cache-aware
```
