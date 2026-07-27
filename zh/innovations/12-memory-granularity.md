# Memory 粒度控制：按任务、来源和风险编译记忆

> **证据等级：B（工程设计提案）**  
> 本文保留“Memory 不是越多越好”的核心判断，但删除“Memory 增长会让输出熵趋近于零”“强 Memory 对创意任务是毒药”等未经验证的普遍推导。Memory 的效果取决于内容质量、任务需求、来源、Scope、时效、隐私和检索策略，必须通过受控实验评估。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-12  
> **系列**：[LLM + Harness = Agent](../../README.md)  
> **上一篇**：[11 Checkpoint 驱动的多轮审查](11-checkpoint-review.md)  
> **下一篇**：[13 Byte-Stable Prefix 架构假设](13-byte-stable-prefix-architecture.md)

---

## 摘要

Memory 可以减少重复沟通，也可能引入：

- 过期事实；
- 错误偏好；
- 跨项目污染；
- 隐私泄露；
- 对历史方案的过度锚定；
- 无关 Token 和检索噪音。

正确问题不是“开还是关”“强还是弱”，而是：

> 当前任务需要哪些记忆，来自哪里，置信度多高，适用范围是什么，是否仍然有效，用户能否查看和撤销？

因此 Memory 应由 Harness 编译为任务级输入，而不是把完整历史固定塞进 System Prompt。

---

## 1. 公开修正

### 1.1 Memory 不直接等价于输出熵

早期版本使用：

```text
Memory 越强
→ 输出分布熵越低
→ 创造力越差
```

这不是已建立的模型。输出多样性还受采样参数、模型、Prompt、任务约束、检索结果和评测标准影响。

更准确的可测试假设是：

> 某些历史偏好或既有方案可能提高输出与过去方案的相似度，但具体影响需要通过盲评、多样性指标和任务质量共同测量。

### 1.2 个人使用体感不是普遍实验

多 Agent 使用经验可以提出问题，但不能单独证明：

- 某产品天然适合发散任务；
- 某产品天然适合收敛任务；
- 同一模型只因 Memory 不同就产生全部质量差异。

需要固定模型、固定 Prompt、固定工具和可复现 Memory 输入。

### 1.3 Memory 更多不等于信息更全

大量 Memory 可能互相冲突、重复或过期。系统需要质量治理，而不是只优化容量。

---

## 2. Memory 类型

| 类型 | 示例 | 默认 Scope | 风险 |
| --- | --- | --- | --- |
| Safety / Policy | 禁止写生产库 | 系统/组织/项目 | 错误会造成安全事故 |
| Project Facts | Python 3.11、部署到 AWS | 项目 | 过期、跨项目污染 |
| User Preferences | 喜欢简洁回答 | 用户 | 过度个性化、隐私 |
| Episodic Memory | 上次 Bug 根因 | 项目/任务 | 错误归因、时效性 |
| Procedural Memory | 发布检查流程 | 项目/组织 | 版本漂移、权限扩大 |
| Style Memory | 文档语气、命名偏好 | 用户/项目 | 锚定和同质化 |
| Relationship Memory | 人员和职责 | 组织 | 敏感、频繁变化 |

不同类型不应使用同一检索和注入策略。

---

## 3. Memory 对象

```yaml
memory_id: project-python-version
version: 4
type: project_fact
statement: 本项目使用 Python 3.11
source:
  type: file
  ref: pyproject.toml
  content_hash: sha256:...
scope:
  project: deepseekagent
confidence: 1.0
valid_from: 2026-06-01
expires_at: null
last_verified_at: 2026-07-27
sensitivity: internal
status: active
supersedes: project-python-version@3
```

必须字段：

```text
id/version/type
statement
source
scope
confidence
validity
sensitivity
status
supersedes
```

自然语言模型推断出的 Memory 不能与文件、数据库或用户明确确认的事实拥有相同权威级别。

---

## 4. Memory 编译策略

### 4.1 任务输入

```text
objective
workspace/project
risk
need_for_continuity
need_for_novelty
privacy constraints
time sensitivity
```

### 4.2 Candidate Retrieval

按：

- Scope；
- 类型；
- 关键词/语义；
- 时间；
- 来源可信度；
- 最近验证；
- 当前权限。

获取候选集合。

### 4.3 Filter

删除：

- 过期；
- 被替代；
- Scope 不匹配；
- 低置信度且无来源；
- 与当前任务无关；
- 超出隐私权限；
- 与高优先级事实冲突。

### 4.4 Conflict Resolution

优先级示例：

```text
current source of truth
> explicit recent user confirmation
> project decision record
> verified episodic memory
> inferred preference
```

