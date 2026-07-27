# Agent 免疫系统：从 Prompt 违规到可审计的系统加固

> **证据等级：B（工程设计提案）**  
> 本文不再把“长对话中必然遗忘 Prompt”写成 Transformer 物理定律，也不再宣称自动生成 Skill 可以把遵守率提升到 100%。核心问题是：当 Agent 发生可复现违规时，Harness 如何把一次失败转化为可审计、可测试、可回滚的系统改进。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-01  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **下一篇**：[02 大脑主动驱动小脑](02-bidirectional-agent.md)

---

## 摘要

Agent 可能因为指令冲突、上下文遗漏、错误检索、工具结果噪音、模型行为波动或 Runtime 缺少强制检查而违反约束。

传统修复通常是：

```text
发现一次错误
→ 在 System Prompt 里再加一句提醒
→ Prompt 越来越长
→ 同类错误仍可能出现
```

“Agent 免疫系统”应被定义为一条系统加固闭环：

```text
违规事件
→ 固定证据
→ 根因分类
→ 提议修复
→ 选择正确控制层
→ 测试与审批
→ 小范围启用
→ 监控复发与副作用
→ 保留回滚
```

关键原则：

> 不是每次失败都生成 Skill；不可妥协的安全约束优先变成 Runtime Policy、Schema、测试或权限规则。Skill 只适合可复用、可解释、需要模型参与的流程知识。

---

## 1. 公开修正

### 1.1 Prompt 违规不等于“模型遗忘”

观察到约束没有被遵守时，至少存在以下可能原因：

- 约束没有进入本轮请求；
- 约束与更新后的用户指令冲突；
- 压缩或检索遗漏约束；
- 模型看到了约束但选择了错误动作；
- Tool Schema 诱导了错误参数；
- Runtime 没有阻止违规副作用；
- Verifier 没有发现错误；
- 约束本身模糊、不可执行或互相矛盾。

没有证据时，不能统一归因于“注意力稀释”或“Prompt 遗忘”。

### 1.2 轮数增加不必然导致遵守率单调下降

不同模型、任务、Prompt 布局和工具链可能呈现不同曲线。重新检索规则、重建上下文、切换独立 Session 或下沉 Runtime Policy 都可能恢复质量。

### 1.3 自动生成 Skill 不是天然修复

错误 Skill 可能成为持久化供应链风险：

```text
恶意或错误上下文
→ 生成 Skill
→ 跨任务自动加载
→ 权限扩大或错误流程被系统化
```

因此 Skill 必须经过来源记录、权限限制、测试、审批、版本化、有效期和回滚。

### 1.4 “无人填补的唯一创新”不成立

行业中已经存在 Policy、Guardrail、Verifier、Hooks、Skills、Memory、Incident Learning 和自动规则提议等不同机制。本文的价值不在于宣称唯一，而在于把这些能力连接成一条严格的失败加固闭环。

---

## 2. 违规事件模型

每次违规都保存结构化事件：

```yaml
incident_id: inc-20260727-001
task_id: task-123
constraint_id: workspace-boundary@3
expected: 只允许修改批准的 Workspace
observed: 尝试写入 ../shared/config.yaml
blocked: true
source_refs:
  - tool-call-882
  - policy-event-991
model: deepseek-v4-pro
runtime_version: 0.1.1
context_fingerprint: sha256:...
severity: critical
status: investigating
```

至少记录：

```text
incident_id
task_id
constraint_id / requirement_ref
expected behavior
observed behavior
model/provider/runtime version
context fingerprint
tool and artifact refs
whether side effect occurred
severity
```

不记录完整私有 Prompt、API Key 或原始 CoT。

---

## 3. 根因分类

### 3.1 Context Failure

- 约束未进入请求；
- Retrieval 漏召回；
- Compaction 丢失；
- 旧摘要覆盖新事实；
- 错误 Session 被恢复。

候选修复：Context Compiler、Constraint Registry、Checkpoint、Retrieval Test。

### 3.2 Model Compliance Failure

- 约束存在且无冲突，但模型仍生成违规建议；
- 模型错误选择工具或参数；
- 模型对风险判断错误。

候选修复：更明确的指令、结构化输出、独立 Reviewer、模型路由，但高风险动作仍应由 Runtime 阻断。

### 3.3 Runtime Enforcement Gap

- 应该拒绝的路径被允许；
- Approval 可被绕过；
- stale Diff 仍可 Apply；
- 不可逆工具没有单独权限。

候选修复：Policy、Sandbox、Schema、状态机、幂等和 Hash 校验。

### 3.4 Requirement Defect

- 约束模糊；
- 两条规则冲突；
- 用户目标已经变化；
- 完成标准不可验证。

候选修复：澄清、版本化 Spec、冲突解决和用户审批。

### 3.5 Verifier Failure

- 测试覆盖不足；
- Reviewer 只读摘要而无来源；
- 失败被错误分类为成功；
- Acceptance Hint 对开发集过拟合。

候选修复：Held-out Tests、Evidence Trace、Verifier 多样性和失败样本复核。

---

## 4. 修复层选择

修复必须进入正确层级：

