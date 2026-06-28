# OKR 增强型 PlanStep + 级联修正引擎

> **证据说明：** 本文提出的是 Harness 设计假设与验证路径。除非明确给出固定版本源码、运行路径和可复现实验，否则“验证”不等于已证明普遍最优。请先阅读 [研究方法与事实校准](../theory/research-method.md)。

> **创新点索引**：I-01, I-03
> **LLM + Harness = Agent** · 第 6 篇
> **系列**：[LLM + Harness = Agent](../../README.md)
> **上一篇**：[05 文档 KV Cache 优化结构](05-document-kv-cache.md)
> **下一篇**：[07 审查切换引擎](07-review-switching.md)

---

> **摘要**：当前所有 Agent 框架的 Plan 模块共享同一个缺陷——PlanStep 是扁平的 `text + status` 清单，步骤之间没有依赖语义。改第 3 步的需求，第 4-7 步不会自动感知到变更——导致产出物的前后矛盾和重复返工。本文提出 OKR 增强型 PlanStep：为每个步骤引入 `key`（可验证的结果指标）、`step_id`（唯一标识）、`parent_id`（父子层级）、`dependency_ids`（跨分支依赖）、`association_strength`（关联强度）五个新字段，将 Plan 从线性 Checklist 升级为有向依赖图。在此基础上构建级联修正引擎：当任意节点被修改时，遍历子图和依赖节点→标记 `pending_review`→触发逐节点重新审查→向上传导到根节点。这不是「重新执行整个 Plan」——是仅重审受影响的最小依赖子图。

---

## 1. 问题定义

### 1.1 现象

你给 Agent 一个任务：「为用户的注册功能写一套 REST API」。Agent 生成一个 7 步 Plan：

```
Step 1: 设计数据库 Schema        [completed]
Step 2: 实现 POST /register       [completed]
Step 3: 实现邮箱验证逻辑           [in_progress]
Step 4: 编写单元测试               [pending]
Step 5: 编写集成测试               [pending]
Step 6: 实现 JWT 鉴权              [pending]
Step 7: 写 API 文档                [pending]
```

执行到第 3 步时，你发现需求理解有偏差——不是「邮箱验证」，应该是「手机号验证」。Agent 把 Step 3 的 text 改了。但 Step 4、5、7 的原有描述仍然写的是「邮箱验证的单元测试」「邮箱验证的集成测试」「邮箱验证的文档」。

Agent 不知道这些步骤之间存在依赖关系。它只知道 Step 3 变了——Step 4-7 不知道、不关心、不更新。

你只能手动逐个检查每个步骤是否受到变更影响——而这恰好是你用 Agent 想要避免的事情。

### 1.2 根因

根因不在 Agent 的模型能力，在 PlanStep 的数据结构。

当前所有主流 Agent 框架的 PlanStep 结构是同一个模式的变体：

```typescript
// OMO (oh-my-claudecode) — PlanProgress
interface PlanProgress {
  total: number;
  completed: number;
  isComplete: boolean;
}

// ACP 协议标准 — PlanEntry
type PlanEntry = {
  content: string;    // 步骤描述
  priority: string;   // 优先级（high/medium/low）
  status: string;     // 状态（pending/in_progress/completed）
}

// CodeWhale — PlanStep (Rust)
struct PlanStep {
  text: String,
  status: StepStatus,
  started_at: Option<Instant>,
  completed_at: Option<Instant>,
}
```

三种结构共享同一个假设：PlanStep 彼此独立——没有父子关系，没有前后依赖，没有关联强度。Plan 本质上是一个扁平的 Checklist，而不是一个有向依赖图（DAG）。

**这个假设从何而来？** 从「Agent 的 Plan 只是给人看的执行进度展示」的产品定位而来。CodeWhale 的 `update_plan` tool description 写得很直白：*"Update optional high-level strategy metadata for complex initiatives. Use checklist_write for primary work progress."* —— Plan 是用来「展示」的，不是用来「驱动」的。

在「展示」定位下，扁平结构足够。在「驱动」定位下——Agent 根据自己的 Plan 自动执行步骤、审查产出、决策下一步——扁平结构完全不够。但今天的 Agent 正在从前一种定位走向后一种定位。数据结构没跟上。

### 1.3 形式化

设 Plan 包含 n 个步骤 P = {p₁, p₂, ..., pₙ}。当前所有框架将 P 建模为无关联的向量：

