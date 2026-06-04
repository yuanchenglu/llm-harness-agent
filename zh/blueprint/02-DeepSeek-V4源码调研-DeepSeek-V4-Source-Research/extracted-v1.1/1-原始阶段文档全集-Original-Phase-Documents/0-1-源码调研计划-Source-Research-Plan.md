# DeepSeek V4 Flash / Pro 源代码调研计划 v0.1

> 目标：把 DeepSeek V4 Flash / Pro 的源码、配置、论文、运行接口彻底拆清楚，形成 DeepSeek Agent Harness 的地基文档。  
> 核心原则：不先做产品设计，不先写 PRD，不先讨论 UI；先回答一个问题：DeepSeek V4 的物理特性到底是什么，Harness 必须如何顺应这些物理特性？

---

## 0. 调研总目标

本轮调研的最终产出不是“看懂模型”，而是形成一套可落地的设计证据链：

```text
V4 源码 / 配置 / 技术报告
        ↓
模型物理特性清单
        ↓
Flash vs Pro 差异矩阵
        ↓
对 Agent Harness 的约束
        ↓
DeepSeek Agent 架构决策
```

最后要回答 5 个问题：

1. DeepSeek V4 Pro / Flash 的底层结构到底是什么？
2. 它相对于 V3 / V3.2 / 其他模型的独特物理特性是什么？
3. Flash 和 Pro 在架构、能力、成本、延迟、上下文、路由策略上有什么本质差异？
4. 这些物理特性如何影响 Agent Harness 的上下文管理、工具调用、Memory、Plan、Review、Skill、模型路由？
5. DeepSeek Agent 哪些设计是“必须专门为 V4 重写”的，而不是泛 Agent 通用设计？

---

## 1. 核心资料源

### 1.1 官方模型仓库

必须阅读：

- `deepseek-ai/DeepSeek-V4-Pro`
- `deepseek-ai/DeepSeek-V4-Flash`
- `deepseek-ai/DeepSeek-V4-Pro-Base`
- `deepseek-ai/DeepSeek-V4-Flash-Base`

重点文件：

```text
config.json
DeepSeek_V4.pdf
inference/model.py
inference/kernel.py
inference/generate.py
inference/convert.py
inference/README.md
encoding/*
tokenizer.json / tokenizer_config.json
```

### 1.2 官方技术报告

必须阅读：

- `DeepSeek_V4.pdf`
- 模型卡中的架构说明、评测表、Reasoning Mode 说明、Chat Template / Encoding 说明

### 1.3 关联官方源码

用于理解 V4 的前身和底层 kernel：

- `deepseek-ai/DeepSeek-V3`
- `deepseek-ai/DeepSeek-V3.2-Exp`
- `deepseek-ai/FlashMLA`
- `deepseek-ai/DeepGEMM`
- `deepseek-ai/DeepEP`
- `deepseek-ai/TileKernels`
- `deepseek-ai/DualPipe`

---

## 2. 阶段划分与产出

## Phase 1：资料定位与源码地图

### 目标

把所有要读的源码、配置、论文、模型卡、运行文档定位清楚，建立源码地图。

### 阅读对象

- HuggingFace 模型仓库
- `config.json`
- `inference/` 目录
- `encoding/` 目录
- 技术报告 PDF
- V3 / V3.2-Exp 对照仓库

### 关键问题

1. V4 的官方源码到底分布在哪里？
2. Pro / Flash / Base / Instruct 四类模型的文件结构有什么差异？
3. 哪些文件是模型结构核心？哪些文件是推理 demo？哪些文件是 kernel？
4. 哪些地方可以直接证实 V4 的物理特性？

### 产出

- `01-source-map.md`：源码地图
- `01-evidence-index.md`：证据索引表
- `01-reading-order.md`：源码阅读顺序

### 验收标准

- 能清楚列出每个关键源码文件的职责。
- 能区分“官方源码证据”“官方文档证据”“论文证据”“推断”。
- 不再出现“V4 源码在哪里”这个不确定问题。

---

## Phase 2：config.json 参数拆解

### 目标

先不读复杂代码，先通过配置文件建立 Flash / Pro 的结构差异底图。

### 阅读对象

- `DeepSeek-V4-Pro/config.json`
- `DeepSeek-V4-Flash/config.json`
- `DeepSeek-V4-Pro-Base/config.json`
- `DeepSeek-V4-Flash-Base/config.json`

### 重点字段

```text
model_type
architectures
max_position_embeddings
hidden_size
num_hidden_layers
num_attention_heads
num_key_value_heads
q_lora_rank
o_lora_rank
index_topk
index_n_heads
index_head_dim
sliding_window / window_size
n_routed_experts
n_shared_experts
num_experts_per_tok
num_hash_layers
expert_dtype
quantization_config
num_nextn_predict_layers
hc_mult
hc_sinkhorn_iters
```

