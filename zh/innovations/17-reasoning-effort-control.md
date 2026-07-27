# 推理强度控制：参数接受、真实语义与任务收益必须分别验证

> **证据等级：A1 + N/B**  
> - **A1**：固定 `encoding_dsv4.py` 可确认 `reasoning_effort` 接受 `None / high / max`，且 `max` 在特定条件下注入一段强化推理指令。  
> - **N/B**：`high` 是否由服务端后端消费、公共 API 是否暴露相同语义、不同档位的质量/延迟/Token 影响，均需端到端实验。  
> 请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-17  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[16 Quick Instruction 路由](16-quick-instruction-routing.md)  
> **下一篇**：[18 最新提醒注入](18-latest-reminder-injection.md)

---

## 摘要

“让模型多想一点”不是一个单一能力。可能涉及：

- 请求参数；
- 模型选择；
- Thinking Mode；
- Prompt 指令；
- 最大输出 Token；
- Planner / Reviewer；
- 重试和验证预算。

编码源码能够证明某些字段和 Prompt 路径存在，但不能单独证明线上 API 的真实行为和收益。

可靠 Harness 应把推理强度建模为 Provider Capability 和 Budget Policy：

```text
Task Risk / Uncertainty / Evidence Gap
→ Candidate Reasoning Policy
→ Provider Capability Check
→ Execute with Budget
→ Verify Result
→ Escalate or Stop
```

---

## 1. 源码可以确认什么

固定编码源码中存在类似校验：

```python
assert reasoning_effort in ["max", None, "high"]
```

并且在特定 `thinking_mode` 和消息位置下，`max` 会注入强化推理文本。

A1 结论：

- 编码实现接受三个值；
- `max` 存在可见 Prompt 渲染逻辑；
- `None` 不注入该文本；
- `high` 在该段编码代码中没有与 `max` 相同的文本注入分支。

不能据此确认：

- `high` 一定由后端推理引擎消费；
- `high` 一定比默认更深；
- 公共 API 会透传该字段；
- `max` 一定改善答案质量；
- 额外延迟和 Token 是固定倍数。

---

## 2. 公开修正

### 2.1 删除未经实验的固定成本数字

早期版本给出过：

```text
high: completion 约 1.5–2x，延迟增加 20–50%
max: completion 约 2–5x，延迟增加 50–200%
```

这些数字没有绑定固定 Endpoint、任务集、重复次数和结果文件，现已删除。后续只能引用可复现实验中的实际分布。

### 2.2 合法值不等于参数生效

API 或 SDK 可能：

- 接受并执行；
- 接受但忽略；
- 转换成其他参数；
- 只在部分模型生效；
- 返回 200 但语义不变。

必须通过输出、Usage、延迟和任务质量共同判断。

### 2.3 Prompt 位置不等于“注意力权重最大”

把指令放在最前、System 中或最近用户消息附近，可能产生不同行为，但不能仅根据位置断言模型内部权重。需要 A/B Test。

### 2.4 更多 reasoning 不等于更正确

更长推理可能：

- 找到更多边界；
- 产生更多错误假设；
- 增加延迟和成本；
- 延迟发现工具证据不足；
- 在简单任务中过度分析。

最终质量必须由 Verifier 和任务结果决定。

---

## 3. Provider Capability

```yaml
provider: deepseek
endpoint: <redacted-endpoint-id>
model: deepseek-v4-pro
observed_at: 2026-07-27
thinking_mode:
  supported: unknown
reasoning_effort:
  accepted_values:
    - null
    - high
    - max
  high_semantics: unverified
  max_prompt_injection_in_source: true
  public_api_effect: unverified
limitations:
  - encoding source does not prove hosted endpoint behavior
```

Capability 应带时间、Endpoint、模型和证据来源，不能写成永久全局常量。

---

## 4. Harness 内部策略

Provider-neutral 表示：

```typescript
type ReasoningPolicy = {
  mode: "minimal" | "standard" | "deep";
  maxInputTokens: number;
  maxOutputTokens: number;
  maxLatencyMs: number;
  maxCost: number;
  requirePlanner: boolean;
  requireIndependentReview: boolean;
  providerParams: Record<string, unknown>;
};
```

上层产品不直接依赖 `high` 或 `max` 字符串。

### 4.1 Minimal

适用：

- 确定性格式转换；
- 简单查询；
- 有强 Verifier 的低风险任务；
- 可快速重试。

### 4.2 Standard

