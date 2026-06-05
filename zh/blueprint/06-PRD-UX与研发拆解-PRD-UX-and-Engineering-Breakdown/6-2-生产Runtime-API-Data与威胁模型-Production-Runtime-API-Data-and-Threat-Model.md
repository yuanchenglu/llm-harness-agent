# 6-2 生产 Runtime / API / Data 与威胁模型

> 版本：2026-06-05 production candidate。实现真相以 `src/deepseek_agent`、测试和 Stage 6 Gate 为准；本文不把未实现能力写成已完成。

## 1. 运行时边界

```text
Desktop / CLI
  → Local Control API
  → Orchestrator / Session Store / Evidence Ledger
  → Permission Policy / Workspace Sandbox / Change Manager
  → Runtime Adapter (current / OpenCode)
  → DeepSeek Provider Adapter
  → External API
```

信任原则：

- 模型输出永远不可信；
- workspace 内文件也可能被恶意内容污染；
- Provider 响应、插件和外部 runtime 都是非信任输入；
- Policy、Sandbox、ChangeManager、SessionStore 和验收器属于本地可信计算基；
- UI 不能绕过本地 policy；
- API key 只存在于进程环境和请求 header。

## 2. 本地 API

建议版本化前缀：`/v1`。P0 默认绑定 `127.0.0.1`，不开放远程访问。

| Method / Path | 用途 | 副作用与要求 |
|---|---|---|
| `POST /v1/tasks` | 创建任务 | 无代码副作用；校验预算、workspace |
| `GET /v1/tasks/:id` | 查询任务 | read |
| `POST /v1/tasks/:id/run` | 执行/继续 | 受 policy 与预算控制 |
| `POST /v1/tasks/:id/cancel` | 取消 | 停止新动作，不回滚已确认动作 |
| `GET /v1/tasks/:id/evidence` | 查询脱敏证据 | 禁止返回 Key/CoT |
| `POST /v1/permissions/:id/decision` | 批准/拒绝 | 写审计日志 |
| `POST /v1/changesets/:id/apply` | 应用 ChangeSet | hash 校验、批准、rollback |
| `POST /v1/changesets/:id/rollback` | 回滚 | 一次性 rollback token |
| `POST /v1/sessions/:id/resume` | 恢复 | 跳过 succeeded 副作用 |
| `POST /v1/benchmarks/e3` | 启动 E3 | 请求/成本硬上限 |
| `POST /v1/benchmarks/e4` | 启动 E4 | 固定任务、适配器与验收器 |

错误统一结构：

```json
{
  "error": {
    "class": "permission|sandbox|stale|provider|timeout|checkpoint|acceptance",
    "code": "stable_machine_code",
    "message": "safe human message",
    "retryable": false,
    "evidence_id": "event-id"
  }
}
```

## 3. 核心数据模型

### Task

```text
id, workspace_id, mode, goal, status, risk_budget,
model_policy, request_budget, max_steps, created_at, updated_at,
active_session_id, acceptance_ids, evidence_ids
```

### Session

```text
schema_version, session_id, step, messages(redacted-on-disk),
tool_calls, approvals, change_sets, usage, evidence
```

不变量：

- 原子写 checkpoint；
- 未知 schema 拒绝；
- succeeded side-effect tool call 永不自动重跑；
- API key 与未脱敏 CoT 不落盘。

### ToolCall

```text
call_id, task_id, session_id, name, arguments_evidence,
risk, status[pending|running|succeeded|failed],
result_evidence, error_class, idempotency_key
```

### PermissionDecision

```text
decision_id, call_id, risk, normalized_path, argv,
rule_id, decision[allow|ask|deny], scope, actor, timestamp
```

### ChangeSet

```text
change_set_id, task_id,
changes[path, original_sha256, proposed_content_hash],
diff_hash, decision_id, apply_status, rollback_token_id
```

### EvidenceEvent

```text
schema_version, event_id, timestamp, task/session/call ids,
event_type, request_sha256, request_structure, response_structure,
usage, cache, error_class, metadata
```

禁止字段：API key、authorization、完整 CoT、默认情况下的用户私有正文、未经许可的完整文件内容。

### BenchmarkResult

```text
run_id, suite, model, adapter, task/case id, repeat, seed, schedule,
status, duration, usage/cache/cost, acceptance, limitations, source index
```

## 4. Runtime Adapter Contract

统一生命周期：

```text
prepare(workspace/task)
→ run(prompt/task)
→ resume(session)
→ collect_evidence()
→ cleanup()
```

适配器必须满足：