```
∀ i, j ∈ [1, n]: relation(pᵢ, pⱼ) = ∅（框架的角度）
```

现实中的任务执行存在显式和隐式依赖：

```
实际依赖图 G = (V, E), V = P
E = {(pᵢ, pⱼ) | pⱼ 的产出直接依赖 pᵢ 的结果}
```

当用户修改 pₖ，受影响集合为 Aₖ = {pₓ ∈ V | 存在从 pₖ 到 pₓ 的路径（包括子孙节点）+ 存在跨分支语义耦合的节点}。在扁平模型中，Aₖ **对 Agent 完全不可见**——Agent 不知道哪些步骤受到了影响，因此也无法修正。在依赖图模型中，Aₖ 可以通过图的传递闭包精确计算，级联修正变的可自动化。

---

## 2. 现有方案与局限

| 方案 | 核心思路 | 为什么不行 |
|------|---------|-----------|
| **OMO PlanProgress** | Markdown checklist 解析：正则匹配 `- [x]` vs `- [ ]`，统计 total/completed/isComplete | 完全扁平的进度追踪。没有 step entity，更谈不上依赖。步骤之间是纯文本行的集合——第 3 行和第 7 行没有任何约束关系 |
| **ACP PlanEntry** | content + priority + status 三字段，每个 entry 独立 | 工业协议标准定义了最低公共分母。跨产品兼容的代价是语义最小化——不能要求所有产品都实现依赖图 |
| **CodeWhale PlanStep** | text + status + started_at/completed_at，原子步骤由单一 PlanState 管理 | 最完善的扁平实现——有状态机校验、单一 in_progress 约束、耗时统计。但仍然没有 parent_id 和 dependency_ids。所有步骤在同一个 Vec 中顺序排列，修改步骤 3 的 text 时，步骤 4-7 是另一行的字符串——彼此之间零关联 |
| **Hermes Kanban task_links** | parent_id/child_id 的多对多关联表，支持进度汇总 | 这是 Hermes Kanban 中最接近依赖图的设计。但 task_links 只有父子二元关系，没有「关联强度」「依赖类型」「只读依赖 vs 强耦合依赖」的语义。且 task_links 服务于任务分发（「子任务完成 → 父任务可推进」），不服务于 Plan 级联修正（「步骤 3 改了 → 步骤 4-7 需重审」） |
| **人类手工管理** | 改了一处后手动检查所有后续步骤 | 不可规模化。Plan 超过 10 步时手动检查的遗漏率急剧上升。且人类检查的颗粒度远低于 Agent 的检查能力——Agent 可以逐行比对产出物，人类只能看标题 |

**共性缺陷**：所有方案都承认 Plan 步骤之间「应该有先后顺序」（通过列表序号隐含），但没有一个方案把这种顺序关系**结构化**。序号是供人类阅读的视觉助记符，不是可供机器推理的数据结构。

---

## 3. 方案设计

### 3.1 OKR 增强型 PlanStep 字段设计

核心思路：借鉴 OKR（Objectives and Key Results）的思想——不仅定义「要做什么」（Objective），还定义「做完是什么样的」（Key Result）——为每个 PlanStep 引入可验证的结果指标。在此基础上增加依赖图字段。

```typescript
// OKR 增强型 PlanStep（本方案）
interface OKRPlanStep {
  // ─── 基础字段（继承自现有扁平模型）────
  text: string;              // 步骤描述（Objective）
  status: PlanStatus;        // pending | in_progress | completed | pending_review

  // ─── OKR 层：可验证的结果指标 ────
  key: string;               // 该步骤的 Key Result：可验证的完成标准
                             // 例："POST /register 返回 201 + 数据库新增一行 user 记录"
                             // 格式：自然语言断言，但必须可被 Agent 或测试代码判定真/假

  // ─── 依赖图层：结构化的步骤间关系 ────
  step_id: string;           // 唯一标识符（UUID 或语义化 ID，如 "step-3"）
  parent_id?: string;        // 父步骤的 step_id。null = 根步骤
                             // 子步骤全部完成 → 父步骤自动标记为完成

  dependency_ids: string[];  // 显式依赖列表：此步骤依赖哪些其他步骤的产出
                             // 区别于 parent_id：前者是「层级包含关系」，后者是「产出依赖关系」
                             // 例如 step 6 可能依赖 step 2 的结果，但它不是 step 2 的子步骤

  association_strength: AssociationStrength;
                             // "strong" | "moderate" | "weak"
                             // strong：修改此步骤必须重审依赖节点
                             // moderate：修改此步骤建议重审依赖节点
                             // weak：修改此步骤仅通知依赖节点，不强制重审

  // ─── 子节点列表（树形结构）────
  children?: OKRPlanStep[];  // 递归嵌套。叶子节点是原子任务，非叶子节点是聚合任务
}
```

