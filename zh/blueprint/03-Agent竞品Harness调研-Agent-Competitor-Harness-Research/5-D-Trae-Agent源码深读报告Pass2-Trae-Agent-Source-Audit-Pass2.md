# 5-D Trae Agent 源码深读报告 Pass 2 Trae Agent Source Audit Pass 2

> **2026-06-04 事实校准提示：** 本文保留为历史调研记录；关键结论已使用官方仓库固定 commit 重新复核。阅读与引用本文前，必须同时阅读 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 与 [`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`](./17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md)。原文中的“终版 / A 级 / 可直接迁移”等措辞不代表已通过运行 benchmark。

> 版本：v0.9  
> 状态：核心 Agent Loop / Tool Loop / Trajectory / Completion 机制已读到可用于架构判断。  
> 仍未完成：每个具体 tool implementation、LLM clients、Docker manager、MCP client 的逐文件全量审计。

---

## 1. 已读核心源码

| 模块 | 源码 | 关键结论 |
|---|---|---|
| BaseAgent | https://github.com/bytedance/trae-agent/blob/main/trae_agent/agent/base_agent.py | 主 loop、LLM step、tool call、reflection、DockerToolExecutor |
| TraeAgent | https://github.com/bytedance/trae-agent/blob/main/trae_agent/agent/trae_agent.py | 软件工程 agent、system prompt、project path、task_done、git diff 验证 |
| TrajectoryRecorder | https://github.com/bytedance/trae-agent/blob/main/trae_agent/utils/trajectory_recorder.py | 记录 LLM interaction、tool calls、usage、agent steps、errors |
| Tools docs | https://github.com/bytedance/trae-agent/blob/main/docs/tools.md | str_replace、bash、sequential_thinking、task_done、json_edit_tool |
| Trajectory docs | https://github.com/bytedance/trae-agent/blob/main/docs/TRAJECTORY_RECORDING.md | 轨迹记录 schema、用途、格式 |

---

## 2. Agent Loop 机制

`BaseAgent` 的主循环可概括为：

```text
new_task
while step <= max_steps:
  _run_llm_step
  if tool_calls:
    _tool_call_handler
  _finalize_step
  check completed
cleanup tools / MCP
```

### 模型-Harness 配合

Trae Agent 不是一次 prompt 生成 patch，而是：

```text
模型提出动作
Harness 执行工具
工具结果回传
模型继续判断
直到 task_done
```

这与 DeepSeek Agent 的基本 Agent Loop 一致。

---

## 3. Tool Loop 与完成协议

`TraeAgentToolNames` 固定包含：

```text
str_replace_based_edit_tool
sequentialthinking
json_edit_tool
task_done
bash
```

来源：https://github.com/bytedance/trae-agent/blob/main/trae_agent/agent/trae_agent.py

`task_done` 工具是完成协议；在 `must_patch=true` 时，TraeAgent 还会检查 git diff，并过滤测试 patch 以判断是否真正完成。

### 对 DeepSeek Agent 的启发

DeepSeek Agent 也应该有显式完成协议：

```text
finish_task / task_done
verification_evidence
git_diff
test_result
review_state
```

不要只靠模型自然语言说“完成了”。

---

## 4. TrajectoryRecorder 机制

`TrajectoryRecorder` 记录：

```text
task
provider
model
max_steps
llm_interactions
agent_steps
success
final_result
execution_time
usage
tool_calls
tools_available
errors
reflections
```

来源：https://github.com/bytedance/trae-agent/blob/main/trae_agent/utils/trajectory_recorder.py

### 对 DeepSeek Agent 的启发

这是必须吸收的能力。DeepSeek Agent 的 trace schema 应扩展为：

```text
model_route: Flash/Pro
thinking_mode
cache_hit_tokens
cache_miss_tokens
prompt_cache_hit_rate
checkpoint_id
reviewer_model
review_result
route_reason
prefix_drift
```

这样 trajectory 不只是日志，而是：

```text
路由学习数据
成本优化数据
失败复盘数据
Skill 生成数据
Benchmark 回放数据
```

---

## 5. sequential_thinking 工具

tools 文档显示 `sequential_thinking` 支持：

```text
sequential thoughts
revision
branch
alternative exploration
hypothesis verification
```

来源：https://github.com/bytedance/trae-agent/blob/main/docs/tools.md

### 对 DeepSeek Agent 的启发

它把一部分 reasoning 外部化。  
这和 DeepSeek V4 的 reasoning_content policy 高度相关：

```text
不要把所有 thinking 都当 memory；
关键推理应结构化沉淀为 checkpoint / decision / hypothesis / failure note。
```

DeepSeek Agent 可以设计：

```text
StructuredReasoningTool
HypothesisTree
PlanGraph
CandidateTrajectory
```

---

## 6. Model-Harness Fit 终版矩阵

| DeepSeek V4 特性 | Trae Agent 适配程度 | 迁移判断 |
|---|---:|---|
| 1M context | C | 需要 V4 Layout Manager |
| CSA/HCA | D | 未见 sparse attention-aware layout |
| cache hit/miss | B- | trajectory 有 usage 字段，可扩展 |
| Flash/Pro route | C+ | model_config 静态配置，需动态 router |
| DSML encoding | D | 需重写 V4 compiler |
| reasoning policy | B | sequential_thinking 可借鉴 |
| checkpoint review | B- | trajectory/git diff 支撑，但需 Pro reviewer |
| trajectory | A | 强借鉴 |
| Docker execution | B+ | 可借鉴 sandbox 思想 |
| task_done protocol | A- | 强借鉴 |

---

## 7. Trae Agent 迁移判断

### 可直接借鉴

```text
Agent loop 结构
TrajectoryRecorder 设计
task_done 完成协议
sequential_thinking 工具思想
tool result → message 回传模式
Docker executor 思路
git diff completion check
```

### 需要 DeepSeek-native 重写

```text
LLMClient
ModelConfig
message compiler
tool call parser
usage parser
context builder
reasoning policy
router
reviewer
```

---

## 8. Trae 结论

Trae Agent 的源码价值主要在：

```text
trajectory-first runtime
externalized reasoning
explicit task_done
tool-loop skeleton
Docker execution
```

它不是 V4-native，但它非常适合作为 DeepSeek Agent 的 trace / reasoning / completion 协议参考。