| 问题 | 首选控制层 | 不推荐 |
| --- | --- | --- |
| 禁止写出 Workspace | Runtime Policy | 只加 Prompt 提醒 |
| 输出必须符合 JSON Schema | Schema Verifier | 依赖模型自述正确 |
| 修改前必须审批 | ChangeSet 状态机 | Skill 清单 |
| 某框架升级固定步骤 | Governed Skill | 硬编码到核心 Runtime |
| 项目使用 Python 3.11 | Environment Check + Project Policy | 每轮重复长提示 |
| 用户偏好注释风格 | Project Memory / Style Rule | 系统级安全策略 |

判定原则：

```text
能用确定性代码验证的，不只依赖 Prompt
涉及副作用的，不只依赖模型判断
需要跨任务复用但有情境变化的，才考虑 Skill
```

---

## 5. 加固闭环

### 5.1 Detect：发现

来源包括：

- Runtime Policy Block；
- Test Failure；
- Reviewer Verdict；
- 用户纠正；
- Rollback；
- Incident Replay；
- 任务失败聚类。

### 5.2 Preserve：固定证据

保存：

```text
Diff Hash
Tool Call ID
Test Run ID
Policy Event
Artifact Hash
Runtime / Model Version
```

### 5.3 Diagnose：根因分类

不得让同一个执行 Agent 仅凭自然语言自判根因。优先使用确定性证据；模型诊断必须标记置信度和备选解释。

### 5.4 Propose：提议修复

修复类型：

```text
policy_patch
test_patch
schema_patch
context_rule
skill_proposal
documentation_fix
model_route_change
```

### 5.5 Validate：验证

每个修复至少包含：

- 能复现原事故的失败测试；
- 修复后通过测试；
- 不相关任务回归测试；
- 权限和副作用检查；
- 性能与成本变化；
- 回滚步骤。

### 5.6 Approve：审批

审批强度按影响范围：

| 范围 | 审批 |
| --- | --- |
| 当前任务临时规则 | 用户或任务 Owner |
| 当前项目 Skill / Policy | 项目 Maintainer |
| 全局 Runtime Policy | 安全负责人 + Maintainer |
| 跨用户自动 Skill | 默认禁止，需更高等级审核 |

### 5.7 Canary：小范围启用

先限定：

```text
workspace
project
user
model
runtime version
time window
```

观察误拦截、漏拦截、成本和任务成功率，再决定扩大范围。

### 5.8 Monitor：监控复发与副作用

记录：

```text
incident recurrence rate
false-positive block rate
false-negative rate
rollback rate
first-pass success
human override
cost per successful task
```

### 5.9 Rollback：回滚

所有自动加固项必须版本化，可禁用、可回滚，并保留原事故与修复关联。

---

## 6. Governed Skill 规范

```yaml
skill_id: python-migrate-pyproject
version: 1.2.0
origin:
  incident_ids: []
  successful_task_ids:
    - task-456
scope:
  workspaces:
    - project-a
permissions:
  tools:
    - read_file
    - propose_patch
  network: false
  write_requires_approval: true
tests:
  - fixture-basic
  - fixture-custom-build
reviewed_by:
  - maintainer@example
expires_at: 2026-10-27
content_hash: sha256:...
rollback_to: 1.1.0
```

要求：

- 默认最小 Scope；
- 默认最小权限；
- 自动生成后默认禁用；
- 用户能查看内容和来源；
- 跨项目启用需重新审批；
- 修改内容后 Hash 和审批失效；
- 长期未命中或频繁失败时自动建议停用。

---

## 7. 验证设计

### 7.1 数据集

包含：

- 已知历史违规；
- 相似但不应触发的负样本；
- 新项目 Held-out 样本；
- 恶意 Prompt Injection；
- 冲突约束；
- 版本升级场景。

### 7.2 指标

```text
incident detection precision / recall
root-cause classification accuracy
policy false positive / false negative
skill trigger precision / recall
regression pass rate
recurrence rate
human override rate
rollback success rate
```

### 7.3 对照组

比较：

```text
只增加 Prompt
vs.
Prompt + Runtime Policy / Test / Governed Skill
```

必须报告副作用，不能只报告原事故是否消失。

---

## 8. 边界与风险

- Reviewer 也可能误判；
- 自动根因分析可能把相关性当因果；
- 过度加固会造成大量误拦截；
- Skill 匹配可能过宽或过窄；
- 安全策略可能与用户目标冲突；
- 历史事故可能已不适用于新版本；
- 自动学习可能被 Prompt Injection 污染。

因此系统必须保留人工接管、证据回放、Scope 限制、有效期和回滚。

---

## 9. 结论

Agent 免疫系统不是“模型忘了一次，就自动生成一个 Skill”。

更可靠的闭环是：

1. 把违规固定成可复现 Incident；
2. 区分 Context、Model、Runtime、Requirement 和 Verifier 根因；
3. 把修复放到正确控制层；
4. 对持久化 Skill 做供应链级治理；
5. 通过测试、审批、Canary、监控和回滚证明改进有效。

真正的自进化不是系统越来越复杂，而是同类失败复发率下降，同时误拦截、权限风险和维护成本保持可控。
