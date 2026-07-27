# 稳定约束与可压缩历史分区：Context Compiler，而不是“KV Cache 免死区”

> **证据等级：B（工程设计提案）**  
> 本文修正早期“把约束放进 KV Cache 前缀即可物理保证不丢、保证遵守”的表述。Provider Prefix Cache、Harness 上下文压缩和模型约束遵守是三个不同问题，必须分别设计和测量。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-04  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[03 注意力预算管理](03-attention-budget.md)  
> **下一篇**：[05 文档稳定前缀结构](05-document-kv-cache.md)

---

## 摘要

长任务会产生用户约束、项目规则、工具轨迹、测试结果、历史讨论和临时信息。它们的生命周期不同，不应该由同一套压缩策略处理。

正确的架构原则是：

> 把必须长期保留的稳定约束、需要追加的证据、当前活跃工作集和可外部检索的历史分区，并为每一类信息定义更新、压缩、失效和验证规则。

这是一项 **Context Compiler** 设计，不是 KV Cache 的“物理隔离能力”。

- Harness 决定哪些信息每轮重新进入请求；
- Provider Prefix Cache 决定共同前缀是否复用计算；
- Runtime Policy 决定某项动作是否允许执行；
- 模型是否遵守自然语言约束，需要任务级测试。

四者不能互相替代。

---

## 1. 公开修正

### 1.1 KV Cache 不是消息中的独立存储区

从客户端 Harness 的视角，请求仍然是一段序列化消息。所谓 Prefix Cache 通常是 Provider 对相同或共同前缀的计算复用机制。

它不意味着客户端可以把一段文本“放进 KV Cache”，然后从后续请求中删除该文本。除非具体 Provider 提供显式持久缓存协议，否则每次请求仍需按照 API 契约发送必要消息。

### 1.2 不参与压缩是 Harness 规则，不是 Cache 属性

如果 Context Compiler 规定：

```text
System Rules 不进入 History Compactor
```

那么规则被保留，是因为请求构造器每轮重新包含它们，而不是因为 Provider Cache 自动保护它们。

因此应使用准确术语：

```text
稳定约束区
可压缩历史区
Provider Prefix Cache
```

而不是把三者统称为“KV Cache 前缀区”。

### 1.3 信息仍在请求中，不等于模型一定遵守

必须区分：

```text
Retention：约束文本是否仍在输入中
Compliance：模型输出或动作是否符合约束
Enforcement：Runtime 是否阻止违规副作用
Cache：Provider 是否复用了共同前缀计算
```

即使 `Retention = 100%`，`Compliance` 也可能低于 100%。真正不可妥协的约束应由 Runtime Enforcement 保证，而不是只靠自然语言 Prompt。

### 1.4 任一字节变化不一定导致整个请求零命中

Prefix Cache 通常围绕共同前缀工作。后缀变化可能仍保留此前共同 Token 的命中；变化位置越早，可能失效的后续部分越多。

具体行为受 Provider、序列化、Tokenizer、缓存策略、TTL、账户和时间影响，必须根据 Usage 遥测和重复实验判断，不能写成普遍的“一个字节变化，全量 Cache 清零”。

### 1.5 历史 `40% → 95%` 结果降级

早期文章中的约束保持率数字缺少可复现 Runner、任务集、原始结果和统计检验，不再作为确认性证据。后续必须分别报告：

- 输入保留率；
- 模型遵守率；
- Runtime 拦截率；
- 最终任务成功率；
- Prefix Cache 命中和成本。

---

## 2. 问题定义

### 2.1 信息生命周期不同

