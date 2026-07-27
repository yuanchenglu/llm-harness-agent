# 风险与证据驱动的审查切换

> **证据等级：B（工程设计提案）**  
> 本文修正早期“审查深度 = f(KV Cache 占用, Plan 复杂度)”的单一模型。上下文长度或 Cache 占用不能直接代表 Reviewer 判断力，更严格的 Prompt 也不保证补偿质量下降。审查策略应由风险、可逆性、影响范围、证据完整性、任务新颖度和上下文健康度共同决定。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-07  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[06 OKR 增强型 PlanStep + 级联修正引擎](06-okr-planstep-cascade.md)  
> **下一篇**：[08 两层面范围蔓延治理](08-scope-creep.md)

---

## 摘要

固定审查流程会在两端失效：

- 对低风险、小改动执行昂贵终审，浪费时间和 Token；
- 对高风险、不可逆或证据不足的改动执行轻量审查，产生虚假安全感。

正确问题不是“上下文多长时要更仔细”，而是：

> 当前动作失败后会造成什么后果，现有证据能否证明它正确，失败是否可恢复，是否需要独立模型或人类批准？

本文提出一个可执行的 Review Router：

```text
Change / Decision
→ Risk Classification
→ Evidence Completeness
→ Reversibility and Blast Radius
→ Context Health
→ Review Mode
→ Verdict + Evidence
```

---

## 1. 公开修正

### 1.1 Cache 占用不是 Reviewer 能力测量器

高 Token 占用可能与复杂任务相关，但不能推出：

```text
上下文 128K
→ Reviewer 质量只剩 40%
```

实际质量受模型、任务、相关信息位置、工具证据、摘要质量、Prompt、采样参数和 Reviewer 独立性共同影响。

### 1.2 更严格的 Prompt 不一定补偿上下文问题

当上下文存在错误、冲突或噪音时，要求模型“更仔细”可能只增加输出长度，而不是提升错误发现率。有效措施可能是：

- 缩小审查输入；
- 重新读取原始 Artifact；
- 使用独立 Session；
- 运行确定性测试；
- 要求人类审批；
- 阻止不可逆动作。

### 1.3 审查深度不是单调变量

“更深”可能意味着不同动作：

```text
更多测试
独立 Reviewer
读取更多原始证据
增加安全扫描
扩大人工审批
执行 Canary
延迟发布
```

不能只用一段更长的 Review Prompt 表示审查升级。

---

## 2. 审查路由输入

### 2.1 风险等级

| 等级 | 示例 | 默认要求 |
| --- | --- | --- |
| R0 | 文案、格式、无副作用分析 | 自动验证或轻审查 |
| R1 | 单文件可逆改动 | 测试 + Diff Review |
| R2 | 多文件、接口、配置变化 | 独立 Reviewer + 回归测试 |
| R3 | 数据迁移、权限、安全、部署 | 专项验证 + 人工批准 |
| R4 | 不可逆生产副作用 | 默认拒绝或严格变更流程 |

### 2.2 Blast Radius

至少考虑：

```text
files
modules
services
users
data
permissions
external systems
```

### 2.3 Reversibility

```text
fully_reversible
reversible_with_backup
partially_reversible
irreversible
unknown
```

未知不能按低风险处理。

### 2.4 Evidence Completeness

审查输入不应只包含模型摘要。检查：

- Spec / Acceptance Criteria；
- Diff / Artifact Hash；
- Test Result；
- Static Analysis；
- Tool Evidence；
- Approval；
- Known Failure；
- Rollback Plan。

### 2.5 Novelty

- 是否第一次修改该模块；
- 是否使用新 Provider / Tool / Dependency；
- 是否超出训练或项目惯例；
- 是否存在未知 Schema 或协议。

### 2.6 Context Health

上下文健康度是一个输入，而不是审查质量本身：

```text
source coverage
conflicting instructions
stale summaries
missing artifacts
retrieval confidence
context size
compaction count
```

出现异常时，优先重建 Review Context，而不是简单提高 Prompt 严格度。

---

## 3. Review Modes

### M0：No Additional Review

适用于：

- 无副作用；
- 确定性格式转换；
- 自动测试已完全覆盖；
- 结果可立即丢弃。

