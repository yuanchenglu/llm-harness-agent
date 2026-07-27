# Checkpoint 驱动的多轮审查：状态快照必须连接原始证据

> **证据等级：B（工程设计提案）**  
> 本文不再假设“所有 Agent 都只在任务结束后审查”，也不再使用“审查质量与上下文长度成反比”的未经验证公式。Checkpoint 的核心价值是把执行状态、恢复条件和 Evidence 固定下来，让 Reviewer 在受控上下文中审查，并能按需回到原始 Artifact。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-11  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[10 意图→策略路由](10-intent-routing.md)  
> **下一篇**：[12 Memory 粒度控制](12-memory-granularity.md)

---

## 摘要

复杂任务需要在执行过程中多次确认：

- 当前目标是否仍一致；
- 已完成步骤是否有证据；
- 工作区是否被意外改变；
- 失败后能否安全恢复；
- 剩余计划是否仍成立；
- 是否需要升级审查或人工介入。

仅在任务结束后读取完整对话不是唯一审查方式，但“只读模型生成的摘要”同样危险。摘要可能遗漏失败、错误归因或把未验证判断写成事实。

因此 Checkpoint 应是：

> 一个版本化、可校验、可恢复的任务状态快照，其中自然语言摘要只是索引，真正的完成判断连接到 Diff、Test、Tool、Approval 和 Artifact Evidence。

---

## 1. 公开修正

### 1.1 Checkpoint 不等于一段摘要

错误设计：

```text
目标 + 已完成摘要 + 剩余计划
```

这种结构适合快速阅读，但不足以恢复或审计。至少还需要：

```text
state version
workspace hash
plan version
changeset ids
artifact hashes
test run ids
approval ids
open errors
resume preconditions
```

### 1.2 Reviewer 不应只读摘要

Reviewer 可以先读简洁 Snapshot，但必须拥有按需获取原始证据的能力：

```text
Snapshot
→ Evidence Index
→ Original Diff / Test / Tool Result / Source File
```

否则会出现 Summary Laundering：执行 Agent 的错误总结被 Reviewer 当成已验证事实。

### 1.3 “上下文更小”不是自动质量保证

更小的 Review Context 可能减少噪音，也可能删除关键证据。需要测量的是：

- 关键来源覆盖率；
- 缺陷发现率；
- 错误引用率；
- 审查成本；
- 恢复成功率。

不能仅以 Token 更少证明审查更可靠。

### 1.4 异步审查必须处理状态漂移

Reviewer 读取 Checkpoint 后，主 Agent 可能继续修改工作区。Verdict 必须绑定：

```text
checkpoint_id
workspace_hash
plan_version
changeset_hash
```

状态变化后，旧 Verdict 只能作为历史记录，不能继续授权新动作。

---

## 2. Checkpoint 数据模型

```yaml
checkpoint_id: cp-0007
task_id: task-123
sequence: 7
created_at: 2026-07-27T00:00:00Z
runtime_version: 0.1.1
state_version: 42
workspace:
  root_id: workspace-a
  git_commit: abcdef123456
  dirty_tree_hash: sha256:...
objective:
  spec_ref: spec-12
  text: 修复权限边界并补齐回归测试
plan:
  version: 8
  current_step_id: step-4
  completed_step_ids:
    - step-1
    - step-2
  pending_step_ids:
    - step-4
    - step-5
changesets:
  proposed:
    - cs-19
  applied:
    - cs-18
evidence:
  test_run_ids:
    - test-88
  tool_event_ids:
    - tool-991
  artifact_refs:
    - diff:cs-18
    - report:security-scan-7
approvals:
  - approval-55
open_issues:
  - id: issue-local-3
    severity: medium
    text: Windows symlink test 尚未运行
resume:
  idempotency_key: resume-task-123-cp-7
  preconditions:
    - workspace_hash_unchanged
    - approval_still_valid
summary:
  completed: 已加入 Workspace boundary check
  next: 补 Windows 和 symlink 回归测试
integrity:
  previous_checkpoint_hash: sha256:...
  checkpoint_hash: sha256:...
```

### 2.1 必须字段

```text
checkpoint_id
task_id
sequence
state_version
workspace identity/hash
objective/spec ref
plan version/current step
changeset refs
evidence refs
approval refs
open issues
resume preconditions
integrity hash
```

### 2.2 摘要字段

摘要只用于导航：

- 不作为唯一完成证据；
- 不覆盖原始错误；
- 不修改历史 Artifact；
- 必须可以从每个主张回到 Evidence Ref。

---

## 3. 触发策略

Checkpoint 不需要每一步都创建。触发由风险和状态变化决定。

### 3.1 必须触发

- Apply ChangeSet 前；
- Apply ChangeSet 后；
- 高风险工具调用前；
- 用户 Approval 后；
- Compaction 前；
- Runtime / Provider / Tool Schema 切换前；
- 长任务暂停或退出前；
- 错误重试预算耗尽时；
- 人工接管前。

### 3.2 条件触发

- 完成一个 Plan 子图；
- 发现新依赖；
- Spec 或目标发生变化；
- Test 从通过变为失败；
- 上下文健康度下降；
- 成本或时间预算达到阈值。

### 3.3 不应触发

- 纯文本流式输出的每个 Chunk；
- 无状态、可重放的只读操作；
- 没有产生新状态或 Evidence 的内部思考步骤。

---

## 4. Reviewer 工作流

