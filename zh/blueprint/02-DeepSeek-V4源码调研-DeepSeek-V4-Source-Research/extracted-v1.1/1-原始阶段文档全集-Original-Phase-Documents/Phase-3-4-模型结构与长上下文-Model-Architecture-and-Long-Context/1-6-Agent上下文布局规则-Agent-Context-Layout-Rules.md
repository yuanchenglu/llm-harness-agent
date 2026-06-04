# 04-context-layout-rules-for-agent.md — DeepSeek Agent 上下文布局规则 v0.1

> 基于 DeepSeek V4 `Attention / Compressor / Indexer` 源码的第一版 Harness 规则。

---

## 1. 核心原则

DeepSeek V4 的 1M context 应被理解为：

> 可被稀疏检索和压缩恢复的巨大工作记忆空间，而不是所有 token 均匀可见的黑板。

所以 Harness 的职责不是“把更多东西塞进去”，而是：

1. 决定哪些信息必须在最近窗口；
2. 决定哪些信息应该成为 attention anchor；
3. 决定哪些信息只配进入 checkpoint；
4. 决定什么时候从 Flash 切 Pro；
5. 决定什么时候压缩、摘要、索引、丢弃。

---

## 2. 推荐上下文布局

```text
┌──────────────────────────────────────────────┐
│ A. Byte-Stable Prefix                         │
│ - Agent identity                              │
│ - Tool schema                                 │
│ - Hard constraints                            │
│ - Memory index                                │
│ - Skill index                                 │
├──────────────────────────────────────────────┤
│ B. Task Anchor Zone                           │
│ - Current objective                           │
│ - Current Plan Step                           │
│ - Key Results / Success Criteria              │
│ - Dependency / Risk / Rollback                │
├──────────────────────────────────────────────┤
│ C. Active Working Set                         │
│ - Current file snippets                       │
│ - Current diff                                │
│ - Recent terminal output                      │
│ - Current tool result                         │
├──────────────────────────────────────────────┤
│ D. Compressed History Zone                    │
│ - Checkpoint snapshots                        │
│ - Prior decisions                             │
│ - Issue summaries                             │
│ - File index / symbol index                   │
├──────────────────────────────────────────────┤
│ E. Turn Tail                                  │
│ - Latest user request                         │
│ - This-turn transient instructions            │
│ - Immediate action target                     │
└──────────────────────────────────────────────┘
```

---

## 3. 最近窗口规则

由于 V4 的 `sliding_window=128`：

- 当前动作的必要信息必须出现在 turn tail 附近。
- 工具调用前要重新声明操作对象和约束。
- 不能只依赖 10 万 token 前的一句“不要删除文件”。
- 权限、危险操作、验收标准应该在执行前短暂重注入。

---

## 4. Anchor 规则

适合成为 anchor 的内容：

```text
[CONSTRAINT]
[CURRENT_GOAL]
[PLAN_STEP]
[KEY_RESULT]
[DEPENDENCY]
[ROLLBACK]
[ACTIVE_FILE]
[ERROR_SIGNATURE]
```

不适合成为 anchor 的内容：

```text
完整执行日志
大段聊天废话
重复文件内容
未结构化网页正文
旧终端输出
长 reasoning_content
```

---

## 5. Checkpoint 规则

每个 checkpoint 应短而完整：

```yaml
checkpoint_id: ckpt-xxx
goal: 当前目标
current_step: step-id
completed:
  - step-id: 结果摘要
unexpected:
  - 发现的问题
active_files:
  - path: why relevant
constraints:
  - 不可违反的约束
remaining:
  - 下一步计划
needs_review: true/false
```

---

## 6. Flash / Pro 上下文策略差异

### Flash

- index_topk=512
- 前两层 compress_ratio=0
- 更依赖清晰 layout
- 更适合：
  - 简单读取
  - 摘要
  - 文件定位
  - 局部编辑
  - 低风险工具调用

### Pro

- index_topk=1024
- 前两层 compress_ratio=128
- 更适合：
  - 长上下文证据检索
  - 复杂架构规划
  - 多文件重构
  - 关键审查
  - 失败复盘
  - agentic workflow

---

## 7. Harness 设计动作

### 7.1 Context Layout Manager

必须有独立模块负责：

- 固定 prefix；
- 当前目标区；
- active working set；
- compressed history；
- turn tail。

### 7.2 Checkpoint Snapshotter

必须自动在以下节点生成 checkpoint：

- Plan 生成后；
- 工具调用失败后；
- 多文件修改后；
- 测试运行后；
- 模型准备切 Pro 审查前；
- 上下文超过阈值前。

### 7.3 Attention Anchor Injector

把关键短字段注入：

```text
CURRENT_GOAL
CURRENT_STEP
SUCCESS_CRITERIA
HARD_CONSTRAINTS
ACTIVE_FILES
```

### 7.4 Model Router

路由策略：

```text
Flash Non-Think: 简单读写、摘要、分类、格式化
Flash Think: 中等规划、简单代码修改
Pro Non-Think: 大上下文快速检索、低推理高知识任务
Pro Think: 复杂规划、架构设计、审查
Pro Max: 高风险决策、失败复盘、关键 benchmark / PR 级任务
```

---

## 8. 关键设计结论

DeepSeek Agent 的 Harness 必须是：

```text
Cache-first
Context-layout-first
Checkpoint-first
Flash-first but Pro-aware
Sparse-attention-aware
Reasoning-budget-aware
```

否则就只是普通 Agent 壳，无法利用 V4 的物理优势。
