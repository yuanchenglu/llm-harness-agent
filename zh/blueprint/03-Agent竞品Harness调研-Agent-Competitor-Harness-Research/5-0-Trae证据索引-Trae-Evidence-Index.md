# 5-0 Trae / Trae SOLO 证据索引 Trae Evidence Index

> **2026-06-04 事实校准提示：** 本文保留为历史产品/架构调研。涉及源码实现与可迁移性判断时，必须以 [`17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md`](./17-1-ClaudeCode-Codex-Trae源码事实校准-Source-Fact-Calibration.md) 和固定 commit 证据为准；产品声明、官方文档、源码事实与工程推论不得混用。

> 阶段：Stage 2C  
> 版本：v0.6  
> 调研对象分两条线：  
> 1. **Trae / SOLO 产品线**：官方网站、SOLO Web、Docs、Changelog；  
> 2. **Trae Agent 开源研究线**：`bytedance/trae-agent` 官方开源仓库与技术报告。

---

## 1. 证据等级

| 等级 | 含义 | 本阶段适用 |
|---|---|---|
| S0 | 官方源码 / 官方仓库 / 官方配置 | `bytedance/trae-agent` |
| S1 | 官方产品页 / 官方 Docs / 官方 Changelog | `trae.ai` / `docs.trae.ai` |
| A | 官方技术报告 / arXiv 论文 | `arXiv:2507.23370` |
| B | 第三方报道 | 隐私/遥测争议仅作风险参考 |
| C | 工程推论 | 必须标注为推论 |

---

## 2. 官方产品线证据

| 论点 | 证据 |
|---|---|
| Trae 官网主张 “More Than Coding”，并提供 TRAE SOLO 与 TRAE IDE 下载入口 | [Trae 首页](https://www.trae.ai/) |
| SOLO 官方页写明 `Define Tasks. Review Results. AI Does the Rest.` | [SOLO Web](https://www.trae.ai/solo-web) |
| SOLO 官方页强调 Work / Code 双模式、Desktop & Web、global file management、chat、deeper tool integration、multiple delivery formats | [SOLO Web](https://www.trae.ai/solo-web) |
| SOLO 官方页称其能读取不同类型上下文，例如 `.docx`、`.csv`、`.pptx`、Python script，并跨整个 project synthesize 信息 | [SOLO Web broader context](https://www.trae.ai/solo-web) |
| SOLO 官方页称 Desktop 和 Web seamless，workspace 可跨设备，云端支持 parallel background tasks | [SOLO Web multi-device / parallel execution](https://www.trae.ai/solo-web) |

---

## 3. Trae Agent 开源仓库证据

| 论点 | 证据 |
|---|---|
| Trae Agent 是 LLM-based agent for general purpose software engineering tasks | [README](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 它提供 CLI，可理解自然语言并用多种工具和 LLM provider 执行复杂软件工程 workflows | [README](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 它支持 OpenAI、Anthropic、Doubao、Azure、OpenRouter、Ollama、Google Gemini 等多模型 provider | [README Multi-LLM Support](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 它的默认工具包括 bash、str_replace_based_edit_tool、sequentialthinking、task_done | [README config tools](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 支持 custom base_url，因此可接 OpenRouter / 私有兼容接口 | [README base_url](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 支持 MCP servers，例如 Playwright MCP | [README MCP config](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 支持 Docker mode | [README Docker mode](https://github.com/bytedance/trae-agent/blob/main/README.md) |
| 支持 trajectory recording，记录 LLM interactions、agent steps、tool usage、execution metadata | [Trajectory Recording docs](https://github.com/bytedance/trae-agent/blob/main/docs/TRAJECTORY_RECORDING.md) |
| 工具文档列出五个内置工具：file editing、bash、sequential_thinking、task_done、json_edit_tool | [Tools docs](https://github.com/bytedance/trae-agent/blob/main/docs/tools.md) |

---

## 4. 技术报告证据

Trae Agent 技术报告提出：

```text
Agent-based ensemble reasoning for repository-level issue resolution
Generation / Pruning / Selection modular agents
Test-time scaling
SWE-bench Verified 75.20% Pass@1
```

来源：[Trae Agent arXiv](https://arxiv.org/abs/2507.23370)。

---

## 5. 风险证据

有第三方报道称 Trae 曾引发遥测/数据采集争议。该类内容是第三方报道，不作为产品能力事实，只作为 DeepSeek Agent 隐私/本地优先设计的风险参考。

---

## 6. 本轮调研边界

Trae IDE / SOLO 客户端完整源码未公开，本轮产品线以官方网站和 Docs 为主；Trae Agent 开源仓库可作为官方源码研究对象。若后续需要更深入的 Trae IDE 内部实现，需要寻找官方公开代码或明确标注非官方逆向资料。
