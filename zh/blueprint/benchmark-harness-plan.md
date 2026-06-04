# DeepSeek API 协议与 Prefix Cache Benchmark Harness：详细执行计划

> 状态：**计划已细化，尚未开始实现或运行实验**  
> 日期：2026-06-04  
> 唯一下一步：建立可复现的 DeepSeek API 协议与 Prefix Cache Benchmark Harness。实验结果出来前，不据此定稿 DeepSeek Agent 的上下文架构、推理回传策略或 Cache-First 优先级。

## 1. 为什么先做这件事

当前理论文档与源码调研已经提出多个可能影响产品架构的判断，但其中最关键的两个基础问题仍缺少同一套真实 API 实验回答：

1. **协议事实是什么**：不同模型、思考模式、工具调用、流式模式下，哪些字段必须发送、可以省略、会被忽略或会触发错误？
2. **Prefix Cache 的真实行为是什么**：哪些序列化变化会导致命中下降，命中对成本和延迟到底有多大影响，稳定性如何？

如果这两点没有验证，后续的上下文编译、工具注册、轨迹保存、模型路由和成本优化都可能建立在错误假设上。因此本 Harness 不是普通性能脚本，而是后续架构决策的**事实底座**。

## 2. 全局视角：它会约束哪些产品层

| 产品层 | 当前未决问题 | 本 Harness 提供的证据 | 可能被优化的方向 |
|---|---|---|---|
| Provider Adapter | DeepSeek 不同模式的字段规则是否一致 | 协议兼容矩阵与错误样本 | provider-aware 请求编译器 |
| Context Compiler | 如何组织稳定前缀与动态历史 | Prefix 变异实验 | byte-stable / semantic-stable 前缀策略 |
| Tool Runtime | 工具调用期间如何保存 reasoning 与 tools | 多轮工具调用协议实验 | 工具状态机、轨迹格式、工具目录稳定化 |
| Observability | 如何判断命中、成本和错误原因 | 统一 trace 与 usage 记录 | 请求指纹、cache telemetry、错误分类 |
| Cost & Latency | Cache 是否值得成为核心约束 | 命中率、成本、TTFT/总延迟对比 | 优先优化成本、延迟，或降低 Cache-First 优先级 |
| Router | 哪种模式适合哪类任务 | 仅提供协议与成本基础数据 | 后续路由实验的输入，不在本阶段实现 |

### 本阶段明确不做

- 不评判模型智能高低；
- 不实现 planner/executor、reviewer、skills 或 memory；
- 不比较其他供应商；
- 不因单次 cache hit 就宣布架构有效；
- 不在协议与缓存结果出来前定稿产品架构。

## 3. 核心研究问题与验收标准

### RQ-1：协议规则能否被机器化描述？

**验证要点**

- `deepseek-chat`、思考模式及可用模型标识的真实响应结构；
- 非流式与流式响应字段是否一致；
- `reasoning_content` 在普通多轮、工具调用中分别应 drop、replay 还是会被忽略；
- `tools`、`tool_choice`、strict/schema 等字段的支持与错误行为；
- SDK 与原始 HTTP 请求是否产生相同语义；
- 无效参数、缺失字段、错误消息的稳定性。

**验收标准**

形成机器可读的 capability matrix；每条结论至少有请求 fixture、脱敏响应、HTTP 状态、运行时间和文档快照来源。协议结论不能只来自 README 或一次成功请求。

### RQ-2：Prefix Cache 命中由哪些变化决定？

**验证要点**

- 完全相同请求重复发送是否稳定命中；
- system、tools、历史消息、当前用户消息发生变化时，命中 token 如何变化；
- JSON key 顺序、空白、Unicode、工具顺序等“语义相同但字节可能不同”的变化是否影响命中；
- prefix 变化位置与命中 token 的关系；
- cache 建立延迟、存续时间、并发请求和重复运行的方差；
- 长前缀、请求边界及共同前缀学习行为。

**验收标准**

每个核心变体至少多次重复，记录 `prompt_cache_hit_tokens`、`prompt_cache_miss_tokens`、输入 token、首 token 延迟、总延迟和估算成本；能够区分“无命中”“命中不稳定”和“命中但收益有限”。

