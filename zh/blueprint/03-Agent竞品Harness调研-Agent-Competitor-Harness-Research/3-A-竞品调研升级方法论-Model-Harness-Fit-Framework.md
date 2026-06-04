# 3-A 竞品调研升级方法论 Model-Harness Fit Analysis Framework

> 版本：v0.5  
> 修订原因：此前 Claude Code / Codex 调研偏产品功能和 Harness 模块，没有充分追问“Agent 产品如何与大模型物理特性配合”。从本文件开始，Stage 2 的每个竞品调研都必须升级为 **模型物理特性 × Harness 适配机制** 调研。

---

## 1. 核心纠偏

旧调研问题：

```text
这个 Agent 产品有哪些功能？
它的 Harness 模块是什么？
对 DeepSeek Agent 有什么启发？
```

新调研问题：

```text
这个 Agent 产品如何把某个模型的物理特性转化为 Agent 能力？
它针对自家模型做了哪些适配？
这些适配在源码 / Docs / 配置 / UI / runtime 中如何体现？
如果接入 DeepSeek V4，它能发挥哪些物理特性？发挥不了哪些？为什么？
DeepSeek Agent 应该如何专门补齐？
```

---

## 2. DeepSeek V4 物理特性作为检查表

每个竞品都要逐条检查下列 V4 物理特性是否被利用：

| 编号 | DeepSeek V4 物理特性 | 竞品调研必须回答 |
|---|---|---|
| V4-P1 | 1M context | 竞品是否有长上下文布局、压缩、索引、分区、active working set？ |
| V4-P2 | CSA / HCA / sparse top-k retrieval | 竞品是否理解“长上下文不是平铺黑板”？是否有 anchor / checkpoint / summary 机制？ |
| V4-P3 | sliding_window=128 | 竞品是否把当前目标、工具结果、约束靠近 turn tail？还是只堆 history？ |
| V4-P4 | DeepSeek cache hit/miss pricing | 竞品是否有 byte-stable prefix、stable tool schema、cache hit telemetry、prefix drift 检测？ |
| V4-P5 | Flash / Pro / Thinking / Max | 竞品是否有模型路由、reasoning budget 路由、失败升级、最终审查升级？ |
| V4-P6 | MoE / hash routing | 竞品是否有稳定标签、固定任务结构、prompt protocol，而不是随意自然语言？ |
| V4-P7 | mHC 多信号传播 | 竞品是否有 goal / constraint / evidence / execution / review 多信号分层？ |
| V4-P8 | V4 encoding / DSML tool calling | 竞品是否能使用 DeepSeek V4 原生 message compiler？还是只能走 generic adapter？ |
| V4-P9 | reasoning_content policy | 竞品是否区分 reasoning 的 display / archive / summarize / prompt？ |
| V4-P10 | FP4/FP8 serving economics | 竞品是否能根据 serving cost、prefill/decode、cache hit/miss 做 UI 和路由？ |
| V4-P11 | endpoint / local / cloud | 竞品的部署形态是否适合 DeepSeek official API / private endpoint / local runtime？ |
| V4-P12 | checkpoint-driven review | 竞品是否支持 checkpoint、rewind、review、proof、test logs？是否能做 Pro review？ |

DeepSeek V4 物理特性证据来源：`02-DeepSeek-V4源码调研-DeepSeek-V4-Source-Research/extracted-v1.1/2-证据增强终稿-Evidence-Enhanced-Final-Drafts/1-10-物理特性总清单与Harness启示-Physical-Traits-and-Harness-Implications.md` 与 `02-DeepSeek-V4源码调研-DeepSeek-V4-Source-Research/extracted-v1.1/2-证据增强终稿-Evidence-Enhanced-Final-Drafts/1-11-证据索引-Evidence-Index.md`。

---

## 3. 每个竞品最终必须产出两张矩阵

### 3.1 Model-Harness Fit Matrix

```text
竞品 Harness 能力 × DeepSeek V4 物理特性
```

评分：

```text
A：已深度适配，可直接发挥
B：部分适配，需要轻改
C：只能通用支持，无法发挥核心优势
D：冲突或缺失
?：证据不足
```

### 3.2 Native Model Optimization Matrix

```text
该竞品对自家模型做了什么专属优化？
这些优化在源码 / Docs / UI / runtime / config 里怎么体现？
能不能迁移到 DeepSeek V4？
```

---

## 4. 证据要求

每个判断必须标注：

```text
证据等级：S0 官方源码 / S1 官方 Docs / A 官方博客论文 / B 第三方 / C 推论
证据链接：源代码或文档链接
是否可作为架构依据：是 / 否 / 仅作线索
```

如果没有证据，只能写：

```text
当前未发现官方证据。
```

不能脑补。

---

## 5. 每个竞品的最终 Lessons 文档必须新增章节

```text
X. Model-Harness Fit：该产品如何配合大模型物理特性？
X.1 它对自家模型做了哪些专属优化？
X.2 如果接 DeepSeek V4，能发挥什么？
X.3 如果接 DeepSeek V4，发挥不了什么？
X.4 这些缺口是否能迭代补齐？
X.5 该产品自己会不会补齐？为什么？
X.6 DeepSeek Agent 必须怎么做？
```

---

## 6. 对前两份调研的修订要求

Claude Code 和 Codex 的 v0.4 调研文件保留，但标记为：

```text
第一轮：产品功能 / Harness 模块级调研
```

v0.5 新增：

```text
3-B-Claude-Code模型适配深度复盘-Claude-Code-Model-Fit-Deep-Dive.md
4-B-Codex模型适配深度复盘-Codex-Model-Fit-Deep-Dive.md
```

后续 Trae、Reasonix、Hermes、CodeWhale 直接按 v0.5 标准调研，不再走浅层版本。
