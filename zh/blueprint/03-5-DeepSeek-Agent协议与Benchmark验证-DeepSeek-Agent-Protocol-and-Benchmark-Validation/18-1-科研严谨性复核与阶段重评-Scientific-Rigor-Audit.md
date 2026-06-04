# 科研严谨性复核与阶段重评

> 复核日期：2026-06-04；结论：此前“已严谨完成至 Stage 6”的表述不成立，现已纠正。

## 1. 对此前工作的审计结论

此前工作完成了可运行的低预算 Pilot 和只读原型，但不满足科研意义上的确认性实验，也不满足生产级 Stage 6。主要问题如下：

1. **样本不足**：每个 Prefix Cache case 仅执行两次，不能估计方差、稳定性或显著差异。
2. **实验混杂**：case 按固定顺序执行；DeepSeek Cache 会因先前请求建立共同前缀，case 之间并非独立。
3. **无随机化与分块**：服务负载、Cache 建立时间和请求顺序可能解释结果。
4. **证据不可审计**：原始 JSONL 被忽略且未提供脱敏证据包；文档中的汇总值无法由仓库内容复算。
5. **Fingerprint 不严谨**：旧实现对 JSON key 排序后计算 fingerprint，但实际 wire payload 未排序，不能证明字节相同。
6. **只看 HTTP 成功**：`200` 只能证明请求被接受，不能证明参数生效、工具链语义正确或任务质量合格。
7. **协议矩阵不完整**：缺少 Pro、流式、连续/并行工具、多 user turn、错误 schema、strict beta、TTL、并发和跨日实验。
8. **Prefix 结论过度**：没有根据官方“完整 cache prefix unit、共同前缀检测、best-effort”机制设计三请求序列。
9. **Stage 3–5 是草案而非完成品**：只有短文档，没有真实任务 Benchmark 支撑 router/planner/reviewer 决策。
10. **Stage 6 不是 Fork/整合完成**：未完成 OpenCode Adapter 运行验证，也没有权限、sandbox、写操作、恢复和验收任务集。

因此，旧 Pilot 只能标为 **探索性观察**，不得用于性能承诺或因果结论。

## 2. 本次严谨性修正

- wire fingerprint 改为对实际发送字节计算 SHA-256；
- trace schema 升级到 v2，保留结构化响应证据、request id、错误类别，同时移除回答正文与 CoT；
- 每个 case 明确 research question、hypothesis 与 interpretation limit；
- 默认重复次数提高到 5；低于 5 必须显式 `--allow-pilot`；
- 协议 case 使用固定 seed 随机化执行顺序；Prefix Cache 使用“随机化序列顺序、固定序列内步骤”的分块设计，并保存 manifest、schedule、Git commit 与官方文档快照；
- 汇总包含成功率、状态分布、延迟分布与 cache hit rate，不再只报告累计值；
- Prefix case 使用 run-specific block 前缀，降低历史账户流量造成的交叉污染，但仍明确其为观察性证据；
- 增加可注入 transport、HTTP/transport 错误分类、精确 wire hash 和敏感数据测试；
- 对 OpenCode 使用固定 commit 源码 Spike，区分“可配置”“源码支持”“已运行验证”。

## 3. 证据等级与阶段完成标准

| 等级 | 含义 | 可支持的结论 |
|---|---|---|
| E0 | 设计或假设 | 只能进入待验证清单 |
| E1 | 官方文档或固定 commit 源码 | 可说明声明/实现存在，不能说明运行效果 |
| E2 | 单次或低样本 Pilot | 可发现问题，不可作稳定性/因果结论 |
| E3 | 可复现重复实验，含 manifest/raw redacted trace/统计 | 可支持受边界约束的实证结论 |
| E4 | 真实任务 Benchmark、多次/跨时段运行 | 可支持产品架构取舍 |
| E5 | 生产观测与安全验证 | 可支持生产发布 |

## 4. 重新评定的阶段状态

| 阶段 | 严谨状态 | 原因 |
|---|---|---|
| Stage 2.5 协议/Cache Harness | **基础设施完成，确认性实验未完成** | 离线可复现框架已补齐；缺新 Key 下的 E3 扩展运行 |
| Stage 3 Gap Analysis | **v0.1 草案** | 有源码事实与 Spike，但缺真实任务 E4 数据 |
| Stage 4 产品战略/架构 | **v0.1 假设性架构** | ADR 可用，但 router/planner/cache ROI 未实证 |
| Stage 5 PRD/研发拆解 | **研究型 MVP PRD v0.1** | 不等于生产 PRD |
| Stage 6 Fork/整合/MVP | **只读研究型 MVP + OpenCode 源码 Spike；完整 Stage 6 未完成** | 缺 OpenCode live adapter、写权限安全层、session/resume、真实任务验收 |

## 5. 不可绕过的下一 Gate

1. 轮换已暴露在对话中的 API Key；使用新 Key 执行 E3 矩阵并保存脱敏 evidence bundle。
2. 建立 20–30 个带确定性验收器的真实代码任务，重复对比 baseline、当前 MVP 与 OpenCode Adapter。
3. 只有当 permission policy、diff preview、sandbox、rollback 与恢复测试通过后，才开放写文件或 shell。
4. 只有 E4 数据显示收益，才定稿 Flash/Pro Router、Planner/Executor、Pro Review 与 Cache-first ROI。
