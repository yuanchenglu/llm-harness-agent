# 范围治理：区分产品范围扩张与实现依赖发现

> **证据等级：B（工程设计提案）**  
> 本文修正早期“范围蔓延是两种病、所有现有方案都混淆二者”的绝对表述。更准确的工程划分是：一类变化增加或改变已批准的用户价值范围，另一类变化是在实现已批准目标时发现必要依赖。两者都需要记录、评估和控制，但审批阈值不同。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-08  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[07 风险与证据驱动的审查切换](07-review-switching.md)  
> **下一篇**：[09 Skills 自进化闭环](09-skills-self-evolution.md)

---

## 摘要

用户说“加一个基础 JWT 登录”，执行中可能出现两类变化：

### A. Product Scope Expansion

增加新的用户能力：

```text
RBAC
OAuth
密码找回
2FA
多租户
```

这些内容即使技术上相关，也超出基础登录的已批准范围，需要 Change Request 和用户决定。

### B. Implementation Dependency Discovery

为完成基础登录必须处理：

```text
密码 Hash
Token 签名配置
认证中间件
错误处理
必要测试
```

这些通常不改变用户目标，但会改变工作量、文件范围和风险，需要 Impact Analysis；达到阈值时仍需审批。

可靠范围治理不是“一律禁止新增步骤”，也不是“技术上合理就自动做”，而是使用可版本化 Scope Contract、Change Proposal、影响分析和批准策略。

---

## 1. 公开修正

### 1.1 不使用“两个病理”的隐喻作为模型

范围变化可能同时包含产品、技术、安全、合规和运维因素。本文使用可操作类型，而不是医学隐喻：

```text
scope expansion
implementation dependency
requirement clarification
corrective work
risk mitigation
```

### 1.2 用户未写“不做什么”不代表 Agent 可以自由扩张

默认规则应是：

> 只执行实现已确认目标和验收标准所必需的最小工作；相邻功能默认不在范围内。

负向边界有帮助，但不能把列完所有非目标的责任转嫁给用户。

### 1.3 实现依赖也不是自动批准

即使某项工作是必要依赖，如果它：

- 改变架构；
- 增加外部服务；
- 扩大权限；
- 修改生产数据；
- 显著增加时间或成本；
- 降低兼容性；

仍需升级为 Change Request。

### 1.4 删除未经证据支持的比例

早期示例中的“某类任务 73% 的蔓延来自某功能”等数字没有可复现数据来源，不再保留。

---

## 2. Scope Contract

```yaml
scope_id: auth-jwt-v1
version: 3
objective: 为现有 Web 应用增加基础账号密码登录
in_scope:
  - 登录端点
  - JWT 签发和验证
  - 密码安全存储
  - 认证中间件
  - 单元和集成测试
non_goals:
  - RBAC
  - OAuth
  - 密码找回
  - 2FA
  - 多租户
acceptance_criteria:
  - 合法用户可登录并获得 Token
  - 错误密码返回 401
  - 受保护端点拒绝无效 Token
constraints:
  - 使用现有数据库
  - 不增加外部身份服务
change_budget:
  max_files_without_approval: 8
  max_estimated_hours_without_approval: 4
  external_dependency_requires_approval: true
  permission_change_requires_approval: true
owner: user-or-product-owner
status: approved
```

### 2.1 Objective

描述用户价值，不是实现手段。

### 2.2 In Scope

列出完成目标已明确包含的能力。

### 2.3 Non-goals

列出高概率相邻功能。无需穷举整个世界，只覆盖当前任务常见扩张方向。

### 2.4 Acceptance Criteria

范围是否完成由验收标准决定，而不是步骤数量。

### 2.5 Constraints

包括技术、时间、平台、兼容和权限边界。

### 2.6 Change Budget

定义哪些小变化可由 Runtime 自动处理，哪些必须升级审批。

---

## 3. 变化分类

### 3.1 Clarification

不改变目标，只消除歧义。

示例：Token 有效期是 30 分钟还是 24 小时。

### 3.2 Implementation Dependency

完成已批准 Acceptance Criterion 所必需。

判定问题：

```text
如果不做该项，是否仍能诚实地满足已批准验收标准？
```

如果答案是否定，可能是必要依赖。

### 3.3 Corrective Work

修复由当前改动引入或暴露的错误。

需要区分：

- 本次变更引入的回归：应修复；
- 既有无关缺陷：记录 Issue，默认不扩入当前范围。

### 3.4 Risk Mitigation

为了使已批准实现达到最低安全、数据完整性或合规要求。

高影响 Risk Mitigation 仍需审批。

### 3.5 Product Scope Expansion

新增用户能力、平台、集成或产品行为。默认需要产品 Owner 批准。

### 3.6 Refactor Opportunity

“顺手重构”“代码更漂亮”不是必要依赖。除非验收、安全或可维护性 Gate 明确要求，否则记录为后续项。

---

## 4. Change Proposal

```yaml
change_id: change-auth-7
scope_version: 3
type: implementation_dependency
description: 增加密码 Hash 库和迁移已有明文密码
reason: 无安全存储无法满足基础账号密码登录
trigger:
  node_id: step-password-storage
impact:
  files: 5
  data_migration: true
  external_dependency: argon2
  permissions_changed: false
  estimated_effort_hours: 6
  rollback_complexity: medium
alternatives:
  - name: 仅支持新用户
    tradeoff: 旧用户无法登录
  - name: 首次登录时渐进迁移
    tradeoff: 实现复杂度增加
recommendation: 请求用户批准迁移策略
approval_required: true
status: proposed
```

