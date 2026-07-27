# Agent 可读文档结构：稳定摘要、内容寻址与按需读取

> **证据等级：B（工程设计提案）**  
> 本文修正早期“只要把核心结论放在文件前面，后续读取就会自动 Prefix Cache 全命中并节省 80% Token”的表述。文档排列、Harness 读取策略和 Provider Prefix Cache 是不同层；实际收益取决于请求组装是否保持共同前缀，以及 Agent 是否只读取需要的章节。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-05  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[04 稳定约束与可压缩历史分区](04-kv-cache-prefix.md)

---

## 摘要

大型项目文档常同时承担四种职责：

- 当前结论；
- 决策依据；
- 完整分析；
- 历史讨论和变更记录。

如果每次任务都全文读取，成本和干扰会随文档增长；如果只读摘要，又可能遗漏关键边界和证据。

更可靠的文档结构是：

```text
机器可读元数据
→ 当前结论与决策
→ Evidence Index
→ 主题化正文
→ 历史与附录
```

Harness 再根据任务选择：

```text
只读摘要
读取指定章节
按 Evidence Ref 获取原始材料
必要时全文读取
```

这首先是信息架构和检索设计；只有当请求组装保持实际共同前缀时，才可能产生 Provider Prefix Cache 收益。

---

## 1. 公开修正

### 1.1 文件前缀稳定不等于 API 请求前缀稳定

文档内容进入模型前，Harness 可能添加：

- System Prompt；
- Tool Schema；
- 用户问题；
- 文件路径和时间戳；
- Retrieval 包装；
- 其他文档片段。

即使文件前 500 Token 不变，只要它在最终请求中的前置内容、顺序或序列化发生变化，实际 Prefix Cache 行为也可能不同。

### 1.2 “追加尾部，只重算尾部”需要前提

只有在以下条件成立时才可能观察到共同前缀复用：

```text
同一 Provider / Model / Endpoint
相同序列化方式
相同前置消息
相同文档前缀
缓存仍有效
Provider 提供可观测的 Prefix Cache
```

因此不能把文件系统的 Append 操作直接等价为推理服务的增量计算。

### 1.3 早期 Token 节省数学不一致

早期版本同时写过：

```text
核心结论 U ≈ 0.3S
```

又写“节省率约 70% 或 >80%”。如果只缓存大小为 `U` 的稳定前缀，且每次仍发送剩余 `D = S-U`，理论上限更接近 `U/S`，不是 `D/S`。此外 Provider 计费、最小缓存块和请求包装会进一步改变结果。

因此本文不再给出未经实验的固定节省率。

### 1.4 稳定区不能永久不可变

核心结论会被新证据推翻。文档设计应支持：

- 版本化更新；
- 旧结论失效；
- 决策替代关系；
- 变更原因；
- 读者定位当前版本。

为了缓存而冻结错误结论，是负优化。

---

## 2. 设计目标

Agent 可读文档需要同时优化：

| 目标 | 含义 |
| --- | --- |
| 快速定位 | 前部明确当前结论和适用范围 |
| 可追溯 | 每个强结论能回到来源和 Evidence |
| 可更新 | 结论变化时有版本与替代关系 |
| 可检索 | 章节有稳定 ID、标题、标签和 Hash |
| 可选择读取 | 摘要、章节、Artifact、全文可分层加载 |
| 可验证缓存 | 请求 Fingerprint、Hit/Miss 和成本可测 |
| 人类可读 | 不为了机器结构牺牲基本阅读体验 |

---

## 3. 推荐结构

```markdown
---
doc_id: architecture-context-compiler
schema_version: 1
revision: 7
status: active
updated_at: 2026-07-27
supersedes: revision-6
owners: [runtime-team]
tags: [context, cache, evidence]
---

# Context Compiler 架构

## Current Summary

## Scope and Non-Goals

## Decision Register

## Evidence Index

## Architecture

## Failure Modes

## Validation

## Change Log

## Historical Discussion
```

### 3.1 Current Summary

只回答：

```text
当前结论是什么
适用范围是什么
仍有哪些未验证项
下一步是什么
```

不写营销语言，不把历史计划写成当前事实。

### 3.2 Scope and Non-Goals

明确文档不解决什么，防止后续 Agent 把相邻需求自动纳入范围。

### 3.3 Decision Register

```yaml
- decision_id: ADR-014
  status: accepted
  statement: Runtime 是唯一 Agent Loop 真源
  rationale_ref: section:architecture/runtime
  evidence_refs:
    - source:runtime-commit-abc
    - test:bridge-integration-22
  supersedes: null
```

### 3.4 Evidence Index

Evidence Index 只保存索引和摘要：

```text
source repository / commit
file and line range
experiment manifest
artifact hash
test report
accessed or generated date
limitations
```

原始大文件放在外部 Artifact 或独立目录，按需读取。

