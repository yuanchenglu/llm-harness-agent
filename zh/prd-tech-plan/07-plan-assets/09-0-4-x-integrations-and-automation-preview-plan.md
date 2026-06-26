# 09. `0.4.x` Integrations And Automation Preview 版本研发计划

## 0. AI 执行提示词

你是 `0.4.x Integrations And Automation Preview` 的版本负责人。只有在 `0.3.x` 本地工作区、Memory、Skill、PlanGraph 成立后，才能接入外部工具和自动化。你的首要责任是安全边界：工具 schema、权限、drift、health、schedule、notification、remote approval 和 audit。不要做公开插件市场、云端常驻、多租户或无审批副作用。所有外部工具输出都是非信任输入。

当前状态（确定，2026-06-17）：

- 本计划对应 `0.4.x` 主线已实现并归档。
- `0.3.x` 已归档，主规格为 `openspec/specs/general-workspace-agent/spec.md`。
- `start-integrations-automation-preview` 已归档到 `openspec/changes/archive/2026-06-17-start-integrations-automation-preview`。
- 主规格已同步到 `openspec/specs/integrations-automation-preview/spec.md`。
- 后续不要把新工作塞回该 archived change；0.4 只接受明确 patch，1.0 准备走 `prepare-stable-public-release`。

## 1. 目标

`0.4.x` 的目标是在本地工作台成熟后，安全预览外部集成和本地自动化。

版本完成后，用户应能：

1. 连接受控 MCP/tool。
2. 查看 local tool catalog。
3. 看见 tool schema fingerprint 和 drift warning。
4. 配置 tool permission profile。
5. 运行 tool health check。
6. 创建本地 scheduled task。
7. 收到 notification。
8. 对预生成 actions 做 remote approval。
9. 查看 automation audit log。

## 2. 事实依据

确定：

- `0.4.x` release line 是 Integrations And Automation Preview。
- PRD TechPlan 明确 `0.4.x` 必须做 MCP client、local tool catalog、schema fingerprint、drift detection、permission profiles、health check、local scheduled tasks、notification bridge、remote approval、automation audit log。
- PRD TechPlan 明确 `0.4.x` 不做公开插件市场、云端常驻、无审批自动副作用、企业 policy center、多租户。
- Runtime-first、Evidence-first、Policy-enforced、Recoverable 仍然是全局约束。
- `0.3.x` General Workspace Agent 已归档到 `openspec/changes/archive/2026-06-09-start-general-workspace-agent`。
- `0.4.x` Integrations And Automation Preview 已归档到 `openspec/changes/archive/2026-06-17-start-integrations-automation-preview`。
- `openspec/specs/integrations-automation-preview/spec.md` strict validate 通过。

前置 gate：

- `0.3.x` Artifact、Memory、Skill、PlanGraph、Review Gate 已通过。
- `openspec/specs/general-workspace-agent/spec.md` strict validate 通过。
- Tool / Skill index 不破坏 prefix cache discipline。
- Evidence ledger 能承载外部工具调用。

需要重新核验：

- 当前可用 MCP client 方案。
- 当前工具权限模型是否足以覆盖外部工具。
- 本地 scheduled task 在目标平台上的启动机制。
- notification bridge 的平台权限和隐私边界。

验证命令：

```bash
python3 scripts/check_repo.py
openspec validate general-workspace-agent --type spec --strict
rg -n "MCP|tool schema|drift|scheduled|notification|approval|audit" \
  docs/llm-harness-agent/zh/prd-tech-plan \
  docs/llm-harness-agent/zh/blueprint
```

## 3. 关键决策

- `0.4.x` 只做 preview，不做开放生态平台。
- Tool schema 必须 fingerprint，变化必须 drift warning。
- Tool permission profile 默认最小权限。
- Scheduled task 默认本地执行，不能云端常驻。
- Remote approval 只批准已生成 action，不允许远端直接发起任意本地工具调用。
- Automation audit log 是 release gate，不是 debug 附件。
- 外部工具输出必须进入 evidence，并标注 trust boundary。

## 4. 非目标

- 不做公开插件市场。
- 不做云端常驻执行。
- 不做企业 policy center。
- 不做多租户。
- 不做个人微信深度控制。
- 不做无审批自动副作用。
- 不允许外部 tool 直接绕过 ChangeSet / permission / rollback。

## 5. 实施步骤与完成事实

### 5.1 OpenSpec

建议 change：

```text
start-integrations-automation-preview
```

OpenSpec 已包含：

