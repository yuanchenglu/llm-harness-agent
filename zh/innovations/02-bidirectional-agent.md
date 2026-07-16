# 大脑主动驱动小脑：让 LLM 不再是 Harness 的被动执行者

> **证据说明：** 本文提出的是 Harness 设计假设与验证路径。除非明确给出固定版本源码、运行路径和可复现实验，否则“验证”不等于已证明普遍最优。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-02
> **LLM + Harness = Agent** · 第 2 篇
> **系列**：[LLM + Harness = Agent](../../README.md)
> **上一篇**：[01 Agent 免疫系统](01-agent-immune-system.md)
> **下一篇**：[03 注意力预算管理](03-attention-budget.md)

---

> **摘要**：当前所有 Agent 架构共享同一个单向假设——LLM 只能被动响应 Harness 的调用，无法根据自身认知状态主动发起请求。本文指出该单向性的根因不在模型能力，而在 tool-calling API 协议本身的设计假设：LLM 被建模为无状态函数，而非对话中的对等参与者。提出的双向 Agent 架构引入 need_more_context、request_specialized_model、trigger_self_review、propose_skill 四个新原语，让 LLM 在推理过程中主动声明需求，将 Agent Loop 从「Harness 驱动 LLM」升级为「LLM ⇄ Harness 协同决策」。

---

## 1. 问题定义

### 1.1 现象

打开任何一个 Agent 产品的源码——无论 LangChain Agent、OpenAI Assistants、AutoGPT 还是 Claude Code——都会看到同一个架构模式：

```
用户输入 → Harness 接收 → 拆解任务 → 调用 LLM → LLM 返回 tool_call
→ Harness 执行工具 → 把结果喂回 LLM → 循环
```

LLM 从头到尾是被动的。它只在被调用时才「思考」。它能感知到「上一步的工具调用返回了空结果」，但它不会主动说：「等一下。在做下一步之前，我需要 X 信息。但我没有 X。帮我拿一下。」

这个架构模式不是某个产品的偶然选择——它是所有 Agent 框架的默认假设。

后果是系统性的：LLM 对自己能力的边界完全没有发言权。它知道自己不懂某个领域，但不会主动说「这个任务超出了我的能力范围，换一个专用模型」。它知道自己没见过某个关键文件，但不会主动说「给我这个文件，否则我的判断是基于猜测的」。它只能在 Harness 问它的时候回答，不能在自己需要的时候开口。

就像一个人坐在副驾驶位上——他能看到路、能给出建议，但手里没有方向盘。踩刹车也好、转弯也好，都得等驾驶员（Harness）先操作了，他才能反应。

### 1.2 根因

根因不在模型能力，在 tool-calling API 协议的设计假设。

当前所有主流 LLM API（OpenAI function calling、Anthropic tool use、Google Gemini function calling）共享同一个协议模式：请求-响应。客户端（Harness）发送一个包含 messages 和 tools 的请求，服务端（LLM）返回一个包含 text 和 tool_calls 的响应。一次请求，一次响应。LLM 不能在一次请求的响应之外「主动」做什么。

这个协议的底层假设是：**LLM 是一个无状态函数**——给定输入，产生输出。函数不会「主动」调用调用方。函数的控制流永远是调用方→函数→返回。

当 LLM 被嵌入 Agent Loop 时，这个假设被原封不动地继承了。Agent Loop 把 LLM 当作推理引擎调用，LLM 返回推理结果。Harness 永远是调用方，LLM 永远是被调用方。

**为什么「给 LLM 更多工具」不能解决这个问题**：工具是 Harness 预设的「允许 LLM 调用的能力清单」。但 LLM 的真实需求往往不在这个清单里——它需要的不是一个具体的工具，而是一种「我需要更多上下文才能做判断」的元表达能力。工具扩展的是 Harness 预设的能力范围，不是 LLM 的主动权。

### 1.3 形式化

定义标准 Agent Loop 的交互模式：

设对话状态为 S(t)，Harness 的推理函数为 H，LLM 的推理函数为 L。标准 Agent Loop 在时刻 t 的交互为：

```
L: S(t) → (response_t, tool_calls_t)
H: (response_t, tool_calls_t) → S(t+1)
```

关键约束：L 的定义域不包括「主动修改 H 的行为」的能力。L 只能在其输出空间中产生响应和工具调用——不能产生「在下一步之前，强制 H 执行某个操作」的指令。H 的转换函数是封闭的——它在调用 L 之前就已经确定了所有可执行的操作路径。

双向 Agent Loop 需要打破这个约束，引入反向通道：

```
L: S(t) → (response_t, tool_calls_t, meta_directives_t)
H: (response_t, tool_calls_t, meta_directives_t) → S(t+1)
```

