# Quick Instruction 路由：编码层能力与公共 API 可用性必须分开

> **证据等级：A1 + N/B**  
> - **A1**：固定 `encoding_dsv4.py` 源码可确认 `action / query / authority / domain / title / read_url` 特殊 Token 和渲染逻辑存在。  
> - **N/B**：当前公开证据不足以证明客户端可在标准 API 请求中直接设置 `task` 字段并稳定触发这些行为；产品集成仍需 Endpoint Spike。  
> 请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-16  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[15 DSML 编码层研究](15-dsml-tool-call-optimization.md)  
> **下一篇**：[17 推理强度控制](17-reasoning-effort-control.md)

---

## 摘要

DeepSeek V4 编码源码定义了六类任务特殊 Token：

```text
action
query
authority
domain
title
read_url
```

它们表明模型编码/服务栈可能支持短输出分类、查询生成、标题生成和 URL 判断等专用任务模式。

但存在关键边界：

```text
编码函数接受 task 字段
≠
标准公开 Chat API 接受客户端 task 字段
```

因此 Harness 的正确策略是：

1. 把 Quick Instruction 作为 Provider Capability；
2. 先做原始 HTTP 端到端探针；
3. 只有 Wire Contract 和行为稳定后才进入默认路由；
4. 始终保留标准 Prompt / Tool 路由回退；
5. 不把源码中的内部分类用途直接写成产品承诺。

---

## 1. 源码可以确认什么

固定源码中存在类似映射：

```python
DS_TASK_SP_TOKENS = {
    "action": "<｜action｜>",
    "query": "<｜query｜>",
    "authority": "<｜authority｜>",
    "domain": "<｜domain｜>",
    "title": "<｜title｜>",
    "read_url": "<｜read_url｜>",
}
```

并在消息渲染时根据 `task` 选择特殊 Token。

A1 级结论：

> DeepSeek V4 编码实现包含六类专用任务 Token，以及对应的 Prompt 渲染路径。

不能仅凭该源码确认：

- 公共 API 请求 Schema 暴露 `task`；
- SDK 会透传 `task`；
- 服务端线上版本与源码一致；
- 输出值和格式稳定；
- 该模式比普通 Prompt 更快、更便宜或更准确。

---

## 2. 三层边界

### 2.1 模型编码层

负责把结构化消息转换为模型 Token 序列。

### 2.2 Provider 服务层

可能：

- 使用上述编码逻辑；
- 对客户端字段做白名单过滤；
- 在内部调用这些任务；
- 不向外部用户暴露；
- 使用不同版本实现。

### 2.3 Harness 客户端

只能依赖：

- 官方 API 文档；
- SDK 行为；
- 原始 HTTP Wire Evidence；
- 可重复 Endpoint 实验。

客户端不应向标准 API 随意加入未文档化字段，然后以 HTTP 200 判断功能生效。

---

## 3. 六类任务的合理假设

以下是基于 Token 名称和渲染位置的工程解释，不是已确认公共产品语义。

| Task | 候选用途 | 需要验证 |
| --- | --- | --- |
| `action` | 搜索/回答或动作路由 | 输出枚举、准确率、thinking 交互 |
| `query` | 生成搜索查询 | 多语言、长度、注入风险 |
| `authority` | 判断来源权威要求 | 标签集合、校准、领域迁移 |
| `domain` | 领域分类 | 分类体系、开放集、混淆矩阵 |
| `title` | 生成会话标题 | 长度、语言、敏感信息泄露 |
| `read_url` | 判断 URL 是否需抓取 | 多 URL、恶意 URL、输出格式 |

“候选用途”不能替代协议文档或端到端结果。

---

## 4. Capability Probe

### 4.1 请求路径

至少比较：

```text
raw HTTP with documented fields
raw HTTP with task field
official SDK with task field
standard prompt emulation
```

### 4.2 结果分类

| 结果 | 含义 |
| --- | --- |
| 4xx 未知字段 | 公共 API 不支持 |
| 200 但行为无差异 | 字段可能被忽略 |
| 200 且输出短但不稳定 | 实验能力，暂不产品化 |
| 200 且跨模型/时间稳定 | 可进入 Capability Snapshot |
| SDK 丢弃字段 | 只能用 raw HTTP，需评估维护成本 |

