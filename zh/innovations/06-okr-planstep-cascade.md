# PlanGraph：验收标准、依赖边与级联失效

> **证据等级：B（工程设计提案）**  
> 本文保留“扁平 Checklist 不足以驱动复杂任务”的核心判断，但修正早期数据模型：关联强度应属于依赖边，`parent_id` 与递归 `children` 不应成为双重真源，单个自然语言 `key` 也不足以证明完成。PlanGraph 的核心能力是显式表示目标、验收、依赖、证据和失效传播，而不是自动推断所有语义关系。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-06  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[05 Agent 可读文档结构](05-document-kv-cache.md)  
> **下一篇**：[07 风险与证据驱动的审查切换](07-review-switching.md)

---

## 摘要

复杂任务中的步骤通常存在：

- 层级分解；
- 先后依赖；
- 数据或接口依赖；
- 共享 Artifact；
- 验收条件；
- 风险与审批；
- Evidence；
- 变更后的失效关系。

一个 `text + status` 列表只能展示进度，不能可靠驱动执行和恢复。

PlanGraph 建模为：

```text
Nodes: Objective / Step / Milestone
Edges: hierarchy / requires / produces-consumes / validates / conflicts
Acceptance Criteria: structured assertions and verifiers
Evidence: tests, artifacts, approvals, tool results
Invalidation: changed inputs make downstream evidence and verdicts stale
```

级联引擎的首要动作不是自动重做，而是计算受影响范围、标记失效、要求重新验证，并由 Runtime 决定是否重执行。

---

## 1. 公开修正

### 1.1 不是“所有 Agent 都只有扁平 Plan”

不同产品可能有任务树、DAG、Issue Links、Workflow Graph 或隐式依赖。准确结论是：许多轻量 Plan API 只暴露内容、状态和优先级，难以表达复杂执行语义。

### 1.2 `association_strength` 应属于 Edge

同一个 Step 对不同下游节点的影响强度不同。把强度放在节点上无法表达：

```text
A 对 B 是强依赖
A 对 C 是弱参考
```

因此依赖类型、强度、来源和置信度必须属于 Edge。

### 1.3 避免 `parent_id` 与 `children[]` 双真源

持久层只保存一个方向，例如 `parent_id` 或单独 Hierarchy Edge；`children` 由查询计算。否则更新一处而忘记另一处会破坏图一致性。

### 1.4 单个 `key` 不等于可验证完成

自然语言 Key Result 可能模糊、复合或不可自动判断。每个 Step 应包含多个 Acceptance Criterion，并声明验证方式：

```text
test
schema
artifact existence
human approval
model review
manual observation
```

### 1.5 级联传播不能证明语义影响

图只能传播已声明关系。漏标、错标和隐式语义依赖仍需类型检查、测试、搜索或 Reviewer 发现。

---

## 2. 核心模型

### 2.1 Plan

```yaml
plan_id: plan-123
version: 8
task_id: task-88
objective: 实现基础 JWT 登录，不包含 RBAC、OAuth、2FA
status: active
root_node_id: objective-auth
created_at: 2026-07-27T00:00:00Z
updated_at: 2026-07-27T01:00:00Z
base_checkpoint_id: cp-7
```

Plan 必须版本化。任何结构、Scope 或验收变化生成新 Version。

### 2.2 Node

```yaml
node_id: step-token-endpoint
kind: step
objective: 实现登录端点并返回访问令牌
status: in_progress
risk: R2
owner: executor-main
acceptance_criteria:
  - criterion_id: ac-http-200
    assertion: 合法账号返回 200
    verifier:
      type: test
      ref: test_login_success
  - criterion_id: ac-invalid-401
    assertion: 错误密码返回 401
    verifier:
      type: test
      ref: test_login_invalid_password
expected_outputs:
  - artifact: src/auth/login.py
constraints:
  - no-rbac
  - no-oauth
evidence_refs: []
```

### 2.3 Edge

```yaml
edge_id: edge-schema-to-login
from: step-user-schema
to: step-token-endpoint
type: requires
strength: strong
source:
  type: planner
  ref: plan-generation-8
confidence: 0.91
condition: null
status: active
```

Edge 类型建议：

| 类型 | 含义 |
| --- | --- |
| `contains` | 层级分解 |
| `requires` | 下游执行前需要上游完成 |
| `consumes` | 使用上游 Artifact |
| `validates` | 某节点验证另一个节点 |
| `conflicts` | 两节点不能同时成立 |
| `related` | 弱关联，只提示 Review |

### 2.4 Evidence Link

```yaml
link_id: ev-step-token-1
node_id: step-token-endpoint
evidence_id: test-run-991
supports:
  - ac-http-200
  - ac-invalid-401
artifact_hash: sha256:...
plan_version: 8
status: valid
```

Evidence 必须绑定 Plan Version、Artifact Hash 和 Criterion。输入变化后可判定是否失效。

---

## 3. 状态机

Node 状态：

```text
pending
ready
in_progress
blocked
awaiting_approval
awaiting_verification
completed
stale
cancelled
```

### 3.1 `completed` Gate

只有所有必需 Acceptance Criteria 都有有效 Evidence，并满足依赖和审批时，才能完成。

```text
all required criteria satisfied
AND all strong prerequisites valid
AND required approvals active
AND no blocking issue
```

模型自然语言声明“已完成”不改变状态。

### 3.2 `stale`

以下情况使节点或 Evidence 失效：