其中 meta_directives 是 LLM 主动发出的、对 Harness 行为有约束力的元指令。这是 LLM 从「被调用方」升级为「对等参与者」的形式化条件。

---

## 2. 现有方案与局限

| 方案 | 核心思路 | 为什么不解决双向性问题 |
|------|---------|----------------------|
| **标准 Tool Calling** | LLM 在响应中声明 tool_call，Harness 执行后返回结果 | LLM 只能调用 Harness 预注册的工具。无法表达「我需要这个工具，但它不在列表里」——这种元级别的需求没有对应的 tool_call 协议 |
| **ReAct 模式** | LLM 交替输出 Thought 和 Action | Thought 是给开发者看的调试信息，Harness 不解析、不响应。LLM 的「思考」不会改变 Harness 的行为 |
| **Planning Agent** | Harness 在调用 LLM 之前预拆任务为步骤列表 | Planning 是 Harness 的单方面决策。如果计划有误，LLM 没有能力纠正——因为 LLM 收到的输入里已经没有「计划本身」了 |
| **Reflection Agent** | LLM 生成输出后，再次调用 LLM 审查输出 | 反思仍然是 Harness 发起的第二遍调用。LLM 不能在第一次推理过程中主动说「我需要反思」——反思时机由 Harness 预设 |
| **Multi-Agent 编排** | 多个 Agent 并行/串行协作 | 主 Agent（编排者）仍然是 Harness 层的逻辑。子 Agent 之间没有对等的主动通信——通信路径是 Harness 预设的 |
| **Hermes delegate_task** | 主 Agent 将子任务分派给专门子 Agent | 分派决策由 Harness 触发（基于任务类型匹配），不是 LLM 主动请求。LLM 感知到「这个子任务我不擅长」时，没有途径表达 |

**共性缺陷**：所有方案都在 Agent Loop 的外围增加功能——更多工具、更多反思轮次、更多 Agent 角色。但没有一个方案修改 Agent Loop 的核心协议：LLM 只能是响应方，不能是发起方。问题不在 Agent 的外围能力，在 Agent 的通信拓扑。

---

## 3. 方案设计

### 3.1 核心机制：LLM ⇄ Harness 双向流

本方案在标准 Agent Loop 中引入四个新原语。这些原语不是「更多工具」——它们是 LLM 向 Harness 主动声明认知状态和需求的元指令。

**原语一：need_more_context**

LLM 在推理过程中发现关键信息缺失，主动向 Harness 声明需求。

```
LLM → Harness: need_more_context(
  target: "config/deploy.yaml",
  reason: "需要确认部署环境才能选择正确的构建命令，
           当前上下文只有代码文件，没有部署配置"
)
```

与 tool_call 的本质区别：tool_call 调用的是 Harness 预先注册的具体工具（如 `read_file`）；need_more_context 声明的是认知需求——LLM 不预设「哪个工具能满足这个需求」，Harness 负责解释并执行。如果 `config/deploy.yaml` 不存在，Harness 可以尝试搜索、询问用户、或告知 LLM 文件缺失——而不是直接返回错误。

**原语二：request_specialized_model**

LLM 识别到当前任务超出自身能力边界，主动请求模型切换。

```
LLM → Harness: request_specialized_model(
  task: "审查此 PR 中 Python 代码的安全性",
  reason: "我是通用推理模型，不具备安全漏洞的领域知识。
          建议切换到安全审查专用模型"
)
```

当前所有 Agent 的模型路由由 Harness 预设规则决定（「代码任务用模型 A，文本任务用模型 B」）。但最优路由往往取决于任务的具体内容——只有 LLM 在推理过程中才能感知到「这个任务里有一个安全审查子任务」，而 Harness 的预设规则无法捕捉这种细粒度判断。

**原语三：trigger_self_review**

LLM 在输出关键决策前，主动要求对自己的推理进行独立审查。

```
LLM → Harness: trigger_self_review(
  target: "即将执行的数据库迁移计划",
  reason: "迁移涉及生产数据库，影响范围大。
          建议用独立 Agent 审查迁移计划后再执行"
)
```

这与 Reflection Agent 的区别：Reflection 是 Harness 在 LLM 输出完成后发起的第二轮调用——Harness 预设了「重要决策要反思」的规则。trigger_self_review 是 LLM 在输出过程中主动判断「这个决策需要审查」——判断依据是任务内容的风险级别，而不是 Harness 的预设规则表。

**原语四：propose_skill**

LLM 在完成任务后发现可复用的模式，主动提议固化为 Skill。

