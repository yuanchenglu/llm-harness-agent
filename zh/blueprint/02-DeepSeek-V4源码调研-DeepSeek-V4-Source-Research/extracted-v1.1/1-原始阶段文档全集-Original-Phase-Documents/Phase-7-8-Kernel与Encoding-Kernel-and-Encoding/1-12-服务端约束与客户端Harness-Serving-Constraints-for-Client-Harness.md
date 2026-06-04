# 07-serving-constraints-for-client-harness.md — V4 Serving 物理约束对客户端 Harness 的影响 v0.1

> 基于 `kernel.py`、`inference/README.md`、模型卡精度说明。

---

## 1. 总体判断

DeepSeek V4 的本地推理不是面向普通用户桌面环境的默认形态。

原因：

```text
1. Pro 权重约 865GB，Base 约 1.61TB
2. 官方 demo 使用 model parallel
3. kernel 依赖 TileLang / CUDA
4. Pro 示例 MP=8
5. 核心路径是 FP4/FP8 custom kernels
```

因此 DeepSeek Agent 产品形态应是：

```text
默认：API / 云端推理
高级：用户自定义 API endpoint
专家：本地/私有化部署连接
```

而不是让普通 Mac/Windows 用户本地加载 V4。

---

## 2. 对桌面端产品的约束

### 2.1 不把“本地模型运行”作为 MVP 目标

MVP 应支持：

```text
DeepSeek 官方 API
兼容 OpenAI API endpoint
私有化 DeepSeek endpoint
自定义 base_url + api_key
```

不应默认承诺：

```text
本地直接运行 V4-Pro
本地直接运行 V4-Flash
普通消费级 GPU 推理 1M context
```

### 2.2 需要 Backend Capability Probe

不同部署后端可能差异很大：

```text
是否支持 1M context
是否支持 thinking
是否支持 max thinking
是否支持 tool calls
是否返回 cache hit/miss
是否支持 FIM
是否支持 reasoning_content
是否限流
```

DeepSeek Agent 应启动时探测或配置后端能力。

---

## 3. 成本/延迟模型

V4 serving 成本应分成：

```text
1. Cache miss prompt prefill
2. Cache hit prompt reuse
3. Decode output tokens
4. Thinking tokens / reasoning budget
5. Tool loop turn count
6. Pro/Flash route cost
```

UI 不应只显示：

```text
本次用了多少 tokens
```

而应显示：

```text
cache hit tokens
cache miss tokens
output tokens
thinking mode
model route
estimated marginal cost
```

---

## 4. Prefill vs Decode

从 `generate.py` 可见：

```text
first forward: prefill phase
subsequent forward: decode phase
```

这与 Agent 设计有关：

- 大上下文任务的第一轮最贵；
- 如果 prefix cache 命中，后续轮边际成本大幅降低；
- 反复修改 system prompt / tool schema 会破坏 prefix cache；
- 工具循环要尽量保持 stable prefix。

---

## 5. Local / Remote / API 三种后端

### 5.1 API 后端

默认：

```text
DeepSeek official API
```

优势：

- 用户门槛最低；
- 自动享受 DeepSeek serving 优化；
- 自动享受 context caching；
- 适合桌面产品 MVP。

### 5.2 Private Endpoint

企业客户：

```text
base_url
api_key
model mapping
capability profile
```

优势：

- 可接入国产算力部署；
- 可支持内网代码仓库；
- 成本和隐私可控。

### 5.3 Local Runtime

高级用户：

```text
torchrun / vLLM / SGLang / custom deployment
```

DeepSeek Agent 不直接实现本地推理，而是接入 endpoint。

---

## 6. Harness 组件要求

### 6.1 Cost Telemetry

必须记录：

```yaml
model: deepseek-v4-flash
thinking_mode: chat / thinking / max
prompt_tokens: ...
cache_hit_tokens: ...
cache_miss_tokens: ...
completion_tokens: ...
estimated_cost: ...
route_reason: ...
```

### 6.2 Cache Strategy Manager

职责：

```text
稳定 system prefix
稳定 tool schema
稳定 Memory / Skill index
动态信息 ride turn tail
减少工具 schema 重排
减少临时变量进入 prefix
```

### 6.3 Backend Profile

```yaml
backend_id: deepseek-official
supports_1m_context: true
supports_reasoning_effort: true
supports_tool_calls: true
supports_fim: true
returns_cache_metrics: true
max_output_tokens: 384000
recommended_max_thinking_context: 384000
```

---

## 7. 产品策略建议

DeepSeek Agent 早期产品应主打：

```text
“充分利用 DeepSeek 官方 API 的 V4 物理特性”
```

而不是：

```text
“桌面本地跑 DeepSeek V4”
```

本地/私有化应该是：

```text
连接用户已有 V4 endpoint
```

而不是：

```text
内置推理引擎
```
