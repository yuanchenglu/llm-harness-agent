# Stage 3：DeepSeek Agent Gap Analysis

> 证据状态：v0.1 草案；主要基于 E1 源码事实与 E2 历史 Pilot，尚缺 E4 真实任务 Benchmark，不能视为最终选型。

## 结论

Stage 2.5 的实测把产品方向从“复制某个竞品”收敛为：**DeepSeek-aware Provider Adapter + 可观测 Context Compiler + 有边界的 Tool Runtime + Evidence Ledger**。

| 能力 | 当前状态 | 与成熟产品差距 | 决策 |
|---|---|---|---|
| V4 Provider Adapter | raw HTTP、thinking、usage 已实现 | capability matrix 尚不完整 | 自研并持续实测 |
| Prefix Cache | 有指纹、telemetry 与 Pilot | 缺 drift 分类、TTL/并发/真实任务数据 | 自研，正确性优先 |
| Tool loop | MVP 可执行并保留 reasoning | 缺权限、写操作审批、恢复 | 借鉴 Codex/OpenCode 的 policy 层 |
| 多 Agent/编排 | 未实现 | 缺状态机与证据交接 | MVP 后再做，不以角色数量为目标 |
| Artifact/Checkpoint | 文档定义，代码未完整实现 | 缺持久 session/evidence schema | 借鉴 OpenSpec/Superpowers |
| 多端 UI | CLI | 缺 Desktop/Server | Runtime 稳定后再扩展 |

## 不采用的过早方案

- 不立即 Fork OpenCode：当前关键差异集中在 DeepSeek 协议、缓存与证据层，先验证 adapter 边界；
- 不把 CodeWhale three-zone、Trae test-time scaling 当作已完成事实；
- 不在无真实任务 benchmark 时承诺 Flash Router、Planner/Executor 或 Pro Review 提升。

## Stage 3 Gate

已明确 P0 自研边界、借鉴方向和延期能力，可以进入产品架构与 PRD；所有未验证项继续保留 evidence 状态。