### RQ-3：Cache-First 是否值得成为 DeepSeek Agent 的架构约束？

**验证要点**

- 在代表性 Agent 请求中，稳定前缀占输入 token 的比例；
- 命中对成本、TTFT 和总延迟的实际改善；
- 为保持前缀稳定所增加的复杂度、正确性风险与工具暴露成本；
- Cache 优化是否与工具动态发现、权限收缩、上下文纠错冲突。

**验收标准**

只在收益可重复、显著且不牺牲正确性/安全性时，才把 byte-stable prefix 提升为架构约束；否则降级为局部成本优化。

## 4. Harness 目标形态

计划实现为一个小型、可复现、可扩展的实验工具，而不是一次性脚本。

```text
benchmark-harness/
├── README.md                 # 运行方式、限制、证据等级
├── pyproject.toml            # 锁定依赖与命令入口
├── config/
│   ├── models.example.yaml   # 模型/端点配置，不含密钥
│   └── pricing.example.yaml  # 可更新的价格快照
├── fixtures/
│   ├── protocol/             # 协议请求样本
│   └── prefix/               # 可控前缀变体
├── src/
│   ├── request_builder.py    # 确定性请求构造与 canonicalization 开关
│   ├── raw_http_client.py    # 原始 HTTP 基线
│   ├── sdk_client.py         # SDK 对照
│   ├── recorder.py           # 脱敏 trace 与 usage
│   ├── metrics.py            # latency/token/cache/cost 指标
│   └── runner.py             # 矩阵执行、重试与速率控制
├── tests/                    # 不调用付费 API 的单元/fixture 测试
└── results/<run-id>/         # manifest、原始脱敏记录、汇总报告
```

### 每次运行必须记录

- UTC 时间、Harness Git commit、依赖版本；
- API base URL、模型标识、模式和参数；
- 实验 ID、随机种子、重复次数、执行顺序；
- 请求的规范化指纹与脱敏后的请求结构；
- HTTP 状态、错误类别、响应字段集合；
- prompt/output/cache hit/cache miss tokens；
- TTFT、总延迟、重试次数与估算成本；
- 官方文档快照日期及已知服务状态异常。

密钥、完整 CoT、用户私有内容不得进入结果文件或 Git。

## 5. 分阶段执行计划

## Phase 0：冻结事实边界与实验配置

### 工作项

1. 保存本轮官方文档 URL、访问日期和关键协议声明；
2. 记录待测 base URL、模型标识、SDK 版本和账户区域；
3. 建立价格配置文件，价格不写死在计算逻辑中；
4. 定义测试预算、速率限制、最大重试与停止条件；
5. 定义脱敏规则和结果目录格式。

### 验证要点

- 配置是否足够复现实验；
- 密钥是否只从环境变量读取；
- 价格或模型变化时是否无需修改核心代码；
- 是否能明确区分“官方文档声明”和“本次实测观察”。

### 结果差异与计划变动

| 结果 | 计划变化 |
|---|---|
| 模型/端点与文档一致 | 进入 Phase 1 |
| 模型标识、字段或文档存在冲突 | 先建立版本化 capability snapshot，再执行实验 |
| 无可用 API key、余额或受限权限 | 只完成离线 Harness 和 mock 验证；真实结论保持未验证 |
| 价格频繁变化 | 报告只输出 token 指标与价格快照下的估算，不输出长期成本承诺 |

**Gate 0**：能够安全、可追踪地发出最小请求，否则不得开始批量实验。

## Phase 1：建立最小可复现 Harness

### 工作项

1. 实现 raw HTTP 与 SDK 两条请求路径；
2. 实现确定性 fixture 构造、请求指纹和 JSONL recorder；
3. 实现单次运行 manifest、重试策略和预算保护；
4. 实现离线单元测试：序列化稳定性、脱敏、成本计算、统计汇总；
5. 用最小非敏感 prompt 做 smoke test。

### 验证要点