### 关键问题

1. Pro 比 Flash 大在哪里？
2. Flash 为什么能做到更低成本？
3. 两者的 attention / expert / indexer 参数差异是什么？
4. 哪些参数直接影响 Agent Harness 设计？
5. 哪些参数只影响服务端部署，不影响客户端产品？

### 产出

- `02-config-diff-pro-vs-flash.md`
- `02-parameter-glossary.md`
- `02-harness-relevance-table.md`

### 验收标准

- 每个重要字段都有解释。
- Pro / Flash 差异能用表格清楚表达。
- 每个对 Harness 有影响的参数都有设计推论。

---

## Phase 3：ModelArgs 与模型总结构拆解

### 目标

读懂 `inference/model.py` 的全局结构，建立“模型从输入到输出”的主流程图。

### 阅读对象

- `ModelArgs`
- `Transformer`
- `Block`
- `Attention`
- `MoE`
- `Gate`
- `Compressor`
- `Indexer`
- `MTP`
- tokenizer / encoding 入口

### 关键问题

1. V4 的模型结构由哪些模块组成？
2. Forward 主路径是什么？
3. 每层 block 内部顺序是什么？
4. 哪些结构是 V4 新增或显著强化的？
5. 哪些结构对 1M context、低 KV cache、低 FLOPs 有直接贡献？

### 产出

- `03-model-architecture-map.md`
- `03-forward-flow-diagram.md`
- `03-module-responsibility-table.md`

### 验收标准

- 能画出从 token input 到 logits output 的主流程。
- 能解释每个核心类在模型中的位置。
- 能指出 V4 相比普通 Transformer 的非标准模块。

---

## Phase 4：Hybrid Attention 深拆：CSA + HCA

### 目标

这是全调研最核心部分之一。必须搞清楚 DeepSeek V4 的 1M context 是如何实现的。

### 阅读对象

- `Attention`
- `Compressor`
- `Indexer`
- `sparse_attn`
- `kernel.py`
- 技术报告中 Hybrid Attention / CSA / HCA 章节
- V3.2-Exp 的 DSA 源码对照

### 关键问题

1. CSA 是怎么选 token 的？
2. HCA 是怎么压缩 KV 的？
3. Compressor 的压缩窗口、overlap、gated pooling 是什么？
4. Indexer 的 top-k 选择逻辑是什么？
5. sliding window 和 sparse attention 如何协同？
6. 1M context 下，模型到底能“看见”什么？
7. 长上下文对 Agent 来说应该如何排布？

### 产出

- `04-hybrid-attention-deep-dive.md`
- `04-csa-hca-visual-explanation.md`
- `04-context-layout-rules-for-agent.md`

### 验收标准

- 能用人话解释 CSA / HCA。
- 能解释为什么 1M context 不等于“所有 token 同等注意”。
- 能产出 Agent 上下文布局规则，例如 hard constraints、plan、recent work、archive、file index 分别放在哪里。

---

## Phase 5：MoE / Routing / Hash Layer 深拆

### 目标

搞清楚 V4 的专家路由机制，尤其是 Flash 和 Pro 的专家数量、激活专家、hash layer 对稳定性的影响。

### 阅读对象

- `Gate`
- `MoE`
- `Expert`
- `n_routed_experts`
- `num_experts_per_tok`
- `num_hash_layers`
- `score_func`
- `route_scale`
- 技术报告中 MoE 相关章节

### 关键问题

1. Pro / Flash 的 routed experts 和 activated experts 差异是什么？
2. hash-based routing 出现在前几层，意义是什么？
3. score-based routing 的不稳定性是否会影响长任务一致性？
4. MoE 的稀疏激活对成本、延迟、任务路由有什么启发？
5. Agent 是否应该根据任务类型选择 Flash / Pro，而不是固定模型？

### 产出

- `05-moe-routing-analysis.md`
- `05-flash-pro-routing-strategy.md`
- `05-agent-model-router-rules.md`

### 验收标准

- 能解释 Flash 为什么便宜、Pro 为什么强。
- 能提出 Agent 模型路由规则：什么时候用 Flash，什么时候切 Pro，什么时候切 Max thinking。

---

## Phase 6：mHC / Hyper-Connections 深拆

### 目标

搞清楚 V4 的 Manifold-Constrained Hyper-Connections 对深层信号传播、长上下文稳定性、复杂推理的影响。

### 阅读对象

