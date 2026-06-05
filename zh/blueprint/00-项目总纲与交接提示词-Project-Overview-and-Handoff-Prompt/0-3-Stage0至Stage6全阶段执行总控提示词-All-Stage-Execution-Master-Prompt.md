# Stage 0–6 全阶段执行总控提示词（复制给新的 AI）

> 这是项目最高优先级交接提示词。Stage 6 提示词只是本提示词到达 Stage 6 后使用的子计划。当前最早未完成阶段是 **Stage 2.5**，不得直接跳到 Stage 6 并假设前置阶段完成。

## 复制下面完整代码块给新的 AI

```text
你现在负责持续推进 /workspace/deepseekagent，直到 Stage 0–6 的所有 Gate 真实完成。你必须实现、验证、记录证据、提交代码；不能只写计划或文档后停止。

一、事实优先与禁止事项

1. 不要相信历史回复里的“已完成”。机器真相源是：
   - docs/LLM-Hermes-Agent/zh/blueprint/stage-gates.json
   - docs/LLM-Hermes-Agent/zh/blueprint/01-总体计划与阶段管理-Master-Plan-and-Stage-Tracking/1-2-Stage0至Stage6全阶段完成度审计-All-Stage-Completion-Audit.md
   - 固定 commit 源码、官方文档、测试、manifest、脱敏 evidence bundle 和真实任务验收结果。
2. 当前最早未完成阶段是 Stage 2.5。原则执行顺序：Stage 2.5 → 3 → 4 → 5 → 6。
3. 可以并行实现不依赖前置结论的安全基础设施，但不能因此提前把后续阶段标为 completed。
4. 不得把 Pass 1、v0.1 草案、文档存在、模块存在、Mock、单次 Pilot、只读 Demo 写成阶段完成。
5. 每个结论标注证据等级：E0 假设；E1 官方文档/固定源码；E2 低样本 Pilot；E3 可复现实验；E4 真实任务 Benchmark；E5 生产安全与观测。
6. 不得使用历史聊天中暴露的 API Key。密钥仅从环境变量读取，禁止写入仓库、日志、fixture 或回复。
7. 查找并遵守所有 AGENTS.md。不要删除他人的修改或为了通过测试降低标准。
8. 每个独立且测试通过的增量都要提交；环境要求时提交后创建 PR。

二、启动检查

进入仓库后立即执行：

pwd
git status --short --branch
git log --oneline -5
find .. -name AGENTS.md -print
cat docs/LLM-Hermes-Agent/zh/blueprint/stage-gates.json
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/check_repo.py
PYTHONPATH=src python -m deepseek_agent.benchmark all --repeats 5 --dry-run

然后阅读：

1. README.md
2. docs/LLM-Hermes-Agent/zh/blueprint/README.md
3. docs/LLM-Hermes-Agent/zh/blueprint/01-总体计划与阶段管理-Master-Plan-and-Stage-Tracking/1-2-Stage0至Stage6全阶段完成度审计-All-Stage-Completion-Audit.md
4. docs/LLM-Hermes-Agent/zh/theory/research-method.md
5. 当前最早未完成阶段的 README、计划、证据索引和已有报告

输出本轮执行表：

| 阶段/Gate | 当前证据 | 缺口 | 本轮动作 | 验收命令 |

从最早未完成 Gate 开始执行，不要只回复计划。

三、Stage 0–6 固定完成 Gate

Stage 0：项目总纲与交接
- 保持 README、master plan、manifest、stage-gates 和提示词一致；
- 自动检查链接、JSON、密钥和状态矛盾；
- 状态变化时同步更新，不维护即重新打开 Gate。

Stage 1：DeepSeek V4 模型事实校准
- 为所有高影响来源记录官方 URL、类型、版本/commit、访问日期；
- 逐条复核 V4 模型结构、上下文、thinking、tool calls、cache、pricing、encoding、kernel/serving 结论；
- 将 V4 官方事实与 V3/V3.2 外推、产品声明、工程推论分开；
- 建立 fixed-source snapshot index、事实校准报告和 unknowns register；
- 修正文档中的错误、过时或绝对化结论；
- Stage 1 只有在高影响结论均有证据分类、未知项明确登记后才能完成。

Stage 2：竞品/Harness 源码调研
- 完成 P0 项目固定 commit Pass 2：OpenCode、OMO、OMC、OpenSpec、Superpowers；
- 对 Claude Code 永久记录官方公开源码边界，不伪造 engine 源码深读；
- 复核 Codex、Trae、Reasonix、Hermes、CodeWhale 的运行路径和测试证据；
- 对 Cursor、Windsurf、Cline/Roo、Devin、OpenHands、Goose、Aider逐项决定：纳入、延期或排除，并写理由；
- 建立统一证据矩阵：声明、模块、真实调用路径、单测、E2E、生产成熟度；
- 统一清理“终版、完整、最优、直接迁移”等无证据措辞。

Stage 2.5：DeepSeek API 与 Prefix Cache E3
- 使用轮换后的环境 Key；无新 Key 时继续其他阶段中不依赖 Live 的任务，不得整体停止；
- 完成 Flash/Pro、thinking、普通多轮、连续/并行工具、streaming、错误参数、resume、raw HTTP/Adapter 协议矩阵；
- 完成 Prefix Cache 的 seed/probe、共同前缀、位置变化、tool/schema/JSON 顺序、append/rewrite、reasoning、TTL、并发和跨时段矩阵；
- 保存 manifest、随机化/分块 schedule、脱敏原始 trace、统计、限制与可复算 evidence bundle；
- 200 只代表接受，不代表参数生效或语义正确。

Stage 3：架构对比与借鉴评估
- 用统一维度覆盖所有纳入项目；
- 产出 Harness 设计模式、反模式、borrow/adapt/reject 矩阵；
- 结论必须引用 Stage 1、2、2.5 和 E4 数据；
- 完成 OpenCode Adapter / Fork / 自研的可比较维度；
- 没有证据的结论保持假设。

Stage 4：产品战略与技术架构定稿
- 完整定义目标用户、价值、产品边界、桌面/CLI、Agent Mode/Code Mode 和竞争策略；
- 用 E3/E4 决定 cache、reasoning、Flash/Pro router、planner/reviewer 和底座；
- 完成 Runtime、Context Compiler、Tool/Safety、Evidence、Session、UI、部署、可观测性和迁移架构；
- 所有 ADR 包含背景、选项、证据、决定、代价、回滚条件；
- 未有证据的设计不能标为最终架构。

Stage 5：生产 PRD、UX 与研发拆解
- 完成桌面端、Agent Mode、Code Mode 的用户流程、信息架构和交互规格；
- 完成 permission、diff、checkpoint、cost/cache telemetry、任务中心、失败恢复 UX；
- 完成生产 Runtime/API/data schema、威胁模型、失败模式、兼容性、发布与回滚计划；
- 研发拆解包含 Epic、Story、依赖、验收标准、测试、风险和估算；
- 建立 20–30 个确定性真实代码任务及验收器，供 Stage 6 使用。

Stage 6：Fork / 整合 / MVP
- 到达本阶段后，完整读取并执行：
  docs/LLM-Hermes-Agent/zh/blueprint/00-项目总纲与交接提示词-Project-Overview-and-Handoff-Prompt/0-2-Stage6执行总控提示词-Stage6-Execution-Master-Prompt.md
- 必须通过底座选择、协议、安全、恢复、质量和发布六个 Gate；
- 实现 permission policy、sandbox、diff preview/apply/rollback、session/checkpoint/resume；
- 当前 runtime 与 OpenCode Adapter 通过相同 mock contract 和 E4 任务；
- 用 E3/E4 形成 Fork/Adapter/自研最终 ADR；
- 只有全部 Gate 通过才可将 Stage 6 标为 completed。

四、每轮执行循环

每轮必须：

1. 从 stage-gates.json 找最早未完成 Gate；
2. 选一个可在本轮完成的最小验证增量；
3. 实现代码/调研/证据，不先改完成状态；
4. 添加自动检查或测试；
5. 运行局部测试和全量离线检查；
6. 更新事实报告、证据索引、README、manifest 和 stage-gates；
7. 只把有证据通过的 Gate 从 open 移到 passed；
8. 运行 git diff --check 和密钥扫描；
9. 提交；
10. 继续下一增量，不要仅汇报后停止。

全量离线检查至少包括：

PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests benchmarks scripts
python scripts/check_repo.py
git diff --check

新增语言或子项目时，加入对应 lint/typecheck/test。

五、阻塞处理

只有外部凭证、外部服务、不可安装依赖或用户才能作出的不可逆决定算真正阻塞。阻塞时必须：

- 记录精确命令、脱敏错误、已尝试方法、解除条件和解除后的第一条命令；
- 继续所有不依赖该阻塞的工作；
- 保持 Gate open；
- 不把“工作量大、需要研究、没有 Key”作为整体停止理由。

六、完成与回复规则

- `stage-gates.json` 是阶段状态真相源；任何 open Gate 都意味着相应阶段未完成；
- 每个“完成”必须能指向固定来源、测试命令、manifest/evidence 或真实任务结果；
- 每轮回复包含：本轮完成、证据等级、验证命令、真实状态、未完成 Gate、下一步；
- 直到 Stage 0–6 全部 Gate 通过前，禁止说“整个项目完成”；
- 最终完成时提供全阶段证据索引、最终 ADR、E3/E4 结果、安全/恢复验证、安装/运行/回滚说明、测试命令、commit 和 PR。

现在立即开始启动检查，从 Stage 2.5 的最早 open Gate 开始；不要直接跳到 Stage 6，不要只回复计划。
```

## 用户验收新 AI 的简单方法

每次只要求它回答并证明：

1. `earliest_incomplete_stage` 是什么？
2. 本轮关闭了哪个 open Gate？证据在哪里？
3. 有没有跳过前置阶段去定稿后续结论？
4. README、manifest 和 `stage-gates.json` 是否一致？
5. 下一条可直接执行的命令是什么？

只要新 AI 不能回答或无法提供证据，就让它继续执行，不要接受“已完成”。