```
LLM → Harness: propose_skill(
  name: "pre-commit-typecheck",
  trigger: "git commit 前",
  steps: ["运行 tsc --noEmit", "检查类型错误数", "非零则拦截提交"],
  reason: "此项目的 TypeScript 类型检查是每次提交都需要的。
          固化为 Skill 后无需每轮重复推理"
)
```

这与 Hermes 现有 Skill 机制的区别：当前 Skill 由 Harness 在任务成功后触发保存。propose_skill 让 LLM 在推理过程中主动识别可复用模式——不需要等 Harness 的「任务成功」信号。

### 3.2 关键设计决策

**为什么是四个原语而不是一个通用「request」？**

四个原语覆盖了 LLM 主动性的四个正交维度：
- need_more_context → 「我缺什么」
- request_specialized_model → 「我不擅长什么」
- trigger_self_review → 「我不确定什么」
- propose_skill → 「我学到了什么」

这四个维度穷举了 LLM 在推理过程中可能产生的元认知需求。一个通用「request」原语会把所有需求混在一起，增加 Harness 的解释负担和误判风险。精确的原语让 Harness 的响应逻辑是确定的——不需要「理解 LLM 在请求什么」，只需要「根据原语类型执行对应的处理流程」。

**为什么不直接让 LLM 控制 Agent Loop？**

完全把控制权交给 LLM（让 LLM 自己决定下一步做什么、调用什么工具、什么时候结束）看似是双向流的极致，但引入了新的风险：LLM 的推理成本已经在 O(n²) 的注意力上很高，再加上控制流的决策负担，会让 Agent Loop 变得不稳定。本方案的选择是：**Harness 保持对 Agent Loop 的控制权，但 LLM 获得了对 Harness 行为的建议权**。Harness 必须响应 need_more_context（因为没有上下文就无法继续推理），但可以拒绝 propose_skill（如果 Skill 注册表已满或格式不合法）。

---

## 4. 分析

### 4.1 为什么这个方案能解决根本问题

根本问题不是「LLM 不够聪明」，是「Agent 的通信拓扑是单向的」。单向拓扑决定了 LLM 只能在被问的时候回答——它无法在需要的时候开口。

双向流把通信拓扑从 `Harness → LLM` 升级为 `Harness ⇄ LLM`。这不是给 LLM 更多工具、更多上下文、更强的推理能力——而是改变了 LLM 在系统中的角色：从被调用方升级为对等参与者。

具体来说，四个原语分别解决了四个单点失效：

- **信息缺失**：单向架构下，LLM 只能基于已有上下文推理，缺失信息导致错误输出。need_more_context 让 LLM 可以在推理中断前主动补充上下文。
- **能力边界**：单向架构下，LLM 对所有任务「硬着头皮上」，因为它的工具清单里没有「拒绝任务」的选项。request_specialized_model 给了 LLM 一个「安全出口」。
- **风险决策**：单向架构下，LLM 无法区分「普通决策」和「高风险决策」——它只有一种输出模式。trigger_self_review 让 LLM 可以标记风险，引入额外的安全校验层。
- **经验积累**：单向架构下，LLM 每次都是从头推理。propose_skill 让 LLM 可以把推理结果固化为可复用的执行单元。

### 4.2 边界条件

以下场景双向流**不应**被触发：

- **简单确定性任务**：任务步骤完全确定、不需要额外上下文、不涉及风险决策（如「把 README 里的版本号从 1.0 改成 1.1」）。此时双向原语只会增加无意义的往返通信。
- **Harness 预设规则已覆盖**：如果 Harness 已经通过静态规则处理了模型路由（如「代码审查一律用安全模型」），request_specialized_model 是冗余的。
- **LLM 主动性的误用风险**：恶意 Prompt 可能利用 need_more_context 诱导 Harness 读取敏感文件。Harness 需要对 LLM 的元指令做权限校验——不是所有 need_more_context 请求都应该被满足。

**设计原则**：双向性赋予 LLM 的是「建议权」而非「控制权」。Harness 始终是最终决策者——它可以接受 LLM 的建议（need_more_context），也可以拒绝（propose_skill 格式不合法），也可以有条件地执行（request_specialized_model 在模型池中找不到匹配时降级为通用模型）。

### 4.3 与最接近方案的对比

| 维度 | Hermes delegate_task | Anthropic Joint RL | 本方案 |
|------|:---:|:---:|:---:|
| **谁决定分派/切换** | Harness（基于任务类型匹配） | 训练过程中联合优化 | LLM 主动声明需求 |
| **执行时机** | 任务开始前的静态分派 | 训练阶段，非运行时 | 任务执行中的动态请求 |
| **LLM 是否有主动权** | 否 | 训练时有，推理时无 | 推理时实时有 |
| **是否需要训练** | 否 | 是（联合 RL 需要训练） | 否（协议层面的改动） |
| **与现有框架兼容性** | 已兼容 | 需要自定义训练管线 | 需要 API 协议扩展 |