1. MCP client requirement。
2. Tool catalog requirement。
3. Schema fingerprint / drift requirement。
4. Permission profile requirement。
5. Scheduled task requirement。
6. Notification bridge requirement。
7. Remote approval requirement。
8. Automation audit log requirement。
9. Security scenarios。

归档后复核：

```bash
openspec validate integrations-automation-preview --type spec --strict
find openspec/changes/archive -maxdepth 2 -type d | rg "start-integrations-automation-preview"
```

### 5.2 MCP client and tool catalog

1. 定义 tool catalog 数据结构：
   - tool_id。
   - provider。
   - schema。
   - schema_hash。
   - risk_profile。
   - health_status。
   - enabled。
2. 支持连接测试。
3. 支持工具禁用。
4. 支持工具来源记录。
5. 支持工具列表 UI。

验证：

```bash
rg -n "tool_id|schema_hash|risk_profile|health_status" src apps tests
```

### 5.3 Drift detection

1. 连接时计算 schema fingerprint。
2. 每次启动或定期 health check 复核 fingerprint。
3. fingerprint 变化时：
   - 标记 drift。
   - 暂停高风险调用。
   - 要求用户重新确认。
4. drift event 写入 audit log。

验证：

```bash
rg -n "drift|fingerprint|schema_hash" src apps tests
```

### 5.4 Permission profiles

1. 定义 profile：
   - read-only。
   - write-with-approval。
   - network-limited。
   - disabled。
2. 每次工具调用前生成 PermissionRequest。
3. 高风险 action 必须 approval。
4. permission decision 写入 evidence。
5. UI 展示工具风险和最后一次 decision。

验证：

```bash
rg -n "PermissionRequest|permission profile|write-with-approval|network-limited" src apps tests
```

### 5.5 Local scheduled tasks

1. 定义 schedule 数据结构：
   - task template。
   - schedule。
   - workspace。
   - permission profile。
   - next run。
   - audit ref。
2. scheduled task 启动时必须写入 audit event。
3. 任何副作用 action 必须进入 approval。
4. task 结束后必须报告 completion evidence、cost 和 human intervention。
5. 失败要有 retry / pause / disable 路径。

验证：

```bash
rg -n "schedule|next_run|automation audit|human intervention" src apps tests
```

### 5.6 Notification bridge

1. 支持本地通知：
   - task completed。
   - approval required。
   - failed。
   - drift detected。
2. 通知内容不包含 secret 或敏感正文。
3. 点击通知回到 task detail。
4. 用户可关闭通知。

验证：

```bash
rg -n "notification|approval required|drift detected" src apps tests
```

### 5.7 Remote approval for pre-generated actions

1. 只允许批准已经生成并持久化的 action。
2. approval token 必须：
   - 短期有效。
   - 单次使用。
   - 绑定 action hash。
   - 绑定 task id。
3. remote approval 不允许修改 action 内容。
4. approval / denial 写入 audit。

验证：

```bash
rg -n "approval token|action hash|single use|remote approval" src apps tests
```

### 5.8 Automation audit log

1. 每次自动化运行记录：
   - trigger。
   - task template hash。
   - tool calls。
   - permissions。
   - approvals。
   - evidence。
   - result。
   - cost。
2. audit log 支持 UI 查看和导出。
3. audit log redaction 有测试。

验证：

```bash
rg -n "automation audit|trigger|task template hash|redaction" src apps tests
```

## 6. 验证命令

```bash
python3 scripts/check_repo.py
openspec validate integrations-automation-preview --type spec --strict
openspec validate desktop-code-workbench-first-slice --type spec --strict
openspec validate general-workspace-agent --type spec --strict
PYTHONPATH=src python3 -m unittest discover -s tests -v
cd apps/desktop && npm run test && npm run build && npm run e2e
rg -n "MCP|schema_hash|drift|permission profile|scheduled|notification|remote approval|automation audit" \
  docs/llm-harness-agent/zh/prd-tech-plan apps src tests
```

## 7. 完成定义

`0.4.x` 完成必须满足，且 2026-06-17 已按归档流程确认：

- MCP connection test 通过。
- Tool schema fingerprint 和 drift detection 有测试。
- Tool permission profile 有默认 deny / approval 行为。
- Scheduled task 有 audit log。
- Notification 不泄露 secret。
- Remote approval token 单次有效并绑定 action hash。
- 自动化报告 completion evidence、approval intervention 和每成功任务成本。
- 无审批自动副作用被测试拒绝。
- `0.3.x` Artifact / Memory / PlanGraph 不回归。
- `start-integrations-automation-preview` 不再出现在 active OpenSpec list。