- 不绕过 PermissionPolicy；
- 不直接写入证据外的私有输出；
- 错误映射到统一 error class；
- 清理临时资源；
- 模型、base URL、thinking、tools、usage 和错误传播可测试；
- runtime-specific resume 不支持时必须显式报错，不能静默新建任务。

## 5. 威胁模型

### 资产

- 源代码与未提交修改；
- API key 与账户预算；
- Git 历史与远程仓库；
- 本地文件、凭证和网络身份；
- session/checkpoint/evidence；
- 用户决策与审批记录。

### 攻击者与入口

| 攻击者/入口 | 示例 |
|---|---|
| 恶意模型输出 | 请求危险命令、伪造完成、诱导越权 |
| 仓库 prompt injection | README/issue/source 中要求泄密或绕过 policy |
| 恶意依赖/脚本 | test/install 脚本执行网络或删除 |
| 路径与链接 | `..`、绝对路径、symlink escape |
| 并发修改 | apply 前文件变化导致覆盖 |
| 恶意/异常 Provider | 错误字段、重复响应、超时、静默忽略 |
| 插件/外部 runtime | 绕过权限、记录正文或 Key |
| 本地非授权用户 | 读取 session/evidence 或调用 localhost API |

### 威胁与缓解

| 威胁 | 严重度 | P0 缓解 | 验证 |
|---|---:|---|---|
| workspace escape | Critical | resolve 后边界检查、阻止 symlink/absolute escape | traversal/symlink tests |
| 未批准写/删/shell/network/Git | Critical | 默认 deny、副作用显式 rule/approval | deny/ask/allow tests |
| shell 注入 | Critical | argv 数组、`shell=False`、危险命令分类 | injection test |
| stale patch 覆盖用户修改 | High | original SHA-256、apply 前复核 | stale hash test |
| 多文件 apply 中断 | High | temp+replace、失败回滚、显式 rollback | mid-apply failure test |
| resume 重复副作用 | Critical | stable call id、状态机、skip succeeded | resume test |
| Key/CoT 泄漏 | Critical | env-only、结构证据、redaction、secret scan | recorder/scan tests |
| 恶意网络外传 | Critical | 默认 network deny | network deny test |
| 无限循环/成本失控 | High | max steps/request/cost/time hard guard | budget tests |
| Provider 静默忽略参数 | High | capability validation、E3 matrix | invalid/ignored parameter E3 |
| Cache 优化导致旧策略复用 | High | 正确性变化主动失效，不把 cache 当正确性层 | E3 + policy tests |
| localhost API 被滥用 | High | loopback、随机 token/OS ACL、CSRF/origin 限制 | release security test |
| evidence 篡改 | Medium | event/hash chain、只追加、导出签名（P1） | integrity test |

## 6. 失败模式与恢复

| 失败点 | 安全状态 | 恢复 |
|---|---|---|
| Provider 请求前崩溃 | 无外部副作用 | 重试请求 |
| Provider 请求后未知结果 | 标记 unknown，不推断成功 | 人工/幂等检查 |
| Tool running 时崩溃 | 不自动假定 succeeded | 按工具幂等性 review/retry |
| ChangeSet apply 中断 | 回滚已应用项 | 验证原始/回滚 hash |
| checkpoint 写入中断 | 旧 checkpoint 保持完整 | 加载旧 checkpoint |
| external adapter 崩溃 | 当前 task failed/paused | 收集结构证据、cleanup、恢复 |
| acceptance 失败 | 不允许 Completed | 修复、rollback、人工接管 |

## 7. 兼容性、发布与回滚

### 支持矩阵

- macOS arm64/x64；
- Windows x64；
- Python 3.10+（核心）；外部 runtime 依其固定版本；
- DeepSeek API capability snapshot 按日期/version；
- OpenCode 固定 commit 与最小配置；
- workspace 文件系统必须支持原子 rename；否则发布阻塞。

### 发布流程

```text
unit/security/recovery tests
→ E3 redacted bundle
→ E4 deterministic task comparison
→ package smoke
→ install/uninstall
→ canary workspace
→ release
```

### 回滚

- 版本回滚不得迁移/删除原 checkpoint；
- 不兼容 schema 必须拒绝并提供导出；
- policy 默认值只允许更严格；
- Provider capability 回退到最近已验证 snapshot；
- 外部 adapter 可禁用并回到当前 runtime；
- ChangeSet rollback token 与应用版本绑定。

## 8. 安全 Gate

发布前必须证明：

- 默认配置无法产生未经批准副作用；
- 所有路径和 shell 边界测试通过；
- session/resume 不重复副作用；
- evidence 不含密钥、正文或 CoT；
- E3/E4/发布产物可复算；
- 未支持能力明确失败，不静默降级。