适用：

- 常规代码修改；
- 多步骤分析；
- 中等风险决策；
- 需要工具证据。

### 4.3 Deep

候选条件：

- 高风险、难回滚；
- 多约束冲突；
- 复杂架构权衡；
- Verifier 多次失败；
- 关键 Evidence 不一致；
- 安全审查。

Deep 不代表自动执行。高风险动作仍需要 Policy 和 Approval。

---

## 5. 路由信号

不要只按关键词：

```python
if "code review" in prompt:
    effort = "high"
```

更可靠信号：

```text
risk
reversibility
blast radius
uncertainty
evidence completeness
novelty
verifier failures
remaining budget
```

示例：

```yaml
reasoning_route:
  policy: deep
  reasons:
    - risk:R3
    - irreversible:false
    - verifier_failures:2
    - evidence_conflict:true
  budget:
    max_latency_ms: 60000
    max_cost: <configured-budget>
  exit_conditions:
    - verifier_pass
    - user_intervention
    - budget_exhausted
```

---

## 6. Escalation 而不是一次性猜测

建议：

```text
Standard Attempt
→ Deterministic Verification
→ 如果通过：结束
→ 如果失败且可修复：带失败证据重试
→ 如果高风险/重复失败：Deep + Independent Review
→ 如果预算耗尽或证据不足：停止并请求用户
```

这样避免所有任务一开始就使用最昂贵模式。

### 6.1 Escalation 记录

```text
from policy
to policy
trigger
previous failure evidence
additional budget
outcome
```

### 6.2 防止无限深思

必须设置：

- 最大重试；
- 最大 Token；
- 最大延迟；
- 最大成本；
- 停止条件；
- 人工接管。

---

## 7. Reasoning Content 与后续轮次

更深模式可能生成更多 reasoning 内容，但是否回传取决于 Provider 协议：

- 某些 Tool Call 链要求保留；
- 某些普通多轮可以删除；
- 某些服务端自动处理；
- 计费和 Cache 行为可能不同。

必须使用 [I-14 Reasoning Content 回传策略](14-reasoning-content-stripping.md) 的 Capability Matrix，而不是为了节省 Token 无条件删除。

---

## 8. 实验矩阵

### 8.1 协议

```text
None / high / max
thinking / non-thinking
stream / non-stream
tools / no tools
raw HTTP / SDK
```

确认：

- 字段是否被接受；
- 响应结构；
- 是否静默忽略；
- Tool Loop 是否可继续。

### 8.2 质量

任务类别：

- 简单确定性；
- 常规代码修改；
- 并发 Bug；
- 架构决策；
- 安全审查；
- 含错误前提的对抗题。

指标：

```text
first-pass success
verifier pass
constraint violation
factual/source accuracy
human preference
```

### 8.3 资源

```text
reasoning tokens
output tokens
input tokens
cache hit/miss
TTFT
total latency
cost
```

### 8.4 实验纪律

- 随机化执行顺序；
- 多次重复；
- 记录服务状态；
- 分离开发集和 Held-out 集；
- 报告分布和失败样本；
- 不只比较输出长度。

---

## 9. 决策规则

一个更深策略只有在以下条件下才进入默认路由：

```text
质量提升可重复
且
每成功任务成本在预算内
且
延迟满足产品要求
且
没有增加安全违规
```

如果只增加 reasoning 长度，没有提高 Verifier Pass 或减少人工介入，应拒绝该策略。

---

## 10. 边界与风险

- Provider 参数可能变化；
- `high` 可能被忽略；
- `max` 可能只是 Prompt Injection；
- 更长 reasoning 可能暴露更多敏感内容；
- Tool Call 协议可能要求回传 reasoning；
- 深模式可能放大错误前提；
- Router 可能对简单任务过度升级；
- 成本估算可能因价格变化失效。

必须有 Capability Version、预算、Fallback 和禁用开关。

---

## 11. 结论

推理强度控制不能从源码中的三个合法值直接推导为三个稳定产品档位。

可靠实现需要：

1. 区分参数接受、语义生效和任务收益；
2. 把 Provider-specific 字段封装在 Adapter；
3. 用风险、可逆性、证据和 Verifier 失败驱动升级；
4. 设置 Token、延迟、成本和重试上限；
5. 通过 Held-out 任务测量质量与每成功任务成本；
6. 在证据不足时停止，而不是无限“多想”。

推理更长不是目标。用可控成本获得更可靠结果才是目标。
