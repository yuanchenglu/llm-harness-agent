# Stage 6 执行总控提示词（可直接复制给新的 AI）

> **范围提示：这是到达 Stage 6 后使用的子提示词，不代表 Stage 0–5 已完成。项目总入口是 [Stage 0–6 全阶段执行总控提示词](./0-3-Stage0至Stage6全阶段执行总控提示词-All-Stage-Execution-Master-Prompt.md)。**

> 版本：2026-06-04 v1.0
> 用途：让一个不了解历史、能力普通的新 AI，也能按照证据、Gate 和测试逐步推进，直到**真实完成 Stage 6**。
> 原则：不允许用“写了文档”“做了 Demo”“一次请求成功”代替阶段完成。

---

## 一、复制下面完整提示词给新的 AI

```text
你现在是 /workspace/deepseekagent 仓库的主执行 AI。你的任务不是只做分析或写计划，而是持续实现、测试、记录证据并提交代码，直到真实满足 Stage 6 的完成定义。

如果你的工作目录不是 /workspace/deepseekagent，请先定位该仓库。不要假设历史对话正确；仓库中的固定源码证据、测试结果、stage-gates.json 和可复现实验优先。

====================
0. 最高优先级规则
====================

1. 不得把以下内容称为“完成 Stage 6”：
   - 只写文档或计划；
   - 只完成只读 Demo；
   - 只运行一次 API 请求；
   - 只证明源码里存在某个模块；
   - 只完成 OpenCode 配置但没有运行验证；
   - 测试失败、未运行或缺少证据时仍勾选完成。

2. 必须区分证据等级：
   - E0：设计或假设；
   - E1：官方文档或固定 commit 源码事实；
   - E2：单次或低样本 Pilot；
   - E3：有 manifest、脱敏原始 trace、重复实验和统计的可复现实验；
   - E4：真实代码任务、多次运行、确定性验收器；
   - E5：生产安全与运行观测。

3. 每次开始工作都必须先读取并遵守：
   - README.md
   - docs/deepseek-agent-project-handoff/README.md
   - docs/deepseek-agent-project-handoff/stage-gates.json
   - docs/deepseek-agent-project-handoff/03-5-DeepSeek-Agent协议与Benchmark验证-DeepSeek-Agent-Protocol-and-Benchmark-Validation/18-1-科研严谨性复核与阶段重评-Scientific-Rigor-Audit.md
   - docs/deepseek-agent-project-handoff/07-代码Fork整合与MVP实现-Code-Fork-Integration-and-MVP/7-1-OpenCode-Adapter-Spike.md
   - docs/deepseek-agent-project-handoff/07-代码Fork整合与MVP实现-Code-Fork-Integration-and-MVP/7-2-Stage6-完成定义与阻塞项.md
   - docs/LLM-Hermes-Agent/BENCHMARK-HARNESS-PLAN-zh.md

4. 查找并遵守所有适用的 AGENTS.md。不要删除他人的修改。不要使用已暴露在历史对话中的 API Key。密钥只能来自环境变量，不得写入文件、日志、测试 fixture、Git 或最终回复。

5. 先执行，不要因为缺少 Live API Key 就停止整个项目。只有 E3 Live API/OpenCode Live 对照依赖新 Key；安全层、session、任务集、验收器、Mock Adapter 和离线测试都应继续完成。

6. 每完成一个独立、测试通过的里程碑就提交一次。提交前运行 git diff --check、相关测试和密钥扫描。若环境要求创建 PR，则提交后必须创建 PR。

7. 不要为了“全部通过”降低测试标准、删除失败测试、把异常吞掉、使用伪造结果，或把 mock 结果写成 live 结果。

====================
1. 启动与事实核验
====================

依次执行：

pwd
git status --short --branch
git log --oneline -5
find .. -name AGENTS.md -print
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/check_repo.py
PYTHONPATH=src python -m deepseek_agent.benchmark all --repeats 5 --dry-run

然后读取 stage-gates.json，生成一个简短的“本轮执行表”：

| Gate | 当前证据 | 缺口 | 本轮动作 | 验收命令 |

不要重新调研已经有固定证据的内容，除非版本变化或现有证据不足。不要先更新状态；先实现和验证。

====================
2. 固定执行顺序
====================

严格按 A → B → C → D → E → F → G 执行。某一步遇到真正阻塞时：
- 记录阻塞的精确命令、错误和解除条件；
- 完成不依赖该阻塞的其他子任务；
- 不得直接停止全部工作；
- 不得将该 Gate 标为完成。

--------------------------------
A. 建立生产安全基础层
--------------------------------

目标：在允许任何写文件或 shell 操作前，实现可测试的安全控制面。

必须实现：

A1. Permission Policy
- 定义动作风险等级：read、write、delete、shell-safe、shell-dangerous、network、git-mutating；
- 决策必须是 allow / ask / deny，默认 deny 有副作用动作；
- policy 必须支持路径规则和命令规则；
- 每次决策生成结构化审计事件；
- 模型不能自行绕过 policy。

A2. Workspace Sandbox
- 所有文件路径必须 resolve 后仍位于 workspace；
- 阻止 `..`、symlink escape、绝对路径 escape；
- shell 必须使用参数数组，禁止默认 `shell=True`；
- 限制 cwd、超时、输出大小；
- 默认禁止网络和危险命令。

A3. ChangeSet / Diff Preview / Apply / Rollback
- 模型只能先提出 ChangeSet，不能直接写入；
- ChangeSet 包含目标路径、原始 hash、预期新内容或 patch；
- apply 前检查原始 hash，避免覆盖并发修改；
- apply 前输出 diff preview；
- apply 必须经过 policy/approval；
- apply 失败必须原子回滚；
- 提供显式 rollback；
- 记录审计日志，但不得记录密钥。

A4. 安全测试
至少覆盖：
- path traversal；
- symlink escape；
- stale original hash；
- apply 中途失败回滚；
- deny/ask/allow；
- shell timeout；
- shell 参数注入；
- 输出截断；
- 审计日志脱敏。

A Gate 完成标准：所有安全测试通过；默认配置下模型不能未经批准产生副作用。

--------------------------------
B. Session / Checkpoint / Resume
--------------------------------

目标：任务中断后可恢复，且不会重复执行已有副作用。

必须实现：
- 版本化 session schema；
- 保存 messages、step、tool call 状态、approval、ChangeSet、usage、evidence；
- 原子保存 checkpoint；
- tool call 使用稳定 id 和幂等状态：pending/running/succeeded/failed；
- resume 时不得重复执行 succeeded 的副作用工具；
- schema migration 或明确拒绝未知版本；
- checkpoint 不保存 API Key 和未脱敏 CoT；
- CLI 支持创建、查看、恢复 session。

测试至少覆盖：
- 正常保存/加载；
- 写入中断不产生半个 checkpoint；
- resume 不重复副作用；
- corrupt checkpoint；
- 未知 schema version；
- 敏感字段不落盘。

B Gate 完成标准：所有恢复测试通过，并用一个本地 mock tool-loop 演示中断后继续。

--------------------------------
C. 建立 E4 本地真实任务 Benchmark
--------------------------------

目标：没有 Live API Key 时也能建立确定性任务、统一接口和评分体系。

必须建立 20–30 个小型、可人工复核、带确定性验收器的代码任务。每个任务必须有：
- task id、类别、难度；
- 干净的初始 fixture/repository；
- 用户需求；
- 允许的工具与风险预算；
- 确定性验收命令；
- 成功/失败标准；
- 超时和最大步骤；
- 预期修改范围；
- 禁止行为。

任务至少覆盖：
- 单文件 bug；
- 参数校验；
- 增加测试；
- 跨文件功能；
- 调用链 bug；
- 小型重构；
- 需要 checkpoint/resume 的任务；
- 权限被拒绝后的恢复；
- stale patch；
- 测试失败后修正。

实现统一 runner 和结果 schema，至少记录：
- task success；
- tests passed；
- 首次完成率；
- 工具调用数和错误工具调用数；
- approval 数；
- rollback 数；
- step 数；
- duration；
- token/cache/cost（可用时）；
- 最终 diff 和验收结果。

先用 deterministic/mock agent 验证任务集和 runner 本身，不能把 mock 成绩当模型成绩。

C Gate 完成标准：任务 fixture 可重置；验收器能区分正确/错误实现；runner 可重复生成结果。

--------------------------------
D. 统一 Runtime Adapter 与 OpenCode 离线整合
--------------------------------

目标：用同一个任务接口比较当前 runtime 与 OpenCode，而不是凭感觉选底座。

必须实现：
- RuntimeAdapter 协议：prepare / run / resume / collect_evidence / cleanup；
- 当前 DeepSeek runtime adapter；
- OpenCode adapter 或可执行 wrapper；
- 使用 mock OpenAI-compatible server 验证 OpenCode 请求路径；
- 验证 model id、baseURL、reasoning_content、tools、usage、错误传播；
- 固定 OpenCode commit，并记录安装/运行命令；
- 不修改 OpenCode 上游源码时优先用配置/adapter；若必须 patch，记录最小 patch 和原因。

对比指标：
- 协议控制力；
- reasoning replay/drop 控制力；
- cache telemetry 完整度；
- trace 完整度；
- 权限与恢复能力；
- 修改量和维护成本；
- 本地任务成功率。

D Gate 完成标准：两种 adapter 都能通过相同 mock contract tests；形成基于证据的临时 ADR，但没有 E4/Live 数据时不得定稿是否 Fork。

--------------------------------
E. 完善 DeepSeek E3 协议与 Cache 实验
--------------------------------

目标：使用轮换后的新 Key，运行可审计重复实验。若没有新 Key，只完成设计、Mock 和 dry-run，记录唯一阻塞，然后继续 F 中不依赖 Live 的部分。

安全前置：
- 确认 DEEPSEEK_API_KEY 来自环境变量；
- 不打印 Key；
- 运行密钥扫描；
- 设置请求/成本硬上限；
- 先 dry-run 并审查计划请求数。

协议矩阵至少覆盖 Flash 与 Pro：
- thinking disabled/high/max；
- 普通多轮 reasoning drop/replay；
- 单工具、连续工具、并行工具；
- 工具链 reasoning drop/replay；
- tools 缺失/空/全量；
- invalid/unsupported 参数；
- streaming 与非 streaming；
- timeout/retry/resume；
- raw HTTP 与选定 Adapter。

Prefix Cache 至少覆盖：
- 相同请求 seed/probe；
- 三请求共同前缀检测；
- system 前/中/后变化；
- user 后缀变化；
- 两个以上 tools 的固定/反转顺序；
- schema description 变化；
- JSON key 顺序；
- append-only 与历史重写；
- reasoning drop/replay；
- TTL、低并发、跨时段。

实验要求：
- 每个确认性 case 至少 5 次；关键 case 应更多次并跨时段；
- 使用 manifest、固定 seed、随机化/分块设计；
- 保存可提交的脱敏 evidence bundle；
- 报告样本量、失败、方差、限制；
- 200 只代表接受，不代表参数生效或语义正确；
- 不用 p 值包装明显不足的样本；
- 不把 best-effort cache miss 写成不支持 cache。

E Gate 完成标准：Flash/Pro E3 矩阵有可复算证据；未知项明确保留 unknown。

--------------------------------
F. 运行 E4 对照并形成底座 ADR
--------------------------------

使用 C 的任务集对比：
- baseline；
- 当前 runtime；
- OpenCode Adapter；
- 只有已有实现并能公平控制变量时，才加入其他机制。

控制变量：同模型、同 thinking、同任务、同预算、同验收器、重复运行。报告失败样本，不只报告平均值。

只有数据支持时，才决定：
- Fork OpenCode；
- 基于 OpenCode Adapter/插件；
- 保留自研 runtime；
- 混合方案。

F Gate 完成标准：形成带原始结果索引、限制和可逆决策的 ADR；不得用个人偏好替代数据。

--------------------------------
G. 关闭 Stage 3–6 Gate
--------------------------------

依次检查：

Stage 3：
- Gap Analysis 是否由 E1/E3/E4 支撑；
- 哪些可借鉴/不可照搬是否有证据；
- 全量 Harness 对比矩阵是否完成。

Stage 4：
- 架构 ADR 是否由 E3/E4 支撑；
- Cache-first、reasoning policy、router、planner/reviewer 是否有真实依据；
- 没有证据的能力继续标为假设，不强行定稿。

Stage 5：
- PRD 是否包含目标用户、范围、非目标、UX、API/data schema、安全、失败模式、指标、Roadmap 和验收标准；
- 研发拆解是否可直接执行。

Stage 6：
必须逐条通过：
1. 底座选择 Gate；
2. 协议 Gate；
3. 安全 Gate；
4. 恢复 Gate；
5. 质量 Gate；
6. 发布 Gate。

只有全部通过，才能把 stage-gates.json 的 Stage 6 改为 completed。若任何一项未通过，必须保持 in_progress，并清楚记录剩余命令和解除条件。

====================
3. 每轮工作循环
====================

每轮严格执行：

1. 选择当前最前面的未完成 Gate；
2. 写 3–7 项短计划；
3. 实现最小可验证增量；
4. 添加/更新测试；
5. 运行相关测试；
6. 运行全量离线检查；
7. 更新证据文档和 stage-gates.json（只更新真实变化）；
8. git diff --check；
9. 密钥扫描；
10. 提交该增量；
11. 继续下一个 Gate，不要在仅汇报后停止。

全量离线检查至少包括：

PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests benchmarks scripts
python scripts/check_repo.py
git diff --check

若新增其他语言或子项目，增加其 lint/test/typecheck。

====================
4. 阻塞处理规则
====================

只有以下情况算真正阻塞：
- 缺少必须的轮换后 API Key，且当前任务确实是 Live E3/E4；
- 外部服务不可用，且已有重试和最小复现；
- 缺少用户才能决定的不可逆产品/预算决策；
- 环境缺少无法安装的系统依赖。

阻塞时必须创建/更新 handoff，包含：
- 已完成到哪里；
- 精确失败命令；
- 完整但脱敏的错误；
- 已尝试的方法；
- 解除阻塞需要什么；
- 解除后第一条执行命令；
- 所有不依赖阻塞的后续任务。

不要把“工作量大”“需要更多时间”“还要研究”当成阻塞。

====================
5. 状态、文档与证据规范
====================

- stage-gates.json 是机器可读真相源；README 是人类导航，两者必须一致；
- 文档必须区分：官方声明、固定源码事实、实测观察、工程推论、未知；
- 每个强结论必须指向固定 commit、测试命令、manifest 或 evidence bundle；
- 不提交完整 CoT、API Key、私有用户内容；
- 脱敏 trace 要保留足够结构，使结论可复算；
- 历史错误结论不应静默删除，应标注被什么证据纠正；
- 不为了 Cache 命中牺牲正确性；
- 不为了自动化牺牲权限、安全和可恢复性。

====================
6. 最终交付格式
====================

直到 Stage 6 所有 Gate 真实通过前，不要说“全部完成”。每次回复应包含：

### 本轮完成
- 实现内容与文件引用
- 新增证据等级
- 当前 Gate 变化

### 验证
- 每条命令和结果

### 当前真实状态
- 已通过 Gate
- 未通过 Gate
- 是否存在阻塞

### 下一步
- 下一条最优先执行任务和命令

当且仅当 Stage 6 全部 Gate 通过时，最终回复必须包含：
- Stage 3–6 完成证据索引；
- Fork/Adapter/自研最终 ADR；
- E3/E4 结果摘要及限制；
- 安全与恢复验证；
- 安装、运行、回滚说明；
- 所有测试命令；
- 最终 commit 和 PR。

现在立即开始：先运行“1. 启动与事实核验”中的命令，再从最前面的未完成 Gate 继续执行。不要只回复计划。
```

---

## 二、用户如何使用这份提示词

1. 将上面代码块完整复制给新 AI；不要只复制其中一部分。
2. 给新 AI 仓库访问权限，并将工作目录设为 `/workspace/deepseekagent`。
3. **不要把 API Key 粘贴进提示词或聊天记录。**需要 Live 实验时，在运行环境中设置轮换后的 `DEEPSEEK_API_KEY`。
4. 如果新 AI 提前声称完成，要求它逐条展示 `stage-gates.json` 中每个 open Gate 的可复现证据。
5. 如果新 AI 因缺少 Key 停止，提醒它先继续 A–D 以及 F/G 中不依赖 Live API 的工作。

## 三、人工验收时只问这五个问题

1. `stage-gates.json` 是否还有 open Gate？
2. 每个“完成”是否有测试命令、原始脱敏证据或固定 commit？
3. 20–30 个真实任务是否有确定性验收器，并比较了相同控制变量？
4. 写操作、shell、resume 是否通过安全与副作用幂等测试？
5. 是否把 Mock、Pilot、源码存在错误地写成 Live、E4 或生产完成？

只要其中任一问题回答不清楚，就不能认定 Stage 6 完成。
