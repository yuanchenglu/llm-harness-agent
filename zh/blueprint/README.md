# DeepSeek Agent 项目交接包 README

> 版本：v0.1  
> 日期：2026-06-04  
> 用途：这是 DeepSeek Agent 项目的总控包 / 交接包。任何 AI 或人接手本项目时，应先阅读本 README，然后按阶段顺序执行任务，并在完成后更新勾选状态。  
> 当前状态：**Stage 0–5 已完成；Stage 6 研究 MVP Gate 已完成；生产 Release Gate 未通过。当前最早未完成项是 `6-release`。完成声明以 `stage-gates.json` 为准。**

---

## 1. 项目一句话目标

构建一个针对 **DeepSeek V4 Flash / Pro** 独特优化的桌面端 Agent 产品：

```text
DeepSeek Agent = DeepSeek V4 + Cache-first / Layout-driven / Checkpoint-gated / Flash-Pro-routed Harness
```

产品形态：

```text
Mac / Windows 桌面端优先
CLI 作为附属入口
Agent Mode + Code Mode
```

---

## 2. 为什么要做这个项目

核心公式：

```text
LLM + Harness = Agent
```

历史调研提出了以下待逐项校准的 DeepSeek V4 模型侧能力假设：

```text
1M context
CSA / HCA Hybrid Attention
sliding_window=128
sparse top-k retrieval
MoE routed/shared experts
mHC multi-copy residual
FP4 routed experts + FP8 mixed precision
DSML tool calling / dedicated encoding
thinking effort modes
API cache hit/miss pricing
```

其中只有完成固定来源校准或 E3 实证的能力才能进入最终架构约束；其余保持为外推、工程假设或 unknown。

---

## 3. 当前目录结构

```text
README.md
00-项目总纲与交接提示词-Project-Overview-and-Handoff-Prompt/
01-总体计划与阶段管理-Master-Plan-and-Stage-Tracking/
02-DeepSeek-V4源码调研-DeepSeek-V4-Source-Research/
03-Agent竞品Harness调研-Agent-Competitor-Harness-Research/
03-5-DeepSeek-Agent协议与Benchmark验证-DeepSeek-Agent-Protocol-and-Benchmark-Validation/
04-竞品架构对比与借鉴评估-Architecture-Comparison-and-Borrowing-Assessment/
05-DeepSeek-Agent产品战略与技术架构-Product-Strategy-and-Technical-Architecture/
06-PRD-UX与研发拆解-PRD-UX-and-Engineering-Breakdown/
07-代码Fork整合与MVP实现-Code-Fork-Integration-and-MVP/
99-归档与原始压缩包-Archives-and-Original-Zips/
```

---

## 4. 总体阶段计划与进度

### Stage 0：项目总纲与交接机制

- [x] 明确项目目标
- [x] 明确执行顺序：先模型事实，再行业事实，再架构综合，再产品 PRD，再代码实现
- [x] 建立 README 作为任务总控入口
- [x] 写入 Stage 0–6 全阶段执行总控提示词和 Stage 6 子提示词

### Stage 1：DeepSeek V4 源码与物理特性调研（已完成：事实边界已校准）

- [x] 定位 DeepSeek V4 官方源码、模型卡、config、技术报告、kernel、encoding
- [x] 完成 Phase 1-2：源码地图 + config 差异
- [x] 完成 Phase 3-4：模型结构 + Hybrid Attention
- [x] 完成 Phase 5-6：MoE + mHC
- [x] 完成 Phase 7-8：Kernel + Encoding
- [x] 完成 Phase 9-10：能力矩阵 + Harness 约束初稿
- [x] 生成 DeepSeek V4 源代码调研全量终版包 v1.1
- [x] 将 v1.1 整合进本交接包
- [x] 建立当前官方来源的固定版本 / 访问日期索引
- [x] 区分 V4 当前事实、V3/V3.2 外推、产品声明和工程推论
- [x] 校准高影响 Harness 结论并建立 unknowns register

### Stage 2：Agent 产品 / Harness 竞品调研（已完成：固定快照与边界内）

> 已完成 P0 固定 commit Pass 2、统一运行/测试矩阵、P1 范围决策和过度声明复核；E4 真实任务收益不属于本阶段完成声明。

