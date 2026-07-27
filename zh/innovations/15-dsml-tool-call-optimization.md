# DSML 编码层研究：内部表示不等于客户端协议

> **证据等级：A1 + A0 + B**  
> - **A1**：固定版本 `encoding_dsv4.py` 可确认 DSML 特殊 Token、模板和参数编码逻辑存在。  
> - **A0（本项目 API Spike）**：公开 API 返回标准 OpenAI-compatible `tool_calls`，客户端不需要 DSML 解析器。  
> - **B**：DSML 是否减少 Token、降低生成错误或改善推理效率，仍需专用 benchmark。  
> 请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-15  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **关联**：[I-14 Reasoning Content 回传策略](14-reasoning-content-stripping.md) · [I-13 Byte-Stable Prefix 架构假设](13-byte-stable-prefix-architecture.md)

---

## 摘要

DeepSeek V4 的编码源码中存在 DSML（DeepSeek Markup Language）特殊 Token 和 XML 风格工具调用模板。这说明模型编码层可能使用专门格式表示工具调用。

但客户端 Harness 应以实际公开 API 契约为准。本项目 2026-07-16 的 API Spike 已观察到：

```text
客户端发送 OpenAI-compatible tools / JSON Schema
→ 服务端内部完成编码、模型生成和结果转换
→ 客户端收到标准 tool_calls
```

因此，以下早期结论已被否定：

- “任何接入 DeepSeek V4 的 Agent 都必须实现 DSML 解析器”；
- “公开 API 直接返回 DSML 文本”；
- “客户端不能继续使用标准 `tool_calls` 数据结构”。

DSML 当前最有价值的研究方向，不是让客户端绕过公共协议，而是理解：模型内部工具表示如何影响服务端行为、Token 使用、错误恢复和未来 Provider 能力。

---

## 1. 三层协议必须分开

### 1.1 客户端公共协议

Harness 实际发送和接收的结构，例如：

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string"}
          },
          "required": ["city"]
        }
      }
    }
  ]
}
```

响应中的标准结构：

```json
{
  "tool_calls": [
    {
      "id": "call_xxx",
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\":\"北京\"}"
      }
    }
  ]
}
```

这是 Provider Adapter 必须支持的契约。

### 1.2 服务端请求编译与结果转换

服务端可能执行：

```text
JSON Schema
→ 模型专用 Prompt / Token 表示
→ 模型输出
→ 结构化解析
→ 标准 API Response
```

客户端通常看不到这层，也不应根据 tokenizer 源码猜测线上服务的全部实现。

### 1.3 模型编码层

`encoding_dsv4.py` 中的 DSML 模板属于模型输入/输出编码逻辑。它可以证明某种内部表示存在，但不能单独证明：

- 公共 Endpoint 接受客户端直接提交 DSML；
- 公共 Endpoint 原样返回 DSML；
- 线上服务与公开源码使用完全相同版本；
- DSML 比 JSON 更省 Token 或更可靠。

---

## 2. 源码可以确认什么

### 2.1 DSML 特殊 Token

固定源码中定义了类似：

```python
dsml_token = "｜DSML｜"
```

工具调用模板使用 XML 风格标签：

```xml
<｜DSML｜tool_calls>
  <｜DSML｜invoke name="get_weather">
    <｜DSML｜parameter name="city" string="true">北京</｜DSML｜parameter>
  </｜DSML｜invoke>
