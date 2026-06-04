# 17-3 六项目校准后综合结论

## 1. 校准后的事实地图

| 项目 | 可作为源码事实参考的核心 | 不应继续宣称 |
|---|---|---|
| Claude Code | 官方插件结构、examples、公开配置与文档行为 | 官方 engine 已完成源码审计 |
| Codex | typed context、turn loop、compaction、guardian、sandbox、完整 Rust 工程 | 旧 Pass 2 是“终版”或已经覆盖全核心 |
| Trae Agent | 小型 Agent loop、trajectory、Docker、MCP、有状态 sequential thinking | 开源实现了 multi-candidate generation–pruning–selection |
| Reasonix | DeepSeek adapter、cache telemetry、plan gate、compaction、reasoning policy | 评分和成本优势已经被 benchmark 证明 |
| Hermes Agent | tool registry、progressive disclosure、trajectory compression、Agent OS 模块 | memoization 已证明提升 DeepSeek prefix cache；自进化已证明持续变好 |
| CodeWhale | prefix drift check、cache/cost telemetry、auto router、reasoning replay、side-git、LSP | 完整 three-zone request-path contract 已上线 |

## 2. 对 DeepSeek Agent 架构决策的影响

### 2.1 可以进入架构候选池

- 从 Codex 借鉴 typed context 与可测试 core 边界；
- 从 Trae 借鉴最小 Agent loop 与 trajectory schema；
- 从 Reasonix 借鉴 cache telemetry、runtime plan gate、compaction 与 provider normalization；
- 从 Hermes 借鉴 tool registry 与 progressive disclosure；
- 从 CodeWhale 借鉴 prefix drift detection、reasoning protocol tests、side-git 与 LSP feedback；
- 从 Claude Code 借鉴插件与产品交互范式，但不依赖不可审计 engine。

### 2.2 不能直接进入 PRD 的未验证假设

```text
stable tags 可以利用 MoE/hash routing
CSA/HCA 必然要求某一种消息布局
Trae 已有开源 test-time scaling runtime
CodeWhale 已完成完整 three-zone compiler
planner/executor 一定比单模型更省钱或更高质
reasoning_content 应永远重传或永远不重传
工具 schema memoization 等于 provider prefix cache optimization
```

这些内容只能作为待验证假设进入实验计划。

## 3. 建议的源码与实验下一步

### P0：协议与成本实验

1. 对同一 DeepSeek endpoint 测试 reasoning_content 的 drop/replay 要求与计费差异；
2. 测试固定 system/tools、工具顺序漂移、mode 切换、compaction 对 cache hit 的影响；
3. 比较 Reasonix 与 CodeWhale 的 prefix/cache 策略；
4. 固定任务集测 Flash router、planner/executor 和 Pro review 的质量/成本。

### P1：源码继续深读

1. Codex：guardian、hooks、skills/subagents、provider、app-server 与 context manager；
2. Reasonix：planner/coordinator、checkpoint、sandbox、plugin 与 E2E tests；
3. Hermes：memory/skill provenance、gateway authority、cron 与 sandbox；
4. CodeWhale：auto router、prompt zones 接线状态、reasoning replay 测试与 side-git；
5. Trae：Docker 安全边界、MCP、trajectory 性能与错误恢复；
6. Claude Code：仅继续审官方 plugins/docs，逆向代码保持 C 级隔离。

## 4. 强制状态修正

截至 2026-06-04：

```text
六项目“源码事实校准 Pass 1”完成；
不再使用“终版源码调研”描述快速变化项目；
此前总评必须与 17-0 / 17-1 / 17-2 / 17-3 一起阅读；
下一阶段先做协议与 benchmark 验证，再把结论写入产品战略和技术架构。
```
