# 06. 整理决策记录

## 1. 2026-06-07 文档分层决策

决策：PRD TechPlan 分成公开入口和内部完整文档两层。

结果：

- 主仓库只保留 `docs/prd-tech-plan/README.md`。
- 子仓库保留 `zh/prd-tech-plan/`。
- 子仓库只保留当前准确 Markdown，不保留旧草案全文和不采用的视觉资产。

理由：

- 公开仓库不应暴露混杂过程草案。
- 完整 PRD / TechPlan / 原型说明不能压进一个巨型 README。
- 后续 AI 需要模块化文档按需读取。
- 子仓库定位是从 0 到 1 开发过程的准确存档。

## 2. 内容融合决策

### 2.1 当前准确主线

保留并融合：

- Blueprint stage truth。
- Blueprint Stage 5 的生产 PRD、runtime/API/data、威胁模型、工程拆解。
- DeepSeek V4 物理特性约束。
- 收敛后的 release lines。
- 技术栈决策。
- 当前有效 UI/UX 信息架构和线框。

### 2.2 不再保留原始旧料

删除但已吸收有效结论：

- 历史 master docs 中的 UI/UX v3 结论。
- 历史 release line 拆分。
- 过细版本规划。
- wireframe 文档中的有效页面结构。
- TXT 参考笔记中的产品、DeepSeek-GUI、微信式交互和开发进展结论。
- 中间审计和决策备忘录。

删除且不进入最终文档：

- 已被更正的旧版本草案全文。
- 不满意的 PNG 视觉草稿。
- 与当前 blueprint 真相冲突的阶段叙事。
- 会误导执行者继续扩张范围的企业、生态、移动端承诺。

## 3. 路线压缩决策

旧路线被压缩为：

- `0.1.x` Public Alpha。
- `0.2.x` Desktop Code Workbench。
- `0.3.x` General Workspace Agent。
- `0.4.x` Integrations And Automation Preview。
- `1.0` Stable Public Release。

理由：

- 原拆分过细。
- 多个版本重复同一 runtime 底座。
- Memory、Skill、PlanGraph 是同一长期任务能力链。
- MCP、自动化、远程审批同属外部连接阶段。
- 1.0 应聚焦稳定公开发布，不应变成企业平台。

## 4. 技术栈决策

当前推荐：

- Python runtime。
- Python CLI。
- React + TypeScript desktop UI。
- Electron first。
- Local HTTP/SSE runtime bridge。
- JSONL event log as evidence truth source。
- SQLite optional index。

理由：

- 当前源码和测试地基在 Python。
- Release gate 不应被 runtime 重写拖延。
- DeepSeek-GUI 证明 desktop shell + local runtime + HTTP/SSE 是可行产品边界。
- 真正一级问题是 DeepSeek-native、cache discipline、policy、rollback、evidence 和 release gate，不是壳体轻量化。

## 5. DeepSeek 物理特性决策

以下必须成为 release-critical gates：

- byte-stable prefix。
- cache hit/miss evidence。
- Flash-first / Pro-on-checkpoint route reason。
- layout-driven context packing。
- reasoning content display/archive boundary。
- Memory / Skill / Tool catalog 不破坏 prefix discipline。

理由：

- 这些不是产品口号，是 DeepSeek-native Agent 的工程边界。
- 如果不能验证这些点，产品只是 generic Agent shell。

## 6. Completion-first 定位决策

决策：PRD TechPlan 的最高层定位改为 completion-first，即以真实项目任务的可验证完成率为第一指标；省 token、懂项目、更可控是服务这个目标的约束和手段。

理由：

- 旧定位“让 DeepSeek 更会做事：更省 token、更懂项目、更可控”方向正确，但容易被执行成并列口号。
- Blueprint Stage 4 已把完成定义绑定到协议正确、cache 可观测、副作用可控和 deterministic verifier。
- Blueprint Stage 5 已包含确定性任务成功率、首次完成率和每成功任务成本。
- Release gate 未关闭前，不能把“极高完成率”写成当前事实，只能写成待证实的 gate 和指标。

非目标：

- 不重开 runtime 架构选型。
- 不扩大 release line。
- 不以单次请求 token 更低替代任务完成、正确性、安全或恢复证据。

## 7. UI/UX 决策

当前只保留：

- Mode-based navigation。
- Code / 助理 / 连接手机三模式模型。
- 左侧 mode context。
- 右侧 context panel。
- Code 工作台核心线框。
- 新建需求、计划详情、diff 审查关键流程。

不保留：

- 不满意的视觉草稿。
- 批量生成的展示图。
- 未确认线框之前的高保真方向。

## 8. 后续维护规则

- 新文档必须先说明依据和置信度。
- 修改路线前先核对 `stage-gates.json`。
- 产品功能进入主线前必须写清用户价值、非目标和 release gate。
- 技术选型变更必须说明它解决的一级问题。
- 删除内容前先确认是否已融合有效结论。
- 不再把“过程存档”理解为保留错误旧文档全文。