- 同一 fixture 是否生成一致的请求指纹；
- recorder 是否保留必要字段且不泄漏密钥/CoT；
- SDK 与 raw HTTP 的实际 wire payload 是否存在差异；
- 网络失败、429、5xx 是否与协议错误分开统计；
- 重试是否会污染 cache 实验。

### 结果差异与计划变动

| 结果 | 计划变化 |
|---|---|
| SDK 与 raw HTTP 语义一致 | 后续以 raw HTTP 为主、SDK 为抽样对照 |
| SDK 自动改写/丢弃字段 | 协议实验以 raw HTTP 为权威，并新增 SDK 兼容层测试 |
| 无法稳定测量 TTFT | 延迟结论降级，只以总延迟和 usage 为主 |
| 重试显著影响 cache | cache 实验禁用自动重试，失败样本单独重跑 |

**Gate 1**：离线测试通过，smoke test 可复现，结果可脱敏审计。

## Phase 2：DeepSeek API 协议真值表

### 实验矩阵

| ID | 变量 | 需要验证的事实 |
|---|---|---|
| P01 | 最小 chat 请求 | 必填字段、基本响应结构 |
| P02 | 非流式 vs 流式 | chunk 字段、usage、结束原因与错误差异 |
| P03 | thinking 开/关或模型模式 | `reasoning_content` 的出现条件与参数限制 |
| P04 | 普通多轮中 drop/replay reasoning | 是否忽略、接受或报错 |
| P05 | 工具调用中 drop/replay reasoning | 工具调用链继续推理所需字段 |
| P06 | tools 全量、空数组、缺失 | 协议是否要求每轮完整工具目录 |
| P07 | tool schema、strict、tool choice | 支持范围与错误行为 |
| P08 | 无效/不支持参数 | HTTP 状态、错误类型、是否静默忽略 |
| P09 | SDK vs raw HTTP | SDK 是否改变协议语义 |
| P10 | 中断、超时、重试 | 幂等性与轨迹恢复边界 |

### 验证要点

- 成功不等于语义正确：必须检查响应字段、finish reason 和下一轮是否可继续；
- “被忽略”与“被接受并生效”必须分开；
- 工具调用至少覆盖一次完整的 assistant → tool → assistant 链；
- 对文档冲突必须保留最小复现样本，不自行猜测原因。

### 结果差异与计划变动

| 观察结果 | 对产品计划的影响 |
|---|---|
| 普通多轮 replay reasoning 报错或无效 | 默认跨 user turn 丢弃，并在 Provider Adapter 强制清理 |
| 工具调用期间必须 replay reasoning | 将 reasoning 作为 tool-loop 临时状态保存，不能全局 stripping |
| 工具调用期间也无需 replay | 简化轨迹状态，但仍保存可观测摘要而非假定所有 provider 相同 |
| 不支持参数被静默忽略 | 增加请求前 capability validation，禁止把“请求成功”当成参数生效 |
| raw HTTP 与 SDK 不一致 | DeepSeek Adapter 固定一条权威路径，并对 SDK 加兼容测试 |
| 协议随模型模式明显分叉 | 建立按 provider + model + mode 的 capability matrix，禁止全局规则 |

**Gate 2**：协议矩阵可以驱动一个确定性的请求编译器；无法确认的格子明确标记为未知。

## Phase 3：Prefix Cache 因果实验

### 3.1 基线与稳定性

| ID | 变量 | 目的 |
|---|---|---|
| C01 | 完全相同请求重复发送 | 确认 cache telemetry 与基础命中率 |
| C02 | 间隔时间与重复次数 | 测量建立延迟和短期稳定性 |
| C03 | 串行 vs 低并发 | 判断并发是否影响建立或命中 |
| C04 | 不同运行日/时段 | 区分架构规律与服务波动 |

### 3.2 变异位置

| ID | 只改变的区域 | 需要观察 |
|---|---|---|
| C10 | system 开头/中间/结尾 | 前缀破坏位置与 hit token 的关系 |
| C11 | tools 列表及单个 schema | 工具目录变化的缓存代价 |
| C12 | 历史 assistant/tool 消息 | 多轮轨迹如何影响命中 |
| C13 | 最后一个 user 消息 | 稳定前缀是否仍可命中 |
| C14 | 文档内容与问题后缀 | 长文档复用的收益 |

