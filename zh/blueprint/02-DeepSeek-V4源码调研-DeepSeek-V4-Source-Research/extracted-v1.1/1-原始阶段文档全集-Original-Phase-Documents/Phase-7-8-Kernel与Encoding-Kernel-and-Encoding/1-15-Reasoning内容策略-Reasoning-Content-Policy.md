# 08-reasoning-content-policy.md — DeepSeek Agent Reasoning Content 策略 v0.1

> 基于 V4 encoding `drop_thinking`、模型卡 reasoning mode、tool calling 行为。

---

## 1. 核心判断

DeepSeek Agent 不应该把 reasoning_content 当普通上下文长期回传。

原因：

```text
1. reasoning_content 很长，消耗 context 和 cache budget
2. encoding 默认 drop old reasoning
3. 旧 reasoning 可能包含错误路径
4. tool conversations 会默认保留 reasoning，需要 Harness 介入压缩
5. Max reasoning 会改变 prompt 前缀，影响 cache stability
```

---

## 2. Reasoning Content 四种状态

```yaml
display:
  用户可见或可展开查看

archive:
  保存到本地任务记录

summary:
  压缩成 checkpoint / decision / failure note

prompt:
  进入下一轮模型上下文
```

默认策略：

```text
display: 可选
archive: 是
summary: 是
prompt: 否，除非当前工具循环必须追踪
```

---

## 3. 普通对话策略

```text
thinking_mode = chat
reasoning_content = none
```

适合：

```text
普通问答
摘要
简单改写
简单工具参数
```

---

## 4. 普通复杂任务策略

```text
thinking_mode = thinking
drop_thinking = true
```

策略：

```text
本轮 reasoning 用于生成答案
旧 reasoning 不回传
保留 final content 和 checkpoint
```

---

## 5. 工具循环策略

官方 encoding 在有 tools 时会自动 disabled drop_thinking。

这对长 Agent loop 有风险：

```text
reasoning_content 会不断累积
工具结果会不断累积
prefix 变长
cache miss 可能增加
attention 噪声增加
```

Harness 应做：

```text
1. 工具循环内短期保留 reasoning
2. 每 N 步生成 checkpoint
3. 将旧 reasoning 转为 summary / decision / error note
4. 从 active prompt 中移除旧 reasoning
5. 必要时开启新 session / compressed context
```

---

## 6. Max Thinking 策略

Max reasoning 会在 prompt 最前注入特殊前缀。

因此：

```text
不能默认启用 Max
不能每轮都 Max
不能在稳定 prefix 中频繁切 Max
```

适合：

```text
最终审查
重大失败复盘
复杂架构决策
用户明确要求最高质量
高风险任务
```

---

## 7. Reasoning Content 不回传原则

推荐规则：

```text
旧 reasoning_content 不进入 prompt
当前 reasoning_content 可用于 display/archive
核心决策进入 checkpoint
失败路径进入 failure note
可复用经验进入 skill / memory
```

---

## 8. 转化格式

### 8.1 Checkpoint

```yaml
checkpoint_id: ckpt-xxx
reasoning_summary: 为什么这样做
decision: 最终决策
discarded_paths:
  - 被否决方案
risks:
  - 风险
next_action: 下一步
```

### 8.2 Skill

```yaml
skill_name: xxx
trigger: 什么时候用
procedure:
  - 步骤
common_failure:
  - 错误路径
validation:
  - 检查标准
```

### 8.3 Memory

```yaml
memory_type: project_decision
content: 用户/项目偏好或稳定决策
source_checkpoint: ckpt-xxx
```

---

## 9. 产品 UI

UI 可以提供：

```text
查看推理摘要
查看完整推理记录
不保存推理
仅保存任务决策
```

但默认用户不应该被 reasoning_content 淹没。

---

## 10. 关键结论

Reasoning 是过程，不是记忆。

DeepSeek Agent 应该：

```text
保存 reasoning 的价值
丢弃 reasoning 的噪声
把 reasoning 结晶成 checkpoint / skill / memory
而不是把 reasoning 原文无限回传
```
