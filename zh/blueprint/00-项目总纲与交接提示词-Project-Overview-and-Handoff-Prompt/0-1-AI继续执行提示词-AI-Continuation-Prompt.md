# AI 继续执行提示词 AI Continuation Prompt

> **状态提示（2026-06-04）：本文记录早期调研阶段，下一步描述已经过时。继续项目时，请使用 [Stage 0–6 全阶段执行总控提示词](./0-3-Stage0至Stage6全阶段执行总控提示词-All-Stage-Execution-Master-Prompt.md)。**

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


## 每个竞品最终必须回答的 DeepSeek V4 适配问题

在每个竞品的 `Lessons for DeepSeek Agent` 文档中，必须加入专门章节：

```text
如果该产品接入 DeepSeek V4 Flash / Pro：
1. 能发挥 DeepSeek V4 的哪些能力？
2. 为什么能发挥？
3. 发挥不了哪些能力？
4. 为什么发挥不了？
5. 要如何迭代才能更好适配？
6. 它自己有没有可能做这些迭代？为什么？
7. DeepSeek Agent 应该如何借鉴或避开？
```

必须覆盖：

```text
1M context
cache hit/miss pricing
Flash / Pro / Thinking / Max 路由
V4 encoding / DSML tool calling
reasoning_content 策略
checkpoint-driven review
cost/cache telemetry
local/cloud/endpoint 部署形态
```

## 交付方式

每完成一个阶段：

1. 更新根目录 `README.md` 的任务勾选状态；
2. 将新文档放入对应阶段文件夹；
3. 如有新证据，更新证据索引；
4. 不删除旧文档，不覆盖原始调研；
5. 必要时生成新的版本压缩包。


---

## v0.5 新增强制要求：Model-Harness Fit

后续所有竞品调研必须使用 `3-A-竞品调研升级方法论-Model-Harness-Fit-Framework.md`。

不要只写产品功能。必须逐条检查 DeepSeek V4 物理特性：

```text
1M context
CSA / HCA
sliding_window=128
cache hit/miss pricing
Flash / Pro / Thinking / Max
MoE / hash routing
mHC 多信号传播
V4 encoding / DSML
reasoning_content policy
FP4/FP8 serving economics
endpoint / local / cloud
checkpoint-driven review
```

每个竞品最终都要有 Model-Harness Fit Matrix。


---

## 源码深读硬性规则

所有竞品源码调研必须执行：

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

不要把 Docs/README 预研称为源码深读完成。