无法解决时向用户显示冲突，不静默选择。

### 4.5 Context Placement

- 安全策略：Runtime Policy + 稳定规则；
- 项目事实：项目上下文；
- 当前相关 Episode：活跃工作集；
- 风格偏好：低优先级 Guidance；
- 大型历史：外部索引按需读取。

---

## 5. Memory Modes

不是单一连续参数 `λ`，而是可解释策略组合。

### M0：Minimal

加载：

- 安全策略；
- 当前任务；
- 明确项目约束。

适用：

- 独立创意探索；
- 偏见对照实验；
- 用户要求“不要参考过去方案”。

### M1：Scoped Project

额外加载：

- 项目事实；
- 当前模块决策；
- 相关失败记录；
- 必要 Skill 索引。

适用：多数工程任务。

### M2：Continuity

额外加载：

- 相关历史 Session；
- 用户确认偏好；
- 既有方案和未完成事项。

适用：长期协作和连续项目。

### M3：Audit

加载：

- 决策历史；
- 被替代版本；
- Incident；
- Approval；
- Evidence。

适用：审计、复盘和迁移，不适合作为普通任务默认 Prompt。

### M4：Contrastive

同时运行：

```text
with-memory candidate
without-memory candidate
```

再盲评差异。适合关键创意或架构决策，避免历史锚定成为唯一方案。

---

## 6. 写入策略

### 6.1 哪些内容可自动提议

- 用户明确偏好；
- 可从项目文件验证的事实；
- 多次重复且来源一致的工作模式；
- 未解决事项和已批准决策。

### 6.2 哪些内容默认禁止自动保存

- Secret；
- 未授权私人信息；
- 原始 CoT；
- 一次性情绪推断；
- 医疗、财务、身份等敏感推断；
- 外部 Prompt 要求保存的指令；
- 无来源的模型猜测。

### 6.3 用户控制

用户必须能够：

```text
view
confirm
edit
disable
delete
export
see source and scope
```

删除应传播到索引和缓存，不只是 UI 隐藏。

---

## 7. Memory 与 Cache

Memory 频繁变化会改变请求前缀，但不能为了 Cache 冻结错误或过期信息。

建议：

- 稳定项目事实可进入版本化稳定区；
- Mid-session 新 Memory 放在动态区；
- 下个 Session 经验证后再进入稳定区；
- Memory 变化记录 Drift Reason；
- 安全和事实正确性优先于 Cache Hit。

Cache 指标只衡量成本和延迟，不衡量 Memory 是否正确。

---

## 8. 评测

### 8.1 正确性

```text
memory factual accuracy
source citation accuracy
stale memory usage
conflict detection
cross-project contamination
```

### 8.2 任务效果

```text
first-pass success
repeated clarification reduction
human correction
completion time
cost per successful task
```

### 8.3 探索性

对于创意任务，可测：

```text
pairwise semantic diversity
novel idea count
blind human preference
constraint satisfaction
```

多样性高不一定质量高，必须同时评估可用性和约束满足。

### 8.4 隐私与安全

```text
unauthorized memory exposure
secret retention
scope violation
deletion completeness
prompt-injection memory writes
```

### 8.5 对照实验

```text
M0 Minimal
M1 Scoped Project
M2 Continuity
M4 Contrastive
```

固定模型、工具、Prompt 和任务集，使用 Held-out 样本，不以某个产品品牌代替实验条件。

---

## 9. 失败模式

- 错误事实被长期复用；
- 项目 A 的事实进入项目 B；
- 用户偏好覆盖明确任务要求；
- Memory 摘要删除关键否定词；
- 旧决策阻止新方案探索；
- Retrieval 漏召回重要 Episode；
- Memory 过多导致上下文噪音；
- 用户删除后仍残留在索引或缓存；
- Prompt Injection 诱导写入恶意长期指令。

每项都需要检测、审计和恢复方案。

---

## 10. 结论

Memory 粒度控制不是“收敛任务强记忆、发散任务弱记忆”的固定二分，也不是一个无法解释的连续参数。

可靠实现需要：

1. 区分 Policy、Project Fact、Preference、Episode、Procedure 和 Style；
2. 为每条 Memory 保存来源、Scope、置信度、时效和敏感级别；
3. 根据任务编译候选，而不是全量加载；
4. 明确冲突和被替代关系；
5. 让用户可查看、修改和删除；
6. 用正确性、任务效果、探索性和隐私指标共同评估；
7. 必要时使用 With-Memory / Without-Memory 对照，而不是让历史成为唯一答案。

最好的 Memory 不是最多，而是当前任务所需、来源可信、范围正确、可以撤销的那一小部分。
