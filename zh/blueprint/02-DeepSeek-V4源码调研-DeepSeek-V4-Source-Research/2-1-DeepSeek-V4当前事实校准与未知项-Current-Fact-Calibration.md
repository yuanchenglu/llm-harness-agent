# 2-1 DeepSeek V4 当前事实校准与未知项

> 校准日期：2026-06-05  
> 状态：Stage 1 校准覆盖层  
> 原则：历史 v1.1 调研包保留为研究记录；当历史文档与本文件冲突时，以本文件和 `stage1-source-snapshot-2026-06-05.json` 为准。

## 1. 证据规则

本轮使用四级证据：

| 级别 | 含义 | 本阶段可支持的结论 |
|---|---|---|
| E1 | 官方产品页、模型卡或公告声明，未独立复现 | 可以写“官方声明/文档显示”，不能写“实测证明” |
| E2 | 固定 revision 的官方源码、配置、encoding 或技术报告 | 可以确认该 revision 中存在的结构与实现，不能自动外推到托管 API 行为 |
| E3 | 可复现的受控 API 实验 | 可以确认特定时间、模型、请求条件下的协议或缓存行为 |
| E4 | 可复现的真实任务 benchmark | 可以支撑产品路由、架构底座和 ROI 决策 |

分类标签：

- `FACT-E2`：固定官方源码事实；
- `CLAIM-E1`：当前官方产品声明；
- `INFERENCE`：由事实推导的工程假设；
- `UNKNOWN`：证据不足、来源冲突或需要 E3/E4；
- `REJECTED`：现有证据不支持，不能进入架构约束。

## 2. 固定来源

机器可读索引见 [`stage1-source-snapshot-2026-06-05.json`](stage1-source-snapshot-2026-06-05.json)。

| 来源 | 固定点 | 用途 |
|---|---|---|
| DeepSeek-V4-Pro 官方 Hugging Face 仓库 | revision `89d501aed998d33fa4f4702102ec1bb2331e10f6` | Pro README、config、inference、encoding、技术报告 |
| DeepSeek-V4-Flash 官方 Hugging Face 仓库 | revision `6976c7ff1b30a1b2cb7805021b8ba4684041f136` | Flash README、config、inference、encoding、技术报告 |
| DeepSeek API Models & Pricing | 2026-06-05 获取页面 SHA-256 已记录 | 当前模型、上下文、输出和展示价格声明 |
| DeepSeek API Thinking Mode | 2026-06-05 获取页面 SHA-256 已记录 | thinking、reasoning effort、reasoning_content 声明 |
| DeepSeek API Context Caching | 2026-06-05 获取页面 SHA-256 已记录 | cache unit、best-effort、usage 字段声明 |
| DeepSeek API Change Log | 2026-06-05 获取页面 SHA-256 已记录 | V4 API 上线日期与兼容接口声明 |

API 文档没有公开不可变 revision，因此“访问日期 + 页面哈希”只能固定本次观察，不能保证未来仍可从原 URL 重建相同内容。

## 3. 当前事实校准

### 3.1 可确认为固定源码事实

| ID | 校准结论 | 分类 | 边界 |
|---|---|---|---|
| S1-F01 | 官方开放了 V4-Pro 与 V4-Flash 模型仓库；模型卡将它们描述为 1.6T/49B active 与 284B/13B active，并声明 1M context | `FACT-E2` + 模型卡声明 | 参数规模和 context 是官方声明；未在本仓库独立复算 |
| S1-F02 | 固定 revision 中存在 hybrid attention、Compressor、Indexer、sparse attention、mHC/Hyper-Connections、MoE、FP4/FP8 相关实现与配置 | `FACT-E2` | 只能证明开放权重 revision；不能证明托管 API 使用完全相同 revision |
| S1-F03 | Pro 与 Flash 的 config 存在层数、hidden size、expert 数、`index_topk` 等差异 | `FACT-E2` | 差异本身不能直接推出真实 Agent 任务优劣 |
| S1-F04 | 官方开放权重提供 dedicated encoding 示例而非 Jinja chat template，并包含 DSML/tool 与 thinking 编码逻辑 | `FACT-E2` | 托管 API 暴露 OpenAI/Anthropic 兼容接口；客户端不应因此直接实现 DSML wire protocol |

### 3.2 当前官方 API 声明

| ID | 校准结论 | 分类 | 边界 |
|---|---|---|---|
| S1-A01 | 2026-04-24 的官方 changelog 宣布 API 支持 `deepseek-v4-pro` 与 `deepseek-v4-flash` | `CLAIM-E1` | 未执行 `/models` 或实际请求验证 |
| S1-A02 | 2026-06-05 的 Models & Pricing 页面展示两模型均为 1M context、最大 384K output，并支持 tool calls | `CLAIM-E1` | 最大长度、稳定性和质量仍需 E3/E4 |
| S1-A03 | 当前页面展示 Flash 价格为 `$0.0028/$0.14/$0.28`，Pro 为 `$0.003625/$0.435/$0.87`，依次对应 cache-hit input / cache-miss input / output，每百万 token | `CLAIM-E1` | 价格可随时变化；未通过账单实证 |
| S1-A04 | Context Caching 页面声明缓存默认开启、完整匹配已持久化 prefix unit 才能命中、服务为 best effort，并返回 hit/miss token 字段 | `CLAIM-E1` | 精确 token 边界、持久时间和跨时段稳定性未知 |
| S1-A05 | Thinking Mode 页面声明 thinking 默认开启，支持 `high/max` effort，工具调用轮次必须回传 `reasoning_content` | `CLAIM-E1` | 两模型和两种兼容接口的实际错误行为需要 E3 |

