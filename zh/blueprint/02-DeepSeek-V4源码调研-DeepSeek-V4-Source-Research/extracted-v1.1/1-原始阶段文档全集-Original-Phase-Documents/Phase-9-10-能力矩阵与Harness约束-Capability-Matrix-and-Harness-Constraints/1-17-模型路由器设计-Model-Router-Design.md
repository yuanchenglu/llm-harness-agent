# 09-model-router-design.md — DeepSeek Agent 模型路由器设计 v0.1

> 目标：把 Flash / Pro / reasoning effort 从“用户手动选择”变成 Harness 自动决策。

---

## 1. 路由器输入

```yaml
task:
  intent: code | research | file | browser | terminal | writing | planning | review
  complexity: simple | medium | complex | critical
  risk_level: low | medium | high | irreversible
  context_tokens: number
  active_files: number
  tool_calls_so_far: number
  failures_so_far: number
  requires_final_review: bool
  user_quality_preference: fast | balanced | best
  budget_preference: cheap | balanced | quality
```

---

## 2. 路由器输出

```yaml
model: deepseek-v4-flash | deepseek-v4-pro
thinking_mode: non_think | think | max
reason: string
expected_cost_level: low | medium | high
review_required: bool
checkpoint_required: bool
```

---

## 3. 第一版规则

### 3.1 默认规则

```text
simple + low risk → Flash Non-think
medium + low/medium risk → Flash Think
complex + medium/high risk → Pro Think
critical / irreversible → Pro Max + user approval
```

### 3.2 Code Mode

```text
读文件 / 定位代码 → Flash Non-think
解释代码 → Flash Think
小 diff → Flash Think
多文件 diff → Flash Think + Pro Review
架构重构计划 → Pro Think
最终 PR review → Pro Think / Max
测试失败复盘 → Pro Think
```

### 3.3 Agent Mode

```text
文件整理 → Flash Non-think
网页/资料摘要 → Flash Think
长文档研究 → Flash Think → Pro Summary Review
多来源冲突判断 → Pro Think
外部工具执行计划 → Pro Think
高风险本地操作 → Pro Think + user approval
```

### 3.4 Research Mode

```text
搜索 query 生成 → Flash Non-think
资料初筛 → Flash Think
证据冲突 → Pro Think
最终报告 → Pro Think
重要结论审查 → Pro Max
```

---

## 4. 自动升级条件

```yaml
upgrade_to_pro_if:
  - context_tokens > 128000 and task.requires_reasoning
  - active_files >= 5
  - dependency_depth >= 3
  - failures_so_far >= 2
  - tool_calls_so_far >= 8
  - risk_level in [high, irreversible]
  - requires_final_review == true
  - user_quality_preference == best
  - evidence_conflict == true
```

```yaml
upgrade_to_max_if:
  - pro_think_failed == true
  - final_delivery_is_high_stakes == true
  - user_explicitly_requests_highest_quality == true
  - task involves irreversible operations
```

---

## 5. 自动降级条件

```yaml
downgrade_to_flash_if:
  - task is extractive
  - task is formatting
  - task is summarization without conflict
  - task is tool parameter filling
  - context has already been checkpointed
  - pro result already produced plan and remaining step is execution
```

---

## 6. Checkpoint 驱动路由

推荐模式：

```text
Flash 执行 3~5 步
  ↓
生成 checkpoint
  ↓
根据风险决定是否 Pro Review
  ↓
继续 Flash 执行
```

这样可以避免：

```text
全程 Pro 成本高
全程 Flash 风险高
全量上下文堆积导致注意力污染
```

---

## 7. 路由可解释性

每次切模型时，UI 应解释：

```text
“这一步只是在整理上下文，我会用 Flash。”
“这一步涉及多个文件之间的依赖，我会切 Pro 做审查。”
“已经连续失败两次，我会用 Pro Think 做根因复盘。”
“这是最终交付前检查，我会用 Pro Max 做严格验证。”
```

---

## 8. 日志结构

```yaml
route_id: route-xxx
step_id: plan-step-id
selected_model: deepseek-v4-pro
thinking_mode: think
reason:
  - active_files >= 5
  - requires_final_review
  - previous_failures = 2
cost:
  estimated: ...
  actual: ...
outcome:
  success: true
  confidence: high
```

---

## 9. 路由器不是一次性规则，而是学习系统

后续可加入：

```text
用户偏好学习
项目风险 profile
任务成功率统计
Flash/Pro 成本收益分析
badcase 自动回放
route policy 自进化
```
