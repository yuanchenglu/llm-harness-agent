# 1-1-总体计划与阶段管理 Master Plan and Stage Tracking

> 本文件是 README 的计划部分拆分版，方便后续单独维护。  
> 正式更新进度时，优先更新根目录 README.md。

## 阶段总览

```text
Stage 0：项目总纲与交接机制
Stage 1：DeepSeek V4 源码与物理特性调研
Stage 2：Agent 产品 / Harness 竞品调研
Stage 3：竞品架构对比与可借鉴性评估
Stage 4：DeepSeek Agent 产品战略与技术架构
Stage 5：PRD / UX / 研发拆解
Stage 6：代码 Fork / 整合 / MVP 实现
```

## 当前进度

- Stage 0：已完成；交接、机器 Gate 与全阶段提示词已一致化。
- Stage 1：已完成；固定来源索引、当前事实校准、外推分离、高影响结论复核与 unknowns register 已通过验证。
- Stage 2：已完成；六项目校准、五项目固定 commit Pass 2、P1 范围决策、统一证据矩阵与过度声明复核已通过。
- Stage 2.5：已完成；E3 Flash/Pro 协议矩阵、Prefix Cache 跨时间验证与脱敏 evidence bundle 已提交。
- Stage 3：已完成；全量 Harness 矩阵、模式/反模式、借鉴/改造/拒绝决策和 E4 输入已完成。
- Stage 4：已完成；E3/E4 约束后的产品战略、Flash/Pro 路由、Cache 与 runtime ADR 已定稿。
- Stage 5：已完成；生产 PRD、桌面双模式 UX、Runtime API/Data、威胁模型与可执行验收拆解已完成。
- Stage 6：研究 MVP Gate 已完成；安全写入链路、session resume、OpenCode fixed-source live probe、rotated-key E4 20/20 与 install/uninstall smoke 已通过。生产 Release Gate 未通过。

当前最早未完成项：`6-release`。

剩余任务只剩 Production Release Gate：Windows、桌面安装包、签名/卸载、兼容矩阵、release rollback drill 与发布决策证据。不能把 Stage 6 写成生产发布完成，直到这些证据闭环。

详细依据见 [Stage 0–6 全阶段完成度审计](./1-2-Stage0至Stage6全阶段完成度审计-All-Stage-Completion-Audit.md)。