- 上游 Artifact Hash 变化；
- Acceptance Criterion 修改；
- Plan Version 更新；
- Tool Schema 或 Runtime 版本变化影响结果；
- Approval 绑定的 Diff 变化；
- 依赖边新增或增强。

---

## 4. 图约束

### 4.1 层级图

`contains` 应形成树或森林：

- 每个节点最多一个层级父节点；
- 不允许层级环；
- 根目标明确。

### 4.2 执行依赖图

`requires / consumes / validates` 默认要求 DAG。创建或更新 Edge 时运行拓扑检查。

循环可能表示：

- 规划错误；
- 两步骤应合并；
- 需要迭代 Fixed Point Workflow；
- 依赖类型标错。

不要静默忽略。

### 4.3 Integrity Rules

- Node ID 唯一；
- Edge 引用存在节点；
- Criterion ID 唯一；
- Completed Node 不得缺少必需 Evidence；
- Cancelled Node 不得作为有效强依赖；
- Evidence Hash 和 Plan Version 必须可验证。

---

## 5. 级联失效算法

### 5.1 输入

```text
changed nodes
changed artifacts
changed acceptance criteria
changed edges
changed constraints
```

### 5.2 传播

```python
def invalidate(graph, changes):
    queue = direct_impacted_nodes(changes)
    visited = set()

    while queue:
        node = queue.pop()
        if node in visited:
            continue
        visited.add(node)

        mark_relevant_evidence_stale(node, changes)
        if node.status == "completed":
            node.status = "stale"

        for edge in graph.outgoing(node):
            if edge.status != "active":
                continue
            if edge.type in {"requires", "consumes", "validates"}:
                queue.push(edge.to)
            elif edge.type == "related":
                create_review_notice(edge.to, reason=changes)

    return impact_report(visited)
```

### 5.3 不是自动重执行

传播结果是 Impact Report：

```yaml
changed:
  - step-user-schema
invalidated:
  - node: step-token-endpoint
    evidence:
      - test-run-991
    reason: consumes changed schema artifact
review_recommended:
  - step-api-docs
blocked:
  - step-integration-tests
```

Orchestrator 根据风险、预算和用户审批选择：

- 自动重跑确定性测试；
- 重新执行 Step；
- 请求独立 Review；
- 请求用户决定；
- 延期并记录风险。

---

## 6. 隐式依赖发现

声明图永远不完整。Runtime 可以从以下证据提议新 Edge：

- Import / Call Graph；
- LSP References；
- Type Errors；
- Test Failures；
- Shared Database Schema；
- Artifact Read/Write Trace；
- Reviewer Finding。

新关系标记来源和置信度：

```yaml
source:
  type: lsp_reference
confidence: 1.0
status: proposed
```

高置信确定性关系可以自动加入；模型推断关系默认需要 Review。

---

## 7. Scope 与 Change Request

PlanGraph 不应在发现依赖后静默扩大产品范围。

区分：

```text
Implementation Dependency：完成已批准目标所必需
Product Scope Expansion：增加新的用户能力或非目标
```

后者生成 Change Request，进入 I-08 的范围治理。

---

## 8. 并发与多 Agent

### 8.1 单一 Loop Authority

只有 Orchestrator 可以修改正式 Plan 状态。子 Agent 提交：

```text
proposed node update
proposed edge
artifact
evidence
blocker
```

### 8.2 乐观并发

更新请求包含：

```text
plan_id
expected_plan_version
patch
```

Version 不匹配则拒绝并重新读取，避免两个 Agent 覆盖状态。

### 8.3 Workspace 隔离

并行写入需要独立 Worktree/Workspace 和明确合并策略。PlanGraph 本身不解决文件冲突。

---

## 9. API 示例

```text
POST /plans/{id}/nodes
POST /plans/{id}/edges
POST /plans/{id}/changes
POST /plans/{id}/evidence
POST /plans/{id}/impact-analysis
POST /plans/{id}/verify
```

所有写操作要求 `expected_plan_version` 和 Idempotency Key。

---

## 10. 评测

### 10.1 图质量

```text
dependency precision / recall
cycle detection
orphan node rate
implicit dependency discovery
```

### 10.2 执行质量

```text
stale evidence escape rate
incorrect completed status
rework steps
first-pass success
resume success
```

### 10.3 成本

```text
impact analysis latency
revalidation tokens
unnecessary re-execution
human review time
```

### 10.4 对照

比较：

```text
flat checklist
hierarchical tree
PlanGraph + evidence invalidation
```

使用包含中途需求变化、接口变化和隐式依赖的 Held-out 任务。

---

## 11. 边界与风险

- Planner 会漏标或错标依赖；
- 图维护成本可能超过小任务收益；
- 稠密图会造成大范围失效；
- 自动发现关系可能产生误报；
- Acceptance Criteria 可能不可验证；
- Evidence 可能来自错误版本；
- 多 Agent 并发会产生状态冲突；
- DAG 不适合所有迭代流程。

简单任务应允许退化为轻量 Checklist，不强制建图。

---

## 12. 结论

PlanGraph 的价值不是多加五个字段，而是建立可计算契约：

1. Node 表示目标和步骤；
2. Edge 表示具体关系、强度、来源和置信度；
3. Acceptance Criteria 连接 Verifier；
4. Evidence 绑定 Plan Version 和 Artifact Hash；
5. 上游变化触发级联失效和 Impact Report；
6. Runtime 决定重验、重做、审批或延期；
7. 图完整性、并发和恢复都可验证。

复杂任务需要图，但图不替代测试、类型系统、Policy 和人的产品判断。
