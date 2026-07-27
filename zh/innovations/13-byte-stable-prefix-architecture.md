# Byte-Stable Prefix：受正确性约束的缓存优化不变量

> **证据等级：A1 + B**  
> 固定源码可以确认部分 Agent 在 Session、Memory、Skills、Plan Mode 和模型协作中主动维护稳定前缀；这证明该设计真实存在。它不能证明“稳定前缀 + 瞬态尾缀”是所有 Agent 的物理最优架构，也不能证明 Prefix Cache 命中必然提高任务质量。本文将 Byte Stability 定位为可观测、可失效、受正确性约束的优化不变量。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-13  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **关联**：[I-04 稳定约束与可压缩历史](04-kv-cache-prefix.md) · [I-05 Agent 可读文档结构](05-document-kv-cache.md)

---

## 摘要

Prefix Cache 的基本工程机会是：如果多次请求共享相同前缀，Provider 可能复用部分计算，降低输入成本或首 Token 延迟。

这可以影响 Agent 架构，但不能成为最高优先级。正确优先级是：

```text
正确性与安全
> Provider 协议兼容
> 状态一致性与可恢复
> 任务质量
> Cache / Token / Latency 优化
```

Byte-Stable Prefix 的准确含义是：

> 对被标记为稳定的请求片段，使用确定性序列化和显式版本；只有在语义、权限和协议未变化时保持字节不变。任何必要更新都必须允许主动失效。

---

## 1. 公开修正

### 1.1 不是“物理最优定律”

Transformer 自回归和 Prefix Cache 解释了为什么共同前缀可能被复用，但不能推出：

- 所有动态信息都必须放在尾部；
- Mid-session 模型切换永远不应发生；
- 前缀越稳定，任务质量越高；
- 任一前缀变化都不可接受；
- 某一开源实现就是全行业最优解。

不同任务可能更需要及时更新安全规则、工具权限、项目事实或模型能力。

### 1.2 编码层与 Harness 层的相似模式不是因果证明

模型编码源码中删除旧 reasoning、保留某些角色，和 Agent Runtime 中稳定 System Prompt，可能共享“稳定信息与瞬态信息分层”的设计直觉。

但它们处在不同层：

```text
模型数据/编码预处理
Provider 服务端缓存
客户端请求编译
Agent Session 状态
```

跨层相似性可以产生研究假设，不能直接证明同一个优化目标或训练意图。

### 1.3 Byte Stability 不等于 Semantic Correctness

完全相同的前缀可能包含：

- 过期 Memory；
- 已撤销工具；
- 错误安全规则；
- 失效价格；
- 旧项目状态。

因此必须先判断语义版本是否仍有效，再追求字节稳定。

### 1.4 Cache 命中不等于任务成功

必须同时报告：

```text
cache hit/miss
latency
cost
task success
constraint violation
human intervention
```

不能只用 Hit Rate 宣称架构更好。

---

## 2. 稳定前缀分段

建议把前缀拆成独立版本段：

```text
P0 Provider / Protocol Contract
P1 System Safety Policy
P2 Product / Runtime Rules
P3 Project Constraints
P4 Tool Catalog
P5 Memory / Skill Index
```

每段都有：

```yaml
segment_id: tool-catalog
semantic_version: 12
serializer_version: 3
content_hash: sha256:...
source_refs:
  - tool-registry@commit-abc
invalidation_reasons:
  - tool_added
  - permission_changed
  - schema_fixed
```

### 2.1 为什么分段

分段可以回答：

- 哪一段变化；
- 为什么变化；
- 是否安全更新；
- 变化发生在前缀什么位置；
- 哪些共同前缀仍可能复用。

比单一 `system_prompt_hash` 更容易诊断。

---

## 3. Canonical Serialization

### 3.1 需要确定性的对象

- Tool Schema 排序；
- JSON Key 顺序；
- Unicode normalization；
- 换行；
- 空白；
- 数字和布尔表示；
- 可选字段缺省策略；
- Message 包装顺序。

### 3.2 Serializer Version

序列化器必须版本化：

```yaml
serializer:
  name: deepseek-openai-compatible
  version: 3
  unicode: NFC
  newline: LF
  sort_tools_by: name
  sort_json_keys: true
```

版本变化应主动记录 Drift，而不是把缓存下降误判为 Provider 故障。

### 3.3 禁止伪稳定

不要为了稳定而：

- 保留已撤销工具；
- 发送用户无权使用的 Schema；
- 隐藏安全更新；
- 把动态日期写成旧值；
- 固定错误 Memory；
- 关闭必要的 Context Rebuild。

---

## 4. 动态信息策略

### 4.1 Turn Tail

适合：