**五个新字段的设计理由**：

**① `key`**：扁平 Plan 的最大问题是「完成」没有验证标准。Agent 把 Step 3 标记为 completed，但你怎么知道它真的完成了？`key` 是嵌入在 Plan 结构中的「验收测试」——每个步骤都带着一个可验证的断言。这让审查 Agent 可以自动判断步骤是否真正完成，而不需要人类逐项检查。

为什么叫 OKR？OKR 的精髓是「每个 Objective 都有可衡量的 Key Result」。把这个思想应用到 PlanStep 上：每个步骤的 `text` 是 Objective（要做什么），`key` 是 Key Result（做完是什么样的）。Plan 从「愿望清单」升级为「可验证的承诺集合」。

**② `parent_id`**：步骤的层级结构。一个 50 步的 Plan 对人类和 Agent 都是认知负载——平坦化到一个列表中，无法看到「这 7 步都属于同一个子目标」。`parent_id` 引入树形结构，让 Agent 可以「聚焦当前分支」，而不是在 50 步的列表中迷失上下文。

**③ `dependency_ids`**：跨分支的产出依赖。`parent_id` 表达的是「逻辑分组」（步骤 4-7 是步骤 3 的子任务），`dependency_ids` 表达的是「数据/产出依赖」（步骤 6「实现 JWT 鉴权」依赖步骤 2「POST /register」的接口定义——但它们不在同一个父子分支中）。没有 dependency_ids，跨分支的影响分析完全不可追踪。

**④ `association_strength`**：不是所有依赖都是等价的。

- 强关联（strong）：步骤 A 的产出在步骤 B 中被直接引用/调用。改 A 必须重审 B。
- 中关联（moderate）：步骤 A 的产出定义了步骤 B 的上下文（如接口约定）。改 A 很可能影响 B，但不是必然。
- 弱关联（weak）：步骤 A 和 B 共享同一个模块/文件，但没有直接调用关系。改 A 只需通知 B，不强制重审。

这个三级强度的设计来自实际工程经验——不是每个「依赖」都意味着「改了就炸」。没有强度分级，所有依赖都被当作强依赖处理，导致过度重审、Token 浪费。

**⑤ `children`**：递归嵌套。原子任务是叶子节点（没有 children），聚合任务是中间节点（children 是子步骤列表）。树形结构让 Plan 的复杂度可以被「折叠」——Agent 看顶层 Plan 时只看到 5 个聚合步骤；进入某个聚合步骤后才能看到里面的 10 个原子步骤。这解决了「50 步 Plan 的认知负载」问题。

### 3.2 级联修正引擎

级联修正引擎是建立在 OKR PlanStep 依赖图之上的自动化传播机制。

**核心算法**：

```
function cascade_correct(modified_node: OKRPlanStep, plan_graph: Graph):
    affected = transitive_closure(modified_node, plan_graph, direction="downstream")
    
    for node in affected:
        match node.association_strength:
            "strong"   → node.status = "pending_review"
                          schedule_review(node)
            "moderate" → node.status = "pending_review"
                          # moderate 节点也会被标记，但审查时的检查深度较浅
            "weak"     → notify(node)  # 仅通知，不强制重审
    
    # 向上传导：如果修改导致父步骤的 key 不再满足，标记父步骤
    current = modified_node.parent
    while current != null:
        if not verify_keys(current):
            current.status = "pending_review"
            schedule_review(current)
        current = current.parent
```

**引擎的三个阶段**：

**阶段一：遍历依赖图 → 标记 affected 集合**

从被修改节点出发，沿 `dependency_ids` 和 `parent_id → children` 做 BFS/DFS 遍历。`transitive_closure` 计算所有「下游被影响」的节点——即所有通过显式依赖或父子关系间接关联的节点。不是遍历整张图——只遍历从修改点出发的**下游子图**。