- [x] Claude Code 第一轮预研完成；源码深读未完成
- [x] OpenAI Codex 第一轮预研完成；源码深读未完成
- [x] Trae / Trae SOLO 第一轮预研完成；源码深读未完成
- [x] DeepSeek Reasonix 源码审计 Pass 1 完成
- [x] Hermes Agent 源码审计 Pass 1 完成
- [x] CodeWhale / DeepSeek-TUI 源码审计 Pass 1 完成
- [x] Claude Code / Codex / Trae / Reasonix / Hermes / CodeWhale 官方源码事实校准完成
- [x] 纠正 Trae 开源 test-time scaling 与 CodeWhale 完整 three-zone contract 误报
- [x] DeepSeek API 协议与 Prefix Cache 实验基础设施；历史 Pilot 已降级为 E2，E3/E4 未完成
- [x] OpenCode 源码审计 Pass 1 完成
- [x] Oh My OpenAgent 源码审计 Pass 1 完成
- [x] Oh My ClaudeCode 源码审计 Pass 1 完成
- [x] OpenSpec 源码审计 Pass 1 完成
- [x] Superpowers 源码审计 Pass 1 完成
- [x] 五项目综合借鉴评估完成
- [x] 五项目源码审计 Pass 2：核心 loop / hooks / team state / schema / skills tests
- [x] 其余第二优先级竞品逐项完成纳入 / 延期 / 排除决策
- [x] 建立十一项目统一运行/测试证据矩阵和机器可读证据清单

### Stage 3：竞品架构对比与可借鉴性评估

- [x] OpenCode / OMO / OMC / OpenSpec / Superpowers 分层能力与借鉴矩阵
- [x] 全量 Agent Harness 对比矩阵
- [x] Agent Harness 设计模式总结
- [x] 哪些可借鉴 / 哪些不可照搬
- [x] DeepSeek Agent Gap Analysis v1.0（已接入 E3/E4 tiny-fixture 输入）

### Stage 4：DeepSeek Agent 产品战略与技术架构 v1.0（研究 MVP 定稿）

- [x] 产品背景与定位 v0.1
- [x] 模型侧事实与实测边界
- [x] 竞品拆解与 Gap Analysis
- [x] 产品定位（evidence-first runtime）
- [x] 核心分层架构
- [x] DeepSeek 专属协议与缓存策略
- [x] 技术 ADR
- [x] MVP 功能边界
- [x] 技术选型建议
- [x] 研发路线图
- [x] 风险与取舍
- [x] PRD / 代码整合计划
- [x] E3/E4 约束后的 Flash/Pro、Cache、Runtime 底座 ADR 定稿

### Stage 5：PRD / UX / 研发拆解（生产规格与可执行验收）

- [x] DeepSeek Agent PRD v0.1
- [x] CLI MVP UX / IA
- [x] 核心数据结构与 API
- [x] Runtime Spec v0.1
- [x] Engineering Breakdown
- [x] Roadmap
- [x] 生产 PRD、桌面双模式 UX、Runtime API/Data、威胁模型、可执行验收拆解

### Stage 6：代码 Fork / 整合 / MVP 实现（研究 MVP Gate 完成；生产 Release 未通过）

- [x] OpenCode 固定 commit 源码 Spike；installed CLI provider smoke 已完成；fixed-source live probe 缺源码 checkout
- [x] Fork / Adapter / 自研最终选择：当前采用小型自研 runtime + OpenCode adapter 候选
- [x] 只读研究型 MVP 实现计划
- [x] Permission policy / sandbox / diff preview / rollback / session resume
- [x] 20-task E4 live tiny-fixture benchmark：Flash 18/20，Pro 17/20
- [x] 研究 MVP；[ ] 生产 Release Gate

---

## 5. 下一步应该做什么

新的 AI 或人员接手时，必须使用：[Stage 0–6 全阶段执行总控提示词](00-项目总纲与交接提示词-Project-Overview-and-Handoff-Prompt/0-3-Stage0至Stage6全阶段执行总控提示词-All-Stage-Execution-Master-Prompt.md)。

当前研究阶段顺序已经完成。后续不能写成“生产发布完成”；正确下一步是 Release Gate：

