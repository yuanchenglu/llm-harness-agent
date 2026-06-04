# Stage 2.5：DeepSeek V4 协议与 Prefix Cache 实证报告

> 记录日期：2026-06-04；模型：`deepseek-v4-flash`；状态：**历史低预算 Pilot，仅 E2 探索性观察，不构成可审计确认性实证。原始脱敏 trace 未进入仓库，汇总值无法独立复算。严谨性复核见 `18-1-科研严谨性复核与阶段重评-Scientific-Rigor-Audit.md`。**

## 1. 实现产物

- 无第三方依赖的 raw HTTP client、确定性请求指纹、脱敏 JSONL recorder；
- protocol 与 prefix cache 两组可重复 suite；
- thinking-mode tool-loop 专项探针；
- 所有密钥只从环境变量读取，结果文件默认被 Git 忽略，`reasoning_content` 被脱敏。

运行入口见 `benchmarks/README.md`，核心代码见 `src/deepseek_agent/core.py` 与 `src/deepseek_agent/benchmark.py`。

## 2. 官方文档快照与实测边界

2026-06-04 官方文档列出了 `deepseek-v4-flash`、`deepseek-v4-pro`；两者均支持 thinking/non-thinking、1M context 与 tool calls。官方 thinking-mode 文档声明：无工具调用的历史 reasoning 可忽略；发生工具调用时应完整回传 reasoning。价格与行为会变化，因此实现采用 capability/config，而非把结论写死。

## 3. 历史 Pilot 观察（已降级，不得作为确认性结论）

### 3.1 协议

| 实验 | 结果 | 解释与行动 |
|---|---|---|
| `GET /models` | 200，返回 Flash 与 Pro | V4 模型标识确认 |
| thinking disabled / high | 均 200 | 一个模型可通过请求参数切换模式 |
| thinking 模式携带 `temperature` | 200 | 与官方“为兼容而接受但不生效”一致；Adapter 必须主动校验，不能以 200 证明参数生效 |
| thinking tool loop：回传 reasoning | 200 | 正常路径成立 |
| thinking tool loop：删除 reasoning | 本次单次探针仍为 200 | **与官方“将返回 400”声明不一致**；不能据此假定 drop 安全，需扩大工具链/模型/轮次矩阵。MVP 仍完整回传 |

### 3.2 Prefix Cache（每个 case 两次，低预算 Pilot）

| Case | 累计 hit / miss tokens | 初步观察 |
|---|---:|---|
| 完全相同长前缀 | 1408 / 1490 | 首次建立、后续命中；两次样本不能估计稳定性 |
| system 尾部变化 | 2816 / 84 | 大部分共同前缀仍命中，说明不是简单“任一字节变化全失效” |
| user 尾部变化 | 2816 / 82 | 稳定前缀被复用 |
| 带单个稳定工具 | 3072 / 360 | 工具目录增加 miss，但共同前缀仍有命中 |

`tools-reordered` Pilot 只有一个工具，因此反转不构成有效变异，该 case 不得用于结论，已列为下一轮修正项。

## 4. 已证实、未证实与架构变化

### 已证实

1. Cache telemetry 可从 usage 中获取；稳定长前缀产生可观测命中。
2. V4 thinking 参数存在“请求成功但参数可能无效”的兼容行为，必须做 capability validation。
3. Cache 是共同前缀复用问题，后缀变化未必破坏此前 token 的命中。

### 未证实

- drop reasoning 在所有 thinking tool loop 中是否安全；
- Pro 与 Flash 的协议是否完全一致；
- 工具顺序、JSON key 顺序、并发、TTL 和跨日稳定性；
- cache 对真实代码任务成功率与总成本的净收益。

### 对计划的实际影响

- 保留 Cache-first，但降级为“可观测优化约束”，绝不优先于正确性；
- Provider Adapter 默认在工具链完整回传 reasoning，普通 user turn 可清理；
- 请求编译器必须记录 capability、prefix fingerprint 与 drift reason；
- 下一轮只扩大 P0 矩阵，不用 Pilot 数字宣传性能。
