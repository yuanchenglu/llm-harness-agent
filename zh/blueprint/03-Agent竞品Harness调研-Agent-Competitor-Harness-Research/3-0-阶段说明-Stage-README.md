# 3-0 Agent 竞品 Harness 调研 Agent Competitor Harness Research

当前阶段：进行中。核心竞品已经完成多轮源码审计；新增五个 Agent 产品 / 插件已完成源码审计 Pass 1 与综合借鉴评估。

第一优先级已覆盖：

```text
Claude Code
OpenAI Codex
Trae / Trae SOLO
DeepSeek Reasonix
Hermes Agent
CodeWhale / DeepSeek-TUI
```

新增重点对象：

```text
OpenCode                 Agent Runtime 与多端产品骨架
Oh My OpenAgent          Harness 增强、并行编排与工具可靠性
Oh My ClaudeCode         Teams-first 编排状态机与可观测性
OpenSpec                 Spec / Artifact 驱动开发协议
Superpowers              可组合的软件工程技能方法论
```

下一步：按源码深读硬性规则执行新增五项目 Pass 2，重点审计核心 loop、hooks、team state、artifact schema、skills tests，并用统一 prototype benchmark 验证对 DeepSeek Agent 的真实收益。


## 2026-06-04 事实校准状态

Claude Code、Codex、Trae Agent、Reasonix、Hermes Agent、CodeWhale 的历史报告已经使用官方仓库固定 commit 重新复核。后续引用应优先阅读 `17-0` 至 `17-3`，并区分源码事实、运行路径、产品声明与工程推论。下一步优先执行协议和 benchmark 验证，而不是继续扩写未经验证的架构判断。