```text
Rotate exposed API key
→ fixed-source OpenCode live probe
→ expand E4 beyond tiny fixtures and repeat
→ install/uninstall/compatibility/security release drills
→ production release decision
```

详细依据见：[Stage 0–6 全阶段完成度审计](01-总体计划与阶段管理-Master-Plan-and-Stage-Tracking/1-2-Stage0至Stage6全阶段完成度审计-All-Stage-Completion-Audit.md)。Stage 6 子提示词只有在到达 Stage 6 时使用。

---

## 6. 调研证据要求

所有论点必须优先基于：

```text
官方源码 > 官方 Docs > 官方模型卡 / 官方博客 > 可信第三方 > 明确标注的工程推论
```

每个关键论点旁边必须带链接，最好是源代码行号链接或官方文档链接。

如果使用泄露源码、非官方镜像、社区逆向仓库，必须明确标注：

```text
来源性质：非官方泄露/镜像，需谨慎使用
可信度：高/中/低
可作为：线索/佐证/不可作为最终事实
```

---

## 7. AI 继续执行提示词

下面这段提示词可以直接给新的 AI，让它接着执行本项目。

```markdown
# AI 继续执行提示词 AI Continuation Prompt

你正在接手一个名为 **DeepSeek Agent** 的产品战略与技术架构项目。

## 你的角色

你是一个顶级 AI Agent 产品架构师、模型应用工程师、源码调研员和技术文档作者。你需要与用户一起，通过“先调研、再讨论、再开发”的方式，设计并最终实现一个针对 **DeepSeek V4 Flash / Pro** 独特优化的桌面端 Agent 产品。

## 项目最终目标

设计并实现一个名为 **DeepSeek Agent** 的产品：

- 形态：纯客户端优先，Mac / Windows 可安装，CLI 作为附属入口。
- 模式：
  - Agent Mode：默认模式，用于通用任务、文件、研究、自动化。
  - Code Mode：代码库模式，用于代码理解、修改、测试、提交。
- 核心思想：`LLM + Harness = Agent`
- DeepSeek 专属优势：
  - V4 Flash / Pro 的 1M context；
  - DeepSeek API 的 cache hit / miss 成本结构；
  - V4 的 CSA / HCA、mHC、MoE、FP4/FP8、DSML encoding 等物理特性；
  - Flash-first / Pro-on-checkpoint 的成本质量路由。

## 重要方法论

必须遵守以下顺序：

```text
先模型事实
再行业事实
再架构综合
再产品 PRD
再代码实现
```

不要跳过竞品调研直接定 Harness 架构。

## 当前状态

已经完成：

- DeepSeek V4 Flash / Pro 官方源码、配置、模型卡、kernel、encoding、API cache 的第一轮完整调研。
- 相关文档已放在：
  - `02-DeepSeek-V4源码调研-DeepSeek-V4-Source-Research/`

接下来应该做：

> Stage 3：Agent 竞品 / Harness 深度调研

第一优先级调研对象：

```text
1. Claude Code
2. OpenAI Codex
3. Trae / Trae SOLO
4. DeepSeek Reasonix
5. Hermes Agent
6. CodeWhale / DeepSeek-TUI
```

其中下一步应优先做：

```text
Claude Code 深度调研
```

## 调研证据要求

所有论点必须基于：

```text
官方源码 > 官方 Docs > 官方模型卡 / 官方博客 > 可信第三方 > 明确标注的工程推论
```

每个关键论点旁边必须带链接，最好是源代码行号链接或官方文档链接。

如果使用泄露源码、非官方镜像、社区逆向仓库，必须明确标注来源性质：

```text
来源性质：非官方泄露/镜像，需谨慎使用
可信度：高/中/低
可作为：线索/佐证/不可作为最终事实
```

不要把泄露源码当作官方事实。

## 文档规范

所有输出文档：

- 正文使用简体中文；
- 文件名格式：`阶段序号-简体中文-English.md`；
- 每个核心文档都要有：
  - 目标；
  - 关键问题；
  - 证据来源；
  - 结论；
  - 对 DeepSeek Agent 的启发；
  - 待验证问题。

## 下一步任务

请从以下任务开始：

```text
3-1-Claude-Code产品形态调研-Claude-Code-Product-Analysis.md
3-2-Claude-Code-Harness架构调研-Claude-Code-Harness-Architecture.md
3-3-Claude-Code上下文权限记忆机制-Claude-Code-Context-Permission-Memory.md
3-4-Claude-Code对DeepSeekAgent的启发-Claude-Code-Lessons-for-DeepSeek-Agent.md
```

调研维度：

```text
1. 产品形态：CLI / IDE / Desktop / Web / Mobile / GitHub / Slack
2. Agent Loop：任务输入、计划、工具调用、执行、审查、恢复
3. Context：CLAUDE.md、memory、compaction、skills、subagents
4. Tool Runtime：file、shell、edit、browser、MCP、git、CI
5. Permission：ask / allow / deny / sandbox / policy
6. State：session、checkpoint、background agents、cloud session
7. Review：diff、tests、logs、PR review、proof
8. UI：plan、logs、permissions、cost、task center
9. 可借鉴点：哪些能借鉴
10. 不可照搬点：哪些不适合 DeepSeek V4 和纯客户端 MVP
```

## 交付方式

每完成一个阶段：

1. 更新根目录 `README.md` 的任务勾选状态；
2. 将新文档放入对应阶段文件夹；
3. 如有新证据，更新证据索引；
4. 不删除旧文档，不覆盖原始调研；
5. 必要时生成新的版本压缩包。

```