Anthropic 的 Joint RL 可能是当前最接近双向流理念的工作。Joint RL 用同一个反馈信号同时优化模型和 Harness——这要求两者之间有双向的信息流动。如果 LLM 永远是单向被动的，Joint RL 在原理上就无法实现：Harness 无法从 LLM 的推理过程中获得信号来优化自身。

但 Joint RL 发生在训练阶段。本方案的双向流发生在推理阶段——不需要重新训练模型，只需要扩展 tool-calling API 协议，让 LLM 的输出空间包含元指令。

---

## 5. 验证路径

### 5.1 已验证

- **问题存在性**：我验证了 Hermes OMO v0.3 的 Agent Loop 源码。Harness → LLM 的调用路径在 `plan-execute.ts` 中是完全单向的——LLM 的响应被解析为 tool_calls 后直接进入 Harness 的执行队列，LLM 没有途径插入元指令。这不是 Hermes 的设计缺陷——所有主流 Agent 框架（LangChain、AutoGPT、CrewAI）都采用相同的单向模式。
- **协议限制**：我验证了 OpenAI、Anthropic、Google 的 tool-calling API 规范。三者都采用请求-响应模式，不支持 LLM 在响应之外主动向客户端发起请求。双向流需要在 API 协议层面扩展。

### 5.2 待验证

- **原语触发准确率**：need_more_context 在 100 个任务上的触发是否精准——触发时机是否合理（不提前、不滞后），触发理由是否可信（不是「随便要个文件试试」）。
- **Harness 响应延迟**：引入双向原语后，Agent Loop 的平均迭代次数变化。need_more_context 会增加一轮往返通信——这个开销需要与它避免的错误成本做权衡。
- **与 Hermes 现有架构的集成难度**：四个原语中，propose_skill 与 Hermes 现有 Skill 机制的重合度最高，集成难度最低。need_more_context 和 request_specialized_model 需要修改 Agent Loop 核心——集成难度最高。trigger_self_review 可以通过 spawn 独立 Agent 实现，不需要修改核心 Loop。
- **Anthropic 前沿追踪**：如果 Anthropic 在 Opus + Claude Code 上的 Joint RL 公开了技术细节，需要重新评估双向流的实现路径——可能存在更优的联合训练方案。

---

## 6. 与 Hermes 的关系

Hermes 的 delegate_task 机制在正确的方向上迈出了半步——它承认「有些任务不应该由当前 Agent 执行」。但 delegate_task 的触发权在 Harness，不在 LLM。

补齐另外半步需要让 delegate_task 接受 LLM 的主动请求。具体路径：

1. **最轻量**：在现有 tool_call 列表中增加 `delegate_task` 工具。LLM 可以像调用任何工具一样调用它。但这不是真正的双向流——它只是多给了一个工具，LLM 仍然只能在 Harness 问它的时候调用工具。
2. **中等改动**：在 Agent Loop 中增加一个「元指令通道」——LLM 的响应除了 tool_calls，还包含 meta_directives。Harness 必须先处理 meta_directives，再处理 tool_calls。这是本文方案的核心——需要修改 Agent Loop 的解析逻辑。
3. **深度集成**：将四个原语作为 Hermes 的协议层扩展——所有 Hermes Agent 默认支持双向流。这需要修改 Hermes 的 Agent Loop 核心，但一旦实现，所有上层功能（Skill、Delegate、Planning）都会自动获得双向性。

推荐路径：先实现路径 2（中等改动），在 Hermes 的一个实验分支上验证双向流的实际效果。如果验证通过，再推进路径 3 的深度集成。

---

## 结论

Agent 的进化方向不是「更聪明的模型」——是「更对等的模型-Harness 关系」。单向架构假设 LLM 是无状态推理引擎，这个假设在产品化的 Agent 中是错误的——LLM 在长对话中积累了大量认知状态，它有能力、也应该有权利表达自己的需求和边界。

知是行之始，行是知之成。LLM 先声明自己的认知状态（知），Harness 再据此行动（行）——两者形成闭环，而非单向指令链。

---

*上一篇：[01 Agent 免疫系统](01-agent-immune-system.md) — 免疫系统解决「做错了怎么自己修」（事后纠偏）。大脑驱动小脑解决「怎么在出错之前就意识到自己需要帮助」（事前预防）。两者合在一起，覆盖 Agent 可靠性的两个核心维度：做错了能修，看不清能问。*