### 3.3 语义相同、表示不同

| ID | 变体 | 需要观察 |
|---|---|---|
| C20 | JSON key 顺序 | 服务端序列化前后规则 |
| C21 | tools 顺序 | 是否需要稳定工具排序 |
| C22 | 空白、换行、Unicode 形式 | byte-stable 的必要程度 |
| C23 | 可选字段缺失 vs 显式默认值 | 请求 canonicalization 是否有价值 |
| C24 | SDK vs raw HTTP 表示 | 客户端序列化对命中的影响 |

### 3.4 Agent 代表性场景

| ID | 场景 | 需要观察 |
|---|---|---|
| C30 | 固定 system + 固定 tools + 变化任务 | 标准 Agent 前缀收益 |
| C31 | 固定 system + progressive tools | 减少工具面的收益与缓存损失 |
| C32 | 多轮工具调用 | reasoning/tool trajectory 对缓存的影响 |
| C33 | 长仓库/文档前缀 + 多问题 | 文档分析场景收益 |
| C34 | 权限或策略更新 | 正确性要求变化时是否应主动牺牲命中 |

### 统计与判定方法

- 核心样本执行 warm-up 后至少重复多次，并随机化变体顺序；
- cache 命中以 API 返回的 hit/miss token 为主，不用延迟反推；
- 延迟同时报告中位数、p95 与样本量，不只报告最好结果；
- 成本报告区分命中输入、未命中输入和输出；
- 记录失败率与方差，避免把 best-effort cache 写成确定承诺；
- 每个结论保留反例与边界条件。

### 结果差异与计划变动

| 观察结果 | 对后续架构的影响 |
|---|---|
| 相同请求仍经常不命中 | Cache-First 降级为 best-effort 成本优化，不承担正确性设计职责 |
| 命中稳定且成本/延迟收益显著 | 建立稳定前缀层、漂移检测和 cache telemetry |
| 命中显著降成本但不改善延迟 | 产品目标写成成本优化，不宣传性能加速 |
| 工具目录变化造成大面积 miss | 优先稳定工具排序与 schema；再评估 progressive disclosure，但不违反协议 |
| 仅字节变化就导致 miss | 引入确定性序列化、canonicalization 和 prefix fingerprint |
| 语义相同变体仍可稳定命中 | byte-stable 要求降级为 semantic/prefix-unit 稳定，减少不必要复杂度 |
| 长文档复用收益高 | 优先开发 document-prefix 工作流 |
| 权限/策略更新与命中冲突 | 正确性和安全优先，显式使缓存失效，不追求命中率 |
| 收益小于维护复杂度 | 不把 Cache-First 设为产品核心架构，只保留观测与局部优化 |

**Gate 3**：能够用实测数据回答 Cache-First 是“核心约束、局部优化，还是暂不投入”。

## Phase 4：综合决策与架构回写

### 必须产出的决策记录

1. **DeepSeek capability matrix**：按模型/模式列出字段规则；
2. **Prefix cache behavior matrix**：按变异类型列出命中变化；
3. **成本与延迟报告**：含样本量、方差、价格快照和限制；
4. **协议状态机草案**：普通轮次与工具轮次如何处理 reasoning；
5. **Context Compiler ADR**：是否采用稳定前缀、稳定到什么程度；
6. **未决问题清单**：不把未知项包装成结论。

### 最终决策树

```text
协议是否按模型/模式分叉？
├─ 是 → Provider Adapter 必须 capability-driven
└─ 否 → 可共享默认路径，但保留版本探测

工具调用是否要求 replay reasoning？
├─ 是 → reasoning 进入 tool-loop 临时状态；跨普通轮次按协议清理
└─ 否 → 简化轨迹，但不得推广到其他 provider

Prefix Cache 是否稳定且收益显著？
├─ 是 → Context Compiler 加稳定前缀、fingerprint、漂移告警
├─ 仅成本显著 → 作为 FinOps 优化，不承诺延迟收益
└─ 否 → 降低 Cache-First 优先级，先优化正确性与上下文质量

工具目录是否是主要 cache 破坏源？
├─ 是 → 稳定排序/schema + 评估 progressive disclosure
└─ 否 → 不为缓存过早重构工具系统
```