---


---

## 9. 每个竞品调研都必须回答的 DeepSeek V4 适配问题

从 v0.3 开始，每一个 Agent / AGI / Coding Agent 产品调研的最终文档，都必须单独回答以下问题：

```text
1. 如果这个产品接入 DeepSeek V4 Flash / Pro，它能发挥 DeepSeek V4 的哪些能力？
2. 为什么能发挥？对应的是该产品 Harness 的哪些设计？
3. 它发挥不了 DeepSeek V4 的哪些能力？
4. 为什么发挥不了？是模型协议、上下文、缓存、工具、权限、路由、UI、部署形态，还是产品定位导致？
5. 如果要让它更好地适配 DeepSeek V4，需要做哪些迭代？
6. 这些迭代它自己有没有可能做？为什么？
7. 对 DeepSeek Agent 的启发是什么？
```

分析维度必须覆盖：

```text
1M context
DeepSeek cache hit/miss pricing
CSA / HCA long-context layout
sliding_window=128 下的 active working set
Flash / Pro / Thinking / Max 路由
V4 DSML tool calling / encoding
reasoning_content drop / archive / summarize
checkpoint-driven Pro review
cost/cache telemetry
local-first / cloud / endpoint 部署差异
```

这部分统一放在每个竞品的 `Lessons for DeepSeek Agent` 文档中，作为最终结论章节。

## 10. 更新规则

每完成一个任务：

1. 更新本 README 的勾选状态；
2. 将新文档放到对应阶段文件夹；
3. 不删除旧文件；
4. 如果发现旧结论错误，新增修订说明，不直接覆盖历史；
5. 需要交付时，重新打包为新版本 zip。


---

## v0.2 更新记录

- [x] 查证并确认 `anthropics/claude-code` 为 Anthropic 官方公开 GitHub 仓库。
- [x] Claude Code 调研证据优先级调整为：官方 GitHub 仓库 + 官方 Docs 双主线。
- [x] 新增 Stage 2A 文档：
  - `3-0-Claude-Code证据索引-Claude-Code-Evidence-Index.md`
  - `3-1-Claude-Code产品形态调研-Claude-Code-Product-Analysis.md`
  - `3-2-Claude-Code-Harness架构调研-Claude-Code-Harness-Architecture.md`
  - `3-3-Claude-Code上下文权限记忆机制-Claude-Code-Context-Permission-Memory.md`
  - `3-4-Claude-Code对DeepSeekAgent的启发-Claude-Code-Lessons-for-DeepSeek-Agent.md`


---

## v0.3 更新记录

- [x] 明确总包生成机制：每次基于上一版总包增量修改，然后重新打成完整总包；不会丢弃旧文件。
- [x] 新增“每个竞品调研都必须回答的 DeepSeek V4 适配问题”。
- [x] 增强 Claude Code `Lessons for DeepSeek Agent` 文档，补充“Claude Code 如果接入 DeepSeek V4，能发挥什么、发挥不了什么、为什么、如何迭代”。


