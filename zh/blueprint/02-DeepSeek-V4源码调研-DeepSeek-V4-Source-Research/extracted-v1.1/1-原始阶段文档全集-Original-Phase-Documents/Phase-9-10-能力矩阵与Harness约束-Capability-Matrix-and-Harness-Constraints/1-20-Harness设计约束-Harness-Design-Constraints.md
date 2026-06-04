# 10-harness-design-constraints.md — DeepSeek Agent Harness 架构约束 v0.1

> 目标：把 DeepSeek V4 物理特性转化为不可违反的 Harness 设计约束。

---

## C-001：Byte-Stable Prefix 是一级架构约束

来源：

- DeepSeek context caching 依赖前缀匹配。
- V4 encoding / tool schema / reasoning mode 都会影响 prompt string。

约束：

```text
system prompt
tool schema
memory index
skill index
hard constraints
```

必须稳定排序、稳定内容、稳定字节。

---

## C-002：Context 必须 Layout-driven

来源：

- sliding_window=128
- attention candidates = window + compressed history
- index_topk 有预算

约束：

```text
不能 history dump
必须有 Context Layout Manager
必须区分 prefix / anchor / active / compressed / tail
```

---

## C-003：Checkpoint 是长任务的一等对象

来源：

- 远程历史会被压缩/稀疏选择。
- reasoning_content 默认不应无限回传。
- 工具循环会积累噪声。

约束：

```text
每个长任务必须周期性 checkpoint
工具失败必须 checkpoint
Pro review 前必须 checkpoint
上下文超过阈值必须 checkpoint
```

---

## C-004：Flash-first, Pro-on-checkpoint

来源：

- Flash 是同构小模型，支持 1M/think/max。
- Pro 在长上下文/agentic/知识上更强。

约束：

```text
Flash 用于执行
Pro 用于规划/审查/失败复盘/最终交付
Max 只用于关键高风险节点
```

---

## C-005：Reasoning 不能当 Memory

来源：

- encoding 默认 drop old reasoning。
- 有 tools 时 reasoning 会累积。
- Max special prefix 会影响 cache。

约束：

```text
reasoning_content 默认 display/archive
不默认进入下一轮 prompt
核心价值转 checkpoint / skill / memory
```

---

## C-006：Tool schema 必须稳定

来源：

- DSML tool calling 由 prompt template 渲染。
- tool schema 变化会破坏 prefix cache。

约束：

```text
工具按 name 排序
参数字段排序
description 不动态生成
不要每轮增删工具
```

---

## C-007：Tool call 必须有 Repair 层

来源：

- DSML 是文本协议，可能 malformed。
- Agent 产品不能依赖模型每次格式完美。

约束：

```text
DSML parser
malformed detector
repair prompt
fallback extractor
retry policy
```

---

## C-008：Backend 必须可探测

来源：

- 官方 API、私有 endpoint、本地部署能力不同。

约束：

```text
supports_1m_context
supports_thinking
supports_max
supports_tool_calls
supports_cache_metrics
supports_fim
max_output_tokens
```

---

## C-009：Cost Telemetry 必须内置

来源：

- V4 成本取决于 cache hit/miss、model、thinking、loop count。

约束：

```text
每轮记录：
model
thinking_mode
cache_hit_tokens
cache_miss_tokens
output_tokens
route_reason
estimated_cost
actual_cost
```

---

## C-010：Prompt 控制信息必须标签化

来源：

- 前 3 层 hash routing。
- mHC 多信号传播。
- sparse retrieval 需要 anchor。

约束：

```text
[CURRENT_GOAL]
[CURRENT_STEP]
[HARD_CONSTRAINTS]
[ACTIVE_FILES]
[CHECKPOINT]
[TEST_RESULT]
[NEXT_ACTION]
```

---

## C-011：Local V4 不作为桌面 MVP 默认路径

来源：

- 官方本地推理依赖权重转换、torchrun、model parallel、TileLang kernels。

约束：

```text
默认 DeepSeek API
支持 private endpoint
本地部署只作为高级 endpoint
```

---

## C-012：FIM / 局部编辑默认 non-thinking

来源：

- 官方 FIM non-thinking only。

约束：

```text
局部补全
小 diff
单文件 edit
```

不应默认走 Think/Max。

---

## C-013：最终交付必须 Review-gated

来源：

- Flash 执行强，但 Pro 在最终 agentic benchmark 更稳。
- 长任务可能偏航。

约束：

```text
复杂任务最终交付前至少一次 Pro Review
高风险任务必须 Pro + User Approval
```

---

## C-014：Memory / Skill 采用 index-in-prefix, body-on-demand

来源：

- prefix cache 需要稳定。
- long context sparse attention 需要短 anchor。

约束：

```text
prefix 放名称/描述/触发条件
body 通过 tool/on-demand 加载
```

---

## C-015：Harness 应保存“可用推理”，不是原始推理

来源：

- reasoning_content 噪声大、长、会污染上下文。

约束：

```text
reasoning → decision
reasoning → checkpoint
reasoning → failure note
reasoning → skill
reasoning 原文 archive-only
```
