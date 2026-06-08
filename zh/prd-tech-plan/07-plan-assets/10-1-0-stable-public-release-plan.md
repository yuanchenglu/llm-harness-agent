# 10. `1.0` Stable Public Release 版本研发计划

## 0. AI 执行提示词

你是 DeepSeekAgent `1.0 Stable Public Release` 的 release lead。你的职责不是继续加功能，而是冻结范围、关闭 gate、验证安装升级卸载、迁移、诊断、文档、安全和 artifact 完整性。执行前必须核对 `0.1.x` 到 `0.4.x` 的 gate、OpenSpec 状态、release artifact、当前 git 状态和公开文档。任何未通过 gate 必须写成 blocker 或延期豁免，不允许用自然语言包装成已完成。

## 1. 目标

`1.0` 的目标是形成真正面向公开用户的稳定产品，而不是企业平台或生态市场。

版本完成后，公开用户应能：

1. 安装 DeepSeekAgent。
2. 配置本地环境和 API key。
3. 运行 doctor。
4. 完成第一个安全任务。
5. 升级版本。
6. 回滚或卸载。
7. 生成 redacted diagnostics bundle。
8. 查阅 Quick Start、Troubleshooting、Security、Compatibility。
9. 提交 issue 或安全报告。

## 2. 事实依据

确定：

- `1.0` release line 是 Stable Public Release。
- PRD TechPlan 规定 `1.0` 必须做 Public README / Quick Start / Troubleshooting、artifact checksum、install / upgrade / uninstall smoke、config migration、diagnostics bundle、privacy / security / permission 文档、issue template、security policy、contributing guide。
- PRD TechPlan 明确 `1.0` 不做企业 SSO / SCIM、云端多租户、商业计费、公开插件市场、企业 policy center、实时多人协作。
- `1.0` gate 需要 prior gates 通过，或未通过 gate 有 blocker / 延期豁免。

前置 gate：

- `0.1.x` CLI-first public alpha gate 已关闭。
- `0.2.x` Desktop Code Workbench gate 已通过。
- `0.3.x` General Workspace Agent gate 已通过或明确延期。
- `0.4.x` Integrations and Automation Preview gate 已通过或明确延期。
- 所有 active OpenSpec change 要么完成并 archive，要么明确标为不进 1.0。

需要重新核验：

- 当前 packaging 方式。
- 支持平台矩阵。
- runtime tag / app version / CLI version 对齐。
- release artifact checksum 机制。
- public docs 链接和安装命令。
- diagnostics redaction 是否覆盖最新日志和 event schema。

验证命令：

```bash
python3 scripts/check_repo.py
openspec list
git status --short --branch
rg -n "Stable Public Release|install|upgrade|uninstall|diagnostics|checksum|Security Policy|Troubleshooting" \
  docs/prd-tech-plan README.md SECURITY.md docs/TROUBLESHOOTING.md docs/llm-harness-agent/zh/prd-tech-plan
```

## 3. 关键决策

- `1.0` 是稳定化和公开发布，不是功能扩张。
- 未完成的 `0.3.x` / `0.4.x` 能力必须显式延期，不能半成品进入 1.0。
- Public docs 必须覆盖 happy path 和失败恢复。
- Diagnostics bundle 必须 redaction，不能包含 API key、secret、未授权文件正文或 raw reasoning_content。
- Release artifact 必须有 manifest 和 checksum 或等价完整性校验。
- Migration / rollback 是 gate，不是 release note。
- E4-style 真实任务报告必须可验证成功率、首次完成率、失败样本、人工接管和每成功任务 token / cost。

## 4. 非目标

- 不做企业 SSO / SCIM。
- 不做云端多租户。
- 不做商业计费。
- 不做公开插件市场。
- 不做企业 policy center。
- 不做实时多人协作。
- 不在 1.0 前临时引入大功能。
- 不发布没有 rollback / uninstall / diagnostics 的“看起来可用”版本。

## 5. 实施步骤

### 5.1 Release freeze

建议 change：

```text
prepare-stable-public-release
```

步骤：

1. 列出所有 active OpenSpec changes。
2. 每个 change 标记：
   - in 1.0。
   - deferred。
   - archived。
   - blocker。
3. 冻结功能范围。
4. 冻结 public API 和 config schema。
5. 建立 release checklist。

验证：

```bash
openspec list
openspec status --change prepare-stable-public-release
```

### 5.2 Version and compatibility matrix

1. 定义版本：
   - DeepSeekAgent app version。
   - CLI version。
   - runtime version。
   - desktop version。
2. 定义平台矩阵：
   - macOS。
   - Linux。
   - Windows，如未支持必须明确。
3. 定义 Python / Node / Electron 支持范围。
4. 定义 DeepSeek provider capability snapshot。
5. 文档中写清兼容限制。

验证：

```bash
rg -n "Compatibility|Limits|Python|Node|Electron|macOS|Linux|Windows" README.md docs
```

### 5.3 Install / upgrade / uninstall smoke

