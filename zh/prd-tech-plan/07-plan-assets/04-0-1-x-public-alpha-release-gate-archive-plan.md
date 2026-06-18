# 04. `0.1.x` Public Alpha Release Gate 归档计划

## 0. AI 执行提示词

你是接手 DeepSeekAgent `0.1.x` 历史 release line 的维护代理。你的任务不是重新实现 `0.1.x`，而是理解它已经如何关闭 production release gate，并在需要补丁时保持原有 gate 纪律。先读 `stage-gates.json`、根 README、release audit 脚本和 PRD TechPlan。任何“已完成”结论必须由命令、文档或 artifact 支撑；不要把未来桌面、Memory、MCP 或 1.0 能力塞回 `0.1.x`。

## 1. 目标

把 `0.1.x Public Alpha` 的已完成计划归档成可复核资产，说明它为什么已经从“研究 MVP”进入“CLI-first release gate 已关闭”的状态。

本计划用于后续 AI 判断：

- `0.1.x` 不是当前主线研发范围。
- 后续只做必要补丁、回归验证和公共试用卫生。
- 新功能应进入 `0.2.x` 之后的版本计划。

## 2. 事实依据

确定：

- `docs/llm-harness-agent/zh/blueprint/stage-gates.json` 中 Stage 6 status 是 `completed`。
- Stage 6 passed 包含 `install_uninstall_smoke`、`cli_doctor_diagnostics`、`release_artifact_manifest`、`release_safety_drill`、`release_observability_smoke`、`public_alpha_release_docs`、`production_gate_audit`、`production_release_gate`。
- `docs/llm-harness-agent/zh/prd-tech-plan/04-roadmap-and-release-gates.md` 说明 `0.1.x` 目标是关闭 CLI-first production release gate。
- 当前产品化路线已进入 runtime kernel 和 desktop code workbench，不再重复 `0.1.x` 研究。

需要重新核验：

- 根仓库当前 `develop` 是否包含未提交 release 相关改动。
- release audit 结果文件是否仍在当前路径。
- README / SECURITY / TROUBLESHOOTING 是否与最新 release artifact 一致。

验证命令：

```bash
python3 scripts/check_repo.py
python3 -m json.tool docs/llm-harness-agent/zh/blueprint/stage-gates.json | sed -n '1,160p'
rg -n "production_release_gate|release_artifact_manifest|cli_doctor_diagnostics|install_uninstall_smoke" \
  docs/llm-harness-agent/zh/blueprint/stage-gates.json \
  README.md SECURITY.md docs/TROUBLESHOOTING.md scripts
```

## 3. 关键决策

- `0.1.x` 的价值闭环是 CLI-first runtime foundation，不是桌面工作台。
- `0.1.x` 只保留 read/write/diff/approval/rollback/session/evidence/release docs 这条闭环。
- `0.1.x` 以后补丁必须继续通过 release safety、observability 和 hygiene checks。
- `0.1.x` 不再承载 Memory、Skill、PlanGraph、MCP、automation 或团队能力。
- 如果后续补丁影响 public CLI 行为，必须新建 OpenSpec，而不是直接改代码。

## 4. 非目标

- 不重开 Stage 0-6 研究。
- 不新增桌面 UI。
- 不新增 General Workspace Agent。
- 不新增 MCP、scheduled tasks、notification、remote approval。
- 不做企业治理、商业计费或插件市场。
- 不把 `deepseek_runtime` 的独立仓库发布混写成 `0.1.x` 主仓库实现。

## 5. 已完成计划归档

### 5.1 CLI-first runtime foundation

已完成事实：

1. CLI-first 路径具备 install / uninstall / doctor smoke。
2. DeepSeek provider、route、cache、usage、cost 和 evidence 已进入 release gate。
3. permission、sandbox、diff preview、approval、rollback 作为安全边界进入 Stage 6 passed。
4. session resume 和 checkpoint/recovery 基础能力进入 Stage 6 passed。

复核方式：

```bash
python3 scripts/check_repo.py
rg -n "doctor|release_gate_audit|rollback|session_resume|permission|sandbox" README.md scripts tests src
```

### 5.2 Public alpha release docs

已完成事实：

1. 根 README 保留公开定位、安装/使用/限制入口。
2. `SECURITY.md` 说明 secret、权限、报告安全问题。
3. `docs/TROUBLESHOOTING.md` 说明 doctor、release drill、artifact checksum 等失败路径。
4. `scripts/check_repo.py` 对这些公开 release 文档做存在性和关键词检查。

复核方式：

```bash
python3 scripts/check_repo.py
sed -n '1,220p' README.md
sed -n '1,220p' SECURITY.md
sed -n '1,220p' docs/TROUBLESHOOTING.md
```

### 5.3 Release gate audit

已完成事实：

1. Stage 6 passed 包含 `production_gate_audit` 和 `production_release_gate`。
2. `scripts/release_gate_audit.py` 是 release gate 复核入口之一。
3. `python3 scripts/check_repo.py` 要求 `scripts/release_gate_audit.py` 中包含 `ready_to_close_gate`、`production_gate_closed`、`commit_hygiene_clean`、`production_release_gate`。

复核方式：

```bash
python3 scripts/check_repo.py
rg -n "ready_to_close_gate|production_gate_closed|commit_hygiene_clean|production_release_gate" scripts/release_gate_audit.py
```

## 6. 实施步骤：后续补丁执行

只有出现 `0.1.x` 回归、文档错误、安全问题或 public alpha 试用阻塞时才执行本节。

1. 定义问题：说明是 CLI 行为、release artifact、文档、安全、diagnostics 还是测试回归。
2. 收集证据：读取相关源码、测试、release artifact、issue 或命令输出。
3. 判断是否需要 OpenSpec：
   - 改 public CLI 行为：需要。
   - 改 release gate 逻辑：需要。
   - 修文档错别字或链接：可跳过，但仍要验证。
4. 最小修复：
   - 只改受影响文件。
   - 不顺手迁移到 desktop/runtime 新架构。
5. 验证：
   - 至少跑 `python3 scripts/check_repo.py`。
   - 行为改动必须跑相关 tests / release drill。
6. 交付：
   - 说明 goal done 与 git staged/committed 状态。

## 7. 验证命令

```bash
python3 scripts/check_repo.py
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/release_gate_audit.py --help
rg -n "0\\.1\\.x|Public Alpha|production_release_gate|release artifact|doctor" \
  docs/prd-tech-plan README.md docs/llm-harness-agent/zh/prd-tech-plan
```

## 8. 完成定义

本归档计划完成的条件：

- 能从 `07-plan-assets/README.md` 找到本文件。
- 本文件清楚说明 `0.1.x` 已关闭 gate，而不是待实现主线。
- 后续 AI 能判断 `0.1.x` 只做补丁和回归，不扩功能面。
- 任何 `0.1.x` 补丁都有明确 OpenSpec 判断、验证命令和完成定义。