---


---

## 11. v0.5 竞品调研深度升级：Model-Harness Fit

从 v0.5 开始，竞品调研不再停留在“产品功能 / Harness 模块”层面，而必须升级为：

```text
模型物理特性 × Agent Harness 适配机制
```

每个竞品都必须回答：

```text
1. 它如何配合自家模型的物理特性？
2. 这些适配在源码 / Docs / UI / runtime / config 中如何体现？
3. 如果接 DeepSeek V4，能发挥哪些 V4 特性？
4. 发挥不了哪些 V4 特性？为什么？
5. 需要哪些迭代才能变成 V4-native Harness？
6. 它自己是否可能做这些迭代？
7. DeepSeek Agent 应如何借鉴与超越？
```

已新增：

```text
3-A-竞品调研升级方法论-Model-Harness-Fit-Framework.md
3-B-Claude-Code模型适配深度复盘-Claude-Code-Model-Fit-Deep-Dive.md
4-B-Codex模型适配深度复盘-Codex-Model-Fit-Deep-Dive.md
```

## v0.4 更新记录

- [x] 完成 OpenAI Codex 第一轮深度调研。
- [x] 明确 Codex 三条主线：CLI（开源本地 Rust Agent）、App（桌面 command center）、Web/Cloud（异步云端任务）。
- [x] 新增 Stage 2B 文档：
  - `4-0-Codex证据索引-Codex-Evidence-Index.md`
  - `4-1-Codex产品形态调研-Codex-Product-Analysis.md`
  - `4-2-Codex官方源码与CLI架构-Codex-Official-Source-and-CLI-Architecture.md`
  - `4-3-Codex客户端云端审查沙箱-Codex-App-Cloud-Review-Sandbox.md`
  - `4-4-Codex对DeepSeekAgent的启发-Codex-Lessons-for-DeepSeek-Agent.md`

---

## v0.5 更新记录

- [x] 将竞品调研标准从“功能/Harness模块调研”升级为“模型物理特性 × Harness适配机制调研”。
- [x] 新增 `3-A-竞品调研升级方法论-Model-Harness-Fit-Framework.md`。
- [x] 新增 `3-B-Claude-Code模型适配深度复盘-Claude-Code-Model-Fit-Deep-Dive.md`。
- [x] 新增 `4-B-Codex模型适配深度复盘-Codex-Model-Fit-Deep-Dive.md`。
- [x] 明确 v0.4 的 Claude Code / Codex 文档属于“第一轮产品功能级调研”，v0.5 新增文档才是“模型适配深度复盘”。


---

## v0.6 更新记录

- [x] 完成 Trae / Trae SOLO 第一轮深度调研。
- [x] 按 Model-Harness Fit 标准拆分 Trae 两条线：
  - Trae / SOLO 产品线：Work / Code 双模式、Workspace、多格式上下文、云端并行、用户审查产物。
  - Trae Agent 开源研究线：多 provider、工具链、sequential thinking、trajectory recording、Docker mode、test-time scaling。
- [x] 新增 Stage 2C 文档：
  - `5-0-Trae证据索引-Trae-Evidence-Index.md`
  - `5-1-Trae-SOLO产品形态调研-Trae-SOLO-Product-Analysis.md`
  - `5-2-Trae-Agent开源源码与模型适配-Trae-Agent-Open-Source-and-Model-Fit.md`
  - `5-3-Trae-Model-Harness-Fit深度分析-Trae-Model-Harness-Fit-Deep-Dive.md`
  - `5-4-Trae对DeepSeekAgent的启发-Trae-Lessons-for-DeepSeek-Agent.md`


---

## v0.7 重要纠偏记录

- [x] 承认并修正：v0.2 / v0.4 / v0.6 的 Claude Code / Codex / Trae 调研属于第一轮预研，不是完整源码深读。
- [x] 新增 `3-Z-竞品源码深读审计计划与状态修正-Source-Code-Audit-Plan-and-Status-Correction.md`。
- [x] README 中将 Claude Code / Codex / Trae 状态改为“第一轮预研完成；源码深读未完成”。
- [ ] 下一步应补做 Claude Code / Codex / Trae 的源码深读审计。


---

## 12. 源码深读硬性规则

