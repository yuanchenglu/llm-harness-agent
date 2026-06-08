# 08. `0.3.x` General Workspace Agent 版本研发计划

## 0. AI 执行提示词

你是 `0.3.x General Workspace Agent` 的版本负责人。你必须在 `0.2.x` Code Workbench 成立后再扩展到通用本地工作区。不要把它做成聊天壳；它仍然是 runtime-first、evidence-first、local-first 的工作台。先核对 `0.2.x` gate、PRD TechPlan、Memory / Skill / PlanGraph 的架构约束，再创建 OpenSpec。所有 artifact、Memory、Skill、PlanStep 都必须可审计、可删除、可恢复，不得破坏 DeepSeek prefix cache discipline。

## 1. 目标

`0.3.x` 的目标是从代码工作台扩展到通用本地工作区，让用户处理本地文件、文档、报告和长期项目知识。

版本完成后，用户应能：

1. 选择普通工作区或项目文件夹。
2. 让 Agent 总结文件夹、阅读多文档、生成报告。
3. 把可验证结果保存为 artifact。
4. 管理 Project Memory。
5. 使用 Skill index / body separation。
6. 查看 PlanGraph 和 Review Gate。
7. 对长期任务恢复、审查和导出 evidence。

## 2. 事实依据

确定：

- `0.3.x` release line 是 General Workspace Agent。
- PRD TechPlan 将文件夹总结、多文档报告、artifact manager、Project Memory、Skill index/body separation、PlanGraph、Review Gate 放入 `0.3.x`。
- Runtime 仍是唯一 agent loop。
- Evidence ledger、route/cache/usage/cost 必须继续可见。
- Memory / Skill / Tool catalog 不能破坏 byte-stable prefix。

前置 gate：

- `0.2.x` Desktop Code Workbench gate 已通过，或有明确延期豁免。
- Desktop/CLI 已能展示 task evidence 和 cost。
- ChangeSet / approval / rollback 语义没有回归。

需要重新核验：

- 当前 runtime 是否已有 Memory / Skill / PlanStep 数据对象或需要新增。
- 当前 event log 格式是否足以承载 artifact 和 PlanGraph。
- 文档解析依赖是否会引入安全或隐私风险。

验证命令：

```bash
python3 scripts/check_repo.py
rg -n "Project Memory|Skill index|PlanGraph|Review Gate|EvidenceEvent|PlanStep" \
  docs/llm-harness-agent/zh/prd-tech-plan \
  docs/llm-harness-agent/zh/blueprint
```

## 3. 关键决策

- `0.3.x` 做通用本地工作区，不做外部工具集成主线。
- Artifact 是一等对象，不能只是 UI 里的文本。
- Memory 默认需要用户确认，必须可编辑、禁用、删除。
- Skill index 常驻；Skill body 按需加载。
- PlanGraph 记录任务步骤、依赖、风险、evidence 和 checkpoint。
- Review Gate 是显式步骤，不是模型自称“已审查”。
- 文档读取只支持本地文件和安全格式；网络抓取不进入 `0.3.x` 默认能力。

## 4. 非目标

- 不做 MCP client。
- 不做定时任务。
- 不做远程审批。
- 不做团队共享 Memory。
- 不做企业治理。
- 不做浏览器深度控制。
- 不做无审批副作用。
- 不把所有 Memory / Skill body 常驻塞进 prompt。

## 5. 实施步骤

### 5.1 OpenSpec

建议 change：

```text
start-general-workspace-agent
```

OpenSpec 必须包含：

1. Artifact requirement。
2. Memory lifecycle requirement。
3. Skill index/body requirement。
4. PlanGraph requirement。
5. Review Gate requirement。
6. Evidence / cache / cost requirement。
7. Security and redaction scenarios。

验证：

```bash
openspec validate start-general-workspace-agent --type change --strict
```

### 5.2 Artifact manager