- `Block`
- `hc_split_sinkhorn`
- `hc_mult`
- `hc_sinkhorn_iters`
- 技术报告中 mHC 章节
- `kernel.py` 中 HC 相关实现

### 关键问题

1. mHC 如何替代或增强传统 residual connection？
2. `hc_mult` 多份 hidden state 的含义是什么？
3. Sinkhorn 在这里解决什么约束？
4. mHC 对长任务、多步推理、agentic workflow 有什么潜在影响？

### 产出

- `06-mhc-hyperconnections-analysis.md`
- `06-harness-implications-for-long-reasoning.md`

### 验收标准

- 能解释 mHC 的机制和目的。
- 能说明它是否影响 Harness 的长任务设计、checkpoint、review、thinking mode 策略。

---

## Phase 7：量化与 Kernel 深拆：FP4 / FP8 / FlashMLA / DeepGEMM

### 目标

理解 V4 的服务端效率来源，判断哪些物理特性会影响客户端 Harness 的延迟、吞吐、成本面板、模型路由。

### 阅读对象

- `kernel.py`
- `fp4_gemm`
- `fp8_gemm`
- `act_quant`
- `fp4_act_quant`
- `FlashMLA`
- `DeepGEMM`
- `DeepEP`
- config 中 `expert_dtype` 和 `quantization_config`

### 关键问题

1. 哪些参数是 FP4，哪些是 FP8？
2. Expert 参数 FP4 是否意味着 MoE 专家计算被特殊优化？
3. Attention / MLP / routing 哪些地方是性能瓶颈？
4. Prefill 和 decode 的瓶颈分别是什么？
5. Harness 应如何显示“预估耗时 / 成本 / 长上下文风险”？

### 产出

- `07-quantization-kernel-analysis.md`
- `07-serving-constraints-for-client-harness.md`

### 验收标准

- 能区分模型能力问题、服务端性能问题、客户端 Harness 问题。
- 能给出成本/延迟 UI 的设计依据。

---

## Phase 8：Reasoning Mode / Encoding / Chat Template 深拆

### 目标

搞清楚 V4 的输入输出格式、thinking 模式、reasoning_content、OpenAI-compatible encoding，对 Agent Loop 极其关键。

### 阅读对象

- `encoding/*`
- 模型卡 Chat Template 说明
- `generate.py`
- Reasoning Mode 说明
- API 文档中 chat / reasoning / tool call / FIM 相关说明

### 关键问题

1. V4 为什么不用传统 Jinja chat template？
2. messages 如何 encode 成模型 input string？
3. thinking / non-thinking / max thinking 的格式差异是什么？
4. reasoning_content 应该如何保存、展示、是否回传？
5. Tool call / JSON / FIM 在不同模式下有什么限制？

### 产出

- `08-encoding-and-reasoning-mode.md`
- `08-agent-loop-message-protocol.md`
- `08-reasoning-content-policy.md`

### 验收标准

- 能设计 DeepSeek Agent 自己的 message protocol。
- 能明确哪些内容进入下一轮 prompt，哪些只是 display-only / archive-only。
- 能避免 reasoning_content 污染上下文和 cache。

---

## Phase 9：Flash vs Pro 能力差异与模型路由策略

### 目标

把源码参数、评测结果、API 价格、reasoning mode 结合起来，形成产品级模型路由策略。

### 阅读对象

- 模型卡评测表
- API pricing
- `config.json` 差异
- Agentic / Long Context / Coding benchmark
- Reasonix 官方集成文档

### 关键问题

1. Flash / Pro 在知识、推理、代码、长上下文、Agentic 上差距多大？
2. Flash high thinking 是否能接近 Pro？
3. 哪些任务必须 Pro？
4. 哪些任务 Flash 足够？
5. 哪些场景需要先 Flash 探路，再 Pro 审查？

### 产出

- `09-flash-vs-pro-capability-matrix.md`
- `09-model-router-design.md`
- `09-cost-quality-routing-policy.md`

### 验收标准

- 形成 DeepSeek Agent 的默认模型路由策略。
- 每条路由规则都有证据来源。
- 明确 UI 中如何向用户解释“为什么这一步切 Pro”。

---

## Phase 10：从物理特性到 Harness 设计约束

### 目标

把前面所有源码结论转化成 DeepSeek Agent 的 Harness 架构约束。

### 关键问题

1. V4 的 1M context 应该如何被 Harness 使用？
2. Cache hit / miss 应该如何被 Harness 最大化？
3. CSA / HCA 对上下文布局有什么要求？
4. MoE 对任务路由有什么启发？
5. Reasoning mode 对 Agent Loop 有什么影响？
6. FP4 / FP8 / kernel 效率对客户端产品有什么影响？
7. 哪些设计是 DeepSeek Agent 独有的？