**阶段二：按 association_strength 分级处理**

- `strong` → 标记 `pending_review`，触发完整审查（重新验证 key、重新检查产出物一致性）
- `moderate` → 标记 `pending_review`，触发轻量审查（只检查接口/类型签名是否仍匹配，不深查实现细节）
- `weak` → 不修改状态，仅向 Agent 发送通知：「步骤 X 被修改了，你可能需要看一眼，但不强制」

分级处理的核心价值：不是所有被影响的步骤都需要重新执行。Token 不是免费的——每轮审查都消耗上下文。分级处理确保审查资源分配给「真正可能出问题」的节点，而不是「理论上有关系但实际互不影响的」节点。

**阶段三：向上传导到根节点**

修改可能导致父步骤的 `key` 不再满足。例如：父步骤的 key 是「所有子步骤的接口文档完整」。Step 3 子步骤改了接口签名——父步骤的 key 变为不满足。引擎沿 `parent_id` 链向上回溯，逐级重新验证 key。

向上传导的关键约束：**单向性**。只向上传导（子→父），不向下传播（父→子）。向下传播（「父步骤改了，所有子步骤重审」）会导致级联风暴——一个顶层修改触发整个 Plan 的重审，Token 消耗爆炸。

### 3.3 为什么是树形而不是通用图

从数据结构的角度看，Plan 的依赖关系构成了一个**有向无环图（DAG）**——不是树（一个子节点可能有多个父依赖）。但在 Plan 的上下文中，`parent_id` 表达的是**逻辑层级**（任务分解的层次结构），`dependency_ids` 表达的是**产出依赖**（数据/接口的依赖关系）。

把两者分开的原因：

1. **逻辑层级是树，产出依赖是图。** 树形层级对应「任务分解」——「实现用户注册」分解为 7 个子任务。这是一种上层对下层的包含关系，天然是树。产出依赖对应「这个步骤的输出是那个步骤的输入」——这是一种横向的数据流，天然是图。把两者分开建模，级联修正引擎只需要遍历「产出依赖图」而不是「整个复杂的混合结构」。

2. **树形层级支持折叠和上下文隔离。** 当 Agent 执行「Step 3.2：实现邮箱验证的 SMTP 部分」时，它不需要看到 Step 5 的内容——它们不在同一个子树中。树形结构让 Agent 的注意力可以聚焦在当前分支上。

3. **级联修正的传播路径在依赖图而非层级树上。** 修改 Step 3.2 时，受影响的是「依赖 Step 3.2 产出的所有节点」——这个传播由 `dependency_ids` 图计算，与层级无关。层级树只用于重新验证父节点的 key——这是「向上验证」而非「级联传播」。

---

## 4. 分析

### 4.1 为什么这个方案能解决根本问题

根本问题不是「PlanStep 字段不够多」——是「Plan 中步骤之间的关系没有被编码为可计算的结构」。

OKR 增强型 PlanStep 的五个新字段分为三个功能层：

- **OKR 层**（`key`）：让「完成」从主观判断变为可验证断言。解决的是「Agent 说做完了但我怎么知道真的做完了」的问题。
- **依赖图层**（`step_id`, `parent_id`, `dependency_ids`）：让步骤间的关系从「人类阅读的隐含假设」变为「可遍历的有向图」。解决的是「改了第 3 步怎么知道第 4-7 步受影响」的问题。
- **强度层**（`association_strength`）：让影响分析的粒度从「二值（受影响/不受影响）」变为「三级渐进」。解决的是「不是每个受影响节点都需要重审——过度重审是 Token 浪费」的问题。

三层合在一起：Plan 从「给人看的 Checklist」升级为「Agent 可推理的执行图」。级联修正引擎不是外挂的修复工具——是依赖图的原生能力。

### 4.2 边界条件

以下场景本方案**无法**覆盖：

