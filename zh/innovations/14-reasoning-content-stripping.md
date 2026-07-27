# Reasoning Content 回传策略：协议正确性优先于 Token 优化

> **证据等级：A1 + A0/E3 + B**  
> - **A1**：固定实现源码可确认部分 Harness 和编码逻辑会条件保留或删除 reasoning 内容。  
> - **A0/E3（限定 Endpoint、账户和时间窗口）**：本项目协议实验表明普通多轮与 Tool Loop 的行为可能不同，且 HTTP 200 不代表字段语义生效。  
> - **B**：删除 reasoning 对质量、成本和 Cache 的净收益，需要按 Provider、模型、模式和任务复现。  
> 请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-14  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **关联**：[I-13 Byte-Stable Prefix](13-byte-stable-prefix-architecture.md)

---

## 摘要

推理模型的响应可能包含：

```text
visible content
tool calls
reasoning / thinking content
provider metadata
signatures or encrypted blocks
```

下一轮是否需要回传 reasoning，不存在跨 Provider 的统一答案。可能出现：

- 普通多轮允许删除；
- Tool Call 连续性要求完整回传；
- Provider 自动处理；
- SDK 重写字段；
- 某些字段仅用于展示；
- 某些字段带签名，不能修改；
- 同一 Provider 的不同 Endpoint 行为不同。

因此 Harness 不应使用全局 `strip_reasoning=true`，而应使用版本化 **Replay Policy**：

```text
Provider Capability
+ Response Shape
+ Tool State
+ Thinking Mode
+ Endpoint Evidence
→ Replay / Drop / Summarize / Reject Unknown
```

---

## 1. 公开修正

### 1.1 Reasoning 不是“100% 无价值 Token”

早期版本把回传 reasoning 写成纯浪费，并给出固定 Token 和金额示例。该表述过强。

Reasoning 可能：

- 是 Tool Call 协议连续性的一部分；
- 包含 Provider 要求的签名或状态；
- 被服务端缓存；
- 对后续推理有影响；
- 在某些模式中被 Provider 主动删除或重构。

只有在确认协议允许删除、任务质量不下降且 Usage 显示实际收益后，才能称为优化。

### 1.2 字段名不能跨 Provider 泛化

`reasoning_content`、thinking block、encrypted content、reasoning item 不是同一协议。内部 Runtime 应统一抽象，但 Wire Adapter 必须保留 Provider-specific 规则。

### 1.3 编码源码不等于托管 API Wire Contract

`encoding_dsv4.py` 中的 `_drop_thinking_messages` 可以证明编码实现存在相应预处理逻辑，但不能单独证明：

- 公共 API 客户端应复制该逻辑；
- 线上服务使用完全相同版本；
- Tool 场景的所有轮次都必须保留；
- 删除后一定节省某个固定数量 Token。

### 1.4 HTTP 200 不等于语义正确

删除字段后请求成功，只能证明服务端接受。还必须确认：

- 下一轮是否保持任务连续；
- Tool Result 是否被正确关联；
- 输出是否退化；
- Usage 是否变化；
- 错误是否在后续轮次才出现。

---

## 2. 消息内容分类

```typescript
type AssistantTurn = {
  visibleContent?: string;
  toolCalls?: ToolCall[];
  reasoning?: ReasoningPayload;
  providerMetadata?: Record<string, unknown>;
};
```

### 2.1 Visible Content

用于用户对话连续性，可以保留、摘要或在 Compaction 中重写，但需要遵守产品语义。

### 2.2 Tool Calls

通常必须与 Tool Results 保持 ID、顺序和状态一致。不得为了省 Token 删除关键调用记录。

### 2.3 Reasoning Payload

Provider-specific：

```typescript
type ReasoningPayload = {
  format: "plain_text" | "signed_block" | "encrypted" | "provider_item";
  rawRef: string;
  replayRequirement: "required" | "optional" | "forbidden" | "unknown";
  sensitivity: "restricted";
};
```

### 2.4 Provider Metadata

可能包含 ID、签名、状态和序列号。Adapter 不能随意丢弃未知字段后继续执行高风险流程。

---

## 3. Replay Policy

```yaml
policy_id: deepseek-thinking-tools-v3
provider: deepseek
endpoint_capability_version: 2026-07-27
conditions:
  thinking: true
  has_tools: true
action: replay_required_fields
fields:
  - role
  - content
  - reasoning_content
  - tool_calls
fallback_on_unknown: stop_and_probe
```

### 3.1 Actions

| Action | 含义 |
| --- | --- |
| `replay_exact` | 原样回传 Provider 要求结构 |
| `replay_required_fields` | 只保留能力矩阵确认必需字段 |
| `drop_reasoning` | 删除 reasoning，保留可见内容和工具状态 |
| `summarize_visible_content` | 只压缩可见对话，不碰协议状态 |
| `stop_and_probe` | 未知协议时停止或运行安全探针 |

### 3.2 默认安全策略

```text
协议未知 + Tool Side Effect
→ 不尝试激进删除
→ 保留服务端原始结构或停止
```

成本优化不能优先于 Tool Loop 正确性。

---

## 4. Capability Matrix

