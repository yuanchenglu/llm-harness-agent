# 研究方法与事实校准：如何阅读本项目

> 本文用于区分“事实、观察、推论、方案和实验结果”。它也是对早期文章中若干过度表述的公开修订记录。

## 1. 为什么需要事实校准

Agent 领域变化很快。README 会过期，默认分支会移动，模块存在不等于已经接入真实运行路径，产品宣传也不等于 benchmark 结果。论文式表达如果不标注证据边界，很容易把有启发的假设写成确定事实。

本项目今后采用以下等级：

```text
A0：固定 commit 的真实运行路径与测试共同证明
A1：固定 commit 的实现源码证明，但尚未确认运行效果
A2：官方 README / docs / config 中的产品声明
B：基于事实的工程推论或设计方案
C：非官方逆向或社区线索
N：在公开证据中未找到实现
```

## 2. 需要公开纠正的观点

### 2.1 “LLM 智商是常数，模型线性，Harness 指数”

这是用于强调系统工程价值的修辞，不是数学定律。模型能力、任务难度和 Harness 质量共同影响结果；Harness 既可能放大模型能力，也可能引入额外错误。

**修订后观点**：模型能力不是产品能力。Harness 决定模型能力能否稳定、安全、经济地到达用户。

### 2.2 “上下文越长，注意力必然越稀释”

长上下文确实会增加检索、布局和成本挑战，但不同模型架构、训练方法和任务对长度的敏感度不同，不能把“越长必然越差”当作普遍定律。

**修订后观点**：上下文窗口是容量上限，不是应该填满的目标；Harness 应维护活跃工作集并按需检索。

### 2.3 “CodeWhale 是 DeepSeek 官方项目”

这是错误表述。CodeWhale 是社区开源项目，围绕 DeepSeek 模型构建，但不能称为 DeepSeek 官方产品。

### 2.4 “CodeWhale 已完成完整 three-zone prefix contract”

源码确认：它已经把 system prompt + tool catalog 的 prefix drift check 接入 turn loop；但完整的 pinned prefix + append log + turn scratch 数据结构仍明确标注尚未接入 request path。

### 2.5 “Trae Agent 已开源 test-time scaling”

公开源码中可以确认 Agent loop、trajectory、Docker、MCP 和有状态 sequential thinking，但未找到 multi-candidate generation–pruning–selection orchestrator。论文或路线图思想不能写成开源实现事实。

### 2.6 “Reasoning content 永远不该回传”

错误。不同 provider 和模式有不同协议要求：有的 thinking block 必须随工具调用回传；有的 endpoint 可以丢弃；有的实现会在特定模式 replay。正确策略必须通过 provider contract 与实际 API 测试决定。

### 2.7 “如果 tools 没变，只发 delta”

多数聊天 API 每次请求仍要求完整 tools 字段；缓存可以降低重复前缀成本，但不等于协议支持只发送工具 delta。Progressive disclosure 是缩小工具面的方案，不是随意省略协议字段。

### 2.8 “Hermes 是唯一拥有 Memory / Skills / Cron 的平台”

这类绝对判断会快速过期，也混淆了“具备某功能”和“把功能组合成同一产品”的差异。

**修订后观点**：Hermes 的研究价值在于把 memory、skills、gateway、cron、tool registry 和长期运行组织在同一个 Agent OS 中；是否领先需要按固定版本与 benchmark 比较。

## 3. 如何从交接调研中整合内容

本项目已经吸收 `deepseek-agent-project-handoff` 的三类成果，但不会复制整个目录：

1. **模型事实**：用于约束 provider、context、cache 和 tool protocol 设计；
2. **竞品源码事实**：用于确认哪些机制真实存在、哪些只是文档或 scaffolding；
3. **产品综合判断**：用于形成 DeepSeek Agent 理论闭环和实验计划。

没有直接复制的原因是：交接目录服务于项目执行，包含阶段状态、历史版本和大量审计细节；本目录服务于独立发布和大众阅读，应保留稳定理论、关键证据和可验证问题。

## 4. 论文写作规范

每篇文章应尽量包含：

```text
问题定义
事实与观察
设计假设
方案
边界条件
验证方法
证据状态
```

建议使用以下措辞：

| 不推荐 | 推荐 |
|---|---|
| 已证明最优 | 在当前源码/样本中表现出优势，仍需 benchmark |
| 唯一实现 | 在本次固定版本调研中确认实现 |
| 必然 / 永远 | 在这些条件下预期 / 需要验证 |
| 源码验证完成 | 已定位关键实现；是否接入运行路径另行说明 |
| 生产级 | 已通过明确的生产指标与运行证据 |

## 5. 当前证据基线

截至 2026-06-04，已对以下项目做固定 commit 源码校准：Claude Code、Codex、Trae Agent、Reasonix、Hermes Agent、CodeWhale。核心结论包括：

- Claude Code 官方仓库不包含完整 engine；
- Codex 的 typed context、turn loop、compaction 等机制有官方源码支撑；
- Trae Agent 没有公开 test-time scaling orchestrator；
- Reasonix 多项 DeepSeek-native 机制有源码支撑，但收益需实验；
- Hermes 的 tool registry、progressive disclosure、trajectory compression 有源码支撑；
- CodeWhale 的 prefix drift check 已接入，完整 three-zone compiler 尚未接入。

## 6. 下一步验证

本项目下一轮只执行一项工作：建立 [DeepSeek API 协议与 Prefix Cache Benchmark Harness](BENCHMARK-HARNESS-PLAN-zh.md)。先验证 `reasoning_content`、工具调用协议、Prefix Cache 漂移、成本和延迟，再由实验结果决定是否以及何时进入路由、planner/executor、reviewer 或 progressive tool disclosure。

## 结论

严谨不等于晦涩。对普通读者最友好的做法，就是清楚说明：什么是我们看到的，什么是我们推出来的，什么是我们准备验证的。
