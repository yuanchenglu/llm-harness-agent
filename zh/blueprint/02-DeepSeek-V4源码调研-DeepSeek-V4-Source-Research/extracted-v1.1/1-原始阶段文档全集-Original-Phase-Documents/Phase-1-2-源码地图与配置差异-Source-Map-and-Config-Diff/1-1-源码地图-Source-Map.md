# 01-source-map.md — DeepSeek V4 官方源码地图 v0.1

> 日期：2026-06-04  
> 阶段：Phase 1 — 资料定位与源码地图  
> 目标：钉死 DeepSeek V4 Flash / Pro 的官方源码、权重、配置、技术报告、推理代码入口。

---

## 1. 官方模型仓库

DeepSeek V4 官方模型仓库主要在 HuggingFace `deepseek-ai` 组织下：

| 仓库 | 类型 | 角色 | 是否有 inference 源码 | 重点 |
|---|---|---|---|---|
| `deepseek-ai/DeepSeek-V4-Pro` | Instruct / Chat | 1.6T 总参数，49B activated，面向最强能力 | 有 | 主读对象 |
| `deepseek-ai/DeepSeek-V4-Flash` | Instruct / Chat | 284B 总参数，13B activated，面向低成本高速 | 有 | 主读对象 |
| `deepseek-ai/DeepSeek-V4-Pro-Base` | Base | Pro 基座模型 | 未看到 inference 目录 | 用于 config/权重对照 |
| `deepseek-ai/DeepSeek-V4-Flash-Base` | Base | Flash 基座模型 | 未看到 inference 目录 | 用于 config/权重对照 |

---

## 2. Pro / Flash Instruct 文件结构

### 2.1 `DeepSeek-V4-Pro`

主仓库大小约 865GB。关键文件：

| 路径 | 大小 | 作用 | 优先级 |
|---|---:|---|---|
| `DeepSeek_V4.pdf` | 4.48MB | 官方技术报告 | P0 |
| `README.md` | 13.2KB | 模型卡、架构、评测、chat template、运行说明 | P0 |
| `config.json` | 1.83KB | 模型结构参数 | P0 |
| `generation_config.json` | 170B | 生成配置 | P2 |
| `encoding/` | 目录 | OpenAI-compatible messages 编码/解析 | P0 |
| `inference/` | 76.3KB | 官方推理源码 | P0 |
| `model-*.safetensors` | 64 shards | 权重 | P1 |

### 2.2 `DeepSeek-V4-Flash`

关键文件结构与 Pro 基本一致：

| 路径 | 大小 | 作用 | 优先级 |
|---|---:|---|---|
| `README.md` | 模型卡 | Flash 架构、评测、运行说明 | P0 |
| `config.json` | 约 1.75KB | 模型结构参数 | P0 |
| `encoding/` | 目录 | OpenAI-compatible messages 编码/解析 | P0 |
| `inference/` | 76.2KB | 官方推理源码 | P0 |
| `model-*.safetensors` | 多 shards | 权重 | P1 |

---

## 3. `inference/` 源码目录

Pro 与 Flash 的 `inference/` 目录结构一致：

| 文件 | Pro 大小 | Flash 大小 | 职责 | 阅读优先级 |
|---|---:|---:|---|---|
| `README.md` | 951B | 951B | 本地推理说明 | P1 |
| `config.json` | 1.07KB | 991B | inference demo 专用配置 | P1 |
| `convert.py` | 7.08KB | 7.08KB | 权重转换 | P2 |
| `generate.py` | 6.3KB | 6.3KB | 交互式生成 / demo | P1 |
| `kernel.py` | 22.2KB | 22.2KB | FP4/FP8 GEMM、sparse attention、HC kernel | P0 |
| `model.py` | 38.6KB | 38.6KB | 模型结构核心实现 | P0 |
| `requirements.txt` | 92B | 92B | 依赖 | P2 |

---

## 4. `model.py` 核心模块地图

官方 `model.py` 已暴露以下核心模块：

| 模块 | 位置/类 | 作用 | 对 Harness 的重要性 |
|---|---|---|---|
| `ModelArgs` | dataclass | 映射 config 字段到模型参数 | 高：所有物理特性的入口 |
| `Linear` / `ColumnParallelLinear` / `RowParallelLinear` | 线性层 | 支持 BF16 / FP8 / FP4 权重 | 中：理解服务端成本与量化 |
| `RMSNorm` | norm | RMSNorm | 低 |
| `precompute_freqs_cis` / `apply_rotary_emb` | RoPE / YaRN | 长上下文位置编码 | 高：1M context 的位置机制 |
| `Compressor` | 压缩 KV | learned gated pooling over `compress_ratio` tokens | 极高：HCA 核心 |
| `Indexer` | sparse attention 索引器 | learned scoring 选择 top-k compressed KV positions | 极高：CSA 核心 |
| `Attention` | MLA + sliding window + compression | 主 attention 路径 | 极高：上下文布局依据 |
| `Gate` | MoE gate | hash routing + score routing | 高：模型路由与稳定性 |
| `Expert` | 单专家 | SwiGLU FFN | 中 |
| `MoE` | 专家路由和执行 | top-k routed experts + shared expert | 高：Flash/Pro 能力差异 |
| `Block` | Transformer block | mHC + Attention + MoE | 高：长链路稳定性 |
| `Transformer` | 总模型 | embedding、blocks、lm_head、MTP | 高：主流程 |

---

## 5. 源码阅读顺序

建议按以下顺序读：

1. `README.md`：确认官方叙事、模型规模、能力、reasoning mode。
2. 顶层 `config.json`：建立 Flash / Pro 差异底图。
3. `inference/model.py::ModelArgs`：确认字段如何进入源码。
4. `inference/model.py::Compressor`：拆 HCA。
5. `inference/model.py::Indexer`：拆 CSA。
6. `inference/model.py::Attention`：拆 sliding window + compressed attention + sparse attention。
7. `inference/model.py::Gate/MoE`：拆专家路由。
8. `inference/model.py::Block`：拆 mHC。
9. `inference/kernel.py`：拆 kernel 层。
10. `encoding/`：拆消息协议和 thinking 模式。

---

## 6. 第一批已经确认的源码事实

### F-001：V4 有官方源码，不在 GitHub 主仓库，而在 HuggingFace 模型仓库

DeepSeek V4 Pro / Flash 的 `inference/model.py`、`kernel.py`、`generate.py`、`convert.py` 均在 HuggingFace 官方模型仓库中。

### F-002：Pro / Flash Instruct 有 inference 源码，Base 仓库主要是权重 + config

Base 仓库可用于结构参数和权重对照，但不是第一优先级源码入口。

### F-003：V4 的核心不是普通 Transformer，而是 MoE + MLA + Hybrid Attention + mHC + FP4/FP8

这点由模型卡、config、`model.py` 共同确认。

### F-004：下一步必须先读 `config.json`，再读 `model.py`

因为 config 已经把 Flash / Pro 的主要物理差异暴露出来，包括 hidden size、layer 数、expert 数、index_topk、compress_ratios、量化方式。