1. 从干净目录安装。
2. 配置 API key，不记录 secret。
3. 运行 doctor。
4. 执行 read-only task。
5. 执行 write task + approval + rollback。
6. 从旧 config 升级。
7. 卸载并确认清理范围。
8. 记录 smoke 输出和 artifact hash。

验证：

```bash
python3 scripts/check_repo.py
python3 -m unittest discover -s tests -v
# 具体 install/upgrade/uninstall 命令在 1.0 OpenSpec 中固定
```

### 5.4 Config migration

1. 列出现有 config schema。
2. 为每个历史 schema 写 migration。
3. migration 必须：
   - 幂等。
   - 可 dry-run。
   - 可 backup。
   - 失败可恢复。
4. migration 不打印 secret。
5. migration 结果进入 diagnostics。

验证：

```bash
rg -n "migration|config schema|dry-run|backup" src apps tests docs
```

### 5.5 Diagnostics bundle

1. bundle 内容：
   - app version。
   - runtime version。
   - platform。
   - config summary。
   - redacted logs。
   - event refs。
   - recent errors。
2. redaction：
   - API key。
   - secret token。
   - Authorization。
   - password。
   - raw reasoning_content。
   - 未授权文件正文。
3. bundle 生成命令或 UI action。
4. bundle schema 文档。

验证：

```bash
rg -n "DiagnosticsBundle|diagnostics bundle|redacted_logs|reasoning_content" src apps tests docs
python3 scripts/check_repo.py
```

### 5.6 Release artifact and checksum

1. 生成 release manifest。
2. 生成 checksum。
3. 验证 checksum。
4. 记录 build input：
   - commit。
   - version。
   - dependency lock。
   - platform。
5. artifact 不包含 `.env`、key、local logs。
6. 文档写清用户如何验证 artifact。

验证：

```bash
python3 scripts/build_release_artifact.py --help
python3 scripts/release_gate_audit.py --help
rg -n "checksum|manifest|artifact" README.md docs scripts
```

### 5.7 Public documentation

1. Public README：
   - 产品定位。
   - Quick Start。
   - install。
   - first task。
   - safety model。
   - troubleshooting link。
2. Troubleshooting：
   - doctor fails。
   - install fails。
   - provider fails。
   - permission denied。
   - stale diff。
   - rollback fails。
   - diagnostics redaction。
3. Security：
   - secret handling。
   - permission model。
   - local-first。
   - report security issue。
4. Contributing：
   - dev setup。
   - tests。
   - OpenSpec workflow。
5. Issue templates：
   - bug report。
   - security route。
   - diagnostics attachment rules。

验证：

```bash
python3 scripts/check_repo.py
rg -n "Quick Start|Troubleshooting|Security Policy|Contributing|issue template|diagnostics" README.md SECURITY.md docs .github
```

### 5.8 E4-style release evidence report

1. 固定真实任务集。
2. 对每个任务记录：
   - success/failure。
   - first-pass completion。
   - failure sample。
   - human intervention。
   - rollback。
   - token。
   - cache hit/miss。
   - cost。
3. 报告不包含 secret、raw prompt、raw response、raw reasoning_content。
4. 报告能复核每成功任务 cost。

验证：

```bash
rg -n "success|first-pass|failure sample|human intervention|cost per successful task|cache" benchmarks docs scripts
```

### 5.9 Release candidate and final release

1. 创建 release candidate branch 或 tag。
2. 跑完整 gate。
3. 修复 blocker。
4. 复跑完整 gate。
5. 确认 worktree clean。
6. 创建双语 commit 和 tag。
7. 推送 remote。
8. 发布 release notes。

验证：

```bash
git status --short --branch
python3 scripts/check_repo.py
python3 -m unittest discover -s tests -v
cd apps/desktop && npm run test && npm run build && npm run e2e
```

## 6. 验证命令

```bash
python3 scripts/check_repo.py
openspec validate prepare-stable-public-release --type change --strict
python3 -m unittest discover -s tests -v
cd apps/desktop && npm run test && npm run build && npm run e2e
rg -n "Stable Public Release|Quick Start|upgrade|uninstall|diagnostics bundle|checksum|manifest|Security Policy|Contributing" \
  README.md SECURITY.md docs scripts apps
```

## 7. 完成定义

`1.0` 完成必须满足：

- Prior gates 已通过，或未通过项有明确 blocker / 延期豁免。
- Public install 通过。
- Upgrade / migration / uninstall tests 通过。
- Build manifest + checksum verification 通过。
- Diagnostics redaction tests 通过。
- Route / cache / evidence smoke 通过。
- E4-style 真实任务证据报告可验证成功率、首次完成率、失败样本、人工接管和每成功任务 token / cost。
- Public README、Quick Start、Troubleshooting、Security、Contributing、Issue Template 完整。
- `production_release_gate` 状态与 Blueprint / manifest 一致。
- 远端 tag、release notes、artifact 和 checksum 可复核。