### 3.5 Historical Discussion

历史讨论保留价值，但默认不进入活跃上下文。每段应标记日期、状态和是否已被替代。

---

## 4. 稳定章节 ID 与内容寻址

标题可能变化，因此每个关键章节建议具有稳定 ID：

```html
<a id="decision-runtime-single-loop"></a>
```

或在机器索引中记录：

```yaml
section_id: decision-runtime-single-loop
heading: Runtime 单一真源
content_hash: sha256:...
revision: 3
```

用途：

- 精确引用；
- 识别章节是否变化；
- 只重新嵌入变化章节；
- 判断旧 Review 是否失效；
- 生成稳定 Retrieval Key。

Hash 不能替代语义版本。小改字也会改变 Hash，因此同时保留 Revision 和变更类型。

---

## 5. 读取策略

### 5.1 Level 0：Metadata

用于搜索和路由：

```text
doc_id
status
revision
tags
updated_at
```

### 5.2 Level 1：Summary + Scope

用于快速理解文档是否相关。

### 5.3 Level 2：Selected Sections

根据任务加载 Architecture、Failure Modes、Validation 等指定章节。

### 5.4 Level 3：Evidence

当需要证明结论时读取固定源码、报告、Diff 或 Test。

### 5.5 Level 4：Full Document

适用于：

- 全面审计；
- 大范围重构；
- 发现摘要与证据冲突；
- Retrieval 置信度低；
- 用户明确要求全文阅读。

Harness 必须记录实际读取层级，不能在只读 Summary 时声称“已完整审阅文档”。

---

## 6. Prompt Assembly 与 Cache

### 6.1 确定性组装

```text
Stable System Rules
Stable Tool Schema
Document Metadata
Document Summary
Selected Sections
Current User Task
```

要求：

- 稳定排序；
- 规范化换行和编码；
- 明确序列化版本；
- 不注入随机时间戳到稳定前缀；
- 动态信息放在尾部；
- 安全更新允许主动失效。

### 6.2 Fingerprint

```yaml
prompt_layout_version: 2
provider: deepseek
model: deepseek-v4-pro
stable_prefix_hash: sha256:...
document_revision: 7
selected_sections:
  - current-summary
  - decision-runtime-single-loop
```

### 6.3 遥测

```text
input tokens
selected document tokens
cache hit/miss tokens
TTFT
total latency
retrieval misses
source citation accuracy
task success
```

只有在任务质量不下降时，Cache 和 Token 指标才有意义。

---

## 7. 验证设计

比较三种策略：

```text
A. 每次全文读取
B. 只读自由摘要
C. 结构化 Summary + Selected Sections + Evidence on demand
```

任务集包括：

- 查询当前结论；
- 查找边界条件；
- 追溯某个决策的证据；
- 识别已被替代的旧结论；
- 根据文档执行修改；
- 发现摘要与正文冲突。

指标：

```text
answer correctness
current-version accuracy
source citation accuracy
missed constraint rate
input tokens
latency
cache hit/miss
human correction rate
```

需要使用多轮重复和 Held-out 问题，不能只用专门针对 Summary 编写的问题。

---

## 8. 文档质量 Gate

每份当前文档至少检查：

- 是否有当前状态和日期；
- 是否区分事实、推论和计划；
- 强结论是否有 Evidence Ref；
- 是否存在失效链接；
- 是否引用本地不存在路径；
- 是否有重复或冲突状态；
- 历史内容是否明确标记；
- Summary 是否与正文一致；
- Revision 是否递增；
- Secret 是否被脱敏。

可使用脚本自动检查元数据、链接、JSON、Hash 和状态短语，但语义一致性仍需要 Review。

---

## 9. 边界与风险

- Summary 会遗漏细节；
- Retrieval 会漏召回；
- 章节拆分过细会破坏整体语义；
- Stable Prefix 过大可能降低灵活性；
- 缓存行为随 Provider 变化；
- 人类阅读和机器解析需求可能冲突；
- 旧 Agent 可能不理解新 Front Matter；
- 内容 Hash 可能造成无意义的频繁失效。

因此必须允许全文回退、显式刷新和人工定位。

---

## 10. 结论

Agent 可读文档的核心不是“把 TL;DR 放前面就自动节省 80% Token”，而是：

1. 当前结论、范围、决策和证据分层；
2. 历史讨论默认不污染活跃工作集；
3. 章节具有稳定 ID、Revision 和内容 Hash；
4. Harness 可以按 Metadata、Summary、Section、Evidence、Full Document 分层读取；
5. Prompt Assembly 使用确定性结构，并实际测量 Cache；
6. 新证据推翻旧结论时，正确性优先于前缀稳定。

文档结构首先服务于准确检索和可追溯决策，Prefix Cache 只是可能获得的附加收益。
