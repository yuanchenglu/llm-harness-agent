# 05-agent-model-router-rules.md — DeepSeek Agent 模型路由规则 v0.1

> 基于 V4 MoE / Flash-Pro 差异的第一版 Agent 模型路由策略。

---

## 1. 路由总原则

DeepSeek Agent 不应该让用户手动理解 Flash / Pro / Think / Max 的差异，而应该内置一个模型路由器：

```text
输入任务
  ↓
任务类型识别
  ↓
上下文长度 / 风险 / 复杂度 / 失败次数 / 成本预算
  ↓
选择 Flash / Pro
  ↓
选择 Non-think / Think / Max
  ↓
执行
  ↓
如失败或不确定，自动升级
```

---

## 2. Flash 的正确定位

Flash 不是“弱智版”，而是同构小模型：

- 同样 1M context；
- 同样 Hybrid Attention；
- 同样 mHC；
- 同样 6 routed experts per token；
- 同样 1 shared expert；
- 同样支持 reasoning effort；
- 只是规模更小、专家池更小、index_topk 更小、层数更少。

### Flash 适合

```text
1. 普通对话
2. 文件读取 / 摘要
3. 简单代码解释
4. 小范围代码修改
5. 工具调用参数生成
6. 日志初筛
7. 搜索结果归纳
8. 低风险本地自动化
9. 上下文整理 / checkpoint 生成
10. Plan 初稿
```

### Flash 不适合单独承担

```text
1. 高风险代码重构
2. 大型架构判断
3. 多文件跨模块依赖推理
4. 长上下文证据冲突判断
5. 复杂法律 / 金融 / 医疗等高风险任务
6. 最终 PR review
7. 失败复盘
8. Agent 长任务的关键决策点
```

---

## 3. Pro 的正确定位

Pro 的优势来自：

- 49B activated；
- 61 层；
- hidden_size 7168；
- 384 routed experts；
- index_topk 1024；
- route_scale 2.5；
- 更强的知识和复杂 agentic workflow 表现。

### Pro 适合

```text
1. 复杂任务规划
2. 架构设计
3. 多文件重构计划
4. 高风险操作前审查
5. 长上下文 evidence reconciliation
6. 失败原因定位
7. 关键 checkpoint review
8. 复杂代码 review
9. Agent 自我纠偏
10. 最终答案/交付物审查
```

---

## 4. 推荐四象限路由

| 模式 | 用途 | 示例 |
|---|---|---|
| Flash Non-think | 快速低成本执行 | 摘要、分类、提取、简单工具参数 |
| Flash Think | 中等复杂度任务 | 小范围代码修改、普通 Plan、日志分析 |
| Pro Non-think | 大上下文但低推理 | 从 1M 上下文中检索事实、汇总证据 |
| Pro Think | 复杂推理和审查 | 架构决策、失败复盘、关键 review |
| Pro Max | 极高风险/极难任务 | 重大产品架构、复杂 agentic benchmark、最终决策 |

---

## 5. 自动升级规则

### 5.1 Flash → Pro

触发条件：

```text
1. Plan 超过 5 个依赖节点
2. 涉及 5 个以上文件/模块
3. 上下文超过 128K tokens
4. 工具调用失败 2 次
5. 模型输出自评不确定
6. 需要最终审查
7. 用户要求“严谨/完整/不要错”
8. 涉及高风险操作：删除、迁移、支付、法律、生产环境
```

### 5.2 Non-think → Think

触发条件：

```text
1. 需要多步推理
2. 需要比较多个方案
3. 需要解释为什么
4. 需要从错误日志推断根因
5. 需要修改代码并保证测试
```

### 5.3 Think → Max

触发条件：

```text
1. Think 失败
2. 出现互相矛盾证据
3. 用户明确要求最高质量
4. 任务是关键架构/安全/上线决策
5. 需要跨 1M 上下文做综合判断
```

---

## 6. 成本控制策略

DeepSeek Agent 应默认：

```text
Flash-first
Pro-on-checkpoint
Pro-on-risk
Pro-on-failure
Pro-on-final-review
```

也就是：

1. Flash 做探索；
2. Flash 做执行；
3. Pro 做关键判断；
4. Pro 做失败复盘；
5. Pro 做最终验收。

---

## 7. 与 MoE 物理特性的对应

| 物理特性 | 路由策略 |
|---|---|
| Flash 和 Pro 同构 | 统一 provider，动态切模型 |
| Flash 13B activated | 默认执行与低风险任务 |
| Pro 49B activated | 高复杂推理/审查 |
| Pro index_topk 1024 | 长上下文检索/证据冲突 |
| Flash index_topk 512 | 需要更强 context layout |
| Pro route_scale 2.5 | 专业任务/复杂领域 |
| 前 3 层 hash routing | prompt 标签稳定化 |
| shared expert | Flash 也可胜任大量通用任务 |

---

## 8. UI 解释语句

产品里可以用用户能理解的话解释路由：

```text
这一步我会使用 Flash 快速整理上下文，成本更低。
```

```text
这一步涉及跨多个文件的架构判断，我会临时切换到 Pro 审查。
```

```text
当前任务已经失败两次，我会切换到 Pro Think 做一次根因复盘。
```

```text
这是最终交付前检查，我会使用 Pro 做严格审查。
```
