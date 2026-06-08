# 01. Runtime Kernel 发布与补丁计划

## 0. AI 执行提示词

你是 DeepSeekAgent / `deepseek_runtime` 的 release engineer。执行本计划时必须使用科研方法论：先定义问题，再核对事实源和命令输出，明确假设与置信度，然后做最小改动。不要把 runtime 写成旁路实验；它是 DeepSeekAgent 主线 runtime kernel。不要重写 runtime 语言，不要扩展桌面、移动端或 hosted service。任何发布判断必须有测试、release drill、live smoke、manifest、tag 或 GitHub 远端证据支撑。未经用户明确要求，不要 stage、commit、push 或创建 tag。

## 1. 目标

把 `deepseek_runtime` 作为 DeepSeekAgent 主线 runtime kernel 资产继续维护：记录已经完成的 `v0.1.1-alpha.0` 独立发布，以及后续完成的 `v0.1.1-alpha.1` ChangeSet 公共 API 补丁。

本计划不是重新抽取 runtime，也不是把 runtime 重新塞回 `deepseekagent` 主仓库。

## 2. 事实依据

确定：

- `deepseek_runtime` 是 DeepSeekAgent 在 CLI-first `0.1.x` 之后向 runtime kernel 收敛的主线基础层，不是旁路实验。
- runtime 仓库位于 `/Users/bluth/Code/deepseek_runtime`。
- runtime 公开 remote 是 `https://github.com/7colorai/deepseek_runtime.git`。
- runtime 默认分支是 `develop`。
- 已发布 tag 包含 `v0.1.1-alpha.0` 和 `v0.1.1-alpha.1`。
- `openspec/changes/extract-deepseek-runtime-kernel/tasks.md` 中 runtime 创建、验证、发布任务已经完成。
- `v0.1.1-alpha.1` 已发布，用于把 ChangeSet 相关 API 暴露给上层桌面 bridge。

验证命令：

```bash
git -C /Users/bluth/Code/deepseek_runtime status --short --branch
git -C /Users/bluth/Code/deepseek_runtime remote -v
git -C /Users/bluth/Code/deepseek_runtime tag --list 'v0.1.1-alpha.*' --sort=version:refname
sed -n '1,120p' openspec/changes/extract-deepseek-runtime-kernel/tasks.md
```

## 3. 关键决策

- Runtime 仓库保持独立，不作为 `deepseekagent` submodule。
- Python runtime 继续作为 kernel 主体，不因桌面端启动而重写成 TypeScript。
- 上层 GUI、CLI、第三方 Agent 都应依赖 runtime kernel，而不是复制 runtime 代码。
- API key、prompt 原文、response 原文、`reasoning_content` 原文不得进入公开 evidence。
- `ChangeManager`、`ChangeSet`、`FileChange`、`RollbackToken` 已在 `v0.1.1-alpha.1` 中列入 top-level public API；桌面首片可以通过 pinned tag 使用这些能力。

## 4. 非目标

- 不实现 hosted Runtime API service。
- 不做桌面 GUI。
- 不做移动端、企业治理或插件市场。
- 不迁移历史研究档案、私有 prompt、历史 trace 或模型输出正文。
- 不改变 `deepseekagent` 主仓库 remote 或把 runtime 作为 submodule。

## 5. 实施步骤与已完成记录：`v0.1.1-alpha.0`

已完成：

1. 创建独立仓库 `/Users/bluth/Code/deepseek_runtime`。
2. 配置 package：`deepseek-runtime`，import namespace：`deepseek_runtime`，版本：`0.1.1a0`。
3. 提供 `deepseek-runtime doctor --json` 和 `deepseek-runtime run`。
4. 提供 `DeepSeekClient`、`DeepSeekRuntime`、diagnostics、observability、sandbox、permission、session 等 kernel 原语。
5. 增加 release drill、safety drill、artifact builder、release audit、live API smoke。
6. 添加 README、双语 README、API、integration guide、physical traits、known unknowns、hosting roadmap、security、troubleshooting。
7. 推送 `develop` 并创建 `v0.1.1-alpha.0` tag。

完成定义：

- runtime 仓库可独立 clone、安装、运行 doctor。
- release audit 成功。
- live API smoke 成功并通过 redaction checks。
- 主仓库 handoff 和 OpenSpec 任务状态已同步。

## 6. 实施步骤与已完成补丁：`v0.1.1-alpha.1`

目标：把已存在的 diff/apply/rollback 能力正式公开给上层桌面 bridge 使用。

已完成：

1. 在 `/Users/bluth/Code/deepseek_runtime` 的 `develop` 分支确认工作区干净。
2. 将以下对象加入 `src/deepseek_runtime/__init__.py` 的 import 和 `__all__`：
   - `ChangeManager`
   - `ChangeSet`
   - `FileChange`
   - `RollbackToken`
   - `Decision`
   - `Risk`
   - `PermissionRule`
   - `PermissionRequest`
   - `content_sha256`
3. 更新 `docs/api.md`，明确这些对象属于 public API。
4. 将版本从 `0.1.1a0` bump 到 `0.1.1a1`。
5. 补测试：
   - top-level import 成功。
   - preview 生成 unified diff。
   - allow 后 apply 写入。
   - rollback 恢复原内容。
   - path escape 被拒绝。
   - 未授权写入被拒绝。
6. 运行完整验证。
7. 使用双语 commit message 提交。
8. live API 和 release audit 通过后，创建并推送 tag `v0.1.1-alpha.1`。

验证命令：

```bash
python3 -m unittest discover -s tests -v
deepseek-runtime doctor --json
python3 scripts/release_drill.py --out release-drill.json
python3 scripts/build_release_artifact.py --out dist --manifest dist/release-manifest.json
DEEPSEEK_API_KEY=... python3 scripts/live_api_smoke.py --out live-smoke.json
python3 scripts/release_gate_audit.py \
  --release-drill-result release-drill.json \
  --live-smoke-result live-smoke.json \
  --manifest dist/release-manifest.json
```

发布证据：

- commit：`86e5dfe Expose ChangeSet public API | 公开 ChangeSet 公共 API`。
- tag：`v0.1.1-alpha.1`。
- live smoke：provider status 200，redaction checks 全部通过。
- release audit：`success: true`。

## 7. 完成定义

`v0.1.1-alpha.1` 已满足以下完成条件：

- top-level public API 包含 ChangeSet 相关对象。
- API 文档说明 preview/apply/rollback 边界。
- 单元测试覆盖 diff、apply、rollback、sandbox、permission。
- release drill、artifact manifest、live smoke、release audit 通过。
- tag `v0.1.1-alpha.1` 已推送到 `7colorai/deepseek_runtime`。
