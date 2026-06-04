# DeepSeek V4 Phase 9-10 调研包

本包是第一轮 V4 源码调研的收束产物。

文件：

1. `09-flash-vs-pro-capability-matrix.md`
2. `09-model-router-design.md`
3. `09-cost-quality-routing-policy.md`
4. `10-v4-physical-traits-inventory.md`
5. `10-harness-design-constraints.md`
6. `10-deepseek-agent-architecture-decisions.md`

核心结论：

- DeepSeek V4-aware Harness 必须围绕物理特性设计。
- Flash-first / Pro-on-checkpoint 是默认策略。
- Context 必须 layout-driven，不是 history dump。
- Reasoning 不能当 memory。
- Tool calling 需要 V4 DSML-aware compiler。
- 本地 V4 推理不是桌面 MVP 默认目标。
- DeepSeek Agent 的第一版技术架构可以从这些架构决策启动。