| 信息类型 | 示例 | 生命周期 | 是否允许压缩 |
| --- | --- | --- | --- |
| 安全策略 | 禁止写出 Workspace | 项目或系统级 | 不允许，仅允许版本化更新 |
| 用户批准约束 | 不修改配置文件 | 任务级 | 默认不允许，需用户显式修改 |
| 工具契约 | Tool Schema、权限等级 | Session/版本级 | 不允许静默改写 |
| 决策与证据 | Approval、Diff Hash、Test Result | 任务全生命周期 | 允许索引化，不允许丢失来源 |
| 活跃工作集 | 当前目标、相关文件片段 | 当前步骤 | 可替换、可重新检索 |
| 工具原始输出 | 日志、搜索结果、文件全文 | 临时 | 可截断或外部存储 |
| 对话讨论 | 备选方案、废弃思路 | 历史 | 可摘要或归档 |

根本问题不是“压缩算法不够聪明”，而是没有先定义：

```text
谁可以改
何时生效
能否压缩
如何失效
如何审计
如何恢复
```

### 2.2 Hard Constraint 的准确含义

真正的 Hard Constraint 应满足：

> 违反后会造成安全、权限、数据完整性或明确验收失败，并且存在可确定执行的检查方法。

例如：

| 约束 | Prompt 提醒 | Runtime Enforcement |
| --- | --- | --- |
| 不写出 Workspace | 可以 | 必须做 Path Boundary Check |
| 不修改 `.git` | 可以 | 必须拒绝受保护路径 |
| 使用 Python 3.11 | 可以 | 在执行和测试环境中校验版本 |
| 修改前必须审批 | 可以 | ChangeSet 状态机必须阻断 |
| 输出使用 Markdown | 足够 | 一般不需要系统级阻断 |

不能仅根据“不得、不要、必须、禁止”等关键词自动升级为系统硬约束。自然语言中可能包含否定、引用、示例、临时偏好和冲突指令，必须结构化确认。

---

## 3. 约束注册表

建议把稳定约束建模为版本化对象：

```yaml
constraint_id: workspace-boundary
version: 3
source:
  type: system_policy
  ref: policy/security.yaml
scope:
  type: workspace
  value: /approved/workspace
enforcement: runtime
severity: critical
priority: 100
message: 只允许读写批准的 Workspace
validator: path_boundary_check
created_at: 2026-07-27T00:00:00Z
supersedes: workspace-boundary@2
```

字段至少包括：

```text
constraint_id
version
source
scope
enforcement
severity
priority
validator
created_at
supersedes
```

### 3.1 Enforcement 类型

| 类型 | 行为 |
| --- | --- |
| `runtime` | 由确定性代码阻断违规动作 |
| `verifier` | 结果生成后由测试、Schema 或规则检查 |
| `model_guidance` | 只能通过 Prompt 引导，不提供强保证 |
| `human_approval` | 需要用户明确批准才能继续 |

在 UI 和 Evidence 中必须显示约束属于哪种类型，避免把 Prompt Guidance 误称为强制安全边界。

### 3.2 冲突与更新

约束系统必须处理：

- 系统策略与用户请求冲突；
- 旧约束与新约束冲突；
- 不同 Scope 的约束重叠；
- 临时豁免；
- 安全更新要求立即生效。

建议优先级：

```text
system safety policy
> organization/project policy
> explicit task approval
> user preference
> inferred preference
```

安全策略更新时，即使会破坏 Prefix Cache，也必须立即重建前缀。正确性和安全优先于缓存命中。

---

## 4. Context Compiler 四区模型

```text
┌──────────────────────────────────────────────┐
│ 1. Stable Rules                             │
│    版本化策略、批准约束、稳定工具契约          │
├──────────────────────────────────────────────┤
│ 2. Append-Only Evidence                     │
│    决策、Approval、Diff、Test、Checkpoint     │
├──────────────────────────────────────────────┤
│ 3. Active Working Set                       │
│    当前目标、相关文件、最近工具结果、开放风险   │
├──────────────────────────────────────────────┤
│ 4. External Index                           │
│    完整轨迹、历史 Session、Artifact、Skill Body│
└──────────────────────────────────────────────┘
```

### 4.1 Stable Rules

要求：