## 4. V3/V3.2 外推分离

以下规则用于防止把旧代事实写成 V4 当前事实：

1. V2/V3 的 MLA、缓存原理或旧 API 行为只能作为机制背景，除非 V4 固定源码或当前 API 文档再次明确。
2. 旧模型名 `deepseek-chat` / `deepseek-reasoner` 的历史行为不能直接代表 V4；当前官方文档只声明它们暂时映射到 V4-Flash 的非思考/思考模式。
3. 旧 Context Caching 公告说明了磁盘缓存的历史动机，但 V4 当前命中规则必须以 2026-06-05 的 Context Caching 页面为准。
4. API 新闻页使用 `DSA`，模型卡和源码材料使用 `CSA/HCA`。两套命名是否严格一一对应保持 `UNKNOWN`，不得自行合并。
5. 托管 API 是否与开放权重 revision、量化方式和 encoding 完全一致保持 `UNKNOWN`。

## 5. 高影响 Harness 结论复核

| 历史结论 | 校准结果 | 处理 |
|---|---|---|
| 1M context 支持长任务 | 官方声明支持，但不代表可平铺历史或保证检索质量 | 保留为容量上限声明；真实任务质量进入 E4 |
| `sliding_window=128` 意味着当前信息必须靠近尾部 | 源码事实支持“近端窗口重要”，但“必须”过强 | 降级为 `INFERENCE`，通过布局 benchmark 验证 |
| Pro `index_topk` 更高，所以更适合长上下文审查 | 配置差异真实，产品结论未验证 | 降级为 `INFERENCE`，进入 Flash/Pro E4 路由实验 |
| hash routing 意味着稳定标签会改善路由 | 没有直接证据证明 prompt 标签可稳定影响目标 expert | 保持 `UNKNOWN`，不得作为架构硬约束 |
| mHC 意味着 prompt 应使用多信号分层 | 从模型内部连接方式跳到 prompt 设计，证据链不足 | `REJECTED` |
| FP4/FP8 证明 Pro-on-demand 成本可控 | 内部数值格式不能直接推出 API 价格或路由 ROI | `REJECTED`；成本只用当前价格与 E4 token 数据计算 |
| dedicated encoding / DSML 意味着 API 客户端必须实现 DSML parser | 托管 API 当前声明 OpenAI/Anthropic 兼容接口 | `REJECTED`；仅本地开放权重适配器可能需要 |
| reasoning 不是 memory | API 文档明确普通轮次可忽略旧 reasoning，但工具调用轮次必须回传 | 保留为带条件的产品原则，协议细节进入 E3 |
| byte-stable prefix 会提升 cache hit | 完整 prefix unit 匹配规则支持该方向，但序列化与 token 边界仍未知 | 保留为强 `INFERENCE`，进入 E3 cache 实验 |
| Flash-first / Pro-on-checkpoint | 是成本质量路由假设，不是模型事实 | 进入 E4；在数据前不得定稿 |

## 6. Unknowns Register

| ID | 未知项 | 关闭证据 | 所属阶段 |
|---|---|---|---|
| U-001 | 实际 `/models` 可见性、两模型请求成功率与当前账单价格 | E3 模型探测、协议矩阵与账单核对 | Stage 2.5 |
| U-002 | 托管 API 是否与开放权重 revision、encoding、量化和 kernel 一致 | 官方明确声明或可验证服务元数据 | Stage 1/2.5，可能永久未知 |
| U-003 | DSA 与源码材料中 CSA/HCA 的准确映射 | 官方技术报告明确定义或官方说明 | Stage 1，当前保持 unknown |
| U-004 | reasoning_content 在 Flash/Pro、OpenAI/Anthropic 接口和工具循环中的精确行为 | E3 协议矩阵 | Stage 2.5 |
| U-005 | cache prefix unit 的精确 token 边界、持久时间和跨时段命中分布 | 跨时段、重复、带对照的 E3 实验 | Stage 2.5 |
| U-006 | byte-stable JSON、工具顺序和消息布局对 cache hit 的因果影响 | 配对随机化 E3 实验 | Stage 2.5 |
| U-007 | 1M context 下不同布局的检索质量与注意力退化 | E4 长上下文真实任务 benchmark | Stage 3/4 |
| U-008 | Flash-first / Pro-on-checkpoint 的质量、成本与延迟 ROI | E4 路由 benchmark | Stage 3/4 |
| U-009 | 稳定标签是否改善 hash routing 或输出稳定性 | 可重复消融实验；若不可观测则永久未知 | Stage 3 |
| U-010 | 官方模型卡 benchmark 的独立复现程度 | 独立评测或内部复现 | 不阻塞 MVP，但不得写成独立证明 |

## 7. Stage 1 结论

Stage 1 可以关闭的内容是“当前事实分类与证据边界”，不是“所有 V4 行为均已验证”：

- 固定源码事实已绑定到官方 revision；
- 当前 API 声明已绑定到访问日期和页面哈希；
- V3/V3.2 外推已与 V4 当前事实分离；
- 高影响 Harness 结论已分为保留、降级、unknown 与 rejected；
- 需要真实 API 或真实任务的数据已明确转交 Stage 2.5 / Stage 3–4。

任何后续文档引用历史 v1.1 包时，都必须同时检查本校准覆盖层。
