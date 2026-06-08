# 00. 计划资产写作标准

## 0. AI 执行提示词

你是 DeepSeekAgent 的长期工程规划代理。你的输出不是会议纪要，也不是愿景文案，而是能交给较弱 AI 逐步执行并交付优秀产品的计划资产。写计划前必须先核对真相源：PRD TechPlan、Blueprint `stage-gates.json`、OpenSpec、当前代码和验证命令。每个事实判断都要能回到文件、命令或 release artifact。不要收录逐字对话、过时中间判断、未采用视觉稿或未经验证的口号。

## 1. 目标

统一 `07-plan-assets/` 下所有计划资产的写法，让后续任何版本计划、补丁计划、产品计划都满足以下标准：

- 较弱 AI 读完也知道从哪里开始、做什么、不做什么、如何验证。
- 已完成事实和待执行计划分开。
- 计划不替代 PRD、OpenSpec 或 release gate。
- 计划中的每个阶段都有明确完成定义。
- 计划能指导优秀产品交付，而不是只列标题。

## 2. 事实依据

确定：

- PRD TechPlan 的主文档位于 `docs/llm-harness-agent/zh/prd-tech-plan/`。
- Blueprint 阶段真相位于 `docs/llm-harness-agent/zh/blueprint/stage-gates.json`。
- 根仓库公开短入口位于 `docs/prd-tech-plan/README.md`。
- 当前 release lines 是 `0.1.x`、`0.2.x`、`0.3.x`、`0.4.x`、`1.0`。
- OpenSpec 是具体变更执行入口；计划资产负责跨阶段交接和弱 AI 可执行说明。

验证命令：

```bash
python3 scripts/check_repo.py
python3 -m json.tool docs/llm-harness-agent/zh/blueprint/stage-gates.json | sed -n '1,160p'
find docs/llm-harness-agent/zh/prd-tech-plan/07-plan-assets -maxdepth 1 -type f | sort
```

## 3. 关键决策

- 每份计划开头必须有 `AI 执行提示词`，锁定角色、工作方式、禁止事项和前置背景。
- 每份计划必须固定包含：目标、事实依据、关键决策、非目标、实施步骤、验证命令、完成定义。
- 计划必须用中文为主，保留必要英文术语、命令、文件名、tag、API 名。
- 计划必须标注已完成事实、待执行任务和需要重新核验的时间敏感事实。
- 计划必须能映射到 OpenSpec change；若还没有 change，计划要给出建议 change 名。
- 计划不能把“OpenSpec tasks 勾选完成”当成代码正确；必须要求可执行验证。

## 4. 非目标

- 不把本目录变成所有历史草稿的全文仓库。
- 不收录逐字对话。
- 不收录过时路线、旧版本拆分、未采用视觉图或错误中间判断。
- 不用计划资产替代 OpenSpec proposal / design / spec / tasks。
- 不在计划里承诺未验证的 benchmark、成功率或成本下降。

## 5. 计划模板

新计划应使用以下结构：

```markdown
# NN. <计划名称>

## 0. AI 执行提示词

<角色、背景、必读文件、思维方式、禁止事项、验证纪律。>

## 1. 目标

<用 3-8 行说明本计划要达成的产品或工程状态。>

## 2. 事实依据

确定：

- <来自文档、代码、测试、tag、release artifact 的事实。>

需要重新核验：

- <时间敏感事实，例如远端 tag、依赖版本、API 行为。>

## 3. 关键决策

- <架构、范围、技术栈、产品边界和 gate 决策。>

## 4. 非目标

- <明确不做什么，防止扩范围。>

## 5. 实施步骤

### 5.1 <阶段名>

1. <可执行步骤。>
2. <验收证据。>

## 6. 验证命令

```bash
<必须运行的命令>
```

## 7. 完成定义

- <所有必须满足的条件。>
```

## 6. 维护流程

1. 先运行或读取真相源，确认当前阶段状态。
2. 判断这是历史归档计划、当前执行计划，还是未来版本计划。
3. 历史归档只写已验证事实、当时完成定义和可复核证据。
4. 当前执行计划必须写到具体文件、命令、测试、风险、回滚。
5. 未来版本计划必须写清前置 gate，不能把后续能力提前写成当前事实。
6. 更新 `07-plan-assets/README.md` 的阅读顺序。
7. 运行 `python3 scripts/check_repo.py` 和针对性 `rg` 检索。

## 7. 验证命令

```bash
python3 scripts/check_repo.py
rg -n "AI 执行提示词|完成定义|非目标|OpenSpec|0\\.2\\.x|0\\.3\\.x|0\\.4\\.x|1\\.0" \
  docs/llm-harness-agent/zh/prd-tech-plan/07-plan-assets
```

## 8. 完成定义

本标准完成的条件：

- `07-plan-assets/README.md` 明确计划资产边界和阅读顺序。
- 所有新增计划都有 `AI 执行提示词`。
- 所有版本计划都包含固定章节。
- 历史计划和未来计划没有混写。
- 文档检索能找到每条 release line 的计划资产。

