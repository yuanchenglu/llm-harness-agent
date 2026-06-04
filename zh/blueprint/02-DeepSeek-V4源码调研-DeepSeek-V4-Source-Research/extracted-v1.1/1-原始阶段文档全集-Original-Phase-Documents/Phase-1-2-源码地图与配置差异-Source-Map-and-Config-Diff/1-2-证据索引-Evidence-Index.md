# 01-evidence-index.md — DeepSeek V4 调研证据索引 v0.1

> 日期：2026-06-04  
> 用途：记录每条关键结论的证据来源，防止把推断当事实。

---

## 证据等级

| 等级 | 含义 |
|---|---|
| S0 | 官方源码 / 官方 config / 官方模型仓库直接确认 |
| S1 | 官方模型卡 / 官方 API 文档直接确认 |
| A | 官方技术报告确认 |
| B | 可信第三方资料 |
| C | 工程推断，必须后续验证 |

---

## 证据清单

| 编号 | 结论 | 等级 | 来源 |
|---|---|---|---|
| E-001 | DeepSeek V4 官方模型仓库在 HuggingFace `deepseek-ai` 组织下 | S0 | `deepseek-ai/DeepSeek-V4-Pro`, `DeepSeek-V4-Flash` |
| E-002 | Pro / Flash Instruct 仓库包含 `inference/` 源码目录 | S0 | `inference/model.py`, `kernel.py`, `generate.py`, `convert.py` |
| E-003 | Pro-Base / Flash-Base 主要是权重 + config，未看到 inference 目录 | S0 | Base 仓库文件列表 |
| E-004 | V4-Pro 为 1.6T total / 49B activated，V4-Flash 为 284B total / 13B activated | S1 | 模型卡 Introduction / Model Downloads |
| E-005 | Pro / Flash 均支持 1M context | S1 / S0 | 模型卡 + `max_position_embeddings=1048576` |
| E-006 | V4 采用 Hybrid Attention：CSA + HCA | S1 / A | 模型卡 Introduction / 技术报告 |
| E-007 | V4-Pro 1M context 下 single-token inference FLOPs 是 V3.2 的 27%，KV cache 是 10% | S1 / A | 模型卡 Introduction |
| E-008 | V4 采用 mHC 增强 residual connections | S1 / A | 模型卡 Introduction |
| E-009 | V4 采用 Muon optimizer | S1 / A | 模型卡 Introduction |
| E-010 | V4 Instruct 支持 Non-think / Think / Think Max 三种 reasoning effort | S1 | 模型卡 Instruct Model |
| E-011 | V4 没有 Jinja chat template，而是提供 `encoding/` 文件夹 | S1 | 模型卡 Chat Template |
| E-012 | Pro config：hidden_size=7168，layers=61，routed_experts=384，index_topk=1024 | S0 | `DeepSeek-V4-Pro/config.json` |
| E-013 | Flash config：hidden_size=4096，layers=43，routed_experts=256，index_topk=512 | S0 | `DeepSeek-V4-Flash/config.json` |
| E-014 | Base config 的 expert_dtype=fp8，Instruct config 的 expert_dtype=fp4 | S0 | 四个 config.json |
| E-015 | `Compressor` 通过 learned gated pooling 压缩 KV cache | S0 | `inference/model.py::Compressor` |
| E-016 | `Indexer` 通过 learned scoring 选择 top-k compressed KV positions | S0 | `inference/model.py::Indexer` |
| E-017 | `Attention` 同时使用 sliding window + optional KV compression + sparse_attn | S0 | `inference/model.py::Attention` |
| E-018 | `Gate` 支持前 `n_hash_layers` hash routing，后续 score routing | S0 | `inference/model.py::Gate` |
| E-019 | `MoE` 路由到 top-k routed experts + 1 shared expert | S0 | `inference/model.py::MoE` |
| E-020 | `Block` 使用 Hyper-Connections 维护 `hc_mult` hidden state copies | S0 | `inference/model.py::Block` |

---

## 当前不确定项

| 编号 | 问题 | 状态 |
|---|---|---|
| Q-001 | `ratio=4` 是否就是 CSA 主路径？ | 高概率，但需读技术报告确认 |
| Q-002 | `ratio=128` 是否就是 HCA 主路径？ | 高概率，但需读技术报告确认 |
| Q-003 | Pro 前两层压缩、Flash 前两层不压缩的原因是什么？ | 未确认 |
| Q-004 | Max thinking 是否只是 encoding/prompt 策略？ | 未确认 |
| Q-005 | V4 API 的 thinking mode 与开源 encoding 的对应关系 | 需读 encoding 源码 |