- **隐式语义依赖**：两个步骤没有显式声明 `dependency_ids`，但它们的产出存在语义冲突（例如 Step 2 定义了 user_id 为 int32，Step 6 在另一个文件中假定 user_id 为 string）。这种跨文件的类型不一致需要 LSP/类型检查器来发现，不是依赖图能解决的。
- **依赖图本身需要维护**：Agent 创建的 Plan 中，`dependency_ids` 和 `association_strength` 的准确性依赖 Agent 在规划阶段的理解。如果 Agent 漏标了依赖（「我以为 Step 4 不依赖 Step 3」但实际依赖），级联修正引擎不会修正这个漏标——它只会按已声明的依赖传播。
- **循环依赖**：依赖图必须是无环的（DAG）。如果 Agent 创建了循环依赖（A 依赖 B 且 B 依赖 A），级联修正会陷入无限循环。需要在 Plan 创建时做 DAG 校验（拓扑排序检测环）。
- **跨会话依赖**：Plan 的步骤可能跨多个 Agent session 执行。session 之间的依赖图一致性需要持久化到共享存储（数据库或文件）中。在 session 隔离的架構下，需要额外的「Plan 状态同步」机制。
- **过大的依赖图**：如果 Plan 包含 100+ 个步骤且依赖图稠密，修改一个节点的级联传播可能涉及数十个节点。虽然这比传统方案的「全部重审」好得多，但仍是不可忽略的 Token 成本。对于超大 Plan，需要引入「检查点隔离」机制——把级联传播限制在同一个检查点区间内。

### 4.3 与现有方案的对比

| 维度 | OMO PlanProgress | ACP PlanEntry | CodeWhale PlanStep | Hermes task_links | 本方案 OKR PlanStep |
|------|:---:|:---:|:---:|:---:|:---:|
| 步骤标识 | 无（文本行） | 隐式（数组位置） | text 字符串 | task id（UUID） | step_id（显式） |
| 步骤间关系 | 无 | 无 | 无（仅顺序） | parent_id/child_id | parent_id + dependency_ids（双重） |
| 关联强度 | 无 | 无 | 无 | 无 | strong/moderate/weak（三级） |
| 完成标准 | 用户主观判断 | 用户主观判断 | 用户主观判断 | 用户主观判断 | key（可验证断言） |
| 级联修正 | 无 | 无 | 无 | 无（仅进度汇总） | dependency-based cascade engine |
| 树形层级 | 无 | 无 | 无 | 有（两层） | 有（多层的 children 递归） |

Hermes task_links 的 parent_id/child_id 是最接近本方案的设计——事实上，Hermes Kanban 已经在任务分发层做了「父子任务」的关联。但 task_links 的设计目标是任务委托（「这个子任务该派给谁」），不是级联修正（「这个修改影响了哪些步骤」）。两者的关键差异：

1. **Hermes task_links 是二元关系**（parent/child），没有 dependency_ids 这种跨层级的产出依赖。在 Hermes Kanban 中，如果 Task A 和 Task B 共享同一个文件但不在同一父子链上，没有任何字段记录它们之间的关联。
2. **Hermes task_links 没有关联强度**。父任务知道「子任务完成了多少」，但不知道「子任务的修改对父任务的影响有多大」。这导致了父子关系的「全或无」——要么完全无关（不在同一 parent chain），要么完全绑定（在 chain 中）。缺少中间状态。
3. **Hermes Kanban 的任务没有 key 字段**。一个 task 被标记为 done 并不意味着它的产出通过了验证——done 只是用户或 Agent 的主观标记。

---

## 5. 验证路径

### 5.1 已验证

- **问题存在性**：交互性验证了三个框架的 Plan 数据结构——
  - OMO：`PlanProgress` 只有 `total/completed/isComplete`，无任何步骤级语义
  - ACP 协议：`PlanEntry` 只有 `content/priority/status`
  - CodeWhale：`PlanStep` 最完善但仍然是扁平结构——`text/status/started_at/completed_at`，存储在 `Vec<PlanStep>` 中，步骤间无关联
  - Hermes Kanban：`task_links` 表有 parent_id/child_id，但仅用于任务分发场景的父子聚合，不服务于 Plan 的级联修正
- **级联修正需求**：在实际 Agent 使用中，「改一步导致后几步失效」是高频场景——尤其在「用户中途修改需求」时。8 款 Agent 产品的深度对比确认了这是 Plan 模块最需要解决但全部未解决的问题

### 5.2 待验证

