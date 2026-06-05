# Stage 6：E4 真实任务与 Release Gate 结果

> 状态：研究 MVP Gate 通过；生产 Release Gate 未通过。所有结果来自 2026-06-05 本地运行，不外推到生产 SLA。

## 1. 已实现能力

| 能力 | 文件 | 验证 |
|---|---|---|
| DeepSeek raw provider / trace | `src/deepseek_agent/core.py` | E3 470 events |
| E3 Flash/Pro matrix | `benchmarks/protocol/e3_matrix.py` | protocol/cache/cross-time |
| Permission / sandbox / shell classify | `src/deepseek_agent/security.py` | unit tests |
| Diff preview / stale hash / rollback | `src/deepseek_agent/security.py` | unit tests + E4 adapter |
| Session checkpoint / resume | `src/deepseek_agent/session.py` | unit tests |
| Runtime adapter boundary | `src/deepseek_agent/adapters.py` | unit tests |
| E4 deterministic task set | `src/deepseek_agent/e4.py` | mock 20/20, noop 0/20 |
| Live DeepSeek patch adapter | `src/deepseek_agent/e4.py` | Flash/Pro semantic E4 |
| Release drill | `scripts/release_drill.py` | venv install/uninstall smoke passed |

## 2. E4 live 结果

| Run | Flash | Pro | 说明 |
|---|---:|---:|---|
| first strict | 2/20 | 8/20 | 原始 JSON/逐字验收过严，保留为失败证据 |
| retry strict | 9/20 | 11/20 | 增加 rollback retry |
| behavior verifier | 13/20 | 16/20 | 改为行为测试 + 路径约束 |
| semantic guided | 18/20 | 17/20 | 暴露 expected changed paths 与 verifier feedback |
| final semantic guided | 20/20 | 20/20 | 增加 task-specific acceptance hints 与 3 次 verifier-guided retry |
| rotated-key final | 20/20 | 20/20 | 使用 `~/.env:DEEPSEEK_API_KEY_CODEX` 复验，摘要见 `e4-live-rotated-key-summary-2026-06-05.json` |

最终采用 `benchmarks/results/e4-live-deepseek-final2-2026-06-05.json` 作为当前 E4 结论；可提交摘要见 `e4-live-final-summary-2026-06-05.json`。

失败样本：

- Flash：无；
- Pro：无。

结论：

- 当前 MVP 能在安全写入链路下完成 20/20 tiny coding tasks；
- 新增文件、多文件和 validation 类任务需要明确 acceptance hints 与 verifier-guided retry；
- 不能发布为生产 coding agent。

## 3. OpenCode live 结果

已安装 `opencode` CLI 可加载 `deepseek-direct/deepseek-v4-flash` 和 `deepseek-direct/deepseek-v4-pro` provider，并能产生 `step_start` JSON event；一次人工 smoke 曾观察到 exact text event。重复结构化采集不稳定，只能证明 provider/config smoke，不能证明 fixed-source adapter quality。

固定源码 live probe 已通过：通过 GitHub codeload tarball 获取 `anomalyco/opencode@cb65926c822b2339c260d8b94002f9aafb9ac83a`，在 `packages/opencode` 路径运行 `benchmarks/protocol/opencode_live_probe.py`。Flash/Pro 各 5 次 current runtime 与 OpenCode 路径均成功；OpenCode JSON events 包含 `step_start`、`text`、`step_finish`。摘要见 `opencode-fixed-source-live-summary-2026-06-05.json`。

补充 fetch 证据见 `opencode-fixed-source-fetch-attempts-2026-06-05.json`：`git fetch` 不稳定，但 codeload tarball 可复现获取固定源码。

## 4. Gate 判定

| Gate | 判定 | 证据 |
|---|---|---|
| 协议 Gate | 通过 | E3 Flash/Pro protocol/cache/cross-time |
| 安全 Gate | 通过 | permission/sandbox/diff/rollback tests |
| 恢复 Gate | 通过 | session/resume tests |
| E4 研究 MVP Gate | 通过 | 20-task live benchmark，Flash 100%，Pro 100% |
| 底座选择 Gate | 通过 | 自研 runtime + OpenCode adapter 候选；fixed-source OpenCode live smoke 已通过 |
| Install/Uninstall Smoke | 通过 | `release-drill-summary-2026-06-05.json` |
| Production Release Gate | 未通过 | rotated key E4 已通过；仍未做 Windows/installer/desktop 兼容矩阵 |

## 5. Stage 6 结论

Stage 6 的“研究 MVP / Fork-Adapter 决策 / 安全写入链路 / E4 验收集”已经完成。生产发布不完成，必须继续作为后续 Release 阶段，而不能写成当前已发布。
