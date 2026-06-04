# DeepSeek V4 Flash / Pro 物理特性调研日志 v0.1

> 创建日期：2026-06-04  
> 目标：为 DeepSeek Agent 的 Cache-First / Long-Context-First Harness 设计建立模型物理特性证据库。  
> 方法：优先读取 DeepSeek 官方 GitHub 开源代码，其次读取 DeepSeek 官方 API 文档、官方论文/技术报告，再使用媒体/第三方资料作为低等级线索。

---

## 0. 证据等级

- **S0：官方源码直接确认**：DeepSeek 官方 GitHub / HuggingFace 中的代码、配置、模型卡。
- **S1：官方文档直接确认**：DeepSeek 官方 API 文档、官方 README、官方发布说明。
- **A：官方论文 / 技术报告确认**：DeepSeek 官方 arXiv / PDF 技术报告。
- **B：可信第三方确认**：Reuters、Tom's Hardware 等媒体或社区文档。
- **C：工程推断**：基于 V3 / V3.2-Exp / API 行为对 V4 的推断，必须后续用 V4 源码或实验验证。

---

## 1. 当前已查官方仓库状态

### 1.1 GitHub `deepseek-ai` 组织

已确认官方 GitHub 组织：`https://github.com/deepseek-ai`。

当前已看到的关键仓库包括：

- `deepseek-ai/DeepSeek-V3`
- `deepseek-ai/DeepSeek-V3.2-Exp`
- `deepseek-ai/DeepGEMM`
- `deepseek-ai/DeepEP`
- `deepseek-ai/3FS`
- `deepseek-ai/FlashMLA`
- `deepseek-ai/TileKernels`
- `deepseek-ai/awesome-deepseek-agent`

### 1.2 V4 GitHub 源码状态

截至本轮检索，尚未在 GitHub 官方组织中直接确认到：

- `deepseek-ai/DeepSeek-V4`
- `deepseek-ai/DeepSeek-V4-Pro`
- `deepseek-ai/DeepSeek-V4-Flash`

注意：这不是最终结论，只是当前检索状态。下一步需要继续查 HuggingFace 官方模型卡、V4 技术报告、发布公告中的源码/权重链接。

---

## 2. 已确认物理特性计数

当前计数：

- 已确认物理特性：**12 条**
- 待验证物理特性：**5 条**
- 已发现对 Harness 有直接设计影响的点：**10 条**

---

## 3. 物理特性清单

### P-01：V4 Flash / Pro 均为 1M 上下文模型

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Models & Pricing`
- 证据：`deepseek-v4-flash` 与 `deepseek-v4-pro` 均标注 `CONTEXT LENGTH 1M`。
- 对 Harness 的设计影响：
  - 不能用传统 32K/128K Agent 的上下文策略。
  - 需要设计“长上下文工作台”，但不是简单把所有内容塞进去。
  - 必须有注意力预算管理、上下文分区、按需加载、Checkpoint 快照、长任务压缩策略。

### P-02：V4 最大输出 384K

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Models & Pricing`
- 证据：`MAX OUTPUT MAXIMUM: 384K`。
- 对 Harness 的设计影响：
  - 可以支持长文档生成、代码批量修改说明、超长任务总结。
  - 但必须限制默认输出长度，否则成本和可读性都会失控。
  - UI 应支持“长输出分段展开”和“自动生成目录”。

### P-03：输入 token 按 cache hit / cache miss 分价

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Models & Pricing`
- 证据：官方价格表将 input token 拆成 `CACHE HIT` 与 `CACHE MISS` 两类。
- 对 Harness 的设计影响：
  - DeepSeek Agent 必须内置 cache hit / miss telemetry。
  - 成本面板不能只显示总 token，而要显示 cache hit 率、miss token、边际成本。
  - Harness 设计必须围绕“稳定前缀最大化、变化尾部最小化”。

### P-04：DeepSeek Context Caching 是硬盘缓存，默认开启

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Context Caching`
- 证据：DeepSeek API Context Caching on Disk Technology 默认开启；如果后续请求与之前请求有重叠前缀，重叠部分从缓存读取。
- 对 Harness 的设计影响：
  - 用户不需要手动开启缓存，但 Harness 需要主动制造可命中的前缀结构。
  - System prompt、工具 schema、项目记忆、Skill index 应 byte-stable。
  - 用户每轮输入变化应尽量 ride the turn tail。