从 v0.8 开始，所有竞品源码调研必须执行以下 8 步，不允许跳步：

```text
1. 仓库结构扫描
2. 关键模块清单
3. 逐文件阅读
4. 函数 / 类 / 配置摘录
5. 证据链接整理
6. Model-Harness Fit Matrix
7. 对 DeepSeek Agent 的迁移判断
8. 产出源码审计报告
```

状态命名必须严格区分：

```text
第一轮预研完成 ≠ 源码深读完成
源码边界确认完成 ≠ 完整 engine 源码审计完成
源码深读 Pass 1 完成 ≠ 全量源码审计完成
```

本规则详见：

```text
03-Agent竞品Harness调研-Agent-Competitor-Harness-Research/
03-5-DeepSeek-Agent协议与Benchmark验证-DeepSeek-Agent-Protocol-and-Benchmark-Validation/
└── 3-Y-源码深读硬性规则-Source-Audit-Mandatory-Rules.md
```


---

## v0.8 更新记录

- [x] 将源码深读 8 步流程写入 README 和项目规则。
- [x] 新增 `3-Y-源码深读硬性规则-Source-Audit-Mandatory-Rules.md`。
- [x] 补做 Claude Code 官方源码边界审计：确认官方仓库主要公开 README + plugins 生态，完整 engine 源码未公开。
- [x] 补做 Codex 源码深读 Pass 1：README / AGENTS.md / config.schema.json。
- [x] 补做 Trae Agent 源码深读 Pass 1：BaseAgent / TraeAgent / TrajectoryRecorder / tools docs。
- [x] 新增源码审计报告：
  - `3-C-Claude-Code源码深读报告-Claude-Code-Source-Audit.md`
  - `4-C-Codex源码深读报告-Codex-Source-Audit.md`
  - `5-C-Trae-Agent源码深读报告-Trae-Agent-Source-Audit.md`


---

## v0.9 更新记录

- [x] 按用户补充，将 `oboard/claude-code-rev` 纳入 Claude Code 审计，严格标注为 C 级逆向源码线索。
- [x] 新增 `3-D-Claude-Code-C级逆向源码审计-Claude-Code-Reverse-Source-Audit.md`。
- [x] 完成 Codex Pass 2：context fragments、InternalModelContextFragment、EnvironmentContext、TurnContext、run_turn、auto compact、config schema。
- [x] 新增 `4-D-Codex源码深读报告Pass2-Codex-Source-Audit-Pass2.md`。
- [x] 完成 Trae Agent Pass 2：BaseAgent、TraeAgent、TrajectoryRecorder、tools/trajectory docs。
- [x] 新增 `5-D-Trae-Agent源码深读报告Pass2-Trae-Agent-Source-Audit-Pass2.md`。
- [x] 新增三者总评：`6-0-ClaudeCode-Codex-Trae源码审计总评-Final-Source-Audit-Summary.md`。
- [x] 将 Claude Code / Codex / Trae 三者调研推进到“足以支撑下一阶段架构设计”的源码审计状态。


---

## v1.0 更新记录

- [x] 完成 Reasonix 源码审计 Pass 1。
- [x] 完成 Hermes Agent 源码审计 Pass 1。
- [x] 完成 CodeWhale / DeepSeek-TUI 源码审计 Pass 1。
- [x] 新增三者总评：`10-0-Reasonix-Hermes-CodeWhale源码审计总评-Source-Audit-Summary.md`。
- [ ] 下一步继续 CodeWhale Rust core、Reasonix Go core、Hermes gateway/cron/memory/skill 的逐文件深读。


---

## v1.1 更新记录

- [x] 按用户要求，不再等待“继续”，独立完成 Reasonix / Hermes / CodeWhale 三者 Pass 2 深度源码调研。
- [x] 新增 CodeWhale Pass 2：`9-1-CodeWhale源码审计Pass2-CodeWhale-Source-Audit-Pass2.md`。
- [x] 新增 Reasonix Pass 2：`7-1-Reasonix源码审计Pass2-Reasonix-Source-Audit-Pass2.md`。
- [x] 新增 Hermes Pass 2：`8-1-Hermes-Agent源码审计Pass2-Hermes-Agent-Source-Audit-Pass2.md`。
- [x] 新增终版综合：`10-1-Reasonix-Hermes-CodeWhale深度源码调研终版综合-Final-Deep-Source-Synthesis.md`。
- [x] 三者已完成到“可支撑 DeepSeek Agent 产品战略与技术架构设计”的源码调研深度。
- [ ] 下一阶段：撰写《DeepSeek Agent 产品战略与技术架构 v0.1》。