- **依赖图创建的准确性**：Agent 在 Plan 创建阶段能否准确识别步骤间的依赖关系并标注合理的 `association_strength`？需要在一组标准任务（50+ 个 multi-step tasks）上测试依赖标注的精确率和召回率
- **级联传播的 Token 成本**：修改一个步骤后，级联修正引擎产生的额外审查 Token vs 传统「全部重审」的 Token 消耗对比。预期级联修正的 Token 成本约为全量重审的 15-35%（因为仅重审受影响的子图）
- **OKR key 的验证率**：Agent 自动验证 `key`（可验证完成标准）的准确率。如果 key 过于抽象（「代码质量良好」），Agent 无法自动验证——key 的价值降为零。需要探索 key 的最佳粒度和表述范式
- **向上传导的误报率**：父步骤被标记 `pending_review` 后，有多少是「确实需要修改」vs「key 验证结果不变，白标记了」？向上传导的精确率决定了引擎的实用价值
- **与 Hermes Kanban task_links 的集成路径**：如果把 OKR PlanStep 的 fields 注入 Hermes Kanban 的 task 模型——需要添加 `dependency_ids`、`association_strength`、`key` 三个新字段和相应的级联逻辑——对现有 kanban kernel 的改动范围和兼容性影响

---

## 6. 与 Hermes 的关系

Hermes 在 Plan 和 Kanban 两方面都具备改造的基础：

**在 Kanban 侧**：Hermes Kanban 的 `task_links` 表已经实现了 parent/child 关系表。这是所有 Agent 产品中最接近依赖图的设计。改造路径：

1. **在 `tasks` 表增加字段**：`key`（可验证完成标准，TEXT）、`association_strength`（关联强度覆盖枚举，TEXT，如 `strong/moderate/weak`）。`step_id` 可以复用现有的 `id`（UUID）。
2. **扩展 `task_links` 表**：增加 `link_type` 字段（`"hierarchy"` 表示 parent_id 关系，`"dependency"` 表示 dependency_ids 关系）。当前的 parent_id/child_id 是层级关系，dependency_ids 是横向依赖——两种关系需要区分但可以共用同一张表。
3. **在 Kanban kernel 中增加级联逻辑**：当一个 task 的 `body` 或 `result` 被修改时，查询 `task_links` 表中以该 task 为 `parent_id` 的所有 dependency 类型关联——将这些关联 task 标记为 `pending_review`。
4. **新增加审查 Agent 的 Kanban 触发**：status 变为 `pending_review` 的 task 由专门的审查 Agent 处理——审查逻辑复用 Hermes 现有的 Skill/审查机制。

**在 Plan 侧**：Hermes 目前使用扁平 PlanStep（`text + status`），不直接从 Kanban task_links 读取依赖信息。改造路径：

1. 让 Agent 在生成 Plan 时使用 OKR 增强型 PlanStep schema——`key` 是必填字段
2. Plan 执行过程中，步骤的变更通过级联修正引擎自动传播
3. Plan 的状态持久化到 Kanban——Plan 的步骤和 Kanban 的 task 是同一个概念在不同层面的投影

**为什么 Hermes 是最适合实现此方案的平台**：

其他所有 Agent 框架的 Plan 都是完全扁平的——从一开始就没有依赖关系的概念。Hermes 的 Kanban 是唯一一个「已经有了 parent/child 关系，只是没有用到 Plan 级联修正上」的平台。从 task_links 到 OKR PlanStep 的改造不是从零开始构建依赖系统——是在已有的关系表上增加语义和传播逻辑。

---

## 结论

Agent 的 Plan 不应该是一个给人类看的 Checklist。Checklist 是「让人逐项打勾」的工具，Plan 是「让 Agent 知道改了 A 之后 B 也需要重审」的推理基础。

OKR 增强型 PlanStep 的五个新字段（key, step_id, parent_id, dependency_ids, association_strength）把 Plan 从扁平的文本列表升级为可计算的有向依赖图。级联修正引擎利用这个图实现了「改一处，精确定位受影响范围，分级处理」的自动化传播——不再需要人类手动检查每一处的连锁反应。

这不是「Plan 写的更详细」——是 Plan 的语义从「文本约定」变成了「结构化数据」。当依赖关系不再是写在步骤描述里的自然语言（「注意：此步骤依赖步骤 3 的输出」），而是结构化的 dependency_ids 数组时，Agent 才能真正去推理「这个修改会影响什么」。

---

*上一篇：[05 文档 KV Cache 优化结构](05-document-kv-cache.md) — Agent 产出的文档也需要 KV Cache 优化*
*下一篇：[07 审查切换引擎](07-review-switching.md) — 审查严格度应根据上下文状态动态调整*