1. 定义 artifact 数据结构：
   - `artifact_id`
   - `task_id`
   - `type`
   - `source_refs`
   - `content_ref`
   - `created_at`
   - `evidence_ids`
2. 支持 artifact 类型：
   - summary。
   - report。
   - extracted notes。
   - review result。
3. Artifact 必须记录来源引用。
4. Artifact 不公开保存 raw secret、raw prompt、raw reasoning_content。
5. UI 支持 artifact list/detail/export。

验证：

```bash
rg -n "artifact_id|source_refs|evidence_ids" apps src tests
```

### 5.3 Document and folder tasks

1. 支持 workspace scan：
   - 文件树。
   - 文件类型。
   - 大小限制。
   - binary 排除。
   - hidden / ignored 文件策略。
2. 支持 read-only summary task。
3. 支持多文档 report task。
4. 支持任务中引用具体文件和行/段落。
5. 支持失败时列出未读文件和原因。

验证：

```bash
python3 -m unittest discover -s tests -v
```

### 5.4 Project Memory

1. Memory 只来自明确 evidence：
   - 用户确认。
   - 成功任务总结。
   - 显式导入。
2. Memory lifecycle：
   - propose。
   - approve。
   - edit。
   - disable。
   - delete。
3. Memory 进入 context 前必须有 index 和 relevance reason。
4. Memory 不能泄露 secret。
5. UI 提供 Memory 管理页。

验证：

```bash
rg -n "memory|Memory" src apps tests docs/llm-harness-agent/zh/prd-tech-plan
```

### 5.5 Skill index / body separation

1. Skill index 放稳定前缀：
   - name。
   - description。
   - trigger。
   - version。
2. Skill body 按需加载：
   - 只有触发时加载。
   - 加载原因进入 evidence。
   - body hash 进入 event。
3. Skill 更新必须有 provenance。
4. Skill 不得直接绕过 permission。

验证：

```bash
rg -n "skill|Skill|body hash|provenance" src apps tests
```

### 5.6 PlanGraph

1. 定义 PlanStep：
   - id。
   - parent_id。
   - dependencies。
   - objective。
   - expected_result。
   - status。
   - risk。
   - evidence_ids。
   - checkpoint_id。
2. UI 展示 PlanGraph：
   - current step。
   - blocked step。
   - completed step。
   - Needs Review。
3. 任务恢复时从 PlanStep 继续，而不是重新开始。
4. 每步必须关联 evidence。

验证：

```bash
rg -n "PlanStep|PlanGraph|checkpoint_id|evidence_ids" src apps tests
```

### 5.7 Review Gate

1. Review Gate 可由以下条件触发：
   - high risk。
   - large artifact。
   - uncertain evidence。
   - failed verifier。
   - user request。
2. Review 输出必须包含：
   - checked evidence。
   - unresolved questions。
   - recommended action。
   - cost/cache summary。
3. Review Gate 不能自动批准写入。

验证：

```bash
rg -n "Review Gate|Needs Review|unresolved|recommended action" src apps tests
```

## 6. 验证命令

```bash
python3 scripts/check_repo.py
openspec validate start-general-workspace-agent --type change --strict
python3 -m unittest discover -s tests -v
cd apps/desktop && npm run test && npm run build && npm run e2e
rg -n "Artifact|Project Memory|Skill index|PlanGraph|Review Gate|cost per successful task" \
  docs/llm-harness-agent/zh/prd-tech-plan apps src tests
```

## 7. 完成定义

`0.3.x` 完成必须满足：

- Artifact 有来源引用并可导出。
- Memory 可确认、编辑、禁用、删除。
- Skill body 只按需加载，且加载原因进入 evidence。
- PlanStep 可持久化、恢复、关联 evidence。
- Review Gate 可触发并写入 evidence。
- 长期任务能汇总完成率、恢复结果、人工接管和 token/cost。
- 所有新增能力不破坏 `0.2.x` diff/approval/rollback。
- 测试、build、E2E 和 `check_repo.py` 通过。