---

## v1.2 更新记录

- [x] 按用户要求，将 OpenCode、Oh My OpenAgent、Oh My ClaudeCode、OpenSpec、Superpowers 纳入正式竞品 / 插件调研范围。
- [x] 严格按源码深读硬性规则标注为“源码审计 Pass 1”，未将仓库扫描和官方文档调研误报为全量源码审计。
- [x] 新增五份独立报告：
  - `11-0-OpenCode源码审计Pass1-OpenCode-Source-Audit-Pass1.md`
  - `12-0-Oh-My-OpenAgent源码审计Pass1-Oh-My-OpenAgent-Source-Audit-Pass1.md`
  - `13-0-Oh-My-ClaudeCode源码审计Pass1-Oh-My-ClaudeCode-Source-Audit-Pass1.md`
  - `14-0-OpenSpec源码审计Pass1-OpenSpec-Source-Audit-Pass1.md`
  - `15-0-Superpowers源码审计Pass1-Superpowers-Source-Audit-Pass1.md`
- [x] 新增综合分层与迁移优先级报告：`16-0-五项目综合借鉴评估-Five-Project-Synthesis.md`。
- [x] 初步明确五层借鉴关系：OpenCode Runtime、OMO Harness 增强、OMC 编排状态机、OpenSpec Artifact 协议、Superpowers 工程技能方法论。
- [x] 五项目 Pass 2、统一证据矩阵与 P1 范围决策已完成；真实任务收益统一转交 Stage 3/6 E4。


---

## v1.3 更新记录：既有六项目源码事实校准

- [x] 通过 GitHub API 获取 Claude Code、Codex、Trae Agent、Reasonix、Hermes Agent、CodeWhale 官方仓库固定 commit 源码快照。
- [x] 新增统一事实校准方法、证据等级和实现成熟度规则：`17-0-六项目源码事实校准方法与证据清单-Six-Project-Source-Calibration-Method.md`。
- [x] 新增两组六项目事实复核与一份校准后综合结论：`17-1`、`17-2`、`17-3`。
- [x] 为既有 Claude Code / Codex / Trae 产品与源码报告，以及 Reasonix / Hermes / CodeWhale 源码报告加入校准提示，要求与固定 commit 校准报告共同阅读。
- [x] 纠正 Trae Agent：官方开源源码未发现 multi-candidate generation–pruning–selection / test-time scaling runtime。
- [x] 纠正 CodeWhale：已接入的是 system prompt + tool catalog 的 prefix drift check；完整 three-zone request contract 仍明确标注尚未接入 request path。
- [x] 明确 Claude Code 官方仓库不含完整 engine；Codex 核心判断成立但路径持续变化；Reasonix/Hermes 的实现事实与设计评估必须分栏。
- [ ] 下一步先执行 DeepSeek API 协议与成本 benchmark，再将相关结论写入产品战略和技术架构。


---

## v1.4 更新记录：理论引导文档重构

- [x] 将 `docs/LLM-Hermes-Agent` 从观点文章集合升级为 DeepSeek Agent 理论与调研入口。
- [x] 新增中英文理论总纲：`THEORY-GUIDE-zh.md` / `THEORY-GUIDE.md`。
- [x] 新增中英文研究方法与事实校准：`RESEARCH-METHOD-zh.md` / `RESEARCH-METHOD.md`。
- [x] 将交接调研中的模型事实、竞品源码校准和产品综合结论提炼进理论文档，而非复制完整交接目录。
- [x] 纠正 CodeWhale 官方归属、Trae test-time scaling、完整 three-zone contract、reasoning_content 普遍删除、tool schema delta 等错误或过度观点。
- [x] 为 14 组中英文创新论文统一增加证据说明，要求区分源码事实、设计假设与待验证实验。
- [ ] 下一步仍是协议与 benchmark 验证，并用实验结果继续修订理论文档。
