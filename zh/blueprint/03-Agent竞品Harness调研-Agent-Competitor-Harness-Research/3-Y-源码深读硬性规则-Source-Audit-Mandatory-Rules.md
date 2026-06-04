# 3-Y 源码深读硬性规则 Source Audit Mandatory Rules

> 版本：v0.8  
> 目的：把用户要求的 8 步源码审计流程写入项目规则。后续任何 AI / 人继续本项目时，都必须按这个规则执行，不能把 Docs/README 预研伪装成源码深读。

---

## 1. 硬性流程

每个 Agent / AGI / Coding Agent 产品的源码调研，都必须完成以下 8 步：

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

---

## 2. 每一步的验收标准

### 1. 仓库结构扫描

必须回答：官方仓库是否存在；是否包含完整核心 engine；还是只包含插件 / examples / docs / SDK；核心代码语言是什么；哪些目录必须读；哪些目录可暂缓。

### 2. 关键模块清单

必须列出：Agent Loop、Model Client / Provider、Context Builder、Tool Runtime、Permission / Sandbox、Memory / Skill / Subagent、Session / Checkpoint、Trajectory / Trace、Config、UI / App Server。没有的模块要明确写“未发现”。

### 3. 逐文件阅读

必须写明已读文件路径、阅读范围、文件职责、关键类 / 函数、是否与模型物理特性适配相关。

### 4. 函数 / 类 / 配置摘录

必须摘录类名、函数名、配置项、调用链、核心字段、关键判断逻辑。不能只写“支持 XXX”。

### 5. 证据链接整理

每个核心论点旁边必须有官方源码链接 / 官方 Docs 链接 / 官方配置链接。若是非官方代码，只能标注为 C 级线索。

### 6. Model-Harness Fit Matrix

必须逐条检查：1M context、CSA/HCA、sliding_window=128、cache hit/miss pricing、Flash/Pro/Thinking/Max、MoE/hash routing、mHC 多信号传播、V4 encoding/DSML、reasoning_content policy、FP4/FP8 serving economics、endpoint/local/cloud、checkpoint-driven review。

### 7. 对 DeepSeek Agent 的迁移判断

每个模块必须判断：可直接复用、可借鉴设计、需要 DeepSeek V4-native 重写、不可用、证据不足。

### 8. 产出源码审计报告

报告必须包含：源码边界、仓库结构、关键模块、逐文件摘录、Model-Harness Fit Matrix、迁移判断、未完成项、下一步阅读清单。

---

## 3. 禁止事项

```text
禁止只读 Docs 就说“源码深读完成”
禁止只读 README 就产出最终架构判断
禁止把非官方泄露源码当官方事实
禁止在没有代码证据时写“代码中实现了”
禁止为了速度牺牲证据链
```

---

## 4. 状态命名规范

| 状态 | 含义 |
|---|---|
| 第一轮预研完成 | 官方 Docs / README / 产品页 / 少量源码线索 |
| 源码边界确认完成 | 确认官方仓库公开了什么、没公开什么 |
| 源码深读 Pass 1 完成 | 已阅读核心模块若干文件，但未全量 |
| 源码深读完成 | 核心模块逐文件审计完毕，有证据矩阵 |
| 架构可迁移性评估完成 | 能明确哪些可 fork / 借鉴 / 重写 |

---

## 5. 当前三项状态

```text
Claude Code：源码边界确认完成；官方完整 engine 源码未公开；插件源码可审计；核心 engine 只能用官方 Docs + 非官方线索
Codex：源码深读 Pass 1 完成；已读 README / AGENTS / config.schema；仍需继续读 core / context / model / tools / sandbox
Trae Agent：源码深读 Pass 1 完成；已读 BaseAgent / TraeAgent / TrajectoryRecorder / tools docs；仍需继续读 provider / tools implementations / Docker / MCP
```