```yaml
provider: deepseek
model: deepseek-v4-pro
endpoint: <redacted-endpoint-id>
observed_at: 2026-07-27
modes:
  ordinary_thinking:
    replay_reasoning:
      accepted: true
      semantic_effect: unverified
    drop_reasoning:
      accepted: true
      continuity: observed_in_test_window
  tool_thinking:
    replay_reasoning:
      accepted: true
    drop_reasoning:
      accepted: inconsistent_or_unverified
limitations:
  - endpoint/account/time scoped
  - hosted API behavior may differ from encoding source
```

每条结论必须绑定：

- Request Fixture；
- Response Shape；
- HTTP Status；
- 多轮后续结果；
- Usage；
- 重复次数；
- 时间和 Endpoint。

---

## 5. Adapter 架构

```text
Session Store
→ Provider-neutral AssistantTurn
→ Replay Policy
→ Provider Wire Builder
→ Raw Request Fingerprint
→ Response Recorder
```

### 5.1 Session Store

可以保存受限引用，但不应默认把完整 reasoning 暴露给普通 UI、日志或 Diagnostics。

### 5.2 Wire Builder

只在发送时应用 Policy，避免为了某个 Provider 永久破坏 Session 原始结构。

### 5.3 Unknown Fields

Provider 返回新字段时：

- 记录字段集合和版本；
- 不打印敏感内容；
- 在 Tool Loop 中默认保守处理；
- 触发 Capability Review。

---

## 6. 安全与隐私

### 6.1 Reasoning 敏感性

Reasoning 可能包含：

- 用户私有信息；
- Secret 的意外复述；
- 内部策略；
- 未验证推断；
- 安全分析细节。

默认：

- 不进入普通日志；
- 不进入 Diagnostics；
- 不作为长期 Memory；
- 不作为 Skill 来源正文；
- 只保存必要的结构和 Hash/Ref。

### 6.2 展示与协议分离

Provider 要求回传，不代表必须向用户展示；用户可查看的解释应是经过产品设计的简明依据，而不是原始隐藏推理。

### 6.3 Tool Injection

Reasoning 中出现的命令或 Tool 建议不具有执行权。Tool Calls 仍需 Schema、Policy、Permission 和 Approval。

---

## 7. Compaction

Compaction 应分别处理：

```text
visible conversation
protocol-required tool state
evidence refs
reasoning payload
```

### 7.1 可压缩

- 历史可见回答；
- 已关闭讨论；
- 重复说明。

### 7.2 不得随意压缩

- 未完成 Tool Call 链；
- Tool Call ID / Result 配对；
- Approval 和 ChangeSet 状态；
- Provider 要求的签名块；
- 当前错误和恢复条件。

### 7.3 Session Rebuild

如果协议要求和历史结构无法兼容，创建明确的 Compaction/Reset 点，并记录：

```text
old session ref
summary artifact
retained evidence
provider reset reason
cache reset reason
```

---

## 8. 实验设计

### 8.1 协议矩阵

```text
ordinary / tools
thinking / non-thinking
replay / drop / modified
stream / non-stream
Flash / Pro
SDK / raw HTTP
```

### 8.2 连续性任务

- 多轮代码修改；
- 顺序 Tool Calls；
- 并行 Tool Calls；
- Tool Failure 后重试；
- Compaction 后继续；
- Provider/模型切换。

### 8.3 指标

```text
HTTP success
next-turn continuity
tool-call completion
first-pass task success
incorrect tool association
input tokens
cache hit/miss
latency
cost per successful task
```

### 8.4 结果纪律

- 不用单次请求下结论；
- 区分接受与生效；
- 报告失败样本；
- 随机化执行顺序；
- 跨时间重复；
- 价格写入快照，不写死长期金额。

---

## 9. 决策规则

允许 `drop_reasoning` 进入默认策略，至少满足：

1. Provider/Endpoint 明确允许或实验稳定支持；
2. 普通多轮和 Tool Loop 分开验证；
3. 任务质量不下降；
4. 没有 Tool State 丢失；
5. Token/成本收益可重复；
6. 有 Feature Flag 和快速回滚；
7. Capability 变化会触发重新验证。

---

## 10. 边界与风险

- Provider 协议快速变化；
- SDK 与 Raw HTTP 行为不同；
- 服务端可能自动重写消息；
- Tool 场景可能只在后续轮次失败；
- 删除 reasoning 可能降低某些任务质量；
- 保留 reasoning 可能增加成本和隐私风险；
- 线上 Endpoint 与公开源码不一致；
- Usage 字段可能不完整。

因此需要 Capability Version、保守默认、Telemetry 和回滚。

---

## 11. 结论

Reasoning Content 处理不是“全部回传”与“全部删除”的二选一。

可靠 Harness 应：

1. 区分可见内容、Tool State、Reasoning 和 Provider Metadata；
2. 以 Provider/Endpoint Capability 决定 Replay Policy；
3. 普通多轮和 Tool Loop 分开处理；
4. 在 Wire Builder 层应用策略，不破坏内部 Session 模型；
5. 对未知协议保守停止或探测；
6. 同时评估连续性、任务成功、Token、Cache、成本和隐私；
7. 不把原始 reasoning 当成用户解释、Memory 或 Skill 素材。

每个 Token 都应证明价值，但协议正确性必须先证明。
