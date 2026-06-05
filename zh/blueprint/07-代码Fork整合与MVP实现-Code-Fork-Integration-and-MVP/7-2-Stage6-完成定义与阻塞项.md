# Stage 6 完成定义与当前阻塞项

## 完成定义

只有以下 Gate 全部通过，才能写“Stage 6 完成”：

1. **底座选择 Gate**：当前 runtime 与 OpenCode Adapter 在同一真实任务集对比，形成有数据的 Fork/Adapter/自研 ADR；
2. **协议 Gate**：Flash/Pro、thinking、连续/并行工具、streaming、resume 的 E3 矩阵通过；
3. **安全 Gate**：写操作与 shell 具备 permission policy、workspace sandbox、diff preview、rollback 和审计日志；
4. **恢复 Gate**：session/checkpoint 可在中断后恢复，工具调用不重复产生副作用；
5. **质量 Gate**：20–30 个确定性任务验收器，多次运行并报告成功率、成本、cache、延迟与人工干预；
6. **发布 Gate**：威胁模型、密钥处理、失败模式、安装/卸载和兼容性测试通过。

## 当前已通过

- 只读研究型 CLI MVP；
- workspace path escape 防护与敏感字段脱敏测试；
- 可审计 Benchmark Runner 的离线基础设施；
- OpenCode 固定 commit 源码审计与两个 targeted tests。
- DeepSeek Flash/Pro E3 protocol/cache/cross-time live bundle；
- permission policy、workspace sandbox、diff preview、stale hash、rollback；
- session checkpoint/resume；
- OpenCode fixed-source live probe；
- rotated-key E4 live tiny-fixture benchmark：Flash 20/20，Pro 20/20；
- install/uninstall smoke drill。

## 当前阻塞

- Production Release Gate 未通过；
- 尚未完成 Windows 兼容矩阵；
- 尚未完成桌面安装包验证；
- 尚未完成签名 / 卸载验证；
- 尚未完成 release rollback drill；
- 尚未形成生产发布决策证据。

这些不是可以通过“多写一份文档”绕过的问题。当前仓库可以声明 Stage 6 研究 MVP Gate 完成，但必须保持 Production Release Gate 未通过，直到上述 Gate 有可复现证据。
