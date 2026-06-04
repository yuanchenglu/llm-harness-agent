# 17-1 Claude Code / Codex / Trae 源码事实校准

## 1. 总体结论

| 项目 | 旧报告总体可信度 | 本轮结论 |
|---|---|---|
| Claude Code | 中高，但只能覆盖公开插件边界 | 边界判断正确；不可用 C 级逆向仓库补足官方 engine 事实 |
| Codex | 高 | 核心源码判断成立；路径已漂移，需固定 commit，且“终版”不成立 |
| Trae Agent | 中高 | Agent loop/trajectory/tool/Docker 判断成立；test-time scaling 被过度陈述 |

## 2. Claude Code：官方源码边界复核

### 2.1 确认项

官方快照只有约 203 个文件，主要是 README、CHANGELOG、examples、scripts 与 `plugins/`。官方插件目录真实包含 commands、agents、skills、hooks 和 MCP 等扩展结构，因此此前关于“插件生态可审计”的判断成立（A1/A2）。例如官方插件说明见 [`plugins/README.md`](https://github.com/anthropics/claude-code/blob/b67fa4fa2c4f42e9b88a31f31906f3142bc165c5/plugins/README.md)。

### 2.2 必须保持的边界

官方仓库中没有 Claude Code 核心 Agent loop、context compaction、session engine、tool runtime 的完整实现。因此：

- `3-C` 将官方 engine 标记为不可完整审计，是正确结论；
- `3-D` 的 `oboard/claude-code-rev` 必须永久保持 C 级，只能用于寻找问题，不能用于证明 Anthropic 当前实现；
- `6-0` 中“file history snapshot、cost tracker、transcript persistence”等可作为产品/文档能力，但不能写成已审过官方 engine 源码。

### 2.3 校准后的结论

```text
Claude Code = 产品与插件设计标杆；不是官方 engine 源码借鉴库。
```

对 DeepSeek Agent 可借鉴其扩展协议和产品行为，但底层实现必须从公开源码项目或自研获得。

## 3. Codex：核心结论成立，但证据必须版本化

### 3.1 已确认的源码事实

- `ContextualUserFragment` 现在定义在独立 `context-fragments` crate，而非只存在于 `core/context`：[`fragment.rs`](https://github.com/openai/codex/blob/16d02ec77c6337ccea02a8c909e05bf3d905f887/codex-rs/context-fragments/src/fragment.rs#L46-L51)（A1）。
- `InternalModelContextFragment`、environment/permission context、TurnContext、`run_turn`、compaction 和 guardian approval/review 均在当前官方源码中存在（A1/A0）。
- 根目录 [`AGENTS.md`](https://github.com/openai/codex/blob/16d02ec77c6337ccea02a8c909e05bf3d905f887/AGENTS.md) 仍明确约束 model-visible context 与 injected fragment（A2）。

### 3.2 旧报告需要校准之处

1. 原 `4-D` 多个链接指向 `main`，仓库变化后路径和符号归属已经发生变化；概念成立，但不可把旧路径当永久事实。
2. ContextualUserFragment 已被抽到独立 crate，说明 Codex 架构还在快速演化；“终版矩阵”措辞不准确。
3. 从 Codex 的 context fragment 规则推导 DeepSeek 的 CSA/HCA、MoE/hash routing 或 byte-stable layout 属于 B 级设计推论，不是 Codex 源码已经实现的 V4 适配。
4. Codex 当前公开源码远超过旧报告读取范围。此前 Pass 2 不是全量核心审计，尤其 guardian、hooks、skills、subagents、app-server、provider 和新的 context manager 尚需继续审。

### 3.3 校准后的结论

Codex 仍是六个对象中最适合作为“通用 Agent 核心工程结构”参考的项目，但引用时必须固定 commit，并把“Codex 源码事实”与“迁移到 DeepSeek 的设计推论”分栏书写。

## 4. Trae Agent：纠正 test-time scaling 误报

### 4.1 已确认的源码事实

- `BaseAgent` 负责 LLM step、工具执行和 Docker tool executor：[`base_agent.py`](https://github.com/bytedance/trae-agent/blob/e839e559ac61bdd0e057c375dd1dee391fee797d/trae_agent/agent/base_agent.py)（A1）。
- `TraeAgent` 提供软件工程 Agent 行为：[`trae_agent.py`](https://github.com/bytedance/trae-agent/blob/e839e559ac61bdd0e057c375dd1dee391fee797d/trae_agent/agent/trae_agent.py)（A1）。
- `TrajectoryRecorder` 记录输入消息、响应、usage、tool calls、tool results、error 与 final result：[`trajectory_recorder.py`](https://github.com/bytedance/trae-agent/blob/e839e559ac61bdd0e057c375dd1dee391fee797d/trae_agent/utils/trajectory_recorder.py#L68-L138)（A1）。
- `SequentialThinkingTool` 不是只有描述；它维护 `thought_history` 和 `branches`，属于有状态工具：[`sequential_thinking_tool.py`](https://github.com/bytedance/trae-agent/blob/e839e559ac61bdd0e057c375dd1dee391fee797d/trae_agent/tools/sequential_thinking_tool.py#L156-L157)（A1）。
- MCP 与 Docker 均有源码实现，而非仅 README 声明（A1）。

### 4.2 被否定或降级的结论

旧 `6-0` 把 Trae 写为：

```text
multi-candidate / generation-pruning-selection
trajectory / reasoning / test-time scaling 标杆
```

本轮对 108 个官方仓库文件扫描后，没有发现 generation–pruning–selection、候选轨迹选择器或 test-time scaling orchestrator 的开源实现。该思想可以来自论文或路线图，但不能写成 Trae Agent 开源源码能力（N/A2，取决于引用来源）。

因此校准为：

```text
Trae Agent = 清晰、较小、可读的 trajectory-first 单 Agent runtime 参考；
不是已开源的 multi-candidate test-time scaling runtime。
```

### 4.3 还需谨慎的点

- TrajectoryRecorder 每次记录都会保存轨迹，是否适合高并发/超长任务需要性能实测；
- sequential thinking 的状态存在于工具实例中，但不等于可靠的跨 session reasoning graph；
- 多 provider 抽象不自动等于 DeepSeek Flash/Pro 策略路由；
- Docker 支持不自动等于完整安全沙箱，仍需审计容器权限、挂载和逃逸面。

## 5. 修订后的三者借鉴排序

| 维度 | 首选参考 | 原因 |
|---|---|---|
| 产品/插件范式 | Claude Code | 产品能力成熟，但实现证据主要来自 docs/plugins |
| 通用核心工程 | Codex | 官方核心源码最完整、类型与测试丰富 |
| 小型 Agent loop / trajectory | Trae Agent | 实现简洁、易读、易做 prototype |
| DeepSeek V4-native | 三者都不是 | 需要另行设计与验证 |