### 产出

- `10-v4-physical-traits-inventory.md`
- `10-harness-design-constraints.md`
- `10-deepseek-agent-architecture-decisions.md`

### 验收标准

- 每个 Harness 约束都能追溯到源码、配置或技术报告。
- 不出现“泛泛而谈 Agent”的设计。
- 能直接支撑下一阶段 PRD 和技术架构文档。

---

## 3. 最终总产出

本轮调研完成后，应该形成一个完整文档包：

```text
docs/research/deepseek-v4/
├── 00-research-plan.md
├── 01-source-map.md
├── 01-evidence-index.md
├── 02-config-diff-pro-vs-flash.md
├── 02-parameter-glossary.md
├── 03-model-architecture-map.md
├── 04-hybrid-attention-deep-dive.md
├── 04-context-layout-rules-for-agent.md
├── 05-moe-routing-analysis.md
├── 05-agent-model-router-rules.md
├── 06-mhc-hyperconnections-analysis.md
├── 07-quantization-kernel-analysis.md
├── 08-encoding-and-reasoning-mode.md
├── 08-agent-loop-message-protocol.md
├── 09-flash-vs-pro-capability-matrix.md
├── 09-model-router-design.md
├── 10-v4-physical-traits-inventory.md
├── 10-harness-design-constraints.md
└── 10-deepseek-agent-architecture-decisions.md
```

最终会汇总成三份核心文档：

1. **《DeepSeek V4 物理特性白皮书》**
2. **《DeepSeek V4 Flash / Pro 差异与模型路由策略》**
3. **《DeepSeek Agent Harness 架构约束说明书》**

---

## 4. 调研方法规范

### 4.1 每个发现必须编号

格式：

```text
P-001：物理特性名称
证据等级：S0 / S1 / A / B / C
证据位置：文件 / 行号 / 技术报告章节
事实描述：
对 Harness 的影响：
待验证问题：
```

### 4.2 每个源码模块必须回答四个问题

```text
1. 它在模型里负责什么？
2. 它和 V3 / V3.2 / 常规 Transformer 有什么不同？
3. 它对 V4 的 1M context / cache / latency / reasoning 有什么贡献？
4. 它要求 Harness 做什么适配？
```

### 4.3 每个 Harness 结论必须可追溯

不能写：

```text
我们应该优化上下文。
```

必须写：

```text
由于 V4 使用 CSA + HCA，且 index_topk 在 Pro 为 1024、Flash 为 512，长上下文并不是全量均匀注意。因此 Harness 应将 hard constraints、current objective、Plan KR、active files 放在高可见度锚点区，而把历史执行日志沉淀为索引和 checkpoint snapshot。
```

---

## 5. 第一批优先问题

先回答这 12 个问题：

1. Pro 的 `index_topk=1024` 和 Flash 的 `index_topk=512` 对 1M 上下文实际可见性意味着什么？
2. `window_size=128` / sliding window 与 compressed sparse attention 如何协同？
3. HCA 的压缩比例如何影响历史 token 的可恢复性？
4. CSA 的 top-k indexer 是否会偏好近期 token、重复 token、结构化 token、特殊锚点？
5. mHC 是否提升长链路 reasoning 稳定性？
6. hash layers 对前几层专家路由稳定性有什么作用？
7. Pro 的 384 routed experts 与 Flash 的 256 routed experts 是否对应不同任务分工？
8. FP4 experts + FP8 non-expert 参数对服务端成本和延迟有什么影响？
9. MTP / next-token prediction 是否影响 Agent 流式输出体验？
10. V4 的 encoding 机制是否要求我们自定义 Agent message protocol？
11. reasoning_content 是否应回传？什么时候保存？什么时候丢弃？
12. Flash high thinking 和 Pro non-thinking / high thinking 的任务边界是什么？

---

## 6. 对 DeepSeek Agent 的预期影响

这轮调研结束后，DeepSeek Agent 的底层设计至少会发生 8 个确定方向：

1. 上下文不是简单长，而是 **layout-driven context**。
2. Prompt 不是简单系统提示，而是 **byte-stable prefix protocol**。
3. Memory 不是全塞上下文，而是 **index + summary + on-demand retrieval**。
4. Plan 不是 checklist，而是 **attention-anchor plan graph**。
5. Review 不是全量重读，而是 **checkpoint snapshot review**。
6. 模型不是用户手动选，而是 **Flash / Pro / Thinking router**。
7. Skill 不是长文本常驻，而是 **index in prefix, body on demand**。
8. 成本不是 token 总量，而是 **cache hit / miss / reasoning budget / route cost**。