仍需记录为什么跳过审查。

### M1：Automated Verification

使用：

```text
schema validation
unit tests
lint / typecheck
hash / path checks
policy checks
```

确定性验证优先于模型自述。

### M2：Light Independent Review

独立 Reviewer 读取：

- 原始目标；
- Diff；
- 关键文件；
- 测试结果；
- 开放风险。

不携带执行 Agent 的完整推理历史。

### M3：Deep Multi-Dimensional Review

按维度拆分：

```text
correctness
security
compatibility
data integrity
performance
operability
rollback
```

可以由不同 Verifier 或 Reviewer 执行，并形成独立 Verdict。

### M4：Human Approval / Change Management

适用于：

- 生产数据；
- 权限扩大；
- 不可逆外部动作；
- 安全策略变化；
- 高影响迁移。

模型审查不能替代授权责任。

### M5：Reject or Defer

证据不足、无法回滚或风险不可接受时，正确结果可能是停止，而不是继续生成更多审查文字。

---

## 4. 路由规则

示例策略：

```python
def choose_review_mode(change):
    if change.irreversible and change.risk >= R3:
        return M4
    if change.evidence_missing or change.context_health == "degraded":
        return M5
    if change.security_sensitive or change.data_migration:
        return M3
    if change.blast_radius > 1 or change.novelty == "high":
        return M2
    if change.has_deterministic_verifier:
        return M1
    return M2
```

真实实现需要版本化 Policy，而不是散落在 Prompt 中。

### 4.1 不对称阈值

不同错误代价不同：

- 低风险改动被过审：成本增加；
- 高风险改动被漏审：可能造成事故。

因此高风险分类采用保守阈值；不确定时升级而不是降级。

### 4.2 Review Context Rebuild

以下情况触发重建：

- 关键来源缺失；
- Compaction 后无法追溯；
- Spec 与 Diff 冲突；
- Reviewer 输入包含过期 Snapshot；
- 工作区 Hash 已变化；
- Provider 或 Tool Schema 变化。

重建后只加载与审查相关的原始证据。

---

## 5. Verdict Schema

```yaml
review_id: review-123
mode: M3
risk: R3
scope:
  files: 8
  services: 2
evidence:
  spec: spec-8
  diff_hash: sha256:...
  test_runs:
    - test-991
findings:
  - severity: high
    type: rollback_gap
    source_ref: diff:src/migrate.py:88
verdict: changes_required
confidence: medium
missing_evidence:
  - windows_compatibility_test
reviewer:
  type: independent_model
  model: deepseek-v4-pro
created_at: 2026-07-27T00:00:00Z
```

Verdict 必须引用具体证据和位置，不能只写“看起来没问题”。

---

## 6. 验证指标

### 6.1 质量

```text
escaped defect rate
review precision / recall
severity-weighted defect detection
false approval rate
false rejection rate
```

### 6.2 成本与速度

```text
review tokens
review latency
human review minutes
cost per prevented defect
```

### 6.3 恢复与安全

```text
rollback availability
rollback success
policy block rate
unreviewed high-risk action count
```

### 6.4 实验设计

比较：

```text
fixed review mode
vs.
risk/evidence review router
```

使用 Held-out 变更集，盲标真实缺陷，报告每个风险等级的混淆矩阵。

---

## 7. 边界与风险

- 风险分类器会误判；
- Reviewer 之间可能共享相同盲点；
- 更多 Reviewer 不一定带来独立信息；
- 自动测试覆盖有限；
- 人工审批也可能流于形式；
- 过度审查会降低交付速度；
- Review Router 本身需要版本、测试和审计。

必须保留手动升级、跳过理由、Policy 版本和事后复盘。

---

## 8. 结论

可靠审查不是固定 Prompt，也不是由 KV Cache 占用决定的四档阈值。

审查切换应围绕：

1. 失败后果；
2. 影响范围；
3. 可逆性；
4. Evidence 完整性；
5. 任务新颖度；
6. Context 健康度；
7. 是否需要独立模型或人类授权。

系统的目标不是“每次都审得最深”，而是在可接受成本下，让高风险错误更难逃逸，并让每个 Verdict 都能回到原始证据。
