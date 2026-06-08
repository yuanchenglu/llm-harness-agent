# 05. PRD TechPlan 分层归档计划

## 0. AI 执行提示词

你是 DeepSeekAgent 文档体系维护代理。你的任务是维护“公开短入口 + 子仓库完整档案”的结构，不是把所有旧草稿重新放回主仓库。先读根 `docs/prd-tech-plan/README.md`、子仓库 `zh/prd-tech-plan/README.md`、`06-decision-log.md` 和 `scripts/check_repo.py`。任何新增计划都必须服务产品执行，不收录逐字对话、过时中间判断或未采用视觉稿。

## 1. 目标

归档 PRD TechPlan 分层治理计划，确保后续 AI 知道：

- 根仓库只保留公开简短入口。
- 完整 PRD、TechPlan、release gate、UI/UX 和计划资产放在 `docs/llm-harness-agent/zh/prd-tech-plan/`。
- 新计划资产放在 `07-plan-assets/`，不污染 `00-06` 主文档顺序。

## 2. 事实依据

确定：

- 根入口：`docs/prd-tech-plan/README.md`。
- 完整中文 PRD TechPlan：`docs/llm-harness-agent/zh/prd-tech-plan/`。
- 决策记录：`docs/llm-harness-agent/zh/prd-tech-plan/06-decision-log.md`。
- `06-decision-log.md` 明确“主仓库短 README + 子仓库完整文档”的分层决策。
- `scripts/check_repo.py` 会检查根公开 release 文档和子仓库 link / JSON hygiene。

需要重新核验：

- 子仓库是否 clean。
- 根仓库是否因为 submodule pointer 或未提交文件处于 dirty 状态。
- README link 是否仍能通过 `check_repo.py`。

验证命令：

```bash
git -C /Users/bluth/Code/deepseekagent status --short --branch
git -C /Users/bluth/Code/deepseekagent/docs/llm-harness-agent status --short --branch
python3 scripts/check_repo.py
sed -n '1,160p' docs/prd-tech-plan/README.md
sed -n '1,220p' docs/llm-harness-agent/zh/prd-tech-plan/06-decision-log.md
```

## 3. 关键决策

- 主仓库公开入口保持短，不塞完整 PRD。
- 子仓库保留当前准确 Markdown，不恢复错误旧稿全文。
- `00-06` 是 PRD TechPlan 主文档；`07-plan-assets` 是执行计划资产。
- 删除旧内容前必须确认有效结论已融入当前文档。
- 新增计划应优先进入 `07-plan-assets`，再在 README 加索引。

## 4. 非目标

- 不把 `docs/prd-tech-plan/README.md` 扩成完整 PRD。
- 不恢复历史 master docs、过细版本规划或旧视觉稿全文。
- 不把 Blueprint 原始研究材料复制进计划资产目录。
- 不让计划资产替代 OpenSpec。
- 不为“存档”保留已被更正的错误判断。

## 5. 已完成计划归档

### 5.1 主文档分层

已完成事实：

1. 根仓库 `docs/prd-tech-plan/README.md` 是公开短入口。
2. 子仓库 `zh/prd-tech-plan/` 保存完整中文 PRD TechPlan。
3. 子仓库已有 `00-06` 主文档：
   - `00-中文表达与术语表.md`
   - `01-product-and-scope.md`
   - `02-prd.md`
   - `03-technical-architecture.md`
   - `04-roadmap-and-release-gates.md`
   - `05-ui-ux-and-prototype-notes.md`
   - `06-decision-log.md`
4. 后续计划资产进入 `07-plan-assets/`。

### 5.2 路线压缩

已完成事实：

1. 旧的过细版本线已压缩成 `0.1.x / 0.2.x / 0.3.x / 0.4.x / 1.0`。
2. 每条 release line 只承担一个用户价值闭环。
3. Runtime 底座不在每个版本重复铺开。

### 5.3 技术栈定稿

已完成事实：

1. Runtime core：Python。
2. CLI：Python。
3. Desktop UI：React + TypeScript。
4. Shell：Electron first。
5. Runtime bridge：Local HTTP/SSE。
6. Evidence truth source：JSONL event log。
7. Query index：SQLite optional。

## 6. 实施步骤：后续维护

每次新增或修改计划资产时执行：

1. 先读 `07-plan-assets/README.md` 和本标准。
2. 判断新文件属于：
   - 历史归档计划。
   - 当前执行计划。
   - 后续版本研发计划。
3. 按 `00-plan-asset-writing-standard.md` 写完整章节。
4. 更新 `07-plan-assets/README.md` 的阅读顺序。
5. 如影响主路线，在 `04-roadmap-and-release-gates.md` 或 `06-decision-log.md` 中只做必要同步。
6. 运行 link / hygiene 检查。
7. 分别检查根仓库和子仓库 git 状态。

## 7. 验证命令

```bash
python3 scripts/check_repo.py
rg -n "07-plan-assets|计划资产|0\\.1\\.x|0\\.2\\.x|0\\.3\\.x|0\\.4\\.x|1\\.0" \
  docs/prd-tech-plan/README.md \
  docs/llm-harness-agent/zh/prd-tech-plan
git -C docs/llm-harness-agent status --short --branch
```

## 8. 完成定义

本归档计划完成的条件：

- 后续 AI 能准确区分根公开入口、子仓库完整 PRD TechPlan 和计划资产区。
- 新计划不再散落在对话或临时说明里。
- README 能引导到所有版本计划和历史归档计划。
- `python3 scripts/check_repo.py` 通过。
