# X Thread: LLM + Harness = Agent 论文草稿发布

## 中文版（主发）

**推文 1（钩子）**
等下一个更好的模型？等不来的。
Transformer 的注意力稀释是物理硬约束——1M Context Window 只是把"忘记"从第 15 轮推迟到第 50 轮。
真正的突破口不在模型，在 Harness。
写了篇论文草稿，把 5000 小时+5 台机器+12 个设计模式串成一个框架：
🔗 github.com/yuanchenglu/llm-harness-agent

**推文 2（核心论点）**
同一个 DeepSeek V4，在不同 Harness 上表现天差地别。
ClaudeCode 上跑 30 轮不丢逻辑，OpenCode 上 15 轮开始重复造轮子。
模型没变——变的是 Harness 的上下文调度策略。
一句话：模型是 CPU，Harness 是操作系统。

**推文 3（四层架构）**
Agent OS 需要四层：
• Memory 层：跨 session 记住你是谁
• Skills 层：经验自动固化，下次不重复踩坑
• Scheduling 层：Cron 定时 + Kanban 分解 + 子 Agent 编排
• Gateway 层：飞书/微信/Discord 统一入口
缺任何一层，都只是个聊天机器人。

**推文 4（上下文管理）**
Agent 跑到第 15 轮开始"变傻"——不是模型不行，是注意力被稀释了。
解决方案不是"让模型记住更多"，是"减少模型需要记住的东西"。
把不可丢失的约束放在 KV Cache 前缀区（永不压缩），把执行日志放在可压缩区。压缩发生，硬约束毫发无损。

**推文 5（自进化）**
Agent 最有价值的能力不是一次性完成任务——是自己变强。
完成复杂任务后，自动提议保存为 Skill。下次触发：零推理 Token。
检测到 Prompt 约束被违反，自动固化为 Skill。下次：不依赖模型记忆。
正向+负向=完整进化闭环。每个 Skill 的诞生=永久 0 Token。

**推文 6（5 机 Agent 矩阵）**
不是纸上架构——是真的在跑：
• 机器 1：Hermes 做 CEO
• 机器 2/3/4：OpenCode/ClaudeCode/CodeX 三个研发组
• 机器 5：OpenClaw 市场运营
飞书上发一条需求 → 分解 → 分配 → 执行 → 推送结果。全程没开终端。

**推文 7（设计原则）**
12 个设计模式→4 条通用原则：
1. 分离不可压缩与可压缩
2. Agent 必须是主动的，不是被动的
3. 记忆粒度要与任务类型匹配
4. 自进化是终局，不是加分项
不限于 Hermes——任何 Agent 系统都适用。

**推文 8（收尾）**
DeepSeek 把引擎造好了。现在轮到我们把底盘造好。
模型改进是线性的（3-6 个月一版，百万美元成本）。
Harness 改进是指数的（今天发现，今晚改配置，明天生效）。
论文草稿里我把这个论点和 12 个设计模式讲透了。欢迎 challenge：
🔗 github.com/yuanchenglu/llm-harness-agent

---

## English Version

**Tweet 1 (Hook)**
"Wait for the next model" is a dead end.
Transformer attention dilution is physics — 1M context window just delays the forgetting from round 15 to round 50.
The real breakthrough isn't the model. It's the harness.
I wrote a draft paper: 5,000+ hrs, 5 machines, 12 design patterns, one framework.
🔗 github.com/yuanchenglu/llm-harness-agent

**Tweet 2 (Core thesis)**
Same DeepSeek V4. Radically different performance across harnesses.
ClaudeCode: 30 rounds, no logic loss. OpenCode: round 15, starts reinventing the wheel.
Model didn't change. The harness's context scheduling did.
Model = CPU. Harness = operating system.

**Tweet 3 (Four layers)**
Agent OS needs four layers:
• Memory: persistent cross-session state
• Skills: auto-crystallize success patterns
• Scheduling: Cron + Kanban + sub-agent orchestration
• Gateway: Feishu/Discord/WeChat unified entry
Miss any layer, and it's just a chatbot.

**Tweet 4 (Context management)**
Agent "getting dumb" around round 15? Not the model. Attention dilution.
Solution isn't "make it remember more." It's "reduce what it needs to remember."
Hard constraints → KV Cache prefix (never compressed). Execution logs → compressible zone.
Compression fires, constraints survive untouched.

**Tweet 5 (Self-evolution)**
Most underrated agent capability: getting better on its own.
Complex task done → auto-propose Skill save. Next trigger: zero inference tokens.
Constraint violation detected → auto-crystallize as Skill. Next time: doesn't rely on model memory.
Positive + negative = full evolution loop. Every Skill born = permanently zero tokens.

**Tweet 6 (5-machine matrix)**
Not a paper architecture. It's running:
Machine 1: Hermes as CEO
Machines 2/3/4: OpenCode/ClaudeCode/CodeX R&D squads
Machine 5: OpenClaw marketing ops
Drop a request in Feishu → decompose → assign → execute → push results. Zero terminal.

**Tweet 7 (Design principles)**
12 patterns → 4 universal principles:
1. Separate non-compressible from compressible
2. Agent must be active, not passive
3. Memory granularity must match task type
4. Self-evolution is the endgame, not a bonus
Applies to any agent system, not just Hermes.

**Tweet 8 (Closing)**
DeepSeek built the engine. Now it's time to build the chassis.
Model improvements: linear (3-6 months, millions in training).
Harness improvements: exponential (discover today, config tonight, live tomorrow).
Full argument + 12 patterns in the draft paper. Challenge me:
🔗 github.com/yuanchenglu/llm-harness-agent