- 当前任务；
- 临时模式；
- 最新工具结果；
- Mid-session Memory 提议；
- 当前日期和位置；
- Pending Approval。

### 4.2 Session Rebuild

以下变化应重建：

- 安全策略；
- Tool 权限；
- Provider 协议；
- 项目根目录；
- 模型能力；
- 错误前缀修复；
- Compaction 结构变化。

### 4.3 Independent Session

Planner、Executor、Reviewer 使用独立 Session 可能有价值：

- 保持各自状态清晰；
- 降低交叉污染；
- 允许不同模型和工具；
- 可能保持各自前缀稳定。

但代价包括：

- 重复输入；
- 状态同步；
- Summary Error；
- 更高总调用成本。

是否采用由任务 benchmark 决定，不应只由 Cache 决定。

---

## 5. Prefix Manifest

每次请求记录脱敏 Manifest：

```yaml
request_id: req-123
provider: deepseek
model: deepseek-v4-pro
endpoint_capability_version: 2026-07-16
segments:
  - id: provider-contract
    semantic_version: 4
    content_hash: sha256:...
  - id: safety-policy
    semantic_version: 9
    content_hash: sha256:...
  - id: tool-catalog
    semantic_version: 12
    content_hash: sha256:...
stable_prefix_hash: sha256:...
first_drift_segment: tool-catalog
drift_reason: permission_changed
cache:
  hit_tokens: 4096
  miss_tokens: 512
```

Manifest 不保存 Secret 或完整私有 Prompt。

---

## 6. Invalidation Policy

### 6.1 主动失效原因

```text
security_policy_update
tool_permission_change
tool_schema_fix
provider_capability_change
project_switch
memory_correction
serializer_upgrade
context_compaction
manual_rebuild
```

### 6.2 不得静默失效

Runtime 应显示：

- 失效原因；
- 受影响段；
- 新旧版本；
- 是否预期；
- 质量和成本影响。

### 6.3 Cache 优先级 Gate

如果保持前缀稳定需要牺牲：

- 正确工具；
- 最新安全策略；
- 正确项目事实；
- 更合适模型；
- 必要审查；

则必须失效 Cache。

---

## 7. Provider Capability

不同 Provider 可能具有：

- 自动 Prefix Cache；
- 显式 Cache Control；
- 最小缓存长度；
- TTL；
- 不同计费；
- 不同 Usage 字段；
- 不同工具协议。

建议 Capability Snapshot：

```yaml
provider: deepseek
model: deepseek-v4-pro
observed_at: 2026-07-16
prefix_cache:
  observable: true
  hit_field: prompt_cache_hit_tokens
  miss_field: prompt_cache_miss_tokens
  ttl: unknown
  deterministic: false
limitations:
  - endpoint/account/time scoped
```

不能把一个 Endpoint 的观察外推到所有模型和时间。

---

## 8. 决策指标

### 8.1 Cache

```text
shared prefix ratio
cache hit tokens
cache miss tokens
hit stability across runs
TTL behavior
```

### 8.2 Performance

```text
TTFT
total latency
input cost
total cost
```

### 8.3 Quality and Safety

```text
first-pass success
constraint violations
incorrect tool calls
human intervention
stale context incidents
```

### 8.4 Complexity

```text
prefix segment count
invalidation frequency
serializer bugs
state synchronization defects
maintenance effort
```

---

## 9. 实验设计

比较：

```text
A. 无稳定化：自然请求组装
B. Canonical Serializer
C. 分段稳定前缀 + Dynamic Tail
D. C + 独立 Planner/Reviewer Session
```

在相同 Held-out 任务上测量：

- 任务成功；
- 成本；
- 延迟；
- Cache；
- 失效次数；
- 维护缺陷。

必须包含安全策略和工具权限变化场景，验证系统能正确牺牲 Cache。

---

## 10. 何时值得成为架构不变量

只有满足以下条件，Byte Stability 才应成为强工程约束：

1. Provider 确实提供稳定、可观测收益；
2. 稳定段占请求的重要比例；
3. Canonicalization 不引入协议错误；
4. 质量和安全不下降；
5. 失效机制清晰；
6. 复杂度收益为正；
7. 多轮和跨时间实验可复现。

否则它应降级为局部优化，而不是系统根原则。

---

## 11. 结论

Byte-Stable Prefix 是有价值的 Harness 优化方向，但必须被准确约束：

- 它优化共同前缀的计算复用；
- 它不保证约束遵守；
- 它不证明模型质量提升；
- 它不能阻止必要的安全和事实更新；
- 它需要分段、版本、Canonical Serializer、Manifest 和 Invalidation Policy；
- 它的价值由每成功任务成本、延迟、质量、安全和维护复杂度共同决定。

Cache 是手段。正确、可恢复、可审计的 Agent 才是目标。
