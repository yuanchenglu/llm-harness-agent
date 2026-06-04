# 09-cost-quality-routing-policy.md — DeepSeek Agent 成本 / 质量路由策略 v0.1

> 目标：把 DeepSeek 的 cache hit/miss、Flash/Pro、thinking effort 变成可控的成本-质量系统。

---

## 1. 成本组成

每轮成本由 6 部分组成：

```text
1. cache miss prompt tokens
2. cache hit prompt tokens
3. output tokens
4. reasoning / thinking tokens
5. model choice: Flash vs Pro
6. loop count: 工具调用轮数
```

不能只看 total tokens。

---

## 2. 成本控制三原则

### 2.1 Flash-first

默认使用 Flash 执行低风险任务。

### 2.2 Pro-on-checkpoint

不是全程 Pro，而是在关键 checkpoint 切 Pro。

### 2.3 Prefix-stable

最大化 cache hit，减少 repeated prefill。

---

## 3. 质量控制三原则

### 3.1 Risk-gated

风险越高，越需要 Pro 和 review。

### 3.2 Failure-gated

失败次数越多，越需要升级 reasoning effort。

### 3.3 Final-review-gated

最终交付前必须至少一次 Pro review，除非任务明确低风险。

---

## 4. 用户模式

### 4.1 省钱模式

```text
Flash Non-think / Flash Think 为主
Pro 只在失败或高风险时使用
Max 默认关闭
```

### 4.2 平衡模式

```text
Flash 执行
Pro 做关键 checkpoint review
Max 只做最终高风险审查
```

### 4.3 最高质量模式

```text
复杂任务默认 Pro Think
关键节点 Pro Max
成本提示但不自动降级
```

---

## 5. 成本 UI

每个任务显示：

```yaml
total_cost_estimate:
cache_hit_rate:
cache_miss_tokens:
output_tokens:
reasoning_mode:
model_route:
pro_steps:
flash_steps:
most_expensive_step:
```

---

## 6. Budget Guardrail

如果预计成本超过阈值：

```text
提示用户
建议压缩上下文
建议切 Flash
建议分阶段执行
建议只审查关键文件
```

---

## 7. Cache Guardrail

如果 cache hit 率下降：

```text
检查 system prefix 是否变化
检查 tool schema 是否变化
检查 Memory/Skill index 是否变化
检查是否插入动态时间戳/随机 ID
检查是否切换 Max special prefix
```

---

## 8. 质量 Guardrail

如果任务风险升高：

```text
强制 checkpoint
强制 Pro Review
强制用户确认
禁止直接执行不可逆操作
```

---

## 9. 核心策略

```text
便宜来自 Flash 和 cache hit
质量来自 Pro 和 review
稳定来自 checkpoint 和 prefix-stable
```
