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

## 当前阻塞

- 用户此前提供的 API Key 已暴露在对话中，科研与安全规范要求先轮换，不能继续把它用于新的确认性实验；
- 尚无经用户确认的真实代码任务集、成功判定器与实验预算；
- OpenCode live direct-provider Adapter 需要新 Key 才能与当前 runtime 做公平对照；
- 写操作安全层与 session resume 尚未实现。

这些不是可以通过“多写一份文档”绕过的问题。当前仓库必须保持 Stage 6 `in_progress`，直到 Gate 有可复现证据。