Change Proposal 必须说明：

```text
变化类型
为什么需要
与 Acceptance Criterion 的关系
影响范围
风险
成本
备选方案
不做的后果
审批要求
```

---

## 5. 决策矩阵

| 条件 | 默认动作 |
| --- | --- |
| 不改变用户能力，低风险，预算内，可逆 | 自动纳入并记录 |
| 必要依赖但超出文件/时间预算 | 暂停并请求批准 |
| 增加外部依赖 | 请求批准 |
| 改变权限、安全或数据 | 高等级 Review + 批准 |
| 新增用户能力 | Product Scope Change |
| 既有无关缺陷 | 建 Issue，不默认修复 |
| 无法判断是否必要 | 标记 Unknown，请求决策 |

---

## 6. 反向澄清

澄清应聚焦高影响边界，而不是罗列所有可能功能。

好的问题：

```text
基础登录是否只包含账号密码 + JWT，不包含 RBAC、OAuth、找回密码和 2FA？
```

更好的系统行为是给出默认最小范围：

```text
我将按“账号密码登录、JWT、认证中间件和必要测试”执行；RBAC、OAuth、找回密码和 2FA 默认不做。
```

用户只需纠正默认值，而不是从空白表单定义一切。

### 6.1 何时必须问

- 选项会改变数据模型；
- 选项难以回滚；
- 成本差异显著；
- 涉及合规或安全；
- 不同答案产生不同产品价值。

### 6.2 何时不应问

- 可以安全选择项目已有惯例；
- 有确定性配置或文档证据；
- 低风险、可逆、预算内；
- 问题只是实现细节且不影响用户价值。

---

## 7. PlanGraph 集成

I-06 的 PlanGraph 将变化映射到：

```text
new node
new edge
changed acceptance criterion
changed constraint
invalidated evidence
```

流程：

```text
Discovery
→ Change Proposal
→ Classify
→ Impact Analysis
→ Approve / Reject / Defer
→ New Scope and Plan Version
→ Invalidate affected Evidence
```

未经批准的 Scope Expansion 不得进入正式 Plan。

---

## 8. 用户打断控制

频繁弹窗会破坏 Agent 价值。使用三档策略：

### Auto-accept

低风险、必要、预算内、可逆，记录到 Timeline。

### Batch Review

多个中等影响变化累积到 Checkpoint，一次展示：

```text
新增 3 个必要实现步骤
预计增加 2 个文件和 40 分钟
不改变产品范围
```

### Immediate Approval

高风险、范围扩张、不可逆、外部副作用或预算超限，立即暂停。

---

## 9. Scope Drift Detection

运行时比较：

```text
approved scope
current plan
actual changed files
actual tools/dependencies
current artifacts
```

异常信号：

- 修改未关联任何 In-scope Criterion 的文件；
- 新增依赖但无 Change Proposal；
- Plan 出现 Non-goal 节点；
- 工具权限扩大；
- 文件数、成本或时间超过预算；
- 产出新增未批准用户能力。

信号触发 Review，不自动证明违规。

---

## 10. Scope Verdict

```yaml
verdict_id: scope-review-11
scope_version: 3
plan_version: 8
status: changes_required
findings:
  - type: product_scope_expansion
    node: step-rbac
    reason: RBAC 明确属于 non_goals
    required_action: remove_or_request_approval
  - type: implementation_dependency
    node: step-password-hash
    reason: 支持基础安全登录所必需
    approval: required_due_to_data_migration
```

Verdict 必须引用 Scope、Plan 和 Evidence 版本。

---

## 11. 评测

### 11.1 范围准确性

```text
unauthorized feature additions
missed necessary dependencies
incorrect change classification
scope drift detection precision / recall
```

### 11.2 任务效果

```text
first-pass acceptance
rework
user corrections
completion time
cost per successful task
```

### 11.3 交互成本

```text
clarification turns
approval interruptions
batched decisions
unnecessary questions
```

### 11.4 对照

比较：

```text
no scope contract
prompt-only scope statement
scope contract + change control
```

使用中途发现依赖、既有缺陷、相邻功能诱惑和高风险变化的 Held-out 任务。

---

## 12. 边界与风险

- Scope Contract 可能不完整；
- Agent 会误判“必要”；
- Change Budget 可能设置过严或过松；
- 用户可能批准错误扩张；
- 实现中发现的安全问题可能必须立即处理；
- 过多 Change Proposal 会增加流程成本；
- 过少审批会造成静默漂移；
- 项目惯例本身可能过时。

需要 Unknown 状态、人工覆盖、审计和事后复盘。

---

## 13. 结论

范围治理不是简单限制步骤数，也不是要求用户预先列出所有“不做什么”。

可靠机制需要：

1. 用 Scope Contract 固定目标、In-scope、Non-goals、验收、约束和 Change Budget；
2. 区分产品范围扩张、实现依赖、纠错、风险缓解和重构机会；
3. 对每个变化生成 Impact 和备选方案；
4. 低风险预算内变化自动记录，中等变化批量审查，高风险变化立即审批；
5. 更新 Scope/Plan Version 并级联失效旧 Evidence；
6. 用范围准确性、任务效果和交互成本共同评估。

目标不是让 Plan 永远不变，而是让每一次变化都有类型、理由、影响、权限和可追溯决定。