</｜DSML｜tool_calls>
```

这可以支持以下 A1 结论：

> DeepSeek V4 编码实现包含模型专用的结构化工具调用表示。

### 2.2 字符串与非字符串参数区分

编码逻辑通过 `string="true|false"` 区分：

- 字符串直接作为文本内容；
- 数字、布尔、数组和对象继续使用 JSON 序列化。

这是一种内部类型编码设计。它可能减少字符串转义复杂度，但“节省多少 Token、是否降低错误率”仍是 B 级推论。

### 2.3 编码与解码逻辑

源码中存在 DSML 渲染和解析代码，说明完整编码链路需要处理：

- 标签边界；
- 工具名；
- 参数名；
- 参数类型；
- 嵌套值；
- 不完整输出和错误恢复。

这证明服务端或本地推理栈需要相应转换逻辑，但不能推出每个 API 客户端都要重复实现。

---

## 3. API Spike 修正

### 3.1 已观察行为

本项目的固定 Spike 记录显示：

```text
输入：标准 OpenAI-compatible tools
输出：标准 tool_calls
客户端：无需 DSML Parser
```

因此 Provider Adapter 的默认实现应：

1. 发送公开文档支持的标准 Tool Schema；
2. 读取结构化 `tool_calls`；
3. 校验 `name`、`arguments`、`id` 和 `finish_reason`；
4. 对无效 JSON Arguments 做明确错误处理；
5. 不依赖响应正文中的私有标记。

### 3.2 仍未确认的边界

当前 Spike 不能证明：

- 所有 Endpoint、区域和账户行为永久一致；
- 流式工具调用的每个 Chunk 字段完全稳定；
- 本地部署或原始推理 Endpoint 也返回标准结构；
- 未来 API 不会提供显式 DSML 模式；
- 服务端内部转换没有版本差异。

因此需要 Capability Snapshot，而不是把一次观察写死为永久协议。

---

## 4. 对 Harness 的正确启示

### 4.1 Provider Contract 优先

Provider Adapter 的优先级：

```text
真实 API 行为
> 官方 API 文档
> 官方 SDK
> 模型编码源码
> 第三方实现
> 工程推论
```

编码源码用于解释和提出实验，不用于绕过公开契约。

### 4.2 保持内部工具模型与 Wire Format 分离

建议 Runtime 内部使用统一类型：

```typescript
interface ToolCall {
  id: string;
  name: string;
  arguments: unknown;
  rawArguments?: string;
  provider: string;
  protocolVersion: string;
}
```

Provider Adapter 负责：

```text
内部 Tool Definition
↔ Provider Request
↔ Provider Response
↔ 内部 ToolCall
```

这样未来即使 Provider 暴露 DSML、JSON、Protobuf 或其他格式，Orchestrator、Policy 和 Tool Runtime 都不需要重写。

### 4.3 不要直接执行模型生成参数

无论服务端返回 JSON 还是其他格式，都必须：

- 验证工具名在允许列表中；
- 按 Schema 验证参数；
- 拒绝未知字段或按明确策略处理；
- 做路径、权限和副作用检查；
- 保存原始响应 Hash 和规范化参数；
- 对解析错误提供可恢复状态。

结构化格式只降低解析歧义，不提供安全保证。

### 4.4 Tool Schema 稳定性

为了便于诊断和可能的 Prefix Cache 复用：

- 工具按稳定规则排序；
- JSON Key 使用确定性序列化；
- Schema 计算 Fingerprint；
- 权限变化或 Schema 修复时主动更新版本；
- 不为了 Cache 命中保留已经撤销的工具权限。

---

## 5. 需要验证的研究问题

### RQ-1：公共 API 的 Wire Contract

矩阵：

```text
Flash / Pro
thinking / non-thinking
stream / non-stream
single / parallel / sequential tools
valid / invalid schema
valid / malformed arguments
```

记录：

- HTTP 状态；
- Response 字段；
- Chunk 字段；
- `finish_reason`；
- Tool Call ID；
- 错误类型；
- 下一轮是否可继续。

### RQ-2：DSML Token 效率

只有在可获得相同 Tokenizer 和相同语义表示时，才能比较：

```text
JSON representation token count
DSML representation token count
escaping overhead
schema size
argument size
```

不能根据字符数量估算 Token 数量，也不能仅凭特殊 Token 名称断言更省。

### RQ-3：生成可靠性

在固定任务集上比较：

```text
valid structured-call rate
argument schema pass rate
incorrect tool-name rate
truncated call rate
recovery success rate
```

如果公共 API 已完成 DSML→标准结构转换，客户端只能测量端到端结果，不能直接把收益归因于 DSML。

### RQ-4：本地推理与公共 API 差异

如果未来使用本地 V4 权重或低层推理接口，需要单独确认：

- 是否输出原始 DSML；
- 官方 Parser 是否可复用；
- Parser 的错误恢复行为；
- 与公共 API 的语义兼容性；
- 是否需要 Provider-specific Adapter。

本地推理结论不能自动外推到托管 API，反之亦然。

---

## 6. 反模式

### 6.1 从编码源码直接推导公共 API

错误链条：

```text
Tokenizer 中有 DSML
→ API 一定接收 DSML
→ API 一定返回 DSML
→ 客户端必须写 Parser
```

每一步都需要独立证据。

### 6.2 为了“模型原生”绕过官方协议

直接拼接私有 Token 可能造成：

- Endpoint 拒绝；
- Prompt Injection 面扩大；
- Tool Schema 与权限系统脱节；
- SDK 和服务端升级后不兼容；
- 调试、审计和错误处理复杂化。

除非官方提供稳定接口和兼容承诺，否则不应进入产品主路径。

### 6.3 把格式效率当作任务质量

即使 DSML 少用一些 Token，也不代表：

- 工具选得更对；
- 参数语义更准确；
- 副作用更安全；
- 任务首次完成率更高。

格式指标和任务指标必须分开。

---

## 7. 当前实现建议

```text
默认路径：OpenAI-compatible Tool API
内部表示：Provider-neutral ToolCall
验证层：Schema + Policy + Permission + Side-effect classification
遥测层：Protocol version + Tool schema fingerprint + Parse errors
实验路径：独立 DSML/tokenizer benchmark，不进入默认客户端执行链路
```

Provider Capability 建议记录：

```yaml
provider: deepseek
endpoint: <redacted-host-id>
model: deepseek-v4-pro
observed_at: 2026-07-16
request_tools_format: openai-compatible-json-schema
response_tool_calls_format: openai-compatible
dsml_visible_on_wire: false
source_commit: <fixed-commit>
limitations:
  - endpoint/account/time scoped
  - local inference not tested
```

---

## 8. 结论

DSML 是值得研究的模型编码机制，但当前客户端架构结论非常明确：

1. 编码层存在 DSML，不等于公共 API 直接暴露 DSML；
2. 本项目 API Spike 已否定“客户端必须实现 DSML Parser”；
3. Harness 应围绕公开 Provider Contract 和统一内部 ToolCall 类型构建；
4. DSML 的 Token、延迟和生成可靠性收益仍需专用 benchmark；
5. 即使格式更结构化，Tool Schema、权限、参数和副作用仍必须由 Runtime 验证。

源码用于提出问题，Wire Evidence 决定客户端实现。