- 序列化稳定；
- 明确版本；
- 更新有原因；
- 可主动失效；
- 不依赖 History Compactor；
- 只放真正稳定且需要模型知道的信息。

### 4.2 Append-Only Evidence

Evidence 可以在请求中使用摘要，但摘要必须保留引用：

```text
evidence_id
artifact_hash
tool_call_id
test_run_id
approval_id
```

原始 Evidence 不能被摘要覆盖或删除。

### 4.3 Active Working Set

每个步骤重新编译，只包含完成当前任务所需的最小相关集合。需要支持重新检索和显式扩大范围，避免因过度裁剪造成漏召回。

### 4.4 External Index

完整历史保存在模型请求之外，通过 Tool 或 Retrieval 按需读取。外部索引是容量扩展手段，但不保证检索正确，因此需要记录查询、候选、选中结果和未命中情况。

---

## 5. Prefix Cache 优化

在正确性成立之后，再优化缓存：

### 5.1 需要稳定的内容

- System Rules 的规范化序列；
- 稳定排序的 Tool Schema；
- 稳定的 Memory / Skill 索引；
- Provider 和模型固定配置；
- 明确的序列化版本。

### 5.2 允许导致失效的变化

- 安全策略更新；
- 工具权限收缩；
- Tool Schema 修复；
- 错误约束删除；
- Provider 协议变化；
- Compaction 或 Session 重建。

### 5.3 遥测

```text
prefix_fingerprint
serializer_version
first_changed_offset
drift_reason
prompt_cache_hit_tokens
prompt_cache_miss_tokens
TTFT
total_latency
cost
```

`prefix_fingerprint` 只用于诊断，不得包含 Secret 或完整私有 Prompt。

---

## 6. 验证矩阵

### 6.1 上下文保留测试

- Compaction 前后约束对象是否一致；
- Constraint ID、Version 和 Scope 是否保留；
- 冲突约束是否被明确拒绝；
- 安全更新是否触发上下文重建。

### 6.2 Runtime Enforcement 测试

- Workspace escape；
- symlink escape；
- `.git` 修改；
- stale Approval；
- 未审批写入；
- 不可逆工具调用；
- 预算超限。

### 6.3 模型遵守测试

在 Runtime 不直接阻断的行为上测量：

```text
instruction compliance rate
format compliance rate
citation correctness
incorrect-tool selection
```

### 6.4 Prefix Cache 测试

控制以下变体并重复运行：

- 完全相同前缀；
- 只改变用户尾部；
- 只改变 System 尾部；
- 改变 Tool 顺序；
- 改变 JSON Key 顺序；
- 安全规则版本升级；
- 不同时间和并发条件。

报告共同前缀命中 Token，而不是只报告“命中/未命中”二元结果。

---

## 7. 边界与失败模式

- 稳定前缀过大，会增加固定输入和维护成本；
- 错误规则被稳定复用，会放大错误；
- 自动提取约束可能误判自然语言；
- 约束冲突如果没有优先级，会导致不可预测行为；
- Provider Cache 是 best-effort，不能进入安全承诺；
- 缓存优化可能与 Progressive Tool Disclosure 冲突；
- 外部索引可能漏召回关键历史；
- 模型仍可能违反只靠 Prompt 引导的规则。

因此必须允许：

```text
invalidate prefix
rebuild context
disable inferred constraints
escalate conflict to user
fall back to full evidence
```

---

## 8. 结论

最重要的设计不是“把约束放进 KV Cache”，而是：

1. 用版本化对象定义哪些约束必须保留；
2. 用 Runtime Policy 强制不可妥协的安全边界；
3. 用 Context Compiler 分离稳定规则、追加证据、活跃工作集和外部历史；
4. 用独立指标测量 Retention、Compliance、Enforcement 和 Cache；
5. 安全更新和正确性修复可以主动牺牲缓存命中。

Prefix Cache 是成本与延迟优化工具，不是约束保留机制，更不是模型遵守保证。
