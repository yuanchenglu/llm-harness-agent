# 10-deepseek-agent-architecture-decisions.md — DeepSeek Agent 架构决策 v0.1

> 目标：把 V4 源码调研结论转成 DeepSeek Agent 的第一版架构决策。

---

## AD-001：产品默认接 API / Endpoint，不内置本地 V4 推理

理由：

- V4 本地推理依赖大型权重、model parallel、TileLang kernels。
- 桌面产品目标是低门槛安装使用。
- 本地/私有化可通过 custom endpoint 支持。

决策：

```text
DeepSeek Agent Core 只依赖 OpenAI-compatible / DeepSeek-compatible endpoint。
Local runtime 作为高级配置。
```

---

## AD-002：实现 DeepSeekV4MessageCompiler

理由：

- V4 没有 Jinja template。
- Tool calling 使用 DSML。
- Tool result merge into user message。
- Reasoning mode 是协议级控制。

决策：

```text
不直接使用 generic OpenAI adapter。
内部先标准化消息，再编译成 DeepSeek V4 prompt protocol。
```

---

## AD-003：实现 Context Layout Manager

理由：

- V4 1M context 是 sparse/compressed。
- sliding_window=128。
- index_topk 有预算。

决策：

```text
上下文分为：
stable_prefix
task_anchor
active_working_set
compressed_history
turn_tail
```

---

## AD-004：实现 Checkpoint Snapshotter

理由：

- 长任务不能靠 raw history。
- reasoning 不应无限回传。
- review 需要小上下文快照。

决策：

```text
所有中长任务都有 checkpoint。
Pro review 读取 checkpoint，不读取全部执行日志。
```

---

## AD-005：实现 Flash / Pro / Thinking Router

理由：

- model_size 和 reasoning_effort 是双轴。
- Flash 适合执行，Pro 适合审查/规划。

决策：

```text
默认 Flash-first。
复杂/失败/高风险/最终审查切 Pro。
Max 只用于关键节点。
```

---

## AD-006：实现 Cost & Cache Telemetry

理由：

- DeepSeek 成本取决于 hit/miss。
- 用户需要知道为什么这一步贵。
- 工程需要优化 prefix 稳定性。

决策：

```text
每轮记录 cache_hit, cache_miss, output, model, thinking, route_reason。
```

---

## AD-007：实现 ToolCallRepair

理由：

- DSML 是文本格式。
- 生产 Agent 必须能处理 malformed tool call。

决策：

```text
解析失败后：
1. 自动修复
2. 低温重试
3. 要求模型重发 tool call
4. 最后降级人工确认
```

---

## AD-008：Memory / Skill 采用 index-first

理由：

- prefix 稳定；
- long context 不应堆 body；
- Skill body 可按需加载。

决策：

```text
prefix 中只保留 Memory/Skill index。
正文通过 tool retrieval 注入 active working set。
```

---

## AD-009：Plan 采用 attention-anchor graph

理由：

- sparse retrieval 需要结构化锚点；
- 多文件任务需要依赖图；
- Pro review 需要短快照。

决策：

```yaml
plan_step:
  id:
  parent_id:
  dependencies:
  current_goal:
  key_result:
  constraints:
  rollback:
  status:
```

---

## AD-010：Review 采用 checkpoint-driven Pro review

理由：

- Pro 更适合长上下文审查；
- checkpoint 比 raw log 更适合 attention；
- 成本更低。

决策：

```text
Flash 执行 → checkpoint → Pro review → Flash 继续。
```

---

## AD-011：ReasoningContentPolicy 四态管理

理由：

- reasoning 不是 memory；
- encoding 默认 drop；
- 工具循环会导致 reasoning 膨胀。

决策：

```text
display
archive
summarize
prompt
```

默认不进入 prompt。

---

## AD-012：权限与高风险操作绑定 Pro Review

理由：

- 高风险操作需要更强推理和用户确认。

决策：

```text
delete / overwrite / migration / production / payment / legal
→ Pro Think + user approval
```

---

## AD-013：早期产品功能优先级

第一阶段只做能验证 V4-aware Harness 的功能：

```text
1. 本地文件/代码库读取
2. Context Layout
3. Flash/Pro Router
4. Checkpoint
5. Tool calling
6. Cost telemetry
7. Pro review
```

暂不做：

```text
复杂插件市场
多平台 Gateway
本地 V4 推理
大型多人协作
```

---

## AD-014：最终架构名称

建议核心命名：

```text
DeepSeek Agent Harness
  ├── V4MessageCompiler
  ├── ContextLayoutManager
  ├── ModelRouter
  ├── CheckpointSnapshotter
  ├── ReviewSwitcher
  ├── ToolCallRuntime
  ├── MemorySkillIndex
  └── CostCacheTelemetry
```

---

## AD-015：一句话架构定位

DeepSeek Agent 不是 DeepSeek API shell。

它是：

```text
针对 DeepSeek V4 物理特性重写的 Cache-first、Layout-driven、Checkpoint-gated、Flash/Pro-routed Agent Harness。
```