```text
Load Checkpoint
→ Validate Integrity
→ Verify State Is Current
→ Read Spec and Open Risks
→ Inspect Evidence Index
→ Fetch Required Original Artifacts
→ Run/Read Deterministic Verifiers
→ Produce Structured Verdict
→ Bind Verdict to Checkpoint Hash
```

### 4.1 Reviewer 最小输入

默认加载：

- Objective / Spec；
- 当前 Checkpoint；
- 相关约束；
- Open Issues；
- Evidence Index。

不默认加载：

- 完整执行对话；
- 全量工具日志；
- 原始 CoT；
- 不相关历史 Session。

### 4.2 Reviewer 按需读取

- 相关 Diff；
- 修改文件；
- Test Logs；
- Static Analysis；
- Tool Result；
- 前一个 Checkpoint；
- 失败样本；
- Approval 内容。

### 4.3 Structured Verdict

```yaml
review_id: review-cp-7
checkpoint_id: cp-0007
checkpoint_hash: sha256:...
verdict: changes_required
risk: R2
findings:
  - severity: high
    claim: Windows compatibility 未验证
    source_refs:
      - checkpoint:cp-0007:open_issues:issue-local-3
missing_evidence:
  - windows_symlink_test
required_actions:
  - run_windows_compatibility_suite
confidence: high
reviewer:
  type: independent_model
  model: deepseek-v4-pro
created_at: 2026-07-27T00:00:00Z
```

Verdict 不直接修改主状态；Orchestrator 根据 Policy 决定阻断、提醒、重试或请求用户。

---

## 5. 多轮审查

### 5.1 每轮审查对象

每次只审查相对于上一个已接受 Checkpoint 的增量：

```text
previous accepted checkpoint
+ current changesets
+ new evidence
+ changed plan/constraints
```

但 Reviewer 可以回溯旧证据，不能被限制为只读增量摘要。

### 5.2 Verdict 继承

旧 Verdict 只有在以下内容未变化时可继承：

```text
spec version
constraint versions
workspace base hash
relevant file hashes
tool schema fingerprint
runtime version
```

否则必须重新验证受影响部分。

### 5.3 级联失效

当某个步骤或 Artifact 改变时：

- 关联 Verdict 标记 `stale`；
- 下游 PlanStep 标记 `pending_review`；
- Approval 如果绑定旧 Hash 则失效；
- Resume 必须从新 Checkpoint 开始。

---

## 6. 恢复语义

### 6.1 Resume 前检查

```text
workspace exists
workspace hash matches or divergence is explained
runtime/provider versions are compatible
pending approvals are still valid
already-applied side effects are not repeated
required secrets are available but not serialized
```

### 6.2 幂等

每个可重试动作需要 `idempotency_key`。恢复时先查 Evidence：

```text
如果动作已成功提交
→ 不重复执行
如果动作状态未知
→ 进入人工确认或安全探测
```

### 6.3 不可恢复动作

外部邮件、支付、生产删除等不可逆动作不能只靠 Checkpoint 回滚。必须使用：

- 预生成 + 审批；
- Dry Run；
- 外部系统幂等键；
- 补偿事务；
- 人工变更流程。

---

## 7. Evidence 完整性

### 7.1 Hash Chain

Checkpoint 可以使用哈希链：

```text
checkpoint_hash = hash(
  canonical_checkpoint_without_hash
  + previous_checkpoint_hash
)
```

作用：

- 发现历史修改；
- 固定 Review 输入；
- 支持导出审计包。

它不能防止拥有写权限的人重写整个链，因此仍需 Git commit、签名或外部存证作为更强边界。

### 7.2 Redaction

不得写入 Checkpoint：

- API Key；
- Authorization；
- 密码；
- 完整私有文件正文；
- 原始 CoT。

使用脱敏摘要、Artifact ID 和 Hash。

---

## 8. 验证指标

### 8.1 Review Quality

```text
defect detection rate
false approval rate
false rejection rate
source citation accuracy
missing evidence detection
```

### 8.2 Recovery

```text
resume success rate
duplicate side-effect rate
stale approval rejection rate
rollback success rate
mean time to recover
```

### 8.3 Cost

```text
checkpoint storage
review prompt tokens
artifact fetch tokens
review latency
cost per prevented defect
```

### 8.4 对照实验

比较：

```text
full-history final review
summary-only checkpoint review
traceable checkpoint + on-demand evidence review
```

使用相同缺陷集和 Held-out 任务，报告质量、成本、延迟和恢复结果。

---

## 9. 边界与风险

- Snapshot 生成器可能漏字段；
- Evidence Index 可能指向错误版本；
- Hash 正确不代表内容真实；
- Reviewer 可能不读取关键 Artifact；
- 异步 Review 可能落后于主状态；
- Checkpoint 过密会增加存储和复杂度；
- Checkpoint 过稀会扩大恢复损失；
- 摘要可能隐藏不确定性。

因此必须有 Schema Validation、Integrity Check、Stale Detection、Evidence Fetch 和人工接管。

---

## 10. 结论

Checkpoint 的价值不在于“把长历史压成更短摘要”，而在于建立：

1. 可版本化状态；
2. 可恢复前置条件；
3. 可追溯 Evidence；
4. 与具体 Hash 绑定的 Review Verdict；
5. 状态变化后的级联失效；
6. 防止重复副作用的幂等语义。

Reviewer 可以使用更小的默认上下文，但每个结论都必须能回到原始 Diff、Test、Tool 和 Approval Evidence。小上下文是手段，可审计完成才是目标。