## 6. 优先级、预算与停止条件

### P0：必须完成

- Harness 可复现骨架与脱敏 recorder；
- reasoning 普通多轮/工具调用协议；
- 完全重复、前缀位置变化、tools 变化的 cache 实验；
- capability/cache matrix 与综合 ADR。

### P1：在 P0 稳定后完成

- SDK/raw HTTP 差异；
- 序列化、Unicode、默认值变体；
- 并发、时间窗口、长文档场景。

### P2：只在数据表明值得时扩展

- 更大规模长期稳定性实验；
- progressive disclosure 原型；
- routing、planner/executor 或 reviewer benchmark。

### 停止条件

出现以下任一情况时暂停批量实验并先修正 Harness：

- 无法证明请求与结果一一对应；
- 结果文件可能泄漏密钥、CoT 或私有内容；
- 429/5xx/网络错误占比足以污染结论；
- 服务版本变化导致前后样本不可比较；
- 超出预设费用或请求预算；
- 重复实验无法区分 Harness bug 与服务方差。

## 7. 风险与控制

| 风险 | 控制方式 |
|---|---|
| API 和模型持续更新 | 每次运行保存日期、模型标识、文档快照与 Harness commit |
| Cache 为 best-effort，结果波动 | 多次重复、跨时段抽样、报告方差与失败率 |
| 付费实验失控 | dry-run、请求/Token/金额预算、硬停止开关 |
| CoT 或密钥泄漏 | 默认不保存完整 CoT；字段级脱敏；提交前 secret scan |
| SDK 隐式改写请求 | raw HTTP 基线 + SDK 对照 |
| 为命中率牺牲正确性 | 权限、策略、工具和事实更新优先触发缓存失效 |
| 将相关性误判为因果 | 每次只改变一个变量，并保存对照组 |

## 8. 完成定义

本阶段只有同时满足以下条件才算完成：

- [ ] Harness 代码、fixtures、配置示例和离线测试可在无密钥环境运行；
- [ ] 真实 API 运行可用一个命令复现，并受预算保护；
- [ ] 协议矩阵覆盖普通多轮、思考模式和工具调用；
- [ ] Cache 矩阵覆盖完全重复、位置变异、tools、序列化和代表性 Agent 场景；
- [ ] 结果包含原始脱敏证据、汇总统计、限制与反例；
- [ ] 明确决定 Cache-First 的架构级别；
- [ ] 根据实验结果修订理论文档，而不是反向选择数据证明既有观点。

## 9. 紧接着的实施顺序

计划获确认后，实施严格按以下顺序推进：

1. 创建 Harness 骨架、配置、recorder 与离线测试；
2. 运行最小 API smoke test，冻结首个 capability snapshot；
3. 完成 P0 协议矩阵；
4. 完成 P0 Prefix Cache 因果实验；
5. 根据 P0 数据决定是否执行 P1；
6. 输出 ADR，并回写 DeepSeek Agent 理论与后续架构计划。

在第 4 步完成以前，不启动其他 Agent 功能的实现。

## 10. 官方协议基线

本计划以 2026-06-04 查阅的 DeepSeek 官方 API 文档作为声明基线，但所有关键结论仍以实测为准：

- Context Caching：<https://api-docs.deepseek.com/guides/kv_cache>
- Thinking Mode：<https://api-docs.deepseek.com/guides/thinking_mode>
- Reasoning Model：<https://api-docs.deepseek.com/guides/reasoning_model>
- Models & Pricing：<https://api-docs.deepseek.com/quick_start/pricing>

官方文档当前说明 Cache 默认启用、命中属于 best-effort，并通过 `prompt_cache_hit_tokens` 与 `prompt_cache_miss_tokens` 提供观测；Thinking Mode 对普通多轮和工具调用中的 `reasoning_content` 有不同处理要求。Harness 的首要任务正是验证这些声明在目标模型、目标端点和目标运行路径中的实际表现。