### P-05：缓存命中要求“完整匹配缓存前缀单元”

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Context Caching`
- 证据：由于 Sliding Window Attention 机制，缓存前缀是独立完整单元；后续请求只有完全匹配某个 cache prefix unit 才能命中。
- 对 Harness 的设计影响：
  - 不能只追求“内容大致相同”，必须追求“字节稳定”。
  - 任何动态时间戳、随机 ID、顺序变化、工具列表变化都会破坏命中。
  - 需要 Byte-Stable Prefix Architecture。

### P-06：缓存前缀会在请求边界、公共前缀、固定 token 间隔处持久化

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Context Caching`
- 证据：缓存持久化发生在 user input 结束位置、model output 结束位置、公共前缀检测、长输入/长输出固定 token 间隔。
- 对 Harness 的设计影响：
  - Agent 应主动把稳定内容放在请求前部，并避免频繁重排。
  - 长文档任务应采用“固定稳定前缀 + 多轮尾部问题”的结构。
  - 可以设计 cache warming / prefix preflight 机制。

### P-07：V4 Flash / Pro 同时支持 thinking / non-thinking 模式

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Models & Pricing`
- 证据：Thinking Mode 支持 thinking 与 non-thinking，并说明旧模型名 `deepseek-chat` / `deepseek-reasoner` 将分别映射到 V4 Flash 的非思考/思考模式。
- 对 Harness 的设计影响：
  - 不应只按 Flash/Pro 两档路由，还要按 thinking/non-thinking 四象限路由。
  - 简单工具调用、格式化、摘要默认 non-thinking。
  - 复杂规划、架构判断、审查、失败复盘使用 thinking。

### P-08：FIM 只支持 non-thinking 模式

- 证据等级：S1
- 来源：DeepSeek 官方 API 文档 `Models & Pricing`
- 证据：FIM Completion 标注 `Non-thinking mode only`。
- 对 Harness 的设计影响：
  - Code 模式中补全、局部编辑、diff 生成应走 non-thinking。
  - 不能把所有代码任务都交给 thinking；应区分“生成代码”和“规划/审查代码”。

### P-09：V3 / V3.2 架构核心是 MoE + MLA + FP8 + MTP

- 证据等级：S0 / A
- 来源：`deepseek-ai/DeepSeek-V3` README、V3 inference code、V3 technical report。
- 证据：V3 README 明确 671B 总参数、37B activated per token、采用 MLA 和 DeepSeekMoE，并使用 auxiliary-loss-free load balancing、MTP、FP8 mixed precision。
- 对 Harness 的设计影响：
  - MoE 模型每 token 激活专家不同，长任务中任务类型切换可能影响延迟和稳定性。
  - MTP / speculative decoding 对低延迟输出有价值，但 Harness 层需要更细粒度流式 UI。
  - FP8 / DeepGEMM / DeepEP 是服务端效率来源，客户端 Harness 应重点利用价格和吞吐优势。

### P-10：V3.2-Exp 引入 DeepSeek Sparse Attention，专门优化长上下文训练和推理效率

- 证据等级：S0 / A
- 来源：`deepseek-ai/DeepSeek-V3.2-Exp` README 与 inference code。
- 证据：V3.2-Exp README 明确它是走向下一代架构的中间步骤，引入 DeepSeek Sparse Attention，用于提升 extended text sequences 的训练和推理效率。源码中出现 `Indexer`、`index_topk`、`fp8_index`、top-k sparse attention 路径。
- 对 Harness 的设计影响：
  - V4 如果继承 DSA，则 1M 上下文并不等价于全量 dense attention。
  - Harness 不应假设模型会均匀关注所有历史 token。
  - 长上下文必须有“重点锚点”“摘要层”“索引层”“最近上下文层”。

### P-11：V3.2-Exp 的源码中 indexer 使用 top-k 选择注意力位置

- 证据等级：S0
- 来源：`DeepSeek-V3.2-Exp/inference/model.py`
- 证据：源码 `ModelArgs` 中有 `index_topk: int = 2048`，`Indexer.forward()` 中通过 `index_score.topk(min(self.index_topk, end_pos), dim=-1)` 选择 top-k indices，再将 mask scatter 到 attention scores。
- 对 Harness 的设计影响：
  - 对 1M context 的正确用法不是“塞入所有东西”，而是让关键内容更容易被 sparse indexer 选中。
  - 需要给关键约束、计划、验收标准、文件索引、当前目标制造高可见度位置。

### P-12：V3/V3.2 MLA 使用 latent KV cache，而不是传统每头完整 KV cache

- 证据等级：S0
- 来源：`DeepSeek-V3/inference/model.py`、`DeepSeek-V3.2-Exp/inference/model.py`
- 证据：MLA 中存在 `kv_lora_rank`、`kv_cache`、`pe_cache`；V3.2-Exp 还模拟 FP8 KV cache。
- 对 Harness 的设计影响：
  - DeepSeek 的长上下文成本优势不仅来自 API cache，也来自模型内部 KV cache 压缩。
  - Harness 要避免频繁 reset session，因为 reset 会浪费内部 KV cache 和外部 prefix cache。

---

## 4. 待验证物理特性

### V-01：V4 Pro 是否为 1.6T 参数、49B activated per token

- 当前状态：第三方资料与媒体有说法，但尚未用官方源码/模型卡确认。
- 下一步：查 HuggingFace `deepseek-ai/DeepSeek-V4-Pro` 模型卡、config.json、技术报告。

### V-02：V4 Flash 是否为 284B 参数、13B activated per token

- 当前状态：第三方资料与媒体有说法，但尚未用官方源码/模型卡确认。
- 下一步：查 HuggingFace `deepseek-ai/DeepSeek-V4-Flash` 模型卡、config.json、技术报告。

### V-03：V4 是否继承 V3.2-Exp 的 DeepSeek Sparse Attention

- 当前状态：V3.2-Exp 明确是 next-generation architecture 的中间步骤，但 V4 是否完全继承 DSA，需要官方 V4 源码或技术报告确认。

### V-04：V4 在 Huawei Ascend / Cambricon 等国产硬件上的实际部署代码改动

- 当前状态：媒体称 V4 adapted for Huawei Ascend chips，但尚未看到官方 kernel / serving 代码。
- 对 Harness 的潜在影响：如果国产硬件导致吞吐/并发/延迟模式不同，客户端应支持 backend capability probing。

### V-05：V4 Pro / Flash 的工具调用稳定性差异

- 当前状态：官方说明两者都支持 Tool Calls，但没有公开详细稳定性 benchmark。
- 下一步：需要用 API 实测 function calling、JSON、long context tool-use 的失败率。

---

## 5. 对 DeepSeek Agent Harness 的第一批架构约束

1. **Byte-Stable Prefix 是一级架构约束**：system prompt、tool schema、memory index、skill index 必须稳定。
2. **所有动态信息 ride the turn tail**：计划切换、权限提示、临时 memory、后台任务结果，不应改 system prefix。
3. **cache hit / miss 必须产品化可见**：每轮显示 hit tokens、miss tokens、hit ratio、成本。
4. **Flash-first，Pro-on-demand**：默认 Flash；复杂规划、关键审查、失败复盘切 Pro。
5. **thinking / non-thinking 双轴路由**：不要把 thinking 当默认；FIM 和局部编辑必须 non-thinking。
6. **长上下文要分层，不要平铺**：hard constraints、plan、KR、current files、recent logs、archive summaries 各有位置。
7. **对 sparse attention 友好**：关键内容要短、稳定、重复出现在锚点位置；历史噪声要进入索引而不是全量塞入。
8. **checkpoint snapshot 替代全量执行日志审查**：审查 Agent 只读目标、已完成、意外、剩余计划。
9. **Skill body 按需加载**：prefix 中只放 skill index，不放长 skill body。
10. **Reasoning 内容默认 display-only**：不回传到下一轮 prompt，避免 token 浪费和 cache 污染。

---

## 6. 下一步调研任务

1. 查找 HuggingFace 官方 V4 Pro / Flash 模型卡与 config。
2. 查找 DeepSeek V4 技术报告 PDF。
3. 继续阅读 V3.2-Exp `model.py`，重点拆解 Indexer / sparse attention / FP8 cache。
4. 阅读 DeepGEMM / FlashMLA / DeepEP，确认模型服务端物理约束如何影响客户端 Harness。
5. 做一组 API 实验：同前缀、多轮变尾部、动态 system prompt、tool schema 变化、reasoning 回传，量化 cache hit/miss。