HTTP 200 只证明请求被接受，不证明参数语义生效。

### 4.3 Manifest

```yaml
probe_id: quick-instruction-action-20260727
provider: deepseek
endpoint: <redacted-endpoint-id>
model: deepseek-v4-pro
sdk_version: null
request_variant: raw-http-task-field
repeats: 20
observed_at: 2026-07-27
response_schema:
  fields: [choices, usage]
behavior:
  expected_labels: [Search, Answer]
  exact_match_rate: null
status: unverified
limitations:
  - endpoint/account/time scoped
```

---

## 5. 产品集成架构

### 5.1 Provider-Neutral Router

```typescript
interface RouteRequest {
  task: string;
  context?: unknown;
  allowedLabels?: string[];
}

interface RouteResult {
  label: string;
  confidence?: number;
  rawOutputRef: string;
  providerCapability: string;
  fallbackUsed: boolean;
}
```

Router 不应把 `action` 等私有 Token 暴露给上层产品逻辑。

### 5.2 Adapter 选择

```text
if provider capability verified:
    use quick-instruction adapter
else:
    use standard structured prompt or lightweight classifier
```

### 5.3 输出清洗

即使专用模式只预期输出一个词，也要处理：

- 前后空白；
- 大小写；
- 多行解释；
- 未知标签；
- 空输出；
- 截断；
- Prompt Injection；
- 流式增量。

建议使用 Allowlist 和 Unknown 回退，不能模糊匹配后直接执行高风险动作。

---

## 6. 风险分层

### 6.1 低风险用途

- 会话标题；
- 搜索查询候选；
- UI 分类标签。

错误通常可恢复。

### 6.2 中风险用途

- 是否联网搜索；
- 是否抓取 URL；
- 工具目录选择。

需要回退和可观察性。

### 6.3 高风险用途

- 权限等级；
- 是否允许写入；
- 是否执行外部副作用；
- 医疗/法律/金融权威判断。

不能只依赖 Quick Instruction。必须由 Policy、确定性规则或人工审批兜底。

---

## 7. 性能假设

Quick Instruction 可能产生短输出，但端到端收益受以下因素影响：

```text
额外网络往返
是否重新发送长前缀
Provider Cache 命中
模型排队
输出长度
后续调用是否被避免
```

一次额外分类调用可能比直接让主模型完成任务更慢。应比较完整工作流：

```text
Router + Main Call
vs.
Single Main Call
```

而不是只比较 Router 自身输出 Token。

---

## 8. 评测

### 8.1 分类质量

```text
accuracy
macro F1
open-set rejection
confidence calibration
cost-weighted errors
```

### 8.2 查询质量

```text
search recall
result relevance
query injection rate
language quality
```

### 8.3 URL 判断

```text
necessary-fetch recall
unnecessary-fetch rate
malicious-url handling
multi-url accuracy
```

### 8.4 性能

```text
router latency
workflow latency
total tokens
cache hit/miss
cost per successful task
```

### 8.5 对照

比较：

- Quick Instruction；
- 标准短 Prompt；
- 规则分类器；
- 小模型分类器；
- 不单独路由。

使用 Held-out 数据和跨时间重复。

---

## 9. 边界与失败模式

- 字段可能被 API 静默忽略；
- 输出标签未文档化；
- 模型版本更新改变行为；
- 与 Tools / Thinking / Streaming 组合不兼容；
- 专用任务可能只用于服务端内部；
- 多一步路由增加延迟；
- 分类错误可能选择错误工具或来源；
- 私有 Token 直接拼接可能破坏协议。

必须提供 Feature Flag、Fallback、Capability Version 和禁用开关。

---

## 10. 结论

Quick Instruction 的源码证据很有研究价值，但当前准确结论是：

1. 六类特殊 Token 和编码路径真实存在；
2. 公共 API 是否暴露 `task` 字段仍需 Wire Evidence；
3. 客户端不能直接根据编码源码实现未文档化协议；
4. 产品层应使用 Provider-Neutral Router 和标准回退；
5. 高风险决策不能只依赖短分类输出；
6. 价值必须用完整工作流的质量、延迟和成本验证。

源码确认“可能有什么能力”，Endpoint 实验决定“客户端现在能否可靠使用”。
